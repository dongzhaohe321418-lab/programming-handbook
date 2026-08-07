# 16.1 Big-O notation

"My program takes 0.8 seconds" is a fact about your laptop as much as your
code — a faster machine, a different Python, or a busy afternoon changes
the number. Computer scientists therefore describe an algorithm's cost in a
machine-independent currency: the **number of basic steps** it performs,
written as a function of the input size $n$. This section builds that idea
from running code — you will count the steps yourself and watch the famous
growth patterns fall out.

## Counting steps instead of seconds

A *basic step* is any small, fixed-cost action: an addition, a comparison,
an assignment, an index lookup. We do not fuss over exactly which actions
count — the whole point of the notation we are building is that such
details wash out. To count steps, we simply bolt a counter onto the code.

**Pattern 1: constant work.** Some operations do the same tiny amount of
work no matter how big the input is:

```python
def first_item_steps(items):
    steps = 0
    steps += 1          # one index lookup — regardless of len(items)
    value = items[0]
    return value, steps

for n in [10, 100, 1_000, 10_000]:
    data = list(range(n))
    value, steps = first_item_steps(data)
    print(f"n = {n:>6}  ->  {steps} step")
```

The list grew by a factor of a thousand; the step count did not move. Work
that ignores $n$ is called **constant time**.

**Pattern 2: a single loop.** Touch every item once and the step count
tracks $n$ exactly:

```python
def sum_steps(n):
    steps = 0
    total = 0
    for i in range(n):
        total += i          # one unit of work per item...
        steps += 1          # ...tallied
    return steps

for n in [1, 2, 4, 8, 16, 32]:
    print(f"n = {n:>2}  ->  steps = {sum_steps(n):>2}")
```

Double the input, double the steps: **linear time**.

**Pattern 3: a nested loop.** Compare every item with every item — a loop
inside a loop — and the count is $n \times n$:

```python
def pair_steps(n):
    steps = 0
    for i in range(n):
        for j in range(n):
            steps += 1      # one comparison per (i, j) pair
    return steps

for n in [1, 2, 4, 8, 16, 32]:
    steps = pair_steps(n)
    print(f"n = {n:>2}  ->  steps = {steps:>5}   (n*n = {n * n})")
```

Double the input and the steps *quadruple* — the signature of **quadratic
time**. At $n = 32$ the single loop cost 32 steps; the nested loop costs
1,024.

**Pattern 4: a loop that halves.** Some algorithms discard half the
remaining input at every turn — binary search, which you will meet properly
in [Chapter 22](../ch22-sorting/03-searching.md), is the classic. How many
halvings does it take to shrink $n$ down to 1?

```python
import math

def halving_steps(n):
    steps = 0
    while n > 1:
        n //= 2             # throw half away
        steps += 1
    return steps

for n in [2, 16, 1_024, 1_000_000, 1_000_000_000]:
    print(f"n = {n:>13,}  ->  steps = {halving_steps(n):>2}"
          f"   (log2(n) = {math.log2(n):5.1f})")
```

A *billion* items need only 29 halvings. The inverse of "double it" is the
base-2 logarithm, so this is **logarithmic time** — the step count is about
$\log_2 n$. Logarithms grow so slowly that for practical purposes they feel
almost constant.

Four runnable experiments, four growth patterns: $1$, $n$, $n^2$, and
$\log_2 n$. Everything else in this chapter is vocabulary for talking about
them.

## Big-O: naming the growth family

Here is the awkward part: real step counts are messy. A careful count of
some loop might give $3n^2 + 5n + 20$ steps — and a colleague who counts
assignments differently might get $2n^2 + 7n + 12$. Both of you would be
"right". Big-O notation exists to throw away exactly the parts you would
disagree about — the constant factors and the smaller terms — and keep the
part that matters: the **growth family**.

We say $f(n)$ *is* $O(g(n))$ — read "f is big-oh of g" — when, for large
inputs, $f$ grows no faster than some constant multiple of $g$. The messy
count $3n^2 + 5n + 20$ is $O(n^2)$: it belongs to the quadratic family,
and the 3, the $5n$, and the 20 are details of accounting, not of the
algorithm.

!!! note "The formal definition, for the curious"

    $f(n) \in O(g(n))$ means: there exist a constant $c > 0$ and a
    threshold $n_0$ such that

    $$ f(n) \le c \cdot g(n) \quad \text{for all } n \ge n_0. $$

    In words: beyond some input size, $f$ stays underneath a scaled-up
    copy of $g$ forever. For $f(n) = 3n^2 + 5n + 20$, take $c = 4$ and
    $n_0 = 7$: from $n = 7$ on, $3n^2 + 5n + 20 \le 4n^2$. You will never
    need to produce $c$ and $n_0$ in this book — but it is worth knowing
    the notation has a precise meaning and is not just hand-waving.

Why is dropping all that information legitimate? Watch what happens to the
ratio between the messy function and plain $n^2$ as $n$ grows:

```python
def f(n):
    return 3 * n**2 + 5 * n + 20

print(f"{'n':>8} {'f(n)':>15} {'f(n) / n^2':>12}")
for n in [10, 100, 1_000, 10_000, 100_000]:
    print(f"{n:>8,} {f(n):>15,} {f(n) / n**2:>12.4f}")
```

The ratio settles toward 3 and never exceeds 4 (for $n \ge 7$). So
$f$ is permanently trapped below $4 \cdot n^2$ — which is precisely what
$f \in O(n^2)$ claims. The lower-order terms $5n + 20$ mattered when $n$
was 10; by $n = 100{,}000$ they contribute less than a hundredth of a
percent. **For large inputs, only the dominant term is audible.**

## Best, worst, and average case

One more subtlety before the notation is safe to use: for many algorithms
the step count depends not just on *how much* input there is, but on *which*
input it is. Linear search — scan a list until you find the target, first
seen in [Chapter 8](../ch08-grids/03-first-algorithms.md) — is the standard
example:

```python
def linear_search_steps(items, target):
    steps = 0
    for i, value in enumerate(items):
        steps += 1                    # one comparison
        if value == target:
            return i, steps
    return -1, steps

data = list(range(100))               # the values 0 .. 99

print("best case  (target first):", linear_search_steps(data, 0)[1], "comparison")
print("worst case (target last) :", linear_search_steps(data, 99)[1], "comparisons")
print("worst case (missing)     :", linear_search_steps(data, 500)[1], "comparisons")

total = sum(linear_search_steps(data, t)[1] for t in data)
print("average case (all targets):", total / len(data), "comparisons")
```

Same algorithm, same $n = 100$: anywhere from 1 comparison to 100. So we
speak of three separate quantities:

| Case | Meaning | Linear search |
| --- | --- | --- |
| **Best case** | Luckiest possible input | $O(1)$ — target is first |
| **Worst case** | Unluckiest possible input | $O(n)$ — target last or absent |
| **Average case** | Expected over typical inputs | $O(n)$ — about $n/2$ comparisons, and $n/2$ is still the linear family |

When someone states a complexity without qualification — "linear search is
$O(n)$" — they almost always mean the **worst case**. It is the honest
default: a guarantee that holds no matter how unlucky the input.

## The dominant-term rule

You now have everything needed to read code and name its family without a
counter. The procedure: count loop nestings over the input, add costs of
sequential parts, then *keep only the dominant term and drop its constant*.
Dominance order (slowest-growing first):

$$ 1 \;<\; \log n \;<\; n \;<\; n \log n \;<\; n^2 \;<\; 2^n $$

Practise on these fragments (each `...` is constant work):

```text
# A: two loops in sequence, not nested
for i in range(n): ...          # n steps
for j in range(n): ...          # + n steps        -> 2n        -> O(n)

# B: nested, then a little extra
for i in range(n):
    for j in range(n): ...      # n*n steps
print("done")                   # + 1              -> n^2 + 1   -> O(n^2)

# C: a halving loop inside a full loop
for i in range(n):              # n iterations, each...
    k = n
    while k > 1: k //= 2        # ...log2(n) steps -> n log n   -> O(n log n)

# D: loop bounded by a constant, not by n
for i in range(1000): ...       # 1000 steps regardless of n    -> O(1)
```

Fragment D is the one that trips people up: a big fixed number of steps is
still *constant* — Big-O asks how cost **scales with n**, not whether the
code is quick.

!!! warning "Common mistakes"

    - **Reading Big-O as a speed report.** $O(1)$ code can be slow and
      $O(n^2)$ code fast *at small n* — the notation only predicts how
      cost grows as $n$ does. For $n = 20$, constants rule (see
      [16.2](02-timing.md)).
    - **Keeping the constants.** "This algorithm is $O(3n^2 + 5n)$" is not
      wrong so much as missing the point — the family is $O(n^2)$; the 3
      and the $5n$ are exactly what the notation is designed to discard.
    - **Counting every nested loop as $n^2$.** Only loops whose lengths
      *both* scale with the input multiply to $n^2$. A loop over `range(5)`
      inside a loop over `range(n)` is $5n$ — linear.
    - **Mixing up the cases.** Finding the target on the first try does
      not make linear search $O(1)$ — that is its *best* case. Unqualified
      Big-O statements describe the worst case.

## Check your understanding

1. A colleague counts an algorithm at $7n + 200$ steps; you count
   $5n + 90$. Who is right, and what is the Big-O?

    ??? success "Answer"

        Both, plausibly — you drew the line around "one step" differently.
        That disagreement is exactly why Big-O exists: both counts are in
        the linear family, $O(n)$, and the notation erases the accounting
        choices.

2. Without running it, give the growth family of the loop that prints all
   *ordered pairs* `(i, j)` with `i` and `j` each from `range(n)` — and of
   the loop that prints each item of a list twice.

    ??? success "Answer"

        Ordered pairs: two input-scaled loops nested, $n \cdot n$ steps,
        so $O(n^2)$. Each item twice: one pass doing two prints per item,
        $2n$ steps, so $O(n)$ — a constant amount of work per element
        never changes the family.

3. Using the formal definition, why is $10n$ **not** in $O(\log n)$?

    ??? success "Answer"

        We would need constants with $10n \le c \cdot \log_2 n$ for all
        large $n$. But $n / \log_2 n$ grows without bound, so no fixed $c$
        can cap it — eventually $10n$ overtakes $c \log_2 n$ for every
        choice of $c$. No such constants exist, so the claim fails.

4. Binary search does at most $\log_2 n$-ish comparisons in the worst
   case. About how many for a *million*-item sorted list — and what does
   your answer suggest about why sorted data is valuable?

    ??? success "Answer"

        $\log_2 1{,}000{,}000 \approx 20$ comparisons — versus up to a
        million for linear search. Keeping data sorted (or indexed) buys
        exponentially cheaper lookups, which is why so many data
        structures in Part III exist to maintain order.
