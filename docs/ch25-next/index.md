# Chapter 25 · The Road Ahead

You have come a remarkably long way. In Chapter 0 a variable was a mystery
and a bit was a rumour; now you can build a binary search tree, argue about
whether an algorithm is $O(n)$ or $O(n \log n)$, and read a stack trace
without flinching. This final chapter does two things. First, it gives you a
guided taste of what a third programming course — the classic *data
structures and algorithms* semester — actually contains: balanced trees,
hash tables, and graphs, each introduced just far enough that when you meet
them for real, they will feel like old acquaintances rather than strangers.

Second, it hands you a map. Courses end; learning to program does not. The
roadmap section lays out concrete next steps organised by goal — solidify
what you know, practise deliberately, build real things, read great code —
so that the day after you finish this handbook is not a blank page. None of
it is homework. All of it is invitation.

There is no exercises page in this chapter, and that is deliberate: the
exercise *is* what you do next.

## After this chapter you can …

- explain the problem that AVL trees, red-black trees, and B-trees solve,
  and what a rotation does in one sentence;
- describe how a hash table turns a key into a bucket index — and recognise
  that Python's `dict` has been one all along;
- model a real-world network as a graph, store it as an adjacency list, and
  trace breadth-first search finding the shortest number of hops;
- name the big topics that come after this book — dynamic programming,
  concurrency, networks — and say in a sentence what each is about;
- pick a personal next step (practice site, project, book) with a concrete
  plan for how to use it.

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
   of each.
2. [25.2 Your roadmap](02-roadmap.md) — where to go from here, organised by
   goal, ending with the only three habits that matter.
