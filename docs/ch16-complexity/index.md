# Chapter 16 · Algorithm Analysis

In [Chapter 14](../ch14-beyond/02-choosing-algorithms.md) you compared
algorithms informally — "this one feels faster on big inputs" — and in
[Chapter 8](../ch08-grids/03-first-algorithms.md) you met your first sorts
and searches. This chapter replaces the feeling with a tool. The question
"how fast is this algorithm?" turns out to have a slippery answer if you
measure in seconds (whose laptop? which Python? was a video rendering in
the background?) and a beautifully stable one if you instead *count steps
as a function of the input size n*. That counting discipline, and the
notation built on it — **Big-O** — is the single most-used piece of theory
in all of programming. Interviews lean on it, documentation is written in
it, and every data structure in the rest of this book is advertised by it.

The chapter works from both ends. First we count: you will run code with
step counters bolted on and *derive* the famous growth families — constant,
logarithmic, linear, quadratic — rather than memorise them. Then we
measure: real timings with `time.perf_counter`, a doubling experiment that
reveals an algorithm's growth family from the outside, and log-log plots
where the slope literally *is* the exponent. Finally we assemble the whole
zoo in one table and one picture, including the honest fine print —
amortized costs, and when a "slower" algorithm wins in practice because
constants matter. Big-O deliberately throws those constant factors away, but
they are real, and they come from the machine: the **CPU performance equation**
in [23.5.1](../ch23b-architecture/01-performance.md) is exactly the
instructions × cycles-per-instruction × cycle-time that a Big-O class hides.
Complexity counts *operations*; architecture counts *cycles* — the two halves of
"how long will this take?"

After this chapter you can:

- count the operations a piece of code performs as a function of $n$,
- read and write Big-O notation, and justify why
  $3n^2 + 5n + 20 \in O(n^2)$,
- distinguish best, worst, and average cases, and say which one Big-O
  statements usually describe,
- time code correctly (repeat, take the minimum) and run a doubling
  experiment to infer a growth family empirically,
- place $O(1)$, $O(\log n)$, $O(n)$, $O(n \log n)$, $O(n^2)$, and $O(2^n)$
  on one mental map, with a named algorithm attached to each,
- estimate "how big can $n$ be?" for a given time budget, and explain what
  *amortized* $O(1)$ means for `list.append`.

**Prerequisites:** loops ([Chapter 6](../ch06-loops/index.md)), lists and
their operations ([Chapter 7](../ch07-arrays/index.md)), the first
algorithms of [Chapter 8](../ch08-grids/index.md), and the collections tour
of [Chapter 14](../ch14-beyond/01-collections-tour.md). Results here are
used constantly from [Chapter 18](../ch18-linked-lists/index.md) onward,
and are summarised for reference in
[Appendix B](../appendix/B-big-o.md).

**Sections**

1. [16.1 Big-O notation](01-big-o.md) — counting steps, growth families,
   and the formal definition (gently).
2. [16.2 Measuring running time](02-timing.md) — `perf_counter`, the
   doubling experiment, log-log plots, and timing pitfalls.
3. [16.3 The complexity zoo](03-complexity-zoo.md) — all the families in
   one table and one figure; amortized costs; built-in operation costs.
4. [Exercises](exercises.md)
