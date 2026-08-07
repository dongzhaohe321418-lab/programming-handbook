# Exercises

Ten problems, easiest first. For each one: attempt it honestly — on paper or
in a scratch block — *before* opening the solution. The predict-the-output
exercises are wasted if you run the code first; the whole point is to test
your mental model against the machine's.

### Exercise 2.1 — Type detective ●

Predict what each line prints, *then* run the block to check yourself.

```python
print(type(3))
print(type(3.0))
print(type("3"))
print(type(3 / 1))
print(type(3 // 1))
```

??? success "Solution"

    ```python
    print(type(3))      # <class 'int'>
    print(type(3.0))    # <class 'float'> — the decimal point decides
    print(type("3"))    # <class 'str'>   — the quotes decide
    print(type(3 / 1))  # <class 'float'> — / ALWAYS returns a float
    print(type(3 // 1)) # <class 'int'>   — // between ints stays int
    ```

    The trap is the fourth line: even though $3 / 1$ divides evenly, true
    division promotes to `float` unconditionally, so the result is `3.0`.

### Exercise 2.2 — Legal or illegal? ●

Which of these are legal Python variable names? For each illegal one, say
*why* it is rejected: `total_2`, `2_total`, `my-score`, `_hidden`, `class`,
`Bill`.

??? success "Solution"

    Legal: `total_2`, `_hidden`, and `Bill` (capital letters are legal —
    though Python style reserves `CapitalizedNames` for classes, so
    `bill` would be better). Illegal: `2_total` starts with a digit;
    `my-score` contains a hyphen, which Python reads as subtraction
    (`my - score`); `class` is a reserved word.

    ```python
    total_2 = 10
    _hidden = 20
    Bill = 30          # legal, but 'bill' is better Python style
    print(total_2 + _hidden + Bill)   # 60
    ```

### Exercise 2.3 — Predict the output: precedence ●●

Work out each result by hand using the precedence table from
[section 2.3](03-operators.md), then run to verify.

```python
print(2 + 3 * 4 ** 2)
print(20 / 5 * 2)
print(-3 ** 2)
print(2 ** 3 ** 2)
```

??? success "Solution"

    ```python
    print(2 + 3 * 4 ** 2)  # 50:  ** first (16), then * (48), then + (50)
    print(20 / 5 * 2)      # 8.0: same level, LEFT to right — (20/5)*2
    print(-3 ** 2)         # -9:  ** beats unary minus — -(3**2)
    print(2 ** 3 ** 2)     # 512: ** groups RIGHT to left — 2**(3**2) = 2**9
    ```

    Line 2 is `8.0`, not `2.0` — and it is a float, because `/` appeared
    anywhere in the chain. Lines 3 and 4 are the two classic `**` traps.

### Exercise 2.4 — The midnight movie ●●

A film starts at 21:30 and runs for 154 minutes. Using only arithmetic
(`*`, `+`, `//`, `%` — no ifs), compute the time it ends, as an hour and a
minute on a 24-hour clock. Hint: work in minutes-past-midnight, and
remember the day is $24 \times 60 = 1440$ minutes long.

??? success "Solution"

    ```python
    start = 21 * 60 + 30            # 1290 minutes past midnight
    finish = (start + 154) % 1440   # add the film, wrap past midnight
    print(finish // 60, "h", finish % 60, "min")
    ```

    This prints `0 h 4 min` — the film ends at 00:04, four minutes past
    midnight. The `% 1440` performs the wrap (1444 folds to 4), then
    `// 60` and `% 60` split the total back into hours and minutes.

### Exercise 2.5 — Digit surgery ●●

Given `n = 2026`, use only `//` and `%` to print: (a) the last digit,
(b) the last *two* digits as one number, (c) the number with its last
digit removed.

??? success "Solution"

    ```python
    n = 2026
    print(n % 10)     # 6   — remainder after dividing by 10
    print(n % 100)    # 26  — remainder after dividing by 100
    print(n // 10)    # 202 — floor division discards the last digit
    ```

    Powers of ten are digit scissors: `% 10**k` keeps the last $k$ digits,
    `// 10**k` removes them. Chain the two and you can visit every digit
    of any number.

### Exercise 2.6 — Seconds to h : m : s ●●

A stopwatch reports `10_000` seconds. Convert that to hours, minutes, and
seconds using `//` and `%`. (Check: the three parts must rebuild 10 000 via
$h \cdot 3600 + m \cdot 60 + s$.)

??? success "Solution"

    ```python
    total = 10_000
    hours = total // 3600           # how many whole hours fit?
    minutes = total % 3600 // 60    # leftover seconds, in whole minutes
    seconds = total % 60            # what remains after the minutes
    print(hours, "h", minutes, "min", seconds, "s")
    print(hours * 3600 + minutes * 60 + seconds)   # rebuild: 10000
    ```

    Output: `2 h 46 min 40 s`, and the rebuild confirms `10000`. The
    pattern — divide by the biggest unit, take the remainder, repeat — is
    the same one you used for clock time in Exercise 2.4.

### Exercise 2.7 — Spot the type error ●●

This program is *meant* to compute the cost of 3 items at \$19.99 plus a
\$1 delivery fee. Predict what actually happens — line by line, because the
bug does **not** strike where most people expect — then fix the program.

```python
# raises TypeError
price_text = "19.99"      # imagine the user typed this
quantity = 3
total = price_text * quantity + 1
print(total)
```

??? success "Solution"

    The sneaky part: `price_text * quantity` does *not* crash!
    `"19.99" * 3` is legal string *repetition*, producing
    `"19.9919.9919.99"`. The `TypeError` only strikes at `+ 1`, when
    Python refuses to add an `int` to that string. The fix is to convert
    the input before any arithmetic:

    ```python
    price_text = "19.99"      # imagine the user typed this
    quantity = 3
    total = float(price_text) * quantity + 1
    print(total)              # 60.97
    ```

    Moral of the story: convert input at the border, the moment it enters
    the program — not somewhere downstream after strings have quietly
    "worked" in ways you never intended.

### Exercise 2.8 — Binary and hex round trip ●●●

Without running any code: (a) what is `0b1100_1010` in decimal? (b) what
will `hex()` of that value return? Then write a block that verifies both
answers and also shows that `int("ff", 16)` recovers 255.

??? success "Solution"

    (a) Reading the set bits: $128 + 64 + 8 + 2 = 202$. (b) $202 = 12
    \times 16 + 10$, and 12 is `c`, 10 is `a`, so `'0xca'`.

    ```python
    n = 0b1100_1010
    print(n)              # 202
    print(hex(n))         # 0xca
    print(int("ff", 16))  # 255
    ```

    Notice the underscore grouped the binary literal into four-bit chunks
    — exactly the chunks that map one-to-one onto the hex digits `c`
    and `a`.

### Exercise 2.9 — Breaking Java's ceiling ●●●

Java's largest primitive integer is `long`, whose maximum value is
$2^{63} - 1$. Write a block that (a) prints that maximum and counts its
digits, (b) computes $3^{40}$ and shows it *exceeds* the Java maximum, and
(c) demonstrates that Python computes it exactly anyway.

??? success "Solution"

    ```python
    java_long_max = 2 ** 63 - 1
    print(java_long_max)                  # 9223372036854775807
    print(len(str(java_long_max)), "digits")   # 19 digits

    n = 3 ** 40
    print(n)                              # 12157665459056928801
    print(n > java_long_max)              # True — no Java primitive holds it
    print(len(str(n)), "digits")          # 20 digits
    ```

    $3^{40}$ is a 20-digit number, past `long`'s 19-digit ceiling — in
    Java this computation overflows (or forces you into `BigInteger`),
    while Python's arbitrary-precision `int` handles it exactly, no
    special syntax required. Converting through `str` to count digits is
    a handy trick: `len(str(n))` works for any positive integer.

### Exercise 2.10 — Marathon math ●●●

A marathon is 42.195 km, and one mile is 1.609344 km. A runner finishes in
3 h 58 min. Write a program that prints (a) the distance in miles, rounded
to 2 decimal places, and (b) the runner's average pace in minutes and
seconds per mile (whole seconds are fine — convert with `int()` before
splitting). Use the *read → convert → compute* structure from
[section 2.4](04-math-input.md), hard-coding the inputs as strings.

??? success "Solution"

    ```python
    # --- read (imagine the user typed these) ---
    km_text = "42.195"
    hours_text = "3"
    minutes_text = "58"

    # --- convert ---
    km = float(km_text)
    total_minutes = int(hours_text) * 60 + int(minutes_text)

    # --- compute ---
    miles = km / 1.609344
    pace_seconds = int(total_minutes * 60 / miles)  # seconds per mile
    print("Distance:", round(miles, 2), "miles")
    print("Pace:", pace_seconds // 60, "min", pace_seconds % 60, "s per mile")
    ```

    Output: `Distance: 26.22 miles` and `Pace: 9 min 4 s per mile`. The
    run is 14 280 seconds over 26.218… miles, or about 544.6 seconds per
    mile; `int()` truncates to 544, and the familiar `// 60` / `% 60`
    pair splits that into 9 min 4 s. Every tool here — `float()`
    conversion, promotion, `round`, floor division, modulo — came from
    this chapter.
