# 4.1 Booleans and logic

Before a program can *decide* anything, it needs a way to represent the
answer to a yes/no question. That is exactly what a **Boolean** is: a value
that is either `True` or `False`, nothing else. Every `if` statement you will
ever write boils down to one Boolean; this section is about where those
Booleans come from and how to combine them.

## True and False are values

`True` and `False` are ordinary Python values, just like `42` or `"hello"`.
They have their own type, `bool`, and you can store them in variables, print
them, and pass them to functions.

```python
is_raining = False
print(is_raining)
print(type(is_raining))
print(type(True))
```

Running this prints `False`, then `<class 'bool'>` twice. Note the
capitalisation: Python spells them `True` and `False` — writing `true` (as in
Java) is a `NameError`, because Python thinks you mean a variable named
`true` that does not exist.

## Comparison operators

You will rarely type `True` or `False` by hand. Most Booleans are *produced*
by **comparison operators** — operators that ask a question about two values
and answer with a `bool`:

| Operator | Question it asks       | Example      | Result  |
| -------- | ---------------------- | ------------ | ------- |
| `==`     | equal?                 | `3 == 3`     | `True`  |
| `!=`     | not equal?             | `3 != 3`     | `False` |
| `<`      | less than?             | `2 < 5`      | `True`  |
| `<=`     | less than or equal?    | `5 <= 5`     | `True`  |
| `>`      | greater than?          | `2 > 5`      | `False` |
| `>=`     | greater than or equal? | `5 >= 6`     | `False` |

Note the double equals sign: `==` *compares*, while a single `=` *assigns*.
Mixing them up is the classic beginner bug — Python at least refuses to run
`if x = 5:` (we demo the error in
[section 4.4](04-switch-style-debug.md)).

```python
x = 7
print(x == 7)    # True
print(x != 7)    # False
print(x < 10)    # True
print(x <= 7)    # True  — "or equal" makes the difference here
print(x > 7)     # False
print(x >= 8)    # False
```

### Comparing strings

The same six operators work on strings. Equality is what you expect —
`"cat" == "cat"` is `True` — and the ordering operators compare
**lexicographically**: character by character, using each character's
underlying code number (in which every uppercase letter comes before every
lowercase letter, and digits come before both kinds of letters).

```python
print("apple" < "banana")   # True  — 'a' comes before 'b'
print("car" < "cat")        # True  — first difference: 'r' < 't'
print("Zoo" < "apple")      # True  — uppercase sorts before lowercase!
print("10" < "9")           # True  — strings compare digit by digit: '1' < '9'
print("apple" == "Apple")   # False — case matters for equality too
```

The last two lines are famous traps: `"10" < "9"` is `True` because these are
*strings*, not numbers — Python compares the first characters `'1'` and
`'9'`, and never looks further. If you want numeric order, convert first:
`int("10") < int("9")` is `False`, as it should be.

## Combining tests: and, or, not

One comparison is often not enough — "you may enter if you are 18 *or older
and* you have a ticket". Python combines Booleans with three **logical
operators**, written as plain English words. Their complete behaviour fits in
three small **truth tables**:

`a and b` — `True` only when *both* sides are `True`:

| `a`     | `b`     | `a and b` |
| ------- | ------- | --------- |
| `True`  | `True`  | `True`    |
| `True`  | `False` | `False`   |
| `False` | `True`  | `False`   |
| `False` | `False` | `False`   |

`a or b` — `True` when *at least one* side is `True`:

| `a`     | `b`     | `a or b` |
| ------- | ------- | -------- |
| `True`  | `True`  | `True`   |
| `True`  | `False` | `True`   |
| `False` | `True`  | `True`   |
| `False` | `False` | `False`  |

`not a` — flips the value:

| `a`     | `not a` |
| ------- | ------- |
| `True`  | `False` |
| `False` | `True`  |

```python
age = 20
has_ticket = True

print(age >= 18 and has_ticket)   # True  — both parts are True
print(age >= 65 or has_ticket)    # True  — the second part is True
print(not has_ticket)             # False — flips True
```

When you mix the three, `not` binds tightest, then `and`, then `or` — just
like `*` binds tighter than `+` in arithmetic. When in doubt, add
parentheses; they cost nothing and make the meaning obvious.

```python
print(not True and False)       # False — means (not True) and False
print(not (True and False))     # True  — parentheses change the grouping
print(True or False and False)  # True  — and binds tighter: True or (False)
```

One trap deserves its own demo. To test "x is 5 or 6", you *must* repeat the
comparison — `or` connects two complete Boolean questions, not two
alternatives for one question:

```python
x = 3
print(x == 5 or 6)         # 6      — wrong! Python reads (x == 5) or (6)
print(x == 5 or x == 6)    # False  — correct: two full comparisons
print(x in (5, 6))         # False  — even neater for a set of options
```

The first line prints `6`, not `False`, because `or` returns one of its
operands and the number `6` counts as "true-ish" (see truthiness below). The
condition would be taken *every time* — a silent, painful bug. (Why `or`
returns an operand instead of a plain `bool` is the short-circuit story of
[Chapter 5](../ch05-under-the-hood/02-shortcuts-gotchas.md).)

## De Morgan's laws

How do you negate a *combined* condition? Two rules from 19th-century
logician Augustus De Morgan cover it — when the `not` moves inside the
parentheses, `and` and `or` swap:

$$
\lnot(A \land B) = (\lnot A) \lor (\lnot B)
\qquad\qquad
\lnot(A \lor B) = (\lnot A) \land (\lnot B)
$$

In Python: `not (a and b)` equals `(not a) or (not b)`, and `not (a or b)`
equals `(not a) and (not b)`. You do not have to take our word for it — with
only two Boolean inputs there are exactly four combinations, so we can check
*all* of them:

```python
from itertools import product

print("a      b      | law 1 holds  law 2 holds")
for a, b in product([False, True], repeat=2):
    law1 = (not (a and b)) == ((not a) or (not b))
    law2 = (not (a or b)) == ((not a) and (not b))
    print(f"{a!s:6} {b!s:6} | {law1!s:12} {law2!s}")

print("Both laws hold for every possible input — verified.")
```

Every row prints `True` for both laws: this is a complete proof by
exhaustive checking, a technique you will meet again when testing code. The
practical payoff: `not (age >= 18 and has_ticket)` can be rewritten as
`age < 18 or not has_ticket` — often much easier to read.

## Truthiness: when non-Booleans act like Booleans

Python lets *any* value stand in where a Boolean is expected. The rule:
zero and "empty" things count as `False`; everything else counts as `True`.
The `bool()` function shows you how any value converts:

```python
print(bool(""), bool("hi"))     # False True  — empty vs non-empty string
print(bool(0), bool(42))       # False True  — zero vs non-zero number
print(bool([]), bool([1, 2]))  # False True  — empty vs non-empty list
print(bool(None))              # False       — "no value at all"

name = ""
if name:                        # relies on truthiness
    print("Hello,", name)
else:
    print("No name given")
```

This is idiomatic Python and you will see `if name:` in real code. But
truthiness has sharp corners:

```python
print(bool("0"))    # True — the *string* "0" is not empty!
print(bool(" "))    # True — a space is still a character
print(bool(-1))     # True — only exactly zero is falsy
```

!!! tip "Prefer explicit comparisons while learning"
    `if name != "":` and `if count == 0:` say exactly what they mean, and
    they cannot surprise you the way `bool("0") == True` does. Reach for
    truthiness once the table above is second nature — until then, spell the
    comparison out.

## Chained comparisons

Mathematics writes "x is between 0 and 10" as $0 \le x < 10$, and Python lets
you write exactly that. A **chained comparison** `a < b < c` means
`a < b and b < c` (with `b` evaluated only once):

```python
x = 7
print(0 <= x < 10)          # True — reads just like the maths
print(0 <= x and x < 10)    # True — the same test, spelled out

temperature = 21
if 18 <= temperature <= 24:
    print("comfortable room")
```

Java has no such feature — this is one of the places the two languages
genuinely part ways:

=== "Python"

    ```python
    x = 7
    print(0 <= x < 10)   # chained comparison — perfectly legal
    ```

=== "Java"

    ```java
    int x = 7;
    // System.out.println(0 <= x < 10);   // does NOT compile:
    // (0 <= x) is a boolean, and "boolean < int" is a type error.
    System.out.println(0 <= x && x < 10); // spell out both halves
    ```

!!! warning "Common mistakes"
    - **Writing `true` or `false`** (lowercase, Java-style). Python raises
      `NameError: name 'true' is not defined`. Capitalise: `True`, `False`.
    - **`x == 5 or 6`** — always acts true, because `6` is truthy. Write
      `x == 5 or x == 6`, or `x in (5, 6)`.
    - **Comparing number-strings as strings**: `"10" < "9"` is `True`.
      Convert with `int()` before comparing numerically.
    - **Over-trusting truthiness**: `bool("0")` and `bool(" ")` are both
      `True`. Only *empty* strings are falsy — the content is irrelevant.

## Check your understanding

1. What does `print("Zebra" < "apple")` output, and why?

    ??? success "Answer"
        `True`. String comparison uses character code numbers, and every
        uppercase letter has a smaller code than every lowercase letter, so
        `'Z'` sorts before `'a'` — even though "Zebra" comes after "apple"
        in a dictionary.

2. Evaluate by hand, then check by running: `not False and True` — is it
   `True` or `False`?

    ??? success "Answer"
        `True`. `not` binds tightest, so this reads
        `(not False) and True` → `True and True` → `True`. If `not` applied
        to the whole thing it would be `not (False and True)` → `True` as
        well here — but try `not True or True`: grouping as
        `(not True) or True` gives `True`, while `not (True or True)` gives
        `False`. Precedence matters.

3. Use De Morgan's laws to rewrite `not (a and not b)` without the outer
   `not`.

    ??? success "Answer"
        `(not a) or b`. The `not` distributes over the `and` (flipping it to
        `or`), negating each side: `not a` stays, and `not (not b)`
        simplifies to `b`.

4. A beginner writes `if answer == "y" or "yes":` and reports that the
   branch runs no matter what the user typed. Explain the bug and fix it.

    ??? success "Answer"
        Python reads it as `(answer == "y") or ("yes")`. The string `"yes"`
        is non-empty, hence truthy, so the whole condition is always true.
        Fix: `if answer == "y" or answer == "yes":` or, more neatly,
        `if answer in ("y", "yes"):`.
