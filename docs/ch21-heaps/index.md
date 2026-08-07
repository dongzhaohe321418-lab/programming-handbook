# Chapter 21 · Heaps and Priority Queues

The queues of [Chapter 19](../ch19-stacks-queues/index.md) are scrupulously
fair: first in, first out. But many real systems are *deliberately* unfair. An
emergency room treats the heart attack before the sprained ankle, no matter
who arrived first; an operating system runs the urgent task before the
background backup. What these systems need is a **priority queue** — a
collection where the next item out is always the *most important* one, even
while new items keep arriving. This chapter builds the data structure that
makes priority queues fast: the **binary heap**.

The heap is a tree, but a strangely relaxed one. Where the binary search tree
of [Chapter 20](../ch20-bst/index.md) keeps *everything* in order, a heap
enforces just one modest rule — each parent is no bigger than its children —
and profits enormously from the discount: it never goes lopsided, it lives
inside a plain Python list with no node objects or pointers at all, and its
two core operations run in $O(\log n)$ *guaranteed*, not just on a lucky day.
The price is that a heap can answer only one question quickly: *what is the
smallest item?* This chapter is the story of why that narrow bargain is one
of the best deals in computer science.

We first pin down the heap's two invariants — the heap property and the
complete shape — and the index arithmetic that turns a tree into a list. Then
we implement the two repair operations, sift-up and sift-down, grow them into
a working `MinHeap` class, meet Python's built-in `heapq` module, and put the
heap to work twice: as **heapsort**, a guaranteed $O(n \log n)$ sorting
algorithm, and as the **top-k pattern** used all over data processing.

## After this chapter you can …

- state the min-heap property and explain precisely how it differs from the
  binary search tree invariant;
- store a complete binary tree in a plain list and navigate it with the index
  formulas $\mathtt{parent} = (i-1)/2$ (floored), $\mathtt{left} = 2i+1$,
  $\mathtt{right} = 2i+2$;
- decide at a glance whether a given list is a valid min-heap;
- trace and implement sift-up (for insert) and sift-down (for extract-min),
  and explain why both cost $O(\log n)$;
- use `heapq` fluently, including the `(priority, item)` tuple pattern and
  the negation trick for max-heaps;
- sort with a heap, and find the $k$ largest of a huge collection without
  sorting all of it.

## Prerequisites

- [Chapter 16 · Algorithm Analysis](../ch16-complexity/index.md) — Big-O
  notation, especially $O(\log n)$.
- [Chapter 19 · Iterators, Stacks, and Queues](../ch19-stacks-queues/index.md)
  — the queue ADT that priority queues generalise.
- [Chapter 20 · Binary Search Trees](../ch20-bst/index.md) — tree vocabulary
  (root, leaf, height) and the BST invariant we will contrast against.

## Sections

1. [21.1 The heap property](01-heap-property.md) — the
   repeatedly-need-the-minimum problem, the heap invariant vs the BST
   invariant, complete trees, and the index math that stores a tree in a
   list.
2. [21.2 Priority queues and heapsort](02-priority-queues.md) — sift-up and
   sift-down, a full `MinHeap` class, the `heapq` module, heapsort, and the
   top-k pattern.
3. [Exercises](exercises.md) — index-math drills, paper traces of sift
   operations, heap validators, and merging $k$ sorted lists.
