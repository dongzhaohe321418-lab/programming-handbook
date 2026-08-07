# 4.3 Equality vs identity

"Are these two things the same?" is actually two different questions. *Do
they have the same value?* — two ten-euro notes have equal value. *Are they
literally the same object?* — those two notes are still two separate pieces
of paper. Python gives each question its own operator: `==` asks about
**equality** (same value), while `is` asks about **identity** (the very same
object in memory). Confusing them produces code that seems to work — until
one day it silently doesn't. Java programmers: this is your `==` vs
`.equals()` distinction wearing a different outfit, and we will map the two
below.

## Two questions, two operators

Lists make the difference easy to see, because you can build two separate
lists with identical contents:

```python
a = [1, 2, 3]
b = [1, 2, 3]     # a second list, built separately, with equal contents
c = a             # NOT a new list — just a second name for a's list

print(a == b)     # True  — same value
print(a is b)     # False — two different objects
print(a == c)     # True  — same value (of course)
print(a is c)     # True  — one object, two names
```

`==` walks through both lists comparing contents; `is` just asks "same
object?". `a` and `b` are equal twins; `a` and `c` are one thing with two
name tags.

## id(): every object's identity tag

Python can show you the identity it uses behind the scenes: `id(x)` returns
a number that uniquely identifies the object `x` for as long as it exists
(in CPython it is the object's memory address). `x is y` is essentially
`id(x) == id(y)`.

```python
a = [1, 2, 3]
b = [1, 2, 3]
c = a

print(id(a) == id(b))   # False — two objects, two ids
print(id(a) == id(c))   # True  — one object, one id
print(id(a), id(b))     # the raw numbers — different from each other
```

The actual id values will differ every time you run this (they depend on
where Python happened to put the objects), but the *comparisons* always come
out the same way.

## Aliasing: why identity matters

If `a` and `c` are the same object, then a change made through either name is
visible through both. Two names for one object are called **aliases**:

```python
a = [1, 2, 3]
c = a             # alias, not copy

c.append(4)       # modify the list via the name c ...

print(c)          # [1, 2, 3, 4]
print(a)          # [1, 2, 3, 4]  — a "changed" too: there is only ONE list
```

For beginners this is the single most surprising behaviour in Python:
`c = a` does **not** copy the list. It copies the *reference* — the name tag.
This becomes central once your programs pass lists to functions and store
them inside other structures, so
[Chapter 9](../ch09-collections/01-references.md) gives references and
copying a full treatment. For now, remember the headline: *assignment never
copies an object; it creates an alias.*

## When is is the right tool: None checks

If `is` is so easy to misuse, when is it correct? One answer covers nearly
all real code: **checking for `None`.** `None` is Python's "no value here"
marker — and there is exactly *one* `None` object in the whole program, so
identity is precisely the right question. The official Python style guide
(PEP 8) says: comparisons to `None` should always use `is` or `is not`,
never `==`.

```python
def find_first_negative(numbers):
    for n in numbers:
        if n < 0:
            return n
    return None                     # signal: nothing found

result = find_first_negative([3, 1, 4])

if result is None:                  # the idiomatic None check
    print("no negative numbers found")
else:
    print("found", result)
```

`is not None` reads just as naturally: `if result is not None: ...`. Beyond
`None` checks (and the odd sentinel object), everyday code has little
business using `is` — reach for `==`.

## The Java version of this trap

Java splits the same idea across its type system, and getting it wrong is a
rite of passage in every Java course. In Java, `==` on **primitives**
(`int`, `double`, `boolean`, …) compares values — but `==` on **objects**
(including `String`!) compares references, i.e. it behaves like Python's
`is`. To compare object *values* you must call `.equals()`. Here is the same
experiment in both languages:

=== "Python"

    ```python
    s1 = "".join(["h", "i"])   # builds the string "hi" at run time
    s2 = "hi"

    print(s1 == s2)   # True  — == always compares values in Python
    print(s1 is s2)   # False — two distinct string objects

    a = 7
    b = 7
    print(a == b)     # True
    ```

=== "Java"

    ```java
    String s1 = new String("hi");    // forces a brand-new object
    String s2 = "hi";

    System.out.println(s1 == s2);        // false — compares REFERENCES
    System.out.println(s1.equals(s2));   // true  — compares characters

    int a = 7;
    int b = 7;
    System.out.println(a == b);          // true — primitives compare values
    ```

The translation table is worth memorising:

| Question           | Python | Java (objects) | Java (primitives) |
| ------------------ | ------ | -------------- | ----------------- |
| same **value**?    | `==`   | `.equals()`    | `==`              |
| same **object**?   | `is`   | `==`           | *(not applicable)* |

So the classic Java bug — `if (name == "quit")` compiling happily but never
being true for user input — cannot happen in Python: `==` on strings always
compares the characters. The price Python pays is a different trap: people
write `is` where they meant `==`, and it *appears* to work because of the
next section.

## Small-int caching: a curiosity, not a tool

Try `is` on small numbers and you get a puzzling result:

```python
small_a = 7
small_b = int("7")          # built at run time from a string
print(small_a == small_b)   # True
print(small_a is small_b)   # True?! — read on

big_a = 10_000
big_b = int("10000")        # also built at run time
print(big_a == big_b)       # True  — equal values, as expected
print(big_a is big_b)       # False — two separate objects
```

Why does `is` say `True` for 7 but `False` for 10 000? Because CPython (the
standard Python, and the Pyodide running these blocks) pre-builds one shared
object for every integer from $-5$ to $256$ and hands that same object out
whenever one of those values appears. It is purely a memory-saving
**implementation detail**: the language makes no promise about it, other
Python implementations do it differently, and the exact behaviour can vary
with how the code is compiled. The lesson is *not* "learn the cached range"
— it is **never use `is` to compare numbers or strings**. Use `==`, which is
guaranteed to mean what you want, everywhere, forever.

!!! info "Java corner"
    Java has the identical quirk: `Integer` objects from $-128$ to $127$ are
    cached, so `Integer a = 127, b = 127; a == b` is `true` while the same
    code with `128` is `false`. Same lesson, same fix: value comparisons on
    objects use `.equals()`, not `==`.

!!! warning "Common mistakes"
    - **Using `is` to compare numbers or strings.** It happens to work for
      small cached ints and some strings, then fails mysteriously for
      others. Only `==` is guaranteed to compare values.
    - **Writing `result == None`.** It usually works, but PEP 8 mandates
      `result is None` — it is faster, cannot be fooled by objects that
      define their own weird `==`, and signals intent.
    - **Expecting `b = a` to copy a list.** It creates an alias; mutations
      through `b` show up in `a`. Real copying comes in
      [Chapter 9](../ch09-collections/01-references.md).
    - **Assuming two equal-looking objects are one object.** `[1] == [1]`
      being `True` says nothing about `is` — equal twins are still two
      people.

## Check your understanding

1. Predict the four printed values, then run the first block on this page
   to check: `a == b`, `a is b`, `a == c`, `a is c`.

    ??? success "Answer"
        `True`, `False`, `True`, `True`. `a` and `b` hold equal but separate
        lists (equal value, different identity); `c = a` makes `c` a second
        name for `a`'s list (same identity — and therefore same value too).

2. Why is `if result is None:` preferred over `if result == None:`?

    ??? success "Answer"
        There is exactly one `None` object, so "is it the `None` object?" is
        an identity question — `is` answers it directly and reliably. PEP 8
        makes this the official style, and `==` could in principle be
        redefined by exotic objects to answer incorrectly.

3. A Java program tests `if (userInput == "quit")` and the branch never
   runs, even when the user types quit. What is wrong, and what is the
   Python equivalent of this bug?

    ??? success "Answer"
        Java's `==` on objects compares references; `userInput` is a
        different `String` object from the literal `"quit"`, so the test is
        `false` regardless of content — it needs
        `userInput.equals("quit")`. The Python analogue is writing
        `if user_input is "quit":` instead of `==` — an identity test where
        a value test was meant.

4. After `x = [10, 20]` and `y = x`, what does `y.append(30)` do to `x` —
   and what single fact about `y = x` explains it?

    ??? success "Answer"
        `x` becomes `[10, 20, 30]`. `y = x` copies the reference, not the
        list — both names point at one object, so a change through either
        name is seen through both.
