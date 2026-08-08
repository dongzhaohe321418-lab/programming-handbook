# Chapter 22 · Sorting and Searching

Sorting and searching are the oldest problems in computing — and still the
most instructive. You met both briefly in
[Chapter 8](../ch08-grids/03-first-algorithms.md), where a first sort and a
first search were your introduction to the very idea of an algorithm. This
chapter returns to them with everything you have gained since: Big-O
analysis from [Chapter 16](../ch16-complexity/index.md), recursion from
[Chapter 17](../ch17-recursion/index.md), and the heap you just built in
[Chapter 21](../ch21-heaps/index.md). This time we are not content that an
algorithm works — we ask *how fast, on which inputs, using how much memory,
and how would we know?*

The chapter's method is experimental. Nearly every claim comes with a
**comparison counter**: we instrument the algorithms to count exactly how
many times they compare two elements, then run them on sorted, random, and
reversed inputs and read the story straight off the numbers. Three results
you will watch happen:

- **Selection sort does identical work on every input** — the same count,
  sorted or shuffled or reversed.
- **Insertion sort drops from tens of thousands of comparisons to a few
  hundred** on nearly-sorted data.
- **Quicksort collapses from $n \log n$ to $n^2$** the moment we pick pivots
  foolishly.

Counting beats believing.

The arc: first the elementary sorts — transparent, quadratic, and still
genuinely useful in the right niche. Then the divide-and-conquer pair, merge
sort and quicksort, that powers real libraries. Finally searching, where
binary search delivers the payoff of all this sorting effort — and where a
five-line function turns out to hide some of the most famous bugs in
programming.

## After this chapter you can …

- implement selection, insertion, and bubble sort, state each one's loop
  invariant, and predict their comparison counts on sorted, random, and
  reversed inputs;
- explain **stability** and identify which sorts have it — and when it
  matters;
- trace merge sort's split-and-merge and quicksort's partition step on
  paper, and implement both;
- explain why merge sort is $O(n \log n)$ *always* while quicksort is
  $O(n \log n)$ *on average* and $O(n^2)$ when pivots go bad — and
  demonstrate the collapse with a counter;
- implement binary search correctly (bounds, midpoint, loop condition) and
  name the classic bugs;
- use `bisect`, `sorted`, and their Java counterparts, and reason about
  when sorting first pays for itself.

## Prerequisites

- [Chapter 16 · Algorithm Analysis](../ch16-complexity/index.md) — Big-O,
  best/worst/average case.
- [Chapter 17 · Recursion](../ch17-recursion/index.md) — merge sort and
  quicksort are recursion's greatest hits.
- [Chapter 8 · Grids, Algorithms, and Testing](../ch08-grids/index.md) —
  the first-pass sort and search we now revisit properly.

## Sections

1. [22.1 Elementary sorts](01-elementary-sorts.md) — selection, insertion,
   and bubble sort; loop invariants; the comparison-counter experiments;
   stability.
2. [22.2 Merge sort and quicksort](02-merge-quick.md) — the two-finger
   merge, recursion trees, partitioning, the pivot gamble, and what real
   libraries actually ship.
3. [22.3 Searching](03-searching.md) — linear search, binary search and its
   bug museum, `bisect`, and the economics of sorting first.
4. [Exercises](exercises.md) — traces, count predictions, a
   first-try-correct binary search challenge, and stability puzzles.
