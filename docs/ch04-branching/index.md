# Chapter 4 · Making Decisions

Every program you have written so far runs straight down the page: line 1,
line 2, line 3, done. Real programs are not like that. A thermostat turns the
heating on *only if* the room is cold; a website shows the logout button
*only if* you are signed in; a grading script prints "A" for one score and
"F" for another. The ability to choose between paths is called **branching**
(or *selection*), and it is the first of the two control-flow superpowers —
the second, repetition, arrives in [Chapter 6](../ch06-loops/index.md).

This chapter builds branching from the ground up. We start with the raw
material: **Boolean values** (`True` and `False`), the comparison operators
that produce them, and the `and`/`or`/`not` operators that combine them. Then
comes the `if`/`elif`/`else` statement itself — including how Python uses
indentation where Java uses braces.

Two special topics follow. The first is the subtle but important difference
between *equal values* and *the same object* (`==` vs `is`). The second is
Python's `match` statement — the cousin of Java's `switch` — together with a
toolkit for debugging and writing readable branches.

Throughout, you will see side-by-side Java tabs wherever the two languages
genuinely differ: chained comparisons, braces vs indentation, `==` vs
`.equals()`, and `switch` fallthrough. If you are following a Java course,
these tabs translate everything you learn here back into Java.

## After this chapter you can …

- evaluate any expression built from comparisons, `and`, `or`, and `not` —
  and simplify it using De Morgan's laws;
- write `if`/`elif`/`else` statements with correct indentation, and read a
  flowchart of what they do;
- explain why the *order* of `elif` tests matters, and pick the right order;
- flatten deeply nested conditions using `and` and guard-style early returns;
- explain the difference between `==` (equal values) and `is` (same object),
  and use `is` correctly for `None` checks;
- choose between an `elif` chain, a `match` statement, and a dictionary
  lookup — and debug a branch that takes the wrong path.

## Prerequisites

- [Chapter 2 · Values, Types, and Expressions](../ch02-data/index.md) —
  variables, arithmetic operators, and expression evaluation.
- [Chapter 3 · Functions and Objects](../ch03-functions/index.md) — defining
  functions and `return`, which the guard pattern in 4.2 relies on.

## Sections

1. [4.1 Booleans and logic](01-booleans-logic.md) — `True`, `False`,
   comparisons, truth tables, De Morgan's laws, truthiness, and chained
   comparisons.
2. [4.2 if, elif, else](02-if-else.md) — the full anatomy of a branch,
   indentation as block structure, flowcharts, nesting, and guards.
3. [4.3 Equality vs identity](03-equality-identity.md) — `==` vs `is`,
   `id()`, `None` checks, and the Java `==`/`.equals()` trap.
4. [4.4 switch/match, debugging, and style](04-switch-style-debug.md) —
   `match`/`case`, dictionary dispatch, tracing which branch ran, and style
   rules that keep branches readable.
5. [Exercises](exercises.md) — truth tables, prediction puzzles, leap years,
   BMI categories, and bug hunts.
