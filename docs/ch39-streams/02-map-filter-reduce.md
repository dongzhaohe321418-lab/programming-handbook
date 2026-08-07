# 39.2 Map, filter, reduce, and Java Streams

Take any data-processing program you have written and squint at it. Almost
all of it is three moves repeated: **change every item** into something else,
**throw away** the items you do not want, and **squash what is left** into a
single answer. Those moves have names — map, filter, reduce — and they are
the vocabulary of Java's Streams API, SQL, Spark, and every dataframe library
in existence. This section builds each one by hand first, in a few lines, so
that the built-in versions never feel like magic; then it shows why Python
prefers comprehensions for the everyday case, and finishes by lining Java's
Stream operations up against their Python equivalents one for one.

## Three verbs

| Verb | Question it answers | In → out |
|---|---|---|
| **map** | "what should each item become?" | $n$ items in, $n$ items out |
| **filter** | "which items do I keep?" | $n$ items in, $\le n$ items out |
| **reduce** | "how do I combine them into one?" | $n$ items in, **one** value out |

Every pipeline in the rest of this chapter is some arrangement of those
three. Notice the shapes: map preserves the count, filter can only shrink it,
reduce collapses it. If you can say which of the three a piece of code is
doing, you can usually delete the loop.

## `map` — transform every item

Here it is, written from scratch. There is nothing else inside the real one.

```python
def my_map(func, items):
    result = []
    for item in items:
        result.append(func(item))
    return result

def celsius_to_f(c):
    return c * 9 / 5 + 32

temps = [0, 21, 37, 100]
print(my_map(celsius_to_f, temps))
print(my_map(str.upper, ["ada", "grace"]))
print(my_map(len, ["pipe", "stream", "map"]))
```

```text
[32.0, 69.8, 98.6, 212.0]
['ADA', 'GRACE']
[4, 6, 3]
```

Four lines, no magic. The built-in `map(func, iterable)` does the same job
with two differences: it accepts *any* iterable (a file, a generator, a
range), and it does not build a list — more on that in a moment.

```python
def celsius_to_f(c):
    return c * 9 / 5 + 32

temps = [0, 21, 37, 100]
print(list(map(celsius_to_f, temps)))

# map over several iterables at once: func gets one item from each
first = ["Ada", "Grace", "Radia"]
last  = ["Lovelace", "Hopper", "Perlman"]
print(list(map(lambda a, b: f"{a} {b}", first, last)))
```

```text
[32.0, 69.8, 98.6, 212.0]
['Ada Lovelace', 'Grace Hopper', 'Radia Perlman']
```

## `filter` — keep the interesting ones

Same treatment. The function you pass is called a **predicate**: it takes one
item and returns something truthy or falsy.

```python
def my_filter(predicate, items):
    result = []
    for item in items:
        if predicate(item):
            result.append(item)
    return result

words = ["stream", "pipe", "map", "generator", "lazy", "fold"]
print(my_filter(lambda w: len(w) > 4, words))
print(list(filter(lambda w: len(w) > 4, words)))     # the built-in agrees
print(list(filter(str.isupper, ["OK", "no", "YES"])))

# A quirk worth knowing: filter(None, xs) drops every falsy item.
print(list(filter(None, [0, 1, "", "hi", None, [], [7]])))
```

```text
['stream', 'generator']
['stream', 'generator']
['OK', 'YES']
[1, 'hi', [7]]
```

## Laziness: nothing happens until you ask

Now the difference that surprises everybody. `my_map` above returned a list.
The real `map` returns an **iterator** — an object that has computed nothing
and will produce items one at a time, on demand. The best way to see this is
with a function that announces itself.

```python
def loud_double(n):
    print(f"  ...computing double({n})")
    return n * 2

numbers = [1, 2, 3]
print("about to call map")
result = map(loud_double, numbers)
print("map returned a", type(result).__name__, "and printed nothing")

print("now consuming it:")
print("  ->", list(result))

print("consuming a second time:")
print("  ->", list(result))
```

```text
about to call map
map returned a map and printed nothing
now consuming it:
  ...computing double(1)
  ...computing double(2)
  ...computing double(3)
  -> [2, 4, 6]
consuming a second time:
  -> []
```

Two lessons in one output. First, **`map` did no work at all** until `list()`
pulled on it — the work happens at consumption time, not construction time.
Second, an iterator is **single-use**: the second `list(result)` is empty
because the iterator is exhausted. If you need the results twice, materialise
them once with `list(...)` and reuse that.

Laziness gets more interesting when stages are chained, because items flow
through the whole pipeline *one at a time* rather than stage by stage:

```python
def loud_double(n):
    print(f"  double({n})")
    return n * 2

def loud_is_big(n):
    print(f"    is_big({n})?")
    return n > 4

pipeline = filter(loud_is_big, map(loud_double, [1, 2, 3]))
print("pipeline built — no output above this line, so nothing has run")

print("asking for ONE item:")
print("got:", next(pipeline))

print("asking for the rest:")
print("got:", list(pipeline))
```

```text
pipeline built — no output above this line, so nothing has run
asking for ONE item:
  double(1)
    is_big(2)?
  double(2)
    is_big(4)?
  double(3)
    is_big(6)?
got: 6
asking for the rest:
got: []
```

Read the interleaving carefully: `double(1)`, then immediately `is_big(2)?`,
then back for the next item. The pipeline does **not** double everything and
then filter everything. Each element is pulled through every stage before the
next element starts. That is what makes a chain of lazy stages usable on a
file bigger than memory — the subject of
[section 39.3](03-pipelines.md) — and it is exactly how Java Streams behave
too.

## Comprehensions: the Pythonic spelling

Python has `map` and `filter`, and mostly uses neither, because the
comprehension syntax from [Chapter 9](../ch09-collections/02-dynamic-lists.md)
says the same thing with fewer moving parts.

| Goal | With `map`/`filter` | As a comprehension |
|---|---|---|
| transform each item | `map(f, xs)` | `[f(x) for x in xs]` |
| keep some items | `filter(p, xs)` | `[x for x in xs if p(x)]` |
| both at once | `map(f, filter(p, xs))` | `[f(x) for x in xs if p(x)]` |
| transform *lazily* | `map(f, xs)` | `(f(x) for x in xs)` |
| build a set | `set(map(f, xs))` | `{f(x) for x in xs}` |
| build a dict | `dict(zip(ks, vs))` | `{k: f(v) for k, v in pairs}` |
| flatten | `chain.from_iterable(xss)` | `[x for xs in xss for x in xs]` |

```python
nums = range(1, 11)

by_map  = list(map(lambda n: n * n, filter(lambda n: n % 2, nums)))
by_comp = [n * n for n in nums if n % 2]
print(by_map)
print(by_comp)
print("identical:", by_map == by_comp)

# Round brackets make it lazy — a generator expression, section 39.3
lazy = (n * n for n in nums if n % 2)
print("lazy object:", type(lazy).__name__, "->", list(lazy))
```

```text
[1, 9, 25, 49, 81]
[1, 9, 25, 49, 81]
identical: True
lazy object: generator -> [1, 9, 25, 49, 81]
```

**When to use which.** The rule that survives code review:

- If you would have to write `lambda` to use `map`, write a comprehension.
  `[n * n for n in nums]` beats `map(lambda n: n * n, nums)` on every count.
- If the function **already exists and takes exactly one argument**, `map` is
  cleaner: `map(str.strip, lines)` says less than
  `[line.strip() for line in lines]`, and `map(int, fields)` is idiomatic.
- If you want laziness, use `map`/`filter` or a generator expression, never a
  list comprehension.

## Chaining: a four-stage pipeline over records

Real work is a chain: parse the raw text, drop the rows you do not want,
reshape what survives, then aggregate. Here is that shape end to end, with
the data printed after every stage so you can see it change.

```python
raw = [
    "2024-01-03,widget,4,9.99",
    "2024-01-03,gizmo,1,24.50",
    "# quarterly export -- ignore this line",
    "2024-01-04,widget,12,9.99",
    "2024-01-05,doohickey,2,3.75",
    "2024-01-05,widget,0,9.99",
    "2024-01-06,gizmo,3,24.50",
]

# --- stage 1: parse ------------------------------------------------------
def parse(line):
    date, item, qty, price = line.split(",")
    return {"date": date, "item": item, "qty": int(qty), "price": float(price)}

rows = [parse(line) for line in raw if not line.startswith("#")]
print("1. parsed  ", len(rows), "rows; first:", rows[0])

# --- stage 2: filter -----------------------------------------------------
sold = [r for r in rows if r["qty"] > 0]
print("2. filtered", len(sold), "rows with qty > 0")

# --- stage 3: transform --------------------------------------------------
priced = [{**r, "total": round(r["qty"] * r["price"], 2)} for r in sold]
for r in priced:
    print(f"   {r['date']}  {r['item']:<10} {r['qty']:>3} x {r['price']:>6.2f}"
          f" = {r['total']:>7.2f}")

# --- stage 4: aggregate --------------------------------------------------
revenue = sum(r["total"] for r in priced)
by_item = {}
for r in priced:
    by_item[r["item"]] = round(by_item.get(r["item"], 0) + r["total"], 2)

print("4. revenue :", round(revenue, 2))
print("   by item :", by_item)
print("   best    :", max(by_item, key=by_item.get))
```

```text
1. parsed   6 rows; first: {'date': '2024-01-03', 'item': 'widget', 'qty': 4, 'price': 9.99}
2. filtered 5 rows with qty > 0
   2024-01-03  widget       4 x   9.99 =   39.96
   2024-01-03  gizmo        1 x  24.50 =   24.50
   2024-01-04  widget      12 x   9.99 =  119.88
   2024-01-05  doohickey    2 x   3.75 =    7.50
   2024-01-06  gizmo        3 x  24.50 =   73.50
4. revenue : 265.34
   by item : {'widget': 159.84, 'gizmo': 98.0, 'doohickey': 7.5}
   best    : widget
```

Each stage is a single expression that takes a list and returns a new list —
no stage edits the one before it, which means you can print, test, or reorder
any stage independently. That is the payoff of the pure-function discipline
from [section 39.1](01-lambdas.md). Note `{**r, "total": ...}` in stage 3: it
builds a *new* dict with one extra key rather than mutating `r`.

!!! tip "Money and floats"

    `round(..., 2)` is doing real work here: `0.1 + 0.2` is not `0.3` in
    binary floating point, as [Chapter 2](../ch02-data/02-number-systems.md)
    warned. For anything where a cent matters, real systems store integer
    **cents** or use `decimal.Decimal`, never a bare `float`.

## The everyday functional toolkit

You do not need a library for most aggregations — the built-ins already are
the functional toolkit, and each one takes a stream of items and gives back
an answer.

```python
sales = [
    {"item": "widget",    "qty": 4,  "total": 39.96},
    {"item": "gizmo",     "qty": 1,  "total": 24.50},
    {"item": "widget",    "qty": 12, "total": 119.88},
    {"item": "doohickey", "qty": 2,  "total": 7.50},
]

print("sum   :", round(sum(r["total"] for r in sales), 2))
print("count :", sum(1 for r in sales if r["item"] == "widget"))
print("any   :", any(r["total"] > 100 for r in sales))
print("all   :", all(r["qty"] > 0 for r in sales))
print("max   :", max(sales, key=lambda r: r["total"])["item"])
print("sorted:", [r["item"] for r in sorted(sales, key=lambda r: -r["qty"])])

print("enumerate:")
for rank, r in enumerate(sorted(sales, key=lambda r: -r["total"]), start=1):
    print(f"   {rank}. {r['item']:<10} {r['total']:>7.2f}")
```

```text
sum   : 191.84
count : 2
any   : True
all   : True
max   : widget
sorted: ['widget', 'widget', 'doohickey', 'gizmo']
enumerate:
   1. widget      119.88
   2. widget       39.96
   3. gizmo        24.50
   4. doohickey     7.50
```

Seven one-line aggregations, no loop bodies to get wrong. `sum(1 for r in sales if ...)`
is the idiomatic "count matching items", and `enumerate(..., start=1)` gives
you the rank without a manual counter.

`zip` is the one that repays a closer look, because it fails silently:

```python
names = ["widget", "gizmo", "doohickey"]
quantities = [4, 1, 2]

print("zip  :", list(zip(names, quantities)))
print("dict :", dict(zip(names, quantities)))

# zip stops at the SHORTEST input — a classic silent data loss
print("short:", list(zip([1, 2, 3], ["a", "b"])))
print("strict-safe check:", len([1, 2, 3]) == len(["a", "b"]))

# enumerate is zip(count(), xs) in disguise
for i, (name, qty) in enumerate(zip(names, quantities)):
    print(f"  {i}: {name} x{qty}")
```

```text
zip  : [('widget', 4), ('gizmo', 1), ('doohickey', 2)]
dict : {'widget': 4, 'gizmo': 1, 'doohickey': 2}
short: [(1, 'a'), (2, 'b')]
strict-safe check: False
  0: widget x4
  1: gizmo x1
  2: doohickey x2
```

The third line is the trap: `zip([1, 2, 3], ["a", "b"])` quietly produces two
pairs and drops the 3. No warning, no error — just a row missing from your
report. On Python 3.10 and later, `zip(a, b, strict=True)` raises a
`ValueError` instead, and it is worth the extra word whenever the two inputs
are *supposed* to be the same length.

## `reduce`, done carefully

`reduce(func, items, initial)` folds a sequence into one value by applying a
two-argument function repeatedly, carrying the running result along. Here it
is by hand — this is the whole implementation:

```python
def my_reduce(func, items, initial):
    accumulator = initial
    for item in items:
        accumulator = func(accumulator, item)
    return accumulator

nums = [3, 1, 4, 1, 5]
print("sum    :", my_reduce(lambda acc, n: acc + n, nums, 0))
print("product:", my_reduce(lambda acc, n: acc * n, nums, 1))
print("max    :", my_reduce(lambda acc, n: acc if acc > n else n, nums, nums[0]))
print("count  :", my_reduce(lambda acc, n: acc + 1, nums, 0))

# Trace the fold to see the accumulator move
acc = 0
for n in nums:
    print(f"   acc {acc:>3} + {n} -> {acc + n}")
    acc += n
```

```text
sum    : 14
product: 60
max    : 5
count  : 5
   acc   0 + 3 -> 3
   acc   3 + 1 -> 4
   acc   4 + 4 -> 8
   acc   8 + 1 -> 9
   acc   9 + 5 -> 14
```

The real one lives in `functools` — **not** in builtins, and that relocation
in Python 3 was a deliberate statement about how often you should reach for
it.

```python
from functools import reduce
import math

nums = [3, 1, 4, 1, 5]
print("reduce sum    :", reduce(lambda a, b: a + b, nums, 0))
print("builtin sum   :", sum(nums))
print("reduce product:", reduce(lambda a, b: a * b, nums, 1))
print("math.prod     :", math.prod(nums))

# Always pass the initial value. Watch what it protects you from:
empty = []
print("reduce on empty with initial:", reduce(lambda a, b: a + b, empty, 0))
print("sum on empty                :", sum(empty))
```

```text
reduce sum    : 14
builtin sum   : 14
reduce product: 60
math.prod     : 60
reduce on empty with initial: 0
sum on empty                : 0
```

Without the initial value, `reduce` uses the first item as the seed — and
has nothing to seed from when the sequence is empty:

```python
# raises TypeError
from functools import reduce

total = reduce(lambda a, b: a + b, [])   # no initial value, no items
print(total)
```

That is the single best argument for always supplying the third argument: an
empty input is not an error in your data, it is Tuesday. Note also that the
initial value fixes the *type* of the result — `reduce(op, rows, {})` folds
into a dict, `reduce(op, rows, [])` into a list.

**Why Python de-emphasizes `reduce`.** Almost every real fold already has a
name: `sum`, `math.prod`, `max`, `min`, `any`, `all`, `"".join`,
`set().union`, `collections.Counter`. Those names say what the fold *means*,
where `reduce(lambda a, b: a + b, xs, 0)` makes the reader simulate a loop in
their head. Reach for `reduce` when the combining step is genuinely custom
and associative — merging dictionaries, intersecting many sets, composing a
list of functions — and use the named tool otherwise.

```python
from functools import reduce

# A fold that has no built-in name: merge a list of config dicts, later wins.
configs = [{"host": "localhost", "port": 80},
           {"port": 8080, "debug": True},
           {"debug": False, "workers": 4}]
merged = reduce(lambda a, b: {**a, **b}, configs, {})
print(merged)

# Another: intersect many sets.
sets = [{1, 2, 3, 4}, {2, 3, 4, 5}, {3, 4, 9}]
print(reduce(lambda a, b: a & b, sets))

# And function composition, from section 39.1.
def compose_all(*funcs):
    return reduce(lambda f, g: lambda x: f(g(x)), funcs, lambda x: x)

clean = compose_all(str.title, str.strip)     # strip runs first
print(repr(clean("   grace hopper   ")))
```

```text
{'host': 'localhost', 'port': 8080, 'debug': False, 'workers': 4}
{3, 4}
'Grace Hopper'
```

## Java Streams: the same three verbs, typed

Java 8 added `java.util.stream`, and if you have followed this section you
already know the model. A stream is a lazy sequence of elements with
**intermediate** operations (which return another stream and do nothing yet)
and exactly one **terminal** operation (which pulls the data through and
produces a result).

=== "Python"

    ```python
    names = ["Ada", "Grace", "Radia", "Barbara", "Linus"]

    result = [n.upper() for n in names if len(n) > 3]
    print(result)
    print(", ".join(sorted(result)))
    print(sum(len(n) for n in names))
    ```

=== "Java"

    ```java
    List<String> names = List.of("Ada", "Grace", "Radia", "Barbara", "Linus");

    List<String> result = names.stream()          // source
            .filter(n -> n.length() > 3)          // intermediate (lazy)
            .map(String::toUpperCase)             // intermediate (lazy)
            .collect(Collectors.toList());        // TERMINAL — runs it all

    System.out.println(result);
    System.out.println(result.stream().sorted()
            .collect(Collectors.joining(", ")));
    System.out.println(names.stream().mapToInt(String::length).sum());
    ```

Java's laziness is exactly Python's. Build a chain with no terminal operation
and nothing runs at all:

```java
// Prints NOTHING. There is no terminal operation, so the stream never runs.
Stream<String> pending = names.stream()
        .peek(n -> System.out.println("seeing " + n))
        .map(String::toUpperCase);

// Add a terminal operation and the elements flow through, one at a time.
long count = pending.filter(n -> n.startsWith("A")).count();
```

Two Java-specific pieces have no exact Python spelling. The first is
`Optional`, the return type of `findFirst`, `min`, and `max` — a box that
either holds a value or is empty, forcing the caller to handle "nothing
matched" instead of returning `null`:

```java
Optional<String> first = names.stream()
        .filter(n -> n.length() > 5)
        .findFirst();

System.out.println(first.isPresent());          // true
System.out.println(first.orElse("none found")); // "Barbara"
```

Python's nearest equivalent is `next(iterator, default)`:

```python
names = ["Ada", "Grace", "Radia", "Barbara", "Linus"]

first = next((n for n in names if len(n) > 5), "none found")
missing = next((n for n in names if len(n) > 50), "none found")
print(first)
print(missing)
```

```text
Barbara
none found
```

The second is `parallelStream()`, which splits the work across the JVM's
common fork/join pool by changing one word:

```java
double total = orders.parallelStream()
        .mapToDouble(Order::total)
        .sum();
```

!!! warning "When `parallelStream()` actually pays"

    Switching `stream()` to `parallelStream()` is one word and often makes
    things **slower**. It pays only when all of the following hold: the
    source splits cheaply (an `ArrayList` or an array — not a `LinkedList` or
    a file), the collection is large (thousands of elements, not dozens), the
    work per element is genuinely CPU-bound, and the lambdas are stateless
    and side-effect free. Otherwise the cost of splitting, scheduling, and
    merging dominates. Two extra traps: every parallel stream in the JVM
    shares one common pool by default, so one long job stalls the others, and
    `forEach` gives you no ordering guarantee (use `forEachOrdered` if you
    need it). Measure before and after; never assume.

    Python's story is different but rhymes: in the standard CPython build the
    **global interpreter lock** means threads do not speed up CPU-bound
    `map`, so the parallel equivalent is
    `multiprocessing.Pool.map` (real parallelism, but the data must be
    picklable and copied to each worker) or a library like NumPy that
    releases the lock inside C code.

### Every Stream operation, mapped to Python

| Java Stream | Kind | Python equivalent |
|---|---|---|
| `collection.stream()` | source | `iter(collection)` (implicit) |
| `Stream.of(a, b, c)` | source | `iter((a, b, c))` |
| `IntStream.range(0, n)` | source | `range(n)` |
| `.filter(p)` | intermediate | `filter(p, xs)` / `(x for x in xs if p(x))` |
| `.map(f)` | intermediate | `map(f, xs)` / `(f(x) for x in xs)` |
| `.flatMap(f)` | intermediate | `chain.from_iterable(map(f, xs))` |
| `.distinct()` | intermediate | `dict.fromkeys(xs)` (order-keeping) or `set(xs)` |
| `.sorted(cmp)` | intermediate | `sorted(xs, key=...)` |
| `.limit(n)` | intermediate | `itertools.islice(xs, n)` |
| `.skip(n)` | intermediate | `itertools.islice(xs, n, None)` |
| `.peek(f)` | intermediate | a generator stage that prints and yields |
| `.forEach(f)` | terminal | `for x in xs: f(x)` |
| `.collect(toList())` | terminal | `list(xs)` |
| `.collect(toSet())` | terminal | `set(xs)` |
| `.collect(joining(", "))` | terminal | `", ".join(xs)` |
| `.collect(groupingBy(f))` | terminal | `dict` of lists, or `itertools.groupby` after sorting |
| `.reduce(id, op)` | terminal | `functools.reduce(op, xs, id)` |
| `.count()` | terminal | `sum(1 for _ in xs)` |
| `.anyMatch(p)` | terminal | `any(map(p, xs))` |
| `.allMatch(p)` | terminal | `all(map(p, xs))` |
| `.noneMatch(p)` | terminal | `not any(map(p, xs))` |
| `.findFirst()` | terminal | `next(it, default)` |
| `.min(cmp)` / `.max(cmp)` | terminal | `min(xs, key=...)` / `max(xs, key=...)` |
| `.parallelStream()` | source | `multiprocessing.Pool.map` (see warning) |

The correspondence is close enough that translating a Stream chain to Python
is mechanical, which is what Exercise 39.6 in the
[chapter exercises](exercises.md) asks you to do. The deep similarity is not coincidence: both are the same lazy pull model,
and both were shaped by the same functional-programming tradition.

!!! warning "Common mistakes"

    - **Forgetting that `map`/`filter` are lazy.** `map(f, xs)` on its own
      prints `<map object ...>` and computes nothing. Wrap it in `list(...)`,
      loop over it, or feed it to `sum`/`any`/`join`.
    - **Consuming an iterator twice.** The second pass is always empty. If
      you need two passes, store `list(...)` once.
    - **`reduce` with no initial value.** Fine until the input is empty, then
      a `TypeError` in production. Always pass the third argument.
    - **`zip` on different-length inputs** silently stops at the shortest.
      Check the lengths, or use `zip(a, b, strict=True)` on Python 3.10+ to
      turn the mismatch into an error.
    - **Reaching for `map(lambda ...)`.** If a lambda is involved, a
      comprehension is almost always clearer.
    - **In Java: building a chain with no terminal operation.** It compiles,
      runs instantly, and does nothing at all.

## Check your understanding

??? success "1. What does this print, and in what order?"

    ```python
    def shout(n):
        print("work", n)
        return n * 10

    it = map(shout, [1, 2])
    print("built")
    print(next(it))
    ```

    ```text
    built
    work 1
    10
    ```

    `map` runs nothing when it is created, so `built` comes first. Asking for
    one item runs `shout` on exactly one element — item 2 is never touched,
    because nobody asked for it.

??? success "2. Rewrite `list(map(lambda w: w.strip().lower(), lines))` idiomatically."

    `[w.strip().lower() for w in lines]`. The lambda is a giveaway that a
    comprehension will read better. If you only needed `strip`, the `map`
    form `map(str.strip, lines)` would be the cleaner one — the rule is about
    whether a lambda is required, not about which function name you like.

??? success "3. Why does `functools.reduce(lambda a, b: a + b, [])` fail while `sum([])` returns 0?"

    `sum` has a documented start value of 0, so an empty input has an obvious
    answer. `reduce` with no initial value seeds the accumulator from the
    first item, and an empty sequence has no first item — it raises
    `TypeError: reduce() of empty iterable with no initial value`. Passing
    `0` as the third argument fixes it.

??? success "4. Which Java Stream operations are lazy, and how would you tell?"

    Every operation that returns another `Stream` is lazy: `filter`, `map`,
    `flatMap`, `distinct`, `sorted`, `limit`, `skip`, `peek`. Anything that
    returns a value, a collection, or `void` — `collect`, `forEach`, `count`,
    `reduce`, `findFirst`, `anyMatch` — is terminal and triggers the work. The
    test is the return type: a chain of intermediates with no terminal
    operation prints nothing at all, exactly as in Python.
