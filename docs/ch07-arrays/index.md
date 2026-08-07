# Chapter 7 · Arrays and Lists

Every program you have written so far kept its data in individually named
variables: one name, one value. That works until the day your program needs
to remember a *hundred* values — a hundred test scores, a hundred sensor
readings, a hundred usernames. This chapter introduces the **collection**:
a single variable that holds many values in numbered slots. In Java these
are called *arrays*; in Python the everyday workhorse is the *list*. They
differ in interesting ways, but the big idea — many values, one name, each
value reachable by its position — is identical.

Collections matter because they unlock loops. A loop over a hundred-element
list processes a hundred values with three lines of code, and the *same*
three lines still work when the list grows to a million. Almost every
program you will ever write combines these two tools: a collection to hold
the data, and a loop to walk through it. This chapter teaches the walking
patterns — visiting, accumulating, searching, transforming — as named
recipes you will reuse for the rest of the handbook.

We also stay honest about what is happening in memory. A Java array and a
Python list look similar in code but are built differently under the hood,
and we introduce NumPy arrays as Python's answer to the "real",
fixed-type array. None of the machinery is scary, and seeing it now makes
Chapter 9's discussion of references much easier.

## After this chapter you can …

- create, index, and measure Java arrays and Python lists, and explain
  how they differ (fixed vs growable, one type vs any type);
- explain why indexing starts at 0 and predict exactly which indexes are
  legal for a collection of length $n$;
- read and write the four core traversal patterns: visit, accumulate,
  search-for-best, and transform;
- keep two *parallel* lists in sync by index, and say why classes
  (Chapter 12) eventually do that job better;
- recognise an `IndexError` (or Java's `ArrayIndexOutOfBoundsException`)
  and fix the off-by-one mistake that caused it;
- create a NumPy array and explain what a `dtype` is and why NumPy exists.

## Prerequisites

You should be comfortable with variables and types from
[Chapter 2](../ch02-data/index.md), writing functions from
[Chapter 3](../ch03-functions/index.md), and — most importantly — `for`
and `while` loops from [Chapter 6](../ch06-loops/index.md). Every section
here leans on loops constantly.

## Sections

- [7.1 Arrays vs Python lists](01-arrays-vs-lists.md) — why one variable
  per value doesn't scale, Java arrays vs Python lists, zero-based
  indexing, out-of-bounds errors, the memory picture, and NumPy.
- [7.2 Traversal patterns and parallel arrays](02-traversal-patterns.md) —
  the four loop recipes every programmer knows by heart, comparing lists,
  and linking two lists by index.
- [Exercises](exercises.md) — practice, from reading indexes to a
  one-pass second-largest search.
