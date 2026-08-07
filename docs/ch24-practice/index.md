# Chapter 24 · Engineering Practice

Everything so far has been about making programs *work*. This chapter is
about the habits that separate code that works tonight from code a team can
still trust next year. Professional software is rarely hard because the
algorithms are hard — you have already met the genuinely tricky ones in
Part III. It is hard because it is written by many hands over a long time,
and every line will be read, changed, broken, and repaired by someone who
was not in the room when it was born (often: you, six months later). The
craft of surviving that is called software engineering, and its core
practices fit in one chapter.

We cover three of them. **Version control as a team sport**: Chapter 1
taught you solo commits; here you meet branches, merges, pull requests, the
anatomy of a merge conflict, and the unglamorous art of the commit message.
**Testing as a discipline**: Chapter 8 introduced `assert`; here you learn
the arrange–act–assert pattern, table-driven tests, edge-case checklists,
and how real test frameworks — pytest and JUnit — organize the same ideas,
including a full test suite for a data structure from Part III. **Reading
and being read**: naming, small functions, comments that explain *why*,
style rules that formatters can enforce, and how to review code — your own
and other people's — with a checklist instead of vibes.

None of this requires new language features, and almost every example runs
right on the page. What it requires is a change of audience: you stop
writing for the interpreter, which is satisfied by anything that parses,
and start writing for people. The interpreter never asks *why*. People
always do.

**After this chapter you can …**

- work the daily Git loop — pull, branch, commit small, push, open a pull
  request — and explain why teams branch at all;
- read the conflict markers in a merge conflict and resolve one calmly;
- write commit messages with an imperative subject line and a body that
  explains *why*, not *what*;
- structure any test as arrange–act–assert, and convert a pile of similar
  tests into one table-driven loop;
- apply an edge-case checklist (empty / one / many, boundaries, duplicates,
  invalid input) to any function you test;
- write a pytest-style suite — and its JUnit 5 counterpart — including
  tests that *expect* an exception;
- say precisely what 100% test coverage does and does not prove;
- rename, split, and comment code so a stranger can follow it, and run a
  self-review checklist before every commit.

**Prerequisites:** [Chapter 1](../ch01-tools/03-git.md) (first taste of
Git), [Chapter 8](../ch08-grids/04-unit-testing.md) (asserts and unit-test
thinking), [Chapter 10](../ch10-exceptions/02-exceptions.md) (exceptions —
we test error paths), and for the worked test suite,
[Chapter 19](../ch19-stacks-queues/02-stacks.md) (the Stack ADT).

**Sections**

- [24.1 A real Git workflow](01-git-workflow.md) — branches, merges,
  conflicts, pull requests, commit messages, and repository hygiene.
- [24.2 Testing beyond the basics](02-testing.md) — arrange–act–assert,
  pytest and JUnit conventions, table-driven tests, edge cases, coverage,
  and regression tests.
- [24.3 Style, reviews, and readable code](03-style-review.md) — naming,
  small functions, honest comments, formatters, and the self-review
  checklist.
- [Exercises](exercises.md) — write commit messages, resolve a conflict on
  paper, hunt edge cases, and refactor a tangle.
