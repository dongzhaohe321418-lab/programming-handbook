# 39.1 Lambdas and higher-order functions

[Chapter 3](../ch03-functions/03-writing-functions.md) taught you to write a
function and call it. This section takes the same `def` you already know and
points out something it has been quietly doing all along: it creates an
**object** and binds a name to it, exactly like `x = 7` does. Once you see a
function as a value — something you can store, pass around, and hand back —
half of modern programming stops looking clever and starts looking obvious.
Sorting a list of employees three different ways, registering a button
handler, building a pipeline: all of them are just "put a function where a
value normally goes".

## A function is a value

Here is the whole idea in one line: **`def name(...)` is an assignment
statement**. It builds a function object and stores it under `name`.

Which means the name is not special. Once a function is an ordinary value
there are exactly three things you can do with it, and the rest of this
section is those three in order: **store** it, **pass** it, and **return**
it.

### Store it: two names, one function

```python
def shout(text):
    return text.upper() + "!"

yell = shout          # NO parentheses: we are naming the function, not calling it

print(yell("hello"))
print("same object?", shout is yell)
print("type:", type(shout))
print("names:", shout.__name__, "/", yell.__name__)
```

```text
HELLO!
same object? True
type: <class 'function'>
names: shout / shout
```

`shout` and `yell` are two labels on one object, the way two variables can
point at one list in [Chapter 9](../ch09-collections/01-references.md). The
`__name__` attribute still says `shout` because that is the name the object
was *born* with; the label you access it through is irrelevant.

**The parentheses are the whole difference.** The most common beginner slip
in this section is writing `yell = shout()` — with parentheses you *call* the
function and store its return value, which here would be an immediate
`TypeError` for a missing argument.

### Pass it: one function, many behaviours

```python
def apply_to_all(func, items):
    """Run func on every item and collect the results."""
    results = []
    for item in items:
        results.append(func(item))
    return results

def double(n):
    return n * 2

def square(n):
    return n * n

numbers = [1, 2, 3, 4]
print(apply_to_all(double, numbers))
print(apply_to_all(square, numbers))
print(apply_to_all(str, numbers))      # built-ins are values too
```

```text
[2, 4, 6, 8]
[1, 4, 9, 16]
['1', '2', '3', '4']
```

`apply_to_all` does not know or care what `func` does. It knows only that
`func` can be called with one argument.

That single parameter turns one six-line function into an unlimited family of
transformations — and you have just hand-written `map`, which
[section 39.2](02-map-filter-reduce.md) will formally introduce.

### Return it: the factory pattern

A function that returns a function is called a **factory**:

```python
def make_tagger(tag):
    """Build a function that wraps text in one particular HTML tag."""
    def tag_it(text):
        return f"<{tag}>{text}</{tag}>"
    return tag_it          # returning the function, not calling it

bold = make_tagger("b")
italic = make_tagger("i")

print(bold("streams"))
print(italic("pipes"))
print("two different objects?", bold is not italic)
print("both born as:", bold.__name__, italic.__name__)
```

```text
<b>streams</b>
<i>pipes</i>
two different objects? True
both born as: tag_it tag_it
```

Two distinct function objects, each remembering a different `tag`. How a
returned function remembers a variable that has gone out of scope is the
subject of **closures**, below — it is the one genuinely surprising idea in
this section, so we will prove it rather than assert it.

## `lambda`: a function with no name

When the function you want to pass is tiny — one expression, used once — a
whole `def` is ceremony. `lambda` is Python's shorthand:

```text
lambda parameters: expression
```

The value of the whole thing is a function object. There is no `return`
keyword because the expression *is* the return value.

```python
def double_def(n):
    return n * 2

double_lambda = lambda n: n * 2      # exactly the same function, written inline

print(double_def(21), double_lambda(21))
print("agree on 0..4?", [double_def(i) == double_lambda(i) for i in range(5)])
print("names:", double_def.__name__, "/", double_lambda.__name__)
```

```text
42 42
agree on 0..4? [True, True, True, True, True]
names: double_def / <lambda>
```

The only visible difference is the name: a lambda is anonymous, so its
`__name__` is the placeholder `<lambda>`, which is what you will see in a
traceback when one blows up.

That is precisely why the code above is a bad habit in real programs: **if you
are giving a lambda a name, use `def`**. The official Python style guide says
so, and the reason is the traceback. Lambdas are for the throwaway case where
the function is *an argument* and never gets a name at all.

### The deliberate limits

A lambda body must be **one expression**. Not one line — one *expression*. No
assignment, no `return`, no `if:` statement, no `for` loop, no `try`. This is
a design decision, not an oversight: it keeps anonymous functions small
enough to read inside an argument list.

```python
# raises SyntaxError
# A lambda body may not contain a statement. Assignment is a statement:
running_total = 0
accumulate = lambda n: running_total = running_total + n
```

The rule is easy to test yourself: *if you could not legally put it after
`return`, you cannot put it in a lambda.* Conditional **expressions** are
legal, because `a if cond else b` is an expression:

```python
classify = lambda n: "even" if n % 2 == 0 else "odd"
print([classify(n) for n in range(5)])

# Multiple parameters, defaults, and *args all work exactly as in def:
area = lambda w, h=1: w * h
print(area(3, 4), area(5))
```

```text
['even', 'odd', 'even', 'odd', 'even']
12 5
```

## Where lambdas genuinely help

Three places, and outside them you should reach for `def`.

### 1. `sorted(key=...)`

The `key` parameter takes a function; `sorted` calls it once per element and
orders by whatever comes back. One list of records, four orderings, no copies
of the sorting code:

```python
records = [
    {"name": "Ada",     "dept": "eng", "salary": 120, "hired": 2019},
    {"name": "Grace",   "dept": "eng", "salary": 145, "hired": 2015},
    {"name": "Linus",   "dept": "ops", "salary": 98,  "hired": 2021},
    {"name": "Barbara", "dept": "eng", "salary": 145, "hired": 2012},
    {"name": "Radia",   "dept": "net", "salary": 132, "hired": 2018},
]

orderings = [
    ("by name",             lambda r: r["name"]),
    ("by salary, high 1st", lambda r: -r["salary"]),
    ("by dept, then name",  lambda r: (r["dept"], r["name"])),
    ("by name length",      lambda r: len(r["name"])),
]

for label, key_fn in orderings:
    print(f"{label:<20} {[r['name'] for r in sorted(records, key=key_fn)]}")
```

```text
by name              ['Ada', 'Barbara', 'Grace', 'Linus', 'Radia']
by salary, high 1st  ['Grace', 'Barbara', 'Radia', 'Ada', 'Linus']
by dept, then name   ['Ada', 'Barbara', 'Grace', 'Radia', 'Linus']
by name length       ['Ada', 'Grace', 'Linus', 'Radia', 'Barbara']
```

Two details worth pocketing:

- **A tuple key sorts by layers.** Returning a **tuple** from the key sorts by
  the first element, then breaks ties with the second — that is how
  "department, then name" happens in one line.
- **Python's sort is *stable*.** Grace comes before Barbara in the salary
  ordering even though they earn the same 145, because equal keys keep their
  original relative order ([Chapter 22](../ch22-sorting/index.md) made the
  same point about merge sort).

### 2. `min` and `max` with a key

Same protocol, one winner:

```python
# continues
print("highest paid: ", max(records, key=lambda r: r["salary"])["name"])
print("longest serving:", min(records, key=lambda r: r["hired"])["name"])
print("longest name:  ", max((r["name"] for r in records), key=len))
print("total payroll: ", sum(r["salary"] for r in records))
```

```text
highest paid:  Grace
longest serving: Barbara
longest name:   Barbara
total payroll:  640
```

Grace wins the salary tie because `max` keeps the *first* maximum it sees and
Grace appears earlier in the list. Ties are a real source of "why did it pick
that one?" bugs; the rule is first-wins for `max` and `min` alike.

### 3. Callbacks

A callback is a function you hand to somebody else so *they* can call it
later, when something happens. That is the entire architecture of the event
loop from [section 14.3](../ch14-beyond/03-guis-and-beyond.md): the framework
owns the loop, you supply the handlers.

```python
handlers = {}

def on(event, callback):
    """Register a function to run when `event` arrives."""
    handlers[event] = callback

on("click", lambda pos: print(f"  handler: clicked at {pos}"))
on("key",   lambda ch:  print(f"  handler: key {ch!r} pressed"))
on("quit",  lambda _:   print("  handler: goodbye"))

# The framework's event loop. Imagine these events coming from a real user.
incoming = [("click", (10, 20)), ("key", "s"), ("click", (44, 3)), ("quit", None)]
for event, payload in incoming:
    print(f"event {event!r}")
    handlers[event](payload)
```

```text
event 'click'
  handler: clicked at (10, 20)
event 'key'
  handler: key 's' pressed
event 'click'
  handler: clicked at (44, 3)
event 'quit'
  handler: goodbye
```

Nothing in the loop knows what any handler does. Add a new event type by
adding one `on(...)` line — the loop never changes. This inversion, "don't
call us, we'll call you", is what people mean by *event-driven* programming.

## Higher-order functions, written by hand

A **higher-order function** is a function that takes a function as an
argument, returns one, or both. You have already written one (`apply_to_all`).
Here are the three classics, each in a handful of lines.

```python
def apply_twice(func, value):
    """f(f(value)) — useful surprisingly often, and the simplest HOF there is."""
    return func(func(value))

def compose(f, g):
    """Return a new function h where h(x) == f(g(x)) — g runs first."""
    def h(x):
        return f(g(x))
    return h

def make_multiplier(factor):
    """A factory: build a function that multiplies by one fixed number."""
    def multiply(n):
        return n * factor
    return multiply

print("apply_twice:", apply_twice(lambda n: n + 3, 10))
print("apply_twice:", apply_twice(str.upper, "hi"))

strip_then_upper = compose(str.upper, str.strip)
print("compose:", repr(strip_then_upper("  quiet  ")))

double, triple = make_multiplier(2), make_multiplier(3)
print("factory:", double(10), triple(10), double(triple(1)))
```

```text
apply_twice: 16
apply_twice: HI
compose: 'QUIET'
factory: 20 30 6
```

Read `compose(f, g)` carefully — the order trips people up. It matches the
mathematical convention $(f \circ g)(x) = f(g(x))$: the function written
*second* runs *first*, because it is the one closest to the argument.

### Closures: how `multiply` remembers `factor`

`make_multiplier(3)` returns and its local variable `factor` should be gone —
the call finished, its frame is dead. Yet `triple(10)` still gives 30. The
inner function did not copy the value; Python kept the *variable itself*
alive in a little box called a **cell**, and attached it to the function
object. A function plus the captured variables it needs is a **closure**.

You can look right at the evidence:

```python
def make_multiplier(factor):
    def multiply(n):
        return n * factor
    return multiply

double = make_multiplier(2)
triple = make_multiplier(3)

print("free variables of multiply:", double.__code__.co_freevars)
print("double captured:", double.__closure__[0].cell_contents)
print("triple captured:", triple.__closure__[0].cell_contents)
print("separate cells? ", double.__closure__[0] is not triple.__closure__[0])
print(double(10), triple(10))
```

```text
free variables of multiply: ('factor',)
double captured: 2
triple captured: 3
separate cells?  True
20 30
```

Three things to read out of that output:

- **`co_freevars`** lists the names the inner function uses but does not
  define — here, `factor`.
- **`__closure__`** holds one cell per free variable, and printing
  `.cell_contents` shows the captured value.
- **Each call to the factory creates a fresh cell**, which is why `double` and
  `triple` do not interfere.

You will rarely poke at `__closure__` in real code — but seeing the cell turns
"somehow it remembers" into a mechanism.

### The late-binding trap

Now the bug that catches everyone exactly once. It follows directly from the
mechanism above: a closure captures a **variable**, not the variable's value
at capture time.

```python
makers = []
for factor in (2, 3, 4):
    makers.append(lambda n: n * factor)     # captures `factor`, not 2/3/4

print("expected [20, 30, 40]")
print("actual  ", [m(10) for m in makers])
print("factor is still:", factor)
```

```text
expected [20, 30, 40]
actual   [40, 40, 40]
factor is still: 4
```

All three lambdas closed over the *same* `factor` variable — the loop
variable of the enclosing scope — and by the time any of them ran, the loop
had finished and left `factor` at 4. Nothing is evaluated early; everything
looks up `factor` at call time.

Two fixes, and both are worth knowing:

```python
makers_default = []
for factor in (2, 3, 4):
    makers_default.append(lambda n, factor=factor: n * factor)   # fix 1

def make_multiplier(factor):
    return lambda n: n * factor

makers_factory = [make_multiplier(f) for f in (2, 3, 4)]         # fix 2

print("default-argument fix:", [m(10) for m in makers_default])
print("factory fix:         ", [m(10) for m in makers_factory])
```

```text
default-argument fix: [20, 30, 40]
factory fix:          [20, 30, 40]
```

**Fix 1 — a default argument snapshots the value.** Default arguments are
evaluated *when the function is defined*, so `factor=factor` copies the
current value into a parameter. It is compact and idiomatic, though the
repeated word looks odd the first time.

**Fix 2 — a factory gives each lambda its own cell.** Every call to
`make_multiplier` creates a fresh enclosing scope, which is the mechanism you
just printed. Prefer this one when the body is more than trivial; it is easier
to name and to test.

!!! note "The same trap in other languages"

    This is not a Python quirk. JavaScript's `var` behaved identically until
    `let` was introduced specifically to fix it, and Java sidesteps it by
    *refusing to compile*: a lambda may only capture a variable that is
    `final` or effectively final, so the offending loop variable is rejected
    outright. Java trades flexibility for a compile-time error instead of a
    3 a.m. one.

## `functools.partial`: freezing an argument

Sometimes you do not need a new function so much as an old one with some
arguments already filled in. `functools.partial` does exactly that, and reads
better than a lambda for the purpose.

```python
from functools import partial

def power(base, exponent):
    return base ** exponent

square = partial(power, exponent=2)
cube   = partial(power, exponent=3)
hex_to_int = partial(int, base=16)          # works on built-ins too

print(square(7), cube(3))
print(hex_to_int("ff"), hex_to_int("1a"))
print([square(n) for n in range(1, 6)])
print("partial keeps the original:", square.func is power, square.keywords)
```

```text
49 27
255 26
[1, 4, 9, 16, 25]
partial keeps the original: True {'exponent': 2}
```

`partial(power, exponent=2)` is roughly `lambda base: power(base, 2)`, with
two advantages:

- **It remembers what it wrapped.** `.func`, `.args`, and `.keywords` are all
  readable — you just printed two of them — so a `partial` is debuggable in a
  way a lambda is not.
- **It cannot fall into the late-binding trap**, because the arguments are
  captured at construction time rather than looked up at call time.

## The same ideas in Java

Java grew lambdas in Java 8, and its version is a good illustration of how
the same concept looks under a static type system.

=== "Python"

    ```python
    doubler = lambda x: x * 2
    print(doubler(21))

    lengths = list(map(len, ["alpha", "be", "gamma"]))
    print(lengths)

    staff = ["Radia", "Ada", "Grace"]
    print(sorted(staff, key=len))
    print(sorted(staff, key=len, reverse=True))
    ```

=== "Java"

    ```java
    // A lambda's TYPE is a functional interface — an interface with
    // exactly one abstract method.
    Function<Integer, Integer> doubler = x -> x * 2;
    System.out.println(doubler.apply(21));      // 42

    // A method reference: "the length method, used as a value".
    Function<String, Integer> len = String::length;

    List<String> staff = new ArrayList<>(List.of("Radia", "Ada", "Grace"));
    staff.sort(Comparator.comparing(String::length));
    staff.sort(Comparator.comparing(String::length).reversed());
    ```

The four functional interfaces you will meet constantly live in
`java.util.function`:

| Java interface | Its one method | Python equivalent |
|---|---|---|
| `Function<T,R>` | `R apply(T t)` | any one-argument function |
| `Predicate<T>` | `boolean test(T t)` | a function returning `True`/`False` |
| `Consumer<T>` | `void accept(T t)` | a function called for its side effect |
| `Supplier<T>` | `T get()` | a zero-argument factory |

!!! info "Java corner — a lambda is an object"

    In Python a function *is* a value; there is nothing underneath. In Java a
    lambda is compiled into an object implementing a **functional interface**
    — an interface with exactly one abstract method — and the interface is
    chosen by the *target type* of the expression. That is why
    `x -> x * 2` has no meaning on its own: written where a
    `Function<Integer,Integer>` is expected it becomes one, and written where
    a `UnaryOperator<Integer>` is expected it becomes that instead. Two
    practical consequences: you call it with the interface's method name
    (`doubler.apply(21)`, `pred.test(x)`), and a Java lambda may only capture
    effectively-final variables, so the late-binding trap above cannot
    compile. `String::length` is a **method reference** — the same value,
    written without the arrow when the lambda would only forward its
    arguments.

## Pure functions, and why testing gets easier

A **pure function** obeys two rules: its result depends only on its
arguments, and it changes nothing outside itself. No mutating the caller's
list, no writing to a global, no touching a file. The payoff is that a pure
function is completely described by a table of inputs and outputs — which is
exactly what a test is.

[Section 8.2](../ch08-grids/02-arrays-functions.md) showed that a list
argument arrives as a *reference*, so a function can rewrite the caller's
data. Here is that fact turned into a testing problem:

```python
def add_bonus_impure(scores, bonus):
    for i in range(len(scores)):
        scores[i] += bonus          # rewrites the CALLER's list
    return scores

def add_bonus_pure(scores, bonus):
    return [s + bonus for s in scores]     # builds a new list

original = [10, 20, 30]
print("impure ->", add_bonus_impure(original, 5), "| caller's list:", original)

original = [10, 20, 30]
print("pure   ->", add_bonus_pure(original, 5), "| caller's list:", original)
```

```text
impure -> [15, 25, 35] | caller's list: [15, 25, 35]
pure   -> [15, 25, 35] | caller's list: [10, 20, 30]
```

Both return the right answer. Only one of them left the input alone.

### Why impurity breaks a test suite

Now watch what the difference does to a test suite that shares a fixture —
the same test, the same input, run twice:

```python
# continues
scores = [10, 20, 30]          # a shared fixture, as in a real test file

def test_impure():
    return add_bonus_impure(scores, 5) == [15, 25, 35]

def test_pure():
    return add_bonus_pure(scores, 5) == [15, 25, 35]

print("impure test, first run: ", test_impure())
print("impure test, second run:", test_impure())
scores = [10, 20, 30]
print("pure test,   first run: ", test_pure())
print("pure test,   second run:", test_pure())
```

```text
impure test, first run:  True
impure test, second run: False
pure test,   first run:  True
pure test,   second run: True
```

The impure test passes or fails depending on **what ran before it**. That is
the single most demoralising kind of bug: a test suite that is green when you
run one file and red when you run all of them, or that depends on alphabetical
test order. Pure functions cannot have it.

This is why the rest of the chapter — `map`, `filter`, comprehensions,
generator pipelines — is built out of functions that return new data instead
of editing old data. Purity is not a moral position; it is what makes a
pipeline safe to reorder, re-run, cache, and eventually run in parallel.

!!! warning "Common mistakes"

    - **Calling instead of passing.** `sorted(records, key=r["name"])` or
      `on("click", handler())` — the parentheses call the function *now* and
      pass the result. Pass the bare name: `key=lambda r: r["name"]`,
      `on("click", handler)`.
    - **Naming a lambda.** `f = lambda x: ...` gives you a function whose
      traceback says `<lambda>`. If it deserves a name it deserves a `def`.
    - **Putting a statement in a lambda.** `lambda x: print(x); x + 1` or an
      assignment inside the body is a `SyntaxError`. One expression only.
    - **The late-binding loop.** Creating lambdas inside a `for` loop that all
      capture the loop variable. Snapshot it with `param=value` or build each
      one through a factory.
    - **Forgetting `key=`.** `sorted(records, lambda r: r["name"])` fails,
      because the second positional parameter of `sorted` does not exist —
      `key` is keyword-only.

## Check your understanding

??? success "1. What does this print, and why?"

    ```python
    def greet(name):
        return "hi " + name

    f = greet
    g = greet("ada")
    print(type(f), type(g))
    ```

    `<class 'function'> <class 'str'>`. `f = greet` copies the *reference to
    the function*; `g = greet("ada")` calls it and stores the returned string.
    The presence or absence of parentheses is the whole difference, and it is
    the single most common mix-up when functions become values.

??? success "2. Rewrite `sorted(words, key=lambda w: w.lower())` without a lambda."

    `sorted(words, key=str.lower)`. `str.lower` is already a function that
    takes one string and returns one string, so wrapping it in a lambda adds a
    layer of nothing. The same shortcut applies to `len`, `str.strip`,
    `abs`, and any other one-argument function you would otherwise forward to.

??? success "3. Predict the output, then explain the fix."

    ```python
    fns = [lambda: i for i in range(3)]
    print([f() for f in fns])
    ```

    It prints `[2, 2, 2]`. Each lambda closed over the comprehension's
    variable `i`, and all three are called after the comprehension finished
    with `i` at 2. The fix is the same as in the loop case:
    `fns = [lambda i=i: i for i in range(3)]` gives `[0, 1, 2]`, because a
    default argument is evaluated when the lambda is created.

??? success "4. Why is `add_bonus_pure` easier to test than `add_bonus_impure`?"

    Because its answer depends only on its arguments. You can call it in any
    order, any number of times, from any test, and get the same result — so a
    test is one line with no setup and no cleanup. The impure version writes
    into the caller's list, so its result depends on the history of the whole
    test session; running the same assertion twice gives two different
    answers, as the runnable comparison above shows.
