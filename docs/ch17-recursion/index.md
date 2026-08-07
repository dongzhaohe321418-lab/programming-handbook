# Chapter 17 · Recursion

A function that calls itself sounds like a paradox — how can something be
defined in terms of itself without going in circles? Yet you already use
self-referential definitions comfortably in mathematics: $n! = n \times (n-1)!$
defines the factorial of $n$ using a *smaller* factorial, and the chain
bottoms out at $0! = 1$. Recursion is exactly that idea turned into code, and
this chapter's first job is to convince you there is no magic involved: a
recursive call is an ordinary function call, handled by the same
[call stack](../ch05-under-the-hood/03-stack-heap.md) you met in Chapter 5.

Once the mechanism is demystified, we tour the classics — summing lists,
reversing strings, fast exponentiation, binary search, Fibonacci, and the
Towers of Hanoi — and along the way meet both recursion's superpower
(problems that shrink into smaller copies of themselves almost solve
themselves) and its trap (naive recursion can redo the same work an
exponential number of times, which *memoization* fixes spectacularly).
Finally we put recursion and iteration side by side: every loop can be
rewritten as recursion and vice versa, so the real skill is knowing which
shape fits which problem — and knowing the honest limits, like Python's
recursion depth cap.

Recursion is also the key that unlocks the rest of Part III. Binary search
trees in [Chapter 20](../ch20-bst/index.md) are recursive structures through
and through, and the fast sorting algorithms in
[Chapter 22](../ch22-sorting/index.md) are divide-and-conquer recursions. The
effort you invest here pays off for the remainder of the book.

**After this chapter you can …**

- explain what happens on the call stack when a function calls itself, and
  trace a recursive run frame by frame;
- design a recursive function by stating its **base case** and showing that
  every call makes **progress** toward it;
- write the classic recursive algorithms (list sum, string reversal,
  `power`, binary search, Fibonacci, Towers of Hanoi) from their definitions;
- recognise exponential blow-up in naive recursion and fix it with a memo
  dictionary or `functools.lru_cache`;
- convert a recursive algorithm into an iterative one with an explicit
  stack, and say when each style is the better engineering choice;
- explain why a missing base case ends in `RecursionError` in Python and
  `StackOverflowError` in Java.

**Prerequisites.** You should be comfortable writing functions
([Chapter 3](../ch03-functions/index.md)), know how the stack and heap divide
a program's memory ([Chapter 5](../ch05-under-the-hood/index.md)), and be
able to read Big-O claims like $O(n)$ and $O(2^n)$
([Chapter 16](../ch16-complexity/index.md)).

**Sections**

1. [17.1 The call stack](01-call-stack.md) — a recursive call is just a
   function call; the two laws of recursion; what happens when there is no
   base case.
2. [17.2 Classic recursive problems](02-classic-recursion.md) — the canon,
   from list sums to Hanoi, plus memoization and a fractal drawn by
   recursion.
3. [17.3 Recursion vs iteration](03-vs-iteration.md) — the same job in two
   shapes, converting between them, and the truth about tail calls.
4. [Exercises](exercises.md)
