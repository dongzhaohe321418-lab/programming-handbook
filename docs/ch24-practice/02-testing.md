# 24.2 Testing beyond the basics

[Chapter 8](../ch08-grids/04-unit-testing.md) gave you `assert` and the idea
that programs should check themselves. Professionals build a whole
discipline on that seed: tests with a standard shape, organized by
convention, run by frameworks, and accumulated over years into a safety net
that lets a stranger change your code *without fear* — converting "I hope
this still works" into "run the suite and know."

## Arrange, act, assert

Almost every good unit test has the same three-beat shape, and naming the
beats makes tests dramatically easier to read and write:

1. **Arrange** — set up the world: build the objects and inputs.
2. **Act** — do the one thing being tested.
3. **Assert** — check that the world ended up as expected.

Here it is on a function that computes a shipping fee:

```python
def shipping_fee(total):
    if total < 0:
        raise ValueError("total cannot be negative")
    return 0 if total >= 50 else 5

def test_big_orders_ship_free():
    order_total = 80.00          # arrange
    fee = shipping_fee(order_total)   # act
    assert fee == 0              # assert

test_big_orders_ship_free()
print("test passed")
```

One test, one behavior — that is the discipline. When a test with seven
asserts fails, you know *something* broke; when this test fails, you know
big orders stopped shipping free. Small tests are diagnostic precision.

## How pytest organizes this (and a mirror you can run)

The de-facto standard Python test framework is **pytest**. It cannot run in
this page's sandbox, but its conventions take one screen to learn. You put
tests in files named `test_*.py`, in functions named `test_*`, using plain
`assert`; pytest finds them, runs them, and reports:

```console
$ pytest                      # discover and run everything
$ pytest -k empty             # run only tests with "empty" in the name
$ pytest -x                   # stop at the first failure
======================== test session starts =========================
collected 3 items
test_checkout.py ..F                                            [100%]
========================= 1 failed, 2 passed =========================
```

Shared setup goes in a **fixture** — a function that builds something tests
need; a test just names it as a parameter:

```text
import pytest

@pytest.fixture
def cart():                  # build a fresh cart for any test that asks
    return Cart(items=["book", "lamp"])

def test_cart_total(cart):   # pytest sees "cart" and calls the fixture
    assert cart.total() > 0
```

There is no magic in any of this — and to prove it, here is a working test
runner in twelve lines, doing what pytest does in miniature: discover
functions named `test_*`, run each, catch failures, report a summary.

```python
def shipping_fee(total):
    if total < 0:
        raise ValueError("total cannot be negative")
    return 0 if total >= 50 else 5

# ---- the tests ----
def test_free_shipping_at_threshold():
    assert shipping_fee(50) == 0

def test_small_order_pays_fee():
    assert shipping_fee(10) == 5

def test_negative_total_rejected():
    try:
        shipping_fee(-1)
    except ValueError:
        return                     # got the error we wanted
    assert False, "expected ValueError, got no error"

# ---- a test runner in miniature ----
passed = failed = 0
for name, fn in sorted(globals().items()):
    if name.startswith("test_") and callable(fn):
        try:
            fn()
            print(f"PASS  {name}")
            passed += 1
        except AssertionError as error:
            print(f"FAIL  {name}  ({error})")
            failed += 1
print()
print(passed, "passed,", failed, "failed")
```

Change `>= 50` to `> 50` in `shipping_fee` and run again: the threshold
test flips to FAIL and the summary tells you instantly. That feedback loop
— break something, *see it immediately* — is what a test suite feels like
from inside.

## Table-driven tests: parametrized thinking

The three shipping tests above share their entire skeleton and differ only
in numbers. Whenever you notice that, stop copy-pasting tests and put the
*data* in a table — one loop, many cases:

```python
def shipping_fee(total):
    if total < 0:
        raise ValueError("total cannot be negative")
    return 0 if total >= 50 else 5

cases = [
    # (total,  expected_fee)
    (0,       5),
    (49.99,   5),      # just under the threshold
    (50,      0),      # exactly at the threshold
    (50.01,   0),      # just over
    (1000,    0),
]

failures = 0
for total, expected in cases:
    actual = shipping_fee(total)
    ok = actual == expected
    failures += (not ok)
    print(f"{'ok  ' if ok else 'FAIL'} shipping_fee({total}) -> {actual}  (expected {expected})")

print(f"\n{len(cases) - failures} of {len(cases)} cases passed")
```

Adding a case is now one line — so you add more of them, especially around
the interesting spots. pytest has this built in as
`@pytest.mark.parametrize(...)`, and JUnit as `@ParameterizedTest`; the
table is the idea, the decorators are packaging.

## The edge-case checklist

Where do the table's rows come from? Bugs cluster at edges, and edges are
predictable. For any function, walk this checklist:

| Category | Ask yourself | For `shipping_fee` / a list function |
| --- | --- | --- |
| Empty / one / many | Does it work for zero items? one? lots? | empty cart; single item; bulk order |
| Boundaries | What happens *exactly at* and *adjacent to* every threshold? | 49.99, 50, 50.01 |
| Duplicates | Do repeated values confuse it? | two identical items |
| Order | Sorted, reversed, shuffled input? | items added in any order |
| Invalid input | What *should* wrong input do — and does it? | negative total → `ValueError` |

That last row deserves emphasis: the error path is part of the contract,
so it needs tests too ([Chapter 10](../ch10-exceptions/02-exceptions.md)
taught you the raising side; this is the checking side). Raw, the error
path looks like this:

```python
# raises ValueError
def shipping_fee(total):
    if total < 0:
        raise ValueError("total cannot be negative")
    return 0 if total >= 50 else 5

shipping_fee(-1)     # no test harness: the exception escapes, run ends
```

A test must instead *expect* the exception: catch it and pass, or fail if
it never arrives — the `try/except/assert False` shape you saw in
`test_negative_total_rejected` above. pytest gives the same logic a
pleasant spelling:

```text
import pytest

def test_negative_total_rejected():
    with pytest.raises(ValueError):
        shipping_fee(-1)          # must raise, or the test fails
```

## A real suite for a real structure

Time to test something with state: the Stack from
[Chapter 19](../ch19-stacks-queues/02-stacks.md). Happy paths, error
paths, and one regression test — the whole kit, runnable:

```python
class Stack:
    def __init__(self):
        self._items = []
    def push(self, item):
        self._items.append(item)
    def pop(self):
        if not self._items:
            raise IndexError("pop from empty stack")
        return self._items.pop()
    def peek(self):
        if not self._items:
            raise IndexError("peek at empty stack")
        return self._items[-1]
    def is_empty(self):
        return len(self._items) == 0
    def __len__(self):
        return len(self._items)

# ---- happy paths ----
def test_new_stack_is_empty():
    s = Stack()
    assert s.is_empty() and len(s) == 0

def test_push_then_peek_leaves_item_in_place():
    s = Stack()
    s.push("a")
    assert s.peek() == "a" and len(s) == 1   # peek must NOT remove

def test_pop_is_last_in_first_out():
    s = Stack()
    s.push(1); s.push(2); s.push(3)
    assert [s.pop(), s.pop(), s.pop()] == [3, 2, 1]
    assert s.is_empty()

# ---- error paths ----
def test_pop_on_empty_raises():
    s = Stack()
    try:
        s.pop()
    except IndexError:
        return
    assert False, "expected IndexError"

# ---- regression: a bug we fixed once, fenced forever ----
def test_failed_pop_does_not_corrupt_length():
    s = Stack()
    try:
        s.pop()
    except IndexError:
        pass
    assert len(s) == 0            # the failed pop must change nothing

passed = failed = 0
for name, fn in sorted(globals().items()):
    if name.startswith("test_") and callable(fn):
        try:
            fn()
            print(f"PASS  {name}")
            passed += 1
        except AssertionError as error:
            print(f"FAIL  {name}  ({error})")
            failed += 1
print()
print(passed, "passed,", failed, "failed")
```

Note what the suite pins down that the *code* never states outright:
`peek` doesn't remove; a failed `pop` has no side effects; LIFO order.
Tests are executable documentation — the only documentation that
complains when it goes stale.

In your Java course, the same suite looks like this under **JUnit 5**:

=== "Python (pytest style)"

    ```text
    def test_pop_is_last_in_first_out():
        s = Stack()
        s.push(1); s.push(2)
        assert s.pop() == 2

    def test_pop_on_empty_raises():
        with pytest.raises(IndexError):
            Stack().pop()
    ```

=== "Java (JUnit 5)"

    ```java
    import static org.junit.jupiter.api.Assertions.*;
    import org.junit.jupiter.api.Test;

    class StackTest {
        @Test
        void popIsLastInFirstOut() {
            Stack<Integer> s = new Stack<>();
            s.push(1); s.push(2);
            assertEquals(2, s.pop());
        }

        @Test
        void popOnEmptyThrows() {
            Stack<Integer> s = new Stack<>();
            assertThrows(NoSuchElementException.class, () -> s.pop());
        }
    }
    ```

Same three beats, same happy/error split; JUnit marks tests with `@Test`
annotations instead of a name prefix, and `assertEquals` / `assertThrows`
instead of bare `assert` — vocabulary, not concept.

## What coverage proves — and what it can't

**Coverage** tools measure which lines your tests executed; "87% coverage"
means 13% of lines never ran under test — that code could be deleted and
no test would notice, which *is* worth knowing. But the number seduces
people into a fatal inversion: 100% coverage does **not** mean the code is
correct. Executing a line is not the same as checking it, and no line of
code exists for the input you forgot:

```python
def average(numbers):
    return sum(numbers) / len(numbers)

# This one test executes 100% of the lines of average():
assert average([2, 4, 6]) == 4.0
print("every line ran; the test passed; coverage: 100%")

# ...and yet the empty case was never even asked about:
try:
    average([])
except ZeroDivisionError:
    print("average([]) still crashes - a bug living happily at full coverage")
```

Use coverage the way it deserves: *low* coverage is a reliable alarm;
*high* coverage is not a certificate. The edge-case checklist finds what
the percentage cannot.

## Regression tests: every bug becomes a test

The most valuable tests you will ever write are born from bugs. The
protocol, forever: when a bug is found, first write a test that fails
*because of* the bug, then fix the code, then watch the test pass — and
leave the test in the suite permanently. You saw one above:
`test_failed_pop_does_not_corrupt_length` exists because some past version
did corrupt state on a failed pop. That bug can never return unannounced;
the suite is a ratchet that only tightens — and, closing the loop with
[Section 24.1](01-git-workflow.md), it is exactly what CI runs on every
push before a PR may merge.

!!! warning "Common mistakes"

    - **Testing only the happy path.** The error path is half the
      contract. If `shipping_fee(-1)` is supposed to raise, an input like
      it belongs in the suite — with `pytest.raises` or its
      try/except equivalent.
    - **Many behaviors, one test.** When `test_everything` fails, you
      know nothing. One behavior per test, named for the behavior, so a
      failure *is* the diagnosis.
    - **Tests that depend on each other.** Each test must build its own
      world (that is what fixtures are for). Suites that only pass in one
      order rot fast — real runners may run tests in any order.
    - **Chasing the coverage number.** Writing assert-free tests to
      reach 100% produces confidence-shaped emptiness. Rows in the
      edge-case table beat points of coverage, every time.

## Check your understanding

1. Label the three beats in `test_big_orders_ship_free`, and explain why
   the *act* beat should usually be a single line.

    ??? success "Answer"
        Arrange: `order_total = 80.00`. Act: `fee =
        shipping_fee(order_total)`. Assert: `assert fee == 0`. Keeping
        the act to one call keeps the test's verdict unambiguous — if it
        fails, the one action under test is the culprit, not some step of
        an elaborate setup-and-poke sequence.

2. Your table-driven suite for `shipping_fee` has cases at 49.99, 50, and
   50.01. Which checklist category is this, and what bug class is it
   hunting?

    ??? success "Answer"
        Boundaries. Threshold logic is where `>=` -versus- `>` (off-by-one
        and off-by-equality) bugs live; testing exactly at the edge and
        one step to each side distinguishes every possible comparison
        operator someone might have typed.

3. A teammate boasts a suite with 100% line coverage of
   `find_largest(numbers)`. Name a bug the suite could still miss, and
   the checklist row that would catch it.

    ??? success "Answer"
        `find_largest([])` — the empty case might crash or return
        something absurd, and no *line* of the function needs to be
        uncovered for that to slip through: coverage counts executed
        lines, not considered inputs. The "empty / one / many" row of the
        edge-case checklist exists precisely for this.

4. In the JUnit tab, which pieces correspond to pytest's `test_` prefix,
   plain `assert`, and `pytest.raises`?

    ??? success "Answer"
        The `@Test` annotation marks a method as a test (no name prefix
        needed); `assertEquals(expected, actual)` plays the role of
        `assert actual == expected`; and
        `assertThrows(SomeException.class, () -> ...)` is JUnit's
        `pytest.raises` — run this action, and fail unless it throws.
