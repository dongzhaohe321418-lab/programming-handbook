# Chapter 40 · The Developer Toolchain

Every program in this handbook so far has been written for a reader — you —
sitting in front of one machine, running one file. A working software team
looks different. The code lives in a repository that a dozen people push to.
It is built by a machine that nobody logs into. It runs on a server in a
building none of them have visited. It is tested automatically before anyone
is allowed to merge it. The programming language is the smallest part of that
picture; the rest is a **toolchain** — the shell that glues commands
together, SSH that reaches remote machines, a build system that knows what to
rebuild, and a test framework that runs a thousand assertions in ten seconds
and tells you exactly which one broke.

None of these tools are hard. What makes them feel hard is that they are
usually taught as a list of incantations to memorise: type this, then type
that. This chapter refuses to do that. Each of the four tools here has one
central idea — word splitting and exit codes for the shell, key pairs and
tunnels for SSH, a dependency graph plus timestamps for Make, a registry of
functions plus a runner for JUnit — and each of those ideas is small enough
to build in Python in around a hundred lines. So every page here does both: it shows the
real tool as you will actually type it, in fences with no Run button, *and*
it hands you a runnable model of the mechanism underneath, so the real tool
stops being magic.

There is a further reason to care, and it is the one that matters most for
your career. Everything in this chapter is **automation of your own work**.
The five minutes a day you spend re-typing a build command, the twenty
minutes you spend re-running tests by hand, the hour you lose when a laptop
sleeps and kills an eight-hour job — all of it is recoverable, permanently,
by writing something down once. That is the highest-leverage skill in this
book: not writing faster code, but arranging never to do the same thing
twice.

## After this chapter you can …

- write a real bash script — shebang, executable bit, arguments, functions,
  loops, conditionals — and explain why `"$var"` is quoted and `$var` is a
  bug waiting to happen;
- read and write `set -euo pipefail` and say what each of the four settings
  does and when it will not save you;
- combine `grep`, `sed`, `awk`, `cut`, `sort`, `uniq`, `find`, and `xargs`
  into a one-line answer to a question about a log file;
- redirect standard output and standard error independently, and explain
  what `2>&1` means in terms of file descriptors;
- generate an SSH key pair, install it on a server, and describe honestly
  what the server checks and what it never sees;
- keep a long job alive across a dropped connection with `tmux`, and reach a
  remote web server through a port-forwarding tunnel;
- read and write Unix permission modes in both `0o755` and `rwxr-xr-x` form;
- explain a build system as a dependency graph plus timestamps, write a
  Makefile with pattern rules and automatic variables, and predict exactly
  which targets a change forces to rebuild;
- implement a working mini-make — topological sort, staleness check, cycle
  detection — and extend it to batch targets for parallel execution;
- write JUnit 5 tests using fixtures, parameterization, exception assertions,
  and nested test classes, and explain why each test gets a fresh instance;
- diagnose a flaky test caused by shared mutable state, and replace an
  awkward dependency (a clock, a mailer) with a test double.

## Prerequisites

- [Section 1.1 · The command line](../ch01-tools/01-command-line.md) —
  `pwd`, `ls`, `cd`, paths, and reading a `console` transcript. Section 40.1
  starts exactly where that page stopped.
- [Section 1.3](../ch01-tools/03-git.md) and
  [Section 24.1](../ch24-practice/01-git-workflow.md) — Git. This chapter
  assumes you can commit and push; it does not re-teach that.
- [Section 8.4](../ch08-grids/04-unit-testing.md) and
  [Section 24.2](../ch24-practice/02-testing.md) — asserts, test functions,
  and pytest. Section 40.4 scales that up to a real framework.
- [Section 39.3 · Pipelines](../ch39-streams/03-pipelines.md) — generators,
  laziness, and the Unix pipe. Section 40.1 builds directly on it.
- Helpful: [Section 37.2](../ch37-graphs/02-traversal.md) for topological
  sort, which is literally how Make orders a build, and
  [Chapter 23](../ch23-os/index.md) for processes and file descriptors.

## Sections

1. [40.1 Bash scripting](01-bash.md) — from typing commands to writing
   programs: the shebang and the executable bit, variables and the quoting
   bug that defines the language, command substitution, exit codes and
   `&&`/`||`, conditionals and loops, functions and positional parameters,
   here-documents, redirection and file descriptors, `set -euo pipefail`
   explained line by line, the classic text toolkit, a complete
   build-and-test runner dissected, a runnable shell-pipeline simulator, and
   an honest account of when to stop and switch to Python.
2. [40.2 SSH and remote development](02-ssh-remote.md) — why your code so
   often runs somewhere else, the client/server model, public-key
   authentication explained without mathematics and then demonstrated with a
   toy key pair, host-key verification and that scary first prompt,
   `ssh-keygen`/`ssh-copy-id`/`~/.ssh/config`/`scp`/`rsync`, `tmux` for
   sessions that survive a closed laptop, port forwarding, editor-based
   remote development, a runnable permissions decoder, and security hygiene.
3. [40.3 Make and build systems](03-make.md) — the arithmetic that makes
   incremental builds worth it, the dependency graph and timestamp model,
   Makefile anatomy including the tab trap and automatic variables, `make -n`
   and `make -j`, a complete mini-make in Python with topological sort,
   staleness propagation and cycle detection, and where Gradle, CMake, npm
   scripts, uv, and Bazel fit.
4. [40.4 JUnit and testing at scale](04-junit.md) — what a framework adds to
   a bare `assert`, JUnit 5 annotation by annotation against real data
   structures, the per-test-instance lifecycle and the flaky tests that
   ignore it, running tests from the command line and in CI, testing
   exceptions and floating point, a runnable JUnit-style micro-framework
   with a deliberately failing test, test doubles including a fake clock,
   and coverage honesty.
5. [Exercises](exercises.md) — eight problems: fix the quoting bug, predict
   a pipeline's output, decode permission modes, write a Makefile for a given
   graph, predict a rebuild, hunt a flaky test, write parameterized tests,
   and extend the mini-make with level-by-level parallel batching.

The companion lookup page is
[Appendix F · Toolchain quick reference](../appendix/F-toolchain-reference.md):
every command, flag, annotation, and keybinding in this chapter on one
scannable page, plus a triage table for the five errors you will hit most.
