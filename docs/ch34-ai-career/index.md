# Chapter 34 · Becoming an AI Engineer

This chapter is a plan, not more theory. Everything before it taught mechanisms;
this one is about what to do with them:

- the order to learn things in;
- what to build;
- what actually convinces a stranger that you can do the work;
- how to keep up with a field that produces more output every month than anyone
  can read.

There is exactly one runnable block per section, and both of them are schedulers
and calculators rather than algorithms. If you came here for another
implementation, [Chapter 33](../ch33-eval/index.md) is where the last one was.

It is written for two readers who need almost the same advice.

- **The graduate of Part V** — you have finished Parts I–IV and Chapters 26–33,
  and want to know what to do next.
- **The working engineer** — you are already shipping software, moving toward AI
  work, and want to know which of the loud things in this field are worth your
  evenings.

Both need the same answer, which is why the chapter is short: build a small
number of things properly, measure them, write them down, and contribute to
something you did not start.

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

**Prerequisites.** All of Part V in spirit, and specifically one group of
chapters per phase:

- **Phase 1** — [Chapter 26](../ch26-llm-internals/index.md) and
  [Chapter 27](../ch27-inference/index.md).
- **Phase 2** — [Chapters 28](../ch28-tools-mcp/index.md),
  [29](../ch29-memory-rag/index.md) and [30](../ch30-agents/index.md).
- **Phase 3** — [Chapters 31](../ch31-rl/index.md) and
  [32](../ch32-data/index.md).
- **Phase 4** — [Chapter 33](../ch33-eval/index.md), which is also the standard
  the whole chapter holds you to.

From Parts I–IV, [Chapter 24](../ch24-practice/index.md) supplies the Git,
testing and review discipline that both sections lean on, and
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

## The chapter in brief

The whole plan on one screen, in the order the two sections lay it out.

- **Work in four phases, and treat each one as a gate rather than a calendar
  block** — you move on when you can do the things in its checklist without
  looking them up ([34.1](01-learning-path.md)).
- **Phase 1 is foundations**: internals and serving, fluent Python and working
  TypeScript, and the ability to say why a system is slow or expensive.
- **Phase 2 is agents**: write the loop by hand before you adopt a framework, and
  ship an MCP server over a data source you actually care about.
- **Phase 3 is RL and data**: keep the model small, because you are debugging a
  pipeline rather than chasing a benchmark.
- **Phase 4 is shipping**: an eval set built from your own failures, a regression
  gate, and a number you can defend.
- **Delegate to a coding agent the work you could do but would rather not, and
  never the work you cannot yet check**
  ([34.1](01-learning-path.md)) — and review the diff, not the summary.
- **Keep a drill list shorter than your weekly budget.** Twelve topics at two a
  week means four of them get reviewed once in three months.
- **Read papers in three passes**, and spend pass 3 only on the few that would
  change how you work; reproducing one small number is the most instructive
  exercise available.
- **Build one portfolio project properly rather than four halfway**, and pick it
  from the four archetypes in [34.2](02-portfolio.md), each of which comes with
  the trap that eats most attempts.
- **A result needs a baseline, an interval, and a limitations section you wrote
  yourself** — that README is the artefact, not the technology list.
- **A merged pull request to somebody else's project is the highest-signal
  credential available**, and documentation and test contributions are the most
  underrated route to one.
- **Answer a system-design question by asking about constraints first, then
  doing the arithmetic out loud** — knowing which knob is expensive beats any
  architecture diagram.

### Key terms

| Term | One-clause reminder |
| --- | --- |
| **phase gate** | you move on when you can pass the checklist, not when a number of weeks has passed ([34.1](01-learning-path.md)) |
| **deliverable** | the one thing each phase asks you to build; the reading exists to unblock it ([34.1](01-learning-path.md)) |
| **verifiable task** | work with a pass/fail attached, which is what makes delegating to a coding agent safe ([34.1](01-learning-path.md)) |
| **three-pass reading** | skim to triage, read to summarise, re-derive to understand ([34.1](01-learning-path.md)) |
| **portfolio archetype** | one of four project shapes that reliably demonstrate Part V skills ([34.2](02-portfolio.md)) |
| **baseline** | the number your result is compared against, measured the same way on the same items ([34.2](02-portfolio.md)) |
| **reproducibility bar** | released code, data, seeds, hyperparameters, hardware, and results over multiple runs ([34.2](02-portfolio.md)) |
| **[eval harness](../appendix/E-ai-glossary.md#e)** | the machinery from [Chapter 33](../ch33-eval/index.md) that turns "it seems better" into a number |

Everything on that list is checkable by somebody else, which is the whole point:
[Chapter 33](../ch33-eval/index.md) taught you to measure, and this chapter is
what to point the measurement at.
