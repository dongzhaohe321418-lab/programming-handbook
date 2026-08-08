# 4.4 switch/match, debugging, and style

An `elif` chain that compares one variable against a series of specific
values — menu choices, status codes, command names — is so common that many
languages grew a dedicated statement for it. Java has had `switch` since day
one; Python added `match` in version 3.10.

This section shows both, shows when a plain dictionary beats either, and then
turns practical: how to *debug* a branch that takes the wrong path, and the
style habits that stop branch bugs from being written at all.

## Python's match statement

`match` takes one subject expression and compares it against a series of
`case` patterns, top to bottom. Four rules cover everything we need here:

- **First match wins.** That pattern's block runs, and the whole statement
  ends.
- **There is no fallthrough**, so there is no `break` — a `case` never leaks
  into the one below it.
- **`_` is the wildcard.** It matches anything, playing the role of `else` or
  Java's `default`.
- **`|` lets several literals share one case**, as in `case 301 | 302:`.

```python
def describe_status(code):
    match code:
        case 200:
            return "OK"
        case 301 | 302:            # two literals, one case
            return "redirect"
        case 404:
            return "not found"
        case 500:
            return "server error"
        case _:                    # wildcard — the default, always last
            return "unknown code"

for code in [200, 302, 404, 418]:
    print(code, "->", describe_status(code))
```

Output: `200 -> OK`, `302 -> redirect`, `404 -> not found`, and
`418 -> unknown code`. Note what did *not* happen: after `302` matched, the
`404` and `500` cases were never considered. Each `case` is a sealed room,
not a step on a staircase.

`match` can do far more than compare literals — patterns can take apart
lists and objects — but literal matching is the part that mirrors your Java
course, so it is all we need here.

## Java's switch — and the fallthrough trap

Java's classic `switch` looks similar but behaves differently in one
treacherous way: after a matching `case` label, execution **falls through**
into the next case unless you explicitly say `break`. Forgetting a `break`
is one of the most notorious bugs in the C family of languages, which is
exactly why Python's `match` refused to inherit it.

=== "Python"

    ```python
    day = 2
    match day:
        case 1:
            print("Monday")
        case 2:
            print("Tuesday")       # runs, then match ENDS — no break needed
        case 3:
            print("Wednesday")
        case _:
            print("some other day")
    ```

=== "Java"

    ```java
    int day = 2;
    switch (day) {
        case 1:
            System.out.println("Monday");
            break;
        case 2:
            System.out.println("Tuesday");
            // break;  <-- forgotten! execution FALLS THROUGH ...
        case 3:
            System.out.println("Wednesday");   // ... and prints this too!
            break;
        default:
            System.out.println("some other day");
    }
    // With the break missing, this prints BOTH Tuesday AND Wednesday.
    ```

=== "Java 17 arrow form"

    ```java
    int day = 2;
    switch (day) {
        case 1 -> System.out.println("Monday");
        case 2 -> System.out.println("Tuesday");   // arrow form: no fallthrough
        case 3 -> System.out.println("Wednesday");
        default -> System.out.println("some other day");
    }
    ```

Modern Java (the arrow `->` form, standard since Java 14) fixed the trap,
and your Java course will likely show both forms. The three shapes side by
side:

| | Python `match` | Java `switch` (classic) | Java `switch` (arrow) |
| --- | --- | --- | --- |
| Falls through? | never | yes, unless you `break` | never |
| `break` needed? | no | yes, on every case | no |
| Share one body | one `case`, several literals | stack `case 6: case 7:` | `case 6, 7 ->` |
| Catch-all | `case _:` | `default:` | `default ->` |

The deliberate *use* of fallthrough — stacking `case 6: case 7:` to share a
body — is what Python's `case 6 | 7:` expresses safely.

## When a dictionary beats both

If every branch does the *same kind* of thing — map a key to a value, or a
key to a function — the most Pythonic tool is not a branch at all but a
**dictionary lookup**. Compare thirty `case` lines against one table you
can read, sort, and even load from a file:

```python
month_days = {"Jan": 31, "Feb": 28, "Mar": 31, "Apr": 30,
              "May": 31, "Jun": 30}

print(month_days.get("Feb", "unknown month"))   # 28
print(month_days.get("Foo", "unknown month"))   # unknown month — the default
```

`get(key, default)` plays the role of `case _`. The same idea scales up to a
**dispatch table** — a dictionary whose values are functions. This is a
genuinely professional pattern: calculators, command interpreters, and web
frameworks all route requests this way.

```python
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

operations = {"+": add, "-": subtract, "*": multiply}

op = "*"                                # imagine the user typed this
if op in operations:
    print(operations[op](6, 7))         # looks up multiply, calls it: 42
else:
    print("unknown operator:", op)
```

Rule of thumb — match the tool to the *shape* of the decision:

| The decision looks like | Reach for |
| --- | --- |
| **Data-shaped**: key → result, e.g. `"FR"` → `"France"` | a dictionary, with `.get(key, default)` |
| **Range- or condition-shaped**: `score >= 90` | an `if`/`elif` chain |
| **Structural**: take a list or object apart | `match`, for its real patterns |

## Debugging branches

Sooner or later a program takes a path you did not expect. Branch debugging
has one core question — *which branch actually ran?* — and one blunt,
effective tool: a trace print in every branch.

```python
score = 79

if score >= 90:
    print("[trace] took the A branch")
    grade = "A"
elif score >= 80:
    print("[trace] took the B branch")
    grade = "B"
else:
    print("[trace] took the fallback branch")
    grade = "C or below"

print("grade:", grade)
```

Run it and the trace says the fallback branch ran — no guessing. Once the
mystery is solved, delete the traces. If a *condition* is too tangled to
reason about, split it into named Booleans and print those; naming the parts
often reveals the bug by itself:

```python
age = 25
income = 42_000
years_at_job = 1

is_adult = age >= 18
earns_enough = income > 30_000
stable_job = years_at_job >= 2

print("is_adult:", is_adult, "| earns_enough:", earns_enough,
      "| stable_job:", stable_job)

if is_adult and earns_enough and stable_job:
    print("loan approved")
else:
    print("loan denied")
```

The printout shows at a glance *which* requirement failed (`stable_job` is
`False`). Now for the three classic branch bugs.

### Bug 1 — `=` where `==` belongs

Python turns this ancient bug into an immediate, loud error instead of a
silent wrong answer — and recent versions even guess what you meant:

```python
# raises SyntaxError
# A single = assigns; a double == compares. Python refuses to run this:
x = 5
if x = 5:
    print("five")
```

### Bug 2 — elif tests in the wrong order

In a chain, the first `True` test wins — so a *general* test placed before a
*specific* one starves it:

```python
score = 95

if score >= 60:
    print("D")          # 95 >= 60 is True, so THIS wins ...
elif score >= 90:
    print("A")          # ... and the A branch is unreachable for any score
```

This prints `D` for a 95. With `>=`-style tests, order from the **highest
boundary down** (as the grade assigner in [4.2](02-if-else.md) does), so
each test only sees what the previous ones rejected.

### Bug 3 — overlapping or gappy ranges

When you write both ends of every range by hand, it is easy to cover a
boundary twice — or not at all:

```python
bmi = 25.0

if bmi < 25:
    print("normal")
elif bmi > 25:
    print("overweight")
# exactly 25.0 matches NEITHER test - nothing prints for it!

print("done")
```

Only `done` appears: 25.0 fell through the crack between `< 25` and `> 25`.
The robust habit is to make each `elif` pick up exactly where the previous
test stopped, and let `else` own the final range — then no gap *can* exist:

```python
bmi = 25.0

if bmi < 18.5:
    print("underweight")
elif bmi < 25:
    print("normal")
elif bmi < 30:
    print("overweight")     # 25.0 lands here — every value has a home
else:
    print("obese")
```

## Style: branches people can read

Three habits, each cheap now and valuable forever:

**Prefer positive conditions.** `if is_ready:` reads instantly;
`if not is_missing:` makes readers do mental double-negation. When an `if`
has both branches, put the positive case first.

**No empty branches.** A branch containing only `pass` is a sign the
condition is written backwards — invert it and drop the dead limb:

```python
logged_in = False

# awkward: an empty branch just to reach the else
if logged_in:
    pass
else:
    print("please log in")

# better: test the case you act on
if not logged_in:
    print("please log in")
```

**Cap your nesting depth.** Two levels of `if` inside `if` is the practical
comfort limit; at three, stop and restructure — combine conditions with
`and`, use the guard pattern from [4.2](02-if-else.md), or split the logic
into a helper function. Deep pyramids are where branch bugs go to hide.

!!! warning "Common mistakes"
    - **No `case _` in a `match`.** If nothing matches, `match` does
      *nothing* — silently. Add a wildcard case unless you have proven every
      value is covered.
    - **Java habits in `match`:** adding `break` (not needed — there is no
      fallthrough) or stacking `case 6: case 7:` (that is a syntax error;
      write `case 6 | 7:`).
    - **Using a bare variable as a `case` pattern.** `case EXIT_CODE:` does
      not compare against your constant — a lone name in a pattern
      *captures* the subject into that name and matches everything. Match
      against literals (or dotted names like `Codes.EXIT`).
    - **`operations[op]` without checking membership.** An unknown key
      raises `KeyError`; guard with `if op in operations:` or use
      `.get(op, default)`.

## Check your understanding

1. In `describe_status`, the subject is `302`. Which cases does Python test,
   and why does the `404` case never run?

    ??? success "Answer"
        Python tests `case 200` (no match), then `case 301 | 302` (match —
        the block returns `"redirect"`). The statement ends the moment one
        case matches: no fallthrough exists, so `404` and everything below
        it are never considered.

2. A Java `switch` prints both `Tuesday` and `Wednesday` for `day = 2`.
   What is the bug, and why can the equivalent Python `match` not have it?

    ??? success "Answer"
        A missing `break` after the `case 2` body makes execution fall
        through into `case 3`. Python's `match` ends automatically after
        the first matching case's block — fallthrough does not exist in the
        language, so there is nothing to forget.

3. You must map 40 country codes to country names. `elif` chain, `match`,
   or dictionary — which fits best, and why?

    ??? success "Answer"
        A dictionary: `{"FR": "France", "JP": "Japan", ...}` with
        `.get(code, "unknown")`. The decision is pure key → value data — no
        conditions, no ranges — so a lookup table is shorter, faster to
        scan by eye, and trivial to extend or load from a file.

4. Predict the output, then explain the flaw:

    ```text
    price = 120
    if price >= 50:
        print("free shipping")
    elif price >= 100:
        print("free shipping + gift")
    ```

    ??? success "Answer"
        It prints `free shipping`. Since `120 >= 50` is `True`, the first
        branch wins and the more specific `>= 100` branch can never run —
        for *any* price. Fix the ordering: test `price >= 100` first, then
        `elif price >= 50:`.
