# 28.4 Writing a real MCP server

The server in [Section 28.3](03-mcp-protocol.md) is honest about its
messages and dishonest about everything else: it lives in the same process as
its client, it implements three methods, and nobody outside this page can use
it. A real MCP server is a separate program that talks over a pipe or a
socket, that any compliant host can launch, and that has to survive being
handed garbage by a model. This section is about the distance between those
two things — the SDKs, the transport, the design decisions, the tests, and
the security work.

## Project layout

An MCP server is an ordinary Python (or Node) project. Nothing exotic:

```text
inventory-mcp/
├── pyproject.toml           # declares the `mcp` dependency and an entry point
├── README.md                # what the tools do, and what permissions they need
├── src/
│   └── inventory_mcp/
│       ├── __init__.py
│       ├── __main__.py      # `python -m inventory_mcp` starts the server
│       ├── server.py        # tool/resource/prompt definitions
│       └── db.py            # the actual work: queries, files, HTTP
└── tests/
    └── test_server.py       # protocol conformance + tool behaviour
```

The important line in that tree is the split between `server.py` and `db.py`.
Protocol code should contain no business logic and business logic should know
nothing about MCP — then you can test the logic without a protocol and the
protocol without a database.

## The Python SDK

The official Python SDK is the `mcp` package. Its high-level API, **FastMCP**,
turns a decorated function into a fully described tool: the parameter type
hints become the JSON Schema, and the docstring becomes the `description`
that the model reads.

!!! warning "This block has no Run button, and that is deliberate"
    The `mcp` package is not available in your browser — it needs a real
    Python install (`pip install "mcp[cli]"`) and a real operating system to
    talk to. The code below is complete and correct in shape, but it is shown
    in a plain text box so it is never executed here. SDK APIs also drift
    between versions; check the package's own README for the current import
    paths before copying.

```text
# src/inventory_mcp/server.py
import logging
import sys

from mcp.server.fastmcp import FastMCP

# stdio transport: stdout belongs to the protocol, so logs go to stderr.
logging.basicConfig(stream=sys.stderr, level=logging.INFO)
log = logging.getLogger("inventory")

mcp = FastMCP("inventory")

INVENTORY = {"widget": 42, "gizmo": 7, "sprocket": 0}
PRICES = {"widget": 3.50, "gizmo": 19.99, "sprocket": 0.75}


@mcp.tool()
def stock_level(sku: str) -> int:
    """Return how many units of one SKU are in the warehouse right now.

    Call this before promising a customer a delivery date. Valid SKUs are
    widget, gizmo, and sprocket. Returns 0 for an item that is out of stock;
    an unknown SKU is an error, not a zero.
    """
    log.info("stock_level sku=%s", sku)
    if sku not in INVENTORY:
        raise ValueError(f"unknown sku {sku!r}; valid: {sorted(INVENTORY)}")
    return INVENTORY[sku]


@mcp.tool()
def restock_cost(sku: str, units: int) -> float:
    """Cost in USD of ordering `units` more of one SKU. Read-only: this
    quotes a price, it does not place an order."""
    if units < 1:
        raise ValueError("units must be at least 1")
    return round(PRICES[sku] * units, 2)


@mcp.resource("inventory://catalogue")
def catalogue() -> str:
    """The full SKU list with prices, as CSV. Application-controlled: the
    host attaches this when the user asks it to, not the model."""
    rows = ["sku,units,unit_price_usd"]
    rows += [f"{s},{INVENTORY[s]},{PRICES[s]:.2f}" for s in sorted(INVENTORY)]
    return "\n".join(rows)


@mcp.prompt()
def restock_review(sku: str) -> str:
    """A user-invoked template: 'review the restock case for this SKU'."""
    return (f"Review whether we should restock {sku}. Check the current "
            f"stock level, quote the cost of reaching 100 units, and state "
            f"a recommendation in one sentence.")


if __name__ == "__main__":
    mcp.run()          # stdio transport by default
```

Four decorators, three primitives, one `mcp.run()`. Everything Section 28.3
implemented by hand — the handshake, `tools/list`, the schema generation, the
JSON-RPC framing — the SDK does for you. What it cannot do for you is write
those docstrings, and they are the part the model actually reads.

## The same server in TypeScript

TypeScript is the ecosystem's other first-class language, and the official
`@modelcontextprotocol/sdk` package mirrors the Python one. Schemas come from
**Zod** validators rather than type hints:

```typescript
// src/server.ts  — needs @modelcontextprotocol/sdk and zod
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const INVENTORY: Record<string, number> = { widget: 42, gizmo: 7, sprocket: 0 };

const server = new McpServer({ name: "inventory", version: "1.0.0" });

server.tool(
  "stock_level",
  "Return how many units of one SKU are in the warehouse right now. " +
    "Call this before promising a customer a delivery date.",
  { sku: z.enum(["widget", "gizmo", "sprocket"]).describe("The SKU to look up.") },
  async ({ sku }) => {
    // console.log() would corrupt the stdio stream — use console.error().
    console.error(`stock_level sku=${sku}`);
    return { content: [{ type: "text", text: String(INVENTORY[sku]) }] };
  },
);

const transport = new StdioServerTransport();
await server.connect(transport);
```

Note the `z.enum` — the allowlist from Section 28.1, expressed in the type
system, and compiled by the SDK into the `enum` keyword of the JSON Schema
the model sees. As with the Python SDK, the exact registration helpers have
changed names across versions; treat this as the shape and check the README.

## Running it over stdio

A stdio server is not a service you start and leave running. The **host**
launches it as a child process, keeps the pipes open for the session, and
kills it on exit. You can still run it by hand to check it starts:

```console
$ pip install "mcp[cli]"
$ python -m inventory_mcp
# now it is waiting on stdin for JSON-RPC. Paste one line and press Enter:
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"manual","version":"0"}}}
{"jsonrpc":"2.0","id":1,"result":{"protocolVersion":"2025-06-18","capabilities":{"tools":{"listChanged":false}},"serverInfo":{"name":"inventory","version":"1.0.0"}}}
$ # ctrl-C to stop
```

To wire it into a host application, you register it in that host's MCP
configuration file. The shape is near-universal: a name, a command, its
arguments, and any environment it needs.

```json
{
  "mcpServers": {
    "inventory": {
      "command": "python",
      "args": ["-m", "inventory_mcp"],
      "env": {"INVENTORY_DB": "/srv/inventory.sqlite"}
    }
  }
}
```

Restart the host, and the tools appear in its tool list. That is the entire
integration — no code written on the host side, because the host already
speaks the protocol. Remote servers are configured with a URL and an
authorization scheme instead of a command; the tools show up the same way.

## Designing tools a model can actually use

The protocol is the easy part. The hard part is deciding what to expose, and
the failure mode is not a crash — it is a model that keeps picking the wrong
tool and you blaming the model.

**Name for the reader that matters.** The model sees only names,
descriptions, and schemas. `verb_noun` names read well: `search_issues`,
`create_ticket`, `get_stock_level`. Avoid internal jargon (`fetch_wo_hdr`)
and avoid two tools whose names differ by one adjective.

**One tool, one thing.** The temptation is a single `manage_inventory(action,
payload)` mega-tool because it is less code on your side. It is much worse on
the model's side:

| Mega-tool | Several small tools |
| --- | --- |
| One vague description covering five behaviours | One precise description each |
| `payload` must be `additionalProperties: true`, so nothing is validated | Every argument typed and enumerated |
| A wrong `action` silently does the wrong thing | A wrong tool name is rejected outright |
| You cannot give `delete` a confirmation step without giving `read` one | Permissions per tool |

Split it. Ten small tools with sharp schemas beat one flexible tool every
time. The counterweight: do not split so far that a routine task needs six
round trips. If the model *always* calls `open_file` then `read_file`, make
that one tool.

**Descriptions are prompts.** Say what the tool does, when to use it, when
*not* to, what the units are, and what happens on failure. "Returns 0 for an
item that is out of stock; an unknown SKU is an error, not a zero" prevents a
specific, real misreading.

**Return structured errors, not exceptions.** As Section 28.3 showed, a tool
that fails should come back as a result with `isError: true` and a message
written for the model — `unknown sku 'flux_capacitor'; valid: ['gizmo',
'sprocket', 'widget']` tells it exactly how to retry. A stack trace tells it
nothing. (SDKs generally convert an exception raised inside a tool into
exactly that shape, which is why the code above can just `raise ValueError`.)

**Prefer idempotent tools.** A model may retry a call it thinks timed out.
`set_quantity(sku, 10)` is safe to run twice; `add_units(sku, 10)` is not. If
a tool must be non-idempotent, give it a caller-supplied idempotency key, or
require confirmation.

**Paginate anything unbounded.** A tool that returns 40,000 rows will blow
the context window and cost real money. Return a page plus a cursor:

```json
{
  "items": [{"sku": "gizmo", "units": 7}],
  "nextCursor": "eyJvZmZzZXQiOiAyMH0=",
  "totalEstimate": 812
}
```

The same convention applies to the protocol's own list methods: `tools/list`,
`resources/list`, and `prompts/list` all accept an optional `cursor` param
and may return a `nextCursor` in the result. Exercise 28.5 has you implement
exactly that.

## Testing an MCP server

An MCP server is unusually pleasant to test, because its interface is
*dicts*. No network, no mocking library, no fixtures beyond a constructor:
build a server, hand it a message, assert on the message that comes back.
That is [arrange, act, assert](../ch24-practice/02-testing.md) with nothing
in the way.

Two families of test are worth writing, and they catch different bugs.
**Protocol conformance** tests check the envelope: ids match, notifications
are silent, unknown methods produce $-32601$. **Tool contract** tests check
the payload: every tool advertises a schema and a real description, a good
call returns content, a bad call returns the right kind of failure.

```python
# --- the server under test: MiniMCPServer from 28.3, condensed -------
class MiniMCPServer:
    def __init__(self, name, version="0.1.0"):
        self.name, self.version, self.tools = name, version, {}

    def add_tool(self, name, description, input_schema, fn):
        self.tools[name] = {"description": description,
                            "inputSchema": input_schema, "fn": fn}

    def handle(self, msg):
        mid = msg.get("id")
        method, params = msg.get("method"), msg.get("params", {})
        if mid is None:
            return None
        if method == "initialize":
            return self._ok(mid, {
                "protocolVersion": "2025-06-18",
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": self.name, "version": self.version}})
        if method == "tools/list":
            return self._ok(mid, {"tools": [
                {"name": n, "description": t["description"],
                 "inputSchema": t["inputSchema"]}
                for n, t in sorted(self.tools.items())]})
        if method == "tools/call":
            name, args = params.get("name"), params.get("arguments", {})
            if name not in self.tools:
                return self._err(mid, -32602, f"no tool named {name!r}")
            required = self.tools[name]["inputSchema"].get("required", [])
            missing = [k for k in required if k not in args]
            if missing:
                return self._err(mid, -32602, "missing required arguments",
                                 {"missing": missing})
            try:
                value = self.tools[name]["fn"](**args)
            except Exception as exc:
                return self._ok(mid, {"isError": True, "content": [
                    {"type": "text", "text": f"{type(exc).__name__}: {exc}"}]})
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


INVENTORY = {"widget": 42, "gizmo": 7, "sprocket": 0}

def stock_level(sku):
    if sku not in INVENTORY:
        raise KeyError(f"unknown sku {sku!r}")
    return INVENTORY[sku]

def build_server():
    """Arrange, factored out: a fresh server for every test."""
    s = MiniMCPServer("inventory-server", "1.0.0")
    s.add_tool("stock_level",
               "Units of one SKU in the warehouse right now.",
               {"type": "object",
                "properties": {"sku": {"type": "string",
                                       "enum": sorted(INVENTORY)}},
                "required": ["sku"]},
               stock_level)
    return s

def request(method, params=None, mid=1):
    msg = {"jsonrpc": "2.0", "id": mid, "method": method}
    if params is not None:
        msg["params"] = params
    return msg


# ---- protocol conformance -------------------------------------------
def test_initialize_reports_name_and_version():
    server = build_server()                                  # arrange
    reply = server.handle(request("initialize", {}, mid=1))   # act
    assert reply["id"] == 1                                   # assert
    assert reply["result"]["serverInfo"]["name"] == "inventory-server"
    assert reply["result"]["protocolVersion"] == "2025-06-18"

def test_response_id_matches_request_id():
    server = build_server()
    assert server.handle(request("tools/list", mid=99))["id"] == 99

def test_notification_gets_no_reply():
    server = build_server()
    assert server.handle({"jsonrpc": "2.0", "method": "tools/list"}) is None

def test_unknown_method_is_32601():
    server = build_server()
    reply = server.handle(request("resources/read", {"uri": "file:///x"}))
    assert reply["error"]["code"] == -32601
    assert "result" not in reply

# ---- tool contract ---------------------------------------------------
def test_every_tool_advertises_a_schema_and_a_description():
    server = build_server()
    for tool in server.handle(request("tools/list"))["result"]["tools"]:
        assert tool["inputSchema"]["type"] == "object"
        assert len(tool["description"]) > 20, f"{tool['name']} needs prose"

def test_tools_call_returns_content():
    server = build_server()
    reply = server.handle(request("tools/call",
                                  {"name": "stock_level",
                                   "arguments": {"sku": "widget"}}))
    result = reply["result"]
    assert result["isError"] is False
    assert result["content"][0]["text"] == "42"

def test_missing_argument_is_invalid_params():
    server = build_server()
    reply = server.handle(request("tools/call", {"name": "stock_level",
                                                 "arguments": {}}))
    assert reply["error"]["code"] == -32602
    assert reply["error"]["data"]["missing"] == ["sku"]

def test_tool_failure_is_a_result_not_an_error():
    server = build_server()
    reply = server.handle(request("tools/call",
                                  {"name": "stock_level",
                                   "arguments": {"sku": "nope"}}))
    assert "error" not in reply, "a failing tool must not be a protocol error"
    assert reply["result"]["isError"] is True
    assert "unknown sku" in reply["result"]["content"][0]["text"]

# ---- run them (pytest does this for you outside the browser) ---------
passed = failed = 0
for name, fn in sorted(globals().items()):
    if name.startswith("test_") and callable(fn):
        try:
            fn()
            print(f"PASS  {name}")
            passed += 1
        except AssertionError as error:
            print(f"FAIL  {name}  ({error})")
            failed += 1
print()
print(passed, "passed,", failed, "failed")
```

Eight tests, eight passes. Note
`test_every_tool_advertises_a_schema_and_a_description`: it loops over
whatever tools exist, so it keeps passing as the server grows and fails the
moment somebody ships a tool with a two-word description. That is a *policy*
encoded as a test, and it is the cheapest quality control an MCP server can
have. Deleting the `> 20` check and re-running is a good way to convince
yourself the loop really inspects every tool.

## Debugging

**The MCP Inspector** is the tool you want first: an interactive developer
tool, published by the protocol's maintainers as
`@modelcontextprotocol/inspector`, that launches your server, performs the
handshake, and gives you a UI to browse `tools/list` and fire `tools/call`
with arguments you type. It shows the raw JSON-RPC in both directions, which
means you can see a malformed schema before a model ever does.

```console
$ npx @modelcontextprotocol/inspector python -m inventory_mcp
```

**Log to stderr — never stdout.** This is the number-one first-day bug on the
stdio transport, and it is worth understanding rather than memorising. On
stdio, your server's **stdout is the protocol**: the client reads it line by
line and parses each line as a JSON-RPC message. A stray `print("got here")`
inserts `got here` into that stream, the client tries `json.loads("got
here")`, and the connection dies with a parse error that names *your debug
line* as the problem. `logging.basicConfig(stream=sys.stderr)` — or
`console.error` in Node — keeps your diagnostics on a channel nobody is
parsing. Over the HTTP transport, stdout is harmless, which is exactly why
this bug is so confusing when a server works in one host and not another.

Three more habits that pay for themselves: run your tests before starting the
host, because a server that crashes during `initialize` often shows up in the
host as a bare "server failed to start"; make the server's own errors
descriptive enough to be read in a log with no context; and version your tool
schemas, because a host may have cached the previous list.

## Security

An MCP server is a piece of software that executes instructions ultimately
derived from a language model, which is in turn influenced by text you do not
control. Everything in Section 28.1's security discussion applies, plus these.

**Validate at the boundary, not in the tool body.** The schema is your first
gate and the SDK enforces it, but schemas cannot express everything: bound
every integer, cap every string length, cap every result size. An unbounded
`limit` parameter is a denial-of-service tool with a friendly name.

**Path traversal is the classic file-tool bug.** A server that exposes
`read_note(name)` under `/srv/notes` must not be talked into reading
`/etc/passwd`. The check that works is not string inspection — it is
*resolve, then compare*:

```python
from pathlib import Path

ROOT = Path("/srv/notes").resolve()

def safe_path(root, user_supplied):
    """Resolve `user_supplied` beneath `root`, and refuse to leave it."""
    candidate = (root / user_supplied).resolve()
    if candidate == root or root in candidate.parents:
        return candidate
    raise ValueError(f"path escapes {root}: {user_supplied!r}")

attempts = [
    "meeting.md",
    "2026/q1/plan.md",
    "../../etc/passwd",
    "notes/../../../etc/shadow",
    "/etc/passwd",
    "./ok/../fine.md",
]
for attempt in attempts:
    try:
        print(f"ALLOW  {attempt:<28} -> {safe_path(ROOT, attempt)}")
    except ValueError as exc:
        print(f"DENY   {attempt:<28} -> {exc}")

# The naive check everybody writes first, and why it is not enough:
def naive_is_safe(user_supplied):
    return ".." not in user_supplied

print()
print("naive '..' check says '/etc/passwd' is safe:",
      naive_is_safe("/etc/passwd"), "— an absolute path needs no '..'")
```

Three allowed, three denied — and look at the last allowed one: `./ok/../fine.md`
contains `..` but stays inside the root, so a string check would wrongly
*deny* it while wrongly *allowing* `/etc/passwd`. Resolving first and
comparing against the root gets both right. (`Path.resolve()` also collapses
symlinks, which is the other way out of a directory.) Note that
`root / "/etc/passwd"` discards the root entirely — absolute paths win in
`pathlib` — which is precisely why the comparison happens after resolution.

**Secrets never go in tool descriptions or schemas.** Every description and
every schema is sent to the model, and from there into logs, traces, and
sometimes a provider's servers. Put credentials in the environment, read them
at startup, and never echo them in an error message.

**Human in the loop for anything irreversible.** Sending, deleting, paying,
deploying, merging. Hosts generally prompt the user before a tool call, but
do not rely on the host: mark destructive tools clearly, keep them separate
from read-only ones, and where the stakes justify it, require a confirmation
token that only a human flow can produce. Least privilege is the same
argument in credential form — if the server only needs to read, give it a
read-only account, and the worst case of a successful prompt injection is an
information leak rather than a deletion.

!!! warning "Common mistakes"

    - **`print()` in a stdio server.** It corrupts the JSON-RPC stream and
      the error message will blame the client. Log to stderr.
    - **Mega-tools with a free-form `payload`.** Nothing is validated, the
      description cannot be precise, and the model guesses.
    - **Unbounded results.** A tool that can return the whole table will
      eventually return the whole table, into a context window, at cost.
      Paginate and cap.
    - **`"/".join` or `..`-checking for path safety.** Resolve the path and
      compare it against the root; anything else has a bypass.
    - **Testing only the happy path.** The interesting bugs live in the
      failures: wrong method, missing argument, tool raising. Those are the
      tests that caught real bugs in the mini server.

## Check your understanding

1. Your server works perfectly when you test it with the Inspector over
   stdio, but the moment you add `print(f"query: {sql}")` for debugging, the
   host reports "failed to parse message". What happened, and what is the
   fix?

    ??? success "Answer"
        On the stdio transport stdout *is* the protocol stream: the client
        reads it line by line and parses each line as JSON-RPC. Your
        `print` injected `query: SELECT ...` into that stream, and
        `json.loads` failed on it. Send diagnostics to stderr instead —
        `logging.basicConfig(stream=sys.stderr)` in Python, `console.error`
        in Node. The same code is harmless over the HTTP transport, which is
        why the bug seems to appear and disappear.

2. You are asked to expose a database. Do you ship one `run_sql(query)` tool
   or five narrow ones like `find_customer` and `list_orders`? Argue both
   sides, then choose.

    ??? success "Answer"
        `run_sql` is maximally flexible and takes an afternoon to write — but
        its schema is a single free-form string, so nothing can be validated,
        the description cannot say anything precise, and a model influenced
        by injected text can issue `DROP TABLE`. Narrow tools are more work
        and cannot answer questions you did not anticipate, but every
        argument is typed and enumerated, each tool can carry its own
        permissions, and read-only ones need no confirmation step. Ship the
        narrow tools; if you truly need ad-hoc queries, expose them through a
        read-only account with a row limit and a human confirmation.

3. Why is `safe_path` written as "resolve, then check the parents" rather
   than "reject any string containing `..`"?

    ??? success "Answer"
        Because the string check is wrong in both directions. It allows
        `/etc/passwd`, which needs no `..` at all — `pathlib` discards the
        root when the right-hand side is absolute — and it denies harmless
        paths like `./ok/../fine.md` that resolve back inside the root.
        Resolving first turns every spelling of a location into one canonical
        path (also collapsing symlinks), and `root in candidate.parents` then
        answers the question you actually care about: is this file inside the
        directory I am willing to serve?

4. A tool called `delete_old_records(days)` is called twice because the host
   retried a request it thought had timed out. What property should the tool
   have had, and what should you do if it cannot have it?

    ??? success "Answer"
        Idempotency: running it twice should leave the system in the same
        state as running it once. `delete_records_older_than(date)` is
        idempotent — the second run finds nothing left to delete — whereas
        anything phrased relative to "now" or "the last N" is not. If a tool
        genuinely cannot be idempotent, give it a caller-supplied
        idempotency key the server remembers, and put a human confirmation
        in front of it, because it is destructive by definition.
