# 8.4 Unit testing

You have just written `linear_search` and `selection_sort`. How do you
*know* they work? Running them once and eyeballing the output proves
almost nothing — and next week, when you "improve" the code, how will
you know you didn't break it?

The professional answer is the **unit test**: a small piece of code that
checks one fact about one function, automatically, in milliseconds. A suite of
unit tests is a safety net you can re-run after every change — and, used well,
a design tool that sharpens your thinking *before* you write the code.

## Why tests exist

Two reasons, both bigger than "catching typos":

1. **Catching regressions.** A *regression* is old, working behaviour
   that a new change silently breaks. Manual re-checking of everything
   after every edit is impossible; an automated suite re-checks it all
   in under a second, every time. That safety net is what makes
   refactoring — improving code without changing behaviour — feel safe
   instead of terrifying.
2. **Encoding the specification.** A test is a *precise, executable*
   statement of what the function promises:
   `assert linear_search([], 9) == -1` nails down the empty-list
   behaviour better than a paragraph of prose ever could — because
   prose can drift out of date, and a test that drifts *fails*.

## The `assert` statement

Python's testing atom is one keyword:

```python
total = 2 + 2

assert total == 4                            # true: nothing happens
assert total == 4, "arithmetic is broken"    # optional failure message
print("both asserts passed, silently")
```

Anatomy: `assert` *condition* `,` *optional message*.

- **Condition true** — the statement does nothing at all. Silence is success.
- **Condition false** — Python raises an `AssertionError`, carrying your
  message if you gave one, and the program stops.

Watch a failure catch a real bug — here a mean function accidentally written
with integer division:

```python
# raises AssertionError
def mean(values):
    return sum(values) // len(values)      # BUG: // truncates!

assert mean([2, 4, 6]) == 4                # passes — the bug hides
assert mean([1, 2]) == 1.5, f"expected 1.5, got {mean([1, 2])}"
```

The traceback ends with:

```text
AssertionError: expected 1.5, got 1
```

Notice how the *first* assert passed: `12 // 3` happens to equal
`12 / 3`, so a lucky example hid the bug. It took a value where
truncation matters to expose it. One test is an anecdote; a good
*suite* is evidence — which is why the choice of test cases (below) is
the real skill.

## From asserts to a test suite

Sprinkling asserts in a script is a start, but real suites organise
each fact into its own **test function** — a function whose name starts
with `test_`, takes no arguments, and passes by simply not raising.
Here is a genuine mini-suite for Section 8.3's functions, complete with
a driver that runs everything and reports the score:

```python
def linear_search(values, target):
    """Return the index of the first occurrence of target, or -1."""
    for i in range(len(values)):
        if values[i] == target:
            return i
    return -1

def selection_sort(values):
    """Sort the list in place, smallest first. Returns None."""
    n = len(values)
    for i in range(n - 1):
        min_i = i
        for j in range(i + 1, n):
            if values[j] < values[min_i]:
                min_i = j
        values[i], values[min_i] = values[min_i], values[i]

# ---------- the tests ----------

def test_search_empty_list():
    assert linear_search([], 5) == -1

def test_search_single_element_hit():
    assert linear_search([5], 5) == 0

def test_search_missing_returns_minus_one():
    assert linear_search([4, 7, 9], 5) == -1

def test_search_finds_last_element():
    assert linear_search([4, 7, 9], 9) == 2

def test_search_duplicates_first_wins():
    assert linear_search([3, 8, 3], 3) == 0

def test_sort_empty():
    data = []
    selection_sort(data)
    assert data == []

def test_sort_single():
    data = [42]
    selection_sort(data)
    assert data == [42]

def test_sort_already_sorted():
    data = [1, 2, 3]
    selection_sort(data)
    assert data == [1, 2, 3]

def test_sort_with_duplicates():
    data = [5, 1, 5, 1]
    selection_sort(data)
    assert data == [1, 1, 5, 5]

def test_sort_typical():
    data = [29, 10, 14, 37, 13]
    selection_sort(data)
    assert data == [10, 13, 14, 29, 37]

# ---------- the driver ----------

def run_tests():
    tests = [
        test_search_empty_list,
        test_search_single_element_hit,
        test_search_missing_returns_minus_one,
        test_search_finds_last_element,
        test_search_duplicates_first_wins,
        test_sort_empty,
        test_sort_single,
        test_sort_already_sorted,
        test_sort_with_duplicates,
        test_sort_typical,
    ]
    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
        except AssertionError as err:
            failed += 1
            print(f"FAIL  {test.__name__}   {err}")
        else:
            passed += 1
            print(f"ok    {test.__name__}")
    print(f"\n{passed} passed, {failed} failed")

run_tests()
```

```text
ok    test_search_empty_list
ok    test_search_single_element_hit
ok    test_search_missing_returns_minus_one
ok    test_search_finds_last_element
ok    test_search_duplicates_first_wins
ok    test_sort_empty
ok    test_sort_single
ok    test_sort_already_sorted
ok    test_sort_with_duplicates
ok    test_sort_typical

10 passed, 0 failed
```

Three habits to copy from this suite:

- **Each test checks one fact, and says so in its name.** When
  `test_search_duplicates_first_wins` fails, the name alone tells you what
  broke.
- **Each test builds its own fresh data.** The sort tests each create their
  own list, so no test can contaminate another.
- **The driver keeps going after a failure.** The `try`/`except` catches each
  `AssertionError`, so one red test cannot hide the others.

Try it: change `return -1` to `return 0` in `linear_search`, re-run, and
watch exactly two tests go red.

## Edge cases first

Look at the *order* of those tests: empty list, single element,
missing target, duplicates — the weird inputs come before the typical
one. That is deliberate.

Bugs live at the **edges**: the empty list that makes `values[0]` explode, the
single element that a loop skips, the duplicate that breaks a "first
occurrence" promise, the already-sorted input that tempts an algorithm into a
corner-cutting error.

A test on a typical input mostly re-proves what your eyeball test already
suggested; a test on an edge asks a question you probably never tried by hand.
For any function taking a list, run down this checklist:

| Edge case | The question it asks |
|---|---|
| empty list | does the code survive having nothing to do? |
| single element | does the loop logic degenerate correctly? |
| duplicates | do "first" / "count" promises still hold? |
| already sorted / target at front | is the easy case accidentally broken? |
| reverse sorted / target at back / absent | is the worst case handled to the very end? |

## What pytest and JUnit add

Our `run_tests()` driver works, but notice the drudgery: we listed
every test by hand, and the report is bare-bones. Professional test
frameworks automate exactly that. **pytest**, the de-facto Python standard:

- **discovers** every `test_*` function in your project by itself;
- **runs each one in isolation**;
- **prints the values on both sides of a failing `==`** — no message string
  needed.

```console
$ pytest test_algorithms.py
========================= test session starts =========================
collected 10 items

test_algorithms.py ..........                                    [100%]

========================== 10 passed in 0.03s ==========================
```

Frameworks also add **fixtures** — shared, reusable setup such as a fresh
database or a temporary file, created before each test and cleaned up
afterwards — plus coverage reports, and ways to run only the tests that touch
what you just changed.

Your Java course's equivalent is **JUnit**, where each test is a method marked
with the `@Test` annotation:

=== "Python (pytest style)"

    ```python
    # test_algorithms.py — pytest finds and runs every test_* function
    def linear_search(values, target):   # code under test (real files import it)
        for i in range(len(values)):
            if values[i] == target:
                return i
        return -1

    def test_search_missing_returns_minus_one():
        assert linear_search([4, 7, 9], 5) == -1

    test_search_missing_returns_minus_one()   # pytest makes this call for you
    print("1 passed")
    ```

=== "Java (JUnit 5)"

    ```java
    import org.junit.jupiter.api.Test;
    import static org.junit.jupiter.api.Assertions.assertEquals;

    class SearchTest {
        @Test
        void missingTargetReturnsMinusOne() {
            int[] data = {4, 7, 9};
            assertEquals(-1, Search.linearSearch(data, 5));
        }
    }
    ```

Same idea in both: plainly named checks, one fact each, discovered and
run by the framework. The concepts you practised with bare `assert`
transfer directly; more in
[testing beyond the basics](../ch24-practice/02-testing.md), and the full
JUnit treatment — every annotation, fixtures, parameterized tests, test
doubles, and running the suite in CI — in
[Section 40.4](../ch40-toolchain/04-junit.md).

## Test-first: tests as a design tool

The deepest use of tests is writing them **before** the code —
*test-driven development* (TDD). The rhythm is **red, then green**:

1. **Write tests that state the spec.**
2. **Watch them fail** — that is what proves they *can* fail.
3. **Write the simplest code that makes them pass.**

Let's do one for real.

**Spec:** `clamp(value, low, high)` returns `value` limited to the
range — `low` if `value` is below it, `high` if above, else `value`
itself.

### Red — write the tests and watch them fail

Translate the spec into tests, with only a stub behind them:

```python
# raises AssertionError
def clamp(value, low, high):
    return value            # stub — not written yet

assert clamp(5, 0, 10) == 5                              # in range
assert clamp(-3, 0, 10) == 0, f"got {clamp(-3, 0, 10)}"  # below
assert clamp(99, 0, 10) == 10                            # above
```

The second assert fails — `AssertionError: got -3` — and that failure
is *good news twice*:

- **It proves the test can tell a wrong answer from a right one.**
- **It hands us a to-do list.**

Writing the asserts also forced us to decide the boundary behaviour: is
`clamp(10, 0, 10)` equal to 10? Yes — the range is inclusive. That is a design
decision made cheaply, before any implementation existed.

### Green — write the simplest code that passes

Now write code whose only job is to turn that red to green:

```python
def clamp(value, low, high):
    """Return value, limited to the inclusive range [low, high]."""
    if value < low:
        return low
    if value > high:
        return high
    return value

assert clamp(5, 0, 10) == 5        # in range: unchanged
assert clamp(-3, 0, 10) == 0       # below: pulled up
assert clamp(99, 0, 10) == 10      # above: pulled down
assert clamp(0, 0, 10) == 0        # boundary, low edge
assert clamp(10, 0, 10) == 10      # boundary, high edge
print("all clamp tests pass")
```

It prints `all clamp tests pass` — green. The tests now stand guard
forever: any future "optimisation" of `clamp` that breaks a promise
turns a test red within milliseconds of being run.

!!! warning "Common mistakes"
    - **Testing only the happy path.** A suite of typical-input tests
      can be all green while the empty list still crashes. Edge cases
      first — that is where the bugs are.
    - **Asserting the wrong thing about in-place functions.**
      `assert selection_sort(data) == [1, 2, 3]` compares `None` to a
      list and always fails. Call the function first, then assert on
      `data`.
    - **Tests that share mutable data.** If two tests sort the same
      module-level list, the second test inherits the first one's
      leftovers. Every test builds its own fresh input.
    - **A test you never saw fail.** If a test passes on the first run,
      make sure it *can* fail (break the code briefly, or check the
      assert isn't vacuous like `assert result is not None` on a
      function that always returns something). A test that can't fail
      is decoration, not protection.

## Check your understanding

1. What is a regression, and how does a test suite guard against it?

    ??? success "Answer"
        A regression is previously working behaviour that a later
        change breaks. Because the suite re-checks *all* recorded
        promises automatically, the change that breaks one turns a test
        red immediately — while the change is still fresh in your mind
        and cheap to fix.

2. Why does the `run_tests` driver wrap each call in `try`/`except`
   instead of just calling the test?

    ??? success "Answer"
        A bare failing assert would crash the whole run at the first
        red test, hiding the results of every test after it. Catching
        `AssertionError` per test lets the driver record the failure,
        keep going, and report the full pass/fail picture.

3. Name four edge cases worth testing for any function that takes a
   list, and say what each one probes.

    ??? success "Answer"
        Empty list (survives having nothing to do?), single element
        (loop bounds degenerate correctly?), duplicates ("first
        occurrence" and counting promises hold?), and already-sorted or
        reverse-sorted input (best and worst cases both handled?).

4. In TDD, why is the *red* step — watching the new test fail — not
   skippable?

    ??? success "Answer"
        Seeing the test fail proves it actually tests something: it can
        tell right code from wrong code. A test that starts green might
        be vacuous or aimed at the wrong function, and it would stay
        green over a real bug — worse than no test, because it radiates
        false confidence.
