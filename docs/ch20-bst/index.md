# Chapter 20 · Binary Search Trees

Every structure so far — arrays, lists, stacks, queues — has been a *line*:
one thing after another. This chapter introduces the first structure shaped
like the problems it solves: the **tree**, a hierarchy of nodes branching
from a single root, exactly the shape of a file system, an org chart, or a
tournament bracket.

Trees are also where [Chapter 17](../ch17-recursion/index.md)'s recursion
stops being a party trick and becomes the natural way to think: every node
of a tree is itself the root of a smaller tree, so almost every tree
algorithm is a few lines that call themselves on the left and right halves.

The star of the chapter is the **binary search tree (BST)**: a binary tree
that keeps everything smaller to the left and everything larger to the
right, *everywhere*. That one invariant lets insert, search, and delete all
run in time proportional to the tree's **height** — and in a bushy tree the
height of $n$ nodes is only about $\log_2 n$. A million items, roughly
twenty steps.

We build the full structure honestly: insert, search, min and max, and all
three cases of delete, each one drawn before it is coded. The chapter then
closes with the two ideas that set up everything after it:

- **The four classic traversals** — three recursive walks, plus the
  level-by-level walk powered by
  [Chapter 19](../ch19-stacks-queues/03-queues.md)'s queue.
- **The balance problem** — the honest admission that feeding a BST sorted
  input degrades it into a linked list, and the reason self-balancing trees
  exist (previewed in [Chapter 25](../ch25-next/01-cs400-preview.md) and
  built for real in [Chapter 35](../ch35-balanced-trees/index.md)).

## After this chapter you can …

- use the tree vocabulary precisely: root, leaf, parent, child, sibling,
  edge, path, subtree, and the difference between a node's *depth* and a
  tree's *height*;
- state the BST invariant exactly, and spot a tree that "looks sorted
  locally" but violates it globally;
- implement and trace `insert`, `contains`, `find_min`/`find_max`, and all
  three delete cases (leaf, one child, two children via in-order successor);
- write in-order, pre-order, post-order, and level-order traversals, and
  predict their output on any given tree;
- explain why in-order traversal of a BST always emits sorted order;
- measure how insertion *order* controls a BST's height, explain why every
  cost in the chapter is really $O(h)$, and say what self-balancing trees
  fix.

## Prerequisites

- [Chapter 17 · Recursion](../ch17-recursion/index.md) — trees are defined
  recursively, and nearly every algorithm here calls itself.
- [Chapter 18 · ADTs and Linked Lists](../ch18-linked-lists/index.md) —
  nodes and references; a tree node is a list node with two `next`s.
- [Chapter 19 · Iterators, Stacks, and Queues](../ch19-stacks-queues/index.md)
  — level-order traversal runs on a queue.
- [Chapter 16 · Algorithm Analysis](../ch16-complexity/index.md) — $O(h)$
  and $O(\log n)$ claims throughout.

## Sections

1. [20.1 Tree vocabulary](01-tree-vocab.md) — hierarchies, the naming of
   parts, trees as recursive structures, binary trees, and why log-depth
   search is worth wanting.
2. [20.2 BST operations](02-bst-ops.md) — the invariant, then insert,
   search, min/max, and the three delete cases, every one diagrammed and
   coded.
3. [20.3 Traversals and the balance problem](03-traversals-balance.md) —
   four ways to visit every node, the sorted-order proof, and what sorted
   input does to an unbalanced tree.
4. [Exercises](exercises.md) — invariant puzzles, traversal prediction,
   recursive tree measurements, and delete drills.
