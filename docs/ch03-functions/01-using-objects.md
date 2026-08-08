# 3.1 Using objects and their methods

Before you can *write* great code, you need to get good at *using* code that
other people wrote — the thousands of ready-made tools that come with Python.
Almost all of those tools are delivered in one of two shapes: as **objects**
that carry their own abilities around with them, or as **functions** grouped
into modules. Learning to tell the two apart, to call them correctly, and to
look up what they can do is the single most practical skill in this chapter —
it is how programmers work every day.

## Everything in Python is an object

An **object** is a value that bundles two things together: some **data** (the
value itself) and some **behaviour** (operations that make sense for that kind
of value). The number `42` knows how to be added; the string `"hello"` knows
how to capitalise itself. In Python this is not a special feature of a few
types — *every* value is an object, and every object knows what type it is:

```python
print(type(42))
print(type(3.5))
print(type("hello"))
print(type(True))
print(type(None))
```

Running this prints:

```text
<class 'int'>
<class 'float'>
<class 'str'>
<class 'bool'>
<class 'NoneType'>
```

The word `class` in the output is Python's term for a **type**: the blueprint
that says what data an object holds and what behaviour it offers. `42` is an
object built from the `int` blueprint, `"hello"` from the `str` blueprint. In
[Chapter 12](../ch12-classes/index.md) you will write blueprints of your own;
for now, your job is to *use* the ones Python provides.

## Calling methods with dot notation

Behaviour that lives inside an object is called a **method** — a function that
belongs to that object. You call a method with **dot notation**: write the
object, a dot, the method name, and parentheses (with any extra inputs
inside).

```python
name = "ada lovelace"
print(name.title())        # ask the string to Title-Case itself
print(name.count("a"))     # ask it how many times "a" appears
print(name.replace("ada", "augusta ada"))
```

This prints:

```text
Ada Lovelace
3
augusta ada lovelace
```

Read `name.title()` as a sentence: "`name`, please run your `title` method."
The object on the left of the dot is the one doing the work. Because the
*result* of a method call is itself an object, you can chain calls left to
right:

```python
messy = "   ada LOVELACE   "
print(messy.strip().title())   # first remove spaces, then fix the case
```

```text
Ada Lovelace
```

`messy.strip()` produces a new, trimmed string, and `.title()` is then called
on *that* string. Chaining is convenient, but keep chains short — two or three
links — so each step stays easy to follow.

!!! note "Methods need parentheses — even with nothing inside"

    `name.title` *names* the method; `name.title()` *runs* it. Forgetting the
    parentheses does not cause an error — it just hands you the method object
    itself, which prints as something like `<built-in method title of str
    object ...>` instead of the answer you wanted.

## None — the value that means "no value"

Python has a special object, `None`, whose whole job is to represent the
*absence* of a useful value. You will meet it constantly, often without asking
for it — because any operation that has nothing meaningful to hand back hands
back `None`. The classic example is `print` itself: it displays text on the
screen, but it *returns* nothing useful.

```python
result = print("Hello!")
print(result)
print(type(result))
```

```text
Hello!
None
<class 'NoneType'>
```

The first line prints `Hello!` as expected — but the value stored in `result`
is `None`, of type `NoneType`. This becomes a genuine bug the moment you try
to *use* a `None` as if it were real data. `None` has no string methods, no
arithmetic, nothing:

```python
# raises AttributeError
winner = None            # no winner has been decided yet
print(winner.upper())    # None is not a string — it has no .upper method
```

The error message is worth memorising, because you will see it often:
`AttributeError: 'NoneType' object has no attribute 'upper'`.

Whenever an error message mentions `NoneType`, the real question is never
"what is `NoneType`?" — it is "*which variable unexpectedly became `None`,
and where?*" Track that variable backwards until you find the operation that
produced it.

=== "Python"

    ```python
    winner = None
    print(winner is None)   # the standard way to test for None
    ```

=== "Java"

    ```java
    String winner = null;
    System.out.println(winner == null);  // the standard null test
    // winner.toUpperCase() would throw a NullPointerException
    ```

Java's `null` plays the same role, and calling a method on it raises the
infamous `NullPointerException` — Java's twin of the `NoneType` attribute
error. One difference: in Java only *reference* variables can be `null`,
while in Python any variable can hold `None`, because every value is an
object.

## Two kinds of behaviour: module functions vs methods

Not all ready-made behaviour lives *inside* objects. Some of it is packaged as
plain functions inside a **module** — a library file you `import`. Compare the
two calling styles:

=== "Python"

    ```python
    import math

    print(math.sqrt(16.0))   # module function: the module does the work
    print("hi".upper())      # method: the object itself does the work
    ```

=== "Java"

    ```java
    double r = Math.sqrt(16.0);       // static method — belongs to the class
    String s = "hi".toUpperCase();    // instance method — belongs to the object
    System.out.println(r);
    System.out.println(s);
    ```

The Python block prints:

```text
4.0
HI
```

The two lines look similar — both use a dot — but they mean different things:

| | **Module function** `math.sqrt(16.0)` | **Method** `"hi".upper()` |
| --- | --- | --- |
| What is left of the dot | the module — a library of functions | the object doing the work |
| Where the main input goes | inside the parentheses | it *is* the thing left of the dot |
| Do you need `import`? | yes, for anything outside the built-ins | no — it comes with the object |
| Java's equivalent | a `static` method, e.g. `Math.sqrt` | an instance method, e.g. `toUpperCase` |

Java draws exactly this line with the keyword `static`. A **static method**
like `Math.sqrt` belongs to a class as a whole — you call it on the class
name, and it works only with the inputs you pass it. An **instance method**
like `toUpperCase` belongs to one particular object — you call it on that
object, and it works with that object's own data.

!!! tip "Which one should you expect?"
    If the operation is *about one particular value's own data* ("this
    string, uppercased"), expect a **method**. If it is a general-purpose
    computation ("the square root of whatever you give me"), expect a
    **module function**.

## A worked example: the random module

Let's read a real library the way a working programmer does. The `random`
module generates pseudo-random numbers — "pseudo" because they come from a
deterministic formula that merely *looks* random. Calling `random.seed(n)`
sets the formula's starting point, so the same seed always produces the same
sequence. We seed every example so that your output matches ours exactly.

```python
import random

random.seed(3)                    # same seed -> same "random" sequence

print(random.randint(1, 6))      # an integer from 1 to 6, both ends included
print(random.randint(1, 6))      # the next number in the sequence
print(random.random())           # a float from 0.0 up to (but excluding) 1.0
print(random.choice(["red", "green", "blue"]))   # pick one item
```

```text
2
5
0.5442292252959519
green
```

Four functions, four jobs:

- **`seed(n)`** — fixes the starting point of the sequence.
- **`randint(a, b)`** — a whole number with **both endpoints included**
  (unusual for Python, where most ranges exclude the end).
- **`random()`** — a float in $[0, 1)$: zero is possible, one is not.
- **`choice(sequence)`** — picks one element out of a sequence.

Run the block twice: because of the seed, you get identical output both
times. Delete the `seed` line and each run differs — fine for a game,
terrible for a reproducible experiment or a test.

Notice the shape of what you just did: *import the module, call its functions
by their documented names, respect their documented rules* (like "both ends
included"). That shape is how you will use every library from now on.

## Discovering what an object can do

You do not need to memorise any of this — Python can introspect itself. The
built-in `dir(x)` lists every attribute and method that `x`'s type offers:

```python
print(dir("hi"))
```

The output is a long alphabetical list. It starts with names wrapped in
double underscores, like `__add__` and `__len__` — these are internal hooks
you can ignore for now. After them come the useful ones: `capitalize`,
`casefold`, `center`, … all the way to `upper` and `zfill`. Every one of those
is a method you can call on any string.

Once `dir` has given you a name, `help` tells you what it does:

```python
help(str.strip)
```

This prints the method's documentation — its **docstring** — straight from
the source code: the method's signature and a short description ("Return a
copy of the string with leading and trailing whitespace removed", plus what
the optional argument does).

The `help`/`dir` pair works on everything:

- `dir(math)` lists a whole module's contents;
- `help(random.randint)` explains one function;
- `help(str)` dumps the documentation for the entire string type.

## How to read API documentation

Library documentation — whether from `help()` or from the official docs at
docs.python.org — describes each function by its **signature**. Learn to
dissect one and every library becomes readable. Take the built-in `round`:

```text
round(number, ndigits=None)
^^^^^ ^^^^^^  ^^^^^^^^^^^^
name  required parameter    optional parameter with a default value
```

Three pieces of anatomy, always in the same places:

- **Name** — what you write before the parentheses: `round(...)`.
- **Parameters** — the inputs, in order. `number` has no default, so you must
  supply it. `ndigits=None` has a default, so you may omit it.
- **Return value** — described in the prose below the signature: `round`
  returns the rounded number; it does not print anything.

```python
print(round(3.14159))       # ndigits omitted -> nearest whole number
print(round(3.14159, 2))    # keep 2 decimal places
print(round(3.14159, 4))
```

```text
3
3.14
3.1416
```

When documentation says a parameter is optional, that is a promise about the
*call*, not the behaviour: omitting `ndigits` changes what `round` does (it
returns an `int` instead of a `float`). Always read the sentence after the
signature, not just the signature itself.

!!! warning "Common mistakes"

    - **Calling a method without its object**: writing `upper("hi")` raises
      `NameError`. Methods are reached through the dot: `"hi".upper()`.
    - **Forgetting the parentheses**: `text.strip` without `()` silently does
      nothing useful — it evaluates to the method object itself instead of
      running it.
    - **Using a `None` as if it were data**: storing the result of `print`
      (or any function that returns nothing) and then calling methods on it
      gives `AttributeError: 'NoneType' object has no attribute ...`.
    - **Forgetting to seed randomness** in code that must be reproducible —
      tests and experiments should call `random.seed(...)` first.

## Check your understanding

1. What two things does every object bundle together?

    ??? success "Answer"
        Data (the value itself) and behaviour (the methods — operations that
        make sense for that kind of value). The object's type/class is the
        blueprint that defines both.

2. Without running it, what does this print?

    ```text
    result = print("hi")
    print(result)
    ```

    ??? success "Answer"
        First `hi` (the side effect of the inner `print`), then `None` —
        `print` returns no useful value, so `result` holds `None`.

3. Is `math.sqrt` more like a Java static method or a Java instance method?
   What about `"abc".upper()`?

    ??? success "Answer"
        `math.sqrt` is like a static method: it belongs to the module/class
        as a whole and works only on the inputs you pass in. `"abc".upper()`
        is like an instance method: it belongs to one particular object and
        works on that object's own data.

4. Your program crashes with
   `AttributeError: 'NoneType' object has no attribute 'split'`. In one
   sentence, what is the *actual* problem you should hunt for?

    ??? success "Answer"
        Some variable you expected to hold a string actually holds `None` —
        find the earlier operation that produced `None` instead of a real
        value.
