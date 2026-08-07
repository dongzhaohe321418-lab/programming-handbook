# Exercises

Counting first, stopwatch second — same as the chapter. Keep every timing
experiment's sizes modest (the solutions show sizes that finish fast), and
remember the protocol: repeat, take the minimum.

### Exercise 16.1 — Predict the counter ●

**Before running it**, write down exactly what this program prints. Then
run it and settle the score.

```python
steps = 0
n = 8
for i in range(n):
    steps += 1
print("after first loop :", steps)

k = n
while k > 1:
    k //= 2
    steps += 1
print("after while loop :", steps)

for i in range(n):
    for j in range(3):
        steps += 1
print("after nested loop:", steps)
```

??? success "Solution"

    Predicted output:

    ```text
    after first loop : 8
    after while loop : 11
    after nested loop: 35
    ```

    ```python
    steps = 0
    n = 8
    for i in range(n):
        steps += 1
    print("after first loop :", steps)

    k = n
    while k > 1:
        k //= 2
        steps += 1
    print("after while loop :", steps)

    for i in range(n):
        for j in range(3):
            steps += 1
    print("after nested loop:", steps)
    ```

    The first loop adds $n = 8$ steps. The halving loop adds
    $\log_2 8 = 3$. The nested loop adds $8 \times 3 = 24$ — note it is
    *not* $n^2$, because the inner loop is a constant 3, so the pattern
    is $O(n)$, not $O(n^2)$.

### Exercise 16.2 — Name that family ●

Classify each fragment as $O(1)$, $O(\log n)$, $O(n)$, or $O(n^2)$, with a
one-sentence justification. Then verify at least two of your answers by
adding a step counter and printing counts for doubling values of `n`.

```text
# A                                  # B
total = 0                            for i in range(n):
for x in data:      # len(data) = n      for j in range(10):
    total += x                               work()

# C                                  # D
k = n                                for i in range(n):
while k > 1:                             for j in range(i + 1, n):
    k //= 3                                  work()
```

??? success "Solution"

    - **A: $O(n)$** — one pass, constant work per element.
    - **B: $O(n)$** — the inner loop is a fixed 10, so $10n$ steps;
      constant factors don't change the family.
    - **C: $O(\log n)$** — dividing by 3 each turn; about $\log_3 n$
      iterations (any-base log is the logarithmic family).
    - **D: $O(n^2)$** — the inner loop shrinks, but the total is
      $n(n-1)/2$ pairs, and $n^2/2$ is still quadratic.

    ```python
    def count_b(n):
        steps = 0
        for i in range(n):
            for j in range(10):
                steps += 1
        return steps

    def count_d(n):
        steps = 0
        for i in range(n):
            for j in range(i + 1, n):
                steps += 1
        return steps

    for n in [8, 16, 32, 64]:
        print(f"n = {n:>2}   B: {count_b(n):>4} (= 10n)"
              f"   D: {count_d(n):>4} (= n(n-1)/2 = {n * (n - 1) // 2})")
    ```

    B doubles when $n$ doubles (linear); D roughly quadruples
    (quadratic).

### Exercise 16.3 — Order the growth ●●

Sort these functions from slowest-growing to fastest-growing:

$$ n \log_2 n, \qquad 2^n, \qquad \log_2 n, \qquad n^2, \qquad n, \qquad 42 $$

Then write a program that prints each function's value at
$n = 10, 100, 1000$ and check that your ordering has taken hold by
$n = 1000$.

??? success "Solution"

    Slowest to fastest: $42$ (constant), $\log_2 n$, $n$, $n \log_2 n$,
    $n^2$, $2^n$.

    ```python
    import math

    funcs = [
        ("42", lambda n: 42.0),
        ("log2 n", lambda n: math.log2(n)),
        ("n", lambda n: float(n)),
        ("n log2 n", lambda n: n * math.log2(n)),
        ("n^2", lambda n: float(n) ** 2),
        ("2^n", lambda n: 2.0 ** n),
    ]

    header = f"{'f(n)':>10}" + "".join(f"{n:>12}" for n in [10, 100, 1000])
    print(header)
    for name, f in funcs:
        row = f"{name:>10}"
        for n in [10, 100, 1000]:
            row += f"{f(n):>12.3g}"
        print(row)
    ```

    At $n = 10$ the ordering is already visible but cosy ($2^{10}$ is
    only 1024); at $n = 1000$, $2^n$ is about $10^{301}$ — a number with
    more digits than there are atoms in the observable universe, while
    $n \log_2 n$ sits at a homely 9,966. Growth families separate
    *dramatically*, not gradually.

### Exercise 16.4 — Doubling detective ●●

You are handed two functions you may *time but not read* (pretend!). Use
the doubling experiment — best-of-3 timings at $n$ and $2n$ — to determine
each one's growth family. Suggested sizes: `mystery_a` at $n = 300$,
`mystery_b` at $n = 50\,000$.

```text
def mystery_a(n):
    total = 0
    for i in range(n):
        for j in range(i):
            total += j
    return total

def mystery_b(n):
    total, i = 0, 0
    while i < n:
        total += i
        i += 1
    return total
```

??? success "Solution"

    ```python
    import time

    def mystery_a(n):
        total = 0
        for i in range(n):
            for j in range(i):
                total += j
        return total

    def mystery_b(n):
        total, i = 0, 0
        while i < n:
            total += i
            i += 1
        return total

    def time_best_of(func, n, repeats=3):
        best = float("inf")
        for _ in range(repeats):
            start = time.perf_counter()
            func(n)
            best = min(best, time.perf_counter() - start)
        return best

    n = 300
    ratio_a = time_best_of(mystery_a, 2 * n) / time_best_of(mystery_a, n)
    n = 50_000
    ratio_b = time_best_of(mystery_b, 2 * n) / time_best_of(mystery_b, n)

    print(f"mystery_a: T(2n)/T(n) = {ratio_a:.1f}  -> near 4: O(n^2)")
    print(f"mystery_b: T(2n)/T(n) = {ratio_b:.1f}  -> near 2: O(n)")
    ```

    `mystery_a`'s inner loop runs $0 + 1 + \cdots + (n-1) = n(n-1)/2$
    times — quadratic, so doubling $n$ quadruples the time. `mystery_b`
    is a plain linear pass dressed up as a `while` loop. (Exact ratios
    wobble; the neighbourhood — 2-ish vs 4-ish — is the verdict.)

### Exercise 16.5 — The accidental $O(n^2)$: strings ●●

A classic trap: building a big string by concatenating in a loop. Each
`+` between strings creates a **brand-new string**, copying everything
built so far — so $n$ concatenations copy $1 + 2 + \cdots + n \approx
n^2/2$ characters in total. Time these three builders with a doubling
experiment at $n = 30\,000$ vs $n = 60\,000$ and classify each:

```text
def build_prepend(n):          # s = "*" + s  in a loop
def build_join(n):             # append pieces to a list, "".join at the end
def build_concat(n):           # s = s + "*"  in a loop
```

One result should surprise you — explain it before reading the solution's
last paragraph.

??? success "Solution"

    ```python
    import time

    def build_prepend(n):
        s = ""
        for _ in range(n):
            s = "*" + s               # copies the whole of s, every time
        return s

    def build_join(n):
        pieces = []
        for _ in range(n):
            pieces.append("*")        # amortized O(1) each
        return "".join(pieces)        # one final O(n) pass

    def build_concat(n):
        s = ""
        for _ in range(n):
            s = s + "*"
        return s

    def time_best_of(func, n, repeats=3):
        best = float("inf")
        for _ in range(repeats):
            start = time.perf_counter()
            func(n)
            best = min(best, time.perf_counter() - start)
        return best

    n = 30_000
    for f in [build_prepend, build_join, build_concat]:
        ratio = time_best_of(f, 2 * n) / time_best_of(f, n)
        print(f"{f.__name__:<14}: T(2n)/T(n) = {ratio:4.1f}")
    ```

    `build_prepend` shows a ratio around 4 — the true quadratic face of
    loop concatenation. `build_join` is the right way: near 2, linear.
    (If you rerun with a much smaller $n$, the prepend ratio sags toward
    2-something: copying short strings is so cheap that loop overhead
    still dominates — pitfall 2 from [section 16.2](02-timing.md) caught
    in the act.)

    The surprise is `build_concat`, which often *also* looks linear.
    That is a CPython-specific mercy: when the string on the left has no
    other references, CPython resizes it in place instead of copying.
    **Do not rely on it** — it vanishes the moment another variable
    refers to the string, it is not promised by the language, and the
    equivalent Java code (`s += "*"` on `String`) really is quadratic,
    which is why Java programmers use `StringBuilder`. Write `join`;
    treat the optimisation as luck, not design.

### Exercise 16.6 — Back of the envelope ●●

Using the $10^8$-simple-operations-per-second rule of thumb and a one-
second budget: (a) estimate by hand the largest feasible $n$ for an
$O(n^3)$ algorithm and for an $O(3^n)$ algorithm; (b) check both with the
`largest_n` binary-search helper from
[section 16.3](03-complexity-zoo.md).

??? success "Solution"

    By hand: $n^3 \le 10^8$ gives $n \le 10^{8/3} \approx 464$. For
    $3^n \le 10^8$: $n \le \log_3 10^8 = 8 / \log_{10} 3 \approx 16.8$,
    so $n = 16$.

    ```python
    budget = 10 ** 8

    def largest_n(cost, hi=10 ** 9):
        lo, best = 1, 1
        while lo <= hi:
            mid = (lo + hi) // 2
            if cost(mid) <= budget:
                best, lo = mid, mid + 1
            else:
                hi = mid - 1
        return best

    print("O(n^3):", largest_n(lambda n: n ** 3))
    print("O(3^n):", largest_n(lambda n: 3 ** n if n < 60 else float("inf")))
    ```

    Cubic algorithms cap out in the mid-hundreds — noticeably tighter
    than quadratic's ten thousand — and base-3 exponentials hit the wall
    even sooner than base-2 ones. The guard `n < 60` avoids computing
    astronomically large powers during the search.

### Exercise 16.7 — The `insert(0, ...)` trap ●●●

Both functions build the list `[n-1, ..., 1, 0]`:

```text
def via_insert(n):                   def via_append(n):
    lst = []                             lst = []
    for i in range(n):                   for i in range(n):
        lst.insert(0, i)                     lst.append(i)
    return lst                           return lst[::-1]
```

Predict each one's complexity using the price-tag table from
[section 16.3](03-complexity-zoo.md), then confirm with a doubling
experiment at $n = 10\,000$ vs $20\,000$.

??? success "Solution"

    `insert(0, x)` shifts every existing element right: $O(n)$ *per
    call*, hidden inside a single innocent line. Called $n$ times, the
    build is $O(n^2)$. `append` is amortized $O(1)$, and the final
    reversing slice is one $O(n)$ pass — total $O(n)$.

    ```python
    import time

    def via_insert(n):
        lst = []
        for i in range(n):
            lst.insert(0, i)
        return lst

    def via_append(n):
        lst = []
        for i in range(n):
            lst.append(i)
        return lst[::-1]

    def time_best_of(func, n, repeats=3):
        best = float("inf")
        for _ in range(repeats):
            start = time.perf_counter()
            func(n)
            best = min(best, time.perf_counter() - start)
        return best

    assert via_insert(6) == via_append(6)      # same answer...

    n = 10_000
    for f in [via_insert, via_append]:
        ratio = time_best_of(f, 2 * n) / time_best_of(f, n)
        print(f"{f.__name__:<10}: T(2n)/T(n) = {ratio:4.1f}")
    ```

    Same output, different families: the insert version's ratio sits
    near 4, the append version's near 2. The lesson generalises: **a
    loop is only as cheap as the dearest operation inside it** — audit
    the built-ins, not just the `for` lines.

### Exercise 16.8 — Hunting for $c$ and $n_0$ ●●●

The formal definition says $f(n) = 5n^2 + 100n$ is in $O(n^2)$ if there
are constants with $f(n) \le c \cdot n^2$ for all $n \ge n_0$. Propose
concrete values of $c$ and $n_0$, justify them algebraically, then write a
program that (a) prints $f(n)/n^2$ for growing $n$ to show where the ratio
settles, and (b) *verifies* your pair by checking every $n$ from $n_0$ to
$100\,000$.

??? success "Solution"

    Take $c = 6$ and $n_0 = 100$: the claim $5n^2 + 100n \le 6n^2$
    rearranges to $100n \le n^2$, i.e. $n \ge 100$. (Infinitely many
    other pairs work — e.g. $c = 105, n_0 = 1$ — the definition only
    asks for *one*.)

    ```python
    def f(n):
        return 5 * n**2 + 100 * n

    print(f"{'n':>8} {'f(n)/n^2':>10}")
    for n in [10, 100, 1_000, 10_000, 100_000]:
        print(f"{n:>8,} {f(n) / n**2:>10.4f}")

    c, n0 = 6, 100
    violations = sum(1 for n in range(n0, 100_001) if f(n) > c * n * n)
    print(f"violations of f(n) <= {c} n^2 for n in [{n0}, 100000]:",
          violations)
    ```

    The ratio glides down toward 5 (the leading coefficient) and dips
    under 6 exactly at $n = 100$ — algebra and experiment agree, and the
    verification loop reports zero violations. This is the formal
    definition made tangible: past $n_0$, $f$ lives permanently below
    $c \cdot g$.
