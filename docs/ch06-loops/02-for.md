# 6.2 for loops and ranges

Most loops in real programs are not "keep going while…" but "do this once
for *each* of these" — each number from 1 to 100, each character in a string,
each score in a list. Python's `for` loop expresses that directly, and it
removes the three chores that make `while` loops fragile: you no longer
initialize, test, or update the loop variable yourself, so the three classic
ways to get them wrong disappear with them.

## for and range: counting without the bookkeeping

Here is the lap counter from the [previous section](01-while.md), written
both ways. The `for` version hands the whole initialize–test–update job to
`range`, which produces a sequence of integers for the loop variable to walk
through.

```python
# The while version — three lines of bookkeeping
lap = 1
while lap <= 5:
    print("lap", lap)
    lap += 1

# The for version — the bookkeeping is range's job
for lap in range(1, 6):
    print("lap", lap)
```

Both halves print `lap 1` through `lap 5`. In the `for` version, `lap` is
created by the loop itself and automatically takes the next value from
`range(1, 6)` on every pass; when the values run out, the loop ends. There is
nothing left to forget.

## The three forms of range

`range` comes in three forms, each adding one more piece of control:

| form | meaning | example | produces |
| ---- | ------- | ------- | -------- |
| `range(stop)` | 0 up to, but not including, `stop` | `range(5)` | 0 1 2 3 4 |
| `range(start, stop)` | `start` up to, but not including, `stop` | `range(1, 6)` | 1 2 3 4 5 |
| `range(start, stop, step)` | as above, moving by `step` | `range(0, 20, 5)` | 0 5 10 15 |

A `range` is lazy — it computes numbers on demand rather than storing them —
so wrapping it in `list(...)` is the quickest way to *see* what it holds:

```python
print(list(range(5)))          # stop only
print(list(range(1, 6)))       # start and stop
print(list(range(0, 20, 5)))   # counting by fives
print(list(range(10, 0, -2)))  # a negative step counts down
```

Check each line against the table: the `stop` value itself never appears, and
a negative `step` walks downward. Laziness matters more than it looks:
`range(1_000_000_000)` is instant and tiny, because no billion-element list
is ever built.

## The half-open convention

Why does `range(1, 11)` mean 1 through 10 — start included, stop excluded?
This is the **half-open interval** convention, written $[1, 11)$ in
mathematics, and it is used deliberately across Python (you will meet it
again in list slicing). It has three payoffs:

- **Length by subtraction.** `range(start, stop)` contains exactly
  `stop - start` numbers — no `+ 1` corrections. `range(1, 11)` has
  $11 - 1 = 10$ values.
- **Zero-based counting fits perfectly.** `range(len(items))` produces
  exactly the valid indexes of a list of that length: `0 … len(items) - 1`.
- **Ranges chain without gaps or overlaps.** `range(0, 5)` followed by
  `range(5, 10)` covers 0–9 with the boundary value 5 appearing exactly
  once.

```python
print(list(range(1, 11)))                  # the numbers 1..10
print(len(range(1, 11)), "values")         # length is 11 - 1
first, second = range(0, 5), range(5, 10)
print(list(first), "+", list(second))      # meet at 5, no overlap
```

So when you want "1 to $n$ inclusive", write `range(1, n + 1)` — the `+ 1`
is the visible price of a convention that saves corrections everywhere else.

Here is a `for` accumulator with its trace table — same discipline as in
[6.1](01-while.md), one row per pass:

```python
total = 0
for n in range(1, 6):
    total += n
print("sum of 1..5 =", total)
```

| pass | `n` | `total` after the pass |
| ---- | --- | ---------------------- |
| 1    | 1   | 1  |
| 2    | 2   | 3  |
| 3    | 3   | 6  |
| 4    | 4   | 10 |
| 5    | 5   | 15 |

Try the same computation with an adjustable upper limit:

```yaml
# widget-config
sliders:
  n: {min: 1, max: 50, step: 1, default: 10, label: "sum 1 to n"}
```

```python
# widget — n is bound from the slider above
total = 0
for k in range(1, int(n) + 1):
    total += k
print(f"1 + 2 + ... + {int(n)} = {total}")
```

## Counting down

A negative `step` makes `range` count down — and the half-open rule still
applies, so the `stop` value is excluded at the *bottom* end:

```python
for t in range(5, 0, -1):
    print(t)
print("liftoff!")
```

`range(5, 0, -1)` produces 5, 4, 3, 2, 1 — the 0 is excluded, which is
exactly what a countdown wants. Beware the silent failure in the other
direction: `range(5, 0)` with no step is simply *empty* (you cannot climb
from 5 up to 0), so the loop body never runs and Python raises no error.

## Looping directly over strings and lists

`for` is not limited to numbers. Any sequence can be walked directly —
each pass hands you the next *element*, no index in sight. This is often
called a **for-each** loop:

```python
for ch in "loop":
    print(ch)

scores = [83, 91, 78]
total = 0
for s in scores:
    total += s
print("average:", total / len(scores))
```

The first loop visits each character of `"loop"` in order; the second folds
each score into an accumulator, averaging to 84.0 — and neither ever
mentions an index or a length. One classic stumble: you loop over the
*sequence itself*, never over its length.

```python
# raises TypeError
for i in len("abc"):    # len(...) is just the number 3
    print(i)
```

The message `'int' object is not iterable` means "3 is not a collection I
can walk through". If you truly need indexes, the fix is `range(len(...))` —
but read on for a better tool.

Java has the same two shapes, with heavier syntax — the enhanced `for` for
elements, the three-part `for` for indexes:

=== "Python"

    ```python
    scores = [83, 91, 78]
    for s in scores:                 # for-each: elements
        print(s)
    for i in range(len(scores)):     # indexed: positions
        print(i, scores[i])
    ```

=== "Java"

    ```java
    int[] scores = {83, 91, 78};
    for (int s : scores) {                       // enhanced for: elements
        System.out.println(s);
    }
    for (int i = 0; i < scores.length; i++) {    // indexed: positions
        System.out.println(i + " " + scores[i]);
    }
    ```

Java's three-part header `for (int i = 0; i < scores.length; i++)` is
initialize–test–update written on one line — the very discipline from
[6.1](01-while.md), packed into the syntax. Python's `range` plays that role
instead.

## enumerate: when you need both

Needing the element *and* its position is so common that Python has a
dedicated tool. `enumerate` wraps any sequence and yields
`(index, element)` pairs; a `start=` argument lets you count from 1 for
human-facing output.

```python
podium = ["gold", "silver", "bronze"]
for place, medal in enumerate(podium, start=1):
    print(f"{place}. {medal}")
```

This prints a numbered medal table — `1. gold` through `3. bronze` — with no
`range(len(...))` and no manual counter to keep in sync. Prefer `enumerate`
whenever you catch yourself writing `range(len(...))` just to look up
`items[i]` inside the loop.

## Choosing between while and for

The rule of thumb is one sentence: **if you can say how many passes there
will be before the loop starts, use `for`; if you can only recognise the
stopping moment when it arrives, use `while`.** Counting, tables, and
"for each element" jobs are `for` loops; sentinels, retry-until-valid, and
"until it converges" jobs are `while` loops.

One `while` shape deserves a name: the **loop-and-a-half**, where you must
*fetch* a value before you can *test* it, and process it only after the test
passes. Forcing that into a plain `while` header duplicates the fetch line;
letting the exit test sit in the middle of the body is cleaner:

```python
readings = [12, 15, 9, -999, 20]   # -999 marks the end of input
i = 0
while True:
    value = readings[i]     # fetch  (the "half" pass)
    if value == -999:
        break               # test — exit mid-body
    print("processing", value)
    i += 1
```

The loop processes 12, 15, and 9, then fetches `-999` and leaves without
processing it. Each full pass is fetch–test–process; the final pass is only
fetch–test — half a pass, hence the name.

## Java's ++ and -- 

Your Java course will be full of `i++`. Java (like C) has dedicated
**increment/decrement operators**: `i++` adds 1 to `i`, `i--` subtracts 1 —
that is what the `++` in `for (int i = 0; i < n; i++)` does. Python made a
different design choice: there is no `++`, and the idiom is `i += 1`.

=== "Python"

    ```python
    i = 0
    i += 1        # the Python idiom for "increment"
    i -= 1        # ... and for "decrement"
    print(i)
    ```

=== "Java"

    ```java
    int i = 0;
    i++;          // increment: i is now 1
    i--;          // decrement: back to 0
    System.out.println(i);
    ```

Writing `i++` in Python is a plain `SyntaxError` — Python tells you
immediately. The nastier trap is that `++i` is *legal* and does nothing you
want:

```python
i = 5
i += 1
print(i)      # 6 — the real increment
print(++i)    # still 6! ++i is +(+i): "plus plus i", not an increment
```

Python reads `++i` as two unary plus signs applied to `i`, which leave the
value unchanged — no error, no increment. If you are translating Java in
your head, translate `i++` to `i += 1` every time.

!!! warning "Common mistakes"

    - **Expecting the stop value to appear.** `range(1, 10)` ends at 9. For
      "1 to $n$ inclusive", write `range(1, n + 1)`.
    - **An empty range fails silently.** `range(5, 0)` produces nothing —
      counting down needs an explicit negative step, `range(5, 0, -1)`.
    - **Reassigning the loop variable does not steer the loop.** Setting
      `n = 99` inside `for n in range(5):` changes `n` for the rest of that
      pass only; the next pass reassigns `n` from the range as if nothing
      happened. (In a `while` loop, by contrast, changing the variable *is*
      the steering.)
    - **Looping over `len(items)` instead of the items.** `for x in
      len(items)` is a `TypeError`; loop over `items` directly, or over
      `range(len(items))` if you need indexes — or better, `enumerate`.

## Check your understanding

1. What list does `list(range(2, 11, 3))` produce, and how many elements
   does it have?

    ??? success "Answer"
        `[2, 5, 8]` — start at 2, step by 3, and stop before reaching or
        passing 11 (the next candidate, 11, is excluded by the half-open
        rule). Three elements.

2. How many times does the body of `for i in range(5, 5):` run?

    ??? success "Answer"
        Zero — `range(5, 5)` is empty, because the interval $[5, 5)$
        contains no integers. The loop is skipped without any error.

3. Rewrite this `while` loop as a single `for` loop:

    ```text
    k = 10
    while k >= 2:
        print(k)
        k -= 2
    ```

    ??? success "Answer"
        `for k in range(10, 0, -2): print(k)` — start at 10, count down by
        2, and stop before 0, producing 10, 8, 6, 4, 2. Checking the
        boundary: the last printed value must be 2, and
        `range(10, 0, -2)` indeed includes 2 and excludes 0.

4. A classmate writes `for place in enumerate(podium):` and gets tuples like
   `(0, 'gold')` printed. What happened, and what is the fix?

    ??? success "Answer"
        `enumerate` yields `(index, element)` *pairs*; with a single loop
        variable, each pair arrives whole. Unpack it into two variables —
        `for place, medal in enumerate(podium):` — and add `start=1` if the
        numbering should begin at 1.
