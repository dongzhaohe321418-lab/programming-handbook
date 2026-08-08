# Chapter 5 · Under the Hood

The first four chapters taught you to *write* programs. This chapter teaches you
to *distrust* them — in the best possible way. Every language you will ever use
sits on top of real hardware, and the hardware leaks through:

- integers that silently wrap around to negative numbers;
- decimal fractions that cannot be stored exactly;
- `and`/`or` expressions that skip half their work;
- variables that turn out to be arrows pointing into memory rather than boxes
  holding values.

These are the traps that a first programming course usually hides until they
bite. We would rather show them to you now, in slow motion, with the machine's
excuses attached.

The good news is that none of this is arbitrary. Once you see *why* a 32-bit
integer must wrap at $2^{31}-1$, why $0.1 + 0.2$ misses $0.3$ by a whisker, and
where your variables actually live while a function runs, whole families of
"mysterious" bugs collapse into one or two simple mental pictures. The two
pictures at the heart of this chapter — the **call stack** of function frames
and the **heap** of objects they point to — will carry you through the rest of
the book, from lists and references in Part II to recursion and linked
structures in Part III.

Along the way we keep one eye on Java. Java exposes some of these mechanics
more nakedly than Python does (its `int` really does overflow; its methods
really can share a name), so the side-by-side views here double as a translation
guide for anyone following a Java course in parallel.

## After this chapter you can …

- explain why fixed-width integers overflow, predict the wrapped value, and
  reproduce real overflow in the browser with NumPy's `int32`;
- say precisely why `0.1 + 0.2 == 0.3` is `False`, and compare floats safely
  with `math.isclose` or an explicit tolerance;
- choose the right number type for money (`decimal`) and recognise `inf` and
  `nan` when they appear;
- predict which parts of an `and`/`or` expression actually run, and use the
  short-circuit *guard idiom* to prevent crashes;
- avoid the `++x` trap, use compound assignment (`+=`, `//=`, …) fluently, and
  read `a if c else b` expressions;
- draw the call stack and the heap for a running program, trace frames being
  created and destroyed, and use `id()` to test whether two names share one
  object;
- replace a set of overloaded Java methods with a single Python function using
  default and keyword arguments, chain methods confidently, and import modules
  without polluting your namespace.

## Prerequisites

You should be comfortable with variables and types
([Chapter 2](../ch02-data/index.md)), writing and calling functions
([Chapter 3](../ch03-functions/index.md)), and boolean logic and `if`
statements ([Chapter 4](../ch04-branching/index.md)). The binary background
from [Chapter 0](../ch00-machine/index.md) helps but is recapped where needed.

## Sections

1. [5.1 Overflow and floating-point pitfalls](01-numeric-pitfalls.md) — why
   numbers have limits, watching `int32` wrap around, and the honest truth
   about `0.1 + 0.2`.
2. [5.2 Short-circuits, compound assignment, gotchas](02-shortcuts-gotchas.md)
   — `and`/`or` laziness, the guard idiom, `+=` and friends, the `++x` trap,
   and the dangling `else`.
3. [5.3 The stack and the heap](03-stack-heap.md) — where variables and
   objects actually live, watching frames come and go, and why two names can
   share one list.
4. [5.4 Overloading, chaining, and imports](04-overloading-imports.md) — Java
   overloading vs Python defaults, keyword arguments, method chaining, and
   imports done right.
5. [Exercises](exercises.md) — predict, break, fix, and design.
