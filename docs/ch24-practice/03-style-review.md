# 24.3 Style, reviews, and readable code

Here is the empirical fact this whole section stands on: code is **read** far
more often than it is written — around ten times more, by most estimates, and
the ratio only grows as software lives longer.

Every line you write tonight will be re-read during debugging, re-read during
review, re-read by a teammate extending it, and re-read by you in six months
with no memory of writing it.

The interpreter doesn't care how the code looks; every reader after the
interpreter cares about almost nothing else. So we optimize for the common
case: we write for readers.

## Names that reveal intention

The single highest-leverage readability decision is what you call things. A
good name answers the reader's question *before it is asked*; a bad name is a
small tax charged on every single read, forever.

Try to work out what this function does before running it:

```python
def chk(l, n):
    c = 0
    for e in l:
        if e >= n:
            c += 1
    return c

print(chk([88, 71, 93, 64], 80))
```

You *can* decode it — the way you can read a smudged photocopy. Now the
same function, renamed and nothing else:

```python
def count_scores_at_or_above(scores, threshold):
    count = 0
    for score in scores:
        if score >= threshold:
            count += 1
    return count

print(count_scores_at_or_above([88, 71, 93, 64], threshold=80))
```

Identical output, identical bytecode shape — and zero decoding required.
The rules the second version follows:

- **Say the intention, not the mechanics**: `count_scores_at_or_above`,
  not `chk` or `process_list`. If you cannot name what a thing is *for*,
  you have found a design problem, not a naming problem.
- **No abbreviations**: `threshold`, not `n`; `score`, not `e`. You save
  two keystrokes once and pay comprehension interest for years.
  (One-letter names are fine only where convention makes them instantly
  clear: `i` for a loop index, `x` in a one-line mathematical lambda.)
- **Booleans read as questions**: prefix with `is_` / `has_` / `can_`, so
  conditions read as English. Watch how the call site improves:

```python
def delivery_status(is_paid, has_items_on_backorder):
    if is_paid and not has_items_on_backorder:
        return "ready to ship"
    return "waiting"

# The call site reads like a sentence:
print(delivery_status(is_paid=True, has_items_on_backorder=False))
print(delivery_status(is_paid=True, has_items_on_backorder=True))
```

Compare `if is_paid and not has_items_on_backorder:` with the version you
would get from names like `flag` and `status2` — the logic is the same;
the *reading* is not.

## Functions: small, one job, few parameters

Readable code is made of functions that do **one thing**, are named for
that thing, and are short enough to hold in your head. Here is the kind of
function that grows in the wild — a receipt builder where pricing rules,
totaling, and formatting are all tangled together, seasoned with
single-letter names:

```python
def do_it(d):
    r = []
    t = 0
    for x in d:
        p = x[1] * x[2]
        if x[3]:
            p = p - p * 0.1
        if x[1] >= 10:
            p = p - p * 0.05
        t = t + p
        r.append(x[0] + ": $" + str(round(p, 2)))
    if t > 100:
        t = t - 5
        r.append("bulk rebate: -$5")
    r.append("TOTAL: $" + str(round(t, 2)))
    return r

order = [("notebook", 3, 4.50, False),
         ("pen", 12, 1.20, True),
         ("desk lamp", 2, 39.99, False)]
for line in do_it(order):
    print(line)
```

It works. It is also a trap: to change *any* rule you must first
reverse-engineer *all* of them. (Quick — what is `x[3]`? What are the `0.1`
and the `0.05` for? Why `- 5`?)

The refactor does two things:

- **splits the function along its three jobs** — *price one line*, *format
  one line*, *assemble the receipt*;
- **promotes every magic number to a named constant.**

At the end, we prove the behavior didn't change by checking against the exact
five lines the tangle printed:

```python
SALE_DISCOUNT = 0.10          # storewide sale price cut
QUANTITY_DISCOUNT = 0.05      # buying 10+ of one item
QUANTITY_THRESHOLD = 10
REBATE_THRESHOLD = 100.00     # orders over this get a flat rebate
BULK_REBATE = 5.00

def line_price(quantity, unit_price, is_on_sale):
    price = quantity * unit_price
    if is_on_sale:
        price -= price * SALE_DISCOUNT
    if quantity >= QUANTITY_THRESHOLD:
        price -= price * QUANTITY_DISCOUNT
    return price

def format_receipt_line(name, price):
    return f"{name}: ${round(price, 2)}"

def build_receipt(order_lines):
    receipt = []
    total = 0
    for name, quantity, unit_price, is_on_sale in order_lines:
        price = line_price(quantity, unit_price, is_on_sale)
        total += price
        receipt.append(format_receipt_line(name, price))
    if total > REBATE_THRESHOLD:
        total -= BULK_REBATE
        receipt.append(f"bulk rebate: -${BULK_REBATE:.0f}")
    receipt.append(format_receipt_line("TOTAL", total))
    return receipt

order = [("notebook", 3, 4.50, False),
         ("pen", 12, 1.20, True),
         ("desk lamp", 2, 39.99, False)]
for line in build_receipt(order):
    print(line)

# Refactoring changes structure, never behavior. Prove it: these are the
# exact lines the tangled version printed.
expected = ["notebook: $13.5", "pen: $12.31", "desk lamp: $79.98",
            "bulk rebate: -$5", "TOTAL: $100.79"]
print("matches the tangle's output exactly:", build_receipt(order) == expected)
```

Same output, different future:

- "Change the sale discount" is now a one-constant edit.
- "Test the pricing rules" now means testing `line_price` in isolation
  ([Section 24.2](02-testing.md)).
- Each function is small enough to *name honestly*.

!!! tip "The real test of one job"
    If an accurate name for the function needs the word "and" in it, split
    the function.

Parameters follow the same budget: past three or four, readers lose track of
what goes where. Bundle related values into a class
([Chapter 12](../ch12-classes/index.md)) or a dataclass instead.

## Comments: why, not what

Comments that narrate *what* the code does are noise — the code already
says it, and when the code changes, the stale comment starts lying:

```text
count += 1            # add one to count        <- noise
prices.sort()         # sort the prices          <- noise
if age >= 18:         # check if age is >= 18    <- insulting noise
```

The comments worth writing record what the code *cannot* say: the reason,
the constraint, the surprise. Business context is the classic case:

```python
def monthly_price(annual_price):
    # Divide by 10, not 12: the yearly plan includes two free months.
    # This is a marketing decision (2024 pricing review) - do not "fix" it.
    return annual_price / 10

print(monthly_price(120.0))
```

Without that comment, `/ 10` looks exactly like a bug, and some well-meaning
reader eventually "corrects" it. With it, the code is safe from helpfulness.

The hierarchy of goodness, in order:

1. **Make the code so clear it needs no comment** — that is what the naming
   and function rules were for.
2. **Comment the *why* that remains.**

A *why* comment ages well, because reasons change more slowly than mechanics.

## Consistent style: let robots end the arguments

Every language community settles on a shared surface style so that all
code looks familiar to all readers. Python's is
**PEP 8**; your Java course follows the **Google Java Style Guide** (or a
close cousin). The essentials:

| Aspect | Python (PEP 8) | Java (Google style) |
| --- | --- | --- |
| Variables & functions | `snake_case` | `camelCase` |
| Classes | `PascalCase` | `PascalCase` |
| Constants | `UPPER_SNAKE_CASE` | `UPPER_SNAKE_CASE` |
| Indentation | 4 spaces | 2 spaces |
| Max line length | 79 (teams often 88–100) | 100 |
| Spacing | `x = f(a, b)` — spaces around `=`, after commas | same idea |

None of these choices matters much; *sharing* them matters enormously — and
arguing about them in code review is the biggest waste of goodwill in
software. So teams delegate the whole topic to robots:

- **Formatters** rewrite code into the standard shape. Python: `black`.
  Java: `google-java-format`.
- **Linters** flag suspicious patterns beyond formatting — unused variables,
  shadowed names, over-long functions. Python: `ruff`, `flake8`. Java:
  `checkstyle`.

A typical setup runs both automatically on every commit or in CI
([Section 24.1](01-git-workflow.md)), which retires the entire category of
"you used the wrong quotes" review comments. The robot is strict, instant, and
impossible to offend.

## The self-review checklist

The cheapest code review is the one you give yourself.

Before every commit, read your own diff — not the files, the *diff* — as if a
stranger wrote it, against a fixed list. Ours:

- [ ] Do all names say what they mean? Any `data2`, `temp`, `flag`, `x`
      left behind?
- [ ] Does each function do one nameable job, in a screenful or less?
- [ ] Any magic numbers that deserve a named constant?
- [ ] Do comments explain *why* — and are any of them now stale lies?
- [ ] Edge cases from the [checklist](02-testing.md): empty, boundary,
      invalid — handled and *tested*?
- [ ] Any leftover debugging `print()`s, commented-out corpses, or
      conflict markers?
- [ ] Does the commit message subject say what this change does, and the
      body say why?

Two quiet minutes with this list catches most of what a human reviewer
would spend their attention on, and lets them spend it on design instead.

## Reading other people's code

Joining any project means landing in ten thousand lines you didn't write.
Reading code is a learnable skill with a technique, and the technique is
*not* "start at line 1":

1. **Skim the skeleton first**: imports, then every `def` / `class` line,
   ignoring bodies. You now know the file's vocabulary and cast of
   characters.
2. **Find the entry point** — the `main()` function, the
   `if __name__ == "__main__":` block, the route handler, the test — and
   trace *one* realistic call all the way through, ignoring side quests.
3. **Read the tests** ([Section 24.2](02-testing.md)): they are worked
   examples of every behavior someone cared enough to pin down.
4. **Interrogate, don't just stare**: rename a confusing variable locally
   and see what breaks; add a `print`; step through in a debugger; write
   down each question and its answer. Active reading sticks.

And when you find something baffling, hold the humility rule: assume it made
sense to someone, find out why it's there, *then* judge. (`git log` and its
commit messages — [Section 24.1](01-git-workflow.md) — exist for exactly
this.)

Half the time the weird code is guarding a bug you haven't met yet, and the
comment explaining it is the one its author skipped writing.

!!! warning "Common mistakes"

    - **"I'll clean it up later."** Later never comes; code review is the
      last reliable gate. The tangle you merge today is the file everyone
      inherits for years.
    - **Renaming into vagueness.** `process_data(info)` is spelled like a
      good name but says nothing. The test is whether the name would let
      a reader *predict the behavior* without opening the body.
    - **Commenting instead of rewriting.** If a block needs a paragraph
      to explain *what* it does, the fix is extraction and naming, not
      prose. Save comments for *why*.
    - **Hand-enforcing style in reviews.** Nitpicking indentation wastes
      the one resource reviews run on — attention. Install the formatter,
      commit its config, and never speak of quotes again.

## Check your understanding

1. Rank these names for a variable holding the number of failed login
   attempts, and justify: `n`, `failed_login_count`, `flc`, `counter`.

    ??? success "Answer"
        `failed_login_count` (says exactly what and why), then `counter`
        (right species, no context), then `n` (bare but at least honestly
        anonymous), then `flc` last — an abbreviation pretends to carry
        meaning while forcing every reader to reconstruct it.

2. In the receipt refactor, the constant `REBATE_THRESHOLD = 100.00`
   replaced a bare `100`. Name *two* distinct benefits.

    ??? success "Answer"
        Readability: `total > REBATE_THRESHOLD` states a rule, while
        `t > 100` states arithmetic — the reader learns *what the 100
        means*. Maintainability: when the rule changes, there is exactly
        one place to edit — no hunting for which of the several `100`s
        in the file is the rebate one (and no missing one of them).

3. Which of these comments is worth keeping, and what is wrong with the
   other? (a) `total *= 0.9  # multiply total by 0.9`
   (b) `total *= 0.9  # partners get 10% off per the 2023 reseller
   agreement`

    ??? success "Answer"
        Keep (b): it records a *reason* that lives nowhere in the code —
        remove it and the discount looks arbitrary or wrong. Comment (a)
        restates the mechanics, adds nothing, and will silently become a
        lie the day the number changes to 0.85.

4. Your teammate's PR is correct but uses 2-space indentation and
   `camelCase` in Python. What is the *systemic* fix — and why is a
   review comment the wrong tool?

    ??? success "Answer"
        Add an auto-formatter (e.g. `black`) and a linter to the repo,
        run in CI or a commit hook, so style is applied mechanically for
        everyone, forever. A review comment fixes one file once, costs
        social capital, and invites a style debate — the robot enforces
        the same rule instantly, uniformly, and impersonally.
