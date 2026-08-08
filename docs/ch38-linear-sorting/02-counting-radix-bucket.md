# 38.2 Counting, radix, and bucket sort

[Section 38.1](01-lower-bound.md) proved that no algorithm can sort faster than
$n \log_2 n$ *by comparing elements*, and then pointed at the loophole: don't
compare. Instead, use the key itself to compute where the element belongs. If
you know a key is an integer between 0 and 99, you do not have to *ask* where
it goes — you already know, because 47 belongs in slot 47. That is the entire
idea behind the three algorithms on this page, and it is exactly the idea
behind hash tables: **treat the key as an address**. The algorithms differ only
in what they do when the key is too big to be an address directly.

Nothing here contradicts the previous section. These sorts are simply outside
the model the theorem describes.

The price of leaving that model is that they stop working on arbitrary data:
you cannot counting-sort a list of arbitrary Python objects, or a list of
64-bit integers, or a list of floats without preprocessing. What you gain, when
the keys cooperate, is $O(n)$.

## Counting sort

Suppose you have $n$ items whose keys are integers in the range $0 \dots k-1$.
Counting sort works in three passes, and the middle one is the clever bit.

1. **Count.** Walk the input and tally how many items have each key.
2. **Prefix-sum.** Turn the tallies into *positions*: `count[v]` becomes the
   number of items with key $\le v$, which is exactly one past the last slot
   where a $v$ belongs.
3. **Place.** Walk the input *backwards*, and for each item, decrement its
   key's counter and drop the item at that index.

Trace it on six exam records keyed by score, with $k = 3$ possible scores:

```text
input:   Ana/2  Bo/1  Cy/2  Di/0  Eve/1  Fay/2
counts:  score 0 -> 1,  score 1 -> 2,  score 2 -> 3
prefix:  [1, 3, 6]        "one item scores <= 0, three score <= 1, six score <= 2"
```

The prefix array says: scores of 0 occupy output slots `[0, 1)`, scores of 1
occupy `[1, 3)`, and scores of 2 occupy `[3, 6)`. Every item now knows its
neighbourhood; the counters just walk backwards through it.

```python
records = [("Ana", 2), ("Bo", 1), ("Cy", 2), ("Di", 0), ("Eve", 1), ("Fay", 2)]

def counting_sort(items, k, show=False):
    """Sort (name, key) pairs by key, where 0 <= key < k. Stable."""
    n = len(items)

    count = [0] * k                         # pass 1: tally
    for _, key in items:
        count[key] += 1
    if show:
        print("  counts        :", count)

    for v in range(1, k):                   # pass 2: running total
        count[v] += count[v - 1]
    if show:
        print("  prefix sums   :", count)

    out = [None] * n                        # pass 3: place, backwards
    for i in range(n - 1, -1, -1):
        name, key = items[i]
        count[key] -= 1                     # the slot this item claims
        out[count[key]] = (name, key)
        if show:
            print(f"  place {name:>4}/{key} at index {count[key]}   {out}")
    return out

print("input :", records)
result = counting_sort(records, 3, show=True)
print("output:", result)
print("sorted correctly:", [r[1] for r in result] == sorted(r[1] for r in records))
```

```text
input : [('Ana', 2), ('Bo', 1), ('Cy', 2), ('Di', 0), ('Eve', 1), ('Fay', 2)]
  counts        : [1, 2, 3]
  prefix sums   : [1, 3, 6]
  place  Fay/2 at index 5   [None, None, None, None, None, ('Fay', 2)]
  place  Eve/1 at index 2   [None, None, ('Eve', 1), None, None, ('Fay', 2)]
  place   Di/0 at index 0   [('Di', 0), None, ('Eve', 1), None, None, ('Fay', 2)]
  place   Cy/2 at index 4   [('Di', 0), None, ('Eve', 1), None, ('Cy', 2), ('Fay', 2)]
  place   Bo/1 at index 1   [('Di', 0), ('Bo', 1), ('Eve', 1), None, ('Cy', 2), ('Fay', 2)]
  place  Ana/2 at index 3   [('Di', 0), ('Bo', 1), ('Eve', 1), ('Ana', 2), ('Cy', 2), ('Fay', 2)]
output: [('Di', 0), ('Bo', 1), ('Eve', 1), ('Ana', 2), ('Cy', 2), ('Fay', 2)]
sorted correctly: True
```

Watch the output array fill in from the outside: `Fay` claims slot 5 (the last
slot for score 2), then `Cy` claims slot 4, then `Ana` claims slot 3. Not one
comparison between two records was made anywhere in that trace. The keys did
all the work.

### Why backwards? Because stability

A sort is **stable** if items with equal keys come out in the same relative
order they went in. That matters constantly: sort a table by name, then by
department, and a stable sort leaves each department's names still
alphabetical. An unstable sort scrambles them.

Counting sort is stable *only because of the direction of the third loop*. The
counter for a key points at the **last** free slot for that key. So walking the
input backwards means the last item with a given key claims the last slot, the
second-to-last claims the one before, and so on — the original order survives.

Flip the loop to run forwards and every group comes out reversed. Rather than
take that on trust, run both:

```python
records = [("Ana", 2), ("Bo", 1), ("Cy", 2), ("Di", 0), ("Eve", 1), ("Fay", 2)]

def counting_sort(items, k, backwards=True):
    count = [0] * k
    for _, key in items:
        count[key] += 1
    for v in range(1, k):
        count[v] += count[v - 1]
    out = [None] * len(items)
    order = range(len(items) - 1, -1, -1) if backwards else range(len(items))
    for i in order:
        name, key = items[i]
        count[key] -= 1
        out[count[key]] = (name, key)
    return out

stable = counting_sort(records, 3, backwards=True)
broken = counting_sort(records, 3, backwards=False)

print("input          :", [n for n, _ in records])
print("backwards loop :", [n for n, _ in stable], " <- stable")
print("forwards loop  :", [n for n, _ in broken], " <- same keys, wrong order")

def groups(res):
    out = {}
    for name, key in res:
        out.setdefault(key, []).append(name)
    return out

print("\nscore -> names, in the original input:", groups(records))
print("after the stable sort               :", groups(stable))
print("after the forwards (unstable) sort  :", groups(broken))
print("\nboth are correctly sorted by key:",
      [k for _, k in stable] == [k for _, k in broken] == [0, 1, 1, 2, 2, 2])
```

```text
input          : ['Ana', 'Bo', 'Cy', 'Di', 'Eve', 'Fay']
backwards loop : ['Di', 'Bo', 'Eve', 'Ana', 'Cy', 'Fay']  <- stable
forwards loop  : ['Di', 'Eve', 'Bo', 'Fay', 'Cy', 'Ana']  <- same keys, wrong order

score -> names, in the original input: {2: ['Ana', 'Cy', 'Fay'], 1: ['Bo', 'Eve'], 0: ['Di']}
after the stable sort               : {0: ['Di'], 1: ['Bo', 'Eve'], 2: ['Ana', 'Cy', 'Fay']}
after the forwards (unstable) sort  : {0: ['Di'], 1: ['Eve', 'Bo'], 2: ['Fay', 'Cy', 'Ana']}

both are correctly sorted by key: True
```

Both outputs are perfectly sorted by key — `0, 1, 1, 2, 2, 2` in each case — so
a test that only checks the keys will pass on the broken version.

The bug shows up only in the *names*: `Ana, Cy, Fay` came in in that order and
came out as `Fay, Cy, Ana`. Hold on to that; the next algorithm's correctness
depends entirely on it.

### The cost, honestly

Counting sort makes three passes: $O(n)$ to tally, $O(k)$ to prefix-sum, $O(n)$
to place. So the cost is

$$
O(n + k)
$$

in both time and space, where **$k$ is the size of the key range, not the number
of distinct keys present**. That distinction is the whole story:

- **A million records keyed by a score from 0 to 100** — $k = 101$, and the
  algorithm is a dream.
- **A million arbitrary 32-bit integers** — $k = 2^{32}$, and it is a disaster.

The arithmetic:

```python
n = 1_000_000
k = 2 ** 32                                # every possible 32-bit integer

print(f"records to sort        : {n:>20,}")
print(f"key range k            : {k:>20,}")
print(f"counters needed        : {k:>20,}")
print(f"as a C array of int32  : {k * 4 / 1024**3:>17.1f} GB")
print(f"as a Python list       : {k * 8 / 1024**3:>17.1f} GB (pointers alone)")
print(f"k / n ratio            : {k / n:>20,.0f}x")

print("\nwhen is counting sort worth it?")
print(f"{'k':>15}{'n + k':>16}{'n log2 n':>14}{'verdict':>18}")
import math
for k_try in (100, 10_000, 1_000_000, 100_000_000, 2 ** 32):
    linear = n + k_try
    comparison = n * math.log2(n)
    verdict = "counting sort" if linear < comparison else "use sorted()"
    print(f"{k_try:>15,}{linear:>16,.0f}{comparison:>14,.0f}{verdict:>18}")
```

```text
records to sort        :            1,000,000
key range k            :        4,294,967,296
counters needed        :        4,294,967,296
as a C array of int32  :              16.0 GB
as a Python list       :              32.0 GB (pointers alone)
k / n ratio            :                4,295x

when is counting sort worth it?
              k           n + k      n log2 n           verdict
            100       1,000,100    19,931,569     counting sort
         10,000       1,010,000    19,931,569     counting sort
      1,000,000       2,000,000    19,931,569     counting sort
    100,000,000     101,000,000    19,931,569      use sorted()
  4,294,967,296   4,295,967,296    19,931,569      use sorted()
```

Sixteen gigabytes of counters to sort a million numbers, most of them zero. The
rule of thumb falls out of the table: **counting sort wins when $k$ is
comparable to $n$**, roughly $k = O(n \log n)$, and becomes absurd beyond that.
Radix sort exists precisely to rescue the cases where it does not.

## Radix sort: sort by one digit at a time

If the key range is too big for one counting sort, chop the key into digits and
counting-sort by each digit separately. A 32-bit integer has four base-256
digits, so instead of one pass over a 4-billion-entry table, you make four
passes over a 256-entry table.

**LSD radix sort** ("least significant digit") sorts by the ones digit first,
then the tens, then the hundreds. That ordering feels backwards the first time
you see it — surely the most significant digit matters most?

The reason it works is the stability we just demonstrated. When the tens-digit
pass runs, the array is already sorted by ones; a *stable* sort by tens
preserves that order within each group of equal tens digits, so after the pass
the array is sorted by the last two digits. Induction does the rest.

```python
def radix_sort(values, base=10, show=False):
    """LSD radix sort using a stable counting sort per digit."""
    a = list(values)
    if not a:
        return a
    largest = max(a)
    place, pass_no = 1, 1

    while largest // place > 0:
        count = [0] * base                            # counting sort on one digit
        for x in a:
            count[(x // place) % base] += 1
        for d in range(1, base):
            count[d] += count[d - 1]
        out = [0] * len(a)
        for i in range(len(a) - 1, -1, -1):            # backwards: STABLE
            digit = (a[i] // place) % base
            count[digit] -= 1
            out[count[digit]] = a[i]
        a = out
        if show:
            print(f"  pass {pass_no} (digit worth {place:>3}): {a}")
        place *= base
        pass_no += 1
    return a

data = [170, 45, 75, 90, 802, 24, 2, 66]
print("input :", data)
result = radix_sort(data, base=10, show=True)
print("output:", result)
print("matches sorted():", result == sorted(data))
```

```text
input : [170, 45, 75, 90, 802, 24, 2, 66]
  pass 1 (digit worth   1): [170, 90, 802, 2, 24, 45, 75, 66]
  pass 2 (digit worth  10): [802, 2, 24, 45, 66, 170, 75, 90]
  pass 3 (digit worth 100): [2, 24, 45, 66, 75, 90, 170, 802]
output: [2, 24, 45, 66, 75, 90, 170, 802]
matches sorted(): True
```

This is the moment the algorithm earns its reputation. After pass 1 the list
looks like noise. After pass 2 it looks *worse* — 802 is at the front, 170 is
in the middle. After pass 3 it is perfectly sorted, and no comparison was ever
made.

Look carefully at pass 2 to see stability doing its job: `2` and `802` both
have tens digit 0, and `2` came after `802` in the pass-1 output, so it stays
after `802`. The hundreds pass then separates them correctly.

### The cost, and choosing the base

The cost is $d$ counting sorts, each $O(n + b)$, where $b$ is the base and $d$
is the number of digits:

$$
O\bigl(d\,(n + b)\bigr)
$$

For 32-bit integers with $b = 256$, that is $4(n + 256)$ — linear in $n$ with a
constant of about 4. Choosing the base is a real trade: a bigger base means
fewer passes but a bigger counter array.

### Break the stability, break the sort

The claim "each pass must be stable" is easy to state and easy to doubt. Here
is the same algorithm with one pass made unstable — the elements within each
digit bucket are reversed — and nothing else changed:

```python
def radix_sort_stable(values, base=10):
    a = list(values)
    place = 1
    while max(a) // place > 0:
        buckets = [[] for _ in range(base)]
        for x in a:
            buckets[(x // place) % base].append(x)
        a = [x for b in buckets for x in b]            # keeps arrival order
        place *= base
    return a

def radix_sort_unstable(values, base=10):
    a = list(values)
    place = 1
    while max(a) // place > 0:
        buckets = [[] for _ in range(base)]
        for x in a:
            buckets[(x // place) % base].append(x)
        a = [x for b in buckets for x in reversed(b)]  # <- stability broken
        place *= base
    return a

data = [170, 45, 75, 90, 802, 24, 2, 66]
good = radix_sort_stable(data)
bad = radix_sort_unstable(data)

print("stable buckets  :", good, " correct:", good == sorted(data))
print("reversed buckets:", bad, " correct:", bad == sorted(data))
print("expected        :", sorted(data))
```

```text
stable buckets  : [2, 24, 45, 66, 75, 90, 170, 802]  correct: True
reversed buckets: [90, 75, 66, 45, 24, 2, 170, 802]  correct: False
expected        : [2, 24, 45, 66, 75, 90, 170, 802]
```

The unstable version is not slightly wrong; it is nonsense. Its output is not
even close to sorted. Every earlier pass's work is destroyed by the next one,
because the whole algorithm rests on "the previous passes' order survives".

!!! note "Stability is load-bearing"

    In counting sort, stability is a useful property. In radix sort it is a
    **correctness requirement**: break it in any single pass and the algorithm
    stops sorting at all.

## Bucket sort

Radix sort handles integers. **Bucket sort** handles values spread over a
continuous range, in three steps:

1. **Scatter** the values into $n$ buckets, by value.
2. **Sort each bucket** with any convenient algorithm.
3. **Concatenate** the buckets in order.

If the values are spread evenly, each bucket holds about one item, the little
sorts cost almost nothing, and the total is $O(n)$.

"If the values are spread evenly" is the entire catch.

```python
import random

def bucket_sort(values, n_buckets=None):
    """Sort floats in [0, 1). Returns (sorted, comparisons, biggest bucket)."""
    n = len(values)
    n_buckets = n_buckets or n
    buckets = [[] for _ in range(n_buckets)]
    for x in values:
        buckets[min(int(x * n_buckets), n_buckets - 1)].append(x)

    comparisons = 0
    out = []
    for b in buckets:
        for i in range(1, len(b)):                 # insertion sort in-bucket
            j = i
            while j > 0:
                comparisons += 1
                if b[j] >= b[j - 1]:
                    break
                b[j - 1], b[j] = b[j], b[j - 1]
                j -= 1
        out.extend(b)
    return out, comparisons, max(len(b) for b in buckets)

rng = random.Random(38)
n = 2000
uniform = [rng.random() for _ in range(n)]
skewed = [rng.random() ** 8 for _ in range(n)]     # crowds everything near 0

print(f"{'distribution':<18}{'comparisons':>13}{'biggest bucket':>16}{'correct':>9}")
for name, data in (("uniform", uniform), ("skewed (x**8)", skewed)):
    out, comps, biggest = bucket_sort(data)
    print(f"{name:<18}{comps:>13,}{biggest:>16,}{str(out == sorted(data)):>9}")

print(f"\nfor reference, insertion sort on all {n} would cost about "
      f"{n * n // 4:,} comparisons")
```

```text
distribution        comparisons  biggest bucket  correct
uniform                     920               7     True
skewed (x**8)           150,299             766     True

for reference, insertion sort on all 2000 would cost about 1,000,000 comparisons
```

On uniform data, 2,000 values cost 920 comparisons — under half a comparison
per element, and the biggest bucket held 7 items. On the skewed data the same
code cost 150,299 comparisons, because one bucket swallowed 766 values and had
to be insertion-sorted at $O(m^2)$. **That is a 163-fold difference from
changing nothing but the input distribution.**

In the true worst case — every value in one bucket — bucket sort degrades to
whatever you used inside the buckets: $O(n^2)$ with insertion sort, or
$O(n \log n)$ if you use `sorted()` there instead, which is what a careful
implementation does.

Bucket sort is the only algorithm on this page whose performance depends on the
*distribution* of the data rather than its type.

## Which sort, when

| Algorithm | Time | Extra space | Stable | Needs | Use when |
|---|---|---|---|---|---|
| Counting sort | $O(n + k)$ | $O(n + k)$ | yes | integer keys in $[0, k)$ | $k$ is comparable to $n$ — ages, scores, byte values, ratings |
| Radix sort (LSD) | $O(d(n + b))$ | $O(n + b)$ | yes | fixed-width integer or string keys | large integer ranges, fixed-length strings, IP addresses |
| Bucket sort | $O(n)$ average, $O(n^2)$ worst | $O(n)$ | depends on inner sort | numeric keys **and** a roughly uniform distribution | sensor readings, random floats, hash values |
| Merge sort | $O(n \log n)$ | $O(n)$ | yes | any orderable type | you need a guaranteed bound and stability |
| Timsort (`sorted()`) | $O(n \log n)$, often much better | $O(n)$ | yes | any orderable type | almost always — see below |

The honest decision procedure is three questions, in this order:

1. **Are the keys small non-negative integers?** If not, none of these apply.
2. **Is the key range within a small multiple of $n$?** If yes, counting sort;
   if no, radix.
3. **Is this actually the bottleneck?** Usually not.

## Head to head: radix versus `sorted()`

Asymptotics say radix sort is $O(n)$ and Timsort is $O(n \log n)$, so radix
should win. Measure it.

```python
import random
import time

def radix_sort(values, base=256):
    a = list(values)
    place = 1
    largest = max(a)
    while largest // place > 0:
        count = [0] * base
        for x in a:
            count[(x // place) % base] += 1
        for d in range(1, base):
            count[d] += count[d - 1]
        out = [0] * len(a)
        for i in range(len(a) - 1, -1, -1):
            digit = (a[i] // place) % base
            count[digit] -= 1
            out[count[digit]] = a[i]
        a = out
        place *= base
    return a

def counting_sort(values, k):
    count = [0] * k
    for x in values:
        count[x] += 1
    out = []
    for v, c in enumerate(count):
        out.extend([v] * c)
    return out

rng = random.Random(38)
n, k = 100_000, 10_000
data = [rng.randrange(k) for _ in range(n)]

results = {}
for name, fn in (("radix sort (base 256, 2 passes)", lambda: radix_sort(data)),
                 ("counting sort (k = 10,000)", lambda: counting_sort(data, k)),
                 ("sorted()  — Timsort in C", lambda: sorted(data))):
    t0 = time.perf_counter()
    out = fn()
    elapsed = time.perf_counter() - t0
    results[name] = elapsed
    assert out == sorted(data)
    print(f"{name:<34}{elapsed * 1000:>8.1f} ms  "
          f"({elapsed / n * 1e9:>5.0f} ns per element)")

fastest = min(results, key=results.get)
print(f"\nfastest here: {fastest}")
for name, t in results.items():
    print(f"  {name:<34}{t / results[fastest]:>6.1f}x the fastest")
```

Run it on your own machine; the exact milliseconds depend on your hardware and
Python build, which is why the block prints a ranking rather than asking you to
trust a number in the text. The pattern, however, is reliable, and it is not
the one the asymptotics predict.

**The $O(n)$ radix sort usually loses to the $O(n \log n)$ `sorted()`.** That
looks impossible until you count what each one actually executes. `sorted()` is
CPython's Timsort, written in C and tuned for two decades; the radix sort above
is a Python `for` loop, and every iteration of a Python loop costs tens of
nanoseconds of interpreter overhead before it does any real work.

A constant factor of 50–100× between interpreted and compiled inner loops is
completely normal, and $\log_2(100{,}000) \approx 17$ is a far smaller factor
than that. Asymptotically radix wins; at $n = 100{,}000$, in this language, the
constant swamps the logarithm.

**Constant factors hide inside Big-O.** Radix sort with base 256 makes two full
passes over the data, and each pass runs two Python-level loops over all
100,000 elements plus modular arithmetic per element. "Linear" describes how
the cost *grows*, not how big it is.

**The counting-sort row is the interesting one.** It usually places well, often
ahead of `sorted()`, because it touches each element in Python exactly once
(the tally loop) and then builds the whole output with `extend`, which runs at
C speed.

But read its code again: it reconstructs the values from the counts, which only
works because the elements *are* their own keys. Give the records any satellite
data — names, rows, objects — and it needs the full placement loop from earlier
on this page, which is another $n$ Python iterations, and the advantage largely
evaporates.

None of this makes the asymptotic analysis wrong. It makes it *incomplete*,
exactly as [section 16.2](../ch16-complexity/02-timing.md) warned. Big-O tells
you which algorithm wins *eventually*; only a stopwatch tells you whether
"eventually" has arrived at your value of $n$, in your language, on your
machine.

!!! tip "When the linear sorts genuinely win"

    Push $n$ far higher and shrink $k$ and the picture flips: counting sort on
    a hundred million bytes is a single pass over a 256-entry array and nothing
    beats it. The real wins in practice come from three situations: (1) the
    keys are bytes or small integers and $n$ is huge; (2) the sort is written
    in a compiled language, where radix sort's flat memory access pattern is
    very cache-friendly; (3) the data lives outside memory, where radix's
    predictable sequential passes beat a comparison sort's random access.
    Database engines and GPU sort libraries use radix sort heavily for exactly
    these reasons.

!!! warning "Common mistakes"

    - **Forgetting that $k$ is the key *range*.** `counting_sort(data, k=max(data)+1)`
      on data containing one value of 10 million allocates 10 million counters
      to sort ten items. Check the range before choosing the algorithm.
    - **Negative keys.** Counting and radix sort index an array with the key, and
      `count[-3]` silently wraps around to the end of the list in Python — no
      error, wrong answer. Shift by subtracting the minimum first, and remember
      to shift back.
    - **Iterating forwards in the placement loop.** It still produces a
      key-sorted result, so unit tests that only check the keys pass. It
      destroys stability, and it destroys radix sort completely.
    - **MSD instead of LSD without extra machinery.** Sorting by the most
      significant digit first requires recursively sorting each bucket
      separately. It works, but it is a different (and more complex)
      algorithm; the simple loop-over-digits version must go least significant
      first.
    - **Bucket sort on skewed data.** Prices, populations, word frequencies and
      file sizes are all famously non-uniform. Without a transformation that
      spreads them out, bucket sort degrades to the sort you used inside the
      buckets.
    - **Reaching for these first.** In Python, `sorted()` is the right answer
      almost always. Use a linear-time sort when you have measured a bottleneck
      *and* your keys have the structure to exploit.

## Check your understanding

1. Counting sort's prefix array for keys `[3, 1, 3, 0, 1, 3]` with $k = 4$ is
   `[1, 3, 3, 6]`. What does the repeated 3 mean?

    ??? success "Answer"
        `count[2] == count[1] == 3` means "three items have a key $\le 1$" and
        "three items have a key $\le 2$" — so **no item has key 2**. The empty
        range `[3, 3)` reserves zero slots for key 2, which is exactly right.
        Repeats in the prefix array mark absent keys.

2. You need to sort 10 million records by a `country_code` field that is an
   integer from 0 to 999. Which algorithm, and roughly how much extra memory?

    ??? success "Answer"
        Counting sort: $k = 1000$ is tiny next to $n = 10^7$, giving
        $O(n + k) \approx O(n)$. The extra memory is the 1,000 counters (a few
        kilobytes) plus the output array of $n$ items — and that output array,
        not the counters, is the real memory cost. Stability comes free, which
        matters if the records were already sorted by something else.

3. Radix sort on 32-bit integers can use base 16 (8 passes over 16 counters) or
   base 65536 (2 passes over 65,536 counters). Which is faster, and what is the
   trade?

    ??? success "Answer"
        Base 65536 does a quarter of the passes, so it moves the data 2 times
        instead of 8 — usually much faster. The cost is a counter array of
        65,536 entries per pass instead of 16, which is still small in absolute
        terms but no longer fits in fast cache. The usual sweet spot is base
        256 (4 passes, 256 counters, comfortably cache-resident), which is why
        real implementations almost always process one byte at a time.

4. Why is bucket sort the only algorithm on this page whose cost depends on the
   data's *distribution* rather than just its type and size?

    ??? success "Answer"
        Because it is the only one that puts a *variable* number of items in
        each slot and then sorts within slots. Counting sort's slots hold
        exactly the items with that key and are never sorted; radix sort's
        passes are fixed in number regardless of the values. Bucket sort's
        promise is "about one item per bucket", and that promise is a statement
        about the distribution, not about the algorithm.

5. `sorted()` beat a hand-written radix sort in the timing block above. Does
   that mean the $O(n)$ analysis was wrong?

    ??? success "Answer"
        No — it means the analysis was about growth, not about the constant in
        front. Radix sort really does scale linearly, while `sorted()` scales
        as $n \log n$; the crossover simply sits at a value of $n$ far beyond
        100,000 *when one is C and the other is interpreted Python*. Write both
        in the same language and the crossover moves down dramatically. Big-O
        answers "which wins as $n \to \infty$"; only measurement answers "which
        wins at my $n$, on my machine, in my language".
