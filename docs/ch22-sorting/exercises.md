# Exercises

## The chapter in brief

- Counting **comparisons** is a steadier instrument than timing runs, and
  every algorithm in the chapter carries a counter
  ([22.1](01-elementary-sorts.md)).
- **Selection sort is oblivious**: exactly $n(n-1)/2$ comparisons on every
  input, sorted or shuffled or reversed.
- **Insertion sort is adaptive**: $O(n)$ on sorted input, about $n^2/4$ on
  random input, $n(n-1)/2$ only when reversed.
- The two sorts' **loop invariants** differ: selection sort's prefix is
  final, insertion sort's prefix is merely sorted so far.
- A sort is **stable** if equal keys keep their input order — insertion sort
  and merge sort are, selection sort and quicksort are not.
- **Merging** two sorted lists is a linear two-finger walk costing at most
  $n - 1$ comparisons ([22.2](02-merge-quick.md)).
- **Merge sort** is $O(n)$ work per level times $\log n$ levels — so
  $O(n \log n)$ on *every* input, at the cost of an $O(n)$ buffer.
- **Quicksort** partitions around a pivot that lands in its final position,
  sorts in place, and is usually faster — but degrades to $O(n^2)$ on
  extreme pivots, which is what sorted input hands a first-element pivot.
- Randomising the pivot moves the danger from the data to the dice.
- **Binary search** halves the live region each probe: $O(\log n)$, about 20
  probes for a million elements ([22.3](03-searching.md)).
- Its classic bugs are a bug museum: bounds that keep `mid` alive, the wrong
  loop condition, and Java's `(lo + hi) / 2` overflow.
- Sorting first pays for itself only after enough searches — here, from
  about the mid-thirties on.

### Key terms

| Term | What it means |
| --- | --- |
| comparison count | the currency every sort in this chapter spends |
| [loop invariant](../concept-index.md#i) | a promise that holds at the top of every loop pass |
| [stability](../concept-index.md#s) | equal keys come out in their input order |
| adaptive sort | one that does less work when the input is nearly sorted |
| [merge sort](../concept-index.md#m) | split to singletons, then merge back up — always $O(n \log n)$ |
| [quicksort](../concept-index.md#q) | partition around a pivot, then recurse on both sides, in place |
| [pivot](../concept-index.md#p) | the element quicksort partitions around; extremes are the bad case |
| Timsort | Python's real sort: merge sort plus insertion sort on runs, stable |
| [binary search](../concept-index.md#b) | halve a *sorted* region until the target is found or the region empties |
| `bisect` | the standard library's binary search — reports where a value *belongs* |

Now the practice. Work the predictions on paper *before* pressing Run — the
entire value of a comparison-count exercise evaporates if the computer
answers first. The binary search exercise has a special rule: you get one
attempt.

### Exercise 22.1 — Predict the passes ●

This insertion sort prints the list after every pass. Predict all three
printed lines for `[4, 2, 5, 1]`, then run to check.

```python
def insertion_sort_verbose(a):
    for i in range(1, len(a)):
        value = a[i]
        j = i - 1
        while j >= 0 and a[j] > value:
            a[j + 1] = a[j]
            j -= 1
        a[j + 1] = value
        print(f"after pass {i}: {a}")

insertion_sort_verbose([4, 2, 5, 1])
```

??? success "Solution"

    ```python
    def insertion_sort_verbose(a):
        for i in range(1, len(a)):
            value = a[i]
            j = i - 1
            while j >= 0 and a[j] > value:
                a[j + 1] = a[j]
                j -= 1
            a[j + 1] = value
            print(f"after pass {i}: {a}")

    insertion_sort_verbose([4, 2, 5, 1])
    ```

    Prints `[2, 4, 5, 1]`, then `[2, 4, 5, 1]` again, then `[1, 2, 4, 5]`.
    Pass 2 changes nothing — the 5 is already bigger than the 4 to its
    left, one comparison and done — which is adaptivity in miniature. Pass
    3 shows the worst case in miniature: the 1 slides past everyone.

### Exercise 22.2 — Selection sort, sight unseen ●

Without running anything: exactly how many comparisons does selection sort
make on (a) `[1, 2, ..., 10]` sorted, (b) the same ten values reversed,
(c) twenty values in random order? Write your three numbers down, then
verify with the counter from
[section 22.1](01-elementary-sorts.md).

??? success "Solution"

    ```python
    def selection_count(items):
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
        return comparisons

    import random
    random.seed(1)
    print(selection_count(list(range(1, 11))))          # 45
    print(selection_count(list(range(10, 0, -1))))      # 45
    print(selection_count(random.sample(range(20), 20)))  # 190
    ```

    (a) and (b) are both $10 \cdot 9/2 = 45$ — order cannot matter to an
    oblivious algorithm. (c) is $20 \cdot 19/2 = 190$: doubling $n$ took
    the count from 45 to 190, roughly $\times 4$, the quadratic fingerprint.

### Exercise 22.3 — Merge by hand ●●

Merge `[1, 5, 6]` and `[2, 3, 7]` with the two-finger walk. On paper,
write every comparison ("1 vs 2 → take 1", …), the final list, and the
total comparison count. Then instrument `merge` to check both.

??? success "Solution"

    ```python
    def merge_counting(left, right):
        merged = []
        comparisons = 0
        i = j = 0
        while i < len(left) and j < len(right):
            comparisons += 1
            if left[i] <= right[j]:
                merged.append(left[i])
                i += 1
            else:
                merged.append(right[j])
                j += 1
        merged.extend(left[i:])
        merged.extend(right[j:])
        return merged, comparisons

    result, count = merge_counting([1, 5, 6], [2, 3, 7])
    print(result)         # [1, 2, 3, 5, 6, 7]
    print(count)          # 5
    ```

    The walk: 1 vs 2 → take 1; 5 vs 2 → take 2; 5 vs 3 → take 3;
    5 vs 7 → take 5; 6 vs 7 → take 6; left side empty → copy the 7. Five
    comparisons for six elements — the 7 arrives without a fight, which
    is why merging never needs more than $n - 1$ comparisons.

### Exercise 22.4 — Count before the counter ●●

Predict insertion sort's exact comparison count for each input, then
verify: (a) `[1, 2, 3, 4, 5, 6]`, (b) `[6, 5, 4, 3, 2, 1]`,
(c) `[2, 1, 4, 3, 6, 5]`. Hint for the bookkeeping: a pass makes one
comparison per shift, plus one more *unless* the card slid all the way to
the front.

??? success "Solution"

    ```python
    def insertion_count(items):
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
        return comparisons

    print(insertion_count([1, 2, 3, 4, 5, 6]))   # 5
    print(insertion_count([6, 5, 4, 3, 2, 1]))   # 15
    print(insertion_count([2, 1, 4, 3, 6, 5]))   # 7
    ```

    (a) Five passes, one comparison each: 5 — the $O(n)$ best case.
    (b) Pass $i$ slides past $i$ elements and falls off the front:
    $1+2+3+4+5 = 15$, the full $n(n-1)/2$. (c) Passes cost 1, 1, 2, 1, 2:
    each swapped pair charges one extra comparison, so three disorders
    cost only 7 — barely worse than sorted.

### Exercise 22.5 — Binary search, first try ●●

The section claimed most programmers get binary search wrong on the first
attempt. Your turn to beat the odds: write `binary_search(items, target)`
returning an index or −1, from memory, and run it against these asserts
**once**. No peeking at section 22.3, no test-and-tweak — decide every
detail (`<=` or `<`? `mid + 1` or `mid`?) *before* running. If any assert
fires, diagnose which museum exhibit you built before fixing it.

```text
data = [3, 9, 14, 20, 27, 33, 41]
assert binary_search(data, 3) == 0        # first element
assert binary_search(data, 41) == 6       # last element
assert binary_search(data, 20) == 3       # middle
assert binary_search(data, 4) == -1       # absent, interior gap
assert binary_search(data, 50) == -1      # absent, past the end
assert binary_search([], 5) == -1         # empty list
assert binary_search([7], 7) == 0         # singleton, present
assert binary_search([7], 3) == -1        # singleton, absent
print("all eight passed")
```

??? success "Solution"

    ```python
    def binary_search(items, target):
        lo, hi = 0, len(items) - 1
        while lo <= hi:
            mid = (lo + hi) // 2
            if items[mid] == target:
                return mid
            elif items[mid] < target:
                lo = mid + 1
            else:
                hi = mid - 1
        return -1

    data = [3, 9, 14, 20, 27, 33, 41]
    assert binary_search(data, 3) == 0
    assert binary_search(data, 41) == 6
    assert binary_search(data, 20) == 3
    assert binary_search(data, 4) == -1
    assert binary_search(data, 50) == -1
    assert binary_search([], 5) == -1
    assert binary_search([7], 7) == 0
    assert binary_search([7], 3) == -1
    print("all eight passed")
    ```

    The four decisions that had to be right: inclusive bounds
    (`hi = len - 1`), inclusive loop (`lo <= hi`), and both updates
    stepping past `mid` (`mid + 1`, `mid - 1`). The empty-list assert is
    quietly the meanest: it requires the loop condition to be false
    immediately when `hi` starts at −1.

### Exercise 22.6 — Find the *first* occurrence ●●

With duplicates, plain binary search returns *some* matching index — no
promises which. Write `find_first(items, target)` that returns the
**leftmost** match (or −1): on finding a match, remember it, but keep
searching *left*. Test:
`find_first([1, 2, 2, 2, 3, 5, 5, 7], 2)` → 1,
`(..., 5)` → 5, `(..., 4)` → −1.

??? success "Solution"

    ```python
    def find_first(items, target):
        lo, hi = 0, len(items) - 1
        found = -1
        while lo <= hi:
            mid = (lo + hi) // 2
            if items[mid] == target:
                found = mid          # a candidate! but maybe not the first...
                hi = mid - 1         # ...so keep hunting to the LEFT
            elif items[mid] < target:
                lo = mid + 1
            else:
                hi = mid - 1
        return found

    data = [1, 2, 2, 2, 3, 5, 5, 7]
    print(find_first(data, 2))    # 1
    print(find_first(data, 5))    # 5
    print(find_first(data, 4))    # -1

    # cross-check against the standard library:
    import bisect
    i = bisect.bisect_left(data, 2)
    print(i if i < len(data) and data[i] == 2 else -1)   # 1
    ```

    The one-line change from plain binary search: a match no longer ends
    the hunt — it becomes the best-so-far while the region shrinks
    leftward, so the loop stays $O(\log n)$. This is exactly
    `bisect_left`'s contract, as the cross-check confirms.

### Exercise 22.7 — The stability sting ●●

Section 22.1 promised selection sort would airlift an element over its
twin. Catch it: selection-sort the records
`[("Ava", 91), ("Ben", 85), ("Cody", 91), ("Dana", 85), ("Eli", 78)]`
by grade, print the result, and compare with the insertion sort output
from that section. Which tied pair kept its order, which pair flipped —
and which single swap did the damage?

??? success "Solution"

    ```python
    records = [("Ava", 91), ("Ben", 85), ("Cody", 91),
               ("Dana", 85), ("Eli", 78)]

    def selection_sort_by_grade(items):
        a = list(items)
        n = len(a)
        for i in range(n - 1):
            smallest = i
            for j in range(i + 1, n):
                if a[j][1] < a[smallest][1]:
                    smallest = j
            a[i], a[smallest] = a[smallest], a[i]
        return a

    for name, grade in selection_sort_by_grade(records):
        print(grade, name)
    ```

    Output order: Eli 78, Ben 85, Dana 85, **Cody 91, Ava 91**. The 85s
    kept their input order (Ben before Dana), but the 91s flipped. The
    culprit is the very first pass: it swaps Eli (index 4) with Ava
    (index 0), teleporting Ava *behind* Cody. One long-range swap, one
    broken tie — and it's input-dependent, the worst kind of bug: this
    sort keeps ties on some data and breaks them on other data.

### Exercise 22.8 — Defusing the pivot bomb ●●●

Section 22.2's fix for the sorted-input catastrophe was a *random* pivot.
The deterministic alternative used by many libraries is
**median-of-three**: pivot on the median of the first, middle, and last
elements of the range. Add a `"median3"` strategy to the counting
quicksort and, on *sorted* inputs of size 50, 100, and 200, print its
counts beside the `"first"` strategy's. Why does median-of-three make
sorted input a *best* case?

??? success "Solution"

    ```python
    def quicksort_comparisons(items, pivot_strategy):
        a = list(items)
        count = 0

        def choose_pivot(lo, hi):
            if pivot_strategy == "median3":
                mid = (lo + hi) // 2
                three = sorted([(a[lo], lo), (a[mid], mid), (a[hi], hi)])
                k = three[1][1]              # index of the median value
                a[k], a[hi] = a[hi], a[k]
            elif pivot_strategy == "first":
                a[lo], a[hi] = a[hi], a[lo]

        def partition(lo, hi):
            nonlocal count
            choose_pivot(lo, hi)
            pivot = a[hi]
            i = lo - 1
            for j in range(lo, hi):
                count += 1
                if a[j] < pivot:
                    i += 1
                    a[i], a[j] = a[j], a[i]
            a[i + 1], a[hi] = a[hi], a[i + 1]
            return i + 1

        def sort(lo, hi):
            if lo < hi:
                p = partition(lo, hi)
                sort(lo, p - 1)
                sort(p + 1, hi)

        sort(0, len(a) - 1)
        assert a == sorted(items)
        return count

    print(f"{'n':>4} | {'first':>7} | {'median3':>7}")
    for n in [50, 100, 200]:
        data = list(range(n))
        f = quicksort_comparisons(data, "first")
        m = quicksort_comparisons(data, "median3")
        print(f"{n:>4} | {f:>7,} | {m:>7,}")
    ```

    On sorted input the middle element of any range is that range's true
    median — the *perfect* pivot — so every partition splits exactly in
    half and the count stays in the $n \log_2 n$ neighbourhood while the `"first"` column
    explodes as $n(n-1)/2$. The honest caveat: unlike the random pivot,
    median-of-three is deterministic, so specially crafted "median-of-3
    killer" inputs can still force it quadratic; randomness buys immunity
    to *every* fixed input, cleverness only to the common ones.
