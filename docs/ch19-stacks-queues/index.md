# Chapter 19 · Iterators, Stacks, and Queues

In [Chapter 18](../ch18-linked-lists/index.md) you built a linked list with
your own hands, node by node. This chapter turns raw structures like that one
into everyday tools. First we open up the most familiar statement in Python —
`for` — and discover the small, elegant machine hiding inside it: the
**iterator protocol**. Once you know the protocol, you can teach *any* class
you write, including your linked list, to work with `for`, `in`, `list()`,
and `sum()` — and Python's generators let you do it in a handful of lines.

Then come two of the most useful abstract data types in all of computing:
the **stack** and the **queue**. Both are just sequences with a discipline.
A stack only ever adds and removes at one end — last in, first out — and that
single restriction is exactly what a bracket-matching parser, an undo system,
and the function call stack all need. A queue adds at one end and removes at
the other — first in, first out — which is exactly what a printer spooler, a
ticket line, and (as you will see in the next chapter) a level-by-level tree
walk all need. Restricting a structure sounds like a loss; in practice it
buys clarity, correctness, and guaranteed $O(1)$ costs.

These three ideas feed directly into the rest of Part III:
[Chapter 20](../ch20-bst/index.md) uses a queue to traverse trees level by
level, [Chapter 21](../ch21-heaps/index.md) builds the priority queue — a
queue where the most urgent item, not the oldest, comes out first — and every
recursive algorithm you have written since
[Chapter 17](../ch17-recursion/index.md) has been running on a stack the
whole time.

## After this chapter you can …

- explain what `for x in obj:` actually does — `iter()`, repeated `next()`,
  and the `StopIteration` signal — and drive an iterator by hand;
- make your own classes iterable by implementing `__iter__` and `__next__`,
  or by writing a generator with `yield`;
- state the difference between an *iterable* and an *iterator*, and predict
  what happens when you try to reuse an exhausted iterator;
- implement a `Stack` class and use it to check balanced brackets, model
  undo/redo, and explain the function call stack;
- explain why `list.pop(0)` is $O(n)$, why `collections.deque` is the right
  queue in Python, and how a circular buffer wraps around with `%`;
- choose between raising an exception and returning `None` when designing a
  data structure's API — and defend the choice.

## Prerequisites

- [Chapter 18 · ADTs and Linked Lists](../ch18-linked-lists/index.md) — the
  `Node`/`LinkedList` classes and the idea of an abstract data type.
- [Chapter 16 · Algorithm Analysis](../ch16-complexity/index.md) — Big-O
  notation, used for every cost claim in this chapter.
- [Chapter 17 · Recursion](../ch17-recursion/index.md) — the call stack,
  which turns out to be the most important stack of all.

## Sections

1. [19.1 Iterators](01-iterators.md) — how `for` really works, the
   `__iter__`/`__next__` protocol, iterating your own linked list, and
   generators with `yield`.
2. [19.2 Stacks](02-stacks.md) — LIFO, push/pop/peek, balanced brackets,
   undo/redo, the call stack, and API design (raise vs `None`).
3. [19.3 Queues](03-queues.md) — FIFO, why the naive list queue is slow,
   `collections.deque`, circular buffers, and a printer-queue simulation.
4. [Exercises](exercises.md) — stack prediction puzzles, a postfix
   calculator, hot potato, and a queue built from two stacks.
