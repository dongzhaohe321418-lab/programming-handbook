# Exercises

Nine problems covering the whole chapter: string surgery, writing functions
from written specifications, formatting tables, and predicting what code does
before you run it. They start gentle and get sharper. For each one, write
your answer (or your prediction) *before* opening the solution — the struggle
is where the learning happens.

### Exercise 3.1 — Tidy the title (●)

The variable below holds a book title with messy spacing and casing:

```python
phrase = "   the quick brown fox   "
print("[" + phrase + "]")
```

Using string methods from [Section 3.2](02-strings.md), produce and print the
cleaned-up version `The Quick Brown Fox` — no surrounding spaces, each word
capitalised. One line of method chaining is enough.

??? success "Solution"

    ```python
    phrase = "   the quick brown fox   "
    print(phrase.strip().title())
    ```

    `strip()` returns a new string without the surrounding whitespace, and
    `title()` is then called on *that* string to capitalise each word —
    chaining works because every method returns a fresh string object.

### Exercise 3.2 — Slice surgeon (●)

Given `word = "computational"`, use indexing and slicing (no methods) to
print, one per line:

1. the first three characters (`com`),
2. the last three characters (`nal`),
3. the substring `put`,
4. the whole word reversed.

??? success "Solution"

    ```python
    word = "computational"
    print(word[:3])       # com
    print(word[-3:])      # nal
    print(word[3:6])      # put — positions 3, 4, 5
    print(word[::-1])     # lanoitatupmoc
    ```

    The key is the half-open rule: `word[3:6]` includes position 3 and
    excludes position 6, and negative indexes (`-3:`) count from the end.

### Exercise 3.3 — Print or return? (●)

Predict *exactly* what this program prints — line by line — before you run
it. Then run it and check.

```python
def mystery(a, b):
    print(a * b)

result = mystery(3, 4)
print(result)
```

??? success "Solution"

    ```python
    def mystery(a, b):
        print(a * b)

    result = mystery(3, 4)
    print(result)
    ```

    It prints `12`, then `None`. The `12` is a side effect from inside
    `mystery`; but the function has no `return`, so the value handed back to
    `result` is `None` — the classic `print`-vs-`return` confusion from
    [Section 3.3](03-writing-functions.md).

### Exercise 3.4 — Initials extractor (●●)

Write a function `initials(full_name)` to this specification: *given a name
consisting of a first name and a last name separated by whitespace (in any
casing), return the two initials, uppercased, each followed by a period.*
For example, `initials("grace hopper")` returns `"G.H."` and
`initials("Alan Turing")` returns `"A.T."`.

??? success "Solution"

    ```python
    def initials(full_name):
        """Return 'X.Y.' initials for a 'First Last' name."""
        parts = full_name.split()
        return parts[0][0].upper() + "." + parts[1][0].upper() + "."

    print(initials("grace hopper"))
    print(initials("Alan Turing"))
    ```

    `split()` cuts the name into a list of two words; `parts[0][0]` then
    indexes twice — first word, first character — and `upper()` normalises
    the case before the periods are glued on.

### Exercise 3.5 — Loaded dice (●●)

Write a function `roll_two()` that returns the **sum** of two six-sided dice
rolls using `random.randint`. In your main program, seed the generator with
`random.seed(11)`, call the function, and print the result as
`You rolled 9`. (With that seed, 9 is exactly what you should get — if you
see anything else, check the order of your calls.)

??? success "Solution"

    ```python
    import random

    def roll_two():
        """Return the total of two fair six-sided dice."""
        return random.randint(1, 6) + random.randint(1, 6)

    random.seed(11)          # seed once, before rolling
    total = roll_two()
    print(f"You rolled {total}")
    ```

    With seed 11 the generator produces 4 then 5, so the function returns 9;
    seeding makes the "random" program reproducible, which is what lets this
    exercise promise you an exact answer.

### Exercise 3.6 — Clock formatter (●●)

Write `seconds_to_clock(seconds)` to this specification: *given a
non-negative number of seconds (an integer smaller than 3600), return a
string in `MM:SS` form, with each part zero-padded to two digits.* So
`seconds_to_clock(754)` returns `"12:34"`, `seconds_to_clock(65)` returns
`"01:05"`, and `seconds_to_clock(9)` returns `"00:09"`. You will want `//`
and `%` from [Section 2.3](../ch02-data/03-operators.md) and a format spec
from [Section 3.4](04-output-formatting.md).

??? success "Solution"

    ```python
    def seconds_to_clock(seconds):
        """Return seconds (0..3599) formatted as zero-padded 'MM:SS'."""
        minutes = seconds // 60
        remainder = seconds % 60
        return f"{minutes:02}:{remainder:02}"

    print(seconds_to_clock(754))
    print(seconds_to_clock(65))
    print(seconds_to_clock(9))
    ```

    Integer division extracts whole minutes, modulo keeps the leftover
    seconds, and the `:02` spec pads each number with a leading zero to two
    digits.

### Exercise 3.7 — The price table (●●)

Using f-string alignment specs, print this table *exactly* — product names
left-aligned in 12 columns, prices right-aligned in 9 columns with two
decimals, and a rule of hyphens 21 characters wide:

```text
Product         Price
---------------------
Notebook         3.50
Backpack        49.00
Pencil           0.35
```

??? success "Solution"

    ```python
    print(f"{'Product':<12}{'Price':>9}")
    print("-" * 21)
    print(f"{'Notebook':<12}{3.5:>9.2f}")
    print(f"{'Backpack':<12}{49:>9.2f}")
    print(f"{'Pencil':<12}{0.35:>9.2f}")
    ```

    Because every row uses the same widths (12 + 9 = 21), the columns line
    up and the rule fits exactly; `:.2f` guarantees `3.5` and `49` display
    as money-style `3.50` and `49.00`.

### Exercise 3.8 — Where did it go? (●●●)

Two programs, almost identical. **Predict** what each one does — runs fine,
or stops with an error (which error, on which line?) — before checking.

Program A:

```text
def brew():
    strength = "strong"
    print("Brewing", strength, "coffee")

brew()
print(strength)
```

Program B:

```text
strength = "mild"

def brew():
    print("Brewing", strength, "coffee")

brew()
print(strength)
```

??? success "Solution"

    Program A prints `Brewing strong coffee`, then crashes — `strength` is a
    *local* variable that vanished when `brew()` returned:

    ```python
    # raises NameError
    def brew():
        strength = "strong"
        print("Brewing", strength, "coffee")

    brew()
    print(strength)
    ```

    Program B runs fine and prints `Brewing mild coffee` then `mild` —
    *reading* a global from inside a function is allowed:

    ```python
    strength = "mild"

    def brew():
        print("Brewing", strength, "coffee")

    brew()
    print(strength)
    ```

    The dividing line is *where the assignment happens*: assigned inside the
    function means local (dies with the call); assigned at the top level
    means global (readable everywhere).

### Exercise 3.9 — Name flipper (●●●)

Write `flip_name(entry)` to this specification: *given a string in the form
`"Last, First"` — possibly with extra spaces around either name or around the
comma — return `"First Last"` with single spacing and no stray whitespace.*
Include a proper docstring. `flip_name("  Hopper ,  Grace  ")` must return
`"Grace Hopper"`, and `flip_name("Turing,Alan")` must return `"Alan Turing"`.

??? success "Solution"

    ```python
    def flip_name(entry):
        """Return 'Last, First' (any spacing) rewritten as 'First Last'."""
        comma = entry.find(",")
        last = entry[:comma].strip()
        first = entry[comma + 1:].strip()
        return first + " " + last

    print(flip_name("  Hopper ,  Grace  "))
    print(flip_name("Turing,Alan"))
    ```

    This is the worked example from [Section 3.2](02-strings.md) wrapped
    into a reusable, documented function: locate the comma, slice each side,
    `strip()` the noise, and reassemble in the new order — messy spacing is
    neutralised entirely by the two `strip()` calls.
