# Chapter 2 · Values, Types, and Expressions

Every program, no matter how sophisticated, boils down to the same routine:
take some values, name them, combine them with operators, and produce new
values. A weather app multiplies and divides temperatures; a game adds points
to a score; a bank rounds interest to the nearest cent. This chapter is where
you learn that routine — the atoms of programming that every later chapter
builds molecules from.

We start with **variables**: what a name really is in Python (a label tied to
an object — not a box, and the difference matters), and the four core types
you will use constantly: `int`, `float`, `str`, and `bool`. Then we look at
how numbers are *written* — decimal, binary, and hexadecimal are three
spellings of the same value — and how Python's integers differ radically from
Java's fixed-size `int` and `long`. From there we cover the arithmetic
operators, including the two kinds of division (a spot where Python and Java
genuinely disagree) and the surprisingly useful modulo operator `%`. We close
with the `math` module and the standard pattern for turning keyboard input
into numbers you can compute with.

If you are following a Java course alongside this handbook, this chapter maps
onto the "data types and expressions" module. Watch for the side-by-side
Python/Java tabs: static vs dynamic typing, integer division, and integer
overflow are the three places the two languages behave differently enough to
trip you up.

**After this chapter you can …**

- create variables, explain what a name refers to, and follow the
  name → object arrow model when values are reassigned;
- identify the type of any value with `type()` and convert between `int`,
  `float`, and `str` — and predict which conversions fail;
- read and write numbers in binary (`0b...`) and hexadecimal (`0x...`) and
  convert between bases;
- evaluate any arithmetic expression by hand using the precedence table, and
  explain why `7 / 2` is `3.5` in Python but `3` in Java;
- use `%` for even/odd tests, digit extraction, and wrap-around (clock)
  arithmetic;
- use the `math` module and the built-ins `abs`, `min`, `max`, and `round` —
  including `round`'s banker's-rounding behaviour;
- write a complete small program that converts user input to numbers and
  prints a formatted result.

**Prerequisites.** You should know what a program is and roughly how one runs
— [Chapter 0](../ch00-machine/index.md) covers that, and
[Chapter 0.2](../ch00-machine/02-binary.md) introduces the binary ideas we
build on in section 2.2. [Chapter 1](../ch01-tools/index.md) is useful if you
want to run examples outside the browser, but every block here runs on the
page.

## Sections

1. [2.1 Variables and types](01-variables-types.md) — names, objects,
   assignment, the four core types, dynamic vs static typing, conversion.
2. [2.2 Number systems](02-number-systems.md) — binary and hex literals,
   converting between bases, Java's fixed-size integers vs Python's unlimited
   ones.
3. [2.3 Operators, precedence, and modulo](03-operators.md) — the seven
   arithmetic operators, the division trap, modulo in the wild, and the full
   precedence table.
4. [2.4 The math library and reading input](04-math-input.md) — `math`
   functions, `round`'s surprise, reading input, and a complete tip
   calculator.
5. [Exercises](exercises.md) — ten problems with full solutions.
