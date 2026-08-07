# Chapter 28 · Tools, Schemas, and MCP

A language model, on its own, is a text box. You put text in, you get text
out, and that is genuinely all it does — [Chapter 26](../ch26-llm-internals/index.md)
built that machine from scratch and [Chapter 27](../ch27-inference/index.md)
made it fast. But the useful things people want from software are not text:
they are *actions*. Look up today's exchange rate. Read the file on my
desktop. Multiply these two nine-digit numbers correctly. Create the ticket.
A model that only predicts tokens cannot do any of that, and no amount of
extra training fixes it, because the information and the ability live
outside the model.

This chapter is about the bridge. The trick — and it is a genuinely small
trick with enormous consequences — is that a model *can* emit text in a
shape your program recognizes: a function name and some arguments. Your
program reads that text, calls a real Python function, and hands the result
back to the model as if it were part of the conversation. The model never
"runs" anything. Your code runs everything. That loop, called **function
calling** or **tool use**, is the entire skeleton of every AI agent you have
ever heard of, and by the end of Section 28.1 you will have written one that
works.

The rest of the chapter hardens that skeleton. Section 28.2 asks the
uncomfortable question the loop depends on: how do you *guarantee* the model
emits parseable JSON rather than "Sure! Here's the JSON you asked for:"?
The answer — masking the model's logits so that impossible tokens can never
be sampled — is one of the most satisfying mechanisms in the field, and we
implement it. Sections 28.3 and 28.4 zoom out to the industry's answer to a
plumbing problem: if every app defines its own tool format, then $M$ apps
and $N$ tools cost $M \times N$ integrations. The **Model Context Protocol**
(MCP), an open standard from Anthropic, replaces that with $M + N$. We will
not just describe the protocol — we will implement a working JSON-RPC tool
server and client in the browser, watch every message go past, and then
write the real thing.

**After this chapter you can …**

- explain why a model cannot multiply reliably or know today's date, and
  what tool use does about it;
- read and write a JSON Schema — types, `properties`, `required`, `enum`,
  nested objects — and explain why the `description` field is a prompt;
- implement a schema validator and a tool dispatcher from scratch;
- write the full multi-turn tool-calling loop, including error handling for
  bad arguments and parallel tool calls;
- explain mechanically how constrained decoding guarantees valid JSON, and
  name the libraries that do it;
- describe the M×N integration problem and how a protocol collapses it;
- read and write JSON-RPC 2.0 requests, responses, notifications, and error
  objects, and narrate the MCP `initialize` handshake;
- distinguish MCP's three primitives — tools, resources, and prompts — by
  who controls them;
- build, test, debug, and secure an MCP server, including path-traversal
  defence and human-in-the-loop confirmation for destructive actions.

**Prerequisites:** [Chapter 26](../ch26-llm-internals/index.md) is required —
Section 28.2 masks the very logits that
[Section 26.4](../ch26-llm-internals/04-sampling.md) sampled from, and
[Chapter 27](../ch27-inference/index.md) is where the streaming wire formats
of Section 28.3 come from. From Parts II–IV you need
[Section 11.2](../ch11-files/02-read-write.md) (text formats — JSON is the
material of this whole chapter),
[Section 10.2](../ch10-exceptions/02-exceptions.md) (raising and catching
exceptions — tool dispatch lives or dies on this),
[Section 12.1](../ch12-classes/01-class-anatomy.md) (classes — every fake
model and every server here is one), and
[Section 24.2](../ch24-practice/02-testing.md) (arrange–act–assert, which we
apply to a protocol server in Section 28.4).

**Sections**

- [28.1 Function calling and JSON Schema](01-function-calling.md) — the
  round trip, JSON Schema as a contract, a hand-written validator, and a
  complete multi-turn tool loop with error handling and security rules.
- [28.2 Structured output and constrained decoding](02-structured-output.md)
  — why "respond in JSON" fails, a repair function, logit masking with a
  toy grammar, the library landscape, and validation-with-retry.
- [28.3 The Model Context Protocol](03-mcp-protocol.md) — the M×N problem,
  MCP's architecture and primitives, JSON-RPC 2.0 taught properly, and a
  runnable mini server and client that print every message.
- [28.4 Writing a real MCP server](04-building-mcp-server.md) — the official
  SDKs in Python and TypeScript, stdio transport, tool design principles,
  testing, debugging, and security.
- [Exercises](exercises.md) — write and debug schemas, repair model JSON,
  extend the mini server, add pagination, and implement a new primitive.

!!! note "What is real and what is simulated here"

    Nothing on these pages calls a model or touches the network — the Run
    buttons execute in your browser. Every model in this chapter is a
    deterministic `FakeLLM` whose replies are scripted or rule-based, and we
    say so each time. What is *faithful* is everything on your side of the
    wire: the schemas, the validation, the dispatcher, the loop, the
    JSON-RPC messages. Swap `FakeLLM` for a real API client and the code
    around it does not change. That is the point.
