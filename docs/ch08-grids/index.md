# Chapter 8 · Grids, Algorithms, and Testing

Chapter 7 gave you a row of values; this chapter gives you the whole
spreadsheet. Two-dimensional collections — grids, tables, game boards,
images — are just lists whose elements are themselves lists, and one new
indexing habit (`grid[row][col]`) unlocks all of them. Along the way we
confront a famous Python trap (the `*` operator that silently makes every
row the *same* row) and preview NumPy's two-dimensional arrays.

The chapter then takes two steps that mark real growth as a programmer.

1. **Lists meet functions.** A list argument is passed as a **reference**, so
   a function can reach back and change the caller's data — sometimes exactly
   what you want, sometimes a baffling bug. That difference is worth an entire
   section.
2. **We write our first genuine algorithms**: linear search and selection
   sort, hand-traced and instrumented with step counters so you can *see* the
   $n^2$ growth that Chapter 16 will make precise.

Finally, we ask the question professionals ask about every function they
write: *how do I know it works?* Unit testing — small, automated checks
that run in milliseconds — is the answer, and testing your own search and
sort functions is the perfect first workout. By the end of the chapter
you will have written a small test suite and used a failing test to drive
a design, which is how a great deal of modern software actually gets
built.

## After this chapter you can …

- build, index, and traverse 2-D grids with `[row][col]`, and compute
  row sums and column sums;
- explain the `[[0] * 3] * 2` aliasing trap and write the comprehension
  that avoids it;
- predict whether a function call changes the caller's list — mutation
  does, rebinding does not — and state precisely what "Java passes
  references by value" means;
- implement, trace, and test linear search and selection sort, and
  explain why selection sort's comparisons grow like $n^2$;
- write `assert`-based test functions, run them with a simple driver,
  and choose edge cases (empty, single, duplicates, already sorted)
  before typical cases;
- describe what pytest and JUnit add on top of bare asserts.

## Prerequisites

[Chapter 7](../ch07-arrays/index.md) is essential — everything here
builds on lists, indexing, and the four traversal patterns. You will
also want functions from
[Chapter 3](../ch03-functions/03-writing-functions.md) and nested loops
from [Chapter 6](../ch06-loops/03-nested-break-continue.md).

## Sections

- [8.1 Two-dimensional arrays](01-2d-arrays.md) — grids as lists of
  lists, `[row][col]`, building grids safely, row and column sums,
  ragged rows, and NumPy 2-D.
- [8.2 Arrays and functions together](02-arrays-functions.md) — passing
  references, mutation vs rebinding, and the pass-by-reference myth.
- [8.3 First algorithms — sort and search](03-first-algorithms.md) —
  linear search and selection sort with full traces and step counts.
- [8.4 Unit testing](04-unit-testing.md) — asserts, test functions,
  edge cases first, and a taste of pytest, JUnit, and test-driven
  development.
- [Exercises](exercises.md) — diagonal sums, a tic-tac-toe referee, and
  test-first practice.
