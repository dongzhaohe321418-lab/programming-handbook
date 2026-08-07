# 39.3 Generators, pipelines, and Unix pipes

[Section 39.2](02-map-filter-reduce.md) ended with a fact worth building on:
`map` and `filter` are lazy, so items flow through a chain one at a time. A
**generator** is how you write your own lazy stage, and once you can do that
you can build pipelines — chains of small, independently testable steps that
process a hundred million records in the memory footprint of about ten. This
is not an exotic technique. It is what happens every time you type a `|` in a
terminal, and by the end of this section you will have written the same
pipeline twice: once as a shell command, once as Python generators, with
identical output.

## Generators, one step further than Chapter 19

[Section 19.1](../ch19-stacks-queues/01-iterators.md) introduced the
iterator protocol and showed that a function containing `yield` returns an
iterator instead of a value. The recap in one block:

```python
def countdown(n):
    """A generator function: calling it runs NO code, it builds an iterator."""
    print("  (generator body starts running now)")
    while n > 0:
        yield n          # hand a value out, then FREEZE here
        n -= 1
    print("  (generator body finished)")

gen = countdown(3)
print("called countdown(3) — notice nothing has printed yet")
print("first next():", next(gen))
print("second next():", next(gen))
print("the rest:", list(gen))
```

```text
called countdown(3) — notice nothing has printed yet
  (generator body starts running now)
first next(): 3
second next(): 2
  (generator body finished)
the rest: [1]
```

The three behaviours that make generators the right pipeline primitive are
all visible above:

1. **Calling the function runs nothing.** You get a paused iterator.
2. **`yield` suspends the function**, keeping every local variable alive,
   and resumes exactly there on the next `next()`.
3. **The values appear one at a time**, so the generator never needs to hold
   more than one of them.

The compact form is the **generator expression** — a comprehension in round
brackets:

```python
squares_list = [n * n for n in range(6)]      # a list: all six exist at once
squares_gen  = (n * n for n in range(6))      # a generator: none exist yet

print(squares_list)
print(squares_gen)                            # (only the repr; nothing computed)
print(list(squares_gen))
print("second pass:", list(squares_gen))      # exhausted, like every iterator

# When a generator expression is the only argument, drop the extra brackets:
print("sum:", sum(n * n for n in range(6)))
```

```text
[0, 1, 4, 9, 16, 25]
<generator object <genexpr> at 0x000000000000>
[0, 1, 4, 9, 16, 25]
second pass: []
sum: 55
```

(The hexadecimal address in the third line is the object's memory location —
yours will differ, and nothing should ever depend on it.)

## The constant-memory property, measured

Here is the claim that makes all of this worth learning: **a generator chain
uses the same amount of memory whether it processes two hundred items or two
hundred million.** A list-based chain uses memory proportional to the data.
`tracemalloc`, in the standard library, tracks Python's peak allocation, so
we can measure rather than assert.

```python
import sys, tracemalloc

N = 200_000

# --- Approach A: a list at every stage ----------------------------------
tracemalloc.start()
squares = [n * n for n in range(N)]           # 200 000 integers, all alive
evens = [s for s in squares if s % 2 == 0]    # 100 000 more, all alive
total_list = sum(evens)
peak_list = tracemalloc.get_traced_memory()[1]
tracemalloc.stop()
del squares, evens

# --- Approach B: the same chain, lazily ---------------------------------
tracemalloc.start()
squares_g = (n * n for n in range(N))         # nothing computed
evens_g = (s for s in squares_g if s % 2 == 0)
total_gen = sum(evens_g)                      # one item in flight at a time
peak_gen = tracemalloc.get_traced_memory()[1]
tracemalloc.stop()

print("same answer? ", total_list == total_gen, "->", total_gen)
print(f"list chain peak memory      : {peak_list/1024:>10,.1f} KB")
print(f"generator chain peak memory : {peak_gen/1024:>10,.1f} KB")
print(f"ratio                       : {peak_list/peak_gen:>10,.0f}x")
print(f"empty list object           : {sys.getsizeof([]):>10,} bytes")
print(f"list of {N:,} squares  : {sys.getsizeof([n*n for n in range(N)]):>10,} bytes")
print(f"the generator object        : "
      f"{sys.getsizeof((n*n for n in range(N))):>10,} bytes")
```

```text
same answer?  True -> 1333313333400000
list chain peak memory      :    8,617.8 KB
generator chain peak memory :        1.2 KB
ratio                       :      7,026x
empty list object           :         56 bytes
list of 200,000 squares  :  1,624,056 bytes
the generator object        :        200 bytes
```

Your exact byte counts will differ — they depend on the interpreter build and
on how the allocator happens to round — but the shape will not. Roughly
**eight megabytes versus one kilobyte** for the identical arithmetic and the
identical answer — a ratio of several thousand. And note the last two lines: the
list *object* alone is 1.6 MB of pointers, before counting the integers it
points at, while the generator object is a couple of hundred bytes no matter
how many items will eventually pass through it.

[Section 23.2](../ch23-os/02-memory-layout.md) explains where that memory
comes from: the list's 1.6 MB block lives on the **heap**, and every one of
those integers is a separate heap object that the garbage collector must
track. The generator keeps a single frame with a couple of local variables
and one item in flight. Multiply by a real log file — 40 GB of web-server
records is unremarkable — and the difference stops being an optimisation and
becomes the difference between "runs" and "your process is killed".

## Building a composable pipeline

The design pattern is: **each stage is a generator that takes an iterable and
yields an iterable**. Stages know nothing about each other, so you can
reorder them, test them individually, and reuse them. Here is a complete ETL
(extract, transform, load) pipeline over a file — the block creates the file
first so you can run it right here.

```python
# --- create the input file so the pipeline has something to read ---------
raw_text = """\
# sensor export v2 -- lines starting with # are comments
2024-03-01T08:00,lab-a,21.4

2024-03-01T08:15,lab-a,21.9
2024-03-01T08:30,lab-b,19.2
   2024-03-01T08:45,lab-a,22.6

2024-03-01T09:00,lab-b,19.8
2024-03-01T09:15,lab-a,BROKEN
2024-03-01T09:30,lab-b,20.1
"""
with open("sensors.csv", "w", encoding="utf-8") as f:
    f.write(raw_text)

# --- stage 1: read lines from the file, one at a time --------------------
def read_lines(path):
    with open(path, encoding="utf-8") as f:
        for line in f:
            yield line

# --- stage 2: strip whitespace ------------------------------------------
def strip_all(lines):
    for line in lines:
        yield line.strip()

# --- stage 3: drop blanks and comments ----------------------------------
def drop_noise(lines):
    for line in lines:
        if line and not line.startswith("#"):
            yield line

# --- stage 4: parse into records, skipping unparseable rows --------------
def parse(lines):
    for line in lines:
        stamp, room, value = line.split(",")
        try:
            yield {"time": stamp[-5:], "room": room, "temp": float(value)}
        except ValueError:
            print(f"  skipping unparseable reading: {value!r}")

# --- compose the four stages: still nothing has been read ----------------
pipeline = parse(drop_noise(strip_all(read_lines("sensors.csv"))))
print("pipeline built:", type(pipeline).__name__, "- the file is untouched")

# --- one pull runs the whole chain for one record ------------------------
print("first record:", next(pipeline))

# --- consume the rest and aggregate --------------------------------------
by_room = {}
for record in pipeline:
    by_room.setdefault(record["room"], []).append(record["temp"])

for room, temps in sorted(by_room.items()):
    print(f"{room}: n={len(temps)} mean={sum(temps)/len(temps):.2f} max={max(temps)}")
```

```text
pipeline built: generator - the file is untouched
first record: {'time': '08:00', 'room': 'lab-a', 'temp': 21.4}
  skipping unparseable reading: 'BROKEN'
lab-a: n=2 mean=22.25 max=22.6
lab-b: n=3 mean=19.70 max=20.1
```

Look at `lab-a: n=2` and make sure it does not surprise you: the 08:00
reading is missing from the aggregate because `next(pipeline)` already pulled
it out. A stream is consumed exactly once, and whatever you take out early is
not there later.

Fifteen lines of pipeline, and it has all the properties you want from
production code. It never holds more than one line in memory, so the same
code works on a four-gigabyte file. Each stage is four lines and testable on
a hand-written list — `list(drop_noise(["", "# x", "keep"]))` is a complete
unit test. Adding a stage (deduplicate, convert units, redact) means writing
one more four-line generator and slotting it into the chain. And the `with`
block inside `read_lines` still closes the file correctly, because the
generator's frame stays alive until the iteration finishes.

!!! note "Nesting reads inside-out"

    `parse(drop_noise(strip_all(read_lines(path))))` executes
    left-to-right in *data* order but reads right-to-left on the page. When a
    chain gets long, name the intermediate stages:

    ```text
    lines   = read_lines(path)
    cleaned = drop_noise(strip_all(lines))
    records = parse(cleaned)
    ```

    Each name is a lazy stream, not a list, so this costs nothing.

## `itertools` highlights

The `itertools` module is the standard library's box of pipeline stages.
Four of them earn their keep immediately.

```python
from itertools import islice, chain, takewhile, count

# islice — take a window of a lazy stream, like Java's limit()/skip()
naturals = count(1)                       # 1, 2, 3, ... forever
print("first 5      :", list(islice(naturals, 5)))
print("next 3       :", list(islice(naturals, 3)))     # count kept its place

# chain — glue streams together end to end, without copying
print("chain        :", list(chain([1, 2], (3, 4), "ab")))
print("chain.from_it:", list(chain.from_iterable([[1, 2], [3], [4, 5]])))

# takewhile — stop at the first item that fails the test
readings = [3, 5, 8, 13, 2, 21]
print("takewhile <10:", list(takewhile(lambda n: n < 10, readings)))
print("filter    <10:", list(filter(lambda n: n < 10, readings)))
```

```text
first 5      : [1, 2, 3, 4, 5]
next 3       : [6, 7, 8]
chain        : [1, 2, 3, 4, 'a', 'b']
chain.from_it: [1, 2, 3, 4, 5]
takewhile <10: [3, 5, 8]
filter    <10: [3, 5, 8, 2]
```

`islice` on an infinite `count` is the pattern to remember: an unbounded
stream is perfectly safe as long as something downstream stops pulling.
Compare the last two lines closely — `takewhile` **stops** at 13 and never
looks at the rest, while `filter` examines every item and keeps the 2 near
the end. On an infinite stream, `takewhile` terminates and `filter` does not.

### `groupby`, and the gotcha that bites everyone

`itertools.groupby` groups *consecutive* items that share a key. It does not
sort. Feeding it unsorted data produces fragments, silently:

```python
from itertools import groupby

sales = [("east", 10), ("west", 7), ("east", 4), ("north", 9), ("east", 2)]

print("WITHOUT sorting first:")
for region, group in groupby(sales, key=lambda r: r[0]):
    items = list(group)
    print(f"  {region:<6} {len(items)} row(s) {items}")

print("WITH sorting first (same key function!):")
ordered = sorted(sales, key=lambda r: r[0])
for region, group in groupby(ordered, key=lambda r: r[0]):
    items = list(group)
    print(f"  {region:<6} {len(items)} row(s) total={sum(v for _, v in items)}")
```

```text
WITHOUT sorting first:
  east   1 row(s) [('east', 10)]
  west   1 row(s) [('west', 7)]
  east   1 row(s) [('east', 4)]
  north  1 row(s) [('north', 9)]
  east   1 row(s) [('east', 2)]
WITH sorting first (same key function!):
  east   3 row(s) total=16
  north  1 row(s) total=9
  west   1 row(s) total=7
```

Three separate `east` groups in the first run, and no error to warn you. The
rule is absolute: **sort by the same key you group by, or use a dict
instead.** Note the second consequence, though — sorting is a stage that must
see *all* the data, so a `groupby` pipeline is no longer constant-memory. If
you want grouping without sorting, accumulate into a dict:

```python
sales = [("east", 10), ("west", 7), ("east", 4), ("north", 9), ("east", 2)]

totals = {}
for region, amount in sales:
    totals[region] = totals.get(region, 0) + amount
print(totals)

from collections import defaultdict, Counter
grouped = defaultdict(list)
for region, amount in sales:
    grouped[region].append(amount)
print(dict(grouped))
print(Counter(region for region, _ in sales))
```

```text
{'east': 16, 'west': 7, 'north': 9}
{'east': [10, 4, 2], 'west': [7], 'north': [9]}
Counter({'east': 3, 'west': 1, 'north': 1})
```

That version makes one pass, holds one entry per distinct key, and needs no
sort — which is why it, and not `groupby`, is the normal Python answer to
Java's `Collectors.groupingBy`.

## The same idea at the operating-system level

Now the punchline. Everything above — lazy stages, one item in flight,
constant memory — is what a Unix shell has been doing since 1973. Here is a
pipeline that finds the IP addresses responsible for the most errors in a web
server log:

```console
$ cat access.log | grep ERROR | cut -d' ' -f1 | sort | uniq -c | sort -rn | head -3
      4 198.51.100.22
      2 203.0.113.7
      1 192.0.2.66
```

Read it stage by stage. Each `|` is a **pipe**: the operating system hands
the left program's standard output straight to the right program's standard
input, as a stream of bytes.

| Stage | What it does | Pipeline role |
|---|---|---|
| `cat access.log` | emit the file, line by line | **source** |
| `grep ERROR` | keep lines containing `ERROR` | filter |
| `cut -d' ' -f1` | split on spaces, keep field 1 (the IP) | map |
| `sort` | order the addresses so equal ones are adjacent | *blocking* |
| `uniq -c` | collapse adjacent duplicates, prefix the count | reduce-by-key |
| `sort -rn` | re-sort numerically, largest first | *blocking* |
| `head -3` | take the first three lines, then stop | limit |

Three things about this deserve to be stated explicitly.

**It streams.** [Section 23.1](../ch23-os/01-os-processes.md) described a
process as a program in motion with its own memory. A pipeline starts *all
seven* processes at once, and they run concurrently: `grep` is filtering line
17 while `cat` is still reading line 400. No temporary file is created, and
no stage waits for the previous one to finish — except the two marked
*blocking*.

**It applies backpressure.** A pipe is a small fixed-size buffer in the
kernel (64 KB is typical on Linux). When `head` has its three lines and stops
reading, the buffer feeding it fills, so `sort -rn` blocks when it writes,
and the stall propagates back down the chain until `cat` itself is paused.
That is exactly `next()` refusing to be called again — a fast producer cannot
overwhelm a slow consumer, because the consumer sets the pace. Piping a huge
file into `head -3` finishes instantly for this reason.

**Sorting is where streaming stops.** `sort` cannot emit its first line until
it has read its last, so it must hold the whole input (real `sort`
implementations spill to temporary files when that input is larger than
memory). Every pipeline has this property: a stage that needs to see
everything is a wall the stream cannot flow through. Put such stages as late
as possible, after the filters have shrunk the data.

!!! tip "`cat file |` is a small waste"

    Experienced shell users write `grep ERROR access.log | ...` and skip
    `cat` entirely — `grep` can open the file itself, so the extra process
    and the extra copy through a pipe buy nothing. It is written out here
    because the seven-stage version shows the structure better. Chapter 40
    covers the shell properly.

## The same pipeline, in Python

Now build it out of generators and confirm the output matches, line for
line. Each shell stage becomes one small function.

```python
ACCESS_LOG = """\
203.0.113.7 - - [05/Feb/2024:10:12:44] "GET /index.html" 200 ok
198.51.100.22 - - [05/Feb/2024:10:12:45] "GET /admin" 500 ERROR upstream timeout
203.0.113.7 - - [05/Feb/2024:10:12:46] "GET /style.css" 500 ERROR disk full
198.51.100.22 - - [05/Feb/2024:10:12:51] "POST /login" 500 ERROR upstream timeout
192.0.2.66 - - [05/Feb/2024:10:13:02] "GET /cart" 503 ERROR pool exhausted
198.51.100.22 - - [05/Feb/2024:10:13:09] "GET /admin" 500 ERROR upstream timeout
203.0.113.7 - - [05/Feb/2024:10:13:11] "GET /about" 200 ok
198.51.100.22 - - [05/Feb/2024:10:13:30] "GET /admin" 500 ERROR upstream timeout
192.0.2.66 - - [05/Feb/2024:10:13:44] "GET /cart" 200 ok
203.0.113.7 - - [05/Feb/2024:10:14:01] "GET /report" 500 ERROR slow query
"""

def cat(text):                       # cat access.log
    for line in text.splitlines():
        yield line

def grep(pattern, lines):            # grep ERROR
    for line in lines:
        if pattern in line:
            yield line

def cut(lines, delim=" ", field=0):  # cut -d' ' -f1
    for line in lines:
        yield line.split(delim)[field]

def sort_stage(items):               # sort   (blocking: consumes everything)
    yield from sorted(items)

def uniq_c(items):                   # uniq -c  (adjacent duplicates only)
    previous, n = None, 0
    for item in items:
        if item == previous:
            n += 1
        else:
            if previous is not None:
                yield (n, previous)
            previous, n = item, 1
    if previous is not None:
        yield (n, previous)

def sort_rn(pairs):                  # sort -rn  (numeric, descending)
    yield from sorted(pairs, key=lambda pair: -pair[0])

def head(n, items):                  # head -3
    for i, item in enumerate(items):
        if i >= n:
            return
        yield item

pipeline = head(3, sort_rn(uniq_c(sort_stage(cut(grep("ERROR", cat(ACCESS_LOG)))))))

for n, ip in pipeline:
    print(f"{n:>7} {ip}")
```

```text
      4 198.51.100.22
      2 203.0.113.7
      1 192.0.2.66
```

Identical to the shell output, produced by seven generators instead of seven
processes. (The exact spacing of real `uniq -c` varies between GNU and BSD
implementations; the `f"{n:>7}"` here matches the GNU one.)

That equivalence is the point of the whole chapter. A Unix pipeline and a
Python generator chain are the same architecture at two scales: independent
stages, connected by a stream, each pulling one item at a time, with the
consumer setting the pace. Java's Streams are a third instance of it. Learn
the shape once and you can read all three.

!!! info "Java corner"

    The Java equivalent of a generator stage is a lazy `Stream`, and the
    equivalent of `yield` is
    `Stream.iterate(...)`, `Stream.generate(...)`, or — for the file case —
    `Files.lines(path)`, which streams a file line by line exactly like
    `read_lines` above. Java has no `yield` keyword for building your own
    lazy sequence; you either compose existing stream operations or implement
    `Iterator` by hand, which is a good deal more ceremony than four lines
    with a `yield` in the middle.

## When *not* to stream

Streaming is not free, and three situations argue against it.

- **You need random access.** A stream has no index. `records[500]`,
  "the last element", and binary search all require a materialised sequence.
  If you find yourself writing `list(stream)[i]`, you wanted a list.
- **You need more than one pass.** An iterator is exhausted after one
  traversal, so "the mean, and then everything above the mean" is two passes
  over the same data. Either store the data or make one pass compute both
  (running sum plus running count is a classic).
- **You must see everything before emitting anything.** Sorting, grouping
  without a pre-sort, "the top 10 by score", the median, and any
  whole-dataset statistic are all blocking. You can still put them at the end
  of a streaming pipeline — filter first so that the blocking stage sees less
  data — but the stage itself will hold what it holds.

And the honest fourth reason: for a thousand rows, a list comprehension is
simpler to read and debug, and simple beats clever. Reach for generators when
the data is big, unbounded, slow to arrive (a network feed, a growing log),
or when the pipeline structure genuinely makes the code clearer.

!!! warning "Common mistakes"

    - **Reusing an exhausted generator.** The second `for` loop over the same
      generator silently does nothing. Materialise with `list(...)` if you
      need two passes.
    - **`len(gen)` or `gen[0]`.** Generators support neither; they have no
      length until they end and no index at all. Use
      `sum(1 for _ in gen)` (which consumes it) or convert to a list.
    - **`groupby` without sorting first.** Produces fragmented groups and no
      error message. Sort by the same key, or use a `dict`/`Counter`.
    - **Printing inside a stage to debug and being confused by the order.**
      Lazy stages interleave; the output order reflects one item passing
      through every stage, not one stage finishing.
    - **Believing a pipeline made things faster.** Generators save *memory*,
      not time — they do the same work, just spread out. Sometimes they are
      slightly slower per item; the win is that the program does not run out
      of RAM, and that `head -3` can stop early.

## Check your understanding

??? success "1. What does this print, and why is it not `[2, 4, 6]`?"

    ```python
    gen = (n * 2 for n in [1, 2, 3])
    print(sum(gen))
    print(list(gen))
    ```

    It prints `12` and then `[]`. `sum` consumed the generator to the end, so
    the `list` call finds nothing left. An iterator is single-use — this is
    the number-one generator bug, and it never raises an error, it just
    quietly returns empty results.

??? success "2. Why can `grep ERROR huge.log | head -3` finish instantly on a 40 GB file?"

    Because the pipeline streams and applies backpressure. `head` reads three
    lines and exits; the pipe feeding it fills, `grep` blocks on its next
    write and receives a signal telling it the reader is gone, and the whole
    chain stops. Nothing ever read the remaining 40 GB. The same is true of
    `next(pipeline)` on a Python generator chain: one pull does one item's
    worth of work.

??? success "3. Where does this pipeline stop being constant-memory?"

    ```text
    read_lines -> parse -> filter -> sorted -> head(10)
    ```

    At `sorted`. Every stage before it handles one record at a time, but
    `sorted` must read the entire input before it can emit its first result,
    so it holds every surviving record in memory at once. That is why the
    `filter` belongs *before* the sort — it is the difference between sorting
    all the records and sorting the few that matter.

??? success "4. Rewrite this loop as a generator pipeline."

    ```python
    lines = ["10", "", "22", "x", "31"]
    out = []
    for line in lines:
        line = line.strip()
        if line.isdigit():
            out.append(int(line) * 2)
    print(out)
    ```

    ```python
    lines = ["10", "", "22", "x", "31"]

    stripped = (line.strip() for line in lines)
    numeric = (line for line in stripped if line.isdigit())
    doubled = (int(line) * 2 for line in numeric)
    print(list(doubled))
    ```

    Both print `[20, 44, 62]`. The generator version reads as three named
    stages, holds one line at a time, and would work unchanged if `lines`
    were a 40 GB file object instead of a list — which is exactly the
    substitution that makes this style worth learning.
