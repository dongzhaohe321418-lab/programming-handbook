# Exercises

## The chapter in brief

- An operating system has two jobs: **landlord** (share scarce resources,
  keep tenants apart) and **abstraction factory** (turn awkward hardware
  into files, windows, and processes) ([23.1](01-os-processes.md)).
- A **program** is a file; a **process** is that program in motion, with its
  own memory, its own PID, and the OS's bookkeeping.
- One core runs many processes by **time-slicing**: run, save state,
  **context switch**, repeat — hundreds of times a second, invisibly.
- **Threads** live inside one process and *share its memory*, which makes
  communication trivial and **race conditions** possible.
- User space cannot touch hardware; every real effect goes through a
  **system call**, and every system call is a checkpoint the kernel can
  refuse.
- A process's address space has four regions: code, static data, **heap**
  (grows up, holds objects) and **stack** (grows down, one frame per call)
  ([23.2](02-memory-layout.md)).
- `RecursionError` is a *stack-depth* limit, not an out-of-memory condition.
- Lists **over-allocate** in a staircase of capacity jumps — the physical
  reason `append` is amortized $O(1)$.
- CPython frees objects by **reference counting** the instant a count hits
  zero, plus a **cycle collector** for objects that only reference each
  other.
- A garbage-collected language still leaks by *accidental retention* — an
  unbounded cache is reachable, so it is kept.
- CPython runs a four-stage pipeline: source → AST → **bytecode** → the
  ceval loop, which is a fetch–decode–execute machine written in software
  ([23.3](03-interpreters-vms.md)).
- "Compiled versus interpreted" is a spectrum: ahead-of-time (C), bytecode
  plus JIT (Java, PyPy), bytecode plus interpretation (CPython).
- The Run buttons on this site are **CPython compiled to WebAssembly** — a
  virtual machine inside a virtual machine inside a sandboxed process on a
  time-sliced kernel on silicon.

### Key terms

| Term | What it means |
| --- | --- |
| [process](../concept-index.md#p) | one running instance of a program, with its own memory and PID |
| [thread](../concept-index.md#t) | an execution stream inside a process, sharing that process's memory |
| race condition | a bug whose outcome depends on the exact interleaving of threads |
| [system call](../concept-index.md#s) | a checked request from user space into the kernel |
| [kernel vs user space](../concept-index.md#k) | the privileged core versus the restricted mode your code runs in |
| [address space](../concept-index.md#a) | a process's private map of memory: code, static data, heap, stack |
| [stack (memory region)](../concept-index.md#s) | one frame per active call; small, disciplined, and where `RecursionError` comes from |
| [heap (memory region)](../concept-index.md#h) | where objects created at run time live |
| [garbage collection](../concept-index.md#g) | the runtime reclaiming what the program can no longer reach |
| [reference counting](../concept-index.md#r) | CPython's main mechanism: free an object the moment its count hits zero |
| [bytecode](../concept-index.md#b) | instructions for a pretend machine, not for any physical CPU |
| [virtual machine](../concept-index.md#v) | a machine made of software, with its own instruction set |
| [JIT compiler](../concept-index.md#j) | compiles hot code to real machine code while the program runs |

Now the exercises. They tour the whole chapter: the operating system's jobs,
the memory map of a process, garbage collection, and the pipeline that turns
your source code into something a machine — real or virtual — can execute.
Do the prediction ones on paper *before* pressing ▶ Run.

### Exercise 23.1 — Whose job is it? ●

For each task below, decide who is responsible: the **operating system**,
**your program**, or the **hardware**.

1. Deciding which process gets the CPU core for the next few milliseconds.
2. Adding two numbers held in a variable.
3. Preventing process 4021 from reading process 519's memory.
4. Physically executing the fetch–decode–execute cycle.
5. Turning `open("diary.txt")` into actual disk operations.
6. Deciding that a shopping-cart total should include a shipping fee.

??? success "Solution"

    ```python
    answers = {
        "1. picking the next process to run": "operating system (the scheduler)",
        "2. adding two numbers in a variable": "your program (running on the CPU)",
        "3. isolating one process's memory":   "operating system (address spaces)",
        "4. fetch-decode-execute, physically": "hardware (the CPU itself)",
        "5. open() -> disk operations":        "operating system (system call + file system)",
        "6. business rules like shipping fees":"your program (only you know the rules)",
    }
    for task, who in answers.items():
        print(f"{task:38} -> {who}")
    ```

    The dividing line: the OS manages *shared resources and protection*;
    your program supplies *meaning*; the hardware does the physical work
    both of them describe.

### Exercise 23.2 — Program or process? ●

You double-click your text editor's icon twice and get two windows. How
many *programs* is that, and (typically) how many *processes*? Then predict:
if one code block calls `os.getpid()` twice, are the two numbers the same
or different?

??? success "Solution"

    ```python
    import os

    first = os.getpid()
    second = os.getpid()
    print("first call :", first)
    print("second call:", second)
    print("same process both times?", first == second)
    ```

    One program (one file of instructions on disk), two processes (two
    independent running instances, each with its own memory and PID). The
    two `getpid()` calls print the *same* number: everything in one run of
    one code block happens inside a single process.

### Exercise 23.3 — System call or not? ●●

Which of these operations require at least one system call, and which can
be completed entirely in user space? Explain each in a few words.

1. `total = 2 ** 20`
2. `print("done")`
3. `data = open("results.csv").read()`
4. `scores.append(91)`

??? success "Solution"

    ```python
    verdicts = [
        ("total = 2 ** 20",  "no  - pure computation in the process's own memory"),
        ("print('done')",    "yes - writing to the terminal is I/O (a write call)"),
        ("open(...).read()", "yes - open and read are the kernel's file API"),
        ("scores.append(91)","mostly no - the allocator works in user space and"
                             " only occasionally asks the OS to enlarge the heap"),
    ]
    for op, verdict in verdicts:
        print(f"{op:20} -> {verdict}")
    ```

    The rule of thumb: touching *devices, files, other processes, or new
    memory from the OS* needs the kernel; rearranging your own bytes does
    not.

### Exercise 23.4 — Predict the reference counts ●●

Read this code and predict the two printed lines *before running it*.
Remember: a `weakref` lets you peek at an object without keeping it alive,
and `peek()` returns `None` once the object is gone.

```text
import weakref

class Box:
    pass

a = Box()
b = a                     # a second name for the same object
peek = weakref.ref(a)

del a
print(peek() is None)     # line 1: True or False?
del b
print(peek() is None)     # line 2: True or False?
```

??? success "Solution"

    ```python
    import weakref

    class Box:
        pass

    a = Box()
    b = a
    peek = weakref.ref(a)

    del a
    print(peek() is None)     # False - b still holds a reference
    del b
    print(peek() is None)     # True  - count hit zero, freed instantly
    ```

    It prints `False`, then `True`. `del a` removes one *name*, but the
    object's reference count only drops from 2 to 1 — `b` keeps it alive.
    Only when the count reaches zero does reference counting reclaim it,
    immediately.

### Exercise 23.5 — Predict the next stair ●●

In [Section 23.2](02-memory-layout.md), the list over-allocation probe on
one machine reported size jumps at lengths 1, 5, 9, 17, 25, 33, 41, and 53.
Predict the length at which the *next* jump occurs, then extend the probe
past length 70 to check yourself.

??? success "Solution"

    ```python
    import sys

    lst = []
    previous = sys.getsizeof(lst)
    jumps = []
    for n in range(1, 81):
        lst.append(n)
        size = sys.getsizeof(lst)
        if size != previous:
            jumps.append(len(lst))
            previous = size

    print("jumps happened at lengths:", jumps)
    ```

    The next jump comes at length **65**. The jump at 53 grew the capacity
    to 64 slots, so appends 54–64 are free; append number 65 finds the
    block full and triggers the next over-allocation. (The byte sizes
    differ between 32- and 64-bit builds, but the jump *lengths* — the
    capacity schedule — are the same.)

### Exercise 23.6 — Decode the bytecode ●●

A mystery one-parameter function `f` disassembles to the listing below
(Python 3.12 style). What does `f(x)` compute? Write the function.

```text
  2           LOAD_FAST                0 (x)
              LOAD_FAST                0 (x)
              BINARY_OP                5 (*)
              LOAD_CONST               1 (1)
              BINARY_OP                0 (+)
              RETURN_VALUE
```

??? success "Solution"

    ```python
    import dis

    def f(x):
        return x * x + 1

    print(f(6))        # 37
    dis.dis(f)         # compare with the listing (details may vary a bit)
    ```

    Read it as stack traffic: push `x`, push `x` again, `BINARY_OP *` pops
    both and pushes $x \cdot x$; push the constant 1, `BINARY_OP +` pops
    and adds; `RETURN_VALUE` hands back the result — so
    $f(x) = x^2 + 1$.

### Exercise 23.7 — Escape the stack ●●●

This recursive function computes $1 + 2 + \dots + n$ but crashes with
`RecursionError` for `n = 5000` — each call adds a stack frame and the
ceiling arrives first:

```text
def sum_to(n):
    if n == 0:
        return 0
    return n + sum_to(n - 1)

print(sum_to(5000))     # RecursionError!
```

Rewrite it *iteratively* so `sum_to(5000)` works, and check the answer
against the formula $n(n+1)/2$ from
[Chapter 16](../ch16-complexity/01-big-o.md).

??? success "Solution"

    ```python
    def sum_to(n):
        total = 0
        for k in range(1, n + 1):
            total += k
        return total

    n = 5000
    print("loop version :", sum_to(n))
    print("closed form  :", n * (n + 1) // 2)
    ```

    Both print `12502500`. The loop keeps everything in *one* stack frame,
    reusing two variables, so stack depth never grows — the trade
    discussed in [Chapter 17](../ch17-recursion/03-vs-iteration.md): the
    recursion's bookkeeping moves into your own variables.

### Exercise 23.8 — Plug the leak ●●●

This cache from [Section 23.2](02-memory-layout.md) retains every page
forever. Fix the leak by bounding it to 100 entries: when full, evict the
*oldest* entry before inserting (Python dicts remember insertion order).
After 2,000 distinct requests, the cache should hold exactly 100 entries.

```text
cache = {}

def render_page(request_id):
    html = f"<html>page for request {request_id}</html>"
    cache[request_id] = html
    return html
```

??? success "Solution"

    ```python
    cache = {}
    MAX_ENTRIES = 100

    def render_page(request_id):
        if request_id in cache:            # a real cache checks first!
            return cache[request_id]
        html = f"<html>page for request {request_id}</html>"
        if len(cache) >= MAX_ENTRIES:
            oldest = next(iter(cache))     # first key = oldest insertion
            del cache[oldest]
        cache[request_id] = html
        return html

    for request_id in range(2000):
        render_page(request_id)

    print("entries alive:", len(cache))
    print("oldest surviving request:", next(iter(cache)))
    ```

    It prints `entries alive: 100` (requests 1900–1999 survive). The
    garbage collector was never the problem — every entry was reachable —
    so the fix had to be a *policy* that makes old entries unreachable.
    The standard library packages this pattern as
    `functools.lru_cache(maxsize=...)`.

### Exercise 23.9 — Explain the tower ●●●

Close the book (well, the tab) and answer from memory, then check:

1. When a Python block runs on this site, list the layers between your
   code and the silicon, top to bottom.
2. *Three* of those layers perform a fetch–decode–execute loop. Which
   ones, and over what instructions?
3. Which single layer is the only one allowed to touch the hardware?

??? success "Solution"

    ```python
    tower = [
        ("your Python code",        "what you typed"),
        ("CPython virtual machine", "fetch-decode-executes PYTHON BYTECODE"),
        ("WebAssembly VM",          "fetch-decode-executes WASM (CPython itself)"),
        ("browser process",         "user space; sandboxed; time-sliced"),
        ("OS kernel",               "the only software allowed to touch hardware"),
        ("physical CPU",            "fetch-decode-executes MACHINE CODE in silicon"),
    ]
    for layer, role in tower:
        print(f"{layer:24} | {role}")
    ```

    The three fetch–decode–execute loops: the CPython VM (over Python
    bytecode), the WebAssembly VM (over Wasm instructions — where the
    "program" is CPython itself), and the physical CPU (over machine
    code). Only the kernel commands the hardware — every layer above it
    must ask, via system calls, from inside its scheduled time slices.
