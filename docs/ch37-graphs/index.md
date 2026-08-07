# Chapter 37 · Graphs

Every structure so far has been about *containment*. A list contains items in
order. A tree contains a parent's children. A heap contains a root that
dominates everything below it. Graphs are about something else entirely:
**relationships between things that have no hierarchy at all**. Two cities
joined by a road, two people who follow each other, two tasks where one must
finish before the other starts — none of these fit in a tree, because a tree
insists every node has exactly one parent and the whole thing has no cycles.
Drop those two rules and you get a graph, which turns out to be the most
widely applicable data structure in computing. The moment you can say "these
things are connected like *this*", you can run the algorithms in this chapter
on them.

That generality is why graphs dominate technical interviews and production
systems in equal measure. Route planning, package managers resolving
dependencies, compilers ordering build steps, social networks suggesting
friends, spell-checkers, garbage collectors, network routing tables, and the
"related items" strip on every shopping site are all graph algorithms wearing
different clothes. This chapter covers the core four: how to *store* a graph
(§37.1), how to *walk* one (§37.2), how to find the *cheapest* route through
one (§37.3), and how to *connect* one at minimum cost (§37.4). Between them
they are perhaps eighty percent of the graph algorithms you will ever need.

The chapter is built on things you already own. Breadth-first search is a
[queue](../ch19-stacks-queues/03-queues.md) plus a
[set](../ch14-beyond/01-collections-tour.md). Depth-first search is the same
loop with a [stack](../ch19-stacks-queues/02-stacks.md), or with
[recursion](../ch17-recursion/index.md) letting the call stack do the work.
Dijkstra's algorithm is breadth-first search with the queue upgraded to the
[priority queue you built in Chapter 21](../ch21-heaps/02-priority-queues.md).
Kruskal's algorithm starts by [sorting](../ch22-sorting/index.md) the edges.
Nothing here is a new primitive; it is old primitives pointed at a new kind of
data. Every algorithm is traced on a drawn example before it is implemented,
and every failure mode — the cycle that traps a naive walk, the negative edge
that breaks Dijkstra, the heuristic that stops being admissible — is
demonstrated with code that actually misbehaves, not merely described.

## After this chapter you can …

- define vertex, edge, degree, path, cycle, connected, strongly connected, and
  DAG precisely, and identify each on a drawing;
- choose between an adjacency matrix, an adjacency list, and an edge list from
  the density of the graph and the operations you need, and justify the choice
  with a memory measurement;
- implement breadth-first and depth-first search — recursively and with an
  explicit stack — and explain why the *only* structural difference is the
  container they pull from;
- explain why a visited set is what makes graph traversal terminate, and count
  the repeat visits that happen without one;
- use traversal to find connected components, 2-colour a bipartite graph,
  detect cycles in directed and undirected graphs, and topologically sort a
  DAG with both Kahn's algorithm and DFS finishing times;
- reconstruct a shortest unweighted path from BFS parent pointers;
- implement Dijkstra's algorithm with a binary heap, state its greedy
  invariant, and explain lazy deletion versus decrease-key;
- show a concrete graph where Dijkstra returns a *wrong* answer, explain
  exactly which step fails, and fix it with Bellman-Ford — including
  negative-cycle detection;
- add an admissible heuristic to get A\*, and measure the reduction in node
  expansions;
- state the cut property and use it to explain why both Prim's and Kruskal's
  algorithms produce a minimum spanning tree;
- implement union-find with union by rank and path compression, and state its
  cost honestly;
- cluster points by building an MST and cutting its heaviest edges.

## Prerequisites

- [Chapter 14 · Collections](../ch14-beyond/01-collections-tour.md) — `dict`
  and `set`, which *are* the adjacency list and the visited set.
- [Chapter 16 · Algorithm analysis](../ch16-complexity/01-big-o.md) — this
  chapter's costs are quoted in two variables, $V$ and $E$, and you need to be
  comfortable with what that means.
- [Chapter 17 · Recursion](../ch17-recursion/index.md), especially
  [recursion versus iteration](../ch17-recursion/03-vs-iteration.md) — DFS is
  written both ways here.
- [Chapter 19 · Stacks and queues](../ch19-stacks-queues/index.md) — the two
  containers that separate DFS from BFS.
- [Chapter 20 · Trees](../ch20-bst/01-tree-vocab.md) — a tree is a special
  graph, and the vocabulary carries over almost unchanged.
- [Chapter 21 · Heaps and priority queues](../ch21-heaps/02-priority-queues.md)
  — the engine inside Dijkstra, A\*, and Prim.
- [Chapter 22 · Sorting](../ch22-sorting/index.md) — Kruskal's algorithm is
  "sort the edges, then be greedy".

## Sections

1. [37.1 Representing graphs](01-representations.md) — five real graphs drawn
   and defined, the full vocabulary against one worked picture, adjacency
   matrix versus adjacency list versus edge list, a memory measurement showing
   exactly when a matrix wastes space, and the small `Graph` class the rest of
   the chapter uses.
2. [37.2 Breadth-first and depth-first search](02-traversal.md) — BFS by
   levels with a queue, DFS recursively and with an explicit stack, the one
   structural difference shown side by side, why the visited set is what makes
   cycles safe, and five applications implemented: components, bipartite
   checking, cycle detection, topological sort, and unweighted shortest paths.
3. [37.3 Shortest paths](03-shortest-paths.md) — why weights break BFS,
   Dijkstra's greedy invariant and heap implementation with a step-by-step
   frontier trace, a graph where Dijkstra is *wrong*, Bellman-Ford and
   negative-cycle detection, A\* with measured expansion counts, and
   Floyd-Warshall in three lines.
4. [37.4 Minimum spanning trees](04-mst.md) — why the answer is a tree, the
   cut property that justifies both algorithms, Prim with a heap, Kruskal with
   union-find, a run of both on the same graph with the totals checked equal,
   and MST-based clustering plotted on real points.
5. [Exercises](exercises.md) — representation choices, traversal-order
   prediction, cycle hunting, a hand-traced Dijkstra, a hand-built
   Dijkstra counterexample, `has_path` and `all_paths`, union-find by hand,
   and bidirectional BFS with measured savings.
