# Exercises

Work through these in order — they start with pure logic and end with bug
hunts in realistic code. Try each one before opening the solution, and use
the Run button to check yourself: for the *predict* exercises, write your
answer down first, then run.

### Exercise 4.1 — Complete the truth table ●

Copy this table onto paper and fill in the last two columns for all four
rows, using only the truth tables from
[section 4.1](01-booleans-logic.md):

| `a`     | `b`     | `a and not b` | `not a or b` |
| ------- | ------- | ------------- | ------------ |
| `True`  | `True`  | ?             | ?            |
| `True`  | `False` | ?             | ?            |
| `False` | `True`  | ?             | ?            |
| `False` | `False` | ?             | ?            |

??? success "Solution"

    ```python
    from itertools import product

    print("a      b      | a and not b   not a or b")
    for a, b in product([True, False], repeat=2):
        print(f"{a!s:6} {b!s:6} | {(a and not b)!s:13} {(not a or b)!s}")
    ```

    Row by row: `a and not b` is `True` only in the single row where `a` is
    `True` and `b` is `False`; `not a or b` is `False` only in that same
    row — the two columns are exact opposites, because
    `not (a and not b) = (not a) or b` by De Morgan's laws.

### Exercise 4.2 — Predict the branch ●

Without running it, write down exactly what this program prints. Then run
it and compare.

```python
x = 10

if x > 5:
    print("big")
if x > 8:
    print("bigger")
else:
    print("medium")
if x > 20:
    print("huge")
print("done")
```

??? success "Solution"

    ```python
    x = 10
    if x > 5:
        print("big")        # 10 > 5  -> runs
    if x > 8:
        print("bigger")     # 10 > 8  -> runs (separate if, tested anyway)
    else:
        print("medium")     # skipped — its if was True
    if x > 20:
        print("huge")       # 20 test fails; no else, so nothing
    print("done")           # always runs
    ```

    It prints `big`, `bigger`, `done`. The key idea: these are three
    *independent* `if` statements, not one `elif` chain, so every condition
    is tested. The `else` belongs only to the second `if`.

### Exercise 4.3 — String showdown ●

Predict `True` or `False` for each line, then run to check. Two of the four
are traps from [section 4.1](01-booleans-logic.md).

```text
print("Apple" < "apple")
print("3" < "20")
print("abc" < "abd")
print("hi" == "hi ")
```

??? success "Solution"

    ```python
    print("Apple" < "apple")   # True  — uppercase sorts before lowercase
    print("3" < "20")          # False — strings! '3' > '2' decides it
    print("abc" < "abd")       # True  — first difference: 'c' < 'd'
    print("hi" == "hi ")       # False — trailing space makes them differ
    ```

    The traps: `"3" < "20"` compares *characters*, not numbers, so only
    `'3'` vs `'2'` matters; and equality sees the invisible trailing space.

### Exercise 4.4 — Leap year ●●

Write a function `is_leap(year)` that returns `True` for leap years. The
full rule: a year is a leap year if it is divisible by 4 — *except* that
years divisible by 100 are not — *except* that years divisible by 400 are
after all. Test it on 1900 (`False`), 2000 (`True`), 2023 (`False`),
2024 (`True`), and 2100 (`False`).

??? success "Solution"

    ```python
    def is_leap(year):
        if year % 400 == 0:      # most specific rule first
            return True
        if year % 100 == 0:
            return False
        return year % 4 == 0     # the comparison IS the answer

    for y in [1900, 2000, 2023, 2024, 2100]:
        print(y, "->", is_leap(y))
    ```

    The guard style checks the *exceptions* in order of specificity
    (400 overrides 100 overrides 4), so each later test only sees years the
    earlier rules did not settle. Note the last line: `year % 4 == 0` is
    already a Boolean, so returning it directly beats
    `if ...: return True else: return False`.

### Exercise 4.5 — BMI categories ●●

Write `bmi_category(weight_kg, height_m)` that computes
$\text{BMI} = \frac{\text{weight}}{\text{height}^2}$ and returns
`"underweight"` (BMI below 18.5), `"normal"` (18.5 up to but not including
25), `"overweight"` (25 up to but not including 30), or `"obese"`
(30 and above). Make sure the boundary values 18.5, 25, and 30 each land in
the correct category — no gaps, no overlaps.

??? success "Solution"

    ```python
    def bmi_category(weight_kg, height_m):
        bmi = weight_kg / height_m ** 2
        if bmi < 18.5:
            return "underweight"
        elif bmi < 25:
            return "normal"        # reached only when 18.5 <= bmi < 25
        elif bmi < 30:
            return "overweight"
        else:
            return "obese"

    print(bmi_category(50, 1.75))   # underweight
    print(bmi_category(68, 1.75))   # normal
    print(bmi_category(80, 1.70))   # overweight
    print(bmi_category(95, 1.70))   # obese
    ```

    Each `elif` starts exactly where the previous test stopped, and `else`
    owns everything from 30 up — so every possible BMI has exactly one
    home. Writing both ends of each range by hand
    (`if 18.5 <= bmi < 25: ...`) also works but invites the
    boundary-gap bug from [section 4.4](04-switch-style-debug.md).

### Exercise 4.6 — Flatten the pyramid ●●

This works, but the logic climbs three levels deep. Rewrite it as a
function `shipping_message(country, total, in_stock)` using the guard
pattern from [section 4.2](02-if-else.md) — no branch deeper than one
level.

```text
if country == "US":
    if total >= 35:
        if in_stock:
            print("Free 2-day shipping!")
        else:
            print("Item out of stock.")
    else:
        print("Add more items for free shipping.")
else:
    print("We don't ship there yet.")
```

??? success "Solution"

    ```python
    def shipping_message(country, total, in_stock):
        if country != "US":
            return "We don't ship there yet."
        if total < 35:
            return "Add more items for free shipping."
        if not in_stock:
            return "Item out of stock."
        return "Free 2-day shipping!"

    print(shipping_message("US", 40, True))
    print(shipping_message("US", 40, False))
    print(shipping_message("US", 20, True))
    print(shipping_message("CA", 40, True))
    ```

    Each guard eliminates one failure case and returns immediately; the
    happy path ends up unindented on the last line. Note how every guard
    *inverts* one of the original conditions (`== "US"` becomes `!= "US"`,
    `total >= 35` becomes `total < 35`).

### Exercise 4.7 — Find the bug: ticket pricing ●●

A cinema charges: under 3 years — free; under 13 — 5 euros; under 65 —
11 euros; 65 and over — 8 euros. This implementation compiles and runs,
yet every customer aged 3 or older pays 11 euros. Predict what it prints
for ages 2, 10, and 70; find the bug; fix it.

```python
def ticket_price(age):
    if age < 3:
        return 0
    elif age < 65:
        return 11
    elif age < 13:
        return 5
    else:
        return 8

for age in [2, 10, 70]:
    print(age, "->", ticket_price(age))
```

??? success "Solution"

    ```python
    def ticket_price(age):
        if age < 3:
            return 0
        elif age < 13:       # more specific test moved BEFORE age < 65
            return 5
        elif age < 65:
            return 11
        else:
            return 8

    for age in [2, 10, 70]:
        print(age, "->", ticket_price(age))   # 0, 5, 8
    ```

    The buggy version prints `0`, `11`, `8`: a 10-year-old hits
    `age < 65` first, which is `True`, so the child test below it is
    unreachable. With `<`-style tests the chain must run from the
    **lowest** boundary up (the mirror image of the highest-first rule for
    `>=` chains) so that specific cases are decided before general ones.

### Exercise 4.8 — is vs == detective ●●

Predict the four printed values, then run. Explain each in one sentence
using the words *value* and *object* (see
[section 4.3](03-equality-identity.md)).

```text
p = [1, 2]
q = [1, 2]
r = q
q.append(3)

print(p == q)
print(p is q)
print(q is r)
print(r)
```

??? success "Solution"

    ```python
    p = [1, 2]
    q = [1, 2]
    r = q            # alias: r and q name the SAME object
    q.append(3)      # mutates that one object

    print(p == q)    # False — values now differ: [1, 2] vs [1, 2, 3]
    print(p is q)    # False — always were two separate objects
    print(q is r)    # True  — one object, two names
    print(r)         # [1, 2, 3] — the append is visible through r too
    ```

    `p` and `q` started as equal-but-separate objects, so the `append`
    changed `q`'s value away from `p`'s. `r = q` copied only the
    reference, so `q` and `r` share identity — a change through either
    name is seen through both.

### Exercise 4.9 — Command dispatcher, three ways ●●●

A tiny text adventure accepts the commands `north`, `south`, `look`, and
`quit` — plus the abbreviations `n`, `s`, and `l`. Unknown input should
produce `I don't understand.` Write a function `respond(command)` **twice**:
once with `match`/`case` (use `|` patterns for the abbreviations and `_`
for the default), and once with a dictionary lookup using `.get()`. The
replies are up to you — just keep both versions identical in behaviour.
Which version would you rather maintain if the game grew to 50 commands?

??? success "Solution"

    ```python
    def respond_match(command):
        match command:
            case "north" | "n":
                return "You walk north."
            case "south" | "s":
                return "You walk south."
            case "look" | "l":
                return "A misty forest surrounds you."
            case "quit":
                return "Goodbye!"
            case _:
                return "I don't understand."

    replies = {
        "north": "You walk north.",  "n": "You walk north.",
        "south": "You walk south.",  "s": "You walk south.",
        "look": "A misty forest surrounds you.",
        "l": "A misty forest surrounds you.",
        "quit": "Goodbye!",
    }

    def respond_dict(command):
        return replies.get(command, "I don't understand.")

    for cmd in ["north", "s", "look", "dance", "quit"]:
        assert respond_match(cmd) == respond_dict(cmd)
        print(f"{cmd:6} -> {respond_dict(cmd)}")
    ```

    Both behave identically (the `assert` proves it on every test input).
    At 50 commands the dictionary wins: it is pure data — easy to scan,
    sort, count, or load from a file — while a 50-case `match` is a wall
    of code. The `match` version earns its keep when cases need different
    *logic*, not just different data.
