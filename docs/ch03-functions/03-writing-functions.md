# 3.3 Writing your own functions

In Section 3.1 you *called* other people's functions; now you get to build
your own. A **function** gives a name to a computation, so you can write the
logic once, test it once, and reuse it forever. Every sizeable program is
stitched together from functions — they are the smallest unit of design, and
the habits you form here (clear names, clean inputs and outputs, honest
documentation) are what make large software possible.

## Why functions?

Three reasons, all mattering from day one:

- **Naming.** `celsius_to_fahrenheit(20)` tells the reader *what* is
  computed; the bare formula `20 * 9 / 5 + 32` only says *how*.
- **Reuse.** Write the logic once, call it in ten places, and fix any bug in
  a single spot.
- **Testing.** A function is a sealed box with inputs and an output, so you
  can feed it known inputs and check the answers mechanically — Chapter 8
  builds a whole workflow
  ([unit testing](../ch08-grids/04-unit-testing.md)) on exactly this.

## Defining a function with `def`

A function definition starts with the keyword `def`, then the function's
name, a parenthesised list of inputs, and a colon. The indented lines below —
the **body** — are the code that runs *each time the function is called*.
Definitions don't run anything by themselves; the body waits until a call.

```python
def cheer(name):
    print("Go, " + name + "!")

cheer("Ada")      # each call runs the body with a different name
cheer("Grace")
```

```text
Go, Ada!
Go, Grace!
```

Python read the definition first (learning what `cheer` means), then executed
the two calls. Definition before call — always. Here is the same idea in
Java, whose method headers carry more machinery:

=== "Python"

    ```python
    def add(a, b):
        return a + b

    print(add(3, 4))
    ```

=== "Java"

    ```java
    public static int add(int a, int b) {
        return a + b;
    }
    ```

The anatomy of that Java header, piece by piece:

```text
public static int add(int a, int b)
^^^^^^ ^^^^^^ ^^^ ^^^ ^^^^^^^^^^^^
|      |      |   |   parameter list — every parameter has a declared type
|      |      |   +-- the method's name
|      |      +------ return type: int here; "void" means returns nothing
|      +------------- static: belongs to the class, not one object (see 3.1)
+-------------------- visibility: public = callable from anywhere
```

Python's `def add(a, b):` declares none of that — no types, no visibility, no
`static` — though the *ideas* survive (a Python function that returns nothing
returns `None`, playing the role of `void`). Python's optional **type
hints**, `def add(a: int, b: int) -> int:`, document intent but are not
enforced at run time.

## Parameters vs arguments

Two words that beginners swap constantly, so let's pin them down. A
**parameter** is the *name* in the definition — a placeholder. An
**argument** is the *value* you supply in a call. Parameters are the slots;
arguments fill them, matched left to right:

```python
def rectangle_area(width, height):    # width, height: parameters
    return width * height

print(rectangle_area(3, 4))           # 3, 4: arguments
print(rectangle_area(6.5, 2.0))       # new call, new values in the slots
```

```text
12
13.0
```

Each call creates *fresh* variables `width` and `height`, fills them with
that call's arguments, runs the body, and throws the variables away — calls
are independent, and nothing lingers from one to the next.

## `return` vs `print` — the classic confusion

This is the most common conceptual bug in early programming. They feel
similar in small test programs, because both make a number "appear" — but
only one of them produces a value your program can use:

| | `return value` | `print(value)` |
| --- | --- | --- |
| What it does | hands the value back to the caller | displays text on the screen |
| What the call evaluates to | that value | `None` |
| Can you compute with the result? | yes | no — `None` breaks arithmetic |
| Who sees it | the rest of your program | the person watching |

```python
def add_return(a, b):
    return a + b      # hand the result back to the caller

def add_print(a, b):
    print(a + b)      # show the result on screen; hand back nothing

x = add_return(3, 4)  # nothing appears on screen — the value went into x
y = add_print(3, 4)   # 7 appears on screen — but what went into y?

print("x holds:", x)
print("y holds:", y)
```

```text
7
x holds: 7
y holds: None
```

Trace it: the lone `7` came from *inside* `add_print`; since `add_print` has
no `return`, the value handed to `y` is `None` (Section 3.1's "nothing"
object). The moment you *compute* with a printed-but-not-returned result,
the bug surfaces:

```python
# raises TypeError
def add_print(a, b):
    print(a + b)

total = add_print(3, 4) * 10    # None * 10 — printed text is not a value
```

The rule of thumb: **functions should `return` their results**; let the
*caller* decide whether to print, store, or keep computing. Reserve `print`
inside functions for functions whose entire job is displaying things.

## Multiple returns

`return` has a second property: it ends the function *immediately* — any
lines after it never run. A function may therefore contain several `return`
statements, and whichever one runs first wins. This gives a clean "answer the
easy cases first" style:

```python
def bus_fare(age):
    if age < 6:            # a tiny preview of Chapter 4 — read it as English
        return 0.00        # small children ride free
    if age < 18:
        return 1.25        # youth fare
    return 2.50            # everyone else

print(bus_fare(4))
print(bus_fare(12))
print(bus_fare(30))
```

```text
0.0
1.25
2.5
```

(We are borrowing `if` a chapter early — read `if age < 6:` as the English it
resembles; [Chapter 4](../ch04-branching/index.md) covers branching
properly.)

A related trick: one `return` can hand back *several* values, separated by
commas, and the caller can unpack them into several variables:

```python
def divide_with_remainder(dividend, divisor):
    return dividend // divisor, dividend % divisor

quotient, remainder = divide_with_remainder(17, 5)
print(quotient, remainder)
```

```text
3 2
```

## Default parameter values

A parameter can carry a **default value**, written `name=value` in the
definition. Callers who are happy with the default simply omit that argument;
callers who are not can override it — positionally, or by naming the
parameter (a **keyword argument**), which reads especially well:

```python
def greet(name, greeting="Hello"):
    return greeting + ", " + name + "!"

print(greet("Ada"))                      # use the default
print(greet("Ada", "Good morning"))      # override positionally
print(greet("Grace", greeting="Ahoy"))   # override by keyword
```

```text
Hello, Ada!
Good morning, Ada!
Ahoy, Grace!
```

One syntax rule: parameters with defaults must come *after* parameters
without them — `def greet(greeting="Hello", name)` is a `SyntaxError`,
because Python could not tell which argument fills which slot.

## Scope: where variables live

Every variable has a **scope** — the region of the program where its name
means something.

### Locals are born and die with the call

A variable assigned inside a function is **local**: it is created when the
call starts and destroyed when the call ends. Inside the body it works like
any other variable; from *outside*, it simply does not exist:

```python
# raises NameError
def bake():
    temperature = 220              # local — born and destroyed with the call
    print("Baking at", temperature)   # works fine in here

bake()
print(temperature)    # the local vanished the moment bake() returned
```

The call succeeds and prints `Baking at 220`; the final line then fails with
`NameError: name 'temperature' is not defined` — the local evaporated when
`bake()` returned.

### Globals can be read from anywhere

A variable assigned at the top level of the file is **global**: readable from
everywhere, including inside functions:

```python
flavour = "vanilla"          # global — defined at the top level

def describe():
    print("The cake is", flavour)    # reading a global: fine

describe()
```

```text
The cake is vanilla
```

### Assigning to a global: the `UnboundLocalError` trap

Reading a global works; **assigning** to one inside a function does not do
what you might hope. The moment a function assigns to a name anywhere in its
body, Python treats that name as local *for the entire function* — so this
familiar-looking code fails in a surprising way:

```python
# raises UnboundLocalError
count = 0

def bump():
    count = count + 1    # assignment makes count local — for the whole body,
    print(count)         # so the right-hand count is an unassigned local!

bump()
```

`UnboundLocalError` is a special kind of `NameError`: "you used a local
variable before giving it a value."

Python does have an escape hatch (a `global` declaration), but the far better
design — the one professionals reach for — is to avoid the situation
entirely: **pass values in as arguments, hand results back with `return`**.
Here that means `def bumped(n): return n + 1` and then
`count = bumped(count)`. No globals touched, no surprises.

## Docstrings: the function's contract

A **docstring** is a string placed as the very first line of a function body,
written in triple quotes. It states the function's *contract*: what inputs it
expects and what it promises to return. Python attaches it to the function,
and `help()` displays it — your documentation becomes part of the tooling
from Section 3.1:

```python
def celsius_to_fahrenheit(c):
    """Convert a temperature from degrees Celsius to Fahrenheit."""
    return c * 9 / 5 + 32

print(celsius_to_fahrenheit(100.0))
help(celsius_to_fahrenheit)
```

The first line prints `212.0`; then `help` prints the signature followed by
your docstring — exactly what future readers (including future you) will
see. Write docstrings as a command ("Convert…", "Return…"), keep the first
line to one sentence, and describe the *contract*, not the code.

## Worked example: from written spec to function

Real tasks arrive as prose, not code. Here is a genuine specification — the
Gregorian calendar's leap-year rule:

> A year is a leap year if it is divisible by 4 — except that years divisible
> by 100 are not leap years, unless they are also divisible by 400.

The design procedure is the same every time:

1. **Name the function and its input** — `is_leap_year(year)`.
2. **Decide the output** — here, `True` or `False`.
3. **Translate each clause** into a divisibility test with `%` from
   [Section 2.3](../ch02-data/03-operators.md).
4. **Combine the clauses**, mirroring the spec's "except… unless…"
   structure.
5. **Check against cases where you already know the answer.**

```python
def is_leap_year(year):
    """Return True if year is a leap year in the Gregorian calendar.

    Rule: divisible by 4, except years divisible by 100,
    unless also divisible by 400.
    """
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

print(is_leap_year(2024))   # divisible by 4, not a century  -> True
print(is_leap_year(1900))   # century, not divisible by 400  -> False
print(is_leap_year(2000))   # divisible by 400               -> True
print(is_leap_year(2023))   # not divisible by 4             -> False
```

```text
True
False
True
False
```

The `and`/`or` operators combine true/false conditions just as the English
words suggest; they get their formal treatment in
[Section 4.1](../ch04-branching/01-booleans-logic.md). Notice how the final
line of code echoes the sentence structure of the spec — that is the mark of
a good translation.

And those four test calls are not decoration: 1900 and 2000 are exactly the
cases that catch wrong implementations, so checking them now is a first taste
of testing.

!!! tip "Functions are values too"
    This page treats a function as something you *call*. It is also something
    you can *hand around*: `rule = is_leap_year` names the function without
    calling it, and a function can accept another function as an argument or
    build and return a brand-new one.
    [Section 39.1](../ch39-streams/01-lambdas.md) develops that one idea into
    lambdas, closures, and higher-order functions — the machinery behind
    `sorted(words, key=len)` and, in Java, behind the Streams API.

!!! warning "Common mistakes"

    - **Printing instead of returning** — the function "works" when you watch
      it, but every value it produces is `None`. If `f(x) * 2` crashes with a
      `NoneType` error, look for a missing `return`.
    - **Defining but never calling** — a `def` block alone produces no
      output. If "nothing happened", check that you actually called the
      function.
    - **Using a local variable outside its function** — locals evaporate when
      the call ends; expecting them to survive causes `NameError`.
    - **Assigning to a global inside a function** — one assignment makes the
      name local for the whole body, triggering `UnboundLocalError` on
      patterns like `count = count + 1`. Pass arguments and return results
      instead.

## Check your understanding

1. In `def scale(value, factor):` followed by the call `scale(10, 2.5)`,
   which words are the parameters and which are the arguments?

    ??? success "Answer"
        `value` and `factor` are parameters (the named slots in the
        definition); `10` and `2.5` are arguments (the values supplied by the
        call, matched left to right).

2. Without running it, what does this program print?

    ```text
    def triple(n):
        print(n * 3)

    result = triple(5)
    print(result)
    ```

    ??? success "Answer"
        `15`, then `None`. The call prints 15 as a side effect, but `triple`
        has no `return`, so `result` receives `None`.

3. A teammate writes `def area(shape="circle", radius):` and gets a
   `SyntaxError`. Why?

    ??? success "Answer"
        Parameters with default values must come after parameters without
        them. Swap the order: `def area(radius, shape="circle"):`.

4. `total = 100` is set at the top level, yet a function whose body is
   `total = total - 5` crashes when called. Which error is raised, and why?

    ??? success "Answer"
        `UnboundLocalError`. Because the function *assigns* to `total`,
        Python makes `total` local for the entire body — so `total - 5`
        reads a local that has no value yet. Pass the value in and return
        the new one instead: `def spend(total): return total - 5`.
