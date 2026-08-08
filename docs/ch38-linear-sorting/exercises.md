# Chapter 38 · Exercises

## The chapter in brief

- A **comparison sort** is one whose only question about the data is "is $a$
  less than $b$?" — which is exactly what makes `sorted()` work on any
  orderable type ([38.1](01-lower-bound.md)).
- Any such algorithm *is* a **decision tree**: comparisons at the internal
  nodes, one leaf per complete run.
- The tree needs at least $n!$ leaves and a binary tree of height $h$ has at
  most $2^h$, so $h \ge \log_2(n!)$ — the whole proof, done by counting.
- **Stirling's approximation** turns that into $n\log_2 n - 1.44n$, poor at
  tiny $n$ and excellent by $n = 1000$.
- Merge sort lands within about **3%** of the bound, so no comparison sort can
  ever beat it by more than a few percent.
- The theorem forbids less than it looks: it is about **comparisons**, about
  the **worst case**, and about **arbitrary keys** — three separate doors.
- **Counting sort** walks through the first door by using each key as an
  index: tally, prefix-sum, then place ([38.2](02-counting-radix-bucket.md)).
- Its third pass runs **backwards**, and that direction alone is what makes it
  **stable**.
- Its cost is $O(n + k)$ where $k$ is the key **range**, not the number of
  distinct keys — which is why 32-bit keys would need 16 GB of counters.
- **Radix sort** rescues those cases by counting-sorting one digit at a time,
  least significant first, and every pass *must* be stable or the result is
  nonsense.
- **Bucket sort** scatters values into buckets and sorts within them: $O(n)$ on
  uniform data, $O(n^2)$ when the data crowds into one bucket.
- Linear does not mean fast: an interpreted $O(n)$ radix sort loses to C's
  $O(n \log n)$ Timsort at $n = 100{,}000$, because Big-O hides the constant.

### Key terms

| Term | What it means |
| --- | --- |
| [comparison sort](../concept-index.md#c) | a sort whose only question is "is $a < b$?" |
| [decision tree](../concept-index.md#d) | the model that turns a sort into a countable set of leaves |
| [lower bound](../concept-index.md#l) | $\log_2(n!)$ comparisons, unavoidable in the worst case |
| Stirling's approximation | $\log_2(n!) \approx n\log_2 n - 1.44n$ |
| [stability](../concept-index.md#s) | equal keys leave in the order they arrived |
| [counting sort](../concept-index.md#c) | tally, prefix-sum, place backwards; $O(n + k)$ |
| prefix sum | running totals that turn counts into output positions |
| key range $k$ | the span of possible keys — the number counting sort really costs |
| [radix sort](../concept-index.md#r) | one stable counting sort per digit, least significant first |
| [bucket sort](../concept-index.md#b) | scatter by value, sort each bucket, concatenate |
| [Timsort](../concept-index.md#t) | what `sorted()` really is: stable, adaptive, and written in C |
| [constant factor](../appendix/B-big-o.md) | what Big-O hides, and what decides the race at your $n$ |

Now put it to work. This chapter has two halves and the exercises follow them:
the first three are about the bound and the arithmetic around it, the rest are
about the algorithms that step around it. Do the pencil work before running the
code — counting sort in particular is an algorithm you only really believe once
you have pushed the counters around by hand.

### Exercise 38.1 — Compute the lower bound ●

For $n = 5, 10, 20$ and $10^6$, compute $\log_2(n!)$ exactly and compare it
with the approximation $n\log_2 n - 1.44n$. Then answer: could a comparison
sort of 20 elements ever get away with 50 comparisons in the worst case?

??? success "Solution"

    $\log_2(20!) \approx 61.1$, so 50 comparisons is impossible — no
    comparison sort can sort 20 elements with fewer than 62 comparisons in the
    worst case.

    ```python
    import math

    print(f"{'n':>9}{'log2(n!)':>14}{'n log2 n - 1.44n':>19}{'ceil bound':>12}")
    for n in (5, 10, 20, 1_000_000):
        exact = math.lgamma(n + 1) / math.log(2)
        approx = n * math.log2(n) - n / math.log(2)
        print(f"{n:>9,}{exact:>14.1f}{approx:>19.1f}{math.ceil(exact):>12,}")

    n = 20
    bound = math.ceil(math.lgamma(n + 1) / math.log(2))
    print(f"\nsorting {n} elements needs at least {bound} comparisons "
          f"in the worst case")
    print(f"a claim of 50 comparisons is {'possible' if 50 >= bound else 'IMPOSSIBLE'}")
    ```

    Notice how bad the approximation is at $n = 5$ — 4.4 against a true 6.9,
    an error of more than a third — and how good it is at $n = 10^6$, where the
    two agree to seven significant figures. Asymptotic formulas describe
    behaviour in the limit; for small $n$, compute the exact value.

### Exercise 38.2 — Predict counting sort's prefix sums ●

The keys are `[4, 1, 3, 1, 4, 4, 0, 3]` and $k = 5$.

**Before running anything**, write down: (a) the count array after pass 1,
(b) the prefix array after pass 2, and (c) which output index the element at
*input index 0* (the first `4`) ends up at.

??? success "Solution"

    (a) `[1, 2, 0, 2, 3]` — one 0, two 1s, no 2s, two 3s, three 4s.
    (b) `[1, 3, 3, 5, 8]` — the repeated 3 marks the absent key 2.
    (c) Index **5**. Working backwards, the 4s at input indices 5, 4 and 0 claim
    output slots 7, 6 and 5 in that order, so the *first* 4 in the input lands
    in the *first* of the three slots reserved for 4s. That is stability.

    ```python
    keys = [4, 1, 3, 1, 4, 4, 0, 3]
    k = 5

    count = [0] * k
    for x in keys:
        count[x] += 1
    print("counts :", count)

    for v in range(1, k):
        count[v] += count[v - 1]
    print("prefix :", count)

    out = [None] * len(keys)
    for i in range(len(keys) - 1, -1, -1):
        count[keys[i]] -= 1
        out[count[keys[i]]] = (i, keys[i])       # remember where it came from
        print(f"  input index {i} (key {keys[i]}) -> output index {count[keys[i]]}")

    print("output (input index, key):", out)
    print("keys in order:", [key for _, key in out])
    print("input index 0 landed at output index:",
          next(j for j, (i, _) in enumerate(out) if i == 0))
    ```

    The `(input index, key)` pairs make stability visible: the three items with
    key 4 came from input indices 0, 4, 5 and appear in exactly that order at
    the end.

### Exercise 38.3 — Repair the broken counting sort ●●

This implementation produces a key-sorted result but is **not stable**, so
using it as a radix-sort pass would give nonsense. Find the single-line bug,
fix it, and write a test that catches the bug (a test on the keys alone will
not).

```python
# no-test
def counting_sort_broken(items, k):
    count = [0] * k
    for _, key in items:
        count[key] += 1
    for v in range(1, k):
        count[v] += count[v - 1]
    out = [None] * len(items)
    for i in range(len(items)):          # <-- somewhere here
        name, key = items[i]
        count[key] -= 1
        out[count[key]] = (name, key)
    return out
```

??? success "Solution"

    The loop runs forwards. Because each counter points at the *last* free slot
    for its key and then decrements, the first item with a given key claims the
    last slot and the last item claims the first — every group of equal keys
    comes out reversed. The fix is `range(len(items) - 1, -1, -1)`.

    The test must compare the *payload* order, not the keys.

    ```python
    def counting_sort(items, k, backwards):
        count = [0] * k
        for _, key in items:
            count[key] += 1
        for v in range(1, k):
            count[v] += count[v - 1]
        out = [None] * len(items)
        idx = range(len(items) - 1, -1, -1) if backwards else range(len(items))
        for i in idx:
            name, key = items[i]
            count[key] -= 1
            out[count[key]] = (name, key)
        return out

    def is_stable(original, result):
        """Every group of equal keys must keep its original relative order."""
        expected = sorted(original, key=lambda pair: pair[1])   # sorted() is stable
        return result == expected

    def keys_sorted(result):
        return [key for _, key in result] == sorted(key for _, key in result)

    data = [("a", 2), ("b", 1), ("c", 2), ("d", 0), ("e", 1), ("f", 2)]

    for label, backwards in (("fixed (backwards)", True), ("broken (forwards)", False)):
        got = counting_sort(data, 3, backwards)
        print(f"{label:<20}{[n for n, _ in got]}"
              f"   keys sorted: {keys_sorted(got)}"
              f"   stable: {is_stable(data, got)}")
    ```

    Both versions pass `keys_sorted`; only the fixed one passes `is_stable`.
    Comparing against `sorted(original, key=...)` is the neatest stability
    test there is, because Python's `sorted` is guaranteed stable.

### Exercise 38.4 — Predict the number of radix passes ●●

You are radix-sorting 100,000 integers whose largest value is 9,999. How many
passes does LSD radix sort make with base 2, base 10, base 16, and base 256?
Which base does the least *total* work, counting both the per-pass loop over
$n$ elements and the per-pass loop over the $b$ counters?

??? success "Solution"

    Passes are $\lfloor \log_b(\max) \rfloor + 1$: **14, 4, 4, 2**. Total work
    is roughly $d \times (2n + b)$, and with $n = 100{,}000$ the $b$ term stays
    negligible until the base gets very large, so fewer passes is almost always
    better — base 256 beats base 16 by two-to-one.

    ```python
    import math

    n, largest = 100_000, 9_999
    print(f"{'base':>7}{'passes':>9}{'counters':>11}{'≈ work units':>15}")
    for base in (2, 10, 16, 256, 65_536):
        passes = math.floor(math.log(largest, base)) + 1
        work = passes * (2 * n + base)
        print(f"{base:>7}{passes:>9}{base:>11,}{work:>15,}")

    print("\nreality check — the real pass counts:")
    for base in (2, 10, 16, 256):
        place, passes = 1, 0
        while largest // place > 0:
            passes += 1
            place *= base
        print(f"  base {base:>5}: {passes} passes")
    ```

    The crude work model even puts base 65,536 in first place, because
    $9999 < 65536$ means a single pass — and that exposes the model's limits.
    A 65,536-entry counter array is 256 KB and no longer fits in a CPU's fast
    L2 cache, so the scattered writes into it cost far more than the formula's
    "one work unit" each; it is also pure waste at $n = 100$, where the counter
    array dwarfs the data. Real implementations settle on one byte per pass
    (base 256, a 1 KB counter array) because it stays cache-resident at every
    size, and digit extraction becomes a shift and a mask rather than a
    division.

### Exercise 38.5 — Choose the sort ●●

For each workload, name the algorithm you would use and say why in one
sentence.

1. 50 million web-server log lines, sorted by HTTP status code (100–599).
2. 10,000 floating-point sensor readings, roughly uniform over $[0, 1)$.
3. 200 million 64-bit user IDs.
4. 1,000 employee records sorted by department, then by surname within
   department.
5. A list of 30 arbitrary Python objects with a custom `__lt__`.

??? success "Solution"

    1. **Counting sort.** $k = 500$ against $n = 5 \times 10^7$: the counter
       array is trivial and the sort is one pass. Stability also preserves the
       original time ordering within each status code — usually what you want
       in a log.
    2. **Bucket sort.** Uniform floats are its exact best case; it is $O(n)$
       with tiny buckets. (`sorted()` is also perfectly fine at $n = 10^4$.)
    3. **Radix sort**, base 256, 8 passes — or honestly, whatever your
       language's built-in sort is, unless you have measured this as the
       bottleneck. Counting sort is out: $k = 2^{64}$.
    4. **`sorted()` twice**, relying on stability: sort by surname first, then
       by department. A stable sort leaves surnames ordered within each
       department. This is the single most useful practical consequence of
       stability.
    5. **`sorted()`**. The keys have no numeric structure to exploit, $n = 30$,
       and a comparison sort is the only thing that can even run.

    ```python
    employees = [
        ("Okafor", "Sales"), ("Bell", "Engineering"), ("Zhao", "Sales"),
        ("Ahmed", "Engineering"), ("Novak", "Sales"), ("Cruz", "Engineering"),
    ]

    by_name = sorted(employees, key=lambda e: e[0])        # first pass
    final = sorted(by_name, key=lambda e: e[1])            # second pass, stable
    for surname, dept in final:
        print(f"  {dept:<12}{surname}")

    print("\nsurnames still alphabetical inside each department:",
          all(
              [s for s, d in final if d == dept] ==
              sorted(s for s, d in final if d == dept)
              for dept in {d for _, d in final}
          ))
    ```

    Scenario 4 is worth remembering: "sort by the least significant key first,
    then the most significant" is radix sort's insight applied to whole fields
    instead of digits, and Python's stable `sorted()` makes it a two-liner.

### Exercise 38.6 — Counting sort with negative keys ●●

Counting sort indexes an array with the key, so a negative key would index from
the *end* of the list — silently, with no error. Extend counting sort to handle
any range of integers, including negatives, and prove it works on data
containing both signs.

??? success "Solution"

    Shift by the minimum: allocate `max - min + 1` counters and use
    `key - min` as the index. Remember to keep the original values in the
    output.

    ```python
    def counting_sort_signed(values):
        if not values:
            return []
        lo, hi = min(values), max(values)
        k = hi - lo + 1
        count = [0] * k
        for x in values:
            count[x - lo] += 1                 # shift into [0, k)
        for v in range(1, k):
            count[v] += count[v - 1]
        out = [0] * len(values)
        for i in range(len(values) - 1, -1, -1):
            count[values[i] - lo] -= 1
            out[count[values[i] - lo]] = values[i]
        return out

    def counting_sort_naive(values):
        """The buggy version, for contrast — no shift."""
        k = max(values) + 1
        count = [0] * k
        for x in values:
            count[x] += 1                      # count[-3] wraps to the END
        out = []
        for v, c in enumerate(count):
            out.extend([v] * c)
        return out

    data = [3, -7, 0, 12, -7, 5, -1, 0]
    print("input        :", data)
    print("expected     :", sorted(data))
    print("with shift   :", counting_sort_signed(data))
    print("without shift:", counting_sort_naive(data), " <- silently wrong")
    print("range used   :", max(data) - min(data) + 1, "counters")
    ```

    The naive version does not crash; `count[-7] += 1` cheerfully increments
    the seventh-from-last counter and the negatives vanish from the output.
    Silent wrongness is worse than a crash, which is why the shift belongs in
    the function rather than in a comment.

### Exercise 38.7 — Radix-sort fixed-length strings ●●●

Sort a list of equal-length lowercase strings with LSD radix sort, using a
stable counting sort on one character position per pass. Requirements:

- process character positions from **last to first**;
- verify against `sorted()` on a random list of at least 10,000 strings;
- print the array after each pass on a small example so the "it falls into
  order" effect is visible;
- explain what would have to change for strings of *different* lengths.

??? success "Solution"

    A character is just a small integer via `ord()`, so each pass is the
    counting sort from §38.2 with `k = 128` (the ASCII range). Sorting by the
    last character first and relying on stability is exactly the digit
    argument, one letter at a time.

    ```python
    import random

    def radix_sort_strings(words, alphabet_size=128, show=False):
        """LSD radix sort for equal-length strings. Stable per pass."""
        if not words:
            return []
        width = len(words[0])
        if any(len(w) != width for w in words):
            raise ValueError("all strings must have the same length")

        a = list(words)
        for pos in range(width - 1, -1, -1):          # last character first
            count = [0] * alphabet_size
            for w in a:
                count[ord(w[pos])] += 1
            for c in range(1, alphabet_size):
                count[c] += count[c - 1]
            out = [None] * len(a)
            for i in range(len(a) - 1, -1, -1):       # backwards -> stable
                c = ord(a[i][pos])
                count[c] -= 1
                out[count[c]] = a[i]
            a = out
            if show:
                print(f"  after position {pos}: {a}")
        return a

    words = ["cat", "car", "bat", "bar", "cab", "arc", "ark", "act"]
    print("input:", words)
    result = radix_sort_strings(words, show=True)
    print("result :", result)
    print("sorted():", sorted(words))
    print("match  :", result == sorted(words))

    rng = random.Random(38)
    big = ["".join(rng.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(5))
           for _ in range(10_000)]
    print(f"\n10,000 random 5-letter strings match sorted(): "
          f"{radix_sort_strings(big) == sorted(big)}")
    ```

    Watch the small example: after sorting on position 2 (the last letter) the
    list is grouped by final letter and looks random; after position 1 it is
    sorted by the last two letters; after position 0 it is correct. Each pass
    only fixes one character and trusts the previous passes to survive — which
    they do, because every pass is stable.

    **Different lengths** break the algorithm in two ways. The obvious one is
    that `w[pos]` would raise `IndexError`. The subtle one is that shorter
    strings must sort *before* longer strings that share their prefix
    (`"car" < "cart"`), which means padding with a character that ranks below
    every real letter — or switching to MSD radix sort, which recursively sorts
    each prefix group and handles ragged lengths naturally. Padding with
    `chr(0)` is the usual quick fix, and it works precisely because 0 ranks
    below every printable character.
