# Chapter 18 · ADTs and Linked Lists

Until now, "a list" has meant one thing: Python's built-in `list` (or Java's
`ArrayList`), a resizable array. This chapter splits that single idea into
two layers that professionals keep rigorously separate. An **abstract data
type (ADT)** is the *contract* — which operations exist and what they
promise. A **data structure** is the *implementation* — how the data is
actually arranged in memory to honour that contract. The same List contract
can be honoured by a contiguous array *or* by a chain of little node objects
scattered across the heap and stitched together with references — and the
two choices have opposite performance personalities. Choosing between them
is the first genuinely architectural decision of your programming life.

The chain-of-nodes idea is the **linked list**, and it is this chapter's
centrepiece. You will build one node by node: first singly linked (each node
knows only its successor), then doubly linked (each node also knows its
predecessor), and finally with a *sentinel* node — a professional trick that
makes a whole family of edge-case bugs structurally impossible. Along the
way you will learn the discipline of **pointer surgery**: drawing the
before/after picture first, then writing the assignments in an order that
never lets a node slip out of reach. Linked lists are where diagrams stop
being decoration and become the actual method of programming.

Why does this matter beyond the exercise? Because everything in the next
four chapters is nodes and references: stacks and queues
([Chapter 19](../ch19-stacks-queues/index.md)) are thin wrappers over these
structures, and trees ([Chapter 20](../ch20-bst/index.md)) are simply nodes
whose "next" grew into "left and right". Master the pointer moves here, on a
straight chain, and trees will feel like a variation instead of a mountain.

**After this chapter you can …**

- state the difference between an ADT and a data structure, and read an
  operations-cost table to choose an implementation;
- explain what generics (`List<String>`, `list[str]`, `Stack[T]`) buy you in
  Java and what type hints honestly do — and do not do — in Python;
- build a singly linked list from scratch with `append`, `prepend`, `find`,
  `delete`, `__len__`, and `__repr__`, and draw every pointer move;
- perform safe pointer surgery: order your assignments so no node is ever
  unreachable, and explain a wrong-order bug when you see one;
- extend nodes with a `prev` reference, do the four-pointer middle
  insertion, and use a sentinel to collapse edge cases into one code path;
- reach for `collections.deque` (or Java's `ArrayDeque`/`LinkedList`) when
  you need these behaviours in production code.

**Prerequisites.** You need references and aliasing from
[Chapter 9](../ch09-collections/01-references.md) (a `Node` variable *is* a
reference), class-writing from [Chapter 12](../ch12-classes/index.md), and
Big-O vocabulary from [Chapter 16](../ch16-complexity/01-big-o.md).
[Chapter 17](../ch17-recursion/index.md)'s recursion helps for the exercises
but is not required.

**Sections**

1. [18.1 Abstract data types and generics](01-adts-generics.md) — WHAT vs
   HOW, the List contract, and one implementation for many element types.
2. [18.2 Singly linked lists](02-singly-linked.md) — the Node idea, building
   the class operation by operation, and pointer-surgery discipline.
3. [18.3 Doubly linked lists](03-doubly-linked.md) — the `prev` reference,
   four-pointer insertion, sentinels, and the production-grade `deque`.
4. [Exercises](exercises.md)
