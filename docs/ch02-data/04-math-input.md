# 2.4 The math library and reading input

Real programs rarely live on `+` and `*` alone — they take square roots,
round prices to cents, and (crucially) accept numbers typed by a human.
This section tours the numeric tools Python ships with, exposes a genuinely
surprising behaviour of `round()`, and establishes the input-handling
pattern you will use in every interactive program from here on.

## Built-ins you already have

Four numeric helpers need no `import` at all:

```python
print(abs(-7.5))          # absolute value
print(min(3, 9, -2))      # smallest of any number of arguments
print(max(3, 9, -2))      # largest
print(round(3.14159, 2))  # round to 2 decimal places
print(round(2.71828))     # no second argument: round to a whole number
```

The output:

```text
7.5
-2
9
3.14
3
```

`round(x, n)` rounds `x` to `n` decimal places; with no `n` it returns a
whole number (an actual `int`). Straightforward — until the value sits
exactly halfway.

### The banker's-rounding surprise

Quick — what is `round(2.5)`? Nearly everyone says `3`. Run it:

```python
print(round(0.5))
print(round(1.5))
print(round(2.5))
print(round(3.5))
```

The output is `0`, `2`, `2`, `4`. Python does **not** round halves up — it
rounds them **to the nearest even number**. This rule is called *banker's
rounding* (officially "round half to even"), and it exists for a good
statistical reason: always rounding `.5` upward drags every total slightly
upward, while rounding to even sends ties up half the time and down half
the time, cancelling the bias. Banks, scientists, and the IEEE
floating-point standard all use it — and so does Python.

Two consequences worth remembering. First, only exact halves are affected —
`round(2.6)` is `3` as usual. Second, floats add their own wrinkle:
`round(2.675, 2)` gives `2.67`, not `2.68`, because `2.675` is *stored* as
a hair under 2.675 before `round` even sees it
([Chapter 5.1](../ch05-under-the-hood/01-numeric-pitfalls.md) has the full
story).

!!! info "Java corner"
    Java's `Math.round(2.5)` returns `3` — it always rounds halves toward
    positive infinity. So the *same expression* gives different answers in
    your two languages: Python `round(2.5)` → `2`, Java `Math.round(2.5)`
    → `3`. Remember this the first time a Python result is one cent off
    from your Java program's.

## The `math` module

Everything beyond those four lives in the **`math` module** — a standard-
library toolbox you bring in with `import math`, then access with a dot:

```python
import math

print(math.sqrt(2))     # square root
print(math.floor(3.7))  # round DOWN to an integer
print(math.ceil(3.2))   # round UP to an integer
print(math.pi)          # the constant pi
```

The output:

```text
1.4142135623730951
3
4
3.141592653589793
```

`floor` always moves down and `ceil` always moves up — unlike `round`,
which moves to whichever integer is nearer. For negative numbers, note that
`floor` and `int()` disagree:

```python
import math
print(math.floor(-3.7))   # -4: floor goes DOWN, even for negatives
print(int(-3.7))          # -3: int() truncates toward zero
```

### `math.pow` vs `**`

The module also has a power function, but it is *not* a synonym for `**`:
`math.pow` converts everything to `float` first, so it inherits float
approximation, while `**` between ints is exact at any size:

```python
import math
print(2 ** 10)           # int result, exact
print(math.pow(2, 10))   # float result
print(2 ** 100)          # still exact — arbitrary precision
print(math.pow(2, 100))  # approximate! only ~16 significant digits survive
```

The output:

```text
1024
1024.0
1267650600228229401496703205376
1.2676506002282294e+30
```

Rule of thumb: use `**` for integer powers, and reserve `math.pow` for
deliberately-float work (it mirrors Java's `Math.pow`, which also returns
`double`).

=== "Python"

    ```python
    import math
    print(math.sqrt(2), math.pi)
    print(abs(-7.5), max(3, 9))     # abs/min/max/round are built-ins
    ```

=== "Java"

    ```java
    Math.sqrt(2);      // 1.4142135623730951
    Math.PI;           // 3.141592653589793
    Math.abs(-7.5);    // 7.5 — in Java these live in Math too
    Math.max(3, 9);    // 9
    Math.floor(3.7);   // 3.0 — careful: Java's floor returns a double!
    ```

The mapping is nearly one-to-one; the main difference is *where* things
live. Java gathers everything into the `Math` class; Python puts the
everyday four (`abs`, `min`, `max`, `round`) straight into the language and
the rest into `math`.

## Reading input from the keyboard

The built-in `input()` function pauses the program, shows a prompt, waits
for the user to type a line and press ++enter++, and hands that line back.
On your own machine, a session looks like this:

```text
>>> name = input("What is your name? ")
What is your name? Ada
>>> print("Hello,", name)
Hello, Ada
```

!!! note "The handbook convention for input"
    The Run button executes code in your browser, where a block **cannot
    pause to wait for typing** — so `input()` is the one built-in the
    runnable blocks never call. Instead, every example *hard-codes the
    pretend user input into a variable* and says so in a comment:

    ```python
    text = "42"   # imagine the user typed this
    print(text)
    ```

    When you run examples on your own machine
    ([Chapter 1.2](../ch01-tools/02-python-setup.md)), replace such lines
    with the real call: `text = input("Enter a number: ")`. Everything
    after that line is identical.

## `input()` always gives you a string

The single most important fact about `input()`: **it returns a string,
always** — even when the user types digits. The string `"19"` is not the
number `19`, and arithmetic on it fails:

```python
# raises TypeError
age_text = "19"        # what input() hands back is a STRING
print(age_text + 1)    # "19" + 1: str and int don't mix
```

The cure is [section 2.1](01-variables-types.md)'s conversion functions —
this three-step pattern (*read → convert → compute*) is the skeleton of
every interactive program:

```python
age_text = "19"        # imagine the user typed this
age = int(age_text)    # convert: str -> int
print(age + 1)         # compute: now arithmetic works
```

This prints `20`. Use `float()` instead when decimals are legal input
(prices, measurements), and remember from 2.1 that a user typing `"abc"`
makes the conversion raise `ValueError` — graceful recovery arrives with
exceptions in [Chapter 10](../ch10-exceptions/index.md).

!!! info "Java corner"
    Java reads input through a `Scanner` object, which has a separate typed
    method for each kind of value — the conversion is built into the read:

    ```java
    Scanner scanner = new Scanner(System.in);
    int age = scanner.nextInt();        // reads AND converts
    double price = scanner.nextDouble();
    String name = scanner.nextLine();
    ```

    Python has exactly one input function that always yields `str`, plus
    explicit conversions. Same job, two philosophies.

## Worked example: a tip calculator

Time to combine the whole chapter — input handling, conversion, arithmetic,
and output — into one honest program. It splits a restaurant bill, tip
included, among friends:

```python
# --- read (imagine the user typed these three answers) ---
bill_text = "62.50"      # input("Bill amount: ")
tip_text = "18"          # input("Tip percent: ")
people_text = "4"        # input("How many people? ")

# --- convert ---
bill = float(bill_text)      # money can have cents -> float
tip_percent = int(tip_text)  # a whole-number percent -> int
people = int(people_text)

# --- compute ---
tip = bill * tip_percent / 100
total = bill + tip
share = total / people

# --- report (:.2f formats to 2 decimals — details in Chapter 3.4) ---
print(f"Tip:        ${tip:.2f}")
print(f"Total:      ${total:.2f}")
print(f"Per person: ${share:.2f}")
```

The output:

```text
Tip:        $11.25
Total:      $73.75
Per person: $18.44
```

Walk the numbers: 18% of \$62.50 is \$11.25; the total is \$73.75; split
four ways, each person owes \$18.4375, displayed to the cent as `$18.44`.
Notice the three-act structure — *read, convert, compute* — and how each
conversion picked the right type (`float` for money, `int` for counts).
The `f"..."` strings with `:.2f` are a preview of **f-strings**, the
formatting tool [Chapter 3.4](../ch03-functions/04-output-formatting.md)
covers properly; here they just mean "show two decimal places".

!!! warning "Common mistakes"
    - **Doing math on raw input.** `input()` returns `str`, so
      `input(...) * 2` doesn't double a number — it *repeats the string*
      (`"7" * 2` is `"77"`). Convert first, always.
    - **Calling `input()` in the browser blocks.** The in-page runner
      cannot wait for typing; hard-code the pretend input as shown above,
      and switch to real `input()` only on your own machine.
    - **Expecting `round(2.5)` to be `3`.** Python rounds half to *even*:
      `round(2.5)` is `2`. If a course exercise or bank spec demands
      half-up rounding, you must code it deliberately.
    - **Using `math.pow` for big integer powers.** It returns an
      approximate `float`; `2 ** 100` via `math.pow` loses digits. Use
      `**` for exact integer exponentiation.

## Check your understanding

1. What are `round(7.5)` and `round(8.5)`? (Careful.)

    ??? success "Answer"
        `8` and `8`. Both are exact halves, so both round to the nearest
        **even** integer — 7.5 goes *up* to 8, and 8.5 goes *down* to 8.
        That is banker's rounding at work.

2. Why does `math.floor(-2.1)` give `-3` while `int(-2.1)` gives `-2`?

    ??? success "Answer"
        `floor` always moves toward negative infinity ("down"), so `-2.1`
        drops to `-3`. `int()` truncates — it simply deletes the fractional
        part, moving toward zero, leaving `-2`. They agree for positive
        numbers and disagree for negatives.

3. The user runs `n = input("Pick a number: ")` and types `5`. What does
   `n * 3` evaluate to, and how do you get `15` instead?

    ??? success "Answer"
        `"555"` — `n` is the *string* `"5"`, and `*` repeats strings.
        Convert first: `int(n) * 3` gives `15`.

4. In one line, compute the exact value of $3^{50}$. Should you use `**`
   or `math.pow`?

    ??? success "Answer"
        `print(3 ** 50)` — the `**` operator keeps integer arithmetic
        exact at any size. `math.pow(3, 50)` would return a `float` with
        only about 16 reliable digits, silently corrupting the rest.
