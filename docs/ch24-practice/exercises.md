# Exercises

These exercises rehearse the whole practice loop: describing changes,
merging them, testing them, and making them readable. Several put you in
the reviewer's chair — the fastest way to grow as an author is a stint as
the audience. Do Exercise 24.4 on paper *before* running anything.

### Exercise 24.1 — Repair the commit subjects ●

Rewrite each subject line to follow the rules from
[Section 24.1](01-git-workflow.md): imperative mood, capitalized, at most
50 characters, no trailing period.

1. `fixed the login bug.`
2. `Updating documentation for the new API endpoints because they changed`
3. `stuff`

??? success "Solution"

    ```python
    repairs = [
        ("fixed the login bug.",
         "Fix crash when logging in with an empty password"),
        ("Updating documentation for the new API endpoints because they changed",
         "Document the new API endpoints"),
        ("stuff",
         "Add input validation to the signup form"),
    ]
    for before, after in repairs:
        print(f"BEFORE: {before}")
        print(f"AFTER : {after}   ({len(after)} chars)")
        print()
    ```

    Each repair states *what the commit does* in the imperative ("if
    applied, this commit will …"), and pushes any *because…* material
    into the body. Note that `stuff` cannot be repaired without knowing
    the change — a subject line is a summary, and you cannot summarize
    what you cannot name.

### Exercise 24.2 — Write the message for this diff ●

A teammate shows you this diff and the context: the site advertises
"free shipping on orders of $50 or more", and a customer with a $50.00
order was charged $5 (bug report #142). Write the full commit message —
subject and body.

```text
--- a/checkout.py
+++ b/checkout.py
@@ -12,7 +12,7 @@ def shipping_fee(total):
-    if total > 50:
+    if total >= 50:
         return 0
     return 5
```

??? success "Solution"

    ```python
    message = """Give free shipping at exactly $50

    The site advertises free shipping on orders of $50 or more, but
    shipping_fee() used a strict comparison, so a $50.00 order was
    charged the $5 fee (bug report #142). Use >= so the boundary case
    matches the advertised policy. Adds a regression test at the
    threshold.
    """
    print(message)
    ```

    The subject says what the change does in under 50 characters; the
    body carries the *why*: the policy, the symptom, the report number.
    Notice the body never narrates the diff ("changed > to >=") — the
    diff shows that already; it explains why `>=` is the *correct*
    operator, which the diff cannot.

### Exercise 24.3 — Resolve the conflict ●●

You merged and Git left this in `pricing.py`. Your branch (`HEAD`) raised
the member rate for a holiday promotion; meanwhile, `update-member-rate`
merged a finance-approved permanent change to 0.12, and the changelog says
the promotion was cancelled. Produce the final file content, and list the
Git commands that finish the job.

```text
def discount(price, is_member):
<<<<<<< HEAD
    rate = 0.15 if is_member else 0.05
=======
    rate = 0.12 if is_member else 0.05
>>>>>>> update-member-rate
    return price * (1 - rate)
```

??? success "Solution"

    ```python
    # The resolved file - their line wins (promotion cancelled),
    # and every marker line is gone:
    def discount(price, is_member):
        rate = 0.12 if is_member else 0.05
        return price * (1 - rate)

    print(discount(100.0, is_member=True))    # 88.0
    print(discount(100.0, is_member=False))   # 95.0
    ```

    Then: `git add pricing.py` and `git commit` to complete the merge
    (rerunning the tests before committing). The resolution itself was a
    *human* decision made from context — the cancelled promotion — which
    is exactly why Git refused to make it. Keeping 0.15, or averaging
    the two, would each produce valid Python and wrong business.

### Exercise 24.4 — Predict the table's verdicts ●●

A teammate wrote `shipping_fee` with `> 50` instead of `>= 50`. *Before
running*, predict each row's verdict (`ok` or `FAIL`) in this
table-driven suite — then run and check yourself.

```python
def shipping_fee(total):
    return 0 if total > 50 else 5      # bug: should be >= 50

cases = [(0, 5), (49.99, 5), (50, 0), (50.01, 0), (1000, 0)]

for total, expected in cases:
    actual = shipping_fee(total)
    verdict = "ok  " if actual == expected else "FAIL"
    print(f"{verdict} shipping_fee({total}) -> {actual}  (expected {expected})")
```

??? success "Solution"

    ```python
    def shipping_fee(total):
        return 0 if total > 50 else 5

    cases = [(0, 5), (49.99, 5), (50, 0), (50.01, 0), (1000, 0)]
    for total, expected in cases:
        actual = shipping_fee(total)
        verdict = "ok  " if actual == expected else "FAIL"
        print(f"{verdict} shipping_fee({total}) -> {actual}  (expected {expected})")
    ```

    Only `(50, 0)` fails: with `>`, a $50.00 order pays the fee
    (`actual` 5, expected 0). Every other row is on the correct side of
    the boundary under either operator — which is why a suite *without*
    the exact-boundary row would have waved this bug straight through.

### Exercise 24.5 — Hunt the missing edge cases ●●

This function returns the most frequent element of a list. Walk the
edge-case checklist from [Section 24.2](02-testing.md) and write the
tests it is missing — at minimum: empty input, single element, and
duplicates with a clear winner. What does the current code do for an
empty list, and is that acceptable behavior to pin down in a test?

```text
def most_common(items):
    best = items[0]
    best_count = 0
    for candidate in set(items):
        count = items.count(candidate)
        if count > best_count:
            best_count = count
            best = candidate
    return best
```

??? success "Solution"

    ```python
    def most_common(items):
        if not items:                       # was: IndexError from items[0]
            raise ValueError("most_common() needs at least one item")
        best = items[0]
        best_count = items.count(best)
        for candidate in items:             # scan order: first-seen wins ties
            count = items.count(candidate)
            if count > best_count:
                best, best_count = candidate, count
        return best

    def test_single_item():
        assert most_common(["only"]) == "only"

    def test_clear_winner_among_duplicates():
        assert most_common(["a", "b", "a", "c", "a"]) == "a"

    def test_tie_goes_to_first_seen():
        assert most_common(["x", "y", "y", "x"]) == "x"

    def test_empty_raises_value_error():
        try:
            most_common([])
        except ValueError:
            return
        assert False, "expected ValueError"

    for test in (test_single_item, test_clear_winner_among_duplicates,
                 test_tie_goes_to_first_seen, test_empty_raises_value_error):
        test()
        print("PASS", test.__name__)
    ```

    The original crashed on `[]` with a bare `IndexError` from
    `items[0]` — an accident, not a decision. Writing the empty-case
    test *forces* a decision (here: a clear `ValueError`). The tie test
    exposed a second buried surprise: iterating over `set(items)` made
    the tie-winner an implementation accident, so the fix scans the list
    in order and pins down "first seen wins."

### Exercise 24.6 — Rename until it explains itself ●●

Refactor this function using only renames (function, parameters, locals)
plus keyword arguments at the call site — no logic changes. Then verify
the output is unchanged.

```python
def f(a, b):
    r = []
    for x in a:
        if x[1] > b:
            r.append(x[0])
    return r

print(f([("Ana", 91), ("Ben", 78), ("Chen", 85)], 80))
```

??? success "Solution"

    ```python
    def names_scoring_above(students, cutoff):
        qualifying_names = []
        for name, score in students:            # unpack: no more x[0], x[1]
            if score > cutoff:
                qualifying_names.append(name)
        return qualifying_names

    result = names_scoring_above(
        [("Ana", 91), ("Ben", 78), ("Chen", 85)], cutoff=80)
    print(result)
    print("unchanged:", result == ["Ana", "Chen"])
    ```

    Same list, `['Ana', 'Chen']`. Beyond renaming, unpacking the tuple
    in the `for` header (`for name, score in students`) is itself a
    naming move — it names the tuple's *parts*, killing the cryptic
    `x[0]` / `x[1]` indexing. The function now answers "what do you
    return?" in its first line: its own name.

### Exercise 24.7 — Review the smelly snippet ●●●

Review this function against the self-review checklist from
[Section 24.3](03-style-review.md). List every issue you find, then
rewrite it cleanly. (There are at least five.)

```text
def calc(x):
    # loop through the list
    t = 0
    for i in range(len(x)):
        t = t + x[i]
    a = t / len(x)
    print("The average is", a)
    return a
```

??? success "Solution"

    ```python
    issues = [
        "1. names say nothing: calc, x, t, a, i",
        "2. the comment narrates WHAT (and adds zero information)",
        "3. crashes on [] with ZeroDivisionError - edge case unhandled",
        "4. print() inside a computing function - side effect nobody asked for",
        "5. un-Pythonic range(len(x)) indexing where sum() or iteration works",
    ]
    for issue in issues:
        print(issue)
    print()

    # The rewrite:
    def average(numbers):
        if not numbers:
            raise ValueError("average() needs at least one number")
        return sum(numbers) / len(numbers)

    print("average([3, 4, 8]) =", average([3, 4, 8]))
    ```

    The deepest smell is number 4: mixing *computing* with *reporting*
    means no caller can get the value silently, and no test can check it
    without capturing output. Compute in the function; let callers
    decide about printing — the same one-job rule that split the receipt
    tangle.

### Exercise 24.8 — Every bug becomes a test ●●●

Bug report: "`average_item_price` crashes with `ZeroDivisionError` when
the cart is empty." Practice the regression protocol from
[Section 24.2](02-testing.md): (1) write a test that fails against the
buggy code, (2) fix the code so an empty cart raises a helpful
`ValueError` instead, (3) show the same test now passes.

```text
def average_item_price(cart):
    return sum(price for _, price in cart) / len(cart)
```

??? success "Solution"

    ```python
    def test_empty_cart_raises_value_error(fn):
        try:
            fn([])
        except ValueError:
            return "PASS"
        except ZeroDivisionError:
            return "FAIL (still the raw crash from the bug report)"
        return "FAIL (no error at all)"

    # Step 1: the test fails against the buggy version - proving it
    # actually detects the bug.
    def average_item_price(cart):
        return sum(price for _, price in cart) / len(cart)

    print("against buggy code:", test_empty_cart_raises_value_error(average_item_price))

    # Step 2: the fix.
    def average_item_price(cart):
        if not cart:
            raise ValueError("cannot average prices of an empty cart")
        return sum(price for _, price in cart) / len(cart)

    # Step 3: the same test, now green - and it stays in the suite forever.
    print("against fixed code:", test_empty_cart_raises_value_error(average_item_price))
    normal = average_item_price([("pen", 1.20), ("lamp", 39.99)])
    print(f"normal path still works: ${normal:.2f}")
    ```

    Watching the test fail *first* is not ceremony — it proves the test
    really exercises the bug (a test that passes against broken code is
    testing nothing). The test then stays in the suite permanently: this
    exact bug can never quietly return.
