# Exercises

Eight workouts for Chapter 6, easiest first. Write your own version before
opening any solution — loops are learned through the fingers, not the eyes.
Difficulty: ● warm-up, ●● standard, ●●● stretch.

### Exercise 6.1 — Countdown clock (●)

Using a `while` loop, print the numbers 5 down to 1, one per line, then
print `Liftoff!`. Identify your initialize, test, and update lines before
you run it.

??? success "Solution"

    ```python
    t = 5                # initialize
    while t > 0:         # test
        print(t)
        t -= 1           # update
    print("Liftoff!")
    ```

    The three-part discipline in its purest form: `t` starts at 5, every
    pass moves it down, and the test fails exactly when the count is done —
    leaving `t == 0` after the loop.

### Exercise 6.2 — FizzBuzz with dignity (●●)

The most famous loop exercise in the world. For each number from 1 to 30:
print `Fizz` if it is divisible by 3, `Buzz` if divisible by 5,
`FizzBuzz` if divisible by both, and the number itself otherwise. The
dignity is in the details: handle the "both" case cleanly, without
repeating tests.

??? success "Solution"

    ```python
    for n in range(1, 31):
        if n % 15 == 0:        # divisible by both 3 and 5
            print("FizzBuzz")
        elif n % 3 == 0:
            print("Fizz")
        elif n % 5 == 0:
            print("Buzz")
        else:
            print(n)
    ```

    The "both" test must come *first*: a number divisible by 15 is also
    divisible by 3, so testing `n % 3` first would print `Fizz` and never
    reach `FizzBuzz`. (An elegant alternative builds a string: append
    `"Fizz"` if `n % 3 == 0`, append `"Buzz"` if `n % 5 == 0`, then
    `print(word or n)` — no combined test at all.)

### Exercise 6.3 — Digit sum (●●)

Compute the sum of the digits of 90210 (expected: $9 + 0 + 2 + 1 + 0 =
12$) using a `while` loop, `% 10` to read the last digit, and `// 10` to
remove it. No strings allowed.

??? success "Solution"

    ```python
    n = 90210
    total = 0
    while n > 0:
        total += n % 10    # read the last digit
        n //= 10           # chop it off
    print("digit sum:", total)
    ```

    An accumulator loop whose update *shrinks the number* instead of
    growing a counter: `n` steps through 90210, 9021, 902, 90, 9, 0 while
    the digits 0, 1, 2, 0, 9 fold into `total`. The loop ends when the
    number is used up.

### Exercise 6.4 — Sentinel average (●●)

The list below simulates temperature readings typed in one at a time,
where $-273.15$ (absolute zero — impossible as a reading) is the sentinel
meaning "no more data". Compute and print the count and the average of the
readings *before* the sentinel, formatted to 2 decimal places. Your loop
must not touch anything after the sentinel.

```text
readings = [18.5, 21.0, 19.5, -273.15, 25.0]
```

??? success "Solution"

    ```python
    readings = [18.5, 21.0, 19.5, -273.15, 25.0]   # imagine these were typed in
    i = 0
    total = 0.0
    count = 0
    while readings[i] != -273.15:
        total += readings[i]
        count += 1
        i += 1
    print(f"{count} readings, average {total / count:.2f}")
    ```

    Prints `3 readings, average 19.67`. The test runs *before* each value
    is processed, so the sentinel is never added — and the `25.0` after it
    is never reached. A good sentinel, like $-273.15\,^\circ$C, is a value
    that could never be genuine data.

### Exercise 6.5 — Predict the output (●●)

Read this nested loop and **write down its exact output** — every number,
every line break — *before* pressing Run. Then run it and grade your
prediction.

```python
for i in range(1, 4):
    for j in range(1, 4):
        if j > i:
            break
        print(i * j, end=" ")
    print()
```

??? success "Solution"

    The output is:

    ```text
    1 
    2 4 
    3 6 9 
    ```

    For each `i`, the inner loop runs while `j <= i` and then `break`
    ends the row: when `i = 1`, only `j = 1` prints (giving 1); when
    `i = 2`, `j` = 1, 2 print (2 and 4); when `i = 3`, all of `j` = 1, 2,
    3 print (3, 6, 9). The bare `print()` still runs after each `break`
    because it belongs to the *outer* loop's body — `break` only exits the
    inner loop.

### Exercise 6.6 — Prime tester (●●)

Write a function `is_prime(n)` that returns `True` when `n` is prime
(divisible only by 1 and itself, with $n \ge 2$). Use a loop that tries
divisors and stops early — either with a found-flag, a `return`, or
loop-`else`. Test it on 2, 9, 17, 91, 97, and 1. (Hint: 91 looks prime.
It is not.)

??? success "Solution"

    ```python
    def is_prime(n):
        if n < 2:
            return False
        d = 2
        while d * d <= n:      # only need divisors up to sqrt(n)
            if n % d == 0:
                return False   # found a divisor — leave immediately
            d += 1
        return True            # loop exhausted: no divisor exists

    for n in [2, 9, 17, 91, 97, 1]:
        print(n, is_prime(n))
    ```

    The early `return False` is the function-return pattern from
    [6.3](03-nested-break-continue.md): the moment a divisor appears, the
    answer is settled. Testing only while $d^2 \le n$ works because
    divisors come in pairs $(d, n/d)$, one of which is always $\le
    \sqrt{n}$ — that is why `is_prime(91)` finds $7 \times 13$ quickly and
    prints `False`.

### Exercise 6.7 — Star pyramid (●●)

Print a centered pyramid of stars with 4 rows using nested loops: row $r$
needs $4 - r$ spaces followed by $2r - 1$ stars. Expected output:

```text
   *
  ***
 *****
*******
```

??? success "Solution"

    ```python
    n = 4
    for row in range(1, n + 1):
        for _ in range(n - row):        # leading spaces
            print(" ", end="")
        for _ in range(2 * row - 1):    # stars
            print("*", end="")
        print()                          # end the row
    ```

    Two inner loops per row, both driven by `row`: the space count falls
    3, 2, 1, 0 while the star count climbs 1, 3, 5, 7. Checking the
    widths: the bottom row is $2 \times 4 - 1 = 7$ stars, and every row is
    centered because spaces + stars/2 stays aligned. The one-line Python
    shortcut is `print(" " * (n - row) + "*" * (2 * row - 1))`.

### Exercise 6.8 — Permission bits (●●●)

A tiny access-control system stores each user's rights in one integer:
`READ = 0b100`, `WRITE = 0b010`, `EXECUTE = 0b001`. Starting from

```text
staff = {"ana": 0b110, "ben": 0b101, "cai": 0b000}
```

write a program that (a) defines a `describe(perms)` function returning an
`rwx`-style string, (b) grants every user `READ`, (c) revokes `ana`'s
`WRITE`, and (d) prints each user's rights before and after, one line per
user. Expected final rights: ana `r--`, ben `r-x`, cai `r--`.

??? success "Solution"

    ```python
    READ, WRITE, EXECUTE = 0b100, 0b010, 0b001

    def describe(perms):
        letters = "r" if perms & READ else "-"
        letters += "w" if perms & WRITE else "-"
        letters += "x" if perms & EXECUTE else "-"
        return letters

    staff = {"ana": 0b110, "ben": 0b101, "cai": 0b000}

    for name, perms in staff.items():
        print(f"before  {name}: {describe(perms)}")

    for name in staff:
        staff[name] |= READ        # (b) grant READ to everyone
    staff["ana"] &= ~WRITE         # (c) revoke ana's WRITE

    for name, perms in staff.items():
        print(f"after   {name}: {describe(perms)}")
    ```

    All three mask moves in one program: `&` *tests* a bit inside
    `describe`, `|=` *sets* the READ bit (a no-op for ana and ben, who
    already had it), and `&= ~WRITE` *clears* exactly one bit of ana's
    rights, leaving her READ intact — `110` becomes `100`, printed as
    `r--`.
