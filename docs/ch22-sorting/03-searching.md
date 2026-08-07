# 22.3 Searching

Sorting is only half of the classic pair — the other half is the question
that made sorting worthwhile in the first place: *is this value in the
collection, and where?* This section covers the only two searches most
programs ever need: the plodding-but-universal linear search, and binary
search — an algorithm five lines long, blazingly fast, and so famously
easy to get *slightly* wrong that we will tour its bugs like a museum.

## Linear search: the unsorted world's only option

If the data is in no particular order, no cleverness is possible: any
element could be anywhere, so the only strategy is to look at each in turn.

```python
def linear_search(items, target):
    for i, value in enumerate(items):
        if value == target:
            return i
    return -1                        # convention: -1 means "not found"

data = [41, 8, 95, 2, 72, 16, 5]
print(linear_search(data, 72))       # 4
print(linear_search(data, 40))       # -1
```

Cost: $O(n)$ — a miss checks all $n$ elements, an average hit about
$n/2$. This is what Python's `in` operator and `list.index` do on a list.
Nothing beats it *on unsorted data*, because any element you skip could
have been the target. To do better, you need a promise about the data's
arrangement — and "the data is sorted" is exactly such a promise.

## Binary search: the halving walk

You have played this game: "I'm thinking of a number from 1 to 100."
Nobody guesses 1, then 2, then 3 — you guess 50, learn *which half* the
answer is in, and repeat. Each guess halves the candidates: 100 → 50 → 25
→ 13 → 7 → 4 → 2 → 1, so seven guesses always suffice, because
$2^7 = 128 \ge 100$. That is the $O(\log n)$ halving story from
[Chapter 16](../ch16-complexity/01-big-o.md), and **binary search** is
that game played against a sorted list: compare the target with the
*middle* element; too small means the target can only live in the right
half, too big means the left half; repeat on the survivor.

We track the still-possible region with two indices, `lo` and `hi`
(inclusive on both ends). Searching for `72` in this 15-element list:

```text
index:  0   1   2   3   4   5   6   7   8   9  10  11  12  13  14
value:  2   5   8  12  16  23  38  41  56  72  88  91  95  97  99
```

| Step | `lo` | `hi` | `mid` | `items[mid]` | Verdict |
| ---- | ---- | ---- | ----- | ------------ | ------- |
| 1 | 0 | 14 | 7 | 41 | 41 < 72 → discard indices 0–7, `lo = 8` |
| 2 | 8 | 14 | 11 | 91 | 91 > 72 → discard indices 11–14, `hi = 10` |
| 3 | 8 | 10 | 9 | 72 | found — return 9 |

Three probes to search fifteen elements; linear search would have taken
ten. And the gap explodes with size — $\lceil \log_2(n+1) \rceil$ probes
against $n$: a million elements need 20 probes, a billion need 30.

## The implementation

```python
def binary_search(items, target):
    lo, hi = 0, len(items) - 1         # inclusive bounds of the live region
    while lo <= hi:                    # region still has at least 1 element
        mid = (lo + hi) // 2
        if items[mid] == target:
            return mid
        elif items[mid] < target:
            lo = mid + 1               # mid itself is ruled out
        else:
            hi = mid - 1               # mid itself is ruled out
    return -1

data = [2, 5, 8, 12, 16, 23, 38, 41, 56, 72, 88, 91, 95, 97, 99]
print(binary_search(data, 72))    # 9   (the trace above)
print(binary_search(data, 2))     # 0   edge: first element
print(binary_search(data, 99))    # 14  edge: last element
print(binary_search(data, 40))    # -1  absent, between 38 and 41
print(binary_search(data, 100))   # -1  absent, off the right end
```

Five lines of logic — with a legendary bug record. The idea was published
in 1946, yet by Donald Knuth's account the first version correct for
*every* list size did not appear until 1962; and when Jon Bentley later
asked groups of professional programmers to write it, roughly nine out of
ten produced a buggy version. The failure modes are so classic they
deserve exhibits.

## The bug museum

Every exhibit below is shown as *non-runnable* text, because two of them
would loop forever in your browser. Compare each against the correct
version above; the fix is always the rule in bold.

**Exhibit A — the stale bound** (`hi = mid` instead of `mid - 1`):

```text
while lo <= hi:
    mid = (lo + hi) // 2
    if items[mid] == target:
        return mid
    elif items[mid] < target:
        lo = mid + 1
    else:
        hi = mid            # BUG: mid stays in the live region
```

Search this for `40` in `[38, 41]`: eventually `lo == hi == mid`, the
element is bigger than the target, and `hi = mid` changes *nothing* — the
same state repeats forever. **After a failed probe, `mid` is disqualified;
both updates must step past it** (`mid + 1` or `mid - 1`).

**Exhibit B — the non-moving floor** (`lo = mid` instead of `mid + 1`):

```text
    elif items[mid] < target:
        lo = mid            # BUG: when hi == lo + 1, mid == lo ...
```

With a two-element region, `(lo + hi) // 2` rounds *down* to `lo`; if the
probe says "go right", `lo = mid` re-creates the identical region. Same
disease as Exhibit A, opposite wall.

**Exhibit C — the shrunken loop** (`while lo < hi` instead of `<=`):

```text
while lo < hi:              # BUG: quits while one candidate remains
```

No infinite loop this time — instead the search abandons the final
one-element region unprobed, so it reports `-1` for targets that are
present (try `2` in a one-element list mentally). **`lo <= hi` is correct
precisely because both bounds are inclusive.**

**Exhibit D — the overflow** (`mid = (lo + hi) / 2` in Java). Harmless in
Python; a genuine, historic bug in Java:

=== "Python"

    ```python
    lo, hi = 2_000_000_000, 2_100_000_000
    mid = (lo + hi) // 2          # Python ints never overflow
    print(mid)                    # 2050000000, no drama
    ```

=== "Java"

    ```java
    int lo = 2_000_000_000, hi = 2_100_000_000;   // both fit in int...
    int mid = (lo + hi) / 2;      // BUG: lo + hi = 4.1e9 overflows int,
                                  // wraps negative -> ArrayIndexOutOfBounds
    int fixed = lo + (hi - lo) / 2;   // the standard remedy
    ```

Java's `int` tops out at $2^{31} - 1 \approx 2.1$ billion
([Chapter 5](../ch05-under-the-hood/01-numeric-pitfalls.md)), so `lo + hi`
can wrap negative even when both indices are individually legal. This
exact bug sat in Java's own `Arrays.binarySearch` for nine years before
being noticed in 2006. The remedy `lo + (hi - lo) / 2` never forms a sum
bigger than `hi`. Python's integers are arbitrary-precision, so
`(lo + hi) // 2` is genuinely fine — but recognise the Java idiom when
you meet it.

## The recursive version

Binary search is "search a smaller range" repeated — which you can spell
with a loop, as above, or with recursion
([Chapter 17](../ch17-recursion/03-vs-iteration.md)): the base case is an
empty region, and each call delegates to a half-sized subproblem.

```python
def binary_search_rec(items, target, lo=0, hi=None):
    if hi is None:
        hi = len(items) - 1
    if lo > hi:                        # base case: region is empty
        return -1
    mid = (lo + hi) // 2
    if items[mid] == target:
        return mid
    if items[mid] < target:
        return binary_search_rec(items, target, mid + 1, hi)
    return binary_search_rec(items, target, lo, mid - 1)

data = [2, 5, 8, 12, 16, 23, 38, 41, 56, 72, 88, 91, 95, 97, 99]
print(binary_search_rec(data, 72))   # 9
print(binary_search_rec(data, 40))   # -1
```

Both versions make identical probes; the recursion just stores `lo`/`hi`
in stack frames instead of loop variables. The iterative form is the
practical default (no stack depth, no call overhead) — the recursive form
is worth writing once to see how neatly "search half" nests inside itself.

## The standard library, as usual, got there first

Python's [`bisect`](https://docs.python.org/3/library/bisect.html) module
ships tuned binary searches. `bisect_left(a, x)` returns the index where
`x` *would be inserted* to keep `a` sorted — which doubles as "the index
of the first element $\ge$ `x`":

```python
import bisect

data = [2, 5, 8, 12, 16, 23, 38, 41, 56, 72, 88, 91, 95, 97, 99]

print(bisect.bisect_left(data, 72))   # 9  -> 72 lives at index 9
print(bisect.bisect_left(data, 40))   # 7  -> 40 would slot in at index 7

# membership test, binary-search fast:
i = bisect.bisect_left(data, 40)
print(i < len(data) and data[i] == 40)    # False: 40 is absent

bisect.insort(data, 40)               # insert, keeping the list sorted
print(data[5:10])                     # [23, 38, 40, 41, 56]
```

Note the different contract: our `binary_search` answers "*where is it?*
(or −1)", while `bisect_left` answers "*where does it belong?*" — never
−1. The pattern in the middle converts the second answer into the first.
When duplicates exist, `bisect_left` finds the *leftmost* position — the
find-first-occurrence problem in
[the exercises](exercises.md) — and `insort` keeps a
list sorted under a trickle of insertions (each one is an $O(\log n)$
search plus an $O(n)$ shift, the sorted-list tax from
[Chapter 21](../ch21-heaps/01-heap-property.md)).

=== "Python"

    ```python
    import bisect
    data = [2, 5, 8, 12]
    print(bisect.bisect_left(data, 8))    # 2
    ```

=== "Java"

    ```java
    import java.util.Arrays;
    import java.util.Collections;
    import java.util.List;

    int[] data = {2, 5, 8, 12};
    int i = Arrays.binarySearch(data, 8);        // 2
    int j = Arrays.binarySearch(data, 9);        // negative: -(insertion point) - 1
    // j == -4 here; decode with:  insertionPoint = -(j + 1)  -> 3

    List<Integer> list = List.of(2, 5, 8, 12);
    int k = Collections.binarySearch(list, 8);   // 2
    ```

Java's version packs both answers into one `int`: non-negative means
found-at-index, negative encodes where it *would* go. Both libraries
demand **sorted input** — hand them an unsorted array and they return
confident nonsense, not an error.

## The economics: when does sorting pay for itself?

Binary search's fine print is the sorted-data requirement, and sorting
costs $O(n \log n)$. So which is cheaper overall — scanning unsorted data
$m$ times, or sorting once and then binary-searching $m$ times?

$$
\underbrace{m \cdot \tfrac{n}{2}}_{\text{just scan every time}}
\quad\text{vs}\quad
\underbrace{n \log_2 n}_{\text{sort once}} +
\underbrace{m \cdot \log_2 n}_{\text{cheap searches}}
$$

Plug in $n = 100{,}000$ and let $m$ grow:

```python
import math

n = 100_000
log_n = round(math.log2(n))               # ~17 probes per binary search
sort_cost = round(n * math.log2(n))       # one-time investment

print(f"{'searches':>8} | {'scan every time':>15} | {'sort + binary':>13} | winner")
for m in [1, 10, 33, 34, 100, 10_000]:
    scan = m * n // 2
    sort_then = sort_cost + m * log_n
    winner = "sort first" if sort_then < scan else "just scan"
    print(f"{m:>8} | {scan:>15,} | {sort_then:>13,} | {winner}")
```

For one search, sorting first is absurd — thirty times the work of a
simple scan. The sort is an *investment*, repaid at roughly
$n/2 - \log_2 n$ comparisons per subsequent search, and here the
break-even lands between $m = 33$ and $m = 34$: from the mid-thirties on,
sorting first wins, and by $m = 10{,}000$ it wins by a factor of several
hundred. Hence the universal pattern — *load once, sort once, query
forever* — behind phone contact lists, dictionary files, and database
indexes. (If you *keep inserting* while querying, re-sorting each time
wrecks the math — that moving-target workload is what
[binary search trees](../ch20-bst/index.md) and
[heaps](../ch21-heaps/index.md) are for.)

## The chapter in one table

| Algorithm | Best | Average | Worst | Extra memory | Stable? |
| --------- | ---- | ------- | ----- | ------------ | ------- |
| Selection sort | $O(n^2)$ | $O(n^2)$ | $O(n^2)$ | $O(1)$ | no |
| Insertion sort | $O(n)$ | $O(n^2)$ | $O(n^2)$ | $O(1)$ | yes |
| Bubble sort (flagged) | $O(n)$ | $O(n^2)$ | $O(n^2)$ | $O(1)$ | yes |
| Merge sort | $O(n \log n)$ | $O(n \log n)$ | $O(n \log n)$ | $O(n)$ | yes |
| Quicksort | $O(n \log n)$ | $O(n \log n)$ | $O(n^2)$ | $O(\log n)$ stack | no |
| Heapsort ([Ch 21](../ch21-heaps/02-priority-queues.md)) | $O(n \log n)$ | $O(n \log n)$ | $O(n \log n)$ | $O(1)$ | no |
| Timsort (`sorted()`) | $O(n)$ | $O(n \log n)$ | $O(n \log n)$ | $O(n)$ | yes |

| Search | Requirement | Cost |
| ------ | ----------- | ---- |
| Linear search | none | $O(n)$ |
| Binary search | sorted data | $O(\log n)$ |

!!! warning "Common mistakes"
    - **Binary-searching unsorted data.** No error, no warning — just
      wrong answers that *sometimes* look right. The sortedness
      precondition is entirely your responsibility.
    - **Bound updates that keep `mid` alive.** `lo = mid` or `hi = mid`
      with an inclusive loop is an infinite loop waiting for the right
      input (Exhibits A and B). Every branch must shrink the region.
    - **Mixing bound conventions.** We use inclusive `hi = len - 1` with
      `while lo <= hi`. An exclusive-`hi` style (`hi = len`,
      `while lo < hi`, `hi = mid`) is *also* correct — but only as a
      package. Swapping pieces between the two styles produces the museum.
    - **Expecting `bisect_left` to return −1.** It reports an insertion
      point, never absence; you must compare `data[i]` against the target
      yourself.

## Check your understanding

1. How many probes does binary search need, worst case, on a sorted list
   of 1,000,000 elements? And on 1,000,000,000?

    ??? success "Answer"
        About 20 and 30: $\lceil \log_2 (10^6) \rceil = 20$,
        $\lceil \log_2(10^9) \rceil = 30$. A thousand-fold increase in
        data costs ten extra probes — the halving story in one sentence.

2. Trace binary search for `16` on the 15-element list in this section:
   list the `(lo, hi, mid)` triples visited.

    ??? success "Answer"
        `(0, 14, 7)` → 41 too big, go left; `(0, 6, 3)` → 12 too small,
        go right; `(4, 6, 5)` → 23 too big, go left; `(4, 4, 4)` →
        `items[4]` is 16 — found at index 4. Four probes.

3. Exhibit C (`while lo < hi`) returns −1 for some present targets. On
   the list `[7]`, searching for `7`, what happens step by step?

    ??? success "Answer"
        `lo = 0`, `hi = 0`; the condition `0 < 0` is false, the loop body
        never runs, and it returns −1 — despite the target sitting right
        there at index 0. A one-element region is exactly what
        `lo <= hi` exists to probe.

4. A program loads 50,000 unsorted product IDs and must answer whether
   *three* particular IDs are present, then exits. Sort first or scan?
   What if it instead had to answer 5,000 such queries?

    ??? success "Answer"
        Three queries: scan — roughly $3 \times 25{,}000 = 75{,}000$
        comparisons, versus about $50{,}000 \times 15.6 \approx 780{,}000$
        just to sort. (A Python `set` would also crush this, but that is
        [Chapter 14](../ch14-beyond/01-collections-tour.md)'s hashing
        story.) At 5,000 queries, scanning costs about 125 million while
        sort-plus-search costs under a million — sort first, and it is
        not close.
