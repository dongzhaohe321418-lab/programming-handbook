# 40.4 JUnit and testing at scale

[Section 8.4](../ch08-grids/04-unit-testing.md) introduced `assert` and a
hand-written driver loop, and [Section 24.2](../ch24-practice/02-testing.md)
turned that into pytest with arrange-act-assert and table-driven cases. Both
pages were about *your* tests for *your* code. This page is about what
happens when a test suite belongs to twenty people, contains eight thousand
cases, must run on every push before anyone is allowed to merge, and has to
say — in the ninety seconds a continuous-integration job is allowed — exactly
which three assertions broke and why. That is a different engineering
problem, and the tool that solved it for the Java world, and set the template
that pytest and almost every other framework followed, is **JUnit**.

!!! info "Java does not run here — the framework model does"
    JUnit is Java, so every JUnit snippet on this page is in a `java` fence
    with no Run button. The runnable centrepiece is a **JUnit-style
    micro-framework written in Python**: a `@test` decorator, assertion
    helpers with real diagnostics, setup and teardown hooks, parameterized
    tests, and a runner that prints a JUnit-style report. It is about eighty
    lines, and it is genuinely the same design.

## What a framework gives you that `assert` does not

A bare `assert` in a `main` method tests one thing. Six features turn that
into infrastructure, and it is worth naming them because every framework in
every language provides the same six:

| Feature | What it means | Why it matters at scale |
|---|---|---|
| **Discovery** | the runner finds test methods itself | nobody maintains a list of 8 000 tests by hand |
| **Isolation** | each test runs independently, on fresh state | one test's mess cannot break the next one |
| **Fixtures** | declared setup and teardown around each test | the arrange step is written once, not fifty times |
| **Reporting** | a machine-readable pass/fail/error summary | CI can post "3 failed" on the pull request |
| **Parameterization** | one test body, many inputs | twenty cases without twenty copies |
| **Diagnostics** | `expected <3> but was <4>`, with a stack trace | you fix the bug without adding print statements |

The last one deserves emphasis. `assert stack.size() == 1` tells you the
assertion failed; `assertEquals(1, stack.size())` tells you it found 4. On a
failure you did not cause, in code you did not write, that difference is
minutes versus an afternoon.

## JUnit 5, annotation by annotation

JUnit 5 (the artifact is called JUnit Jupiter) drives everything with
annotations. The examples below test data structures you built in Parts III
and VI, so the *subject* is familiar and only the machinery is new.

### `@Test` and the basic assertions

```java
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class ArrayStackTest {

    @Test
    void popReturnsTheMostRecentlyPushedItem() {
        ArrayStack<String> stack = new ArrayStack<>();
        stack.push("a");
        stack.push("b");

        assertEquals("b", stack.pop());     // expected first, actual second
        assertEquals(1, stack.size());
        assertFalse(stack.isEmpty());
    }
}
```

Two conventions matter. The **expected value comes first** in
`assertEquals` — reversing the arguments does not break the test, but it
prints the failure message backwards, which is worse than useless at 2 a.m.
And the method name is a sentence: the report shows method names, so
`popReturnsTheMostRecentlyPushedItem` is documentation that cannot go stale.
Unlike JUnit 4, neither the class nor the methods need to be `public`.

### `assertThrows` — testing that something fails correctly

```java
@Test
void poppingAnEmptyStackThrows() {
    ArrayStack<String> stack = new ArrayStack<>();

    NoSuchElementException thrown = assertThrows(
            NoSuchElementException.class,
            stack::pop);

    assertTrue(thrown.getMessage().contains("empty"),
               "the message should say what went wrong");
}
```

`assertThrows` fails if the code does *not* throw, or throws the wrong type,
and returns the exception so you can assert on its message. The error path is
part of the specification, and it is the part beginners forget: an empty
stack that returns `null` instead of throwing has a bug that no
happy-path test will ever find.

### `assertAll` — see every failure, not just the first

```java
@Test
void aFreshTrieIsCompletelyEmpty() {
    Trie trie = new Trie();

    assertAll("a newly created trie",
            () -> assertEquals(0, trie.size()),
            () -> assertFalse(trie.contains("cat")),
            () -> assertTrue(trie.wordsWithPrefix("c").isEmpty()));
}
```

Normally the first failing assertion ends the test, so you fix it, re-run,
and discover the next one — a slow loop. `assertAll` evaluates every
assertion and reports all the failures together.

### Fixtures: `@BeforeEach`, `@AfterEach`, `@BeforeAll`, `@AfterAll`

```java
import org.junit.jupiter.api.*;

class BinarySearchTreeTest {

    private BinarySearchTree<Integer> tree;

    @BeforeAll
    static void announce() {                 // once, before any test; static
        System.out.println("BST suite starting");
    }

    @BeforeEach
    void createEmptyTree() {                 // before EVERY test
        tree = new BinarySearchTree<>();
    }

    @AfterEach
    void invariantStillHolds() {             // after EVERY test, pass or fail
        assertTrue(tree.isValidSearchTree(),
                   "BST ordering invariant was violated");
    }

    @Test
    void insertedKeysAreFound() {
        tree.insert(5);
        tree.insert(3);
        assertTrue(tree.contains(3));
    }

    @Test
    void deletingTheRootKeepsTheOtherKeys() {
        tree.insert(5);
        tree.insert(3);
        tree.delete(5);
        assertTrue(tree.contains(3));
        assertFalse(tree.contains(5));
    }
}
```

`@BeforeAll` and `@AfterAll` must be `static`, because they run once for the
whole class rather than per instance — the one exception being a class
annotated `@TestInstance(Lifecycle.PER_CLASS)`, which asks JUnit for a single
shared instance and therefore allows non-static hooks. The `@AfterEach` here
is worth copying:
checking the structure's **invariant** after every single test is how the
data-structure chapters recommend you work, and a framework hook makes it
automatic.

### `@DisplayName` — reports humans can read

```java
@DisplayName("A hash table with separate chaining")
class SeparateChainingMapTest {

    @Test
    @DisplayName("keeps both entries when two keys collide")
    void collidingKeysBothSurvive() {
        // ...
    }
}
```

The report then reads like a specification instead of like camel case.

### `@ParameterizedTest` — one body, many inputs

```java
@ParameterizedTest
@ValueSource(ints = {1, 2, 3, 5, 8, 13, 21})
void everyInsertedKeyIsFoundAgain(int key) {
    BinarySearchTree<Integer> tree = new BinarySearchTree<>();
    tree.insert(key);
    assertTrue(tree.contains(key));
}

@ParameterizedTest(name = "{0} keys => height at most {1}")
@CsvSource({
        "1, 1",
        "3, 2",
        "7, 3",
        "15, 4"
})
void aBalancedTreeStaysLogarithmic(int keys, int maxHeight) {
    AvlTree<Integer> tree = new AvlTree<>();
    for (int i = 1; i <= keys; i++) {
        tree.insert(i);                       // sorted input: the worst case
    }
    assertTrue(tree.height() <= maxHeight,
               "height was " + tree.height());
}
```

Each row becomes a separately reported test, so a failure names the exact
input. `@ValueSource` supplies one argument per case; `@CsvSource` supplies
several; `@MethodSource` points at a method that returns the cases when they
are too complex for a string. This is the framework's answer to the
table-driven style of [Section 24.2](../ch24-practice/02-testing.md).

### `@Nested`, `@Disabled`, and `assertTimeout`

```java
@DisplayName("A ring buffer")
class RingBufferTest {

    @Nested
    @DisplayName("when empty")
    class WhenEmpty {
        RingBuffer<String> buffer = new RingBuffer<>(3);

        @Test
        void hasSizeZero() { assertEquals(0, buffer.size()); }

        @Test
        void throwsOnPop() { assertThrows(IllegalStateException.class, buffer::pop); }
    }

    @Nested
    @DisplayName("when full")
    class WhenFull {
        RingBuffer<String> buffer = new RingBuffer<>(3);

        @BeforeEach
        void fill() { buffer.push("a"); buffer.push("b"); buffer.push("c"); }

        @Test
        void dropsTheOldestOnPush() {
            buffer.push("d");
            assertEquals("b", buffer.pop());
        }
    }

    @Test
    @Disabled("flaky on CI — see issue #412")
    void resizesUnderConcurrentLoad() { /* ... */ }

    @Test
    void prefixLookupStaysFast() {
        assertTimeout(Duration.ofMillis(200), () -> {
            Trie trie = new Trie();
            for (int i = 0; i < 100_000; i++) trie.insert("word" + i);
            assertEquals(10, trie.wordsWithPrefix("word999").size());
        });
    }
}
```

`@Nested` groups tests that share a *situation*, and each group gets its own
fixtures — this is how you avoid a class with fourteen boolean flags in
`@BeforeEach`. `@Disabled` skips a test and **requires a reason**: a skipped
test with no explanation becomes permanent. `assertTimeout` runs the code in
the calling thread and reports afterwards if it took too long;
`assertTimeoutPreemptively` runs it in another thread and aborts it, which is
what you want for something that might hang, but which is unsafe if the code
touches thread-local state.

!!! warning "Timing assertions are the number-one source of flaky tests"
    A 200 ms limit that passes on your laptop will fail on a loaded CI runner
    that is sharing a core with five other jobs. Use generous limits, use
    them rarely, and prefer asserting on *operation counts* — "this lookup
    visited at most 12 nodes" — which are deterministic.

## The lifecycle, and the flaky test that ignores it

JUnit creates **a brand new instance of the test class for every test
method**. That is a deliberate design decision, not an implementation detail:
it guarantees that a field written by one test cannot be observed by another,
so tests can run in any order — and JUnit does not promise an order.

The failure mode when state *is* shared is the classic flaky test. Here it is
reproduced runnably: two tests, one shared object, and the only difference
between the two runs is the order.

```python
class ShoppingCart:
    def __init__(self):
        self.items = []

    def add(self, name):
        self.items.append(name)

    def total_items(self):
        return len(self.items)


SHARED_CART = ShoppingCart()        # created ONCE — like a Java static field


def test_adding_one_item():
    SHARED_CART.add("apple")
    assert SHARED_CART.total_items() == 1, \
        f"expected 1 item, found {SHARED_CART.total_items()}"


def test_a_new_cart_is_empty():
    assert SHARED_CART.total_items() == 0, \
        f"expected 0 items, found {SHARED_CART.total_items()}"


def run(order):
    print(f"  order {[t.__name__ for t in order]}")
    for t in order:
        try:
            t()
            print(f"    PASS  {t.__name__}")
        except AssertionError as exc:
            print(f"    FAIL  {t.__name__}: {exc}")


SHARED_CART.items.clear()
run([test_a_new_cart_is_empty, test_adding_one_item])
SHARED_CART.items.clear()
run([test_adding_one_item, test_a_new_cart_is_empty])
```

```text
  order ['test_a_new_cart_is_empty', 'test_adding_one_item']
    PASS  test_a_new_cart_is_empty
    PASS  test_adding_one_item
  order ['test_adding_one_item', 'test_a_new_cart_is_empty']
    PASS  test_adding_one_item
    FAIL  test_a_new_cart_is_empty: expected 0 items, found 1
```

Same code, same assertions, two different verdicts. In a real suite the order
changes when someone adds a test, renames a class, or turns on parallel
execution — so the failure appears weeks later, in a pull request that
touched nothing related, and everybody blames the wrong change. The fix is
never "add a `sleep`" or "re-run the job"; it is to give each test its own
state:

```java
class ShoppingCartTest {
    private ShoppingCart cart;          // an instance field, not static

    @BeforeEach
    void freshCart() { cart = new ShoppingCart(); }
    // ... every test now starts from empty, in any order
}
```

Shared mutable state is the disease; `static` fields, singletons, real
databases, real clocks, real files in a fixed location, and leftover
temporary directories are its common carriers.

## Running tests from the command line and in CI

Test frameworks are command-line tools first; the IDE button is a
convenience. The two dominant JVM build tools both wire JUnit in
automatically:

```console
$ mvn test                                     # Maven: compile and run everything
$ mvn -Dtest=BinarySearchTreeTest test         # one class
$ mvn -Dtest=BinarySearchTreeTest#insertedKeysAreFound test   # one method
$ ls target/surefire-reports/                  # XML + text reports land here

$ ./gradlew test                               # Gradle
$ ./gradlew test --tests "*BinarySearchTree*"  # pattern
$ ./gradlew test --info                        # show output from passing tests
$ open build/reports/tests/test/index.html     # a browsable HTML report
```

Both write a machine-readable XML report in the JUnit format — which is worth
knowing because it became the *lingua franca*: pytest writes it with
`--junitxml=results.xml`, and essentially every CI system knows how to read
it and annotate a pull request with the failures.

That is the connection to [Section 24.1](../ch24-practice/01-git-workflow.md).
The workflow described there — branch, commit, pull request, review — gets
its teeth from a CI job that runs the suite on every push and blocks the
merge if anything is red:

```yaml
name: tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'
      - run: ./gradlew test
```

Once that exists, "it works on my machine" stops being an argument, and the
question "is `main` releasable?" has an answer that nobody has to check by
hand. Mark the job as a required status check and the repository will refuse
the merge itself.

## Testing the hard things

**Exceptions** — covered above: `assertThrows`, and assert on the message so
that the error is *useful*, not merely present.

**Deep equality** — `assertEquals` calls `.equals()`. For a class that does
not override it, that is identity comparison, so two structurally identical
objects are "not equal" and the failure message shows two values that look
the same. Either implement `equals`/`hashCode` (records do it for you) or
compare the parts. For collections, use the assertion that matches the shape:

```java
assertArrayEquals(new int[]{1, 2, 3}, sorter.sort(new int[]{3, 1, 2}));
assertIterableEquals(List.of("a", "b"), trie.wordsWithPrefix("")); // order matters
assertEquals(Set.of("a", "b"), new HashSet<>(trie.wordsWithPrefix(""))); // it does not
```

**Floating point** — never with `==`.
[Section 5.1](../ch05-under-the-hood/01-numeric-pitfalls.md) showed why
`0.1 + 0.2 != 0.3`: binary fractions cannot represent those decimals exactly,
so arithmetic accumulates tiny errors. Both languages give you a tolerance:

=== "Java"

    ```java
    assertEquals(0.3, 0.1 + 0.2);          // FAILS: expected <0.3> but was <0.30000000000000004>
    assertEquals(0.3, 0.1 + 0.2, 1e-9);    // passes: the third argument is the delta
    ```

=== "Python"

    ```python
    import math
    print(0.1 + 0.2 == 0.3)                        # False
    print(math.isclose(0.1 + 0.2, 0.3))            # True
    print(math.isclose(0.1 + 0.2, 0.3, abs_tol=1e-9))  # True
    ```

Choose the delta deliberately: a tolerance of `1e-9` on a physics simulation
that accumulates a million operations is far too strict, and `0.5` on a
currency calculation is far too loose. If you find yourself widening a delta
until a test passes, the test is no longer testing anything.

**Property-based testing** attacks the problem that you only ever write the
test cases you thought of. Instead of examples, you state a *property* that
must hold for all inputs, and the library generates hundreds of cases and
shrinks any failure to a minimal example. **jqwik** does this for Java
(`@Property`, `@ForAll`); **Hypothesis** does it for Python (`@given` plus
strategies). Both are third-party libraries, and both are exceptionally good
at finding the empty list, the duplicate key, and the Unicode surrogate you
never considered. Properties worth asserting about the structures in this
part: sorting is idempotent and preserves multiset contents; inserting then
deleting a key restores the original tree; a serialiser followed by a parser
is the identity function.

## A JUnit-style micro-framework you can run

Time to build it. Everything below is the real design — a registry, a
decorator, assertion helpers that raise a distinguished exception type, hooks
around each test, a parameterized helper, and a runner that catches and
classifies. Note the deliberate distinction between a **failure** (an
assertion said no) and an **error** (the code blew up unexpectedly): JUnit
reports those separately because they mean different things, and so does
this.

The class under test is a fixed-capacity ring buffer, and it contains a
one-character bug. Watch the report find it.

```python
"""A JUnit-style micro-framework, and the class it puts on trial."""

# ============ the framework ================================================


class TestFailure(AssertionError):
    """An assertion said no. Distinct from a crash, exactly as in JUnit."""


_registry = []                                   # (display name, callable)
_hooks = {"before": None, "after": None}


def test(arg):
    """`@test` or `@test("a readable name")` — JUnit's @Test + @DisplayName."""
    if callable(arg):
        _registry.append((arg.__name__, arg))
        return arg

    def decorate(func):
        _registry.append((arg, func))
        return func
    return decorate


def before_each(func):                           # JUnit's @BeforeEach
    _hooks["before"] = func
    return func


def after_each(func):                            # JUnit's @AfterEach
    _hooks["after"] = func
    return func


def parameterized(name, rows):
    """JUnit's @ParameterizedTest + @CsvSource: one test per row of data."""
    def decorate(func):
        for row in rows:
            args = row if isinstance(row, tuple) else (row,)
            label = f"{name}[{', '.join(repr(a) for a in args)}]"
            _registry.append((label, lambda f=func, a=args: f(*a)))
        return func
    return decorate


def assert_equals(expected, actual, hint=""):
    if expected != actual:
        raise TestFailure(f"expected: <{expected!r}> but was: <{actual!r}>"
                          + (f" -- {hint}" if hint else ""))


def assert_true(condition, hint="expected True but was False"):
    if not condition:
        raise TestFailure(hint)


def assert_close(expected, actual, delta, hint=""):
    if abs(expected - actual) > delta:
        raise TestFailure(f"expected: <{expected}> +/- {delta} but was: "
                          f"<{actual}> (off by {abs(expected - actual):.3g})"
                          + (f" -- {hint}" if hint else ""))


def assert_raises(exc_type, func, *args):
    """Returns the exception so you can assert on its message, like JUnit."""
    try:
        func(*args)
    except exc_type as exc:
        return exc
    except Exception as exc:
        raise TestFailure(f"expected {exc_type.__name__} but "
                          f"{type(exc).__name__} was raised: {exc}") from None
    raise TestFailure(f"expected {exc_type.__name__} to be raised, "
                      f"but nothing was")


def run_tests(title):
    passed = failed = errored = 0
    print(title)
    print("-" * len(title))
    for name, func in _registry:
        if _hooks["before"]:
            _hooks["before"]()
        try:
            func()
        except TestFailure as exc:
            failed += 1
            print(f"  FAIL   {name}")
            print(f"         {exc}")
        except Exception as exc:
            errored += 1
            print(f"  ERROR  {name}")
            print(f"         {type(exc).__name__}: {exc}")
        else:
            passed += 1
            print(f"  PASS   {name}")
        finally:
            if _hooks["after"]:
                _hooks["after"]()
    print(f"\nTests run: {passed + failed + errored}, "
          f"Failures: {failed}, Errors: {errored}")


# ============ the code under test ==========================================


class RingBuffer:
    """A fixed-capacity FIFO. When full, the oldest item is dropped."""

    def __init__(self, capacity):
        if capacity <= 0:
            raise ValueError(f"capacity must be positive, got {capacity}")
        self.capacity = capacity
        self._items = []

    def push(self, item):
        if len(self._items) > self.capacity:      # <-- one character is wrong
            self._items.pop(0)
        self._items.append(item)

    def pop(self):
        if not self._items:
            raise IndexError("pop from an empty RingBuffer")
        return self._items.pop(0)

    def __len__(self):
        return len(self._items)

    def to_list(self):
        return list(self._items)


# ============ the tests ====================================================

fixture = {}


@before_each
def make_a_fresh_buffer():
    fixture["buf"] = RingBuffer(3)


@test("a new buffer is empty")
def test_new_is_empty():
    assert_equals(0, len(fixture["buf"]))


@test("push then pop returns the same item")
def test_push_pop_roundtrip():
    fixture["buf"].push("a")
    assert_equals("a", fixture["buf"].pop())


@test("items come out in the order they went in")
def test_fifo_order():
    for item in "abc":
        fixture["buf"].push(item)
    assert_equals(["a", "b", "c"], fixture["buf"].to_list())


@test("pushing past capacity drops the oldest item")
def test_overflow_drops_oldest():
    for item in "abcd":
        fixture["buf"].push(item)
    assert_equals(3, len(fixture["buf"]), "capacity is 3")


@test("popping an empty buffer raises IndexError")
def test_pop_empty_raises():
    exc = assert_raises(IndexError, fixture["buf"].pop)
    assert_true("empty" in str(exc), f"unhelpful message: {exc}")


@test("a zero capacity is rejected")
def test_zero_capacity_rejected():
    assert_raises(ValueError, RingBuffer, 0)


@parameterized("length after n pushes", [(0, 0), (1, 1), (2, 2), (3, 3)])
def test_length_after_pushes(pushes, expected_len):
    for i in range(pushes):
        fixture["buf"].push(i)
    assert_equals(expected_len, len(fixture["buf"]))


run_tests("RingBufferTest")
```

```text
RingBufferTest
--------------
  PASS   a new buffer is empty
  PASS   push then pop returns the same item
  PASS   items come out in the order they went in
  FAIL   pushing past capacity drops the oldest item
         expected: <3> but was: <4> -- capacity is 3
  PASS   popping an empty buffer raises IndexError
  PASS   a zero capacity is rejected
  PASS   length after n pushes[0, 0]
  PASS   length after n pushes[1, 1]
  PASS   length after n pushes[2, 2]
  PASS   length after n pushes[3, 3]

Tests run: 10, Failures: 1, Errors: 0
```

Read the report the way you would read a real one. Nine tests passed, so the
buffer is broadly right; one failed, and the diagnostic says the whole story
without you opening a debugger: after four pushes into a capacity-3 buffer
there were **four** items. The `hint` string is doing exactly what
JUnit's optional message argument does — turning "4 is not 3" into "4 is not
3, and 3 is the capacity".

The bug is `>` where `>=` belongs: `push` only drops the oldest item once the
buffer has already *exceeded* its capacity, so it always holds one item too
many. One character:

```python
# continues — patches the buggy method and re-runs the same registered tests


def fixed_push(self, item):
    if len(self._items) >= self.capacity:        # >= instead of >
        self._items.pop(0)
    self._items.append(item)


RingBuffer.push = fixed_push
run_tests("RingBufferTest (after the one-character fix)")
```

```text
RingBufferTest (after the one-character fix)
--------------------------------------------
  PASS   a new buffer is empty
  PASS   push then pop returns the same item
  PASS   items come out in the order they went in
  PASS   pushing past capacity drops the oldest item
  PASS   popping an empty buffer raises IndexError
  PASS   a zero capacity is rejected
  PASS   length after n pushes[0, 0]
  PASS   length after n pushes[1, 1]
  PASS   length after n pushes[2, 2]
  PASS   length after n pushes[3, 3]

Tests run: 10, Failures: 0, Errors: 0
```

Every framework you will ever use is this, plus polish: discovery by
inspecting modules instead of a decorator, stack traces trimmed to your code,
coloured output, XML reports, parallel workers, and plugins. The core is a
list of callables and a `try`/`except`.

## Test doubles: stub, mock, and fake

Real code depends on things that are awkward in a test — a clock, a network
service, a payment gateway, a mail server, a random number generator. A
**test double** stands in for one, and the three words for them mean
genuinely different things:

| Double | What it is | Typical use |
|---|---|---|
| **Stub** | returns canned answers, no logic | `getExchangeRate()` always returns 1.25 |
| **Fake** | a real, working implementation that is unsuitable for production | an in-memory database; a clock you control |
| **Mock** | records the calls made to it so the test can assert on them | "was `send()` called exactly once, with this address?" |

The clock is the example everybody meets first, because the alternative is a
test that sleeps. A cache with a 30-second time-to-live tested against the
real clock takes 31 seconds to run and is flaky on a loaded machine. Tested
against a **fake clock**, it takes microseconds and is exact:

```python
class FakeClock:
    """A test double for the system clock: it moves only when you say so."""

    def __init__(self, now=0.0):
        self.now = now

    def __call__(self):
        return self.now

    def advance(self, seconds):
        self.now += seconds


class TTLCache:
    """Caches values for `ttl` seconds. The clock is INJECTED, not imported."""

    def __init__(self, ttl, clock):
        self.ttl, self.clock, self.store = ttl, clock, {}

    def put(self, key, value):
        self.store[key] = (value, self.clock() + self.ttl)

    def get(self, key):
        if key not in self.store:
            return None
        value, expires_at = self.store[key]
        if self.clock() >= expires_at:
            del self.store[key]
            return None
        return value


clock = FakeClock()
cache = TTLCache(ttl=30, clock=clock)
cache.put("user:7", "Ada")

print(f"t={clock.now:>5.0f}s  get -> {cache.get('user:7')!r}")
clock.advance(29)
print(f"t={clock.now:>5.0f}s  get -> {cache.get('user:7')!r}")
clock.advance(2)
print(f"t={clock.now:>5.0f}s  get -> {cache.get('user:7')!r}")
clock.advance(86400)
cache.put("user:7", "Grace")
print(f"t={clock.now:>5.0f}s  get -> {cache.get('user:7')!r}  (re-cached)")


class RecordingMailer:
    """A fake with a mock's memory: it works, and it remembers every call."""

    def __init__(self):
        self.sent = []

    def send(self, to, subject):
        self.sent.append((to, subject))


def notify_expired(cache, keys, mailer):
    for key in keys:
        if cache.get(key) is None:
            mailer.send(f"{key}@example.com", "Your session expired")


mailer = RecordingMailer()
notify_expired(cache, ["user:7", "user:8"], mailer)
print("emails the fake recorded:", mailer.sent)
```

```text
t=    0s  get -> 'Ada'
t=   29s  get -> 'Ada'
t=   31s  get -> None
t=86431s  get -> 'Grace'  (re-cached)
emails the fake recorded: [('user:8@example.com', 'Your session expired')]
```

Look at what made this possible: `TTLCache` takes its clock as a constructor
argument instead of calling `time.time()` internally. That is **dependency
injection**, and it is the design decision — not the testing library — that
makes the code testable. A class that reaches out and grabs its
dependencies can only be tested by monkey-patching; a class that is *handed*
them can be tested by handing it something else. Java's Mockito and Python's
`unittest.mock` automate the bookkeeping, but the fifteen-line hand-written
fake above is often clearer, and it never lies about an API that has since
changed.

## What to test, and what not to

The last honest section. [Section 24.2](../ch24-practice/02-testing.md)
showed that 100% line coverage can miss the empty-input case entirely, and
that is the key to reading coverage numbers correctly: **coverage tells you
what was executed, never what was verified.** A test suite that calls every
line and asserts nothing scores 100%.

Worth testing, in roughly this order:

- **Every branch of your own logic**, especially the error paths.
- **Boundaries**: empty, one element, exactly full, one past full, the first
  and last index, zero, negative, the maximum value.
- **The invariant**, after every operation, via an `@AfterEach`-style hook.
- **Every bug you have ever fixed** — a regression test is a promise that it
  will not come back, and it costs three minutes at the moment you already
  understand the bug.
- **The public contract**, not the private helpers. Tests against internals
  break on every refactor and are the main reason people come to resent
  their test suite.

Not worth testing:

- **The language and the standard library.** `assertEquals(3, 1 + 2)` and a
  test that `HashMap.get` works are noise.
- **Trivial getters and setters** with no logic.
- **Generated code, and third-party libraries** — test *your use* of them.
- **Exact log messages or private method names**, which change constantly
  without any behaviour changing.

And a working target: aim for a suite that is fast enough to run on every
save (seconds, not minutes), deterministic enough that a red result is always
a real bug, and specific enough that a failure names the cause. A suite with
those three properties gets run. One without them gets ignored, then
disabled, then deleted.

!!! warning "Common mistakes"
    - **Arguments backwards in `assertEquals`.** Expected first, actual
      second — otherwise every failure message lies to you.
    - **`assertTrue(a.equals(b))` instead of `assertEquals(a, b)`.** Both
      fail correctly, but the first prints only "expected true".
    - **Sharing mutable state between tests** through a `static` field, a
      class attribute, or a real database. This is the flaky-test factory
      demonstrated above.
    - **Comparing floating-point results with `==`.** Use a delta, and choose
      it deliberately.
    - **`@Disabled` with no reason**, which becomes a permanently dead test
      nobody dares delete.
    - **Testing private methods.** Test through the public interface; if that
      is impossible, the class is probably doing too much.
    - **Treating a coverage percentage as a quality score.** It measures
      execution, not verification.

## Check your understanding

??? success "1. Why does JUnit create a new instance of the test class for every test method?"

    So that fields written by one test cannot be seen by another. JUnit makes
    no promise about the order in which tests run, and CI may run them in
    parallel, so any dependence between tests is a latent bug. A fresh
    instance per method makes each test start from the state its
    `@BeforeEach` establishes and nothing else. The runnable shopping-cart
    block shows what happens when that guarantee is broken: the same two
    tests pass in one order and fail in the other.

??? success "2. This test passes but is nearly worthless. Why?"

    ```java
    @Test
    void sortWorks() {
        int[] data = {3, 1, 2};
        Sorter.sort(data);
        assertTrue(data.length == 3);
    }
    ```

    It never checks that anything was *sorted*. The array length is
    unchanged by any implementation, including one whose body is empty, so
    the assertion cannot fail for a reason you care about — yet it counts as
    a passing test and covers every line of `sort`. That is coverage without
    verification. The real assertion is
    `assertArrayEquals(new int[]{1, 2, 3}, data)`.

??? success "3. A test fails only when the whole suite runs, and passes on its own. What is the first thing to suspect?"

    Shared mutable state. Something earlier in the suite left a static field,
    a singleton, a cache, a temporary file, or a database row in a state your
    test did not expect. Second suspects: a dependence on the system clock or
    the current date, and an unseeded random number generator. All three are
    fixed the same way — give the test its own state, and inject the clock
    and the random source rather than reaching for the global ones.

??? success "4. What does the micro-framework's report show if `RingBuffer.__init__` is changed to raise `TypeError` instead of `ValueError` for a bad capacity?"

    Only the `a zero capacity is rejected` case changes, and it becomes a
    **FAIL** rather than an ERROR: `assert_raises` catches the wrong
    exception type on purpose and converts it into a `TestFailure` reading
    `expected ValueError but TypeError was raised: ...`. Every other test
    still passes, because `@before_each` builds `RingBuffer(3)`, which is a
    legal capacity. That failure-versus-error split is what separates "the
    behaviour is wrong" from "the test could not even run" — and if you
    instead broke `__init__` for *valid* capacities, `@before_each` would
    raise and the report would show nine ERRORs, pointing straight at the
    fixture rather than at nine unrelated tests.
