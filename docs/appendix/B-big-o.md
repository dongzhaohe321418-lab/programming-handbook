# B · Big-O reference

The whole book's complexity knowledge on one page. Costs are for the usual
implementations, **average case unless marked otherwise**; "amortized"
means occasional expensive operations averaged over many cheap ones
([Chapter 9.2](../ch09-collections/02-dynamic-lists.md)). If any notation
here looks unfamiliar, [Chapter 16.1](../ch16-complexity/01-big-o.md) is
the full story.

## The growth families

| Notation | Name | Plain-English intuition | Where you met it |
| --- | --- | --- | --- |
| $O(1)$ | constant | same cost whether $n$ is 10 or 10 million | stack push/pop ([Ch 19.2](../ch19-stacks-queues/02-stacks.md)), `dict` lookup ([Ch 14.1](../ch14-beyond/01-collections-tour.md)) |
| $O(\log n)$ | logarithmic | halve the problem at every step | binary search ([Ch 22.3](../ch22-sorting/03-searching.md)), balanced BST ([Ch 20.2](../ch20-bst/02-bst-ops.md)) |
| $O(n)$ | linear | touch everything once | linear search, list traversal ([Ch 7.2](../ch07-arrays/02-traversal-patterns.md)) |
| $O(n \log n)$ | linearithmic | sort territory: $\log n$ passes over $n$ items | merge sort ([Ch 22.2](../ch22-sorting/02-merge-quick.md)), heapsort ([Ch 21.2](../ch21-heaps/02-priority-queues.md)) |
| $O(n^2)$ | quadratic | compare every pair | selection/insertion sort ([Ch 22.1](../ch22-sorting/01-elementary-sorts.md)), nested loops ([Ch 6.3](../ch06-loops/03-nested-break-continue.md)) |
| $O(2^n)$ | exponential | try every subset | naive recursive Fibonacci ([Ch 17.2](../ch17-recursion/02-classic-recursion.md)) |
| $O(n!)$ | factorial | try every ordering | brute-forcing all routes through $n$ cities |

The whole zoo, with worked examples:
[Chapter 16.3](../ch16-complexity/03-complexity-zoo.md).

## Picture the growth

One picture explains why the family matters more than the constant.
Every curve here is drawn as if one step costs the same — watch what
happens anyway:

```python
import numpy as np
import matplotlib.pyplot as plt

n = np.linspace(1, 30, 300)

plt.figure(figsize=(7, 4.5))
plt.plot(n, np.ones_like(n), label="$O(1)$")
plt.plot(n, np.log2(n), label="$O(\\log n)$")
plt.plot(n, n, label="$O(n)$")
plt.plot(n, n * np.log2(n), label="$O(n \\log n)$")
plt.plot(n, n ** 2, label="$O(n^2)$")
plt.plot(n, 2.0 ** n, label="$O(2^n)$")
plt.ylim(0, 200)
plt.xlim(1, 30)
plt.xlabel("n  (input size)")
plt.ylabel("basic operations")
plt.title("Growth families: by n = 30 the race is already over")
plt.legend(loc="upper left")
plt.grid(True, alpha=0.3)
```

$O(2^n)$ exits through the ceiling before $n$ reaches 8; $O(n^2)$ follows
by $n \approx 14$; the three curves you can still see at the right edge —
constant, logarithmic, linear(ish) — are the ones that scale. Measuring
this for real, with timers: [Chapter 16.2](../ch16-complexity/02-timing.md).

## What Python's built-ins cost

`list` (a dynamic array — [Ch 9.2](../ch09-collections/02-dynamic-lists.md)):

| Operation | Cost | Note |
| --- | --- | --- |
| `xs[i]`, `xs[i] = v` | $O(1)$ | direct index arithmetic |
| `xs.append(v)` | $O(1)$ amortized | occasional resize-and-copy |
| `xs.pop()` (end) | $O(1)$ | |
| `xs.pop(0)`, `xs.insert(0, v)` | $O(n)$ | shifts every element — use `deque` |
| `v in xs`, `xs.index(v)` | $O(n)$ | linear scan |
| `xs[a:b]` slice | $O(b-a)$ | copies the slice |
| `xs + ys` | $O(n+m)$ | copies both |
| `xs.sort()`, `sorted(xs)` | $O(n \log n)$ | Timsort; see the sorting table |
| `len(xs)` | $O(1)$ | stored, not counted |

`dict` and `set` (hash tables — [Ch 14.1](../ch14-beyond/01-collections-tour.md)):

| Operation | Cost | Note |
| --- | --- | --- |
| `d[k]`, `d[k] = v`, `del d[k]` | $O(1)$ avg | $O(n)$ worst with pathological collisions |
| `k in d`, `v in s`, `s.add(v)` | $O(1)$ avg | the reason membership tests love sets |
| iterate all items | $O(n)$ | |
| `len(d)` | $O(1)$ | |

`collections.deque` (the proper queue —
[Ch 19.3](../ch19-stacks-queues/03-queues.md)):

| Operation | Cost | Note |
| --- | --- | --- |
| `append`, `appendleft`, `pop`, `popleft` | $O(1)$ | both ends, always |
| `dq[i]` in the middle | $O(n)$ | it is not an array — don't index it |

`str` (immutable — [Ch 3.2](../ch03-functions/02-strings.md)):

| Operation | Cost | Note |
| --- | --- | --- |
| `len(s)`, `s[i]` | $O(1)$ | |
| `s + t` | $O(n+m)$ | builds a brand-new string |
| `sub in s`, `s.find(sub)` | $O(n)$ typical | |
| `"".join(parts)` | $O(\text{total length})$ | the right way to assemble strings |
| `s += piece` in a loop | $O(n^2)$ overall | the wrong way — each `+=` recopies |

## What Java's collections cost

| Structure | Access | Add at end | Add/remove at front | Search | Notes |
| --- | --- | --- | --- | --- | --- |
| `ArrayList` | $O(1)$ `get(i)` | $O(1)$ amortized | $O(n)$ | $O(n)$ | Java's `list` |
| `LinkedList` | $O(n)$ `get(i)` | $O(1)$ | $O(1)$ | $O(n)$ | doubly linked ([Ch 18.3](../ch18-linked-lists/03-doubly-linked.md)) |
| `HashMap` / `HashSet` | $O(1)$ avg by key | $O(1)$ avg `put`/`add` | — | $O(1)$ avg | worst $O(n)$; no ordering |
| `TreeMap` / `TreeSet` | $O(\log n)$ | $O(\log n)$ | — | $O(\log n)$ | red-black tree; keys stay sorted ([Ch 25.1](../ch25-next/01-cs400-preview.md)) |
| `ArrayDeque` | ends only, $O(1)$ | $O(1)$ | $O(1)$ | $O(n)$ | stack *and* queue of choice |
| `PriorityQueue` | $O(1)$ `peek` | $O(\log n)$ `offer` | $O(\log n)$ `poll` | $O(n)$ | binary heap ([Ch 21](../ch21-heaps/index.md)) |

## Part III structures at a glance

| Structure | Operation | Typical | Worst | Taught in |
| --- | --- | --- | --- | --- |
| Singly linked list | prepend / remove head | $O(1)$ | $O(1)$ | [Ch 18.2](../ch18-linked-lists/02-singly-linked.md) |
| | append with tail pointer | $O(1)$ | $O(1)$ | |
| | find / index / append without tail | $O(n)$ | $O(n)$ | |
| Doubly linked list | insert/remove at either end | $O(1)$ | $O(1)$ | [Ch 18.3](../ch18-linked-lists/03-doubly-linked.md) |
| | remove a node you already hold | $O(1)$ | $O(1)$ | |
| Stack | push / pop / peek | $O(1)$ | $O(1)$ | [Ch 19.2](../ch19-stacks-queues/02-stacks.md) |
| Queue | enqueue / dequeue | $O(1)$ | $O(1)$ | [Ch 19.3](../ch19-stacks-queues/03-queues.md) |
| BST — **balanced** | search / insert / delete | $O(\log n)$ | $O(\log n)$ | [Ch 20.2](../ch20-bst/02-bst-ops.md) |
| BST — **degenerate** | search / insert / delete | — | $O(n)$ | [Ch 20.3](../ch20-bst/03-traversals-balance.md) |
| Any binary tree | full traversal | $O(n)$ | $O(n)$ | [Ch 20.3](../ch20-bst/03-traversals-balance.md) |
| Binary heap | peek min/max | $O(1)$ | $O(1)$ | [Ch 21.1](../ch21-heaps/01-heap-property.md) |
| | push / pop | $O(\log n)$ | $O(\log n)$ | |
| | build from $n$ items (heapify) | $O(n)$ | $O(n)$ | |
| Hash table | get / put / delete | $O(1)$ avg | $O(n)$ | [Ch 14.1](../ch14-beyond/01-collections-tour.md) |

The balanced-vs-degenerate BST gap is the punchline of
[Chapter 20](../ch20-bst/index.md): the *shape* of the tree, not the code,
decides which column you live in.

## Sorting and searching

The algorithms of [Chapter 22](../ch22-sorting/index.md), plus the two
library sorts you actually call. **Stable** means equal items keep their
original order — why that matters is in
[Chapter 22.1](../ch22-sorting/01-elementary-sorts.md).

| Algorithm | Best | Average | Worst | Extra space | Stable? |
| --- | --- | --- | --- | --- | --- |
| Selection sort | $O(n^2)$ | $O(n^2)$ | $O(n^2)$ | $O(1)$ | no |
| Insertion sort | $O(n)$ | $O(n^2)$ | $O(n^2)$ | $O(1)$ | yes |
| Bubble sort (early exit) | $O(n)$ | $O(n^2)$ | $O(n^2)$ | $O(1)$ | yes |
| Merge sort | $O(n \log n)$ | $O(n \log n)$ | $O(n \log n)$ | $O(n)$ | yes |
| Quicksort | $O(n \log n)$ | $O(n \log n)$ | $O(n^2)$ | $O(\log n)$ avg | no |
| Heapsort ([Ch 21.2](../ch21-heaps/02-priority-queues.md)) | $O(n \log n)$ | $O(n \log n)$ | $O(n \log n)$ | $O(1)$ | no |
| Timsort — Python's `sort()`/`sorted()` | $O(n)$ | $O(n \log n)$ | $O(n \log n)$ | $O(n)$ | yes |

!!! info "Java corner"

    `Arrays.sort` uses dual-pivot quicksort for primitives (fast, not
    stable — irrelevant for `int`s, which are indistinguishable when
    equal) and a Timsort variant for objects, where stability *is*
    observable and guaranteed. `Collections.sort` is the object case.

Searching ([Chapter 22.3](../ch22-sorting/03-searching.md)):

| Algorithm | Cost | Requirement |
| --- | --- | --- |
| Linear search | $O(n)$ | none — works on anything |
| Binary search | $O(\log n)$ | data **sorted**, with $O(1)$ indexing |

Binary search on a *linked* list is still $O(n)$ — jumping to the middle
costs a walk. The precondition is two-part: sorted **and** random-access.

## How big can $n$ get? — the back of the envelope

Rule of thumb: a tight loop runs very roughly $10^7$–$10^8$ simple steps
per second in Python, and $10^8$–$10^9$ in Java or C. To guess whether an
approach can finish in about a second, match your $n$ to the worst
complexity you can afford:

| If $n$ is up to… | You can afford… | Feel |
| --- | --- | --- |
| ~10 | $O(n!)$ | try every ordering |
| ~20 | $O(2^n)$ | try every subset |
| ~500 | $O(n^3)$ | triple nested loop |
| ~10,000 | $O(n^2)$ | double nested loop |
| ~1,000,000 | $O(n \log n)$ | sort it and go |
| ~100,000,000 | $O(n)$ | one pass, nothing fancy |
| anything at all | $O(\log n)$, $O(1)$ | effectively free |

These are order-of-magnitude estimates, not promises — constants,
languages, and hardware shift every boundary. But when a problem says
"$n$ can be one million" and your plan is a double loop, this table is
telling you, politely, to think again.
