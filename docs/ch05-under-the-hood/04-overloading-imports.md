# 5.4 Overloading, chaining, and imports

A good API lets you say more with less: `greet("Ada")` when the default
greeting will do, `greet("Ada", "Welcome")` when it won't. Java and Python
reach that goal by opposite routes — Java writes several methods with one
name, Python writes one function with flexible arguments — and knowing both
routes will save you real confusion when you move between the languages. This
section covers that split, then two everyday skills that grow out of it:
chaining method calls, and importing modules without wrecking your namespace.

## Java overloads methods; Python uses defaults

In Java, several methods may share a name as long as their **parameter
lists** differ — the compiler picks the right one by looking at the arguments
in each call. This is **method overloading**:

=== "Java"

    ```java
    static String greet(String name) {
        return "Hi, " + name + "!";
    }

    static String greet(String name, String greeting) {
        return greeting + ", " + name + "!";
    }

    // greet("Ada")             → "Hi, Ada!"        (first version chosen)
    // greet("Ada", "Welcome")  → "Welcome, Ada!"   (second version chosen)
    ```

=== "Python"

    ```python
    def greet(name, greeting="Hi"):
        return f"{greeting}, {name}!"

    print(greet("Ada"))              # default fills the gap
    print(greet("Ada", "Welcome"))   # caller overrides the default
    ```

Run the Python tab:

```text
Hi, Ada!
Welcome, Ada!
```

One function, same flexible API. The `greeting="Hi"` in the `def` line is a
**default argument**: if the caller omits it, `"Hi"` steps in. Python *needs*
this mechanism because it does not have overloading at all — a name can refer
to only one function at a time, and a second `def` with the same name simply
**replaces** the first:

```python
def area(w):
    return w * w

def area(w, h):          # this REPLACES the first area — no overloading!
    return w * h

print(area(3, 4))        # 12 — only the two-parameter version exists now
# area(3) would now raise TypeError: missing required argument 'h'
```

No error, no warning: the one-parameter `area` is silently gone. Where a Java
class offers `area(int)` *and* `area(int, int)` side by side, the Python
design is one `def` whose defaults and keywords cover all the variants.

## Keyword arguments read like sentences

Defaults get more powerful when combined with **keyword arguments**: at the
call site you may name any parameter explicitly, in any order, and skip the
ones whose defaults you like.

```python
def brew(drink, size="medium", milk=False, shots=1):
    milk_txt = "with milk" if milk else "no milk"
    return f"{size} {drink}, {shots} shot(s), {milk_txt}"

print(brew("latte", milk=True, shots=2))   # skip size, name the rest
print(brew("espresso", size="small"))
print(brew(drink="tea"))                   # even the first one can be named
```

Output:

```text
medium latte, 2 shot(s), with milk
small espresso, 1 shot(s), no milk
medium tea, 1 shot(s), no milk
```

Compare `brew("latte", milk=True, shots=2)` with the hypothetical positional
call `brew("latte", "medium", True, 2)` — the keyword version documents
itself; the positional version demands that every reader memorise the
parameter order. Two grammar rules keep calls unambiguous: positional
arguments must come *before* keyword arguments (`brew(drink="tea", 2)` is a
syntax error), and each parameter may receive at most one value. In Java, an
API this flexible would need four or more overloads — one per combination the
designers anticipated; Python callers can mix and match freely.

## Method chaining: reading a pipeline left to right

You have called methods on objects since
[Chapter 3](../ch03-functions/01-using-objects.md). Because a method call is
an *expression* that produces a value, you can immediately call a method on
the result — no intermediate variable required. Step by step first:

```python
raw = "   hi there   "

step1 = raw.strip()      # a NEW string, whitespace removed
step2 = step1.upper()    # a NEW string, uppercased

print(repr(raw))         # the original is untouched
print(repr(step1))
print(repr(step2))

print(repr("   hi there   ".strip().upper()))   # the same pipeline, chained
```

Output:

```text
'   hi there   '
'hi there'
'HI THERE'
'HI THERE'
```

Read a chain strictly left to right: `"   hi there   ".strip()` evaluates to
`'hi there'`, and *that* string's `.upper()` is then called, giving
`'HI THERE'`. Each link works because string methods **return a new string**
(strings can never be modified in place — they are immutable, as
[Chapter 3](../ch03-functions/02-strings.md) showed). Chaining is wonderful
for short pipelines — clean-up-then-transform is everywhere in real code —
but it has a booby trap: methods that return nothing. A method like
`list.sort()` changes its object *in place* and returns `None`, so chaining
onto it explodes:

```python
# raises AttributeError
numbers = [3, 1, 2]
numbers.sort().reverse()    # sort() returned None; None has no .reverse()
```

Before chaining, know what each link returns. String methods: safe. Methods
that mutate their object: usually `None`, chain over.

## Imports done right

Every program you write leans on code someone else wrote. A **module** is a
file of Python definitions — `math.py` is the module `math` — and a
**package** is a folder of related modules with a name of its own (`numpy` is
a package containing dozens of modules). The `import` statement is how you
bring them in, and there are three respectable forms.

**Form 1 — `import module`.** You get one new name, the module itself, and
reach everything inside it with a **qualified name**, `module.thing`:

```python
import math

print(math.sqrt(16))
print(math.pi)
```

Qualified names are longer, but they are collision-proof — your names and the
module's names live in separate rooms:

```python
import math

def sqrt(x):
    return f"(a very rough guess near {x ** 0.5:.0f})"   # our own sqrt

print(sqrt(16))         # ours:      (a very rough guess near 4)
print(math.sqrt(16))    # the real one: 4.0 — no clash, thanks to math.
```

**Form 2 — `from module import name`.** When you use one or two functions
constantly, import just those names directly:

```python
from math import sqrt, pi

print(sqrt(2))
print(pi)
```

Shorter calls, but note what you traded away: `sqrt` now lives in *your*
namespace, so nothing stops a later `def sqrt(...)` from silently replacing
it. Import names sparingly and deliberately.

**Form 3 — `import module as alias`.** For long module names, the community
settles on standard abbreviations — and you should use the standard ones, not
invent your own:

```python
import numpy as np      # THE standard alias, used in every tutorial on Earth

values = np.array([1.0, 2.0, 3.0])
print(values.mean())
```

## Never `from module import *`

There is a fourth form, and it is a trap: `from module import *` dumps
*every* public name from the module straight into your namespace. Watch it
destroy a variable:

```python
log = "Day 1: our ship set sail at dawn"    # our captain's log

from math import *      # imports dozens of names... one of them is log()

print(log)              # our string is GONE — replaced by math's log function
```

Output:

```text
<built-in function log>
```

No error, no warning — the captain's log is simply overwritten by the natural
logarithm. And it is not just `log`; a `*`-import from `math` silently
injects a small crowd of names (`e`, `pow`, `gamma`, `degrees`, …), any of
which may collide with yours:

```python
import math

public = [name for name in dir(math) if not name.startswith("_")]
print(len(public), "names would be dumped, e.g.:", public[:8])
```

Every name in that list is a landmine `import *` buries in your namespace —
and a reader of your code can no longer tell where any name came from. The
rule is simple and near-universal in professional Python: **never
`from module import *`** (its one traditional excuse is quick experiments at
the interactive prompt). Qualified names or a short, explicit `from`-import
list tell every reader exactly where each name was born.

!!! info "Java corner"
    Java's `import java.util.*;` looks similar but is far tamer: it only lets
    you *write* `Scanner` instead of `java.util.Scanner`, and the compiler
    flags genuine ambiguities as errors instead of silently overwriting.
    Python's `*`-import really does clobber your variables at run time, as the
    captain's log just demonstrated.

!!! warning "Common mistakes"
    - **Defining the same function name twice, expecting overloading.** The
      second `def` replaces the first, silently. Use default and keyword
      arguments instead.
    - **Positional arguments after keyword arguments.** `f(x=1, 2)` is a
      `SyntaxError`; positionals always come first.
    - **Chaining onto a method that returns `None`.**
      `numbers.sort().reverse()` raises `AttributeError` because `sort()`
      mutates in place and returns `None`.
    - **`from module import *`.** It can silently overwrite your variables
      and makes every name's origin a mystery. Import the module, or list the
      few names you need.

## Check your understanding

1. A Java class has three constructors-worth of flexibility:
   `ticket(name)`, `ticket(name, qty)`, `ticket(name, qty, vip)`. What single
   Python `def` line provides the same API?

    ??? success "Answer"
        `def ticket(name, qty=1, vip=False):` — callers write `ticket("Ada")`,
        `ticket("Ada", 3)`, or `ticket("Ada", vip=True)`, and the defaults
        fill whatever is omitted.

2. What does `" Data Science ".strip().lower()` evaluate to, and in what
   order do the calls happen?

    ??? success "Answer"
        `'data science'`. Left to right: `.strip()` runs on
        `' Data Science '` producing `'Data Science'`, then `.lower()` runs
        on that result.

3. Your script defines `max_speed = 88`, then later runs
   `from math import *` — which does not define any `max_speed`. Is your
   variable safe? Is this style safe in general?

    ??? success "Answer"
        `max_speed` survives, since `math` exports no name spelled that way —
        but the style is still unsafe: `*`-imports overwrite any name they
        *do* share (like `log`, `e`, or `pow`), today or after any future
        update of the module, without any warning.

4. Why does `scores.sort().count(3)` fail, while
   `sorted(scores).count(3)` works?

    ??? success "Answer"
        `scores.sort()` sorts the list in place and returns `None`, and
        `None` has no `.count` method — `AttributeError`. The built-in
        `sorted(scores)` returns a *new* sorted list, a real object you can
        keep chaining on.
