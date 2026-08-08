# Chapter 6 · Loops

Everything a computer is admired for — indexing the web, rendering a game
frame, adding up a million bank transactions — comes down to doing simple
things *many, many times*. The **loop** is the language feature that unlocks
this power. Until now, every program you have written ran each line at most
once; after this chapter, three lines of code will be able to do three
billion steps of work.

We start with the `while` loop, the most general form: *keep going as long as
a condition holds*. You will learn the initialize–test–update discipline that
keeps loops correct, the classic counter, accumulator, and sentinel patterns,
and — because everyone writes one eventually — how to recognise and fix an
infinite loop.

Then comes the `for` loop and Python's `range`, the tool of choice whenever
you know in advance how many repetitions you need. Nested loops, `break`, and
`continue` follow, for shaping exactly *which* repetitions happen.

The chapter closes with two topics that travel alongside loops in a typical
first-semester course: **bitwise operators**, which manipulate the individual
binary digits inside an integer (a direct payoff from
[Chapter 0's binary](../ch00-machine/02-binary.md)), and **enums**, named
constants that make code with a fixed set of options far harder to break.

## After this chapter you can …

- write `while` loops that provably start, make progress, and stop;
- use counter, accumulator, and sentinel patterns to process data;
- emulate Java's `do-while` idiomatically in Python;
- diagnose the three classic causes of infinite loops — and fix them;
- choose confidently between `while` and `for`, and use all three forms of
  `range`;
- loop directly over strings and lists, and use `enumerate` when you also
  need the index;
- write and *trace* nested loops (times tables, star patterns);
- use `break` and `continue` precisely, including escaping from nested loops;
- test, set, and clear individual bits with `&`, `|`, `^`, `~`, `<<`, `>>`;
- define named constants with `enum.Enum` and explain when enums beat strings.

## Prerequisites

You should be comfortable with
[variables and types](../ch02-data/index.md),
[writing and calling functions](../ch03-functions/index.md), and
[boolean conditions and `if`/`elif`/`else`](../ch04-branching/index.md) —
a loop is essentially an `if` that keeps coming back.

## Sections

1. [6.1 while and do-while](01-while.md) — the anatomy of repetition, loop
   patterns, and infinite-loop first aid.
2. [6.2 for loops and ranges](02-for.md) — `range` in all three forms, the
   half-open convention, and looping over sequences directly.
3. [6.3 Nested loops, break, continue](03-nested-break-continue.md) — grids,
   star patterns, and precise control over which passes run.
4. [6.4 Bitwise operators and enums](04-bitwise-enums.md) — flipping bits
   inside integers, and giving names to fixed sets of values.
5. [Exercises](exercises.md) — from a countdown clock to a permission-bits
   puzzle.
