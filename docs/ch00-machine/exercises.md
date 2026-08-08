# Exercises

## The chapter in brief

- A computer is four kinds of hardware — CPU, RAM, storage, and input/output
  — and [0.1](01-hardware.md) is the tour of each.
- The CPU repeats one loop forever: **fetch** the next instruction,
  **decode** it, **execute** it, with a program counter tracking where it is.
- Instructions and data share the same memory — the von Neumann idea — which
  is why *a program is data too*: it can be loaded, copied, and edited like
  any other file.
- RAM is fast and volatile; storage is slow and permanent, and "saving"
  means copying from the first to the second.
- Access times form a hierarchy — register, cache, RAM, SSD, disk, network —
  where each step down is orders of magnitude slower than the one above.
- Every value is stored as **bits**: $n$ bits give $2^n$ patterns, and 8 bits
  make one byte ([0.2](02-binary.md)).
- Binary becomes decimal by adding place values; decimal becomes binary by
  repeated division by 2, reading the remainders bottom to top.
- Hexadecimal is binary for humans: one hex digit is exactly four bits, so
  one byte is always exactly two hex digits.
- Negative numbers use **two's complement**, where the top bit is worth
  $-2^{n-1}$ — and flip-every-bit-then-add-1 negates a value.
- Text is numbers too: every character has a Unicode **code point**, reached
  with `ord()` and returned with `chr()`.
- A compiler translates ahead of time and an interpreter performs the code as
  it reads it; Python quietly compiles to bytecode on every run
  ([0.3](03-programs.md)).
- **Tracing** — one row per line, one column per variable — lets you predict
  a program's output before running it.

### Key terms

| Term | What it means |
| --- | --- |
| [**CPU**](../concept-index.md#c) | The chip that executes instructions, one fetch–decode–execute cycle at a time |
| [**RAM vs storage**](../concept-index.md#r) | Fast memory that forgets at power-off, versus slow storage that remembers |
| [**von Neumann architecture**](../concept-index.md#v) | Design in which instructions and data live in the same memory |
| [**bit**](../concept-index.md#b) / [**byte**](../concept-index.md#b) | One 0-or-1 digit; a group of eight of them |
| [**binary**](../concept-index.md#b) | Base 2 — the only number system the hardware has |
| [**hexadecimal**](../concept-index.md#h) | Base 16, a compact way to write bit patterns |
| [**two's complement**](../concept-index.md#t) | The convention that lets one adder handle negative numbers |
| [**Unicode**](../concept-index.md#u) | The standard assigning a numeric code point to every character |
| [**compiler**](../concept-index.md#c) | Translates a whole program ahead of time into another form |
| [**interpreter**](../concept-index.md#i) | Reads a program and carries out its instructions as it goes |
| [**bytecode**](../concept-index.md#b) | Instructions for a virtual machine, not for real hardware |
| **tracing** | Running a program by hand, keeping a table of every variable |

Now put all of it to work. Work these in order — they are arranged easiest
first. Do the "by hand" parts on paper *before* touching the Run button; the
code is there to check you, not to replace you.

### Exercise 0.1 — Binary to decimal, by hand ●

Convert $10110_2$ to decimal using the place-value method (write $16, 8, 4,
2, 1$ under the bits and add the places holding a 1). Then verify your
answer in Python.

??? success "Solution"

    Ones sit in the 16, 4, and 2 places: $16 + 4 + 2 = 22$.

    ```python
    print(int("10110", 2))
    ```

    `int(text, 2)` reads the string as base 2 — the standard way to check
    a hand conversion.

### Exercise 0.2 — Decimal to binary, by hand ●

Convert 37 to binary by repeated division by 2, keeping a table of
quotients and remainders. Then verify with `bin()`.

??? success "Solution"

    $37 \div 2 = 18$ r **1**; $18 \div 2 = 9$ r **0**; $9 \div 2 = 4$ r
    **1**; $4 \div 2 = 2$ r **0**; $2 \div 2 = 1$ r **0**; $1 \div 2 = 0$ r
    **1**. Reading the remainders bottom-to-top: $100101_2$.

    ```python
    print(bin(37))            # 0b100101
    print(int("100101", 2))   # and back again: 37
    ```

    The remainders come out least-significant-digit first, which is why
    you read the column upwards.

### Exercise 0.3 — How many patterns? ●

Without running anything: how many different values can 1 byte hold? How
many can 2 bytes hold? A display needs to represent 500 distinct brightness
levels — how many bits per pixel does it need? Check all three answers in
Python (`bit_length()` helps with the last one).

??? success "Solution"

    $n$ bits give $2^n$ patterns: 1 byte (8 bits) gives 256, 2 bytes (16
    bits) give 65 536. For 500 levels, 8 bits (256) is too few and 9 bits
    ($2^9 = 512$) is enough.

    ```python
    print(2 ** 8)                 # 256
    print(2 ** 16)                # 65536
    print((499).bit_length())     # 9 — bits needed to count 0..499
    print(2 ** 9 >= 500)          # True
    ```

    `bit_length()` on 499 (the largest level, counting from 0) reports how
    many bits its binary form needs.

### Exercise 0.4 — Hex colour codes ●●

Web colours pack three bytes — red, green, blue, each 0–255 — into six hex
digits. Decode `#FF7F00` by hand into its three decimal components (place
values within a pair: sixteens and ones). Which colour do you expect: full
red plus half green plus no blue makes …? Then decode it in Python by
slicing the string and using `int(part, 16)`.

??? success "Solution"

    `FF` $= 15 \cdot 16 + 15 = 255$; `7F` $= 7 \cdot 16 + 15 = 127$;
    `00` $= 0$. Full red, half green, no blue: orange.

    ```python
    color = "FF7F00"
    r = int(color[0:2], 16)
    g = int(color[2:4], 16)
    b = int(color[4:6], 16)
    print("red:", r, " green:", g, " blue:", b)
    ```

    Each pair of hex digits is exactly one byte — hex is just a compact
    costume for the underlying bits.

### Exercise 0.5 — Secret message ●●

The list `[67, 80, 85, 33]` is a message stored the way all text is stored:
as Unicode code points. Decode it by hand if you can guess the range
(capital letters start at 65), then decode it with `chr()` in a loop.

??? success "Solution"

    67 is `C` (two past `A` = 65), 80 is `P`, 85 is `U`, 33 is `!` — the
    message is `CPU!`.

    ```python
    codes = [67, 80, 85, 33]
    message = ""
    for code in codes:
        message = message + chr(code)
    print(message)
    ```

    `chr()` turns a code point back into its character; `ord()` would take
    each character back to its number.

### Exercise 0.6 — Two's complement by hand ●●

Using 8 bits, work out the two's-complement pattern for $-7$ two ways:
(a) flip the bits of 7 and add 1; (b) find the bits so that the sign bit's
$-128$ plus the other place values equals $-7$. Confirm both with code.

??? success "Solution"

    (a) 7 is `00000111`; flipped: `11111000`; plus 1: `11111001`.
    (b) Check: $-128 + 64 + 32 + 16 + 8 + 1 = -7$. Both give `11111001`.

    ```python
    def to_twos_complement(value, bits=8):
        return format(value % 2 ** bits, f"0{bits}b")

    print(to_twos_complement(-7))         # 11111001
    print(-128 + 64 + 32 + 16 + 8 + 1)    # -7, reading the pattern back
    ```

    The `% 2 ** bits` trick wraps a negative number around to the pattern
    that represents it — exactly what fixed-width hardware does.

### Exercise 0.7 — Predict, then run ●●

Trace this program by hand with a variable table — one row per line, one
column per variable. Write down exactly what it will print *before*
running it.

```text
1   a = 2
2   b = a + 3
3   a = b * 2
4   b = a - b
5   print(a, b)
```

??? success "Solution"

    After line 1: `a` = 2. Line 2: `b` = 5. Line 3: `a` = 10 (`b` still 5).
    Line 4: `b` = $10 - 5 = 5$. It prints `10 5`.

    ```python
    a = 2
    b = a + 3
    a = b * 2
    b = a - b
    print(a, b)
    ```

    The trap is line 4: it uses the *new* `a` (10) and the *old* `b` (5) —
    each line sees the latest value of every variable at the moment it
    runs.

### Exercise 0.8 — Racing the interpreter ●●●

Section 0.1 timed a million additions in a Python loop. The built-in
`sum()` function does its looping *inside* the interpreter's own machine
code instead of in Python bytecode. Time both approaches on the same
500 000 numbers with `time.perf_counter()` and compare. Before running:
which do you expect to win, and why?

??? success "Solution"

    `sum()` should win comfortably — usually several times faster — because
    the Python loop pays interpreter overhead (fetch bytecode, look up
    names, box up result objects) on every single addition, while `sum()`
    pays it once for the whole call.

    ```python
    import time

    n = 500_000

    start = time.perf_counter()
    total_loop = 0
    for i in range(n):
        total_loop += i
    loop_time = time.perf_counter() - start

    start = time.perf_counter()
    total_builtin = sum(range(n))
    builtin_time = time.perf_counter() - start

    print(f"Python loop : {loop_time:.4f} s")
    print(f"sum() call  : {builtin_time:.4f} s")
    print("same answer :", total_loop == total_builtin)
    ```

    Exact times vary by machine, but the ranking should not. This is the
    speed hierarchy and the interpreter story in one experiment: the work
    is identical, only the *layer* doing it changes.
