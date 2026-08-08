# Exercises

## The chapter in brief

- Numbers have limits because a processor register is a fixed row of bits, and
  32-bit two's complement therefore tops out at $2^{31}-1$
  ([5.1](01-numeric-pitfalls.md)).
- Java's `int` wraps silently past that top, Python's `int` grows without
  limit, and NumPy's `int32` reproduces the Java behaviour — with no warning
  at all for array arithmetic.
- A `float` is an IEEE-754 double, so most decimals are rounded when stored:
  that is why `0.1 + 0.2 == 0.3` is `False`, and why computed floats need
  `math.isclose` or an explicit tolerance instead of `==`.
- Money belongs in `decimal`, built from *strings*, because `Decimal(0.1)`
  faithfully imports the float's error.
- Floats saturate to `inf` rather than wrapping, and `nan` is the one value
  not equal to itself — test it with `math.isnan`.
- `and` and `or` stop the moment the answer is known, which is what makes the
  guard idiom work: the safety check goes on the **left**
  ([5.2](02-shortcuts-gotchas.md)).
- `+=` and its family read, compute, then rebind — and Python has no `++`, so
  `++x` is legal, silent, and changes nothing.
- Java's dangling `else` binds to the nearest unmatched `if` whatever the
  indentation suggests, a bug Python cannot have because indentation *is* the
  syntax.
- Names live in frames on the **call stack**, objects live in the **heap**,
  and assignment copies the arrow rather than the object
  ([5.3](03-stack-heap.md)).
- `id(x)` and `is` reveal whether two names share one object, and the garbage
  collector — reference counting in CPython, tracing in Java — reclaims
  whatever nothing can reach.
- Python has no method overloading: a second `def` silently replaces the
  first, and default plus keyword arguments cover every variant instead
  ([5.4](04-overloading-imports.md)).
- A chain only works while each link returns an object, so never chain onto a
  mutator that returns `None` — and never write `from module import *`.

### Key terms

| Term | One-line reminder |
| --- | --- |
| [overflow](../concept-index.md#o) | a fixed-width integer wrapping past its largest value |
| [two's complement](../concept-index.md#t) | the encoding in which one step past the top lands on the most negative value |
| [floating point](../concept-index.md#f) | IEEE-754's binary approximation of a fractional number |
| [infinity and `NaN`](../concept-index.md#i) | the saturating and the meaningless results of float arithmetic |
| [short-circuit evaluation](../concept-index.md#s) | `and`/`or` skipping the right side once the answer is settled |
| guard idiom | the cheap check on the left of `and`, the risky expression on the right |
| compound assignment | `+=`, `//=`, `**=`, … — read the variable, compute, rebind |
| [call stack](../concept-index.md#c) | the tower of frames, one per function call still running |
| [frame (stack)](../concept-index.md#f) | one call's workspace: its local names plus a return bookmark |
| [heap (memory region)](../concept-index.md#h) | the pool where every object actually lives |
| [reference](../concept-index.md#r) | the arrow from a name to an object; assignment copies the arrow |
| [garbage collection](../concept-index.md#g) | automatic reclaiming of objects nothing can still reach |
| [method overloading](../concept-index.md#m) | Java's several-methods-one-name, replaced in Python by defaults |
| [keyword argument](../concept-index.md#k) | naming a parameter at the call site, as in `brew(size="small")` |

## The exercises

These exercises rehearse the chapter's reflexes: predicting what fixed-width
and floating-point arithmetic really do, exploiting short-circuits, drawing
the stack and the heap before trusting your intuition, and designing flexible
function signatures. For every *predict* exercise, commit to an answer on
paper **before** pressing Run — the gap between your prediction and the
output is where the learning lives.

### Exercise 5.1 — Predict the float comparisons (●)

Write down `True` or `False` for each printed comparison, then run the block
and check yourself.

```python
print(0.1 + 0.2 == 0.3)
print(0.5 + 0.25 == 0.75)
print(0.1 * 3 == 0.3)
print(float("nan") == float("nan"))
```

??? success "Solution"

    ```python
    print(0.1 + 0.2 == 0.3)               # False
    print(0.5 + 0.25 == 0.75)             # True
    print(0.1 * 3 == 0.3)                 # False
    print(float("nan") == float("nan"))   # False
    ```

    `0.5` and `0.25` are exact powers of two, so line 2 is exact arithmetic
    and compares `True`; `0.1`, `0.2`, and `0.3` are all rounded when stored,
    so lines 1 and 3 miss by about $10^{-17}$; and NaN is defined by IEEE-754
    to be unequal to everything, including itself.

### Exercise 5.2 — Predict the short circuits (●)

Exactly which `probe:` lines appear, and what are the three printed results?
Predict the full output, then run.

```python
def probe(name, value):
    print("probe:", name)
    return value

print(probe("A", True) or probe("B", True))
print(probe("C", False) and probe("D", True))
print(probe("E", True) and probe("F", False))
```

??? success "Solution"

    ```python
    def probe(name, value):
        print("probe:", name)
        return value

    print(probe("A", True) or probe("B", True))    # probe: A / True
    print(probe("C", False) and probe("D", True))  # probe: C / False
    print(probe("E", True) and probe("F", False))  # probe: E, probe: F / False
    ```

    `B` is skipped because `or` already has `True`; `D` is skipped because
    `and` already has `False`; only `F` actually runs its right side, because
    `E` was `True` and `and` still needed the answer.

### Exercise 5.3 — Fix the overflow (●●)

This population dashboard doubles each region's population as a projection —
and prints nonsense. Explain what happened, then fix the code so the
projection is correct. (Keep using NumPy.)

```python
import numpy as np

pop = np.array([2_100_000_000, 1_400_000_000], dtype=np.int32)
print(pop * 2)     # negative populations?!
```

??? success "Solution"

    ```python
    import numpy as np

    pop = np.array([2_100_000_000, 1_400_000_000], dtype=np.int64)
    print(pop * 2)     # [4200000000 2800000000]
    ```

    `np.int32` holds at most $2^{31}-1 \approx 2.147$ billion, so doubling
    2.1 billion wrapped past the top into negative territory — silently,
    because NumPy does not check array integer arithmetic. Choosing the wider
    `np.int64` box (max $\approx 9.2 \times 10^{18}$) makes the products fit.

### Exercise 5.4 — The missing cent (●●)

First predict what this receipt code prints. Then rewrite it with the
`decimal` module so the comparison is `True` and the total prints as `0.30`.

```python
subtotal = 0.10 + 0.20
print(subtotal)
print(subtotal == 0.30)
```

??? success "Solution"

    ```python
    from decimal import Decimal

    subtotal = Decimal("0.10") + Decimal("0.20")
    print(subtotal)                     # 0.30
    print(subtotal == Decimal("0.30"))  # True
    ```

    The float version prints `0.30000000000000004` and `False`, because
    `0.1` and `0.2` are rounded when stored in binary. `Decimal` works in
    base ten, so cents add exactly — just remember to build Decimals from
    *strings*, never from the already-rounded floats.

### Exercise 5.5 — Trace the stack on paper (●●)

Three functions call each other. On paper, write the complete output in
order — one line per `print` — by tracking frames being created and
destroyed. Only then run the block to check.

```python
def c():
    print("start c")
    print("end c")

def b():
    print("start b")
    c()
    print("end b")

def a():
    print("start a")
    b()
    print("end a")

a()
print("done")
```

??? success "Solution"

    ```python
    def c():
        print("start c")
        print("end c")

    def b():
        print("start b")
        c()
        print("end b")

    def a():
        print("start a")
        b()
        print("end a")

    a()
    print("done")
    # start a / start b / start c / end c / end b / end a / done
    ```

    The "start" lines appear as frames stack up (`a`, then `b`, then `c`),
    and the "end" lines appear in *reverse* order as the frames are destroyed
    newest-first — the call stack is last in, first out.

### Exercise 5.6 — The stuck counter (●●)

A Java-trained friend wrote this and swears the loop runs. Predict what it
prints, explain the bug in one sentence, and fix it.

```python
count = 0
for letter in "abc":
    ++count
print(count)
```

??? success "Solution"

    ```python
    count = 0
    for letter in "abc":
        count += 1
    print(count)    # 3
    ```

    The original prints `0`: Python has no `++` operator, so `++count` is
    parsed as `+(+count)` — unary plus twice — which computes `count`'s value
    and throws it away, three times. `count += 1` performs the real
    increment.

### Exercise 5.7 — Write the guard (●●)

A class-average checker crashes when no scores have been entered yet. Using
the short-circuit guard idiom (a single `if` with `and`, no nesting), make it
print `honour roll` only when `n != 0` *and* the average `total / n` exceeds
90 — and never crash when `n` is 0. Test with both pairs of values given in
the comments.

```text
total = 0        # also try: total = 380
n = 0            # also try: n = 4

if ...:          # your one-line condition here
    print("honour roll")
else:
    print("not (yet) on the honour roll")
```

??? success "Solution"

    ```python
    total = 380      # also try: total = 0
    n = 4            # also try: n = 0

    if n != 0 and total / n > 90:
        print("honour roll")
    else:
        print("not (yet) on the honour roll")
    ```

    With `n = 4` the guard passes and `380 / 4 = 95.0 > 90` prints
    `honour roll`; with `n = 0` the left side is `False`, `and`
    short-circuits, and `total / n` never runs — no `ZeroDivisionError`.
    The guard must be on the *left*: swapping the two conditions reintroduces
    the crash.

### Exercise 5.8 — Predict the aliases (●●●)

Draw the stack-and-heap arrow diagram for this code (three names, how many
list objects?), predict all five printed lines, then run it.

```python
a = [10, 20]
b = a
c = [10, 20]

print(a is b)
print(a is c)
print(a == c)

b.append(30)
print(a)
print(c)
```

??? success "Solution"

    ```python
    a = [10, 20]
    b = a               # copies the arrow: a and b share ONE list
    c = [10, 20]        # a second, look-alike list object

    print(a is b)       # True
    print(a is c)       # False
    print(a == c)       # True  — equal contents, different objects
    b.append(30)
    print(a)            # [10, 20, 30] — a sees b's change: same object!
    print(c)            # [10, 20]     — the look-alike is untouched
    ```

    There are only *two* list objects on the heap. `b = a` copied a
    reference, so `b.append(30)` modified the single list both names point
    at; `c` was built by its own list literal, so it lives — and stays —
    apart. (`a == c` is `True` only until the append changes `a`'s contents.)

### Exercise 5.9 — Design a keyword-argument API (●●●)

A Java library offers three overloads for ordering tickets:

```java
String order(String name)                          // 1 standard ticket
String order(String name, int qty)                 // qty standard tickets
String order(String name, int qty, boolean vip)    // qty VIP tickets
```

Design a *single* Python function `order(...)` with defaults so that all
three call styles below work, then add the fourth call — impossible to
express cleanly with Java's overloads — where a caller upgrades to VIP
*without* restating the quantity.

```text
order("Ada")                  → "1 standard ticket(s) for Ada"
order("Ada", 3)               → "3 standard ticket(s) for Ada"
order("Ada", 2, True)         → "2 VIP ticket(s) for Ada"
order("Ada", vip=True)        → "1 VIP ticket(s) for Ada"
```

??? success "Solution"

    ```python
    def order(name, qty=1, vip=False):
        kind = "VIP" if vip else "standard"
        return f"{qty} {kind} ticket(s) for {name}"

    print(order("Ada"))
    print(order("Ada", 3))
    print(order("Ada", 2, True))
    print(order("Ada", vip=True))
    ```

    One `def` with two defaults replaces all three overloads, and the
    keyword call `order("Ada", vip=True)` skips the middle parameter
    entirely — Java would need yet another overload (`order(String,
    boolean)`) for that, and it would clash confusingly with the existing
    two-argument version.
