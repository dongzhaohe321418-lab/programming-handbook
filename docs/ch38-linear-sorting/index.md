# Chapter 38 · Sorting in Linear Time

[Chapter 22](../ch22-sorting/index.md) built five sorting algorithms and ranked
them by cost, and the ranking bottomed out at $O(n \log n)$. Merge sort and
quicksort got there; bubble, selection, and insertion sort did not. The chapter
left an impression that is very nearly true and quietly wrong: that
$O(n \log n)$ is the speed limit for sorting. It is not. It is the speed limit
for one *family* of sorting algorithms — the ones that work by comparing
elements to each other — and this chapter proves that limit properly and then
escapes it.

The proof comes first, because it is one of the most satisfying arguments in
computer science and needs nothing beyond counting. Any algorithm that sorts by
asking yes/no questions of the form "is $a$ less than $b$?" is a decision tree,
its leaves must include every one of the $n!$ possible input orderings, and a
binary tree with $n!$ leaves is at least $\log_2(n!) \approx n \log_2 n$ levels
deep. That single counting argument rules out a comparison-based sort faster
than $n \log n$ *forever* — no cleverness, no future hardware, no undiscovered
algorithm. It is a statement about information, not about programming.

Then comes the escape. Counting sort, radix sort, and bucket sort break the
bound by refusing to play: instead of comparing elements they use the keys
themselves as array indices — the same trick that makes hash tables fast — and
sort $n$ items in $O(n)$ time. There is no contradiction, because they never
ask a comparison question. There *is* a price, and this chapter is careful
about it: these algorithms need keys with structure (small integers, fixed-width
strings, values from a known range), they use extra memory proportional to the
key range, and on a real machine running real Python they are often *beaten* by
`sorted()` anyway. Knowing when the linear-time sorts genuinely win is worth
more than knowing how to write them, so we measure that too, honestly.

## After this chapter you can …

- state precisely what makes a sorting algorithm "comparison-based", and
  classify any sort you meet;
- explain the decision-tree argument step by step — $n!$ orderings, $2^h$
  leaves, $h \ge \log_2(n!)$ — and reproduce it without notes;
- use Stirling's approximation to turn $\log_2(n!)$ into
  $n \log_2 n - 1.44n$, and say how good that approximation is;
- verify the bound experimentally by counting the comparisons a real merge sort
  performs;
- say exactly what the theorem does *not* forbid, and why that is the door the
  next section walks through;
- implement counting sort, explain what the prefix-sum array means, and
  demonstrate why iterating backwards is what makes it stable;
- compute the memory a counting sort would need for a given key range, and
  decide from that whether it is usable;
- implement LSD radix sort on top of a stable counting sort, explain why each
  pass must be stable, and show what breaks when it is not;
- implement bucket sort and demonstrate its quadratic worst case on skewed
  data;
- choose between a linear-time sort and `sorted()` for a concrete workload, and
  justify the choice with a measurement rather than an asymptotic symbol.

## Prerequisites

- [Chapter 22 · Sorting and searching](../ch22-sorting/index.md) — especially
  [merge sort and quicksort](../ch22-sorting/02-merge-quick.md), whose
  comparison counts we measure against the bound.
- [Chapter 16 · Algorithm analysis](../ch16-complexity/01-big-o.md) and
  [measuring runtimes](../ch16-complexity/02-timing.md) — the second half of
  this chapter is an extended lesson in why the asymptotic winner sometimes
  loses on the clock.
- [Chapter 7 · Arrays](../ch07-arrays/index.md) — counting sort is an
  array-indexing algorithm and nothing more.
- Helpful: the hash-table idea previewed in
  [section 25.1](../ch25-next/01-cs400-preview.md) — "use the key to compute
  the address" is exactly what these sorts do.

## Sections

1. [38.1 The comparison lower bound](01-lower-bound.md) — what "comparison
   sort" means, the decision tree for $n = 3$ drawn and enumerated in code,
   the $n! \le 2^h$ counting argument, Stirling's approximation stated gently
   and checked numerically, merge sort's real comparison counts against the
   bound for $n = 8, 16, 32$, and a careful statement of what the theorem does
   and does not forbid.
2. [38.2 Counting, radix, and bucket sort](02-counting-radix-bucket.md) — keys
   as addresses, counting sort with its count and prefix arrays printed at
   every stage, the backwards loop that buys stability demonstrated by breaking
   it, the honest arithmetic of the key range, LSD radix sort printed after
   each digit pass, bucket sort and its skewed worst case, a decision table,
   and a head-to-head timing against `sorted()` with an explanation of why the
   asymptotically slower algorithm often wins.
3. [Exercises](exercises.md) — lower-bound arithmetic, prefix sums by hand, a
   broken counting sort to repair, radix-pass prediction, sort selection for
   real scenarios, and a radix sort for fixed-length strings verified against
   `sorted()`.
