# 8.3 First algorithms — sort and search

An **algorithm** is a precise, step-by-step recipe for solving a
problem — precise enough that a machine can follow it and you can
*prove things* about it. This section presents your first two: linear
search ("is this value here, and where?") and selection sort ("arrange
these values in order").

Both are built entirely from Chapter 7's traversal patterns, and both can be
traced by hand on paper. Both also teach the habit that separates programmers
from great programmers: asking *how many steps does this take as the data
grows?*

## Linear search

The problem: given a list and a target value, report the *index* where
the target first appears — or report that it is absent. The recipe
could not be plainer: check each element from the front, and stop the
moment you find it.

```python
def linear_search(values, target):
    """Return the index of the first occurrence of target, or -1."""
    for i in range(len(values)):
        if values[i] == target:
            return i          # found: stop instantly
    return -1                 # the loop finished without finding it

data = [12, 5, 8, 5, 9]
print(linear_search(data, 8))
print(linear_search(data, 5))
print(linear_search(data, 7))
```

```text
2
1
-1
```

Hand-trace the successful search for `8`:

| step | `i` | `values[i]` | equal to 8? | action |
|---|---|---|---|---|
| 1 | 0 | 12 | no | keep going |
| 2 | 1 | 5 | no | keep going |
| 3 | 2 | 8 | **yes** | `return 2` |

And the failed search for `7`: every one of the five comparisons says
"no", the loop runs out of elements, and control falls through to
`return -1`. That placement is the subtle part — `return -1` sits
*after* the loop, so it runs only when the entire list has been
checked. Beginners often try to return `-1` inside the loop's `else`
branch, which wrongly gives up after the very first mismatch.

Note also that searching for `5` returned `1`, not `3`: the recipe
stops at the *first* occurrence.

### What should "not found" look like?

Three designs are all in common use:

- **Return `-1`** — an impossible index. This is the Java convention, and
  exactly what Java's own `String.indexOf` does.
- **Return `None`** — often preferred in Python, because it reads clearly at
  the call site: `if result is None:`.
- **Raise an error** — what Python's own `list.index` method does.

All three work. What matters is that a "not found" answer can never be
confused with a real index, and that your docstring says which convention you
chose.

### How many steps?

In the worst case (target absent, or hiding in the
last slot) linear search makes $n$ comparisons on an $n$-element list.
Double the data, double the work — growth is proportional to $n$, and
you cannot do better without extra knowledge about the list (a preview
of binary search in [Chapter 22](../ch22-sorting/03-searching.md),
which exploits *sorted* data).

## Selection sort

Sorting — rearranging a list into increasing order — is the classic
first "real" algorithm. **Selection sort** repeats one simple move:
*find the smallest element in the unsorted part, and swap it to the
front of that part.*

The algorithm's promise after each pass is called an **invariant** — a
statement that is true every time you check it: after pass $i$, **the
first $i+1$ positions hold the smallest $i+1$ values, in their final
sorted order, forever.** The sorted region grows from the left, one
guaranteed-correct element per pass; the algorithm never revisits it.

```python
def selection_sort(values):
    """Sort the list in place, smallest first. Returns None."""
    n = len(values)
    for i in range(n - 1):            # i = boundary of the sorted part
        min_i = i                     # running champion: smallest so far
        for j in range(i + 1, n):     # scan the unsorted part
            if values[j] < values[min_i]:
                min_i = j
        values[i], values[min_i] = values[min_i], values[i]   # swap in

data = [29, 10, 14, 37, 13]
selection_sort(data)
print(data)
```

This prints `[10, 13, 14, 29, 37]`. The inner loop is exactly
Chapter 7's search-for-best pattern (tracking the champion's *index*),
and the swap is Section 8.2's helper inlined. Here is the full trace on
`[29, 10, 14, 37, 13]`:

| pass | list before pass | smallest in unsorted part | swap | list after pass |
|---|---|---|---|---|
| $i=0$ | [29, 10, 14, 37, 13] | 10 (index 1) | swap 29, 10 | [**10**, 29, 14, 37, 13] |
| $i=1$ | [**10**, 29, 14, 37, 13] | 13 (index 4) | swap 29, 13 | [**10, 13**, 14, 37, 29] |
| $i=2$ | [**10, 13**, 14, 37, 29] | 14 (index 2) | swap 14, 14 (stays) | [**10, 13, 14**, 37, 29] |
| $i=3$ | [**10, 13, 14**, 37, 29] | 29 (index 4) | swap 37, 29 | [**10, 13, 14, 29**, 37] |

Bold marks the sorted region growing left to right — the invariant made
visible. After pass $i=3$ only one element remains unsorted, and a
single leftover element is necessarily in the right place, which is why
the outer loop runs to $n-1$, not $n$.

### Counting the steps

How much work is that? Pass 0 scans $n-1$ elements, pass 1 scans
$n-2$, and so on down to 1. The total number of comparisons is

$$ (n-1) + (n-2) + \dots + 1 \;=\; \frac{n(n-1)}{2}, $$

which grows like $n^2$: double the list, roughly *quadruple* the work.
Don't take the formula on faith — instrument the code and count:

```python
def selection_sort_counting(values):
    """Sort in place and return the number of comparisons made."""
    comparisons = 0
    n = len(values)
    for i in range(n - 1):
        min_i = i
        for j in range(i + 1, n):
            comparisons += 1
            if values[j] < values[min_i]:
                min_i = j
        values[i], values[min_i] = values[min_i], values[i]
    return comparisons

import random
random.seed(3)                       # reproducible shuffles
for n in [5, 10, 20, 40]:
    data = random.sample(range(1000), n)
    made = selection_sort_counting(data)
    print(f"n = {n:>2}: {made:>3} comparisons   (n(n-1)/2 = {n*(n-1)//2})")
```

```text
n =  5:  10 comparisons   (n(n-1)/2 = 10)
n = 10:  45 comparisons   (n(n-1)/2 = 45)
n = 20: 190 comparisons   (n(n-1)/2 = 190)
n = 40: 780 comparisons   (n(n-1)/2 = 780)
```

The count matches the formula exactly — selection sort always makes
every comparison, sorted input or not — and each doubling of $n$
roughly quadruples the count ($45 \to 190 \to 780$). This
growth-rate way of judging algorithms has a name, *Big-O*, and
selection sort is our first citizen of class $O(n^2)$. Chapter 16
develops the idea properly — see
[Big-O notation](../ch16-complexity/01-big-o.md).

```yaml
# widget-config
sliders:
  n: {min: 2, max: 500, step: 1, default: 10, label: "list length n"}
```

```python
# widget — n is bound from the slider above
n = int(n)
print(f"Selection sort on {n} elements always makes")
print(f"{n * (n - 1) // 2} comparisons.")
```

Drag the slider and watch the count race ahead of $n$: at $n = 100$
the sort is already making 4,950 comparisons; at $n = 500$, 124,750.

## Insertion sort, briefly

Selection sort has a sibling you should recognise on sight.
**Insertion sort** keeps the left part sorted too, but grows it
differently: take the next element and *slide it left* into its proper
place, shifting bigger elements right to make room — the way most
people sort playing cards in hand.

```python
def insertion_sort(values):
    """Sort the list in place, smallest first. Returns None."""
    for i in range(1, len(values)):
        current = values[i]           # the card just picked up
        j = i - 1
        while j >= 0 and values[j] > current:
            values[j + 1] = values[j] # shift a bigger element right
            j -= 1
        values[j + 1] = current       # drop the card into the gap

data = [29, 10, 14, 37, 13]
insertion_sort(data)
print(data)
```

This prints `[10, 13, 14, 29, 37]` — same result, different route. In
the worst case insertion sort is $O(n^2)$, just like selection sort.

Its special talent is *nearly sorted* input. An element already in place
costs just one comparison and zero shifts, so on almost-sorted data insertion
sort finishes in nearly linear time — while selection sort grinds through its
full $n(n-1)/2$ regardless:

```python
def insertion_sort_counting(values):
    shifts = 0
    for i in range(1, len(values)):
        current = values[i]
        j = i - 1
        while j >= 0 and values[j] > current:
            values[j + 1] = values[j]
            shifts += 1
            j -= 1
        values[j + 1] = current
    return shifts

nearly  = [1, 2, 4, 3, 5, 6, 7, 8]       # one pair out of order
reverse = [8, 7, 6, 5, 4, 3, 2, 1]       # worst case
print("nearly sorted :", insertion_sort_counting(nearly), "shifts")
print("reverse sorted:", insertion_sort_counting(reverse), "shifts")
```

```text
nearly sorted : 1 shifts
reverse sorted: 28 shifts
```

One shift versus twenty-eight, on lists of the same length. The two siblings
side by side:

| | Selection sort | Insertion sort |
| --- | --- | --- |
| How the sorted region grows | find the smallest remaining value, swap it to the front | slide the next value left until it lands in place |
| Worst case | $O(n^2)$ | $O(n^2)$ |
| Nearly sorted input | no help at all — still the full $n(n-1)/2$ comparisons | nearly linear: one comparison and no shifts per settled element |

*Which* sort wins depends on the data — your first taste of a theme that runs
through all of computer science.

## What you actually call

Real programs almost never hand-roll sorts. Both languages ship
industrial-strength sorting that is faster than anything in this
section — roughly $O(n \log n)$, provably better than $O(n^2)$:

```python
data = [29, 10, 14, 37, 13]

print(sorted(data))     # returns a NEW sorted list...
print(data)             # ...leaving the original alone

data.sort(reverse=True) # sorts IN PLACE (and returns None)
print(data)
```

```text
[10, 13, 14, 29, 37]
[29, 10, 14, 37, 13]
[37, 29, 14, 13, 10]
```

`sorted()` and `list.sort()` are the return-new / mutate-in-place pair
from [Section 8.2](02-arrays-functions.md), living side by side in the
standard library. Java's equivalent is `java.util.Arrays.sort(values)`,
which sorts the array in place:

```java
int[] data = {29, 10, 14, 37, 13};
java.util.Arrays.sort(data);           // in place, like list.sort()
System.out.println(java.util.Arrays.toString(data));
// [10, 13, 14, 29, 37]
```

So why learn selection sort at all? Because library sorts are *made of*
these ideas — invariants, swaps, comparisons, step counts — and because
"implement and trace a simple sort" is the standard proving ground for
algorithmic thinking (and a perennial exam and interview question).
Chapter 22 opens the hood on the
[fast sorts](../ch22-sorting/02-merge-quick.md).

!!! warning "Common mistakes"
    - **`data = data.sort()`.** `sort()` mutates and returns `None`, so
      this line sorts the list and then throws it away. Either
      `data.sort()` alone, or `data = sorted(data)`.
    - **Returning `-1` (or `None`) from inside the search loop.** The
      "not found" return belongs *after* the loop; inside an
      `else`, it reports failure after checking only the first element.
    - **Swapping values instead of tracking the index.** In selection
      sort's inner loop, only `min_i` moves. The swap happens once per
      outer pass; swapping every time you see a smaller element turns
      it into a different (and slower-to-reason-about) algorithm.
    - **Off-by-one in the outer loop.** `range(n - 1)` is correct: when
      $n-1$ elements are placed, the last one is automatically right.
      Running to `range(n)` does a harmless-but-wasteful extra pass;
      stopping at `range(n - 2)` leaves the last pair unsorted.

## Check your understanding

1. `linear_search([4, 4, 4], 4)` returns what? And
   `linear_search([], 9)`?

    ??? success "Answer"
        `0` — the *first* match wins, and index 0 matches immediately.
        On the empty list the loop body never runs, so it returns `-1`
        straight away: the empty list is handled correctly for free.

2. After two full passes of selection sort ($i = 0$ and $i = 1$) on a
   6-element list, exactly what does the invariant guarantee?

    ??? success "Answer"
        The first two positions hold the two smallest values of the
        whole list, in sorted order, and they will never move again.
        The remaining four positions hold the other four values in some
        unknown order.

3. How many comparisons does selection sort make on a 6-element list
   that is *already sorted*?

    ??? success "Answer"
        $6 \times 5 / 2 = 15$ — the same as for any 6-element list.
        Selection sort cannot notice sortedness; it must scan the whole
        unsorted region every pass. (Insertion sort on the same input
        makes just 5 comparisons and 0 shifts — that is its superpower.)

4. Your program needs `data` sorted but also needs the original order
   later. Which library call do you use?

    ??? success "Answer"
        `ordered = sorted(data)` — it returns a new sorted list and
        leaves `data` untouched. `data.sort()` would destroy the
        original order (and return `None`).
