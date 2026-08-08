# 5.2 Short-circuits, compound assignment, gotchas

Some of the most confusing bugs in beginner code come not from big concepts
but from small syntax: an `and` that never ran its right half, a `++x` that
looked like it incremented and didn't, an `else` that quietly attached itself
to the wrong `if`. This section collects those little mechanisms in one place
— how Python evaluates them, where Java differs, and the idioms that turn each
trap into a tool.

## `and` / `or` stop early — short-circuit evaluation

You know from [Chapter 4](../ch04-branching/01-booleans-logic.md) what `and`
and `or` answer. Here is *how* they answer: lazily.

- **`and` stops at a false left side.** The result is already `False`, so the
  right side is **never evaluated**.
- **`or` stops at a true left side.** The result is already `True`, so again
  the right side never runs.

This is called **short-circuit evaluation**, and we can prove it with a
function that announces every time it runs:

```python
def check(label, value):
    print(f"  ...checking {label}")
    return value

print("False and B:")
result = check("A", False) and check("B", True)
print("result:", result)

print("True or B:")
result = check("A", True) or check("B", True)
print("result:", result)
```

Output:

```text
False and B:
  ...checking A
result: False
True or B:
  ...checking A
result: True
```

In both runs, *B is never checked* — no `...checking B` line ever appears. The
right side is not "evaluated and ignored"; it simply never runs. That matters
whenever the right side does something observable: prints, modifies data, or
— most importantly — might crash.

!!! info "Java corner"
    Java's `&&` and `||` short-circuit exactly the same way. Java also has
    non-short-circuit versions, `&` and `|`, which always evaluate both sides
    — a classic source of Java bugs when someone types one symbol instead of
    two.

## The guard idiom: make the left side your bodyguard

Short-circuiting has one killer application: put a *safety check* on the left
so that a *dangerous expression* on the right only runs when it is safe. The
classic example guards a division:

```python
x = 0     # imagine the user typed 0

if x != 0 and 1 / x > 0.5:
    print("the reciprocal of x is big")
else:
    print("x is zero, or its reciprocal is small")
```

With `x = 0`, the left side `x != 0` is `False`, so `and` short-circuits and
`1 / x` **never executes** — no crash, and the `else` branch runs. Now watch
what happens if you write the same test with the guard on the wrong side:

```python
# raises ZeroDivisionError
x = 0     # imagine the user typed 0

if 1 / x > 0.5 and x != 0:      # guard is too late — 1/x runs first!
    print("this line is never reached")
```

Same two conditions, opposite order, and the program dies with
`ZeroDivisionError: division by zero`.

!!! tip "The guard goes first"
    Put the cheap safety check on the **left** of `and` and the dangerous
    expression on the right. Short-circuiting then guarantees the dangerous
    half never runs unless the check has already passed.

The same idiom protects any "check before you touch" situation — `n != 0 and
total / n > 90`, or (once you know lists) checking a list is non-empty before
reading its first element.

## Compound assignment: `+=` and its family

"Take the variable, change it, store it back" is so common that Python (like
Java, and C before it) has shorthand for it:

| Shorthand  | Same as           | Note                              |
|------------|-------------------|-----------------------------------|
| `x += 5`   | `x = x + 5`       | works on strings too: `s += "!"`  |
| `x -= 2`   | `x = x - 2`       |                                   |
| `x *= 3`   | `x = x * 3`       |                                   |
| `x /= 4`   | `x = x / 4`       | true division — result is a float |
| `x //= 4`  | `x = x // 4`      | floor division                    |
| `x %= 3`   | `x = x % 3`       | remainder                         |
| `x **= 2`  | `x = x ** 2`      | power                             |

```python
score = 10
score += 5      # 15
score -= 2      # 13
score *= 3      # 39
score //= 4     # 9  (39 // 4 floors to 9)
print(score)
```

This prints `9`. Read `x += 5` exactly as you read `x = x + 1`: *evaluate the
whole right-hand side first, then bind the name to the result.* That is why
`x = x + 1` is not a paradox — the `x + 1` on the right uses the *old* value,
finishes computing, and only then does the name `x` move to the new value.

For numbers and strings, `x += 1` and `x = x + 1` behave identically. For
lists there is a genuinely subtle difference, which needs the memory picture
of the [next section](03-stack-heap.md) and is settled properly in
[Chapter 9](../ch09-collections/01-references.md).

## Python has no `++` — and `++x` is a trap

Java and C programmers increment with `count++` or `++count`. Python
deliberately has no such operator; the idiom is `count += 1`. The postfix form
at least fails loudly:

```python
# raises SyntaxError
x = 5
x++
```

But here is the nasty part — the *prefix* form does **not** fail. It runs,
silently, and does nothing you wanted:

```python
x = 5
print(++x)      # 5  — not 6!
print(--x)      # 5  — not 4!
print(+-x)      # -5
print(x)        # 5 — x itself never changed
```

Why? Python parses `++x` as `+(+x)`: the **unary plus** operator applied
twice. Unary plus leaves a number unchanged, so `++x` is just `x`; likewise
`--x` is `-(-x)`, which is also `x`. No error, no increment — the worst kind
of bug, because the program keeps running with a value that never changes.
If you catch yourself writing `++`, your fingers are speaking Java; translate
to `x += 1`.

## The dangling `else` — a Java trap Python cannot have

In Java, indentation is decoration: the compiler reads only braces and
keywords. That allows a famous illusion called the **dangling else**, where
the code *looks* like it does one thing and *compiles* as another:

=== "Java — compiles, but lies"

    ```java
    int a = -1, b = 5;
    if (a > 0)
        if (b > 0)
            System.out.println("both positive");
    else                                        // lines up with the FIRST if...
        System.out.println("a is not positive");
    ```

=== "Python — indentation is law"

    ```python
    a, b = -1, 5
    if a > 0:
        if b > 0:
            print("both positive")
    else:
        print("a is not positive")
    ```

In the Java version, the indentation says the `else` belongs to `if (a > 0)`.
The compiler disagrees: **an `else` binds to the nearest unmatched `if`**, so
it actually pairs with `if (b > 0)`.

Follow that through with `a = -1`. The outer condition is false, so the entire
inner `if`/`else` is skipped, and the program prints *nothing at all* — while
the programmer confidently expects `a is not positive`. The Java fix is to
always write braces `{ }`.

Run the Python version: it prints `a is not positive`, exactly what it looks
like. Python has no dangling else *because indentation is the syntax* — the
`else` at column 0 can only belong to the `if` at column 0. What you see is
what executes. (The price: Python programs with inconsistent indentation don't
run at all, as you may have discovered already.)

## Conditional expressions: a choice inside an expression

Sometimes a full `if`/`else` *statement* is heavy machinery for a small choice
of value. Both languages offer a one-line **conditional expression**:

```python
n = 7
parity = "even" if n % 2 == 0 else "odd"
print(n, "is", parity)

# it is an expression, so it can live anywhere a value can:
print("big" if n > 100 else "small")
```

Output:

```text
7 is odd
small
```

=== "Python"

    ```python
    n = 7
    label = "even" if n % 2 == 0 else "odd"
    print(label)
    ```

=== "Java"

    ```java
    int n = 7;
    String label = (n % 2 == 0) ? "even" : "odd";
    ```

Note the different word orders:

| Language | Word order |
| -------- | ---------- |
| Java     | `condition ? value-if-true : value-if-false` |
| Python   | `value-if-true if condition else value-if-false` |

Python puts the happy path first, like the English sentence "coffee, if it's
morning, else tea." Both languages short-circuit: only the chosen branch is
evaluated.

Use conditional expressions for short, simple choices of a value. The moment
you feel tempted to nest one inside another, switch back to an honest `if`
statement.

!!! warning "Common mistakes"
    - **Putting the guard on the wrong side**: `1/x > 0.5 and x != 0` crashes
      on `x = 0`; the check must come *before* the danger.
    - **Writing `++count`**: it is legal Python that silently does nothing.
      The increment is `count += 1`.
    - **Expecting the right side of `and`/`or` to run**: code with side
      effects (like `print`) on the right side may be skipped entirely.
    - **Trusting indentation in Java snippets**: without braces, `else` binds
      to the nearest `if`, whatever the indentation suggests. In Python this
      cannot happen — but only because you *must* indent correctly.

## Check your understanding

1. What does this print?

    ```text
    def probe(name, value):
        print("probe:", name)
        return value

    result = probe("A", True) or probe("B", False)
    ```

    ??? success "Answer"
        Only `probe: A`. Since the left side of `or` is `True`, the answer is
        already decided and `probe("B", ...)` never runs. (`result` is `True`.)

2. Rewrite `if len_items != 0 and total / len_items >= 90:` with the two
   conditions swapped. What changes when `len_items` is `0`?

    ??? success "Answer"
        `if total / len_items >= 90 and len_items != 0:` now performs the
        division *first*, so with `len_items = 0` it raises
        `ZeroDivisionError` instead of quietly evaluating to `False`.

3. After `x = 8; x //= 3; x **= 2`, what is `x`?

    ??? success "Answer"
        `x //= 3` floors `8 / 3` to `2`; `x **= 2` squares it. `x` is `4`.

4. A Java-trained friend writes `++lives` inside a Python game loop and
   reports that "lives is stuck". Explain the bug in one sentence and give
   the fix.

    ??? success "Answer"
        Python parses `++lives` as `+(+lives)` — unary plus applied twice —
        which computes the same value and throws it away, changing nothing;
        the fix is `lives += 1`.
