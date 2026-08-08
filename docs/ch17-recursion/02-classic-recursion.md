# 17.2 Classic recursive problems

Recursion has a canon — a handful of problems that every programmer solves
recursively at least once, because they teach the *design recipe* better than
any lecture. The recipe is always the same three questions:

1. **What is the base case?** Which input can be answered outright, with no
   recursive call?
2. **How does the problem shrink?** What smaller version of itself does each
   call hand onward?
3. **How do we combine?** Assuming the smaller call *already works*, how do
   we build our answer out of its answer?

That third step is the leap of faith beginners resist: you must **trust the
smaller call** and not try to mentally trace every frame. Trace once or twice
to build confidence (you did, in the last section) — then design by recipe.

## Sum of a list: head + rest

To sum a list, split it into its first element (the *head*) and everything
after (the *rest*). The sum is `head + sum(rest)`, and the sum of an empty
list is `0` — that is the whole design:

```python
def total(items):
    if not items:                      # base case: empty list sums to 0
        return 0
    return items[0] + total(items[1:])  # head + (trust: sum of the rest)

print(total([4, 8, 15, 16, 23, 42]))
print(total([]))
```

This prints `108` and `0`. Read the recursive line with the recipe in mind:
we do *not* think about how `total(items[1:])` works — it is a smaller list,
so by assumption it works — we only decide what to *do* with its answer (add
the head). The slice `items[1:]` is the "progress" of law 2: each call
handles a list one element shorter, marching toward `[]`.

## Reverse a string

Same skeleton, different combination step: the reversal of a string is the
reversal of its rest, with the head moved to the *end*.

```python
def reverse(s):
    if len(s) <= 1:            # base case: "" and "x" are their own reverse
        return s
    return reverse(s[1:]) + s[0]

print(reverse("stressed"))
print(reverse("a"))
```

The output is `desserts` and `a`. One-line proof of correctness by the
recipe: *if* `reverse("tressed")` really is `"dessert"`, then
`"dessert" + "s"` is `"desserts"`. Trust the smaller call.

## Fast exponentiation: shrink harder

The obvious recursion for $x^n$ peels off one factor at a time:
$x^n = x \cdot x^{n-1}$, base case $x^0 = 1$. That takes about $n$ calls. But
there is a much better shrink: when $n$ is even,
$x^n = (x^{n/2})^2$ — one recursive call *halves* the problem instead of
nibbling at it. Count the calls to feel the difference:

```python
slow_calls = 0
def power_slow(x, n):
    global slow_calls
    slow_calls += 1
    if n == 0:
        return 1
    return x * power_slow(x, n - 1)

fast_calls = 0
def power_fast(x, n):
    global fast_calls
    fast_calls += 1
    if n == 0:
        return 1
    if n % 2 == 0:
        half = power_fast(x, n // 2)   # ONE call, used twice
        return half * half
    return x * power_fast(x, n - 1)

print(power_slow(2, 100) == power_fast(2, 100) == 2 ** 100)
print("slow calls:", slow_calls)
print("fast calls:", fast_calls)
```

Both compute $2^{100}$ correctly, but the slow version makes 101 calls and
the fast one just 10 — that is $O(n)$ versus $O(\log n)$, the same gap you
measured in [Chapter 16](../ch16-complexity/01-big-o.md).

One caution is baked into the code: on the even branch we call `power_fast`
**once** and square the result. Writing
`power_fast(x, n // 2) * power_fast(x, n // 2)` computes the same value with
*two* calls at every level, and that innocent-looking duplication brings the
cost right back to $O(n)$. Duplicated recursive calls are exactly the disease
we dissect with Fibonacci below.

## Binary search, recursively

Binary search — introduced iteratively in
[Chapter 22](../ch22-sorting/03-searching.md) — is recursion-shaped at heart:
look at the middle element; if it is not the target, the answer lies entirely
in one half, which is a *smaller* sorted list. The base case is a search
range that has shrunk to nothing.

```python
def binary_search(items, target, lo=0, hi=None):
    if hi is None:
        hi = len(items) - 1
    if lo > hi:                     # base case: empty range, not found
        return -1
    mid = (lo + hi) // 2
    if items[mid] == target:
        return mid
    if items[mid] < target:
        return binary_search(items, target, mid + 1, hi)   # right half
    return binary_search(items, target, lo, mid - 1)       # left half

sorted_data = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
print(binary_search(sorted_data, 17))
print(binary_search(sorted_data, 4))
```

This prints `6` (the index of `17`) and `-1`. Note the trick of carrying the
search *range* (`lo`, `hi`) as extra parameters instead of slicing the list —
slices copy data, while indices make each call $O(1)$ apart from the
comparison. Like `power_fast`, each call halves the range: $O(\log n)$ calls.

## Fibonacci and the exponential trap

The Fibonacci sequence $0, 1, 1, 2, 3, 5, 8, \dots$ has the most seductive
recursive definition in mathematics: $F(n) = F(n-1) + F(n-2)$, with
$F(0)=0$, $F(1)=1$. Translate it directly and count the calls:

```python
calls = 0
def fib(n):
    global calls
    calls += 1
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)

for n in [5, 10, 15, 20, 25]:
    calls = 0
    value = fib(n)
    print(f"fib({n:2d}) = {value:6d}   {calls:7d} calls")
```

The output shows the trap in cold numbers:

```text
fib( 5) =      5        15 calls
fib(10) =     55       177 calls
fib(15) =    610      1973 calls
fib(20) =   6765     21891 calls
fib(25) =  75025    242785 calls
```

Adding 5 to `n` multiplies the work by roughly 11 — the call count grows
*exponentially*, roughly $O(1.62^n)$. Each call spawns two more, and unlike
`power_fast`'s halves, the two subproblems overlap almost entirely.

That overlap is the whole problem. `fib(25)` recomputes `fib(1)` tens of
thousands of times, even though the result set is tiny: only the 26 values
`fib(0)` … `fib(25)` exist, yet we compute a quarter of a million of them.

**Memoization** is the fix: remember every answer in a dictionary the first
time you compute it, and look it up ever after.

```python
calls = 0
memo = {}
def fib(n):
    global calls
    calls += 1
    if n in memo:                    # seen it before? answer instantly
        return memo[n]
    if n < 2:
        return n
    memo[n] = fib(n - 1) + fib(n - 2)
    return memo[n]

print("fib(25) =", fib(25))
print("calls:", calls)
```

Same function shape, same trust-the-smaller-call logic — but now **49 calls**
instead of 242 785.

That is the wow moment of this chapter: a four-line cache turns an exponential
algorithm into a linear one, because each value is computed once and every
repeat is a dictionary hit.

The pattern is so useful that Python ships it ready-made:
`functools.lru_cache` is a **decorator** — a line starting with `@` placed
above a `def`, which wraps the function in extra behaviour. Here the extra
behaviour is exactly our memo dictionary, managed automatically:

```python
from functools import lru_cache

@lru_cache(maxsize=None)
def fib(n):
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)

print("fib(25) =", fib(25))
print(fib.cache_info())
```

`cache_info()` reports `misses=26` — the 26 genuinely distinct computations —
and `hits=23` for every repeated question. The function body stays a pure
transcription of the mathematics; the cache is bolted on from outside.

## Towers of Hanoi

Three pegs; $n$ disks stacked smallest-on-top on peg A; move the whole tower
to peg C, one disk at a time, never placing a larger disk on a smaller one.
Iteratively this feels impossible to plan. Recursively it is three lines of
*trust* — to move $n$ disks from `source` to `target`:

1. **Clear the way.** Move the top $n-1$ disks to the spare peg.
2. **Move the big disk.** One move, `source` to `target`.
3. **Pile them back on.** Move those $n-1$ disks from the spare onto it.

```python
move_count = 0
def hanoi(n, source, target, spare):
    global move_count
    if n == 0:                        # base case: nothing to move
        return
    hanoi(n - 1, source, spare, target)   # step 1: clear the way
    move_count += 1
    print(f"move disk {n}: {source} -> {target}")
    hanoi(n - 1, spare, target, source)   # step 3: pile them back on top

hanoi(4, "A", "C", "B")
print("total moves:", move_count)
```

Sixteen lines of output: fifteen moves, then `total moves: 15`. Is 15
special? The move count $M(n)$ obeys $M(n) = 2M(n-1) + 1$ (two sub-towers
plus one big-disk move), which solves to $M(n) = 2^n - 1$. Verify it without
printing a single move:

```python
def count_moves(n):
    if n == 0:
        return 0
    return 2 * count_moves(n - 1) + 1

for n in range(1, 11):
    print(f"n={n:2d}: {count_moves(n):5d} moves  (2**{n} - 1 = {2**n - 1})")
```

Every row agrees with the formula. The exponential here is *honest* — unlike
Fibonacci's wasted recomputation, Hanoi genuinely requires $2^n - 1$ moves,
so no cache can save you. The legend of monks moving a 64-disk tower would
take $2^{64}-1$ moves — around 585 billion years at one move per second.

## A recursive picture: the fractal tree

Recursion does not only compute — it *draws*. A tree branch is a line segment
with two smaller tree branches sprouting from its tip; the base case is a
branch too small to matter. That sentence is the entire algorithm:

```python
import math
import matplotlib.pyplot as plt

def draw_branch(ax, x, y, angle_deg, length, depth):
    if depth == 0:                    # base case: twig too small, stop
        return
    x2 = x + length * math.cos(math.radians(angle_deg))
    y2 = y + length * math.sin(math.radians(angle_deg))
    color = "saddlebrown" if depth > 4 else "forestgreen"
    ax.plot([x, x2], [y, y2], linewidth=depth * 0.6, color=color)
    draw_branch(ax, x2, y2, angle_deg - 25, length * 0.72, depth - 1)
    draw_branch(ax, x2, y2, angle_deg + 25, length * 0.72, depth - 1)

fig, ax = plt.subplots(figsize=(6, 6))
draw_branch(ax, 0.0, 0.0, 90, 1.0, 8)
ax.set_aspect("equal")
ax.set_xlabel("x")
ax.set_ylabel("y")
ax.set_title("255 branches from one recursive function")
```

Run it: eight levels of recursion produce $1 + 2 + 4 + \dots + 128 = 255$
line segments arranged into an unmistakable tree. Each call draws *one*
segment and delegates the two sub-trees — trust the smaller call, even when
the "answer" is a picture. Change the angles (`- 25` and `+ 25`), the shrink factor
(`0.72`), or the depth and rerun; keep depth at 8 or below, since the number
of branches doubles with each extra level.

!!! warning "Common mistakes"
    - **Tracing instead of trusting.** Trying to hold all of `fib(25)`'s
      frames in your head is hopeless and unnecessary. Verify the base case,
      verify the shrink, verify the combination step — done.
    - **Duplicating a recursive call.** `power_fast(x, n//2) ** 2` computed
      via *two* identical calls silently reintroduces the exponential
      blow-up. Call once, store, reuse.
    - **Slicing when an index would do.** `total(items[1:])` copies the rest
      of the list at every level ($O(n^2)$ copying overall). Fine for
      learning; for real code pass `lo`/`hi` indices as `binary_search` does.
    - **Memoizing a function that never repeats work.** A cache on
      `binary_search` or `hanoi` wastes memory: their subproblems are all
      distinct. Memoization only pays when subproblems *overlap*, as in
      Fibonacci.

## Check your understanding

1. For `reverse("abc")`, what are the three questions of the design recipe
   and their answers?

    ??? success "Answer"
        Base case: strings of length 0 or 1 are their own reverse. Shrink:
        recurse on `s[1:]` (`"bc"`), one character shorter. Combine: append
        the head to the reversed rest — `reverse("bc") + "a"` = `"cb" + "a"`
        = `"cba"`.

2. `power_fast(2, 64)` — roughly how many calls does it make, and why?

    ??? success "Answer"
        About $\log_2 64 + 2 \approx 8$ calls: 64 is a power of two, so every
        step halves `n` (64, 32, 16, 8, 4, 2, then 1 and 0 — with one extra
        call because `n = 1` takes the odd branch).

3. Naive `fib(30)` makes 2 692 537 calls. Roughly how many calls does the
   memoized version make, and where does that number come from?

    ??? success "Answer"
        About $2 \times 30 = 60$ calls (59, to be exact): each of the 31
        distinct values `fib(0)`…`fib(30)` is computed at most once, and each
        computed value asks two sub-questions, which are either base cases or
        instant cache hits — linear in $n$, not exponential.

4. Why can memoization not speed up the Towers of Hanoi?

    ??? success "Answer"
        Hanoi's cost is in the *moves themselves*, and $2^n - 1$ moves must
        genuinely all happen; no two subproblems produce reusable, identical
        output the way `fib(k)` does. Caching helps only when the same
        subproblem is solved repeatedly.
