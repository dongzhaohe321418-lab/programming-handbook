# 5.1 Overflow and floating-point pitfalls

A calculator that quietly turns two billion into a negative number, or insists
that $0.1 + 0.2$ is not $0.3$, sounds broken. Yet every mainstream computer
does both, on purpose, billions of times per second — and programs that ignore
this have crashed rockets and mispriced bank accounts. This section shows you
exactly where the limits are, why the hardware imposes them, and the small set
of habits (tolerant comparisons, the `decimal` module, wider integer types)
that keep your programs on the right side of them.

## Why numbers have limits at all

Inside the processor, a number lives in a **register**: a row of physical
circuits, each holding one bit. The row has a fixed length — typically 32 or
64 bits — because the adder and multiplier circuits are literally wired for
that many inputs.

Fixed width is what makes arithmetic so fast, and it buys two things at once:

- **Every operation costs the same.** Adding two 64-bit numbers takes about
  one clock cycle, no matter what the numbers are.
- **Storage is predictable.** A million of them in a row occupy exactly
  8 million bytes, so the machine always knows where number 500,001 starts.

The price of a fixed-size box is a biggest value that fits in it. With 32 bits
and the usual **two's complement** encoding (met in
[Chapter 2's number systems](../ch02-data/02-number-systems.md)), the range is

$$-2^{31} \;\le\; n \;\le\; 2^{31}-1, \qquad 2^{31}-1 = 2{,}147{,}483{,}647.$$

What happens one step past the top? The bits carry over like a car odometer
rolling past 999999 — and in two's complement, the pattern just past the
largest positive value *is* the most negative value. That wrap-around is
called **integer overflow**.

## Integer overflow: Java wraps, Python grows

Java's `int` is exactly this 32-bit box. Push it past the top and it wraps —
no error, no warning, just a wrong answer:

=== "Java"

    ```java
    int big = Integer.MAX_VALUE;        // 2147483647, i.e. 2^31 - 1
    System.out.println(big + 1);        // prints -2147483648  (wrapped!)
    System.out.println(2_000_000_000 + 2_000_000_000);  // prints -294967296
    ```

=== "Python"

    ```python
    big = 2**31 - 1
    print(big + 1)                      # 2147483648 — no drama
    print(2_000_000_000 + 2_000_000_000)
    print(2**100)                       # ints grow as large as memory allows
    ```

Run the Python version: `big + 1` is simply `2147483648`. Python's `int` is
not a fixed-size register value. It is an object that grows extra digits as
needed, so **Python integers never overflow** — `2**100` prints all 31 digits
of $2^{100}$ happily.

The trade-off is speed: flexible ints cost more memory and more time per
operation than raw hardware integers. Java made the opposite trade, which is
why its `int` is fast *and* dangerous.

!!! info "Java corner"
    Java's `long` is the same idea with 64 bits: it wraps at
    $2^{63}-1 \approx 9.2 \times 10^{18}$. Bigger range, same cliff. For truly
    unbounded integers Java offers a library class, `java.math.BigInteger` —
    essentially what Python gives you by default.

## Watch real overflow happen — NumPy's fixed-width integers

You do not need Java to see overflow. The **NumPy** library (the standard tool
for numerical computing in Python, which you will meet properly later) stores
numbers in fixed-width hardware types just like Java and C — including
`np.int32`, a faithful replica of Java's `int`. So we can watch the odometer
roll over right here in the browser:

```python
import numpy as np

MAX = np.iinfo(np.int32).max          # ask NumPy for int32's largest value
print("largest int32:", MAX)

a = np.int32(MAX)
b = a + np.int32(1)                   # one step past the top...
print("MAX + 1 =", b)
```

The printed result is:

```text
largest int32: 2147483647
MAX + 1 = -2147483648
```

and above it (at least the first time you run the block) NumPy shows a
warning ending in:

```text
RuntimeWarning: overflow encountered in scalar add
```

That warning is NumPy being unusually polite: it noticed the single-value
("scalar") addition wrapping and told you. The *value* is still the wrapped
one — the warning changes nothing about the arithmetic. Now try the same
overflow inside an array:

```python
import numpy as np

followers = np.array([2_000_000_000, 5, 42], dtype=np.int32)
doubled = followers * 2
print(doubled)
```

Output:

```text
[-294967296         10         84]
```

The first account's followers doubled to four billion, which does not fit in
32 bits, so the value wrapped to a negative number — and notice: **no warning
at all** this time. For speed, NumPy does not
check array arithmetic for integer overflow — which is exactly how Java and C
behave all the time. The fix is to choose a wider box up front, for example
`dtype=np.int64`, or a floating-point type when approximation is acceptable.

!!! note "The rule of thumb"
    Plain Python `int`: safe, never overflows. NumPy/Java/C integers: fast,
    fixed-width, and they *wrap silently* — so when values might approach
    $2^{31} \approx 2.1$ billion, pick a wider type before you compute, not
    after the bug report.

## Floating-point: the honest truth about 0.1

Fractional numbers use a different fixed-width format: **IEEE-754 double
precision**, the near-universal standard behind Python's `float`, Java's
`double`, and your GPU. A double spends its 64 bits like this:

| Field    | Bits | Its job                            |
| -------- | ---- | ---------------------------------- |
| sign     | 1    | positive or negative               |
| exponent | 11   | which power of two to scale by     |
| fraction | 52   | the digits of the number itself    |

Together they store a number as *binary* scientific notation,
$\pm\, 1.\text{fraction} \times 2^{\text{exponent}}$.
[Section 23.5.3](../ch23b-architecture/03-arithmetic.md) opens this format at the
bit level — a runnable inspector that splits any float into its sign, exponent,
and fraction and rebuilds it — so you can watch exactly where the rounding below
gets baked into the hardware.

Sixty-four bits can represent only finitely many numbers, so almost every
decimal you type gets rounded to the *nearest representable* double. That
single fact explains the most famous line in programming:

```python
print(0.1 + 0.2)
print(0.1 + 0.2 == 0.3)
```

Output:

```text
0.30000000000000004
False
```

Why can't 64 bits hold something as tame as $0.1$? Because $0.1 = 1/10$, and
$10 = 2 \times 5$. In binary, a fraction terminates only if its denominator is
a power of 2 — the factor of 5 makes $0.1$ an *infinite repeating* binary
fraction, exactly like $1/3 = 0.3333\ldots$ in decimal. The machine keeps the
first 52 fraction bits and rounds. You can see the rounded values by asking
for more digits than Python normally shows:

```python
print(f"{0.1:.20f}")
print(f"{0.2:.20f}")
print(f"{0.3:.20f}")
```

Output:

```text
0.10000000000000000555
0.20000000000000001110
0.29999999999999998890
```

So the `0.1` you typed is really a hair *above* $0.1$, and `0.3` is a hair
*below* $0.3$. Add the two slightly-large numbers and you land just above the
slightly-small one — hence `False`. Neither value is wrong by more than about
$10^{-17}$; doubles carry roughly 15–17 significant decimal digits. The errors
are tiny, but they *accumulate*:

```python
total = 0.0
for _ in range(10):
    total += 0.1
print(total)
print(total == 1.0)
```

Ten dimes make `0.9999999999999999`, not a dollar. Numbers that are sums of
powers of two — `0.5`, `0.25`, `0.75`, `3.375` — are stored exactly, which is
why floating-point bugs feel random: some decimals are perfect, most are not.

## Never compare floats with ==

The lesson is a habit, not a fix: **never use `==` between computed floats.**
Ask instead whether two values are *close enough*, using either the standard
tool `math.isclose` or an explicit tolerance:

```python
import math

a = 0.1 + 0.2

print(math.isclose(a, 0.3))          # True — within relative tolerance 1e-9
print(abs(a - 0.3) < 1e-9)           # True — hand-rolled absolute tolerance
```

`math.isclose(a, b)` checks that the *relative* difference is below
$10^{-9}$ by default (about 9 matching significant digits), which adapts
sensibly whether your values are near $10^{-6}$ or $10^{12}$. The
`abs(a - b) < tol` form is the simple absolute version — fine when you know
the scale of your numbers, and worth writing at least once so `isclose` is
never magic to you.

## Money needs `decimal`

Binary floats and money are a famously bad match: customers notice a missing
cent. Python's standard-library `decimal` module stores numbers in base ten
with exact decimal digits, so cents behave like cents:

```python
from decimal import Decimal

subtotal = Decimal("0.10") + Decimal("0.20")
print(subtotal)
print(subtotal == Decimal("0.30"))

# And here is why you build Decimals from STRINGS, not floats:
print(Decimal(0.1))
```

Output:

```text
0.30
True
0.1000000000000000055511151231257827021181583404541015625
```

That last line is the exact value of the double `0.1`. `Decimal(0.1)`
faithfully imports the float's error, while `Decimal("0.1")` means the decimal
you actually wrote.

There are two other industrial-strength options worth knowing. Keep money as
an integer number of *cents* and format it only on output. And if you are in
Java, `BigDecimal` does the same job as Python's `decimal`.

The cost of `decimal` is speed — hardware has no decimal circuits — which is
why it is the exception for money and measurement, not the default for all
arithmetic.

## Infinity and NaN

Two more citizens of IEEE-754 will eventually visit your programs. Where fixed
integers wrap, floats that grow too large (beyond about
$1.8 \times 10^{308}$) *saturate* to a special value, **infinity** — and some
operations produce **NaN**, "Not a Number":

```python
import math

huge = 1e308 * 10
print(huge)                 # inf — float overflow does NOT wrap or crash

weird = huge - huge         # infinity minus infinity has no sensible value
print(weird)                # nan

nan = float("nan")
print(nan == nan)           # False (!)
print(nan != nan)           # True  (!!)
print(math.isnan(nan))      # True — the correct test
```

Output:

```text
inf
nan
False
True
True
```

`inf` behaves like a number bigger than everything, which makes
`best = float("inf")` a handy starting value when hunting for a minimum. `nan`
is stranger: it is the **only value in Python that is not equal to itself**,
by decree of the IEEE-754 standard (any comparison with NaN answers "false",
signalling that the value is meaningless). So `x == float("nan")` can never
succeed — use `math.isnan(x)`.

So Python offers three numeric personalities, and now you can name all three:

| Number type | At the limit it … | So watch for … |
| --- | --- | --- |
| plain `int` | **grows** — it never overflows | more memory and time per operation than a hardware int |
| NumPy / Java / C integer | **wraps** silently (a scalar add may warn) | choosing a wider type *before* the values get big |
| `float` (IEEE-754 double) | **saturates** to `inf` | the quiet rounding of nearly every decimal below that |

!!! warning "Common mistakes"
    - **Comparing computed floats with `==`** — `0.1 + 0.2 == 0.3` is `False`.
      Use `math.isclose(a, b)` or `abs(a - b) < tol`.
    - **Building decimals from floats** — `Decimal(0.1)` imports the binary
      rounding error. Always `Decimal("0.1")`, from a string.
    - **Assuming "Python never overflows" covers NumPy** — `np.int32`
      arithmetic wraps just like Java's `int`, and *array* operations do not
      even warn. Choose `np.int64` (or a float dtype) when values can be large.
    - **Testing for NaN with `==`** — `x == float("nan")` is always `False`.
      Use `math.isnan(x)`.

## Check your understanding

1. Java prints `Integer.MAX_VALUE + 1` as `-2147483648`. In one sentence, why
   that exact number?

    ??? success "Answer"
        A 32-bit two's-complement integer wraps around like an odometer: one
        step past the largest positive value ($2^{31}-1$) carries over to the
        bit pattern of the most negative value, $-2^{31} = -2147483648$.

2. `0.5 + 0.25 == 0.75` is `True`, yet `0.1 + 0.2 == 0.3` is `False`. What is
   special about the first three numbers?

    ??? success "Answer"
        $0.5$, $0.25$, and $0.75$ are sums of powers of two
        ($2^{-1}$, $2^{-2}$, $2^{-1}+2^{-2}$), so they are stored *exactly* in
        binary floating point, and the arithmetic is exact. $0.1$, $0.2$, and
        $0.3$ have a factor of 5 in their denominators, so each is rounded —
        and the rounding errors don't cancel.

3. Your program tracks video view counts in a NumPy `int32` array, and a viral
   video just passed 2.2 billion views. What do you expect to see, and what is
   the fix?

    ??? success "Answer"
        The count wraps to a large *negative* number — silently, since NumPy
        does not warn for array integer overflow. Fix: store the array with a
        wider type, e.g. `dtype=np.int64`, before the values grow.

4. Why does `float("nan") == float("nan")` print `False`?

    ??? success "Answer"
        IEEE-754 defines NaN as unequal to everything, *including itself* —
        it marks a meaningless result, and two meaningless results are not
        the same value. Test with `math.isnan(x)` instead.
