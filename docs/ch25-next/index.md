# Chapter 25 · The Road Ahead

You have come a remarkably long way. In Chapter 0 a variable was a mystery
and a bit was a rumour; now you can build a binary search tree, argue about
whether an algorithm is $O(n)$ or $O(n \log n)$, and read a stack trace
without flinching.

This chapter closes Part IV and does two things.

**First, it gives you a taste of the third course.** The classic *data
structures and algorithms* semester contains balanced trees, hash tables, and
graphs — each introduced here just far enough that when you meet them for
real, they will feel like old acquaintances rather than strangers. Every one
of those previews is then built properly in
[Part VI](../part6-overview.md), which continues straight on from here.

**Second, it hands you a map.** The roadmap section starts with the seventeen
chapters of this handbook that come *after* this one —
[Part V · AI Engineering](../part5-overview.md) and
[Part VI · Programming III](../part6-overview.md) — and then lays out steps
organised by goal for when those run out too: solidify what you know,
practise deliberately, build real things, read great code. None of it is
homework. All of it is invitation.

There is no exercises page in this chapter, and that is deliberate: the
exercise *is* what you do next.

## After this chapter you can …

- explain the problem that AVL trees, red-black trees, and B-trees solve,
  and what a rotation does in one sentence;
- describe how a hash table turns a key into a bucket index — and recognise
  that Python's `dict` has been one all along;
- model a real-world network as a graph, store it as an adjacency list, and
  trace breadth-first search finding the shortest number of hops;
- say what the remaining two parts of this handbook contain and pick the one
  that fits your goal;
- name the big topics that lie outside even those — dynamic programming,
  concurrency, networks — and say in a sentence what each is about;
- pick a personal next step (chapter, practice site, project, book) with a
  concrete plan for how to use it.

## Prerequisites

This chapter leans on the whole of Part III, especially:

- [Chapter 16 · Algorithm Analysis](../ch16-complexity/index.md) — Big-O
  vocabulary is used freely here.
- [Chapter 19 · Iterators, Stacks, and Queues](../ch19-stacks-queues/index.md)
  — breadth-first search is a queue wearing a trench coat.
- [Chapter 20 · Binary Search Trees](../ch20-bst/index.md) — the balance
  problem raised there gets its answer here.
- [Chapter 21 · Heaps and Priority Queues](../ch21-heaps/index.md) — heaps
  return in Dijkstra's algorithm.

## Sections

1. [25.1 A preview of Programming III](01-cs400-preview.md) — balanced
   trees, hash tables, and graphs: why each exists, plus one runnable taste
   of each, and a pointer to the Part VI chapter that builds it in full.
2. [25.2 Your roadmap](02-roadmap.md) — where to go from here: first the rest
   of this book, then steps organised by goal, ending with the only three
   habits that matter.

## Part IV in brief

Part IV took you from "programs that work" to "programs and machines you can
reason about". What you now carry forward into Parts V and VI:

- **Trees** are the first non-linear structure, defined recursively, and a
  binary search tree turns lookup into a walk down one short path
  ([Chapter 20](../ch20-bst/index.md)).
- Every BST operation costs $O(h)$ — which is $O(\log n)$ only while the
  tree stays bushy, and $O(n)$ the moment sorted input arrives.
- **Heaps** trade the BST's total ordering for one modest rule and get a
  guaranteed $O(\log n)$ priority queue that lives in a plain list
  ([Chapter 21](../ch21-heaps/index.md)).
- **Sorting** is a menu of trade-offs — adaptive versus oblivious, stable
  versus not, guaranteed versus expected — and counting comparisons settles
  every argument ([Chapter 22](../ch22-sorting/index.md)).
- **Binary search** is the payoff for sorting, and a five-line function with
  a museum of classic bugs.
- **The operating system** shares one machine among many processes by
  time-slicing, isolating their memory, and gating every real effect behind
  a system call ([Chapter 23](../ch23-os/index.md)).
- A running program's memory is a map — code, static data, heap, stack — and
  that map explains `RecursionError`, amortized `append`, and how garbage
  collection can still leak.
- Your Python is **compiled to bytecode** and executed by a virtual machine
  which, on this very site, is itself compiled to WebAssembly.
- **Engineering practice** — branches and pull requests, arrange–act–assert
  tests, edge-case checklists, names and reviews — is what makes code
  survivable by other people ([Chapter 24](../ch24-practice/index.md)).
- And this chapter's previews — balanced trees, hash tables, graphs — are
  the doors into [Part VI](../part6-overview.md), while
  [Part V](../part5-overview.md) takes the same foundations somewhere else
  entirely.

Two parts follow, and neither depends on the other. Pick the one that matches
what you want to build next.
