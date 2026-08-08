# Chapter 39 · Exercises

## The chapter in brief

- A function in Python is an ordinary **value**: you can store it under a
  second name, pass it as an argument, and return it from another function
  ([39.1](01-lambdas.md)).
- A `lambda` is a function of **one expression** and no name — and if it
  deserves a name, it deserves a `def`.
- Lambdas genuinely pay for themselves in exactly three places:
  `sorted(key=...)`, `min`/`max` with a key, and callbacks.
- A **closure** captures a *variable*, not its value, which is why lambdas
  created in a loop all see the loop's final value — and why
  `param=value` or a factory fixes it.
- `functools.partial` freezes arguments at construction time, so it reads
  better than a lambda and cannot fall into that trap.
- A **pure function** — result from arguments only, nothing mutated — is
  testable in one line, because its answer never depends on what ran before.
- Almost all data work is three verbs: **map** (change each item), **filter**
  (drop some), **reduce** (collapse to one)
  ([39.2](02-map-filter-reduce.md)).
- Comprehensions are the Pythonic spelling of map-and-filter; reach for `map`
  only when the function already exists and takes one argument.
- `map` and `filter` are **lazy** and **single-use**: nothing runs until
  something consumes them, and the second pass is always empty.
- Java's Streams are the same model with types — intermediate operations are
  lazy, exactly one terminal operation pulls the data through, and every
  operation has a Python equivalent.
- A **generator** is how you write your own lazy stage, and a chain of them
  processes any amount of data in constant memory — measured, not asserted
  ([39.3](03-pipelines.md)).
- A Unix pipeline is that same architecture at the process level: streaming,
  backpressure, and blocking stages such as `sort` that no stream can flow
  through.

### Key terms

| Term | One-clause reminder |
|---|---|
| First-class function | a function used as a value — stored, passed, returned |
| Higher-order function | a function that takes a function, returns one, or both |
| `lambda` | an anonymous function whose body is a single expression |
| [Closure](../concept-index.md#c) | a function plus the captured variables it still needs |
| Late binding | a captured variable is read at *call* time, not at capture time |
| Pure function | the result depends only on the arguments, and nothing outside changes |
| Predicate | a function returning true or false, of the kind `filter` takes |
| Fold (`reduce`) | collapse a sequence into one value with a two-argument function |
| Laziness | no work happens until something consumes the result |
| [Generator](../concept-index.md#g) | a function containing `yield`; calling it returns a paused iterator |
| Pipeline stage | a generator that takes an iterable and yields an iterable |
| [Backpressure](../concept-index.md#b) | a slow consumer throttles a fast producer, because the consumer pulls |
| Blocking stage | one that must see all the input before emitting anything, like `sort` |
| Terminal operation | the Java Stream call that finally runs the chain |

Full command reference for the pipe side of this chapter:
[Appendix F](../appendix/F-toolchain-reference.md).

Now put it to work. The functional style is learned by translation: most of
these exercises hand you code in one shape and ask for it in another — a loop
into a comprehension, a Java Stream chain into Python, a nested loop into a
pipeline — because that is exactly the skill you need when you meet this style
in somebody else's codebase. Two of them are bug hunts, one asks you to
predict before running, and the last one builds a piece of machinery that
`itertools` normally hands you.

### Exercise 39.1 — Loops into comprehensions, and back ●

Rewrite each loop as a single comprehension, then rewrite the last
comprehension back into an explicit loop.

```python
# (a)
lengths = []
for word in ["stream", "pipe", "lazy"]:
    lengths.append(len(word))

# (b)
warm = []
for t in [18.2, 24.6, 30.1, 12.0, 27.7]:
    if t > 20:
        warm.append(t)

# (c)
labels = []
for n in [3, 8, 11, 4]:
    if n % 2 == 0:
        labels.append(f"even:{n}")

# (d) -- rewrite THIS one as a loop
squares_by_name = {name: len(name) ** 2 for name in ["ada", "grace"]}
```

??? success "Solution"

    ```python
    words = ["stream", "pipe", "lazy"]
    temps = [18.2, 24.6, 30.1, 12.0, 27.7]
    nums = [3, 8, 11, 4]

    a = [len(word) for word in words]
    b = [t for t in temps if t > 20]
    c = [f"even:{n}" for n in nums if n % 2 == 0]

    print("a:", a)
    print("b:", b)
    print("c:", c)

    # (d) the comprehension, expanded back into a loop
    squares_by_name = {}
    for name in ["ada", "grace"]:
        squares_by_name[name] = len(name) ** 2
    print("d:", squares_by_name)

    # ... and the map/filter spelling of (a) and (b), for comparison
    print("a via map   :", list(map(len, words)))
    print("b via filter:", list(filter(lambda t: t > 20, temps)))
    ```

    ```text
    a: [6, 4, 4]
    b: [24.6, 30.1, 27.7]
    c: ['even:8', 'even:4']
    d: {'ada': 9, 'grace': 25}
    a via map   : [6, 4, 4]
    b via filter: [24.6, 30.1, 27.7]
    ```

    The pattern is mechanical: the `append` expression moves to the front,
    the `for` line stays in the middle, and the `if` goes at the end. Part (a)
    is the one case where `map` genuinely reads better, because `len` already
    exists and needs no lambda.

### Exercise 39.2 — Predict the lazy evaluation order ●

**Write down the exact output before you press Run.** Include the order of
the lines, not just their contents.

```python
def tag(n):
    print(f"  tag({n})")
    return n * 10

def keep(n):
    print(f"    keep({n})?")
    return n > 15

print("A")
stream = filter(keep, map(tag, [1, 2, 3]))
print("B")
first = next(stream)
print("C", first)
rest = list(stream)
print("D", rest)
```

??? success "Solution"

    ```python
    def tag(n):
        print(f"  tag({n})")
        return n * 10

    def keep(n):
        print(f"    keep({n})?")
        return n > 15

    print("A")
    stream = filter(keep, map(tag, [1, 2, 3]))
    print("B")
    first = next(stream)
    print("C", first)
    rest = list(stream)
    print("D", rest)
    ```

    ```text
    A
    B
      tag(1)
        keep(10)?
      tag(2)
        keep(20)?
    C 20
      tag(3)
        keep(30)?
    D [30]
    ```

    Three things to notice. Nothing at all happens between `A` and `B` —
    building the chain runs no code. The single `next()` does **not** stop
    after one element: `tag(1)` produces 10, `keep(10)?` rejects it, so the
    filter goes back for another one, and only `tag(2)` → 20 passes. A lazy
    pipeline does the minimum work needed to produce *one output*, which may
    be several inputs. And element 3 stays untouched until `list()` asks for
    it, which is why `tag(3)` appears after `C`.

    If you predicted the values but not the interleaving, re-read
    [39.2](02-map-filter-reduce.md#laziness-nothing-happens-until-you-ask):
    laziness is about *when*, and the interleaving is the whole point.

### Exercise 39.3 — Sort and select with keys ●

Using `sorted`, `min`, and `max` with `key=` — and no loops — print:

1. the books sorted by year, oldest first;
2. the books sorted by author surname (the last word of `author`), and within
   the same surname by title;
3. the longest title;
4. the total page count;
5. the shortest book published after 1960.

```python
books = [
    {"title": "The Left Hand of Darkness", "author": "Ursula Le Guin",
     "year": 1969, "pages": 304},
    {"title": "A Wizard of Earthsea", "author": "Ursula Le Guin",
     "year": 1968, "pages": 183},
    {"title": "Cybernetics", "author": "Norbert Wiener",
     "year": 1948, "pages": 212},
    {"title": "Structured Programming", "author": "Edsger Dijkstra",
     "year": 1972, "pages": 220},
]
```

??? success "Solution"

    ```python
    books = [
        {"title": "The Left Hand of Darkness", "author": "Ursula Le Guin",
         "year": 1969, "pages": 304},
        {"title": "A Wizard of Earthsea", "author": "Ursula Le Guin",
         "year": 1968, "pages": 183},
        {"title": "Cybernetics", "author": "Norbert Wiener",
         "year": 1948, "pages": 212},
        {"title": "Structured Programming", "author": "Edsger Dijkstra",
         "year": 1972, "pages": 220},
    ]

    print("1.", [b["year"] for b in sorted(books, key=lambda b: b["year"])])

    by_surname = sorted(books, key=lambda b: (b["author"].split()[-1], b["title"]))
    print("2.", [f"{b['author'].split()[-1]}/{b['title'][:12]}" for b in by_surname])

    print("3.", max(books, key=lambda b: len(b["title"]))["title"])
    print("4.", sum(b["pages"] for b in books))

    modern = [b for b in books if b["year"] > 1960]
    print("5.", min(modern, key=lambda b: b["pages"])["title"])
    ```

    ```text
    1. [1948, 1968, 1969, 1972]
    2. ['Dijkstra/Structured P', 'Guin/A Wizard of ', 'Guin/The Left Han', 'Wiener/Cybernetics']
    3. The Left Hand of Darkness
    4. 919
    5. A Wizard of Earthsea
    ```

    The two ideas being drilled
    are the **tuple key** for "sort by this, then by that", and the fact that
    `min`/`max` take the same `key` protocol as `sorted`, so "the smallest
    by *some measure*" never needs a loop. Note that `"Le Guin".split()[-1]`
    gives `"Guin"` — surname extraction is a genuinely hard problem, and this
    exercise's simple rule is wrong for a great many real names.

### Exercise 39.4 — Fix the late-binding closure bug ●●

This code builds three validators and is supposed to print
`[True, True, True]`. It prints something else. Explain why, then fix it two
different ways.

```python
limits = [10, 100, 1000]
validators = []
for limit in limits:
    validators.append(lambda n: n <= limit)

print([v(5) for v in validators])          # expected [True, True, True]
print([v(500) for v in validators])        # expected [False, False, True]
```

??? success "Solution"

    ```python
    limits = [10, 100, 1000]

    # --- the bug -----------------------------------------------------------
    broken = []
    for limit in limits:
        broken.append(lambda n: n <= limit)
    print("broken, n=5  :", [v(5) for v in broken])
    print("broken, n=500:", [v(500) for v in broken])

    # --- fix 1: snapshot the value in a default argument -------------------
    fixed_a = []
    for limit in limits:
        fixed_a.append(lambda n, limit=limit: n <= limit)
    print("fix 1, n=500 :", [v(500) for v in fixed_a])

    # --- fix 2: a factory gives each closure its own cell ------------------
    def make_validator(limit):
        return lambda n: n <= limit

    fixed_b = [make_validator(limit) for limit in limits]
    print("fix 2, n=500 :", [v(500) for v in fixed_b])
    print("cells differ :",
          fixed_b[0].__closure__[0].cell_contents,
          fixed_b[2].__closure__[0].cell_contents)
    ```

    ```text
    broken, n=5  : [True, True, True]
    broken, n=500: [True, True, True]
    fix 1, n=500 : [False, False, True]
    fix 2, n=500 : [False, False, True]
    cells differ : 10 1000
    ```

    The broken version passes the `n=5` test — which is exactly why this bug
    reaches production. All three lambdas share **one** variable `limit`,
    left at 1000 when the loop ended, so all three are really "`n <= 1000`".
    The default-argument fix captures the value at definition time; the
    factory fix gives each lambda its own enclosing call and therefore its own
    cell, which the last line prints to prove.

### Exercise 39.5 — Implement `my_reduce` ●●

Write `my_reduce(func, items, initial)` without using `functools`. Then use
it to build four different aggregations, and check each against the built-in
that normally does the job. Finally, make your version work when `initial` is
omitted — raising a clear error on an empty input, exactly as the real one
does.

??? success "Solution"

    ```python
    _MISSING = object()          # a sentinel: "the caller passed nothing"

    def my_reduce(func, items, initial=_MISSING):
        iterator = iter(items)
        if initial is _MISSING:
            try:
                accumulator = next(iterator)
            except StopIteration:
                raise TypeError(
                    "my_reduce() of empty iterable with no initial value"
                ) from None
        else:
            accumulator = initial
        for item in iterator:
            accumulator = func(accumulator, item)
        return accumulator

    import math
    nums = [3, 1, 4, 1, 5, 9]

    print("sum    ", my_reduce(lambda a, b: a + b, nums, 0), sum(nums))
    print("product", my_reduce(lambda a, b: a * b, nums, 1), math.prod(nums))
    print("max    ", my_reduce(lambda a, b: a if a > b else b, nums), max(nums))
    print("reverse", my_reduce(lambda a, b: [b] + a, nums, []), nums[::-1])

    print("empty with initial:", my_reduce(lambda a, b: a + b, [], 0))
    try:
        my_reduce(lambda a, b: a + b, [])
    except TypeError as e:
        print("empty without initial ->", e)
    ```

    ```text
    sum     23 23
    product 540 540
    max     9 9
    reverse [9, 5, 1, 4, 1, 3] [9, 5, 1, 4, 1, 3]
    empty with initial: 0
    empty without initial -> my_reduce() of empty iterable with no initial value
    ```

    Two details make this a real implementation rather than a toy. Calling
    `iter(items)` first means the function works on a generator, not just a
    list — and it lets the no-initial case consume the first element and then
    continue with the *same* iterator. The `_MISSING` sentinel is the standard
    way to tell "argument omitted" apart from "argument was `None`", since
    `None` is a perfectly good initial value for some folds.

### Exercise 39.6 — Translate a Java Stream chain ●●

Here is a Java method from a code review. Translate it to idiomatic Python
(a comprehension or generator chain, not a literal `map`/`filter`
transcription), and produce the same output for the same input.

```java
public static String topSpenders(List<Order> orders) {
    return orders.stream()
            .filter(o -> o.getStatus().equals("paid"))
            .filter(o -> o.getTotal() >= 50.0)
            .sorted(Comparator.comparingDouble(Order::getTotal).reversed())
            .limit(3)
            .map(o -> o.getCustomer().toUpperCase())
            .distinct()
            .collect(Collectors.joining(", "));
}
```

??? success "Solution"

    ```python
    orders = [
        {"customer": "ada",   "total": 120.0, "status": "paid"},
        {"customer": "linus", "total": 42.5,  "status": "paid"},
        {"customer": "grace", "total": 300.0, "status": "paid"},
        {"customer": "radia", "total": 210.0, "status": "refunded"},
        {"customer": "ada",   "total": 95.0,  "status": "paid"},
        {"customer": "barbara", "total": 51.0, "status": "paid"},
    ]

    def top_spenders(orders):
        paid = (o for o in orders if o["status"] == "paid" and o["total"] >= 50)
        ranked = sorted(paid, key=lambda o: -o["total"])[:3]
        names = (o["customer"].upper() for o in ranked)
        return ", ".join(dict.fromkeys(names))      # dict.fromkeys = distinct

    print(top_spenders(orders))

    # the mapping, operation by operation
    for java, python in [
        (".stream()",            "iterate the list"),
        (".filter(p)",           "a generator with an if"),
        (".sorted(cmp)",         "sorted(key=...)"),
        (".limit(3)",            "[:3] or itertools.islice"),
        (".map(f)",              "a generator expression"),
        (".distinct()",          "dict.fromkeys (keeps order) / set (does not)"),
        (".collect(joining())",  "', '.join(...)"),
    ]:
        print(f"  {java:<22} -> {python}")
    ```

    ```text
    GRACE, ADA
    ```

    …followed by the mapping table. Only **two** names come out, and that is
    correct: the top three paid orders over 50 are Grace's 300, Ada's 120 and
    Ada's 95, so `distinct` collapses the two Ada rows. Barbara's 51 never
    reaches the `distinct` stage because `limit(3)` came first — reading a
    Stream chain in order matters as much as translating it.

    Three translation points worth keeping. The two `filter` calls collapse
    into one `if` with `and`, which is what a Python reviewer would expect.
    `limit(3)` becomes a slice on a list (or `islice` if the source is lazy).
    And `distinct()` maps to `dict.fromkeys(...)` rather than `set(...)`,
    because `set` would scramble the order you just sorted into — a mistake
    that is easy to make and hard to spot in a test that happens to have one
    element.

### Exercise 39.7 — Build a four-stage generator pipeline ●●

Write a pipeline of four generator stages that processes a log file and
yields structured records:

1. `read(path)` — yield lines from the file;
2. `decode(lines)` — strip whitespace, drop blanks and `#` comments;
3. `only(level, lines)` — keep lines whose second field is `level`;
4. `to_record(lines)` — yield `{"time": ..., "level": ..., "message": ...}`.

The block must create the file before reading it. Then use the pipeline to
count `ERROR` records and print the first two.

??? success "Solution"

    ```python
    with open("app.log", "w", encoding="utf-8") as f:
        f.write("""\
    # app log -- generated
    08:01:14 INFO  service started

    08:02:03 ERROR database unreachable
    08:02:04 WARN  retrying in 5s
    08:02:09 ERROR database unreachable
    08:03:00 INFO  recovered
    08:04:41 ERROR disk almost full
    """)

    def read(path):
        with open(path, encoding="utf-8") as f:
            for line in f:
                yield line

    def decode(lines):
        for line in lines:
            line = line.strip()
            if line and not line.startswith("#"):
                yield line

    def only(level, lines):
        for line in lines:
            if line.split()[1] == level:
                yield line

    def to_record(lines):
        for line in lines:
            time, level, message = line.split(maxsplit=2)
            yield {"time": time, "level": level, "message": message}

    pipeline = to_record(only("ERROR", decode(read("app.log"))))
    print("built:", type(pipeline).__name__, "- nothing read yet")

    records = list(pipeline)
    print("ERROR count:", len(records))
    for r in records[:2]:
        print(f"  {r['time']}  {r['message']}")

    # each stage is testable on its own, with no file involved
    print("stage test:", list(decode(["  keep me ", "", "# skip", " x "])))
    ```

    ```text
    built: generator - nothing read yet
    ERROR count: 3
      08:02:03  database unreachable
      08:02:09  database unreachable
    stage test: ['keep me', 'x']
    ```

    The shape to internalise: every stage takes an iterable and yields an
    iterable, so the stages compose in any order and each one is unit-testable
    against a hand-written list — the last line tests `decode` with no file at
    all. Swapping `read` for a network socket or a generator of test data
    changes nothing downstream.

### Exercise 39.8 — Grouped aggregation, without `itertools` ●●●

Write two functions with no imports at all:

- `group_by(records, key_fn)` → a dict mapping each key to the list of
  records with that key, **preserving first-seen key order** and requiring no
  pre-sorting;
- `aggregate(records, key_fn, value_fn, combine, initial)` → a dict mapping
  each key to the fold of its records' values, in one pass.

Then use them to answer three questions about a sales list: total revenue per
region, the number of orders per region, and the largest single order per
region. Verify at least one answer against a hand-computed number.

??? success "Solution"

    ```python
    def group_by(records, key_fn):
        """Bucket records by key. One pass, no sorting, insertion order kept."""
        groups = {}
        for record in records:
            groups.setdefault(key_fn(record), []).append(record)
        return groups

    def aggregate(records, key_fn, value_fn, combine, initial):
        """Fold each group down to one value, in a single pass."""
        totals = {}
        for record in records:
            key = key_fn(record)
            running = totals[key] if key in totals else initial
            totals[key] = combine(running, value_fn(record))
        return totals

    sales = [
        {"region": "east",  "rep": "ada",     "amount": 120.0},
        {"region": "west",  "rep": "linus",   "amount": 75.5},
        {"region": "east",  "rep": "grace",   "amount": 310.0},
        {"region": "north", "rep": "radia",   "amount": 44.0},
        {"region": "east",  "rep": "ada",     "amount": 65.0},
        {"region": "west",  "rep": "barbara", "amount": 210.25},
    ]

    by_region = group_by(sales, lambda s: s["region"])
    print("groups:", {k: len(v) for k, v in by_region.items()})

    revenue = aggregate(sales, lambda s: s["region"], lambda s: s["amount"],
                        lambda a, b: a + b, 0.0)
    orders = aggregate(sales, lambda s: s["region"], lambda s: 1,
                       lambda a, b: a + b, 0)
    biggest = aggregate(sales, lambda s: s["region"], lambda s: s["amount"],
                        lambda a, b: a if a > b else b, 0.0)

    print(f"{'region':<8}{'orders':>8}{'revenue':>12}{'largest':>10}")
    for region in by_region:
        print(f"{region:<8}{orders[region]:>8}"
              f"{revenue[region]:>12.2f}{biggest[region]:>10.2f}")

    hand_checked = 120.0 + 310.0 + 65.0
    print("east revenue checked by hand:", revenue["east"] == hand_checked)
    ```

    ```text
    groups: {'east': 3, 'west': 2, 'north': 1}
    region    orders     revenue   largest
    east           3      495.00    310.00
    west           2      285.75    210.25
    north          1       44.00     44.00
    east revenue checked by hand: True
    ```

    Three ideas are doing the work. `setdefault` turns "create the bucket if
    it does not exist, then append" into one line. `aggregate` is
    `functools.reduce` applied per key — one running accumulator per group,
    seeded from `initial`, which is why counting is just
    `value_fn=lambda s: 1`. And because both functions make a single pass and
    never sort, they cost $O(n)$ and work on a generator that is far too big
    to hold in memory — unlike `itertools.groupby`, which needs its input
    sorted by the same key first.
