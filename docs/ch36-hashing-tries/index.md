# Chapter 36 · Hashing, Tries, and Skip Lists

You have been using a hash table since [Chapter 14](../ch14-beyond/01-collections-tour.md).
Every `counts[word] += 1`, every `if user in seen`, every `cache.get(key)`
reached into one and came back instantly, and the handbook has so far asked
you to take that on faith. This chapter opens the box. By the end of
[36.1](01-hash-tables.md) you will have written a working `dict` — get, put,
remove, `len`, `in` — out of nothing but a list and one arithmetic idea:
**stop searching for the key and compute where it must be**. And you will
have measured, not been told, what separates a good hash function from a
disastrous one.

[Chapter 35](../ch35-balanced-trees/index.md) closed the hole where a binary
search tree collapses on sorted input. Hash tables have a hole of their own,
and it is stranger: they are $O(1)$ *on average* and $O(n)$ when the keys
conspire, and the conspiracy can be arranged deliberately by an attacker.
[Section 36.2](02-collisions-resizing.md) proves collisions are unavoidable
(the birthday paradox says a million-bucket table collides after about 1178
keys), implements chaining and the three probing schemes, walks into the
tombstone bug and fixes it, plots the classic cost-versus-load-factor
curves, and ends with the comparison table that finally answers the question
every beginner asks: **why don't dictionaries keep things in order?**

The last two sections are the structures that pick up what hash tables drop.
A **trie** ([36.3](03-tries.md)) stores keys as *paths*, which makes prefix
questions — autocomplete, spell-checking, IP routing — cost $O(L)$ in the
length of the query and nothing at all in the number of keys stored; you
will build a genuinely usable autocomplete engine with frequency ranking. A
**skip list** ([36.4](04-skip-lists.md)) reaches balanced-tree performance
with coin flips instead of rotations, in eighty lines with no case analysis,
which is why it shows up inside Redis, RocksDB, and Java's concurrent
collections. Everything is verified on the page: every invariant has a
runnable checker, every complexity claim has a measurement, and every
"trust me" is replaced by a print statement.

## After this chapter you can …

- explain how a lookup can cost the same for ten keys and ten million, and
  demonstrate it with a measurement;
- write a hash function, judge one against the four criteria (deterministic,
  uniform, fast, avalanche), and *measure* its bucket distribution with a
  chi-squared test and a plot;
- say why table size matters, and show a good hash function ruined by a bad
  one;
- implement a complete `HashMap` with chaining — `get`, `put`, `remove`,
  `__len__`, `__contains__` — and a second one with open addressing;
- state the hash/equality contract, implement `__hash__` and `__eq__`
  correctly on your own class, and recognise the silent data loss that
  follows from breaking either rule;
- compute how many keys a table of $m$ buckets tolerates before a collision
  becomes likely, from the birthday formula;
- compare separate chaining, linear probing, quadratic probing, and double
  hashing, and explain primary clustering with numbers;
- delete from an open-addressed table without corrupting it, and say what a
  tombstone is for;
- choose a load-factor threshold from the cost curves, implement
  rehash-on-threshold, and explain why doubling makes insertion amortized
  $O(1)$;
- explain hash flooding, why CPython randomizes string hashes, and what
  Java's tree-ified buckets buy;
- choose correctly between a hash table, a balanced tree, and a sorted array
  — and explain why a `dict` cannot answer range queries;
- implement a trie with insert, search, prefix collection, and the subtle
  pruning delete, and build an autocomplete engine on top of it;
- explain what a radix/PATRICIA tree compresses and why routers use one;
- implement a skip list with search, insert, and delete, and explain what
  "expected $O(\log n)$" gives you and what it withholds compared with AVL.

## Prerequisites

- [Chapter 14 · Beyond the basics](../ch14-beyond/01-collections-tour.md) —
  you have used `dict` and `set`; this chapter builds them.
- [Chapter 16 · Algorithm Analysis](../ch16-complexity/index.md) — $O(1)$
  versus $O(\log n)$ versus $O(n)$, and especially
  [amortized cost](../ch16-complexity/03-complexity-zoo.md), which is what
  makes resizing free.
- [Chapter 17 · Recursion](../ch17-recursion/index.md) — trie collection and
  deletion are both recursive walks.
- [Chapter 18 · Linked Lists](../ch18-linked-lists/02-singly-linked.md) — a
  chained hash bucket is a linked list, and a skip list is several of them
  stacked. [Doubly linked lists](../ch18-linked-lists/03-doubly-linked.md)
  return in the final exercise.
- [Chapter 12 · Classes](../ch12-classes/index.md) — `__hash__`, `__eq__`,
  and `__len__` are the dunder methods from that chapter, used in earnest.
- [Chapter 35 · Balanced Search Trees](../ch35-balanced-trees/index.md) —
  the structure this chapter is repeatedly compared against. Section 36.4
  is a direct alternative to [AVL](../ch35-balanced-trees/02-avl.md).

## Sections

1. [36.1 Hash tables from scratch](01-hash-tables.md) — the $O(1)$ promise
   measured, three hash functions compared and plotted, why a sum of
   character codes fails, powers of two versus primes, a complete chaining
   `HashMap`, hashability and immutability, and the `__hash__`/`__eq__`
   contract with Java's `hashCode`/`equals` alongside.
2. [36.2 Collisions and resizing](02-collisions-resizing.md) — the birthday
   paradox simulated, chaining measured against $1 + \alpha/2$, linear
   probing's primary clustering counted, quadratic probing and double
   hashing, the tombstone bug demonstrated and fixed, probe-count curves
   versus load factor, amortized $O(1)$ from doubling, hash flooding, and
   the hash-versus-tree-versus-array comparison.
3. [36.3 Tries](03-tries.md) — the key as a path, end-of-word markers, a
   complete trie with prefix collection and pruning delete, $O(L)$
   independence from $n$ measured, radix/PATRICIA compression, a working
   frequency-ranked autocomplete engine, and longest-prefix IP routing.
4. [36.4 Skip lists](04-skip-lists.md) — from a sorted linked list to
   express lanes, coin-flip promotion verified by histogram, a complete
   implementation with the update array, a traced search, expected versus
   guaranteed $O(\log n)$, and why Redis and RocksDB chose one.
5. [Exercises](exercises.md) — bucket arithmetic by hand, a broken hash
   function to diagnose, collision prediction, a tombstone repair, trie
   prefix counting, a scaling measurement, a skip-list trace, and an LRU
   cache built from a `dict` and a doubly linked list.
