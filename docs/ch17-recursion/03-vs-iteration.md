# 17.3 Recursion vs iteration

Recursion and loops are not rivals from different universes — they are two
notations for the same underlying idea, *repetition*, and every algorithm
written in one style can be rewritten in the other. That equivalence matters
practically: it means the choice between them is an engineering decision
about clarity, memory, and language limits, not a question of what is
possible. This section shows the same job in both shapes, gives honest
criteria for choosing, and teaches the one conversion trick you will actually
need — replacing the call stack with a stack you manage yourself.

## Same job, two shapes

Here is `factorial` twice. The recursive version restates the mathematical
definition; the iterative version narrates the computation as an
accumulation:

```python
def factorial_recursive(n):
    if n == 0:
        return 1
    return n * factorial_recursive(n - 1)

def factorial_iterative(n):
    result = 1
    for k in range(2, n + 1):
        result *= k
    return result

for n in [0, 1, 5, 10]:
    r, i = factorial_recursive(n), factorial_iterative(n)
    print(f"{n}! = {r}  (iterative agrees: {r == i})")
```

Both are correct, both are $O(n)$, and both fit in five lines. The state that
the loop keeps in *variables* (`result`, `k`), the recursion keeps in
*stack frames* (each frame's `n` and its pending multiplication). That is the
deep symmetry: **a loop's variables are a recursion's frames, flattened.**

## When recursion wins

Recursion earns its keep when the *data itself* is recursively shaped, so
the code that mirrors the shape is dramatically simpler than any loop:

- **Nested / tree-shaped structures.** A folder contains files and more
  folders; a JSON object contains values and more objects; the binary search
  trees of [Chapter 20](../ch20-bst/index.md) are nodes whose children are
  themselves trees. One loop cannot follow all the branching paths — you
  would end up hand-managing a stack anyway (see below).
- **Divide and conquer.** Merge sort and quicksort in
  [Chapter 22](../ch22-sorting/02-merge-quick.md) split the input, solve the
  halves by trusting the smaller call, and combine. Their recursive
  statements are three lines; their iterative forms are famously awkward.
- **Backtracking.** Solving a maze, placing chess queens, filling a sudoku:
  "try an option, recurse, undo if it fails" is recursion at its most
  natural. A taste of this arrives with tree traversals in Chapter 20.

Here is the shape argument in miniature — count every item in a nested list
of lists, arbitrarily deep. The recursive version is barely longer than the
problem statement:

```python
def count_items(item):
    if not isinstance(item, list):   # base case: a single item
        return 1
    return sum(count_items(child) for child in item)  # a list: sum the parts

project = ["readme.md", ["src", ["main.py", "util.py"]], ["docs", ["a.md", "b.md", ["img", "tree.png"]]]]
print(count_items(project))
```

It prints `9` — and it would work unchanged on a structure nested 50 levels
deep. Try writing that with plain `for` loops and no stack: you cannot,
because you never know in advance how deep the nesting goes.

## When iteration wins

- **Simple counting and accumulating.** Summing a flat list or counting to
  $n$ has no recursive structure to exploit; a loop says it plainer and
  faster.
- **Depth is large.** Python caps the call stack (about 1000 frames by
  default, per [section 17.1](01-call-stack.md)). A loop over a
  million items is routine; a recursion a million deep is a crash.
- **Per-call overhead.** Every call pushes a frame — allocation, argument
  passing, return. A loop iteration is much cheaper. Measure it:

```python
import time

def factorial_recursive(n):
    if n == 0:
        return 1
    return n * factorial_recursive(n - 1)

def factorial_iterative(n):
    result = 1
    for k in range(2, n + 1):
        result *= k
    return result

t0 = time.perf_counter()
for _ in range(1000):
    factorial_recursive(300)
recursive_ms = (time.perf_counter() - t0) * 1000

t0 = time.perf_counter()
for _ in range(1000):
    factorial_iterative(300)
iterative_ms = (time.perf_counter() - t0) * 1000

print(f"recursive: {recursive_ms:7.1f} ms for 1000 runs")
print(f"iterative: {iterative_ms:7.1f} ms for 1000 runs")
print(f"ratio: recursion ~{recursive_ms / iterative_ms:.1f}x slower here")
```

Exact numbers vary by machine, but the recursive version is consistently
slower (typically around $2\times$ for this workload) — same $O(n)$ complexity,
bigger constant factor. When the algorithm is identical either way, the loop
is the cheaper spelling.

## Converting recursion to iteration: the explicit stack

The general-purpose conversion replaces the *call* stack with a plain Python
list used as a stack (push with `append`, pop with `pop` — the structure
formalized in [Chapter 19](../ch19-stacks-queues/02-stacks.md)). Instead of
each frame remembering what remains to be done, *you* keep a to-do stack of
pending work. Here is the nested-list traversal from above, both ways:

```python
project = ["readme.md", ["src", ["main.py", "util.py"]], ["docs", ["a.md", "b.md", ["img", "tree.png"]]]]

def collect_recursive(item, out):
    if not isinstance(item, list):
        out.append(item)
        return
    for child in item:
        collect_recursive(child, out)

def collect_with_stack(root):
    out = []
    stack = [root]                     # to-do list of things to process
    while stack:
        item = stack.pop()             # take the most recent piece of work
        if isinstance(item, list):
            for child in reversed(item):   # reversed, so the FIRST child
                stack.append(child)        # is popped next
        else:
            out.append(item)
    return out

names_r = []
collect_recursive(project, names_r)
names_s = collect_with_stack(project)
print(names_r)
print(names_r == names_s)
```

Both produce the same nine names in the same order. Study the two moves of
the conversion: a recursive *call* becomes a *push*, and returning to
continue an enclosing call becomes *popping the next item*. The `reversed`
is the classic fine point — a stack pops last-pushed-first, so children must
be pushed backwards to come out forwards. This stack lives on the heap and
can grow to millions of entries, so the depth limit disappears; the price is
that the elegant shape of the recursion is gone.

## Tail recursion, honestly

A **tail call** is a recursive call that is the *very last thing* a function
does — nothing is left pending after it returns:

```text
def countdown(n):                 # tail-recursive shape
    if n == 0:
        return "done"
    return countdown(n - 1)       # no work after the call
```

Some languages (Scheme, Haskell, and others) detect this shape and quietly
reuse the current frame instead of pushing a new one, so tail recursion runs
exactly like a loop — no stack growth at all. **Python does not do this, and
neither does Java.** The elegant tail form still pushes a frame per call and
still hits the wall:

```python
# raises RecursionError
def countdown(n):
    if n == 0:
        return "done"
    return countdown(n - 1)       # tail position — but Python doesn't care

print(countdown(100_000))
```

`RecursionError`, long before 100 000. (CPython leaves tail calls
unoptimized deliberately: collapsing frames would destroy the clean
tracebacks that make Python errors debuggable.) The honest rule: in Python
and Java, if a recursion can be deep *and* is tail-shaped, it wanted to be a
loop all along — the conversion is mechanical, replace the call with an
update to the variables:

```python
def countdown(n):
    while n != 0:                 # the tail call became a loop step
        n = n - 1
    return "done"

print(countdown(100_000))
```

!!! warning "Common mistakes"
    - **Reaching for recursion on flat data.** Summing a plain list
      recursively costs a frame per element and dies at ~1000 elements;
      `for` (or `sum`) is the right tool. Match the tool to the *shape* of
      the data.
    - **Believing tail recursion is safe in Python.** It is not optimized;
      the tail-shaped `countdown(100_000)` crashes exactly like any other
      deep recursion.
    - **Forgetting `reversed` when pushing children.** In the explicit-stack
      pattern, pushing children in natural order visits them backwards —
      a correct-looking traversal with mysteriously reversed output.
    - **Raising the recursion limit instead of converting.**
      `sys.setrecursionlimit(10**6)` trades a clean `RecursionError` for the
      risk of crashing the whole interpreter when the real stack memory runs
      out. Convert to an explicit stack instead.

## Check your understanding

1. What plays the role of the loop variables `result` and `k` when
   `factorial` is written recursively?

    ??? success "Answer"
        The stack frames: each frame stores its own `n` and its pending
        multiplication. The loop keeps state in variables; the recursion
        keeps the same state spread across frames.

2. You must process a nested comment thread (replies can have replies,
   depth unknown but at most ~20) and, separately, sum a flat list of two
   million numbers. Which style fits each, and why?

    ??? success "Answer"
        The comment thread is tree-shaped with modest depth — recursion
        mirrors the structure and stays far under the depth limit. The flat
        sum is a simple accumulation two million items long — a loop (or
        `sum`): no structure to exploit, and recursion would exceed the
        depth limit anyway.

3. In the explicit-stack conversion, what do a recursive *call* and a
   *return* each become?

    ??? success "Answer"
        A call becomes a push onto the to-do stack; a return becomes simply
        moving on — popping the next pending item off the stack and
        processing it.

4. Why does the tail-recursive `countdown` still raise `RecursionError` in
   Python even though some languages would run it in constant stack space?

    ??? success "Answer"
        Tail-call optimization means *reusing* the current frame for a call
        in tail position. CPython (and Java) never do this — every call
        pushes a new frame regardless of position — partly to keep full
        tracebacks intact. So the frames pile up until the recursion limit.
