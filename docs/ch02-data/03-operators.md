# 2.3 Operators, precedence, and modulo

Expressions are where programs actually *compute*, and Python gives you
seven arithmetic operators to build them with. Five behave exactly as school
math trained you to expect. The other two — division and modulo — are where
beginners (and Java programmers switching languages) get bitten, so this
section slows down for both, then arms you with the full precedence table so
you can read any expression with confidence.

## The seven arithmetic operators

| Operator | Name | Example | Result |
| --- | --- | --- | --- |
| `+` | addition | `17 + 5` | `22` |
| `-` | subtraction | `17 - 5` | `12` |
| `*` | multiplication | `17 * 5` | `85` |
| `/` | true division | `17 / 5` | `3.4` |
| `//` | floor division | `17 // 5` | `3` |
| `%` | modulo (remainder) | `17 % 5` | `2` |
| `**` | exponentiation | `2 ** 5` | `32` |

```python
a, b = 17, 5
print(a + b, a - b, a * b)
print(a / b)
print(a // b)
print(a % b)
print(2 ** 5)
```

The output is `22 12 85`, then `3.4`, `3`, `2`, and `32`. The first line
holds no surprises; the next three deserve their own sections.

## True division vs floor division

Python has **two** division operators because "divide" means two different
things. `/` is **true division**: the mathematically exact quotient, always
returned as a `float`. `//` is **floor division**: divide, then round *down*
to the nearest whole number.

=== "Python"

    ```python
    print(7 / 2)     # true division: 3.5
    print(7 // 2)    # floor division: 3
    print(6 / 3)     # 2.0 — / gives a float even when it divides evenly!
    ```

=== "Java"

    ```java
    System.out.println(7 / 2);      // 3   — int / int stays int in Java!
    System.out.println(7 / 2.0);    // 3.5 — only when a double is involved
    ```

This is the classic Java trap: in Java, dividing two `int`s silently throws
the remainder away, so `7 / 2` is `3` and an average like
`(a + b) / 2` can be quietly wrong. Python refuses to guess — `/` always
gives the exact answer (`3.5`), and if you *want* whole-number division you
say so explicitly with `//`.

Five expressions cover everything you need to remember:

| Expression | Result | Why |
| --- | --- | --- |
| `7 / 2` | `3.5` | true division — the exact quotient |
| `7 // 2` | `3` | floor division — divide, then round down |
| `6 / 3` | `2.0` | `/` returns a float even when the division is exact |
| `-7 // 2` | `-4` | floor rounds *down*, and $-3.5$ floored is $-4$ |
| `int(-7 / 2)` | `-3` | `int()` truncates toward zero instead |

The last two rows are the subtlety: `//` rounds **down** (toward negative
infinity), not toward zero, so for negative results the two differ:

```python
print(-7 // 2)       # -4: -3.5 floored DOWNWARD is -4
print(int(-7 / 2))   # -3: int() truncates toward zero instead
```

The output is `-4` then `-3`. Java's integer division truncates toward zero,
so Java's `-7 / 2` is `-3` — a real cross-language difference, though one
that only matters when negatives meet division.

## Modulo: the remainder operator

`a % b` gives the **remainder** after floor-dividing `a` by `b`. The two
operators are partners — for any integers (with `b` nonzero):

$$
a = b \cdot (a \mathbin{//} b) + (a \bmod b)
$$

so `17 % 5` is `2` because $17 = 5 \times 3 + 2$. Modulo looks humble but
appears constantly in real code. Here are its four everyday uses.

### Even or odd

A number is even exactly when dividing by 2 leaves remainder 0:

```python
print(10 % 2)   # 0 -> 10 is even
print(11 % 2)   # 1 -> 11 is odd
```

### Extracting digits

`% 10` peels off the last decimal digit, and `// 10` discards it — the basis
of every digit-processing trick:

```python
n = 8675309
print(n % 10)          # last digit: 9
print(n // 10)         # everything but the last digit: 867530
print(n // 10 % 10)    # second-to-last digit: 0
```

### Wrap-around (clock) arithmetic

Clocks wrap at 12 or 24; modulo *is* that wrap. What time is 7 hours after
22:00?

```python
start = 22
finish = (start + 7) % 24
print(finish)          # 5 -> 05:00, correctly wrapped past midnight
```

Plain addition says 29 o'clock; `% 24` folds it back onto the clock face,
printing `5`. The same idea handles minutes, in four moves: convert to
minutes-past-midnight, add, wrap, convert back.

```python
# What time is 90 minutes after 22:45?
start = 22 * 60 + 45              # minutes since midnight: 1365
finish = (start + 90) % (24 * 60) # wrap around the 1440-minute day
print(finish // 60, "h", finish % 60, "min")
```

This prints `0 h 15 min` — a quarter past midnight, thanks to the wrap.
Notice how `// 60` and `% 60` split the total back into hours and minutes:
quotient and remainder answering "how many whole groups?" and "what's left?"

### Cycling through a sequence

When you need position 0, 1, 2, 0, 1, 2, … forever — dealing cards, taking
turns, striping table rows — `% length` converts an ever-growing counter into
a repeating index:

```python
players = ["Ada", "Grace", "Alan"]
for turn in range(7):                    # the for line just counts 0..6 —
    print("turn", turn, "->", players[turn % 3])   # loops in Chapter 6
```

The output cycles `Ada, Grace, Alan, Ada, Grace, Alan, Ada`: turn 3 maps to
`3 % 3 = 0`, wrapping back to the first player. (Loops get their full
treatment in [Chapter 6](../ch06-loops/index.md) — here the `for` line just
repeats the `print` seven times.)

!!! info "Java corner"
    For negative operands the languages disagree: Python's result takes the
    sign of the **divisor** (`-7 % 3` is `2`), while Java's takes the sign
    of the **dividend** (`-7 % 3` is `-1`). Python's convention is the one
    you want for wrap-around: `(hour - 5) % 24` is always a valid hour, even
    when `hour - 5` is negative.

## Exponentiation and unary minus

`**` raises to a power, works with fractional exponents, and — uniquely
among the arithmetic operators — groups **right to left**:

```python
print(2 ** 10)       # 1024
print(9 ** 0.5)      # 3.0 — a square root via a fractional power
print(2 ** 3 ** 2)   # 512, NOT 64: read it as 2 ** (3 ** 2)
print((2 ** 3) ** 2) # 64 — parentheses override
```

`2 ** 3 ** 2` evaluates the *right* `**` first: $3^2 = 9$, then $2^9 = 512$.

Unary minus (the sign in `-x`) binds *less* tightly than `**`, which
produces a famous surprise:

```python
print(-2 ** 2)     # -4: parsed as -(2 ** 2)
print((-2) ** 2)   # 4:  the parentheses make the minus part of the base
```

`-2 ** 2` is `-4` because Python computes $2^2$ first and negates the
result. If you mean "negative two, squared", write `(-2) ** 2`.

## Precedence and associativity

**Precedence** decides which operator in a mixed expression goes first;
**associativity** breaks ties between operators on the same level. The full
table for this chapter's operators, highest first:

| Level | Operators | Associativity |
| --- | --- | --- |
| 1 (first) | `(...)` parentheses | — |
| 2 | `**` | right to left |
| 3 | unary `+x`, `-x` | right to left |
| 4 | `*`, `/`, `//`, `%` | left to right |
| 5 (last) | binary `+`, `-` | left to right |

(Comparisons like `<` and `==`, and `and`/`or`/`not`, sit *below* all of
these — they join the table in [Chapter 4](../ch04-branching/index.md).)

Predict these four, then run:

```python
print(2 + 3 * 4)      # * before +
print((2 + 3) * 4)    # parentheses first
print(20 / 4 * 5)     # same level -> LEFT to right
print(10 - 4 - 3)     # same level -> LEFT to right
```

The output is `14`, `20`, `25.0`, and `3`. The third line trips many
people: `/` and `*` share a level, so Python works left to right —
$(20 / 4) \times 5 = 25.0$, *not* $20 / (4 \times 5) = 1.0$. Same for the
fourth: $(10 - 4) - 3 = 3$, not $10 - (4 - 3) = 9$.

!!! tip "Parenthesize when in doubt"
    Memorizing the table is less important than this habit: **if you have
    to think twice about an expression, add parentheses.** `(bill * tip) /
    people` costs three characters and reads instantly;
    `bill * tip / people` makes every future reader re-derive the table.
    Parentheses are free. Debugging is not.

## Strings meet `+` and `*`

Two arithmetic operators moonlight for strings: `+` **concatenates**
(joins) and `*` **repeats**:

```python
first = "pro"
second = "gram"
print(first + second)          # join two strings
print("na" * 4 + " Batman!")   # repeat, then join
```

The output is `program` and `nananana Batman!`. But `+` never mixes the two
worlds — it either adds two numbers or joins two strings, and anything in
between is a type error:

```python
# raises TypeError
print("Age: " + 21)   # str + int: Python refuses to guess what you meant
```

The fix is an explicit conversion: `"Age: " + str(21)`. (Java, for the
record, *does* auto-convert here — `"Age: " + 21` is fine in Java. Python
chose explicitness.)

## Mixed-type arithmetic

When `int` and `float` meet, the result is **promoted** to `float` — the
type that can hold either without losing the fraction:

```python
print(2 + 3)          # int + int   -> int
print(2 + 3.0)        # int + float -> float
print(type(2 + 3.0))
print(True + True)    # bool is secretly a tiny int: True is 1
```

The output is `5`, `5.0`, `<class 'float'>`, and `2`. Yes, `True + True`
is `2` — `bool` is a subtype of `int` with values 1 and 0. Amusing at
parties; avoid relying on it in real code. And remember the one operator
that promotes *unconditionally*: `/` returns a `float` even for `6 / 3`.

!!! warning "Common mistakes"
    - **Bringing Java division habits.** In Python `7 / 2` is `3.5`, never
      `3`. If you want `3`, that is `7 // 2` — say it explicitly.
    - **Misreading `-2 ** 2`.** It is `-4`, because `**` outranks the unary
      minus. Write `(-2) ** 2` for `4`.
    - **Assuming same-level operators can go in any order.** `20 / 4 * 5`
      is `25.0` (left to right), not `1.0`. Only `**` groups right to left.
    - **Joining text and numbers with `+`.** `"score: " + 10` raises
      `TypeError`; convert first (`str(10)`), or use the formatting tools
      from [Chapter 3.4](../ch03-functions/04-output-formatting.md).

## Check your understanding

1. Without running: what do `17 % 5` and `5 % 17` each evaluate to?

    ??? success "Answer"
        `17 % 5` is `2` ($17 = 3 \times 5 + 2$). `5 % 17` is `5` — the
        quotient is 0, so the whole dividend is the remainder. When the
        left operand is smaller (and non-negative), `a % b` is just `a`.

2. What does `2 ** 2 ** 3` print, and why not `64`?

    ??? success "Answer"
        `256`. `**` is right-associative, so it is `2 ** (2 ** 3)`
        $= 2^8 = 256$. Getting `64` would require `(2 ** 2) ** 3`.

3. A shop is open 24 hours. A delivery arrives at 20:00 and the next one
   comes 55 hours later. Write one expression for the arrival hour.

    ??? success "Answer"
        `(20 + 55) % 24`, which is `75 % 24 = 3` — the delivery arrives at
        03:00. Modulo folds any number of hours back onto the 24-hour
        clock.

4. Predict the output of `print("ab" * 3)` and of `print("ab" + 3)`.

    ??? success "Answer"
        The first prints `ababab` — `*` repeats a string. The second raises
        `TypeError: can only concatenate str (not "int") to str` — `+`
        refuses to mix a string with a number; you would need
        `"ab" + str(3)`.
