# Exercises

## The chapter in brief

- A recursive call is an ordinary function call: it pushes a **stack frame**
  with its own copy of the parameters, and pops it on return
  ([17.1](01-call-stack.md)).
- Every correct recursive function obeys **two laws** — it has a base case,
  and every call makes progress toward it.
- A recursive run has a V shape: the frames pile up on the way down, and the
  pending work finishes on the way back up.
- Break either law and Python raises `RecursionError` at its frame limit
  (1000 by default); Java raises `StackOverflowError`.
- Designing a recursion is three questions: what is the base case, how does
  the problem shrink, and how do we combine the smaller answer
  ([17.2](02-classic-recursion.md)).
- The leap of faith is to **trust the smaller call** rather than trace every
  frame.
- Shrinking *harder* changes the family: peeling one factor off $x^n$ costs
  $O(n)$ calls, halving the exponent costs $O(\log n)$.
- Naive Fibonacci is exponential because its two subproblems overlap;
  **memoization** — a dict, or `functools.lru_cache` — collapses it to
  linear.
- Caching only pays when subproblems repeat: Hanoi's $2^n - 1$ moves are an
  *honest* exponential that no cache can rescue.
- Recursion and iteration are interchangeable, so the choice is engineering:
  match the code's shape to the data's shape ([17.3](03-vs-iteration.md)).
- Any recursion converts to a loop by keeping your own **explicit stack** —
  a call becomes a push, a return becomes a pop.
- Neither Python nor Java optimizes **tail calls**, so a deep tail-shaped
  recursion still crashes; write it as a loop.

### Key terms

| Term | Reminder |
| --- | --- |
| [recursion](../concept-index.md) | a function defined in terms of a smaller version of itself |
| [base case](../concept-index.md) | the input answered directly, with no recursive call |
| progress | the guarantee that each call moves strictly closer to the base case |
| [stack frame](../concept-index.md) | one call's private workspace of parameters and locals |
| [call stack](../concept-index.md) | the pile of frames for all calls currently in progress |
| [`RecursionError`](../concept-index.md) | Python's error when the frame limit is exceeded |
| [memoization](../concept-index.md) | caching each answer the first time, so repeats are lookups |
| `functools.lru_cache` | the decorator that supplies that cache for you |
| divide and conquer | split the input, solve the parts recursively, combine |
| explicit stack | a list used as a to-do pile, replacing the call stack |
| [tail call / tail recursion](../concept-index.md) | a recursive call with nothing left to do after it returns |

Now the drills.

Work these in order — they climb from tracing on paper to converting
recursion into stack-driven iteration. For every function you write, state
the base case and the progress argument *before* coding; that habit is the
whole point of the chapter.

### Exercise 17.1 — Trace on paper, then verify ●

Without running it, write down exactly what this program prints, line by
line. Pay attention to which prints happen before the recursive call and
which happen after. Then run it and compare.

```text
def mystery(n):
    print("enter", n)
    if n > 0:
        mystery(n - 1)
    print("leave", n)

mystery(3)
```

??? success "Solution"

    ```python
    def mystery(n):
        print("enter", n)
        if n > 0:
            mystery(n - 1)
        print("leave", n)

    mystery(3)
    ```

    The output is `enter 3, enter 2, enter 1, enter 0`, then
    `leave 0, leave 1, leave 2, leave 3` — the `enter` lines happen on the
    way down the call stack, and the `leave` lines run in *reverse* order as
    the frames pop on the way back up.

### Exercise 17.2 — count_down ●

Write a recursive function `count_down(n)` that prints the numbers from `n`
down to 1, then prints `Liftoff!`. No loops allowed. Test with
`count_down(5)`.

??? success "Solution"

    ```python
    def count_down(n):
        if n == 0:               # base case: nothing left to count
            print("Liftoff!")
            return
        print(n)
        count_down(n - 1)        # progress: n shrinks toward 0

    count_down(5)
    ```

    Printing *before* the recursive call gives descending order; the base
    case supplies the final message.

### Exercise 17.3 — sum_digits ●

Write a recursive `sum_digits(n)` returning the sum of the decimal digits of
a non-negative integer, e.g. `sum_digits(4712)` is `14`. Hint: `n % 10` is
the last digit and `n // 10` is the rest — the head/rest split for numbers.

??? success "Solution"

    ```python
    def sum_digits(n):
        if n < 10:                        # base case: one digit left
            return n
        return n % 10 + sum_digits(n // 10)   # last digit + sum of the rest

    print(sum_digits(4712))
    print(sum_digits(7))
    print(sum_digits(999999))
    ```

    Prints `14`, `7`, `54`. Each call chops off one digit, so `n // 10`
    strictly shrinks toward the single-digit base case.

### Exercise 17.4 — is_palindrome ●●

Write a recursive `is_palindrome(s)` that returns `True` when the string
reads the same forwards and backwards (`"racecar"`, `"noon"`, `""`). The
recursive insight: a string is a palindrome when its first and last
characters match *and* everything between them is a palindrome.

??? success "Solution"

    ```python
    def is_palindrome(s):
        if len(s) <= 1:                  # base case: "" and "x" qualify
            return True
        if s[0] != s[-1]:                # mismatch at the ends: fail fast
            return False
        return is_palindrome(s[1:-1])    # progress: two characters shorter

    for word in ["racecar", "noon", "python", "", "ab"]:
        print(word.ljust(8), is_palindrome(word))
    ```

    Each call strips one character from both ends, so the string shrinks by
    two toward the empty/one-character base case.

### Exercise 17.5 — Count the moves, trust the formula ●●

Using the Hanoi recurrence — moving $n$ disks takes the moves for $n-1$
disks, twice, plus one — write `count_moves(n)` *without printing any
moves*, and verify `count_moves(n) == 2**n - 1` for `n` from 1 to 15.

??? success "Solution"

    ```python
    def count_moves(n):
        if n == 0:
            return 0
        return 2 * count_moves(n - 1) + 1

    for n in range(1, 16):
        assert count_moves(n) == 2 ** n - 1
    print("formula verified for n = 1..15")
    print("a 15-disk tower needs", count_moves(15), "moves")
    ```

    The recurrence $M(n) = 2M(n-1) + 1$ with $M(0)=0$ unrolls to
    $2^n - 1$ — verified here by brute agreement rather than algebra.

### Exercise 17.6 — Memoize a slow function ●●

The number of shortest grid paths from the top-left to the bottom-right of
an $r \times c$ grid (moving only right or down) satisfies
`paths(r, c) = paths(r-1, c) + paths(r, c-1)`, with one path when `r == 0`
or `c == 0`. Write the naive version with a call counter, run
`paths(10, 10)`, then add a memo dictionary and compare the call counts.

??? success "Solution"

    ```python
    calls = 0
    def paths(r, c):
        global calls
        calls += 1
        if r == 0 or c == 0:
            return 1
        return paths(r - 1, c) + paths(r, c - 1)

    naive_result = paths(10, 10)
    naive_calls = calls

    calls = 0
    memo = {}
    def paths_memo(r, c):
        global calls
        calls += 1
        if (r, c) in memo:
            return memo[(r, c)]
        if r == 0 or c == 0:
            return 1
        memo[(r, c)] = paths_memo(r - 1, c) + paths_memo(r, c - 1)
        return memo[(r, c)]

    memo_result = paths_memo(10, 10)
    print("result:", naive_result, "| memoized agrees:", naive_result == memo_result)
    print("naive calls:   ", naive_calls)
    print("memoized calls:", calls)
    ```

    Same answer (184 756), but 369 511 naive calls collapse to a few
    hundred: the naive version recomputes each grid cell exponentially often,
    while the memo computes each of the $11 \times 11$ cells once.

### Exercise 17.7 — Deepest nesting ●●

Write a recursive `depth(item)` that returns how deeply lists are nested:
`depth(42)` is `0`, `depth([1, 2])` is `1`, and
`depth([1, [2, [3]], [4]])` is `3`. Hint: the depth of a list is one more
than the depth of its *deepest* child; an empty list has depth 1.

??? success "Solution"

    ```python
    def depth(item):
        if not isinstance(item, list):      # base case: not a list at all
            return 0
        if not item:                        # empty list: just itself
            return 1
        return 1 + max(depth(child) for child in item)

    print(depth(42))
    print(depth([1, 2]))
    print(depth([1, [2, [3]], [4]]))
    print(depth([[[[["deep"]]]]]))
    ```

    Prints `0`, `1`, `3`, `5`. The recursion mirrors the data's shape: each
    level of brackets adds one, and `max` picks the deepest branch.

### Exercise 17.8 — Recursion to explicit stack ●●●

This recursive function sums every number in a nested list structure:

```text
def deep_sum(item):
    if not isinstance(item, list):
        return item
    return sum(deep_sum(child) for child in item)
```

Rewrite it as `deep_sum_iterative(root)` using a plain Python list as an
explicit stack and **no recursion**, then check both agree on
`[1, [2, 3], [[4], 5, [6, [7, 8]]], 9]` (total 45). Bonus thought: does your
iterative version care about the order children are pushed? Why not?

??? success "Solution"

    ```python
    def deep_sum(item):
        if not isinstance(item, list):
            return item
        return sum(deep_sum(child) for child in item)

    def deep_sum_iterative(root):
        total = 0
        stack = [root]                  # to-do pile of unprocessed items
        while stack:
            item = stack.pop()
            if isinstance(item, list):
                stack.extend(item)      # calls become pushes
            else:
                total += item
        return total

    data = [1, [2, 3], [[4], 5, [6, [7, 8]]], 9]
    print(deep_sum(data), deep_sum_iterative(data))
    print(deep_sum(data) == deep_sum_iterative(data) == 45)
    ```

    Each recursive call becomes a push and each return becomes "pop the next
    item" — and because addition is order-independent, this conversion can
    skip the `reversed()` trick needed when output order matters.
