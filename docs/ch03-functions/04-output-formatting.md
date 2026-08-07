# 3.4 Formatting output

A program that computes the right answer but prints `27.219999999999999` is
only half finished. Output is the part of your program people actually see,
and making it clean — two decimals for money, columns that line up, thousands
separators in big numbers — is a small skill with outsized payoff. Python's
modern tool for this is the **f-string**, a tiny formatting language that
lives inside your string literals. This section takes you from `print`'s own
options to f-string format specs to a fully aligned receipt.

## Fine-tuning `print`: `sep` and `end`

You have been giving `print` several values at once for a while now. Two
optional keyword arguments control how it joins and finishes them: `sep` is
the text placed *between* values (default: one space), and `end` is the text
printed *after* the last one (default: a newline, which is why each `print`
normally starts a fresh line).

```python
print("2026", "8", "7")
print("2026", "8", "7", sep="-")     # join with hyphens instead of spaces
print("Loading", end="")             # suppress the newline...
print("...", end="")                 # ...so the next prints continue the line
print("done")
print("A", "B", "C", sep="", end="!\n")
```

```text
2026 8 7
2026-8-7
Loading...done
ABC!
```

`sep` and `end` are your first taste of keyword arguments doing real work:
the same function, reshaped by two named options.

## f-strings: expressions inside your text

An **f-string** is a string literal with an `f` immediately before the
opening quote. Inside it, anything wrapped in curly braces `{}` is evaluated
as a Python expression and its value is spliced into the text:

```python
name = "Ada"
age = 36
print(f"{name} is {age} years old.")
print(f"In four years she will be {age + 4}.")   # any expression works
print(f"{name.upper()} has {len(name)} letters.")
```

```text
Ada is 36 years old.
In four years she will be 40.
ADA has 3 letters.
```

Without the `f`, the braces are just characters — `"{name}"` prints
literally as `{name}`. With it, the string becomes a template. Keep the
expressions inside braces *simple* (a variable, a small computation, one
method call); anything cleverer belongs on its own line above.

## Format specs: controlling how values appear

After the expression, a colon introduces a **format spec** — instructions
for how to render the value. The pattern is `{expression:spec}`. Specs
compose from a few parts, in this order: *alignment and width*, a *comma*
for thousands, a *precision*, and a *type letter*. You will use a handful of
combinations constantly.

### Precision: `.2f` and friends

The spec `.2f` means "**f**ixed-point notation, 2 digits after the decimal
point" — the workhorse for money and measurements. The value is *rounded*,
and trailing zeros are kept, so amounts like `7.5` print as `7.50`:

```python
pi = 3.14159265
print(f"{pi:.2f}")
print(f"{pi:.4f}")

price = 7.5
print(f"{price:.2f}")    # money wants exactly two decimals

third = 1 / 3
print(f"{third:.3f}")
```

```text
3.14
3.1416
7.50
0.333
```

### Width and alignment: `>8`, `<8`, `^8`

A number after the colon reserves that many columns; `<`, `>`, and `^` pick
left, right, or centre alignment within them. The brackets in this demo show
exactly where the padding spaces go:

```python
word = "cat"
print(f"[{word:>8}]")    # right-aligned in 8 columns
print(f"[{word:<8}]")    # left-aligned
print(f"[{word:^8}]")    # centred

n = 42
print(f"[{n:>8}]")
print(f"[{n:08}]")       # pad with zeros instead of spaces
```

```text
[     cat]
[cat     ]
[  cat   ]
[      42]
[00000042]
```

Left out, alignment has sensible defaults: strings align left, numbers align
right — which is exactly what tables want.

### Thousands separators and percentages: `,` and `%`

```python
population = 8025000000
print(f"{population:,}")     # commas every three digits

fraction = 0.8732
print(f"{fraction:.1%}")     # multiply by 100, add %, 1 decimal
print(f"{fraction:.0%}")

debt = 1234567.891
print(f"{debt:,.2f}")        # specs combine: commas AND two decimals
```

```text
8,025,000,000
87.3%
87%
1,234,567.89
```

Note what `%` does: it *multiplies by 100* on the way out, because it expects
a fraction between 0 and 1. Feeding it a value that is already a percentage
(`f"{87:.0%}"`) produces a startling `8700%`.

The combinations you will reach for most often:

| Spec | Meaning | Example | Output |
| --- | --- | --- | --- |
| `:.2f` | fixed-point, 2 decimals | `f"{3.14159:.2f}"` | `3.14` |
| `:>8` | right-align, width 8 | `f"{'cat':>8}"` | `     cat` |
| `:<8` | left-align, width 8 | `f"{'cat':<8}"` | `cat     ` |
| `:^8` | centre, width 8 | `f"{'cat':^8}"` | `  cat   ` |
| `:,` | thousands separators | `f"{1234567:,}"` | `1,234,567` |
| `:.1%` | percentage, 1 decimal | `f"{0.873:.1%}"` | `87.3%` |
| `:8.2f` | width 8 *and* 2 decimals | `f"{3.5:8.2f}"` | `    3.50` |

## Worked example: a receipt printer

Alignment specs shine when every row uses the *same* column widths — the
columns then line up automatically, like a spreadsheet. Here is a small
receipt: item names left-aligned in 14 columns, quantities right-aligned in
3, prices right-aligned in 7 and 8 with two decimals. Note the nested quotes:
the f-string uses double quotes, so the string literals *inside* the braces
use single quotes.

```python
print(f"{'MORNING MARKET':^32}")
print(f"{'Item':<14}{'Qty':>3}{'Each':>7}{'Total':>8}")
print("-" * 32)
print(f"{'Green tea':<14}{2:>3}{4.50:>7.2f}{2 * 4.50:>8.2f}")
print(f"{'Sourdough':<14}{1:>3}{6.25:>7.2f}{1 * 6.25:>8.2f}")
print(f"{'Blueberries':<14}{3:>3}{3.99:>7.2f}{3 * 3.99:>8.2f}")
print("-" * 32)

total = 2 * 4.50 + 1 * 6.25 + 3 * 3.99
print(f"{'TOTAL':<24}{total:>8.2f}")
```

```text
         MORNING MARKET         
Item          Qty   Each   Total
--------------------------------
Green tea       2   4.50    9.00
Sourdough       1   6.25    6.25
Blueberries     3   3.99   11.97
--------------------------------
TOTAL                      27.22
```

Every row adds up to the same total width ($14 + 3 + 7 + 8 = 32$), so the
ruled lines fit exactly. This is also your defence against floating-point
noise from [Chapter 5](../ch05-under-the-hood/index.md): the raw `total` is
actually `27.219999999999999`, but `:.2f` rounds it for display. Formatting
fixes the *display*, not the stored value.

## The older styles you will still meet

Two earlier formatting systems survive in tutorials and older code. The `%`
operator is printf-style formatting inherited from C, and `.format()` was
the standard before f-strings arrived in Python 3.6. Recognise them; write
f-strings.

```python
name = "Ada"
score = 9.75
print("%s scored %.2f" % (name, score))          # oldest: printf-style
print("{} scored {:.2f}".format(name, score))    # older: .format()
print(f"{name} scored {score:.2f}")              # modern: f-string
```

```text
Ada scored 9.75
Ada scored 9.75
Ada scored 9.75
```

The good news: the *spec language* (`.2f`, `>8`, `,`) is the same in
`.format()` and f-strings, and Java's `printf` uses close cousins of the `%`
codes — so this knowledge transfers everywhere:

=== "Python"

    ```python
    name = "Ada"
    score = 9.756
    print(f"{name} scored {score:.2f}")
    print(f"|{42:>5}|")
    print(f"{1234567:,}")
    ```

=== "Java"

    ```java
    String name = "Ada";
    double score = 9.756;
    System.out.printf("%s scored %.2f%n", name, score);
    System.out.printf("|%5d|%n", 42);
    System.out.printf("%,d%n", 1234567);
    ```

Both print `Ada scored 9.76`, `|   42|`, and `1,234,567`. The mapping is
mechanical:

| Java `printf` | Python f-string | Meaning |
| --- | --- | --- |
| `%s` | `{x}` | insert as text |
| `%d` | `{x}` or `{x:d}` | integer |
| `%.2f` | `{x:.2f}` | 2-decimal fixed point |
| `%5d` | `{x:>5}` | right-align, width 5 |
| `%-10s` | `{x:<10}` | left-align, width 10 |
| `%,d` | `{x:,}` | thousands separators |
| `%n` | (automatic) | newline — `print` adds its own |

!!! warning "Common mistakes"

    - **Forgetting the `f`** — `print("{name}")` prints the braces
      literally. No error, just wrong output, which makes it easy to miss.
    - **Quote collisions** — `f"{"Item"}"` breaks because the inner quotes
      end the string. Use different quotes inside: `f"{'Item':<14}"`.
    - **Feeding `%` a whole percentage** — `f"{87:.1%}"` prints `8700.0%`.
      The `%` spec expects a *fraction* like `0.87`.
    - **Expecting `:.2f` to change the number** — formatting affects display
      only; the variable still holds the full-precision value. Rounding for
      *computation* is `round()`'s job.

## Check your understanding

1. Without running it, what does `print(f"{7 / 2:.1f}")` output?

    ??? success "Answer"
        `3.5` — the expression `7 / 2` evaluates to `3.5`, and `.1f` shows
        one decimal place.

2. What exactly does `print("a", "b", "c", sep="--", end="|")` print, and
   does the next `print` start on the same line or a new one?

    ??? success "Answer"
        It prints `a--b--c|` with **no** newline (since `end="|"` replaced
        it), so the next `print` continues on the same line.

3. You want the header `Name` left-aligned in 10 columns followed by `Score`
   right-aligned in 6. Write the f-string.

    ??? success "Answer"
        `f"{'Name':<10}{'Score':>6}"` — `Name` gets 6 trailing spaces to fill
        its 10 columns, and `Score` gets 1 leading space to fill its 6.
        (Strings default to left alignment, so `{'Name':10}` also works for
        the first part.)

4. A test score is stored as `ratio = 0.916`. Which prints `91.6%` — 
   `f"{ratio:.1%}"` or `f"{ratio * 100:.1%}"`?

    ??? success "Answer"
        `f"{ratio:.1%}"`. The `%` spec multiplies by 100 itself; the second
        version multiplies *twice* and prints `9160.0%`.
