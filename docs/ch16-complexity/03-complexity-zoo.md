# 16.3 The complexity zoo

You have now derived growth families by counting and detected them with a
stopwatch. This section assembles the whole menagerie in one place: the six
families that describe nearly every algorithm in this book, one picture
that shows why the differences dwarf any hardware upgrade, and the honest
fine print — amortized costs and the price tags on Python's own built-in
operations — that turns the table into a practical tool.

## The six families

Each family below is attached to a concrete algorithm you meet in this
book, so the symbols stay anchored to real code:

| Family | Nickname | Doubling $n$ does what? | Example in this book |
| --- | --- | --- | --- |
| $O(1)$ | constant | nothing | dict lookup — [Chapter 14](../ch14-beyond/01-collections-tour.md) |
| $O(\log n)$ | logarithmic | adds one step | binary search — [Chapter 22](../ch22-sorting/03-searching.md) |
| $O(n)$ | linear | doubles the work | linear search — [Chapter 8](../ch08-grids/03-first-algorithms.md) |
| $O(n \log n)$ | linearithmic | a bit more than doubles | merge sort — [Chapter 22](../ch22-sorting/02-merge-quick.md) |
| $O(n^2)$ | quadratic | quadruples the work | selection sort — [Chapter 22](../ch22-sorting/01-elementary-sorts.md) |
| $O(2^n)$ | exponential | **squares** the step count | naive Fibonacci — [Chapter 17](../ch17-recursion/02-classic-recursion.md) |

Read the third column twice — it is the doubling experiment of
[section 16.2](02-timing.md) in reverse, and it is why the gaps between
rows are unbridgeable by faster hardware: a machine 100× faster moves an
$O(2^n)$ algorithm's feasible $n$ up by less than 7.

!!! info "Why the sorting row stops at $O(n \log n)$"
    Merge sort sits in the $O(n \log n)$ row, and from here on this handbook
    treats that as the floor for sorting. The floor is a *theorem*, not a
    habit: any algorithm that learns about its data only by comparing pairs
    of items must make at least about $n \log n$ comparisons in the worst
    case, and [Section 38.1](../ch38-linear-sorting/01-lower-bound.md) proves
    it by counting the leaves of a decision tree.
    [Section 38.2](../ch38-linear-sorting/02-counting-radix-bucket.md) then
    slips out of the theorem the only way anyone can — by sorting without
    comparing.

## One picture, two scales

Plotting all six on ordinary axes is almost comic: $2^n$ leaves the frame
so fast that the others flatten into the floor. The fix is the same log
trick as in section 16.2 — and together the two panels *are* the argument
of this whole chapter:

```python
import numpy as np
import matplotlib.pyplot as plt

n = np.arange(2, 31)
families = {
    "$O(1)$": np.ones_like(n, dtype=float),
    "$O(\\log n)$": np.log2(n),
    "$O(n)$": n.astype(float),
    "$O(n \\log n)$": n * np.log2(n),
    "$O(n^2)$": n.astype(float) ** 2,
    "$O(2^n)$": 2.0 ** n,
}

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
for label, y in families.items():
    ax1.plot(n, y, label=label)
    ax2.semilogy(n, y, label=label)

ax1.set_ylim(0, 200)                     # zoom, or 2^n hides everyone else
ax1.set_title("Linear scale (zoomed to 200 steps)")
ax1.set_ylabel("steps")
ax2.set_title("Log scale — every family visible")
for ax in (ax1, ax2):
    ax.set_xlabel("n")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
fig.tight_layout()
```

- **Left panel (linear scale).** By $n = 14$, $O(2^n)$ has already burst
  through a ceiling that $O(n \log n)$ won't reach until $n$ is in the
  dozens.
- **Right panel (log scale).** Each family settles into its own lane. Equal
  vertical steps mean "×10 more work", so the exponential becomes a
  *straight line upward*, gaining a ×10 every few units of $n$.

Families below $O(n \log n)$ hug the floor so closely they are hard to tell
apart — which matches practice: the great divide is quadratic-and-above
versus everything below.

## How big can $n$ be?

A wonderfully useful back-of-envelope: a modern machine performs on the
order of $10^8$ simple Python-level operations per second. Given a budget
of about one second, how large an input can each family digest? We can ask
by binary-searching the largest $n$ whose step count fits the budget:

```python
import math

budget = 10 ** 8          # simple operations in about one second

def largest_n(cost, hi=10 ** 9):
    lo, best = 1, 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if cost(mid) <= budget:
            best, lo = mid, mid + 1
        else:
            hi = mid - 1
    return best

costs = {
    "O(n)": lambda n: n,
    "O(n log n)": lambda n: n * math.log2(n) if n > 1 else 1,
    "O(n^2)": lambda n: n * n,
    "O(2^n)": lambda n: 2 ** n if n < 100 else float("inf"),
}
for name, cost in costs.items():
    print(f"{name:<10} -> n can be about {largest_n(cost):>13,}")

# O(log n) needs no search: even n = 10**300 costs only ~1,000 steps.
print(f"O(log n)   -> even n = 10**300 costs {math.log2(10 ** 300):,.0f} steps")
```

Rounded to memorable figures:

| Family | Feasible $n$ in ~1 second |
| --- | --- |
| $O(\log n)$ | effectively unlimited |
| $O(n)$ | $\sim 10^8$ (a hundred million) |
| $O(n \log n)$ | a few million |
| $O(n^2)$ | $\sim 10^4$ (ten thousand) |
| $O(2^n)$ | $\sim 26$ |

This table answers real questions instantly:

- **Sorting a million records with an $O(n \log n)$ sort?** Comfortable.
- **A nested-loop comparison over 100,000 records?** That is $10^{10}$ steps
  — minutes, not seconds. Redesign.
- **Anything exponential beyond $n \approx 30$?** Not on any computer that
  will ever be built. The family, not the hardware, is the verdict.

To see the exponential wall from inside, count the calls made by the naive
recursive Fibonacci (you will meet it properly in
[Chapter 17](../ch17-recursion/02-classic-recursion.md)):

```python
calls = 0

def fib(n):
    global calls
    calls += 1
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)

for n in [10, 15, 20, 25]:
    calls = 0
    result = fib(n)
    print(f"fib({n}) = {result:>6,}  took {calls:>8,} calls")
```

Each `+5` in $n$ multiplies the call count by roughly 11. `fib(25)` takes
about a quarter of a million calls; `fib(50)` would take tens of billions.
Same five-line function — the family does the damage.

## Amortized cost: the honest story of `append`

One entry in every cost table needs an asterisk. `list.append` is listed as
$O(1)$, yet a Python list stores its elements in one contiguous block of
memory — and when the block fills, the list must allocate a bigger block and
copy *everything* across, an $O(n)$ event.

So how can `append` be called constant-time? Watch how often that expensive
event actually happens, by probing the list's allocated size as it grows:

```python
import sys

lst = []
last_size = sys.getsizeof(lst)
print(f"len {len(lst):>5}  ->  {last_size:>6} bytes allocated")
for i in range(2_000):
    lst.append(i)
    size = sys.getsizeof(lst)
    if size != last_size:                # a reallocation just happened
        print(f"len {len(lst):>5}  ->  {size:>6} bytes allocated")
        last_size = size
```

The byte counts jump, and the jumps get *rarer* as the list grows — the gaps
between reallocations widen. That is the trick: whenever the block fills, the
list over-allocates **proportionally to its current size**.

Follow the arithmetic for the textbook version of the scheme, which doubles
the capacity each time:

1. Growing from 1 to $n$ by doubling means reallocating at sizes
   $1, 2, 4, \ldots, n/2$.
2. The total number of elements ever copied is therefore
   $1 + 2 + 4 + \cdots + n/2 < n$.
3. So $n$ appends cost $O(n)$ *in total*, which averages to $O(1)$ per
   append.

(CPython's real growth factor is smaller than 2 — roughly 12.5% headroom —
which trades a little more copying for less wasted memory. The principle and
the conclusion are the same.)

This averaged guarantee is called **amortized** $O(1)$: any *individual*
append might trigger an expensive copy, but spread over the whole sequence
of appends the cost per operation is constant. It is a weaker promise than
true $O(1)$ — and for almost every purpose just as good.

## Price tags on the built-ins

You use these operations constantly; now you can read their price tags.
Average-case costs, Python and its Java counterparts side by side:

| Operation | Python | Java | Cost |
| --- | --- | --- | --- |
| Append/add at end | `lst.append(x)` | `list.add(x)` (ArrayList) | $O(1)$ amortized |
| Index access | `lst[i]` | `list.get(i)` | $O(1)$ |
| Insert at front | `lst.insert(0, x)` | `list.add(0, x)` | $O(n)$ — shifts everything |
| Membership in list | `x in lst` | `list.contains(x)` | $O(n)$ — linear search |
| Membership in set | `x in s` | `set.contains(x)` (HashSet) | $O(1)$ average |
| Dict/map lookup | `d[k]`, `k in d` | `map.get(k)`, `containsKey` (HashMap) | $O(1)$ average |
| Dict/map insert | `d[k] = v` | `map.put(k, v)` | $O(1)$ average, amortized |
| Sort | `lst.sort()` | `Collections.sort(list)` | $O(n \log n)$ |

Two rows deserve a highlight:

- **`x in lst` versus `x in s`** — the same one-character expression with a
  factor-of-$n$ difference. The single most profitable optimisation in
  everyday Python is replacing repeated list membership tests with a set,
  exactly as the collections tour in
  [Chapter 14](../ch14-beyond/01-collections-tour.md) promised.
- **`insert(0, x)`** — an $O(n)$ shift hiding inside an innocent-looking
  call, and the seed of many accidental quadratic loops. One awaits you in
  the [exercises](exercises.md).

!!! warning "Common mistakes"

    - **Treating $O(2^n)$ as merely 'slow'.** It is *infeasible*: beyond
      $n \approx 30$-ish no constant factor, compiler, or supercomputer
      rescues it. Quadratic is slow; exponential is a wall.
    - **Forgetting the cost of operations inside a loop.** A single loop
      containing `x in lst` or `lst.insert(0, ...)` is not $O(n)$ — the
      hidden linear operation makes it $O(n^2)$. Count the built-ins'
      price tags, not just the visible loops.
    - **Reading 'amortized $O(1)$' as 'always fast'.** Individual appends
      occasionally pay a full copy. Fine in ordinary code; worth knowing
      about in real-time systems where a rare slow operation matters.
    - **Assuming dict/set lookups are guaranteed $O(1)$.** They are
      *average-case* $O(1)$ (hash collisions can degrade them), which in
      practice is what you will observe — but the table says "average"
      because that is the truth.

## Check your understanding

1. Your $O(n^2)$ routine handles $n = 1{,}000$ in about 0.01 s. Estimate
   the time for $n = 100{,}000$ — and should you ship it?

    ??? success "Answer"

        $n$ grew by $100\times$, so cost grows by roughly
        $100^2 = 10{,}000\times$: about 100 seconds. Ship it only if
        inputs genuinely stay small; otherwise redesign toward
        $O(n \log n)$ — the back-of-envelope table says $10^5$ is well
        past quadratic's comfort zone.

2. Why does the $O(2^n)$ curve appear as a straight line on the log-scale
   panel, and what is its everyday consequence?

    ??? success "Answer"

        On a log axis, equal vertical steps are equal *multiplications*,
        and $2^n$ multiplies by a constant (2) for each unit of $n$ —
        constant multiplicative growth is a straight line. Consequence:
        each single increment of $n$ costs the same *factor*, so feasible
        $n$ tops out around the twenties regardless of hardware.

3. `append` is amortized $O(1)$. If the list instead grew its capacity by
   a *fixed* 100 slots each time it filled, what would $n$ appends cost in
   total?

    ??? success "Answer"

        A reallocation would occur every 100 appends, and each copies the
        whole list: about $100 + 200 + \cdots + n$ elements copied
        $\approx n^2 / 200$ — total $O(n^2)$, i.e. amortized $O(n)$ per
        append. Proportional (multiplicative) growth is what makes the
        total collapse to $O(n)$.

4. A loop runs `if x in seen:` where `seen` is a list, $n$ times. What is
   the loop's overall complexity, and what one-word change fixes it?

    ??? success "Answer"

        Each membership test on a list is $O(n)$, so the loop is
        $O(n^2)$. Make `seen` a **set**: average $O(1)$ membership turns
        the loop into $O(n)$ — same code shape, different price tag.
