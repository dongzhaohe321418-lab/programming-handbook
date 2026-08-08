# Chapter 28 · Exercises

## The chapter in brief

- A model cannot calculate, cannot know today's date, and has no hands — and
  all three gaps close the same way: **let it ask your program to run a
  function** ([28.1](01-function-calling.md)).
- The model never executes anything. It emits *text*; your dispatcher parses
  it, calls Python, and appends the result to the conversation.
- One round of tool use costs **two** model calls, because the model has to be
  shown the result before it can talk about it.
- A **JSON Schema** is the contract, and its `description` fields are a
  prompt: the model chooses tools by reading them.
- Your **dispatcher is the security boundary** — allowlist the tool name, the
  enum values, and the property names, and never `eval()` model output.
- "Reply in JSON" fails in a short, stable list of ways; syntax is repairable,
  but truncation must be **refused, never guessed**
  ([28.2](02-structured-output.md)).
- **Constrained decoding** sets forbidden logits to $-\infty$, so invalid
  tokens have probability exactly zero — a structural guarantee, not a
  statistical one.
- Constraints buy *syntax*, never *sense*, which is why validate-and-retry
  still earns its place alongside them.
- $M$ applications times $N$ systems is $M \times N$ integrations; a protocol
  in the middle makes it $M + N$ ([28.3](03-mcp-protocol.md)).
- **MCP** speaks JSON-RPC 2.0 over stdio or HTTP, and its three primitives —
  tools, resources, prompts — are sorted by *who decides to use them*.
- A **notification has no `id`** and gets no reply; a tool that merely failed
  returns `isError: true`, not a JSON-RPC error.
- A real server is an ordinary project with an SDK, narrow idempotent tools,
  paginated results, tests over dicts, logs on stderr, and resolved paths
  ([28.4](04-building-mcp-server.md)).

### Key terms

| Term | One-clause reminder |
| --- | --- |
| [Function calling](../appendix/E-ai-glossary.md) | The model emits a tool name and arguments; your code runs the tool |
| [Tool use](../appendix/E-ai-glossary.md) | The same idea, named from the model's side |
| [JSON Schema](../appendix/E-ai-glossary.md) | A JSON document describing the shape of other JSON documents |
| `enum` | An allowlist of legal values, enforceable by your validator |
| `additionalProperties: false` | Reject any field the schema did not name |
| Dispatcher | The function that maps a validated tool name to a real Python call |
| Confused deputy | A trusted component acting on an attacker's instructions it cannot distinguish from yours |
| [Structured output](../appendix/E-ai-glossary.md) | Getting a model to emit parseable, schema-conforming data |
| [Constrained decoding](../appendix/E-ai-glossary.md) | Masking logits so ungrammatical tokens can never be sampled |
| [MCP](../appendix/E-ai-glossary.md) | Model Context Protocol: an open standard for connecting hosts to capabilities |
| [JSON-RPC 2.0](../appendix/E-ai-glossary.md) | The request / response / notification message format MCP uses |
| Host, client, server | The app the user runs, its per-connection connector, and the capability provider |
| Notification | A request with no `id`, and therefore no reply |
| Capability negotiation | The `initialize` exchange in which both sides declare what they support |
| `isError: true` | A tool that ran and failed — a result for the model, not a protocol error |

The [concept index](../concept-index.md) points each of these at the section
where it is built.

Now the problems.

Eight problems on schemas, structured output, and the protocol. They build on
[28.1](01-function-calling.md), [28.2](02-structured-output.md),
[28.3](03-mcp-protocol.md), and [28.4](04-building-mcp-server.md), and every
solution runs in the browser. Exercise 28.3 asks you to *predict* the output
before you run it — write your answer down first; the gap between your
prediction and the printed result is where the learning is.

Nothing here calls a model or touches the network. Where a model is needed it
is a scripted `FakeLLM`, and where a server is needed it is the
`MiniMCPServer` from Section 28.3, condensed so each solution stands alone.

---

### Exercise 28.1 — Write the schema (●)

Here is a function a model should be able to call:

```text
def book_room(room, date, start_hour, duration_hours=1,
              attendees=None, notify=True):
    """Reserve a meeting room. Rooms are 'blue', 'green', 'atrium'.
    start_hour is a whole hour from 8 to 20 inclusive; duration_hours is
    1 to 4; attendees is a list of email addresses."""
```

Write the full tool definition — `name`, `description`, and an
`input_schema` with types, `enum`s, bounds, `required`, and
`additionalProperties: false`. Give every property a description written for
the model, not for a human reading your source. Then validate these four
calls with the validator from Section 28.1 and check you reject the right
ones:

1. `{"room": "blue", "date": "2026-03-04", "start_hour": 9}`
2. the same, plus `duration_hours`, `attendees`, and `notify`
3. `{"room": "cellar", "date": "2026-03-04", "start_hour": 7, "duration_hours": 1.5, "attendees": "ada@example.com", "room_id": 3}`
4. `{"date": "2026-03-04"}`

??? success "Solution"

    ```python
    def validate(value, schema, path="$"):
        """The validator from 28.1, unchanged."""
        errors = []
        py_types = {"object": dict, "array": list, "string": str,
                    "number": (int, float), "integer": int, "boolean": bool}
        expected = schema.get("type")
        if expected is not None:
            ok = isinstance(value, py_types[expected])
            if expected in ("number", "integer") and isinstance(value, bool):
                ok = False
            if not ok:
                return [f"{path}: expected {expected}, "
                        f"got {type(value).__name__}"]
        if expected == "object":
            for key in schema.get("required", []):
                if key not in value:
                    errors.append(f"{path}: missing required property '{key}'")
            props = schema.get("properties", {})
            for key, sub in value.items():
                if key in props:
                    errors += validate(sub, props[key], f"{path}.{key}")
                elif schema.get("additionalProperties") is False:
                    errors.append(f"{path}: unexpected property '{key}'")
        if expected == "array" and "items" in schema:
            for i, item in enumerate(value):
                errors += validate(item, schema["items"], f"{path}[{i}]")
        if "enum" in schema and value not in schema["enum"]:
            errors.append(f"{path}: {value!r} is not one of {schema['enum']}")
        if "minimum" in schema and isinstance(value, (int, float)):
            if value < schema["minimum"]:
                errors.append(f"{path}: {value} is below minimum "
                              f"{schema['minimum']}")
        if "maximum" in schema and isinstance(value, (int, float)):
            if value > schema["maximum"]:
                errors.append(f"{path}: {value} is above maximum "
                              f"{schema['maximum']}")
        return errors


    book_room_schema = {
        "name": "book_room",
        "description": ("Reserve a meeting room for a block of whole hours "
                        "on one day. Creates a real booking and emails the "
                        "attendees, so check availability first."),
        "input_schema": {
            "type": "object",
            "properties": {
                "room": {"type": "string",
                         "enum": ["blue", "green", "atrium"],
                         "description": "Which room to book."},
                "date": {"type": "string",
                         "description": "The day, as YYYY-MM-DD."},
                "start_hour": {"type": "integer", "minimum": 8, "maximum": 20,
                               "description": "Start time on a 24-hour "
                                              "clock, 8 to 20 inclusive."},
                "duration_hours": {"type": "integer", "minimum": 1,
                                   "maximum": 4,
                                   "description": "Length in whole hours, "
                                                  "1 to 4. Defaults to 1."},
                "attendees": {"type": "array",
                              "items": {"type": "string"},
                              "description": "Email addresses to invite."},
                "notify": {"type": "boolean",
                           "description": "Send the invitations now?"},
            },
            "required": ["room", "date", "start_hour"],
            "additionalProperties": False,
        },
    }

    calls = [
        {"room": "blue", "date": "2026-03-04", "start_hour": 9},
        {"room": "blue", "date": "2026-03-04", "start_hour": 9,
         "duration_hours": 2, "attendees": ["ada@example.com"],
         "notify": True},
        {"room": "cellar", "date": "2026-03-04", "start_hour": 7,
         "duration_hours": 1.5, "attendees": "ada@example.com", "room_id": 3},
        {"date": "2026-03-04"},
    ]
    for i, call in enumerate(calls, 1):
        problems = validate(call, book_room_schema["input_schema"])
        print(f"call {i}: {'VALID' if not problems else 'REJECTED'}")
        for p in problems:
            print("   ", p)
    ```

    Calls 1 and 2 pass. Call 3 collects five separate complaints — a room
    outside the enum, an hour below the minimum, a float where an integer
    was required, a bare string where an array was required, and an invented
    property. Call 4 reports the two missing required fields. Every one of
    those is a mistake a real model makes; the schema turns each into a
    message it can act on.

---

### Exercise 28.2 — Find the bugs in this schema (●)

This weather tool "works in testing" and misbehaves in production. There are
four problems. Find them, write the fixed schema, and demonstrate with the
validator that the fixed version catches a bad model reply the buggy one
waves through.

```text
{
  "type": "object",
  "properties": {
    "city": {"type": "string"},
    "days": {"type": "number", "minimum": 1},
    "unit": {"type": "string", "description": "celsius or fahrenheit"}
  },
  "required": ["city", "days", "unit", "country"]
}
```

??? success "Solution"

    The four bugs: (1) `required` names `country`, which is not in
    `properties` at all — the model is asked for a field that is never
    described and never validated; (2) `days` is `number`, so `3.5` days is
    legal; (3) `unit` puts its allowed values in prose instead of an `enum`,
    so `"F"` sails through; (4) there is no `additionalProperties: false`, so
    a typo'd property is silently accepted. A fifth, softer problem: `city`
    and `days` have no descriptions.

    ```python
    def validate(value, schema, path="$"):
        errors = []
        py_types = {"object": dict, "array": list, "string": str,
                    "number": (int, float), "integer": int, "boolean": bool}
        expected = schema.get("type")
        if expected is not None:
            ok = isinstance(value, py_types[expected])
            if expected in ("number", "integer") and isinstance(value, bool):
                ok = False
            if not ok:
                return [f"{path}: expected {expected}, "
                        f"got {type(value).__name__}"]
        if expected == "object":
            for key in schema.get("required", []):
                if key not in value:
                    errors.append(f"{path}: missing required property '{key}'")
            props = schema.get("properties", {})
            for key, sub in value.items():
                if key in props:
                    errors += validate(sub, props[key], f"{path}.{key}")
                elif schema.get("additionalProperties") is False:
                    errors.append(f"{path}: unexpected property '{key}'")
        if "enum" in schema and value not in schema["enum"]:
            errors.append(f"{path}: {value!r} is not one of {schema['enum']}")
        if "minimum" in schema and isinstance(value, (int, float)):
            if value < schema["minimum"]:
                errors.append(f"{path}: {value} is below minimum "
                              f"{schema['minimum']}")
        if "maximum" in schema and isinstance(value, (int, float)):
            if value > schema["maximum"]:
                errors.append(f"{path}: {value} is above maximum "
                              f"{schema['maximum']}")
        return errors


    buggy = {
        "type": "object",
        "properties": {
            "city": {"type": "string"},
            "days": {"type": "number", "minimum": 1},
            "unit": {"type": "string",
                     "description": "celsius or fahrenheit"},
        },
        "required": ["city", "days", "unit", "country"],
    }

    fixed = {
        "type": "object",
        "properties": {
            "city": {"type": "string",
                     "description": "City name, e.g. 'Oslo'."},
            "country": {"type": "string",
                        "description": "ISO 3166-1 alpha-2 country code, "
                                       "e.g. 'NO'. Disambiguates city names."},
            "days": {"type": "integer", "minimum": 1, "maximum": 14,
                     "description": "Days of forecast to return, 1 to 14."},
            "unit": {"type": "string", "enum": ["celsius", "fahrenheit"],
                     "description": "Temperature unit for the result."},
        },
        "required": ["city", "country", "days", "unit"],
        "additionalProperties": False,
    }

    model_output = {"city": "Oslo", "days": 3.5, "unit": "F", "unots": "F"}
    print("against the buggy schema:")
    for p in validate(model_output, buggy):
        print("   ", p)
    print("\nagainst the fixed schema:")
    for p in validate(model_output, fixed):
        print("   ", p)
    ```

    The buggy schema finds one problem; the fixed one finds four. The extra
    three are exactly the failures that reach production: a fractional day
    count, an abbreviation the backend does not understand, and a misspelled
    property that silently does nothing.

---

### Exercise 28.3 — Predict the validator's output (●)

**Predict before running.** Given this schema:

```text
{"type": "object",
 "properties": {"sku":     {"type": "string", "enum": ["widget", "gizmo"]},
                "units":   {"type": "integer", "minimum": 1},
                "express": {"type": "boolean"}},
 "required": ["sku", "units"],
 "additionalProperties": false}
```

write down how many problems the Section 28.1 validator reports for each of
these four payloads, and what each problem is:

1. `{"sku": "widget", "units": 3}`
2. `{"sku": "gizmo", "units": True}`
3. `{"sku": "sprocket", "units": 0, "rush": True}`
4. `{"units": 5, "express": "yes"}`

Then run the block.

??? success "Solution"

    Expected: **0, 1, 3, 2**.

    ```python
    def validate(value, schema, path="$"):
        errors = []
        py_types = {"object": dict, "array": list, "string": str,
                    "number": (int, float), "integer": int, "boolean": bool}
        expected = schema.get("type")
        if expected is not None:
            ok = isinstance(value, py_types[expected])
            if expected in ("number", "integer") and isinstance(value, bool):
                ok = False
            if not ok:
                return [f"{path}: expected {expected}, "
                        f"got {type(value).__name__}"]
        if expected == "object":
            for key in schema.get("required", []):
                if key not in value:
                    errors.append(f"{path}: missing required property '{key}'")
            props = schema.get("properties", {})
            for key, sub in value.items():
                if key in props:
                    errors += validate(sub, props[key], f"{path}.{key}")
                elif schema.get("additionalProperties") is False:
                    errors.append(f"{path}: unexpected property '{key}'")
        if "enum" in schema and value not in schema["enum"]:
            errors.append(f"{path}: {value!r} is not one of {schema['enum']}")
        if "minimum" in schema and isinstance(value, (int, float)):
            if value < schema["minimum"]:
                errors.append(f"{path}: {value} is below minimum "
                              f"{schema['minimum']}")
        return errors


    schema = {
        "type": "object",
        "properties": {
            "sku": {"type": "string", "enum": ["widget", "gizmo"]},
            "units": {"type": "integer", "minimum": 1},
            "express": {"type": "boolean"},
        },
        "required": ["sku", "units"],
        "additionalProperties": False,
    }

    payloads = [
        {"sku": "widget", "units": 3},
        {"sku": "gizmo", "units": True},
        {"sku": "sprocket", "units": 0, "rush": True},
        {"units": 5, "express": "yes"},
    ]
    for i, payload in enumerate(payloads, 1):
        problems = validate(payload, schema)
        print(f"payload {i}: {len(problems)} problem(s)")
        for p in problems:
            print("     ", p)
    ```

    The one most people miss is payload 2. In Python `True` **is** an `int`
    — `isinstance(True, int)` is `True` — so a naive type check would accept
    it. JSON Schema treats booleans and integers as different types, which
    is why the validator has that explicit `isinstance(value, bool)` guard.
    Payload 3 fails three ways at once (enum, minimum, unexpected property);
    payload 4 misses a required field and has a string where a boolean
    belongs.

---

### Exercise 28.4 — The unknown-method error response (●)

Your server implements `initialize`, `tools/list`, and `tools/call`. Write
`method_not_found(request)` returning the correct JSON-RPC 2.0 response for a
method you do not have: right reserved code, the request's `id` echoed back,
a useful `message`, and `data` listing what you *do* support. Handle the case
where the incoming message is a notification. Test it on
`resources/read` with `id: 7`, the same request with no `id`, and
`prompts/get` with the string id `"abc-1"`.

??? success "Solution"

    ```python
    import json

    RESERVED = {-32700: "Parse error", -32600: "Invalid Request",
                -32601: "Method not found", -32602: "Invalid params",
                -32603: "Internal error"}
    IMPLEMENTED = ["initialize", "tools/list", "tools/call"]


    def method_not_found(request):
        """The JSON-RPC response for a method this server does not have.
        Returns None for a notification — those never get a reply."""
        mid = request.get("id")
        if mid is None:
            return None
        return {"jsonrpc": "2.0",
                "id": mid,
                "error": {"code": -32601,
                          "message": f"Method not found: "
                                     f"{request.get('method')!r}",
                          "data": {"available": IMPLEMENTED}}}


    requests = [
        {"jsonrpc": "2.0", "id": 7, "method": "resources/read",
         "params": {"uri": "file:///etc/passwd"}},
        {"jsonrpc": "2.0", "method": "resources/read"},        # notification
        {"jsonrpc": "2.0", "id": "abc-1", "method": "prompts/get"},
    ]
    for req in requests:
        reply = method_not_found(req)
        print(json.dumps(reply) if reply is not None
              else "(notification: no reply is permitted)")

    print()
    print("code -32601 is reserved for:", RESERVED[-32601])
    ```

    Three details are easy to get wrong. The response carries `error` and
    **no** `result` — a JSON-RPC response has exactly one of them. The `id`
    is echoed *unchanged*, including its type: `7` stays an integer and
    `"abc-1"` stays a string. And a notification gets nothing at all, not
    even an error, because there is no `id` to correlate a reply with.

---

### Exercise 28.5 — Repair a model's JSON (●●)

Write `repair(text)` that recovers a JSON object from a model reply. It must
handle a markdown fence, prose before and after, a trailing comma, and
Python-literal syntax — and it must **raise** on a reply that was truncated
rather than inventing the missing data. One extra trap beyond Section 28.2:
a `}` inside a string value must not end the object early.

Test it on: plain JSON, a chatty preamble, a fenced block, a trailing comma,
Python literals, a nested object with chatter on both sides, an object whose
string value contains `}`, and a truncated reply.

??? success "Solution"

    ```python
    import ast
    import json
    import re

    def repair(text):
        """Recover a JSON object from a model reply, or raise."""
        fenced = re.search(r"```(?:json|JSON)?\s*(.*?)```", text, re.DOTALL)
        if fenced:
            text = fenced.group(1)
        start = text.find("{")
        if start == -1:
            raise ValueError("no object in reply")
        depth, end = 0, None
        in_string = escaped = False
        for i in range(start, len(text)):
            ch = text[i]
            if in_string:                    # inside "...": braces are data
                if escaped:
                    escaped = False
                elif ch == "\\":
                    escaped = True
                elif ch == '"':
                    in_string = False
                continue
            if ch == '"':
                in_string = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break
        if end is None:
            raise ValueError("unbalanced braces: the reply was cut off")
        candidate = re.sub(r",\s*([}\]])", r"\1", text[start:end])
        try:
            return json.loads(candidate)
        except ValueError:
            pass
        try:
            value = ast.literal_eval(candidate)   # literals only, never eval
        except (ValueError, SyntaxError) as exc:
            raise ValueError(f"unrepairable: {exc}") from None
        if not isinstance(value, dict):
            raise ValueError("not an object")
        return value


    replies = [
        ("plain", '{"ticket": 91, "status": "open"}'),
        ("preamble", 'Of course! Here you go:\n{"ticket": 91, "status": "open"}'),
        ("fenced", '```json\n{"ticket": 91, "status": "open"}\n```'),
        ("trailing comma", '{"ticket": 91, "status": "open",}'),
        ("python literals",
         "{'ticket': 91, 'status': 'open', 'urgent': False}"),
        ("nested + chatter",
         'Result:\n{"ticket": 91, "meta": {"tags": ["bug",]}}\nHope that helps!'),
        ("brace in a string", '{"ticket": 91, "note": "use } carefully"}'),
        ("truncated", '{"ticket": 91, "status":'),
    ]
    for label, text in replies:
        try:
            print(f"{label:18} -> {repair(text)}")
        except ValueError as exc:
            print(f"{label:18} -> REJECTED ({exc})")
    ```

    Seven recovered, one refused. The string-aware brace counter is the
    addition: without the `in_string` flag, `"use } carefully"` would end
    the object at the `}` inside the quotes and produce
    `{"ticket": 91, "note": "use }` — invalid JSON, from valid input. And
    the truncated reply is still rejected, because syntax is repairable and
    missing data is not.

---

### Exercise 28.6 — Add a tool to the mini server (●●)

Register a third tool, `low_stock`, on the `MiniMCPServer` from Section 28.3.
It takes an integer `threshold` and returns the sorted list of SKUs with
strictly fewer than that many units. Write the schema (bounds included) and a
description a model can act on, then exercise it over JSON-RPC with a normal
call, a call that returns nothing, a call missing its argument, and a call
whose argument is legal per the schema but rejected by the tool.

??? success "Solution"

    ```python
    import json

    class MiniMCPServer:
        """The 28.3 server, condensed to what this exercise needs."""

        def __init__(self, name="inventory-server", version="1.0.0"):
            self.name, self.version, self.tools = name, version, {}

        def add_tool(self, name, description, input_schema, fn):
            self.tools[name] = {"description": description,
                                "inputSchema": input_schema, "fn": fn}

        def handle(self, msg):
            mid = msg.get("id")
            method, params = msg.get("method"), msg.get("params", {})
            if mid is None:
                return None
            if method == "tools/list":
                return self._ok(mid, {"tools": [
                    {"name": n, "description": t["description"],
                     "inputSchema": t["inputSchema"]}
                    for n, t in sorted(self.tools.items())]})
            if method == "tools/call":
                name, args = params.get("name"), params.get("arguments", {})
                if name not in self.tools:
                    return self._err(mid, -32602, f"no tool named {name!r}",
                                     {"available": sorted(self.tools)})
                required = self.tools[name]["inputSchema"].get("required", [])
                missing = [k for k in required if k not in args]
                if missing:
                    return self._err(mid, -32602,
                                     "missing required arguments",
                                     {"missing": missing})
                try:
                    value = self.tools[name]["fn"](**args)
                except Exception as exc:
                    return self._ok(mid, {"isError": True, "content": [
                        {"type": "text",
                         "text": f"{type(exc).__name__}: {exc}"}]})
                return self._ok(mid, {"isError": False, "content": [
                    {"type": "text", "text": str(value)}]})
            return self._err(mid, -32601, f"unknown method: {method!r}")

        @staticmethod
        def _ok(mid, result):
            return {"jsonrpc": "2.0", "id": mid, "result": result}

        @staticmethod
        def _err(mid, code, message, data=None):
            err = {"code": code, "message": message}
            if data is not None:
                err["data"] = data
            return {"jsonrpc": "2.0", "id": mid, "error": err}


    INVENTORY = {"widget": 42, "gizmo": 7, "sprocket": 0, "flange": 118}

    def low_stock(threshold):
        if threshold < 0:
            raise ValueError("threshold must be zero or more")
        return sorted(s for s, n in INVENTORY.items() if n < threshold)

    server = MiniMCPServer()
    server.add_tool(
        "low_stock",
        "List every SKU whose warehouse quantity is strictly below a "
        "threshold. Use this to decide what to reorder; it returns an empty "
        "list when everything is well stocked.",
        {"type": "object",
         "properties": {"threshold": {"type": "integer", "minimum": 0,
                                      "description": "Report SKUs with "
                                                     "fewer than this many "
                                                     "units."}},
         "required": ["threshold"]},
        low_stock)

    def call(mid, name, arguments):
        return server.handle({"jsonrpc": "2.0", "id": mid,
                              "method": "tools/call",
                              "params": {"name": name,
                                         "arguments": arguments}})

    listed = server.handle({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
    tool = listed["result"]["tools"][0]
    print("tools/list advertises:", tool["name"])
    print("  required:", tool["inputSchema"]["required"])
    print()
    print(json.dumps(call(2, "low_stock", {"threshold": 10})))
    print(json.dumps(call(3, "low_stock", {"threshold": 0})))
    print(json.dumps(call(4, "low_stock", {})))
    print(json.dumps(call(5, "low_stock", {"threshold": -5})))
    ```

    Note the two different failures at the end. The missing argument comes
    back as JSON-RPC error $-32602$, because the request never satisfied the
    schema. The negative threshold *does* satisfy the schema's `required`
    check, reaches the function, and fails there — so it comes back as a
    normal result with `isError: true`, which is the form the model can read
    and correct. (Our condensed server only enforces `required`; the
    `minimum: 0` in the schema is what a full validator would have caught
    first.)

---

### Exercise 28.7 — Paginate `tools/list` (●●)

A server with hundreds of tools should not return them all in one message.
The MCP list methods take an optional `cursor` param and may return a
`nextCursor` in the result; when `nextCursor` is absent, you are on the last
page. Subclass the mini server so `tools/list` returns two tools per page
with an **opaque** cursor (encode the offset — clients must never parse it),
and reject a malformed cursor with $-32602$. Drive it with a loop that
collects every page.

??? success "Solution"

    ```python
    import base64
    import json

    class MiniMCPServer:
        def __init__(self, name="paged-server", version="1.0.0"):
            self.name, self.version, self.tools = name, version, {}

        def add_tool(self, name, description, input_schema, fn):
            self.tools[name] = {"description": description,
                                "inputSchema": input_schema, "fn": fn}

        def handle(self, msg):
            mid = msg.get("id")
            if mid is None:
                return None
            if msg.get("method") == "tools/list":
                return self._ok(mid, {"tools": [
                    {"name": n, "description": t["description"],
                     "inputSchema": t["inputSchema"]}
                    for n, t in sorted(self.tools.items())]})
            return self._err(mid, -32601, f"unknown method: "
                                          f"{msg.get('method')!r}")

        @staticmethod
        def _ok(mid, result):
            return {"jsonrpc": "2.0", "id": mid, "result": result}

        @staticmethod
        def _err(mid, code, message, data=None):
            err = {"code": code, "message": message}
            if data is not None:
                err["data"] = data
            return {"jsonrpc": "2.0", "id": mid, "error": err}


    class PagedMCPServer(MiniMCPServer):
        """tools/list with an opaque cursor, as the MCP spec describes it."""

        PAGE_SIZE = 2

        @staticmethod
        def _encode(offset):
            return base64.urlsafe_b64encode(
                json.dumps({"offset": offset}).encode()).decode()

        @staticmethod
        def _decode(cursor):
            raw = base64.urlsafe_b64decode(cursor.encode())
            return json.loads(raw)["offset"]

        def handle(self, msg):
            if msg.get("method") != "tools/list" or msg.get("id") is None:
                return super().handle(msg)
            cursor = msg.get("params", {}).get("cursor")
            try:
                offset = 0 if cursor is None else self._decode(cursor)
            except Exception:
                return self._err(msg["id"], -32602,
                                 f"invalid cursor {cursor!r}")
            names = sorted(self.tools)
            page = names[offset:offset + self.PAGE_SIZE]
            result = {"tools": [{"name": n,
                                 "description": self.tools[n]["description"],
                                 "inputSchema": self.tools[n]["inputSchema"]}
                                for n in page]}
            if offset + self.PAGE_SIZE < len(names):
                result["nextCursor"] = self._encode(offset + self.PAGE_SIZE)
            return self._ok(msg["id"], result)


    server = PagedMCPServer()
    for name in ["alpha", "bravo", "charlie", "delta", "echo"]:
        server.add_tool(name, f"Demo tool {name}.",
                        {"type": "object", "properties": {}, "required": []},
                        lambda: None)

    cursor, page_no, seen = None, 0, []
    while True:
        page_no += 1
        params = {} if cursor is None else {"cursor": cursor}
        reply = server.handle({"jsonrpc": "2.0", "id": page_no,
                               "method": "tools/list", "params": params})
        got = [t["name"] for t in reply["result"]["tools"]]
        seen += got
        cursor = reply["result"].get("nextCursor")
        print(f"page {page_no}: {got}  nextCursor={cursor}")
        if cursor is None:
            break

    print("\nall tools, in order:", seen)
    bad = server.handle({"jsonrpc": "2.0", "id": 9, "method": "tools/list",
                         "params": {"cursor": "not-a-cursor"}})
    print("bad cursor ->", json.dumps(bad["error"]))
    ```

    Three pages of 2, 2, 1, and the loop terminates because the last page
    omits `nextCursor` — not because it counted. That is the contract: the
    client keeps going while a cursor comes back and stops when one does
    not, which lets the server change its page size, or switch from offsets
    to keyset pagination, without any client changing. Base64-encoding a
    JSON blob is not encryption and not security; it is a way to make the
    cursor visibly opaque so nobody is tempted to do arithmetic on it.

---

### Exercise 28.8 — Implement the `resources/read` primitive (●●●)

Give the mini server the second MCP primitive. Add `resources/list` (returning
each resource's `uri`, `name`, `description`, and `mimeType`) and
`resources/read` (returning a `contents` array of `{uri, mimeType, text}`),
and advertise the new capability in the `initialize` handshake so a client
knows the methods exist. Enforce three rules: a missing `uri` is $-32602$; a
URI that is not in your registry is $-32602$ with the available list in
`data` — never a filesystem lookup — and existing methods keep working
untouched. Then show a private URI being refused.

??? success "Solution"

    ```python
    import json

    class MiniMCPServer:
        """The 28.3 server, condensed."""

        def __init__(self, name="mini", version="1.0.0"):
            self.name, self.version, self.tools = name, version, {}

        def handle(self, msg):
            mid, method = msg.get("id"), msg.get("method")
            if mid is None:
                return None
            if method == "initialize":
                return self._ok(mid, {
                    "protocolVersion": "2025-06-18",
                    "capabilities": {"tools": {"listChanged": False}},
                    "serverInfo": {"name": self.name,
                                   "version": self.version}})
            if method == "tools/list":
                return self._ok(mid, {"tools": sorted(self.tools)})
            return self._err(mid, -32601, f"unknown method: {method!r}")

        @staticmethod
        def _ok(mid, result):
            return {"jsonrpc": "2.0", "id": mid, "result": result}

        @staticmethod
        def _err(mid, code, message, data=None):
            err = {"code": code, "message": message}
            if data is not None:
                err["data"] = data
            return {"jsonrpc": "2.0", "id": mid, "error": err}


    NOTES = {
        "notes://team/standup": "Mon: shipped the parser.\nTue: fixed a bug.",
        "notes://team/retro": "Went well: tests. Try next: smaller tools.",
        "notes://private/salaries": "SHOULD NOT BE REACHABLE",
    }


    class ResourceMCPServer(MiniMCPServer):
        """Adds the resources primitive: resources/list and resources/read."""

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.resources = {}

        def add_resource(self, uri, name, description, mime_type, reader):
            self.resources[uri] = {"name": name, "description": description,
                                   "mimeType": mime_type, "reader": reader}

        def handle(self, msg):
            mid, method = msg.get("id"), msg.get("method")
            params = msg.get("params", {})
            if mid is None:
                return None

            if method == "initialize":
                # Capability negotiation: say what we actually implement.
                reply = super().handle(msg)
                reply["result"]["capabilities"]["resources"] = {
                    "subscribe": False, "listChanged": False}
                return reply

            if method == "resources/list":
                return self._ok(mid, {"resources": [
                    {"uri": u, "name": r["name"],
                     "description": r["description"], "mimeType": r["mimeType"]}
                    for u, r in sorted(self.resources.items())]})

            if method == "resources/read":
                uri = params.get("uri")
                if uri is None:
                    return self._err(mid, -32602,
                                     "resources/read requires a 'uri'")
                if uri not in self.resources:      # allowlist, never a lookup
                    return self._err(mid, -32602, f"unknown resource {uri!r}",
                                     {"available": sorted(self.resources)})
                res = self.resources[uri]
                try:
                    text = res["reader"]()
                except Exception as exc:
                    return self._err(mid, -32603,
                                     f"{type(exc).__name__}: {exc}")
                return self._ok(mid, {"contents": [
                    {"uri": uri, "mimeType": res["mimeType"], "text": text}]})

            return super().handle(msg)          # everything else, unchanged


    server = ResourceMCPServer("notes-server")
    for uri in ["notes://team/standup", "notes://team/retro"]:
        server.add_resource(uri, uri.rsplit("/", 1)[1],
                            f"Team note at {uri}.", "text/markdown",
                            lambda u=uri: NOTES[u])

    def show(msg):
        print(f"--> {json.dumps(msg)}")
        print(f"<-- {json.dumps(server.handle(msg))}")
        print()

    show({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
    show({"jsonrpc": "2.0", "id": 2, "method": "resources/list"})
    show({"jsonrpc": "2.0", "id": 3, "method": "resources/read",
          "params": {"uri": "notes://team/retro"}})
    show({"jsonrpc": "2.0", "id": 4, "method": "resources/read",
          "params": {"uri": "notes://private/salaries"}})
    show({"jsonrpc": "2.0", "id": 5, "method": "resources/read", "params": {}})
    show({"jsonrpc": "2.0", "id": 6, "method": "tools/list"})
    ```

    Three things are worth pointing at. The `initialize` reply now carries a
    `resources` capability alongside `tools` — that is how a client learns
    these methods exist, instead of discovering it from a $-32601$. The
    registry is an **allowlist**: `notes://private/salaries` exists in the
    `NOTES` dict but was never registered, so it is refused with the same
    message as a URI that does not exist at all, and no attacker learns
    which private URIs are real. And `tools/list` still answers, because the
    final `return super().handle(msg)` passes every unrecognised method back
    to the parent — the extension adds behaviour without touching what was
    already there.
