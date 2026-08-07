# 22.1 Elementary sorts

Python's `sorted()` is faster than anything we will write in this chapter,
so why study "slow" sorts at all? Three honest reasons. First,
*transparency*: selection and insertion sort are simple enough to hold
entirely in your head, which makes them the ideal specimens for practising
invariants and cost analysis. Second, *they are not actually slow at small
sizes* — for a dozen elements the quadratic sorts win on low overhead,
which is why real libraries (Python's and Java's included) switch to
insertion sort for tiny subarrays inside their fancy algorithms. Third,
*building blocks*: you cannot appreciate what merge sort and quicksort buy
you until you have counted what the elementary sorts cost.

## The experiment kit: counting comparisons

Timing runs ([Chapter 16](../ch16-complexity/02-timing.md)) wobble with
your machine's mood. For sorting there is a steadier instrument: count the
**comparisons** — every time the algorithm asks "is this element smaller
than that one?", increment a counter. Comparisons are the currency all our
sorts spend, the counts are exactly reproducible, and they map straight
onto the Big-O story. Every implementation in this chapter carries a
counter, and the counters are where the lessons live.

## Selection sort, revisited

You met selection sort in
[Chapter 8](../ch08-grids/03-first-algorithms.md); now we can say
precisely what it promises. The idea: find the smallest element, swap it
into slot 0; find the smallest of the rest, swap it into slot 1; continue.

Its **loop invariant** — the promise that holds every time the outer loop
comes around: *after $i$ passes, slots $0 \dots i-1$ hold the $i$ smallest
elements, in their final sorted positions.* The sorted prefix grows by one
per pass and is never touched again.

```python
def selection_sort(items):
    a = list(items)               # work on a copy
    comparisons = 0
    n = len(a)
    for i in range(n - 1):
        smallest = i
        for j in range(i + 1, n):
            comparisons += 1
            if a[j] < a[smallest]:
                smallest = j
        a[i], a[smallest] = a[smallest], a[i]
    return a, comparisons

result, count = selection_sort([29, 10, 14, 37, 13])
print(result)
print("comparisons:", count)
```

Five elements: the passes scan 4, 3, 2, then 1 candidates —
$4+3+2+1 = 10$ comparisons. In general pass $i$ scans $n-1-i$ elements, so
the total is

$$
(n-1) + (n-2) + \dots + 1 = \frac{n(n-1)}{2} \approx \frac{n^2}{2},
$$

which is $O(n^2)$. But here is the interesting part — that count does not
depend on the *values* at all. The inner loop scans every remaining
element no matter what it finds. Watch:

```python
import random

def selection_sort(items):
    a = list(items)
    comparisons = 0
    n = len(a)
    for i in range(n - 1):
        smallest = i
        for j in range(i + 1, n):
            comparisons += 1
            if a[j] < a[smallest]:
                smallest = j
        a[i], a[smallest] = a[smallest], a[i]
    return a, comparisons

random.seed(22)
n = 400
inputs = {
    "already sorted": list(range(n)),
    "random order  ": random.sample(range(n), n),
    "reversed      ": list(range(n - 1, -1, -1)),
}
for label, data in inputs.items():
    _, c = selection_sort(data)
    print(f"{label}: {c:,} comparisons")
print(f"n(n-1)/2 for n={n}: {n * (n - 1) // 2:,}")
```

All three lines print **79,800** — sorted, shuffled, or reversed, to the
comparison. Selection sort is **oblivious**: it does identical work
regardless of input, because it never uses what it learns mid-scan to skip
anything. Hand it an already-sorted list and it will diligently
double-check all 79,800 pairs. Remember this number; insertion sort is
about to embarrass it.

## Insertion sort

Insertion sort is how most people sort playing cards: keep the cards in
your left hand sorted, pick up the next card, and slide it leftward into
its place.

The invariant is subtly different from selection sort's: *after processing
element $i$, slots $0 \dots i$ are sorted **relative to each other*** —
but they are not necessarily in their final positions, because a small
card may still arrive and push them all rightward. Selection sort's prefix
is *finally placed*; insertion sort's prefix is merely *locally tidy*.
That difference is exactly what lets insertion sort quit early.

Trace it on `[7, 3, 9, 4, 2]` — each row is one pass, with the sorted
prefix marked off by a `·`:

| Pass | Insert | Before | After |
| ---- | ------ | ------ | ----- |
| $i=1$ | 3 | `[7 · 3, 9, 4, 2]` | `[3, 7 · 9, 4, 2]` — 3 shifts past 7 |
| $i=2$ | 9 | `[3, 7 · 9, 4, 2]` | `[3, 7, 9 · 4, 2]` — $9 \ge 7$, stays put: **one comparison, done** |
| $i=3$ | 4 | `[3, 7, 9 · 4, 2]` | `[3, 4, 7, 9 · 2]` — 4 slides past 9 and 7, stops at 3 |
| $i=4$ | 2 | `[3, 4, 7, 9 · 2]` | `[2, 3, 4, 7, 9]` — 2 slides past everyone |

The implementation shifts larger elements rightward with a `while` loop,
then drops the saved value into the gap (this is the shift technique from
[Chapter 7](../ch07-arrays/02-traversal-patterns.md), pointed backwards):

```python
def insertion_sort(items):
    a = list(items)
    comparisons = 0
    for i in range(1, len(a)):
        value = a[i]              # the card we picked up
        j = i - 1
        while j >= 0:
            comparisons += 1
            if a[j] > value:      # too big -> shift it right
                a[j + 1] = a[j]
                j -= 1
            else:                 # found something <= value -> stop early
                break
        a[j + 1] = value          # drop the card into the gap
    return a, comparisons

result, count = insertion_sort([7, 3, 9, 4, 2])
print(result)
print("comparisons:", count)
```

Nine comparisons for the trace above (1 + 1 + 3 + 4). Worst case — reversed
input, every card slides all the way home — is the same
$n(n-1)/2 \approx n^2/2$ as selection sort. But the `break` changes
everything on friendly inputs:

```python
import random

def insertion_sort(items):
    a = list(items)
    comparisons = 0
    for i in range(1, len(a)):
        value = a[i]
        j = i - 1
        while j >= 0:
            comparisons += 1
            if a[j] > value:
                a[j + 1] = a[j]
                j -= 1
            else:
                break
        a[j + 1] = value
    return a, comparisons

random.seed(22)
n = 400
nearly = list(range(n))
random.seed(5)
for _ in range(5):                 # spoil a sorted list with 5 adjacent swaps
    i = random.randrange(n - 1)
    nearly[i], nearly[i + 1] = nearly[i + 1], nearly[i]

random.seed(22)
inputs = {
    "already sorted": list(range(n)),
    "nearly sorted ": nearly,
    "random order  ": random.sample(range(n), n),
    "reversed      ": list(range(n - 1, -1, -1)),
}
for label, data in inputs.items():
    _, c = insertion_sort(data)
    print(f"{label}: {c:,} comparisons")
```

Read this next to selection sort's flat 79,800 / 79,800 / 79,800:

| Input (n = 400) | Selection | Insertion |
| --------------- | --------- | --------- |
| already sorted | 79,800 | **399** |
| nearly sorted | 79,800 | **404** |
| random order | 79,800 | 40,145 |
| reversed | 79,800 | 79,800 |

On sorted input each new card needs exactly one look — $n-1 = 399$ total:
that is $O(n)$, *linear*. Five out-of-place pairs cost just five extra
comparisons. Random input costs about $n^2/4$ (each card slides halfway,
on average) — half of selection's bill. Only the malicious reversed input
makes the two sorts equal. **Insertion sort is adaptive: the closer the
input is to sorted, the less it does.** This is its professional niche —
data that is *almost* in order (a sorted file with a few appended records,
a leaderboard after one score changes) — and it is why Timsort, coming in
[section 22.2](02-merge-quick.md), keeps insertion sort on staff.

Drag the slider to feel the quadratic curve — note how doubling $n$
roughly quadruples both counts on random data:

```yaml
# widget-config
sliders:
  n: {min: 10, max: 400, step: 10, default: 100, label: "list size n"}
```

```python
# widget — n is bound from the slider above
import random

size = int(n)
random.seed(0)
data = random.sample(range(size), size)

def selection_count(items):
    a = list(items)
    count = 0
    for i in range(len(a) - 1):
        smallest = i
        for j in range(i + 1, len(a)):
            count += 1
            if a[j] < a[smallest]:
                smallest = j
        a[i], a[smallest] = a[smallest], a[i]
    return count

def insertion_count(items):
    a = list(items)
    count = 0
    for i in range(1, len(a)):
        value = a[i]
        j = i - 1
        while j >= 0:
            count += 1
            if a[j] > value:
                a[j + 1] = a[j]
                j -= 1
            else:
                break
        a[j + 1] = value
    return count

print(f"random list of n = {size}")
print(f"selection sort: {selection_count(data):>7,} comparisons (always n(n-1)/2)")
print(f"insertion sort: {insertion_count(data):>7,} comparisons (about half)")
print(f"insertion on SORTED input would need just {size - 1}")
```

## Bubble sort, in one honest paragraph

Bubble sort repeatedly sweeps the list, swapping adjacent out-of-order
pairs; each sweep floats the largest remaining element to the end, and a
sweep with zero swaps proves the list is sorted, allowing an early exit.
It is taught everywhere because "swap neighbours until calm" is a
wonderfully visual first sorting idea — and used almost nowhere, because it
makes roughly as many comparisons as insertion sort but far more writes:
elements shuffle one slot at a time instead of leaping into place. With
the early-exit flag it shares insertion sort's $O(n)$ best case, and it
remains $O(n^2)$ otherwise. Consider it cultural literacy.

```python
def bubble_sort(items):
    a = list(items)
    for end in range(len(a) - 1, 0, -1):
        swapped = False
        for j in range(end):
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                swapped = True
        if not swapped:            # a calm sweep -> already sorted
            break
    return a

print(bubble_sort([6, 2, 8, 1, 4]))
```

## Stability: the tie-breaker rule

A sort is **stable** if elements that compare as equal keep their original
relative order. That sounds like trivia until your elements carry more
data than the sort key. Sort student records by grade and watch the names
inside each grade:

```python
records = [("Ava", 91), ("Ben", 85), ("Cody", 91),
           ("Dana", 85), ("Eli", 78)]

def insertion_sort_by_grade(items):
    a = list(items)
    for i in range(1, len(a)):
        record = a[i]
        j = i - 1
        while j >= 0 and a[j][1] > record[1]:   # strictly greater!
            a[j + 1] = a[j]
            j -= 1
        a[j + 1] = record
    return a

for name, grade in insertion_sort_by_grade(records):
    print(grade, name)
```

Ben and Dana both scored 85, and Ben — who came first in the input — still
comes first in the output; likewise Ava before Cody at 91. Insertion sort
is stable, and the load-bearing character is that `>` in the `while`: a
sliding card shifts only *strictly greater* neighbours, so it stops
*behind* any equal one rather than jumping over it. Change `>` to `>=` and
stability silently dies.

Why care? Because stable sorts **compose**. Sort those records by name
first, then stably by grade, and each grade group comes out
alphabetical — a two-level sort for free. Spreadsheets, database engines,
and `sorted()` itself (guaranteed stable) all lean on this. Selection sort,
by contrast, is not stable as usually written: its long-range swap can
airlift an element clean over a twin — you will catch it red-handed in
[the exercises](exercises.md).

!!! warning "Common mistakes"
    - **Blurring the two invariants.** Selection sort's prefix holds final
      values that never move again; insertion sort's prefix is sorted but
      still shifts as newcomers arrive. Exam questions love this
      distinction.
    - **Forgetting `j >= 0` in insertion sort's `while`.** Without the
      bounds check, the smallest card walks off the left edge — and Python's
      negative indexing turns that into silent corruption instead of a
      crash: `a[-1]` is the *last* element.
    - **Expecting selection sort to speed up on sorted input.** It cannot;
      it never looks at the data's order. If your "optimised" selection
      sort reports fewer comparisons on sorted input, you have accidentally
      written a different algorithm.
    - **Writing `>=` where stability needs `>`.** Sliding equal elements
      past each other (insertion sort) — or swapping on ties anywhere —
      reorders equal keys and breaks composed sorts in ways no small test
      catches.

## Check your understanding

1. Selection sort makes 4,950 comparisons on a random list of 100 items.
   Exactly how many does it make on a *sorted* list of 100 items? On a
   list of 200 random items?

    ??? success "Answer"
        4,950 again — selection sort is oblivious, so order never changes
        its count, which is always $n(n-1)/2 = 100 \cdot 99 / 2$. For
        $n = 200$: $200 \cdot 199/2 = 19{,}900$ — doubling $n$ roughly
        quadruples the work, the signature of $O(n^2)$.

2. During insertion sort's pass $i = 3$ on `[3, 7, 9, 4, 2]`, list the
   comparisons made, in order, while inserting the 4.

    ??? success "Answer"
        4 vs 9 (shift 9), 4 vs 7 (shift 7), 4 vs 3 (stop — 3 is not
        greater). Three comparisons, two shifts, and 4 drops into index 1:
        `[3, 4, 7, 9, 2]`.

3. Your log file is sorted by timestamp except for about ten stragglers
   that arrived slightly late. You will sort it once. Which elementary
   sort, and what is the rough cost?

    ??? success "Answer"
        Insertion sort: nearly-sorted input is its best case. Cost is
        roughly $O(n + d)$ where $d$ is the total displacement of the
        stragglers — close to one comparison per element, versus
        $n^2/2$ for selection sort no matter what.

4. A stable sort processes `[("b", 2), ("a", 1), ("c", 1)]` by the number.
   What orders are possible for the output? What if the sort is unstable?

    ??? success "Answer"
        Stable: exactly one output —
        `[("a", 1), ("c", 1), ("b", 2)]`, with `"a"` before `"c"` because
        that is their input order. Unstable: `("c", 1)` may also come out
        before `("a", 1)`; both orders are "correctly sorted", which is
        precisely why stability must be promised separately.
