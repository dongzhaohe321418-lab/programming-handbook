# 2.2 Number systems

[Chapter 0.2](../ch00-machine/02-binary.md) showed that a computer stores
everything as bits. This section makes that idea practical: how to *write*
binary and hexadecimal numbers directly in Python code, how to convert
between bases, and — a genuine Python superpower — why Python integers never
run out of room while Java's can overflow.

## One number, three costumes

`42`, `0b101010`, and `0x2A` are three ways of *writing* the same integer.
The `0b` prefix means "the digits that follow are **binary** (base 2)"; `0x`
means **hexadecimal** (base 16, digits `0–9` then `a–f`). Once Python has
read the literal, the resulting object is identical — an `int` is an `int`,
no matter which costume it wore in the source code:

```python
print(42)          # decimal (base 10)
print(0b101010)    # binary  (base 2):  32 + 8 + 2
print(0x2A)        # hex     (base 16): 2*16 + 10
print(0b101010 == 0x2A == 42)
```

All three print `42`, and the comparison prints `True`. Notice that `print`
always shows integers in decimal — the base was a property of the *source
code text*, never of the value. (There is also an octal prefix `0o` for
base 8, which you will rarely need.)

Hexadecimal earns its keep as a *compact abbreviation of binary*: one hex
digit is exactly four bits, so `0x2A` unpacks digit-by-digit to
`0010 1010`. That is why memory addresses, colour codes like `#FF8800`, and
error codes are conventionally written in hex.

## Converting between bases

Two built-in functions convert an integer *to* a string in another base, and
`int()` with a second argument converts *back*:

```python
print(bin(42))            # int -> binary string
print(hex(42))            # int -> hex string
print(int("101010", 2))   # binary string -> int
print(int("2a", 16))      # hex string -> int
```

The output:

```text
0b101010
0x2a
42
42
```

Look carefully at the first two lines: `bin()` and `hex()` return
**strings** (note they print with the prefix, and `type(bin(42))` is
`str`). They are for *displaying* a value in another base; the moment you
want arithmetic, you want the plain `int`.

Try the round trip yourself with the slider:

```yaml
# widget-config
sliders:
  n: {min: 0, max: 255, step: 1, default: 42, label: "number"}
```

```python
# widget — n is bound from the slider above
n = int(n)
print("decimal:", n)
print("binary :", bin(n))
print("hex    :", hex(n))
```

## Underscores make big literals readable

Since Python 3.6 you may drop underscores into any numeric literal as visual
grouping — Python ignores them completely:

```python
population = 8_100_000_000        # eight billion, readable at a glance
mask = 0b1111_0000                # group binary digits in fours
budget = 1_000_000
print(population)
print(mask)
print(budget)
```

The output is `8100000000`, `240`, and `1000000` — the underscores exist
only in the source code, never in the value. Use them for anything past
about five digits; `1000000000` and `100000000` are one squint apart, while
`1_000_000_000` and `100_000_000` are unmistakable.

## How big can an integer get?

Here Python and Java part ways completely. Java gives you a menu of
fixed-size integer types — each one a fixed number of bits, and therefore a
fixed range:

| Java type | Size | Range |
| --- | --- | --- |
| `byte` | 8 bits | $-128$ to $127$ |
| `short` | 16 bits | $-32{,}768$ to $32{,}767$ |
| `int` | 32 bits | $-2{,}147{,}483{,}648$ to $2{,}147{,}483{,}647$ (about $\pm 2.1$ billion) |
| `long` | 64 bits | about $\pm 9.2 \times 10^{18}$ |

=== "Python"

    ```python
    big = 2 ** 100                     # no special type needed
    print(big)
    print(len(str(big)), "digits")
    ```

=== "Java"

    ```java
    int  a = 2147483647;               // the largest int — one more overflows
    long b = 9223372036854775807L;     // largest long; note the trailing L
    // long c = 2^100  →  impossible: no primitive type is big enough
    ```

Python has exactly **one** integer type, `int`, with **arbitrary
precision**: it grows to however many bits the value needs. The Python tab
prints

```text
1267650600228229401496703205376
31 digits
```

— a 31-digit number, computed exactly, with no ceremony. In Java, $2^{100}$
does not fit in *any* primitive type; you would have to reach for the
`BigInteger` library class.

!!! info "Java corner"
    What happens when a Java `int` exceeds its 32 bits? It silently
    **overflows** and wraps around: `2147483647 + 1` evaluates to
    `-2147483648`, with no error and no warning. This is a real and famous
    source of bugs, and it is why
    [Chapter 5.1](../ch05-under-the-hood/01-numeric-pitfalls.md) treats
    overflow in depth. Python's `int` cannot overflow — one less thing to
    fear.

## Floats are approximations (a preview)

Integers in Python are exact at any size — but `float` is a different
animal. A float is stored in 64 bits, base **two**, and most decimal
fractions (like $0.1$) have no exact base-two representation, just as
$\tfrac{1}{3}$ has no exact decimal one. The stored value is the nearest
representable approximation:

```python
print(0.1 + 0.2)
```

This prints `0.30000000000000004` — not `0.3`. Nothing is broken: each of
`0.1` and `0.2` was already a hair off before the addition even happened.
For now, remember two habits: expect tiny errors in float arithmetic, and
never test floats with `==`. The full story — and the right way to compare
floats — is in
[Chapter 5.1](../ch05-under-the-hood/01-numeric-pitfalls.md).

!!! warning "Common mistakes"
    - **Invalid digits for the base.** `0b102` is a `SyntaxError` — binary
      literals may contain only `0` and `1`. Likewise `0x` digits stop at
      `f`.
    - **Forgetting the base argument.** `int("2a")` raises `ValueError`;
      you must say `int("2a", 16)` so Python knows the string is hex.
    - **Doing math on `bin()`/`hex()` output.** They return *strings*:
      `bin(4) + 1` raises `TypeError`. Convert back with `int(s, 2)` first.
    - **Trusting float digits too far.** `0.1 + 0.2 == 0.3` is `False`.
      With floats, use rounding or a tolerance — never exact equality.

## Check your understanding

1. Without running code: what decimal value is `0xFF`? And `0b1000`?

    ??? success "Answer"
        `0xFF` is $15 \times 16 + 15 = 255$ (the largest value of one
        byte). `0b1000` is $2^3 = 8$.

2. What does `bin(10)` return, and what is its type?

    ??? success "Answer"
        The **string** `'0b1010'`, of type `str`. `bin()` is a display
        helper — it does not produce a number.

3. A friend's Java program crashes with weird negative numbers after a
   counter passes two billion. What happened, and would Python have the
   same problem?

    ??? success "Answer"
        The counter was a 32-bit Java `int`, which overflowed past
        $2{,}147{,}483{,}647$ and wrapped around to negative values. Python
        would not: its `int` is arbitrary-precision and simply grows.
        (A Java fix is to use `long` — or `BigInteger` for truly huge
        values.)

4. Is `1_0_0` a legal Python literal? If so, what is its value?

    ??? success "Answer"
        Legal (if eccentric): underscores may appear between any two
        digits, so `1_0_0` is just `100`. Style-wise, use underscores in
        groups of three (`1_000_000`) so they help rather than confuse.
