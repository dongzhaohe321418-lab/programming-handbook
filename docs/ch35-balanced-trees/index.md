# Chapter 35 · Balanced Search Trees

[Chapter 20](../ch20-bst/index.md) ended with a confession. A binary search
tree gives you insert, search, and delete in $O(h)$ time, and in a bushy
tree $h$ is about $\log_2 n$ — a million keys in twenty steps. But $h$ is
not a law of nature; it is a consequence of the order the keys happened to
arrive in. Feed the same tree its keys already sorted and it degenerates
into a linked list of height $n-1$, and every logarithm in the chapter turns
back into a linear scan. Worse, sorted input is not an exotic attack: log
entries by timestamp, database rows by auto-incrementing id, names imported
alphabetically. The failure mode is the *common* case.

This chapter closes that hole four times over. It starts with the single
structural move that makes repair possible — the **rotation**, a
three-pointer re-wiring that changes a tree's shape while leaving its
in-order traversal untouched — and then builds three complete answers on top
of it. **AVL trees** enforce the tightest useful balance rule and stay
within about 44% of a perfect tree's height. **Red-black trees** relax the
rule in exchange for cheaper updates, which is why they are the tree inside
Java's `TreeMap`, C++'s `std::map`, and the Linux kernel. **B-trees** throw
out the binary shape entirely: when your data lives on a disk, the cost that
matters is blocks read, not comparisons, and a tree with 256-way branching
answers a query over a billion keys in four block reads instead of thirty.

Everything here is verified rather than asserted. Every invariant is stated
as a formula, drawn in a diagram, and then checked by a runnable validator
that runs after every operation — including randomized stress tests that
delete thousands of keys and re-check the structure after each one. If a
claim in this chapter says a tree stays balanced, there is code on the page
that proves it did.

## After this chapter you can …

- perform left, right, left-right, and right-left rotations by hand and in
  code, and explain why every one of them preserves the in-order traversal;
- state the AVL invariant formally, compute balance factors, and identify
  which of the four cases (LL, RR, LR, RL) applies to any unbalanced node;
- implement a complete AVL tree with insertion, deletion, and cached
  heights, and verify it with a randomized stress test;
- state the five red-black properties exactly, write a validator that names
  which one a broken tree violates, and trace the insertion fix-up cases;
- explain the black-height argument for the $2\log_2(n+1)$ height bound;
- say honestly why red-black deletion is usually left to a library, and what
  "doubly black" means;
- explain why a disk changes the cost model, and compute how many block
  reads a B-tree of a given branching factor needs;
- implement B-tree search, insertion by splitting, and deletion by borrowing
  or merging, and explain why every relational index is a B+ tree.

## Prerequisites

- [Chapter 20 · Binary Search Trees](../ch20-bst/index.md) — the BST
  invariant, insert/search/delete, traversals, and especially
  [the balance problem](../ch20-bst/03-traversals-balance.md) that this
  chapter exists to solve.
- [Chapter 16 · Algorithm Analysis](../ch16-complexity/index.md) — $O(\log
  n)$ versus $O(n)$, and why constants sometimes matter after all.
- [Chapter 17 · Recursion](../ch17-recursion/index.md) — every operation
  here is written recursively.
- [Chapter 22 · Sorting and Searching](../ch22-sorting/03-searching.md) —
  binary search reappears *inside* each B-tree node.
- Helpful but not required:
  [Chapter 23 · Memory layout](../ch23-os/02-memory-layout.md) for the
  block-and-page model that motivates B-trees, and
  [Chapter 21 · Heaps](../ch21-heaps/index.md) for a second example of a
  tree kept balanced by an invariant rather than by luck.

## Sections

1. [35.1 Rotations](01-rotations.md) — the balance problem measured, the
   insight that many trees hold the same sorted data, single and double
   rotations derived from first principles, and a checker proving in-order
   traversal survives every one.
2. [35.2 AVL trees](02-avl.md) — the height-difference invariant, cached
   heights and balance factors, the four rebalancing cases as a
   hand-followable decision table, a full implementation with deletion, and
   the $1.44\log_2 n$ height bound verified empirically.
3. [35.3 Red-black trees](03-red-black.md) — the five colour properties, a
   validator that names the violated one, the black-height argument, the
   insertion fix-up loop implemented and checked after every insert, an
   honest account of deletion, and where these trees live in real software.
4. [35.4 B-trees and the disk](04-b-trees.md) — why a block-transfer cost
   model changes the answer, wide nodes and equal-depth leaves, splitting
   and merging implemented and stress-tested, B+ trees with linked leaves,
   and a closing comparison across every structure in the chapter.
5. [Exercises](exercises.md) — rotation identification, AVL prediction,
   red-black colour repair, B-tree splits by hand, empirical height
   measurement, and a full AVL deletion to write yourself.
