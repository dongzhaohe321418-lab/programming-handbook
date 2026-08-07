# Project 5 · Mini MCP Server and Client

[Chapter 28](../../ch28-tools-mcp/index.md) showed you the messages. This
project makes you own them. You will write a JSON-RPC 2.0 server that
implements five MCP methods, a schema validator that rejects bad arguments
at the boundary, three tools worth calling — including a file reader over a
sandboxed filesystem that refuses to be talked out of its directory — a set
of resources addressed by URI, and a client that performs the handshake and
drives the whole thing. Everything runs in memory, so you can watch every
byte that crosses the wire.

The point is not to reimplement a protocol for its own sake. It is that once
you have handled `-32602` yourself, "the SDK does that for you" stops being
a spell and becomes a convenience.

## What you'll build

One program, six labelled acts. Here are three of them — the schema check,
the traversal guard, and a scripted model driving tools it discovered at
runtime:

```text
3. schema validation at the boundary
      ok          search_notes({"query": "retention"})
      -32602      search_notes({"query": "retention", "limit": 99})
                  -> arguments.limit: 99 is above maximum 20
      -32602      search_notes({"query": "retention", "lmit": 2})
                  -> arguments.lmit: unknown; expected one of ['limit', 'query']
      TOOL FAILED calculate({"expression": "2 +"})
                  -> ValueError: the expression ended in the middle

4. the path-traversal guard
      ALLOW ./x/../todo.md         '- [x] write the retention spec'
      DENY  ../../etc/passwd       ValueError: path escapes /notes: '../../etc/passwd'
      DENY  /etc/passwd            ValueError: path escapes /notes: '/etc/passwd'

6. a model driving the protocol
   step 1: search_notes({"query": "retention", "limit": 3})
           | meeting.md:3: - retention policy sign-off still pending
           | specs/retention.md:1: Retention policy (approved 2026-02-14)
           | todo.md:1: - [x] write the retention spec
   step 2: read_note({"path": "specs/retention.md"})
           | Retention policy (approved 2026-02-14)
           | Raw events are kept for 18 months, then deleted.
           | Archived events move to cold storage after 90 days.
   step 3: search_notes({"query": "GB-month", "limit": 2})
           | specs/pricing.md:1: Cold storage costs 0.023 USD per GB-month.
           | specs/pricing.md:2: Hot storage costs 0.115 USD per GB-month.
   step 4: calculate({"expression": "500 * 0.023 * 18"})
           | 207.0

   Raw events are kept for 18 months. Holding 500 GB in cold storage that long costs $207.00 at 0.023 USD per GB-month.
```

Read step 4 again. Nothing in the host loop knows what a retention policy
is, what a note is, or that `calculate` exists. The model learned all of it
from one `tools/list` response.

## What it exercises

- [28.3 The Model Context Protocol](../../ch28-tools-mcp/03-mcp-protocol.md)
  — JSON-RPC envelopes, the `initialize` handshake, the reserved error
  codes, and the `isError`-versus-`error` distinction that this project
  makes you feel rather than read.
- [28.4 Writing a real MCP server](../../ch28-tools-mcp/04-building-mcp-server.md)
  — resolve-then-compare path safety, tool design, and the stdout/stderr
  rule you will meet the first time you deploy one.
- [28.1 Function calling and JSON Schema](../../ch28-tools-mcp/01-function-calling.md)
  and [28.2 Structured output](../../ch28-tools-mcp/02-structured-output.md)
  — the schema *is* the contract; here you write the validator that enforces
  it.
- [Chapter 10 · Errors and Exceptions](../../ch10-exceptions/index.md) — the
  server catches everything and turns it into data. A server that raises is
  a server that hangs up.
- [Chapter 17 · Recursion](../../ch17-recursion/index.md) — the schema
  validator recurses into nested properties, and the calculator is a
  textbook recursive-descent parser.
- [11.1 Paths](../../ch11-files/01-paths.md) — why `join(root, "/etc/passwd")`
  quietly discards the root, and what to do about it.

## Milestones

### Milestone 1 — message plumbing and the handshake

**Goal:** a `MiniMCPServer.handle_line(text)` that parses one line of JSON,
dispatches on `method`, and returns one line of JSON back — plus
`_ok(id, result)` and `_error(id, code, message, data)` helpers, and a
`MiniMCPClient` that owns an id counter and performs `initialize` followed
by the `notifications/initialized` notification.

**Done when...** the handshake prints four lines (request, response,
notification, silence); a response's `id` always equals its request's `id`;
a message with no `id` returns `None` and never a reply; `handle_line("not
json")` returns a `-32700` error object; and a request whose `jsonrpc` field
is missing or not `"2.0"` returns `-32600`.

??? tip "Hint"

    Serialise for real, even though both ends live in one process. Passing
    dicts around hides exactly the bugs a transport creates — a value that
    is not JSON-serialisable, a tuple that arrives as a list:

    ```python
    import json

    def handle_line(line):
        """Parse one transport line; -32700 is the only error you can
        report when you could not even read the id."""
        try:
            message = json.loads(line)
        except json.JSONDecodeError as exc:
            return json.dumps({"jsonrpc": "2.0", "id": None,
                               "error": {"code": -32700,
                                         "message": f"invalid JSON: {exc.msg}"}})
        return json.dumps({"jsonrpc": "2.0", "id": message.get("id"),
                           "result": {"echo": message.get("method")}})

    print(handle_line('{"jsonrpc":"2.0","id":7,"method":"ping"}'))
    print(handle_line("not json at all"))
    ```

    Note the `id: null` in the parse-error case: you could not read an id,
    so JSON-RPC says report `null`. Every *other* error must echo the real
    id, or the client can never match the reply to its request.

### Milestone 2 — a tool registry with schema validation

**Goal:** `add_tool(name, description, input_schema, fn)`, a `tools/list`
that returns every tool with its full schema, and a `validate(schema, value)`
that returns a *list of human-readable problems* — checking `type`,
`required`, `properties`, `additionalProperties: false`, `enum`,
`minimum`/`maximum`, and `minLength`/`maxLength`.

**Done when...** a good call succeeds; a wrong type, an out-of-range number,
a too-short string, an unknown key, and a missing required key each come
back as `-32602` with the specific problem in `error.data`; and
`validate({"type": "integer"}, True)` reports a type error, because in JSON
`true` is not the number 1.

??? tip "Hint"

    Return problems, do not raise them. A validator that raises tells the
    caller about one mistake; a validator that accumulates tells the model
    about all of them in a single round trip:

    ```python
    def validate(schema, value, where="arguments"):
        problems = []
        for key in schema.get("required", []):
            if key not in value:
                problems.append(f"{where}.{key}: required but missing")
        for key, sub in schema.get("properties", {}).items():
            if key in value and "maximum" in sub and value[key] > sub["maximum"]:
                problems.append(f"{where}.{key}: {value[key]} is above "
                                f"maximum {sub['maximum']}")
        return problems

    schema = {"type": "object", "required": ["query"],
              "properties": {"limit": {"type": "integer", "maximum": 20}}}
    print(validate(schema, {"query": "notes", "limit": 5}))
    print(validate(schema, {"limit": 99}))
    ```

    Recursion arrives for free the moment you handle nested objects: an
    object's `properties` are themselves schemas, so the object branch calls
    `validate` on each present key and concatenates the lists.

### Milestone 3 — three tools worth calling

**Goal:** `read_note(path)` over an in-memory `NOTES` dict with a
path-traversal guard, `search_notes(query, limit)`, and `calculate(expression)`
built as a recursive-descent parser — no `eval`, ever.

**Done when...** `meeting.md` and `./x/../todo.md` are allowed;
`../../etc/passwd` and `/etc/passwd` are refused; a missing note raises
`FileNotFoundError` whose message names what to try next; and `calculate`
handles `2 + 3 * 4` (14.0), `(2 + 3) * 4` (20.0), unary minus, and
`1 / 0` — the last three as errors the *model* can read.

??? tip "Hint"

    Normalise first, compare second. The naive `".." not in path` check is
    wrong in both directions — it allows `/etc/passwd`, which needs no `..`
    at all, and denies harmless paths that resolve back inside the root:

    ```python
    import posixpath

    ROOT = "/notes"

    def sandbox_path(name):
        candidate = posixpath.normpath(posixpath.join(ROOT, name))
        if candidate != ROOT and not candidate.startswith(ROOT + "/"):
            raise ValueError(f"path escapes {ROOT}: {name!r}")
        return candidate

    for attempt in ["specs/a.md", "./x/../b.md", "../../etc/passwd",
                    "/etc/passwd"]:
        try:
            print("ALLOW", attempt, "->", sandbox_path(attempt))
        except ValueError as exc:
            print("DENY ", attempt, "->", exc)
    ```

    `posixpath.join("/notes", "/etc/passwd")` is `"/etc/passwd"` — an
    absolute right-hand side wins and the root vanishes. That is exactly why
    the comparison happens *after* normalisation, and it is the same
    behaviour `pathlib` has on a real disk, where you would use
    `Path.resolve()`.

### Milestone 4 — resources

**Goal:** `add_resource(uri, name, description, mime_type, reader)`, plus
`resources/list` and `resources/read`. Advertise resources in the
`initialize` capabilities so a client knows to ask.

**Done when...** `resources/list` returns one entry per note with a
`note:///…` URI and a `mimeType`; `resources/read` returns
`{"contents": [{"uri": …, "mimeType": …, "text": …}]}`; and reading an
unknown URI is `-32602` with the available URIs in `error.data`.

??? tip "Hint"

    The distinction that matters is *who decides*, not what the bytes look
    like. `read_note` is a **tool** — the model decides to call it.
    `note:///specs/pricing.md` is a **resource** — the host attaches it
    because the user picked it from a menu. The same file, reached two ways,
    with two different trust models.

    Registering readers in a loop has one classic trap:

    ```python
    NOTES = {"a.md": "alpha", "b.md": "beta"}

    late = {p: (lambda: NOTES[p]) for p in NOTES}          # WRONG
    early = {p: (lambda q: lambda: NOTES[q])(p) for p in NOTES}   # right
    print("late binding:", {p: fn() for p, fn in late.items()})
    print("bound early:", {p: fn() for p, fn in early.items()})
    ```

    The first closes over the *variable* `p`, which by call time holds the
    last key, so both readers return `"beta"`. The second captures the value.

### Milestone 5 — every error code, deliberately

**Goal:** produce all five reserved codes on purpose, and keep tool failures
*out* of that set.

**Done when...** you can print, in order: `-32700` from unparseable bytes,
`-32600` from a request sent before the handshake completes, `-32601` from
`prompts/list` (with the implemented methods in `data`), `-32602` from an
unknown tool name and from schema violations, `-32603` from a handler bug —
and a *failing tool* comes back as a normal result with `isError: true`,
never as an error object.

??? tip "Hint"

    Give handlers a way to name their own code without every one of them
    building an envelope:

    ```python
    class JsonRpcError(Exception):
        """Raised inside a handler to become a JSON-RPC error object."""
        def __init__(self, code, message, data=None):
            super().__init__(message)
            self.code, self.message, self.data = code, message, data

    def dispatch(method):
        try:
            if method != "tools/list":
                raise JsonRpcError(-32601, f"unknown method {method!r}",
                                   {"available": ["tools/list"]})
            return {"tools": []}
        except JsonRpcError as exc:
            return {"code": exc.code, "message": exc.message, "data": exc.data}

    print(dispatch("tools/list"))
    print(dispatch("prompts/list"))
    ```

    Then wrap the whole dispatch in a second `except Exception` that returns
    `-32603`. A server that lets an exception escape has hung up on its
    client mid-conversation, and the host will report it as "server crashed"
    with no detail at all.

### Milestone 6 — a model driving the protocol

**Goal:** a `FakeLLM` that reads a transcript and returns either a tool call
or a final answer, plus a `run_over_mcp(question, client, llm)` loop that
calls `tools/list` once and then never mentions a tool by name.

**Done when...** the model answers a question no single tool can — it
searches, reads the note the search found, searches again for a price,
computes with the numbers it extracted, and states the answer — and
`run_over_mcp` contains no string literal naming any of your tools.

??? tip "Hint"

    Make every rule fire on something *missing* from the transcript, and
    pull the arguments out of what came back. A policy that hard-codes
    `"specs/retention.md"` is a script; one that picks the path out of the
    search results is reacting:

    ```python
    import re

    transcript = ("Observation: meeting.md:3: retention sign-off pending\n"
                  "specs/retention.md:1: Retention policy\n")
    paths = re.findall(r"^(\S+?):\d+:", transcript, re.M)
    print("candidates:", paths)
    print("chosen:", max(paths, key=lambda p: "retention" in p))
    ```

    Test the reaction by changing the data, not the policy: edit a note so
    the retention period is 24 months and the final answer should follow,
    with no change to `FakeLLM`.

## Reference implementation

Build yours milestone by milestone. Compare when you are stuck, and compare
*tests* as eagerly as code — the six labelled acts in the driver are really
six test suites wearing a print statement.

??? success "Full reference implementation"

    ```python
    """Mini MCP: a JSON-RPC 2.0 server with tools and resources, and a client."""
    import json
    import posixpath
    import re

    PROTOCOL_VERSION = "2025-06-18"          # MCP revisions are date-stamped

    # JSON-RPC 2.0 reserved error codes.
    PARSE_ERROR, INVALID_REQUEST = -32700, -32600
    METHOD_NOT_FOUND, INVALID_PARAMS, INTERNAL_ERROR = -32601, -32602, -32603

    # ===================== the sandbox: an in-memory disk =====================
    SANDBOX_ROOT = "/notes"                  # a virtual root; nothing real is read
    NOTES = {
        "meeting.md": "Standup 2026-03-02\n"
                      "- export job ships Friday\n"
                      "- retention policy sign-off still pending\n",
        "specs/retention.md": "Retention policy (approved 2026-02-14)\n"
                              "Raw events are kept for 18 months, then deleted.\n"
                              "Archived events move to cold storage after 90 days.\n",
        "specs/pricing.md": "Cold storage costs 0.023 USD per GB-month.\n"
                            "Hot storage costs 0.115 USD per GB-month.\n",
        "todo.md": "- [x] write the retention spec\n"
                   "- [ ] rotate the API keys\n",
    }


    def sandbox_path(name):
        """Resolve `name` under SANDBOX_ROOT and refuse anything that escapes.

        The rule is *normalise first, compare second* — the same rule
        `Path.resolve()` implements on a real disk. `posixpath.join` throws the
        root away when the right-hand side is absolute, which is exactly why the
        comparison cannot happen before normalisation.
        """
        candidate = posixpath.normpath(posixpath.join(SANDBOX_ROOT, name))
        inside = (candidate == SANDBOX_ROOT
                  or candidate.startswith(SANDBOX_ROOT + "/"))
        if not inside:
            raise ValueError(f"path escapes {SANDBOX_ROOT}: {name!r}")
        return candidate


    def relative_key(resolved):
        """Turn '/notes/specs/pricing.md' into the dict key 'specs/pricing.md'."""
        return resolved[len(SANDBOX_ROOT) + 1:]


    # ============================ the three tools =============================
    def read_note(path):
        """Return the whole text of one note that lives inside the sandbox."""
        key = relative_key(sandbox_path(path))
        if key not in NOTES:
            raise FileNotFoundError(
                f"no note {key!r}; call search_notes or resources/list first")
        return NOTES[key]


    def search_notes(query, limit=3):
        """Return `path:line: text` for every line containing `query`."""
        hits = [f"{path}:{n}: {line.strip()}"
                for path in sorted(NOTES)
                for n, line in enumerate(NOTES[path].splitlines(), start=1)
                if query.lower() in line.lower()]
        if not hits:
            return f"no notes match {query!r}"
        shown = hits[:limit]
        if len(hits) > limit:
            shown.append(f"... {len(hits) - limit} more hit(s); raise `limit`")
        return "\n".join(shown)


    NUMBER = re.compile(r"\d+\.\d+|\d+")
    TOKEN = re.compile(r"\d+\.\d+|\d+|[-+*/()]|\S")


    def calculate(expression):
        """Evaluate + - * / and parentheses with a recursive-descent parser.

        Never `eval()` on text a model produced: that is arbitrary code
        execution wearing a calculator costume. Parsing costs twenty lines and
        can only ever produce a number.
        """
        tokens = TOKEN.findall(expression)
        junk = [t for t in tokens if not re.fullmatch(r"\d+\.\d+|\d+|[-+*/()]", t)]
        if junk:
            raise ValueError(f"unexpected token(s) {junk} in {expression!r}")
        at = [0]

        def peek():
            return tokens[at[0]] if at[0] < len(tokens) else None

        def take():
            token = peek()
            at[0] += 1
            return token

        def factor():
            token = take()
            if token == "-":
                return -factor()
            if token == "(":
                value = expression_rule()
                if take() != ")":
                    raise ValueError("unbalanced parentheses")
                return value
            if token is None:
                raise ValueError("the expression ended in the middle")
            if not NUMBER.fullmatch(token):
                raise ValueError(f"expected a number, found {token!r}")
            return float(token)

        def term():
            value = factor()
            while peek() in ("*", "/"):
                operator, right = take(), factor()
                if operator == "/" and right == 0:
                    raise ZeroDivisionError("division by zero")
                value = value * right if operator == "*" else value / right
            return value

        def expression_rule():
            value = term()
            while peek() in ("+", "-"):
                operator, right = take(), term()
                value = value + right if operator == "+" else value - right
            return value

        value = expression_rule()
        if at[0] != len(tokens):
            raise ValueError(f"trailing input at {tokens[at[0]]!r}")
        return round(value, 6)


    # ===================== a small honest JSON Schema check ===================
    JSON_TYPES = {"string": str, "integer": int, "number": (int, float),
                  "boolean": bool, "array": list, "object": dict}


    def validate(schema, value, where="arguments"):
        """Check `value` against a subset of JSON Schema; return the problems.

        An empty list means valid. The subset implemented here — type, required,
        properties, additionalProperties, enum, minimum/maximum, minLength /
        maxLength — covers what tool schemas actually use.
        """
        kind = schema.get("type")
        if kind is not None:
            ok = isinstance(value, JSON_TYPES[kind])
            if kind in ("integer", "number") and isinstance(value, bool):
                ok = False                  # JSON says `true` is not the number 1
            if not ok:
                return [f"{where}: expected {kind}, got {type(value).__name__}"]

        problems = []
        if kind == "object":
            properties = schema.get("properties", {})
            for key in schema.get("required", []):
                if key not in value:
                    problems.append(f"{where}.{key}: required but missing")
            if schema.get("additionalProperties") is False:
                for key in sorted(value):
                    if key not in properties:
                        problems.append(f"{where}.{key}: unknown; expected one of "
                                        f"{sorted(properties)}")
            for key, subschema in properties.items():
                if key in value:
                    problems += validate(subschema, value[key], f"{where}.{key}")
            return problems

        if "enum" in schema and value not in schema["enum"]:
            problems.append(f"{where}: {value!r} is not one of {schema['enum']}")
        if "minimum" in schema and value < schema["minimum"]:
            problems.append(f"{where}: {value} is below minimum {schema['minimum']}")
        if "maximum" in schema and value > schema["maximum"]:
            problems.append(f"{where}: {value} is above maximum {schema['maximum']}")
        if "minLength" in schema and len(value) < schema["minLength"]:
            problems.append(f"{where}: shorter than minLength {schema['minLength']}")
        if "maxLength" in schema and len(value) > schema["maxLength"]:
            problems.append(f"{where}: longer than maxLength {schema['maxLength']}")
        return problems


    # ============================== the server ================================
    class JsonRpcError(Exception):
        """Raised inside a handler to become a JSON-RPC error object."""

        def __init__(self, code, message, data=None):
            super().__init__(message)
            self.code, self.message, self.data = code, message, data


    class MiniMCPServer:
        """An MCP-style server that speaks real JSON-RPC 2.0 over text lines.

        A production server reads those lines from stdin and writes them to
        stdout. Ours hands them to a client object in the same process, so the
        only thing missing is the pipe.
        """

        def __init__(self, name, version="1.0.0"):
            self.name, self.version = name, version
            self.tools, self.resources = {}, {}
            self.initialized = False
            self.diagnostics = []      # stands in for stderr — NEVER for stdout

        # ---- registration ----------------------------------------------------
        def add_tool(self, name, description, input_schema, fn):
            """Register one model-controlled tool."""
            self.tools[name] = {"description": description,
                                "inputSchema": input_schema, "fn": fn}

        def add_resource(self, uri, name, description, mime_type, reader):
            """Register one application-controlled, read-only resource."""
            self.resources[uri] = {"name": name, "description": description,
                                   "mimeType": mime_type, "read": reader}

        # ---- transport -------------------------------------------------------
        def handle_line(self, line):
            """One line of the transport in; one line out, or None for silence."""
            try:
                message = json.loads(line)
            except json.JSONDecodeError as exc:
                return json.dumps(
                    self._error(None, PARSE_ERROR, f"invalid JSON: {exc.msg}"))
            reply = self.handle(message)
            return None if reply is None else json.dumps(reply)

        # ---- dispatch --------------------------------------------------------
        def handle(self, message):
            """One JSON-RPC message in, one response dict out (None if silent)."""
            mid, method = message.get("id"), message.get("method")
            params = message.get("params", {})

            if message.get("jsonrpc") != "2.0":
                return self._error(mid, INVALID_REQUEST,
                                   "jsonrpc must be exactly '2.0'")
            if not isinstance(method, str):
                return self._error(mid, INVALID_REQUEST, "missing 'method' string")

            if mid is None:                     # a notification: act, stay silent
                if method == "notifications/initialized":
                    self.initialized = True
                    self.diagnostics.append("handshake complete")
                return None

            handlers = {"initialize": self._initialize,
                        "tools/list": self._tools_list,
                        "tools/call": self._tools_call,
                        "resources/list": self._resources_list,
                        "resources/read": self._resources_read}
            if method not in handlers:
                return self._error(mid, METHOD_NOT_FOUND,
                                   f"unknown method {method!r}",
                                   {"available": sorted(handlers)})
            if method != "initialize" and not self.initialized:
                return self._error(mid, INVALID_REQUEST,
                                   "connection is not initialized; send "
                                   "'initialize' and 'notifications/initialized'")
            try:
                return self._ok(mid, handlers[method](params))
            except JsonRpcError as exc:
                return self._error(mid, exc.code, exc.message, exc.data)
            except Exception as exc:            # a server must never fall over
                return self._error(mid, INTERNAL_ERROR,
                                   f"{type(exc).__name__}: {exc}")

        # ---- the five methods ------------------------------------------------
        def _initialize(self, params):
            asked = params.get("protocolVersion", PROTOCOL_VERSION)
            self.diagnostics.append(f"client speaks MCP {asked}")
            return {"protocolVersion": PROTOCOL_VERSION,
                    "capabilities": {"tools": {"listChanged": False},
                                     "resources": {"subscribe": False,
                                                   "listChanged": False}},
                    "serverInfo": {"name": self.name, "version": self.version}}

        def _tools_list(self, params):
            return {"tools": [{"name": name, "description": tool["description"],
                               "inputSchema": tool["inputSchema"]}
                              for name, tool in sorted(self.tools.items())]}

        def _tools_call(self, params):
            name, args = params.get("name"), params.get("arguments", {})
            if name not in self.tools:
                raise JsonRpcError(INVALID_PARAMS, f"no tool named {name!r}",
                                   {"available": sorted(self.tools)})
            problems = validate(self.tools[name]["inputSchema"], args)
            if problems:
                raise JsonRpcError(INVALID_PARAMS,
                                   "arguments do not match inputSchema",
                                   {"problems": problems})
            self.diagnostics.append(f"tools/call {name} {json.dumps(args)}")
            try:
                value = self.tools[name]["fn"](**args)
            except Exception as exc:
                # A tool that FAILS is a result the model should read and react
                # to — not a protocol error aimed at the host's programmer.
                return {"isError": True, "content": [
                    {"type": "text", "text": f"{type(exc).__name__}: {exc}"}]}
            return {"isError": False,
                    "content": [{"type": "text", "text": str(value)}]}

        def _resources_list(self, params):
            return {"resources": [
                {"uri": uri, "name": r["name"], "description": r["description"],
                 "mimeType": r["mimeType"]}
                for uri, r in sorted(self.resources.items())]}

        def _resources_read(self, params):
            uri = params.get("uri")
            if uri not in self.resources:
                raise JsonRpcError(INVALID_PARAMS, f"unknown resource {uri!r}",
                                   {"available": sorted(self.resources)})
            resource = self.resources[uri]
            return {"contents": [{"uri": uri, "mimeType": resource["mimeType"],
                                  "text": resource["read"]()}]}

        # ---- envelopes -------------------------------------------------------
        @staticmethod
        def _ok(mid, result):
            return {"jsonrpc": "2.0", "id": mid, "result": result}

        @staticmethod
        def _error(mid, code, message, data=None):
            error = {"code": code, "message": message}
            if data is not None:
                error["data"] = data
            return {"jsonrpc": "2.0", "id": mid, "error": error}


    # ============================== the client ================================
    class McpError(RuntimeError):
        """A JSON-RPC error object, raised on the host's side of the wire."""

        def __init__(self, error):
            super().__init__(f"{error['code']} {error['message']}")
            self.code, self.message = error["code"], error["message"]
            self.data = error.get("data")


    class MiniMCPClient:
        """The host's connector: one client, one server, one id counter."""

        def __init__(self, server, verbose=False):
            self.server, self.verbose = server, verbose
            self._next_id = 0
            self.server_info = None

        def _send(self, method, params=None, notification=False):
            message = {"jsonrpc": "2.0", "method": method}
            if params is not None:
                message["params"] = params
            if not notification:              # notifications carry no id, ever
                self._next_id += 1
                message["id"] = self._next_id
            line = json.dumps(message)
            self._show("-->", line)
            reply_line = self.server.handle_line(line)
            if reply_line is None:
                self._show("<--", "(silence — a notification never gets a reply)")
                return None
            self._show("<--", reply_line)
            reply = json.loads(reply_line)
            if reply.get("id") != message.get("id"):
                raise RuntimeError(f"id mismatch: sent {message.get('id')}, "
                                   f"got {reply.get('id')}")
            if "error" in reply:
                raise McpError(reply["error"])
            return reply["result"]

        def _show(self, arrow, text):
            if self.verbose:
                print(f"   {arrow} {text}")

        def initialize(self):
            """The handshake: no other message may be sent before it finishes."""
            result = self._send("initialize", {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {},
                "clientInfo": {"name": "handbook-host", "version": "0.1.0"}})
            self.server_info = result["serverInfo"]
            self._send("notifications/initialized", notification=True)
            return result

        def list_tools(self):
            return self._send("tools/list")["tools"]

        def call_tool(self, name, arguments):
            return self._send("tools/call",
                              {"name": name, "arguments": arguments})

        def list_resources(self):
            return self._send("resources/list")["resources"]

        def read_resource(self, uri):
            return self._send("resources/read", {"uri": uri})["contents"][0]


    # ======================= wiring the server together =======================
    def build_server():
        """A server exposing three tools and one resource per note."""
        server = MiniMCPServer("notes-server", "1.0.0")
        server.add_tool(
            "read_note",
            "Return the full text of one note. Paths are relative to the notes "
            "root, e.g. 'specs/retention.md'. Anything outside the root is "
            "refused; an unknown note is an error, not an empty string.",
            {"type": "object", "additionalProperties": False,
             "properties": {"path": {"type": "string", "minLength": 1,
                                     "maxLength": 120,
                                     "description": "Note path inside the root."}},
             "required": ["path"]},
            read_note)
        server.add_tool(
            "search_notes",
            "Case-insensitive search across every note. Returns one "
            "'path:line: text' row per hit, newest search first. Use this "
            "before read_note when you do not know the path.",
            {"type": "object", "additionalProperties": False,
             "properties": {"query": {"type": "string", "minLength": 2,
                                      "description": "Substring to look for."},
                            "limit": {"type": "integer", "minimum": 1,
                                      "maximum": 20,
                                      "description": "Maximum rows to return."}},
             "required": ["query"]},
            search_notes)
        server.add_tool(
            "calculate",
            "Evaluate one arithmetic expression over + - * / and parentheses, "
            "e.g. '500 * 0.023 * 18'. Numbers only: no variables, no units.",
            {"type": "object", "additionalProperties": False,
             "properties": {"expression": {"type": "string", "minLength": 1,
                                           "maxLength": 200,
                                           "description": "The expression."}},
             "required": ["expression"]},
            calculate)
        for path in sorted(NOTES):
            server.add_resource(
                f"note:///{path}", path,
                f"The note stored at {path}.", "text/markdown",
                (lambda p: lambda: NOTES[p])(path))
        return server


    # ============================== the FakeLLM ===============================
    class FakeLLM:
        """Deterministic stand-in for a real chat model API.

        Everything it knows about this server arrived over the protocol in
        `tools/list`. Every rule fires on something still MISSING from the
        transcript, so it reacts to what the server actually returned rather
        than replaying a fixed script.
        """

        def decide(self, transcript, tools):
            names = {tool["name"] for tool in tools}
            if "Observation:" not in transcript and "search_notes" in names:
                return {"tool": "search_notes",
                        "arguments": {"query": "retention", "limit": 3}}
            if "months" not in transcript:
                paths = re.findall(r"^(\S+?):\d+:", transcript, re.M)
                best = max(paths, key=lambda p: "retention" in p)
                return {"tool": "read_note", "arguments": {"path": best}}
            if "GB-month" not in transcript:
                return {"tool": "search_notes",
                        "arguments": {"query": "GB-month", "limit": 2}}
            months = re.search(r"(\d+) months", transcript).group(1)
            price = re.search(r"([\d.]+) USD per GB-month", transcript).group(1)
            if "Action: calculate" not in transcript:
                return {"tool": "calculate",
                        "arguments": {"expression": f"500 * {price} * {months}"}}
            total = float(re.findall(r"^Observation: ([\d.]+)$",
                                     transcript, re.M)[-1])
            return {"final": f"Raw events are kept for {months} months. Holding "
                             f"500 GB in cold storage that long costs "
                             f"${total:,.2f} at {price} USD per GB-month."}


    def run_over_mcp(question, client, llm, max_steps=6):
        """The host's tool loop. It names no tool: the menu arrives at runtime."""
        tools = client.list_tools()
        transcript = f"Question: {question}\n"
        for step in range(1, max_steps + 1):
            decision = llm.decide(transcript, tools)
            if "final" in decision:
                return decision["final"]
            name, args = decision["tool"], decision["arguments"]
            print(f"   step {step}: {name}({json.dumps(args)})")
            result = client.call_tool(name, args)
            text = result["content"][0]["text"]
            for line in text.splitlines():
                print(f"           | {line}")
            transcript += (f"Action: {name} {json.dumps(args)}\n"
                           f"Observation: {text}\n")
        raise RuntimeError(f"no answer within {max_steps} steps")


    # ================================ driver ==================================
    server = build_server()
    client = MiniMCPClient(server, verbose=True)

    print("1. handshake")
    info = client.initialize()
    print(f"      connected to {info['serverInfo']['name']} "
          f"{info['serverInfo']['version']}, MCP {info['protocolVersion']}, "
          f"capabilities {sorted(info['capabilities'])}")

    print("\n2. discovery")
    client.verbose = False
    for tool in client.list_tools():
        print(f"      tool     {tool['name']:<14} "
              f"required={tool['inputSchema']['required']}")
    for resource in client.list_resources():
        print(f"      resource {resource['uri']:<30} {resource['mimeType']}")
    first = client.read_resource("note:///specs/pricing.md")
    print(f"      read     {first['uri']} -> "
          f"{first['text'].splitlines()[0]!r}")

    print("\n3. schema validation at the boundary")
    attempts = [("search_notes", {"query": "retention"}),
                ("search_notes", {"query": "retention", "limit": 99}),
                ("search_notes", {"query": "x"}),
                ("search_notes", {"query": "retention", "lmit": 2}),
                ("search_notes", {"limit": 2}),
                ("calculate", {"expression": "2 +"})]
    for name, args in attempts:
        try:
            result = client.call_tool(name, args)
            flag = "TOOL FAILED" if result["isError"] else "ok"
            print(f"      {flag:<11} {name}({json.dumps(args)})")
            if result["isError"]:
                print(f"                  -> {result['content'][0]['text']}")
        except McpError as exc:
            print(f"      {exc.code:<11} {name}({json.dumps(args)})")
            for problem in exc.data.get("problems", [exc.message]):
                print(f"                  -> {problem}")

    print("\n4. the path-traversal guard")
    for attempt in ["meeting.md", "specs/retention.md", "./x/../todo.md",
                    "../../etc/passwd", "/etc/passwd", "specs/missing.md"]:
        result = client.call_tool("read_note", {"path": attempt})
        if result["isError"]:
            print(f"      DENY  {attempt:<22} {result['content'][0]['text']}")
        else:
            head = result["content"][0]["text"].splitlines()[0]
            print(f"      ALLOW {attempt:<22} {head!r}")

    print("\n5. every error code, on purpose")
    print(f"      {json.loads(server.handle_line('not json at all'))['error']}")
    fresh = MiniMCPServer("fresh", "1.0.0")
    early = fresh.handle({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
    print(f"      {early['error']['code']}  {early['error']['message']}")
    try:
        client._send("prompts/list")
    except McpError as exc:
        print(f"      {exc.code}  {exc.message} -> try {exc.data['available']}")
    try:
        client.call_tool("delete_everything", {})
    except McpError as exc:
        print(f"      {exc.code}  {exc.message} -> try {exc.data['available']}")
    silent = server.handle_line(json.dumps(
        {"jsonrpc": "2.0", "method": "tools/call",
         "params": {"name": "delete_everything"}}))
    print(f"      notification reply: {silent!r}  (no id, so no answer allowed)")

    print("\n6. a model driving the protocol")
    answer = run_over_mcp(
        "How long do we keep raw events, and what would 500 GB of cold "
        "storage cost for that period?", client, FakeLLM())
    print(f"\n   {answer}")
    print(f"\n   server diagnostics (stderr, never stdout): "
          f"{len(server.diagnostics)} lines")
    ```

    Break it on purpose: delete the `additionalProperties: False` line from
    `search_notes` and watch the `lmit` typo sail through and get silently
    ignored. Swap `isError` for a `JsonRpcError` in `_tools_call` and watch
    the model lose its ability to recover from a bad expression. Both are
    real bugs that ship regularly.

## Taking it real

Nothing above needs the network, which is why it runs in your browser. A
real server is a separate process, and the official SDKs remove almost all
of the code you just wrote — the framing, the handshake, the schema
generation — leaving you with the part that actually matters: the tools and
their descriptions.

The Python SDK's high-level API is **FastMCP**: type hints become the JSON
Schema, and the docstring becomes the description the model reads. This
needs `pip install "mcp[cli]"` and a real operating system, so it appears
here with no Run button:

```text
# notes_mcp/server.py
import logging
import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP

# On the stdio transport, stdout IS the protocol. Diagnostics go to stderr.
logging.basicConfig(stream=sys.stderr, level=logging.INFO)
log = logging.getLogger("notes")

mcp = FastMCP("notes")
NOTES_ROOT = Path("/srv/notes").resolve()


@mcp.tool()
def read_note(path: str) -> str:
    """Return the full text of one note.

    Paths are relative to the notes root, e.g. 'specs/retention.md'.
    A path outside the root is refused; an unknown note is an error,
    not an empty string.
    """
    candidate = (NOTES_ROOT / path).resolve()
    if candidate != NOTES_ROOT and NOTES_ROOT not in candidate.parents:
        raise ValueError(f"path escapes the notes root: {path!r}")
    log.info("read_note path=%s", path)
    return candidate.read_text(encoding="utf-8")


@mcp.resource("note:///{path}")
def note_resource(path: str) -> str:
    """Application-controlled read: the host attaches this when the user
    picks a note, rather than the model deciding to fetch it."""
    return read_note(path)


if __name__ == "__main__":
    mcp.run()          # stdio transport by default
```

The TypeScript SDK mirrors it, with **Zod** validators in place of type
hints. Note `z.number().int().min(1).max(20)` — that is milestone 2's
`minimum`/`maximum` check, expressed in a type system and compiled into the
schema the model sees:

```typescript
// src/server.ts — needs @modelcontextprotocol/sdk and zod
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const server = new McpServer({ name: "notes", version: "1.0.0" });

server.tool(
  "search_notes",
  "Case-insensitive search across every note. Returns one 'path:line: text' " +
    "row per hit. Use this before read_note when you do not know the path.",
  {
    query: z.string().min(2).describe("Substring to look for."),
    limit: z.number().int().min(1).max(20).default(3)
      .describe("Maximum rows to return."),
  },
  async ({ query, limit }) => {
    // console.log() would corrupt the stdio stream — use console.error().
    console.error(`search_notes query=${query}`);
    return { content: [{ type: "text", text: search(query, limit) }] };
  },
);

await server.connect(new StdioServerTransport());
```

A stdio server is not a service you start and leave running: the host
launches it as a child process and kills it on exit. You can still drive it
by hand to check that it starts and answers, which is the fastest way to
find a broken `initialize`:

```console
$ pip install "mcp[cli]"
$ python -m notes_mcp
# it is now waiting on stdin. Paste one line and press Enter:
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"manual","version":"0"}}}
{"jsonrpc":"2.0","id":1,"result":{"protocolVersion":"2025-06-18","capabilities":{"tools":{"listChanged":false},"resources":{"subscribe":false,"listChanged":false}},"serverInfo":{"name":"notes","version":"1.0.0"}}}
$ # ctrl-C to stop, then browse it in the official inspector instead:
$ npx @modelcontextprotocol/inspector python -m notes_mcp
```

!!! warning "`print()` is the first-day bug on stdio, and it blames the wrong file"

    On the stdio transport your server's **stdout is the protocol**: the
    client reads it line by line and parses each line as JSON-RPC. One
    stray `print("got here")` inserts `got here` into that stream, the
    client's `json.loads` fails on it, and the connection dies reporting a
    parse error that names *your debug line* as the malformed message.
    Send diagnostics to stderr — `logging.basicConfig(stream=sys.stderr)`
    in Python, `console.error` in Node. Over the HTTP transport the same
    `print` is harmless, which is why the bug seems to come and go when you
    move a server between hosts. Our reference server keeps a
    `self.diagnostics` list for exactly this reason: it is the stderr
    channel, and nothing in the protocol path ever writes to stdout.

## Going further

- **Pagination.** `tools/list`, `resources/list`, and `prompts/list` all
  accept an optional `cursor` param and may return a `nextCursor`. Add a
  page size of two, make `nextCursor` an opaque string (base64 of
  `{"offset": 2}` is the usual trick — opaque means clients cannot depend on
  its contents), and have the client loop until `nextCursor` is absent. Then
  make `search_notes` do the same, because a tool that can return the whole
  corpus eventually will.
- **Progress notifications.** A long-running tool can send
  `notifications/progress` messages carrying the `progressToken` the client
  put in `params._meta`. Give the client a callback list, have a slow tool
  emit three progress notifications, and confirm none of them gets a reply —
  they have no `id`, so they cannot.
- **An HTTP transport sketch.** Keep `handle_line` exactly as it is and put
  a different pipe in front of it: a function `post(body) -> str` standing in
  for one HTTP POST, and a session id echoed in a header dict. Write it as a
  `text` sketch rather than a real socket, and notice how little changes —
  that is the whole argument for separating the transport from the dispatch.
  Real deployments add what the pipe brings with it: authorization, origin
  checks, and per-session state.
- **The prompts primitive.** Add `prompts/list` and `prompts/get` — a
  user-invoked `review-retention` template that expands into messages. Now
  your server covers all three primitives, and the "who decides" table from
  [28.3](../../ch28-tools-mcp/03-mcp-protocol.md) is something you have
  implemented rather than read.
- **Conformance tests.** Turn the six acts of the driver into the two test
  families from
  [28.4](../../ch28-tools-mcp/04-building-mcp-server.md): protocol
  conformance (ids echo, notifications are silent, unknown methods are
  `-32601`) and tool contract (every tool has a schema and a description
  longer than twenty characters). The second one is a *policy* encoded as a
  test, and it fails the day somebody ships `"Searches."` as a description.
- **Two servers, one host.** Give the client a sibling — a second server
  exposing a `units` conversion tool — and merge both `tools/list` results
  into one menu, prefixing names with the server they came from. Your
  `run_over_mcp` loop should need no changes at all. That is the $M + N$
  argument from [28.3](../../ch28-tools-mcp/03-mcp-protocol.md), in code you
  wrote.
