# Chapter 3 · Functions and Objects

So far, every program you have written has been a straight line: a handful of
statements that run once, top to bottom, and then stop. Real programs are not
built that way. They are built from *pieces* — values that carry their own
behaviour around with them (objects), and named, reusable blocks of code that
you can call whenever you need them (functions). This chapter is where your
programs stop being scripts and start being *designed*.

We begin on the "using" side: every value in Python is an **object** that
bundles data together with the operations that make sense for it, and you ask
an object to do something with **dot notation**, like `"hello".upper()`. You
will spend most of the chapter with the most method-rich object of all — the
**string** — learning to slice it, search it, and transform it. Then we cross
to the "defining" side: writing your own functions with `def`, understanding
the crucial difference between *returning* a value and *printing* it, and
seeing where variables live and die (scope). We close with the practical craft
of formatting output beautifully with f-strings. If you are following a Java
course alongside this handbook, this chapter parallels the classic "using
objects and defining methods" unit — the side-by-side Java tabs will show you
exactly where the two languages agree and where they part ways.

## After this chapter you can …

- Explain what an object is and call methods on one with dot notation.
- Say what `None` means, recognise `NoneType` errors, and explain the
  difference between a module-level function (`math.sqrt`) and a method
  (`"hi".upper()`) — and map both onto Java's static and instance methods.
- Use the `random` module as a worked example of reading and using a library.
- Index, slice, search, and transform strings, and explain why string methods
  always return *new* strings.
- Write your own functions with `def`, including parameters, default values,
  return values, and docstrings — and never confuse `return` with `print`
  again.
- Predict which variables are visible where (local vs global scope) and read
  the error messages that scope mistakes produce.
- Format numbers and build aligned, table-like output with f-strings.

## Prerequisites

You should be comfortable with variables, types, and arithmetic from
[Chapter 2](../ch02-data/index.md), including the modulo operator `%` and the
`math` library from [Section 2.4](../ch02-data/04-math-input.md). No knowledge
of `if` statements or loops is needed — where a single tiny `if` sneaks into
an example, we flag it and point ahead to
[Chapter 4](../ch04-branching/index.md).

## Sections

1. [3.1 Using objects and their methods](01-using-objects.md) — everything is
   an object; dot notation; `None`; static vs instance behaviour; the
   `random` module; discovering APIs with `help()` and `dir()`.
2. [3.2 Strings](02-strings.md) — literals and escapes, immutability,
   indexing and slicing, the big method tour, comparing strings, and a
   worked name-parsing example.
3. [3.3 Writing your own functions](03-writing-functions.md) — `def`,
   parameters vs arguments, `return` vs `print`, defaults, scope, docstrings,
   and designing a function from a written specification.
4. [3.4 Formatting output](04-output-formatting.md) — `print`'s `sep` and
   `end`, f-strings from basics to format specs, and building aligned tables.
5. [Exercises](exercises.md) — nine graded problems, from string puzzles to
   predicting scope errors.
