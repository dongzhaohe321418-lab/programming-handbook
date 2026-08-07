# Chapter 34 · Becoming an AI Engineer

This chapter is a plan, not more theory. Everything before it taught mechanisms;
this one is about what to do with them — the order to learn things in, what to
build, what actually convinces a stranger that you can do the work, and how to
keep up with a field that produces more output every month than anyone can read.
There is exactly one runnable block per section, and both of them are schedulers
and calculators rather than algorithms. If you came here for another
implementation, [Chapter 33](../ch33-eval/index.md) is where the last one was.

It is written for two readers who need almost the same advice. The first has
finished Parts I–IV and Chapters 26–33 and wants to know what to do next. The
second is already a working engineer moving toward AI work and wants to know
which of the loud things in this field are worth their evenings. Both need the
same answer, which is why the chapter is short: build a small number of things
properly, measure them, write them down, and contribute to something you did not
start.

The honest framing you should carry through both sections is this. **The tools
move fast and the fundamentals do not.** Between the writing of this chapter and
your reading of it, some framework in Part V will have been renamed, some
benchmark will have saturated, and some model will have made a paragraph
somewhere read as quaint. None of that touches attention, KV-cache arithmetic,
the policy-gradient and DPO update rules, Bradley-Terry preference modelling,
confidence intervals, or the structural fact that instructions and untrusted
content share one context window. Those are the parts of Parts I–IV,
[Chapter 26](../ch26-llm-internals/index.md) and
[Chapter 31](../ch31-rl/index.md) that age slowly, and they are what let you
read next year's announcement and decide in an afternoon whether it changes
anything for you. Learn the mechanism; rent the tool.

**After this chapter you can …**

- lay out a staged plan from "finished Part V" to "shipped and measured a real
  system", with a concrete deliverable and a self-check at each stage;
- say what fluency in Python and TypeScript means in testable terms for this
  kind of work;
- use an AI coding agent well — verifiable tasks, letting it run the tests,
  reviewing diffs rather than summaries, writing a project rules file — and say
  which work you should never delegate;
- keep interview-ready data-structures skills alive on a realistic weekly budget,
  and see why a drill list longer than the budget silently fails;
- read a paper with the three-pass method, and reproduce a result in a way that
  teaches you something whether or not the number matches;
- choose between four portfolio archetypes, and name the trap in each;
- write a README that leads with a measured number, a baseline, an interval, and
  an honest limitations section;
- find a first open-source issue, open a pull request that gets merged, and say
  why documentation and test contributions are the most underrated;
- calibrate what a preprint, a workshop paper and a top-conference paper each
  represent, and what the reproducibility bar now is;
- answer an LLM system-design question by asking about constraints first and
  doing capacity arithmetic out loud;
- keep current on an hour a week without mistaking a feed for knowledge.

**Prerequisites.** All of Part V in spirit; specifically
[Chapter 26](../ch26-llm-internals/index.md) and
[Chapter 27](../ch27-inference/index.md) (Phase 1),
[Chapters 28](../ch28-tools-mcp/index.md),
[29](../ch29-memory-rag/index.md) and [30](../ch30-agents/index.md) (Phase 2),
[Chapters 31](../ch31-rl/index.md) and [32](../ch32-data/index.md) (Phase 3),
and [Chapter 33](../ch33-eval/index.md) (Phase 4, and the standard the whole
chapter holds you to). From Parts I–IV,
[Chapter 24](../ch24-practice/index.md) supplies the Git, testing and review
discipline that both sections lean on, and
[Part VI](../part6-overview.md) supplies the data structures that interviews
still ask about. [Chapter 25](../ch25-next/index.md) covered the
general-programming version of "what next"; this chapter is the Part V version
of it, and the two are complementary rather than overlapping.

**Sections**

- [34.1 The four-phase learning path](01-learning-path.md) — foundations,
  agents, RL and data, shipping: each with goals, chapter links, one thing you
  build, and a self-check to pass before moving on; a real treatment of agentic
  coding workflows and when not to delegate; a spaced-repetition schedule for
  keeping algorithm skills warm; a weekly time budget that survives a job; and
  the three-pass method for reading a paper plus how to reproduce a result.
- [34.2 Portfolio, open source, and research](02-portfolio.md) — four portfolio
  archetypes with what to measure and the trap in each; the README that gets you
  hired; open-source contribution as the highest-signal credential, with
  first-PR etiquette; what workshop and conference papers actually require;
  interviewing for LLM roles with a worked system-design answer and its
  arithmetic; and how to stay current without drowning.

!!! note "There are no exercises in this chapter"
    The exercises are the deliverables. Each phase in 34.1 names one thing to
    build, and 34.2 names four projects and tells you which trap eats each. A
    solution block would defeat the purpose: nobody can check this work for you,
    which is precisely why [Chapter 33](../ch33-eval/index.md) came first.
