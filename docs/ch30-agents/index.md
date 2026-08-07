# Chapter 30 · Agent Architectures

[Chapter 28](../ch28-tools-mcp/index.md) taught a model to call a function, and
[Chapter 29](../ch29-memory-rag/index.md) gave it something to remember. Put
those two together inside a `while` loop, and hand the loop's steering wheel to
the model, and you have an **agent**. That is the whole idea, and it is smaller
than the word suggests: the novelty is not that a program calls a model
repeatedly — you could write that in [Chapter 6](../ch06-loops/index.md) — but
that the *control flow itself* becomes data the model produces at runtime. Your
program stops being a recipe and starts being a loop that asks "what next?" and
does what it is told.

Everything interesting about agents follows from that one change, including
everything that goes wrong. A loop whose exit condition is decided by a
language model may not exit. A model that mistypes a tool name will mistype it
again. A transcript that grows every step costs quadratically over a run. A
chain of twenty steps that are each 95% reliable finishes correctly about a
third of the time. None of these are exotic research problems; they are the
daily engineering of the field, and each one has a concrete, mechanical fix
that you will write on these pages.

So this chapter is a build. You will write a complete ReAct agent with three
real tools, a parser and a repair path; break it four ways on purpose and fix
each break; add a planner, a replanner and a reflection loop measured by a real
verifier; run a beam search over an action space; wire up a three-agent team
with a message router, a deadlock detector and a critic that runs a genuine
checklist; and finish with a tracer, a backoff schedule and a
prompt-injection guard. Only then do we open the framework catalogue — because
LangGraph's state graph is much easier to understand once you have written the
state machine it is a production version of. Frameworks should look like
conveniences, not magic, and the only reliable way to get there is to have
built the thing yourself first.

**After this chapter you can …**

- define an agent precisely, and say who decides control flow in a single
  completion, a chain, a workflow and an agent;
- name the six parts of any agent — goal, model, tools, memory, loop, stopping
  condition — and say what breaks when each is missing;
- implement a full ReAct loop: Thought / Action / Action Input parsing with a
  repair path, a tool registry, a step budget and a printed trace;
- diagnose and fix the four standard failure modes — non-termination, repeated
  failed actions, hallucinated tool names, and context growth;
- explain why tool *descriptions* usually matter more than model size, and
  when to prefer native function calling over text parsing;
- compute compounding reliability ($p^n$) and use it to choose an
  architecture;
- build plan-then-execute with a replanner, and order subtasks with a
  topological sort that also detects cycles;
- write a reflection loop whose improvement is measured by a deterministic
  verifier rather than asserted;
- apply self-consistency, beam search over actions, and verification-first
  design, and say what each costs;
- design a multi-agent system: pick a topology, define a message schema, route
  through a supervisor, and detect deadlock and ping-pong;
- decide honestly whether a task needs one agent or several;
- map the framework landscape — LangChain, LangGraph, LlamaIndex, AutoGen,
  CrewAI, the provider agent SDKs, and MCP as the interop layer — onto the
  code you wrote by hand;
- instrument an agent with spans and traces, and ship one with cost caps,
  timeouts, backoff, idempotency keys, sandboxing and injection defences.

**Prerequisites.** [Chapter 28](../ch28-tools-mcp/index.md) is required —
Section 30.1 continues directly from the tool-dispatch loop of
[28.1](../ch28-tools-mcp/01-function-calling.md), and 30.4 links back to
[MCP](../ch28-tools-mcp/03-mcp-protocol.md).
[Chapter 29](../ch29-memory-rag/index.md) is strongly recommended: an agent's
transcript is memory, and
[29.3](../ch29-memory-rag/03-agent-memory.md) is where the growth problem in
30.1 gets solved properly. From Parts I–IV you need
[Chapter 6](../ch06-loops/index.md) (loops and loop guards),
[9.1](../ch09-collections/01-references.md) (references and aliasing — shared
state between agents is aliasing at team scale),
[10.2](../ch10-exceptions/02-exceptions.md) (raising and catching — agent tools
*return* errors rather than raise them, and knowing the difference matters),
[12.1](../ch12-classes/01-class-anatomy.md) (classes — every agent here is
one), and [21.2](../ch21-heaps/02-priority-queues.md) plus
[37.2](../ch37-graphs/02-traversal.md) for the beam search and the topological
sort in 30.2.

**Sections**

- [30.1 The agent loop and ReAct](01-agent-loop-react.md) — what an agent is,
  the anatomy of one, a complete runnable ReAct agent with three tools, the
  four failure modes run live, and why descriptions beat model size.
- [30.2 Planning and reflection](02-planning-reflection.md) — compounding
  error, plan-execute-replan, dependency ordering, a verified reflection loop,
  self-consistency, beam search, and when planning is the wrong choice.
- [30.3 Multi-agent systems](03-multi-agent.md) — five topologies, a message
  router and mailboxes, a runnable orchestrator–worker team with a
  researcher, a writer and a critic, shared state versus messages, deadlock
  and ping-pong detection, and a one-versus-many checklist.
- [30.4 The framework landscape](04-frameworks.md) — what frameworks give and
  cost, honest profiles of the main projects, a LangGraph-style state graph
  beside the hand-written equivalent, a minimal tracer, and the production
  checklist including prompt injection.
- [Exercises](exercises.md) — debug a trace, predict reliability numbers,
  extend the agent, design a message schema, implement backoff, and make an
  agent survive a crash.

!!! note "What is real and what is simulated here"

    Nothing on these pages calls a model or touches the network — the Run
    buttons execute in your browser. Every model is a deterministic,
    rule-based `FakeLLM` that reacts to the text in its prompt, so the traces
    are identical on every machine and on every run, and we say so each time.
    What is *faithful* is everything on your side of the wire: the loop, the
    parser, the budgets, the guards, the plan repair, the message routing, the
    tracer, the retry schedule. Swapping a `FakeLLM` for a real API client is
    a one-line change, shown in
    [30.1](01-agent-loop-react.md#swapping-in-a-real-model), and the code
    around it does not change at all. That is the point.
