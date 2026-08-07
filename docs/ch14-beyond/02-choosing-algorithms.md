# 14.2 Comparing algorithms

Until now, "does it work?" was the only question we asked of a program.
This section asks the second question: "how *well* does it work?" Two
programs can both be correct and differ in speed by a factor of a
thousand — not because one is written in a fancier style, but because
they do fundamentally different amounts of *work*. Learning to see, count,
and measure that work is the skill that separates code that survives
contact with real data from code that melts. It is also the doorway to
everything in Part III.

## One problem, two answers

The problem: given a spelling list of 10,000 words, check whether each
of 1,000 candidate words is on it. Solution A stores the list in a
`list`; solution B pours it into a `set` first. Both are correct. Let us
time them with `time.perf_counter`, the stopwatch of choice — it returns
a high-precision time in seconds, so we subtract two readings:

```python
import time

words = [f"word{i}" for i in range(10_000)]     # the spelling list
word_set = set(words)                           # same words, as a set
targets = [f"word{i}" for i in range(0, 10_000, 10)]   # 1,000 lookups

t0 = time.perf_counter()
found_list = sum(1 for t in targets if t in words)      # scan the list
list_time = time.perf_counter() - t0

t0 = time.perf_counter()
found_set = sum(1 for t in targets if t in word_set)    # hash lookup
set_time = time.perf_counter() - t0

print(f"list: {list_time * 1000:8.2f} ms  ({found_list} found)")
print(f"set:  {set_time * 1000:8.2f} ms  ({found_set} found)")
print(f"the set was roughly {list_time / set_time:.0f}x faster")
```

The exact milliseconds depend on your machine, but the *shape* of the
result never changes: the set wins by a factor in the hundreds. Why?
Each `in words` walks the list until it finds a match — on average
thousands of comparisons per lookup. Each `in word_set` computes the
word's hash and jumps essentially straight to the answer. Same problem,
same result, wildly different work.

## Counting steps instead of milliseconds

Stopwatches are honest but noisy — a busy laptop can double a
measurement. The deeper comparison counts the **steps** an algorithm
takes, which no background process can distort. Here are the two search
strategies from [Chapter 8](../ch08-grids/03-first-algorithms.md),
instrumented to report how many elements they examined:

```python
def linear_steps(items, target):
    """How many elements linear search examines."""
    steps = 0
    for value in items:
        steps += 1
        if value == target:
            return steps
    return steps

def binary_steps(items, target):
    """How many elements binary search examines (items must be sorted)."""
    steps, lo, hi = 0, 0, len(items) - 1
    while lo <= hi:
        steps += 1
        mid = (lo + hi) // 2
        if items[mid] == target:
            return steps
        if items[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return steps

data = list(range(10_000))          # sorted, as binary search requires
for target in [0, 5_000, 9_999]:
    print(f"target {target:>5}: linear {linear_steps(data, target):>5} "
          f"steps, binary {binary_steps(data, target):>2} steps")
```

The output is exact and reproducible:

```text
target     0: linear     1 steps, binary 13 steps
target  5000: linear  5001 steps, binary 13 steps
target  9999: linear 10000 steps, binary 14 steps
```

Linear search's cost depends entirely on where the target sits — 1 step
if you are lucky, 10,000 if you are not. Binary search barely notices:
each step halves the remaining range, so 10,000 items cost at most 14
looks, because $2^{14} = 16384 > 10000$. Halving is the same trick the
set's hash table exploits even more aggressively — and it only works
because the data is *sorted*, a price linear search never has to pay.

```yaml
# widget-config
sliders:
  n: {min: 100, max: 100000, step: 100, default: 10000, label: "items to search"}
```

```python
# widget — n is bound from the slider above
n = int(n)
halvings = 0
remaining = n
while remaining > 0:
    halvings += 1
    remaining //= 2
print(f"searching {n:,} sorted items, worst case:")
print(f"  linear search: {n:,} steps")
print(f"  binary search: {halvings} steps")
```

Drag the slider: multiply the items by a thousand and binary search asks
for about ten more steps. That astonishing flatness is what Part III
will name $O(\log n)$.

## Watch the growth: the doubling experiment

The most useful lab technique in this whole area costs three lines:
**double the input and watch what the time does.** Linear work should
take about twice as long; if it takes four times as long, the algorithm
is doing quadratic work. First, a linear scan:

```python
import time

def total(data):
    result = 0
    for x in data:
        result += x
    return result

previous = None
print(f"{'n':>9} {'time (ms)':>10} {'ratio':>6}")
for n in [50_000, 100_000, 200_000, 400_000]:
    data = list(range(n))
    t0 = time.perf_counter()
    total(data)
    elapsed = time.perf_counter() - t0
    ratio = f"{elapsed / previous:.1f}x" if previous else "-"
    print(f"{n:>9,} {elapsed * 1000:>10.2f} {ratio:>6}")
    previous = elapsed
```

The ratio column hovers around `2.0x` — double the data, double the
time. Now the same experiment on a nested-loop algorithm that compares
every pair of elements:

```python
import time

def has_duplicate(data):
    """Compare every pair — roughly n * n / 2 comparisons."""
    n = len(data)
    for i in range(n):
        for j in range(i + 1, n):
            if data[i] == data[j]:
                return True
    return False

has_duplicate(list(range(500)))        # warm-up, so timings are fair
previous = None
print(f"{'n':>6} {'time (ms)':>10} {'ratio':>6}")
for n in [500, 1_000, 2_000]:
    data = list(range(n))              # no duplicates: the worst case
    t0 = time.perf_counter()
    has_duplicate(data)
    elapsed = time.perf_counter() - t0
    ratio = f"{elapsed / previous:.1f}x" if previous else "-"
    print(f"{n:>6} {elapsed * 1000:>10.2f} {ratio:>6}")
    previous = elapsed
```

This time the ratios land near `4.0x`: doubling the input quadruples the
work, because both loops grow together. The individual timings wobble —
that is measurement noise — but the ratios tell the truth. An algorithm
whose time quadruples on doubling will take a $10\times$ larger input
$100\times$ longer; sizes that finish in a blink today can become an
overnight run.
Notice also that at $n = 500$ the quadratic function looks perfectly
innocent — a couple of milliseconds. Small tests hide growth problems;
doubling exposes them.

## Fast enough beats clever

A confession to balance all this: the list version of the spelling
checker is *fine* if you check ten words once. Readable-but-slower code
that finishes in a millisecond needs no rescue, and rewriting it wastes
the scarcest resource — your time. The professional rules of thumb:

1. **Write the clear version first.** Correct and readable beats fast
   and mysterious.
2. **Measure before optimizing.** Programmers guess wrong about where
   the time goes so reliably that "I profiled it" is the only accepted
   evidence. `time.perf_counter` is the entry-level profiler you now
   own.
3. **When measurement says act, change the algorithm, not the
   spelling.** Swapping a list scan for a set lookup (or linear for
   binary search) yields factors of hundreds; micro-tweaks to the same
   algorithm yield percents.

The doubling experiment is how you *predict* trouble before users find
it: measure at two sizes, look at the ratio, and extrapolate to the size
production will see.

## The doorway to Part III

You now hold the two experimental tools — the stopwatch and the doubling
ratio — but experiments only describe the machine they ran on. The next
part of the handbook builds the theory that predicts these results for
*any* machine: [Chapter 16](../ch16-complexity/index.md) names the
growth patterns you just witnessed ($O(n)$, $O(n^2)$, $O(\log n)$) and
turns today's lab notes into one of the sharpest tools in computer
science.

!!! warning "Common mistakes"

    - **Trusting a single timing.** One run can be doubled by a
      background process. Time the *ratio* across sizes, or repeat runs
      and take the smallest.
    - **Benchmarking toy sizes.** At $n = 100$ everything is instant and
      the quadratic algorithm may even win. Measure at sizes shaped like
      the real problem, or use doubling to reveal the trend.
    - **Binary-searching unsorted data.** The halving logic silently
      returns wrong answers if the list is not sorted — no exception,
      just nonsense. Sorting first costs time too; count it.
    - **Optimizing before measuring.** Rewriting code that was never the
      bottleneck adds bugs and subtracts readability, for nothing.

## Check your understanding

1. A program's running time goes from 80 ms to 320 ms when its input
   doubles. What growth pattern is that, and what would you predict for
   double the input again?

    ??? success "Answer"
        Time quadrupled ($4\times$) on doubling — quadratic growth.
        Doubling again should land near $4 \times 320 = 1280$ ms.

2. Binary search examined at most 14 elements out of 10,000. Roughly
   how many would it examine for 1,000,000 sorted items, and why?

    ??? success "Answer"
        About 20, because each step halves the range and
        $2^{20} = 1048576 > 10^6$. A hundred-fold larger input costs
        about six more steps.

3. Your teammate wants to spend a week making a report generator
   faster. What single question should come first?

    ??? success "Answer"
        "Have we measured where the time actually goes?" Optimization
        starts with evidence — profile or time the parts, find the true
        bottleneck, and only then decide whether a better algorithm (not
        micro-tweaks) can fix it.
