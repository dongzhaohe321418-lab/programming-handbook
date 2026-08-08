# Exercises

## The chapter in brief

- `sys.argv` is a plain list of strings, and element 0 is the script's own
  name — the user's first argument is `sys.argv[1]`
  ([10.1](01-cli-programs.md)).
- Because arguments arrive as text, `argv[1] + argv[2]` *concatenates*;
  convert with `int()` or `float()` before computing anything.
- A well-mannered tool checks its argument count first, prints a **usage
  message** when the call is wrong, and reports failure to the shell with a
  non-zero **exit code**.
- An exception is an *object* describing a failure: it abandons the normal
  flow and flies up the call chain looking for a handler
  ([10.2](02-exceptions.md)).
- `try`/`except` lets the program survive a failure — and it should survive
  *narrowly*, because a bare `except` swallows your own bugs and manufactures
  plausible wrong answers.
- `else` is the success lane; `finally` runs no matter what, even when the
  exception escapes unhandled.
- `raise` is how your own functions refuse nonsense, on the principle that a
  wrong value travels while an exception stops.
- A handler can catch a failure raised many calls below it, which is why
  exception control flow is called **non-linear**.
- Java splits exceptions into checked and unchecked and makes the compiler
  police the checked ones; in Python every exception is unchecked.
- A traceback is read bottom-up: the last line says *what*, the bottom frame
  says *where*, and walking upward says *how we got there*
  ([10.3](03-stack-traces.md)).
- When the bottom frame sits inside a library, the bug is almost always in
  the last frame that belongs to your own files.
- Two stories separated by "During handling of the above exception" means
  chaining — and the bottom-most story is still the newest.

### Key terms

| Term | Reminder |
| --- | --- |
| [`sys.argv`](../concept-index.md) | the command-line words handed to your program, script name at index 0 |
| usage message | the one-line reminder of how the tool is meant to be called |
| [exit code](../concept-index.md) | the integer a program hands the shell — 0 success, non-zero failure |
| [exception](../concept-index.md) | an object describing a failure, raised instead of returning a wrong answer |
| [`try` / `except` / `finally`](../concept-index.md) | meet a failure, take the success lane, and clean up whatever happens |
| [raising an exception](../concept-index.md) | refusing an impossible argument loudly, at the line where it appeared |
| bare `except` | the handler that catches everything — including the typo you have not found yet |
| [traceback](../concept-index.md) | the call stack, printed at the instant an exception ran out of handlers |
| [frame (stack)](../concept-index.md) | one entry of that stack: file, line, function, and source line |
| exception chaining | a second exception raised while the first was still being handled |

Now the drills.

Exceptions reward practice at prediction: for every "predict" exercise,
write the exact output — including which handler fires — *before* running.
Difficulty: ● warm-up, ●● standard, ●●● challenge.

### Exercise 10.1 — Which except runs? ●

For each of the three inputs, predict which line is printed, then run.

```python
values = ["7", "0", "x"]

for text in values:
    try:
        print(10 // int(text))
    except ValueError:
        print("V:", text)
    except ZeroDivisionError:
        print("Z:", text)
```

??? success "Solution"

    ```python
    values = ["7", "0", "x"]

    for text in values:
        try:
            print(10 // int(text))
        except ValueError:
            print("V:", text)      # fires for "x" — int("x") fails first
        except ZeroDivisionError:
            print("Z:", text)      # fires for "0" — conversion fine, division not
    ```

    Output: `1`, then `Z: 0`, then `V: x`. `"7"` succeeds
    (`10 // 7` is `1`); `"0"` converts but explodes at the division;
    `"x"` never reaches the division because `int()` raises first.

### Exercise 10.2 — Sum the arguments ●

A tool is called as `python sum.py 4 8 15`. Using the handbook's `argv`
convention, print the total of *all* numeric arguments (there may be any
number of them). Remember what type the arguments arrive as.

??? success "Solution"

    ```python
    argv = ["sum.py", "4", "8", "15"]   # what sys.argv would contain

    total = 0
    for text in argv[1:]:               # skip argv[0], the program name
        total += int(text)
    print(total)                        # 27
    ```

    `argv[1:]` slices off the program name, and each remaining element is
    a *string* that must be converted before adding — `"4" + "8"` would
    have concatenated.

### Exercise 10.3 — A validator that raises ●●

Write `parse_age(text)`: it returns the age as an `int`, but raises
`ValueError` with a helpful message if the text is not a whole number *or*
the age is outside 0–130. Then show both failure modes being caught with a
`try`/`except` that prints the message.

??? success "Solution"

    ```python
    def parse_age(text):
        age = int(text)                 # may itself raise ValueError — good!
        if age < 0 or age > 130:
            raise ValueError(f"age must be between 0 and 130, got {age}")
        return age

    for entry in ["35", "abc", "999"]:
        try:
            print("parsed:", parse_age(entry))
        except ValueError as error:
            print("rejected:", error)
    ```

    `"35"` parses; `"abc"` is rejected by `int()`'s own `ValueError`;
    `"999"` is rejected by ours. Both failures are the same *type*, so one
    handler catches both — and the message tells the user which rule broke.

### Exercise 10.4 — else, finally, and the order of things ●●

Predict the exact output of both calls — two words per call, but *which*
two? Then run.

```python
def attempt(text):
    try:
        n = int(text)
    except ValueError:
        print("except", end=" ")
    else:
        print("else", end=" ")
    finally:
        print("finally")

attempt("5")
attempt("five")
```

??? success "Solution"

    ```python
    def attempt(text):
        try:
            n = int(text)
        except ValueError:
            print("except", end=" ")
        else:
            print("else", end=" ")
        finally:
            print("finally")

    attempt("5")      # else finally
    attempt("five")   # except finally
    ```

    `else` runs only when the `try` body raised nothing; `except` runs
    only when it did; `finally` runs in both stories — and always last.

### Exercise 10.5 — Rescue the bare except ●●

This function returns `-1` whenever *anything* goes wrong — including its
own bug. Narrow the handler to the one failure that is genuinely expected
(a price that is not a number), fix the typo the bare except was hiding,
and make the good inputs work.

```text
def total_price(prices):
    try:
        return sum(price)        # hmm...
    except:
        return -1

print(total_price(["12", "8"]))   # currently -1. It should be 20.
```

??? success "Solution"

    ```python
    def total_price(prices):
        try:
            total = 0
            for text in prices:
                total += int(text)      # ValueError is the EXPECTED failure
            return total
        except ValueError:
            return -1

    print(total_price(["12", "8"]))     # 20
    print(total_price(["12", "oops"]))  # -1 — the anticipated bad input
    ```

    The original had two problems hiding behind one bare `except`: the
    typo `sum(price)` (a `NameError` bug) and unconverted strings (a
    `TypeError` waiting to happen). Narrowing to `except ValueError`
    means only genuinely bad *input* triggers the fallback; any future
    bug will crash loudly and point at itself.

### Exercise 10.6 — Traceback comprehension ●●

A program printed the traceback below. Without seeing the source, answer:
(a) what failed, exactly? (b) in which function and on which line was the
exception raised? (c) which function called it? (d) what would you check
first?

```text
Traceback (most recent call last):
  File "billing.py", line 14, in <module>
    print(invoice_total(cart))
  File "billing.py", line 9, in invoice_total
    subtotal = subtotal + line_cost(item)
  File "billing.py", line 4, in line_cost
    return item["price"] * item["qty"]
KeyError: 'qty'
```

??? success "Solution"

    (a) A `KeyError`: some item dict has no `'qty'` key. (b) In
    `line_cost`, line 4 of `billing.py` — the bottom frame. (c)
    `invoice_total`, from line 9. (d) The contents of `cart`: at least one
    item was built without a `'qty'` field (or with a misspelled one) —
    the failing line only *revealed* it. A quick reproduction:

    ```python
    # raises KeyError
    def line_cost(item):
        return item["price"] * item["qty"]

    cart = [{"price": 5, "qty": 2}, {"price": 3}]   # second item is malformed
    total = 0
    for item in cart:
        total = total + line_cost(item)
    ```

    Bottom line first (*what*: missing `'qty'`), then the bottom frame
    (*where*), then walk up to find *who supplied the bad data*.

### Exercise 10.7 — A robust temperature converter ●●●

Build the complete tool `temp.py`, called as `python temp.py 100 c`. It
must: print a usage message if the argument count is wrong; handle a
non-numeric value with a friendly message (no traceback!); accept units
`c` or `f`; and print the conversion as `100.0 C = 212.0 F` (formulas:
$F = C \times 9/5 + 32$, $C = (F - 32) \times 5/9$). Test all four paths
by editing `argv`.

??? success "Solution"

    ```python
    argv = ["temp.py", "100", "c"]   # what sys.argv would contain

    if len(argv) != 3:
        print(f"usage: python {argv[0]} VALUE UNIT   (UNIT is c or f)")
    else:
        try:
            value = float(argv[1])
        except ValueError:
            print(f"not a number: {argv[1]}")
        else:
            unit = argv[2]
            if unit == "c":
                print(f"{value} C = {value * 9 / 5 + 32} F")
            elif unit == "f":
                print(f"{value} F = {(value - 32) * 5 / 9} C")
            else:
                print(f"unknown unit: {unit} (expected c or f)")
    ```

    Each failure gets the cheapest adequate response: a *count* problem is
    a normal `if` (no exception needed), the *conversion* is guarded by a
    narrow `except ValueError`, and the success path lives in `else` so
    the `try` block stays minimal. Try `["temp.py", "212", "f"]`,
    `["temp.py", "warm", "c"]`, and `["temp.py", "100"]`.

### Exercise 10.8 — Re-raise with a better message ●●●

Write `load_setting(settings, key)` that returns `settings[key]` but, when
the key is missing, raises a *new* `KeyError` whose message names the key
and suggests checking the config file. First let the improved exception
escape and observe the chained traceback (`During handling of the above
exception...`); then show a caller catching it and printing the message.

??? success "Solution"

    ```python
    # raises KeyError
    def load_setting(settings, key):
        try:
            return settings[key]
        except KeyError:
            raise KeyError(f"missing setting '{key}' — check your config file")

    print(load_setting({"theme": "dark"}, "volume"))
    ```

    Running that shows *two* stories: the original `KeyError: 'volume'`,
    the chaining sentence, then our friendlier one — newest at the bottom,
    as always. And the caught version:

    ```python
    def load_setting(settings, key):
        try:
            return settings[key]
        except KeyError:
            raise KeyError(f"missing setting '{key}' — check your config file")

    settings = {"theme": "dark"}
    for key in ["theme", "volume"]:
        try:
            print(key, "=", load_setting(settings, key))
        except KeyError as error:
            print("config problem:", error)
    ```

    Catch-and-re-raise upgrades a low-level failure into one that speaks
    the caller's language, while the chained traceback preserves the
    original evidence for whoever debugs it.
