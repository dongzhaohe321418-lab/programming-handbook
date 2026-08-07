# A · Python ↔ Java cheat sheet

Everything in one place: the Python you learned here on the left, the Java
from a typical university course on the right. Python facts hold for
CPython 3.11+; Java facts hold for Java 17. Rows link to the chapter that
explains the *why* whenever the difference is deeper than spelling. Skim it
now, bookmark it, and come back every time your two languages blur.

## Program skeleton and entry point

Python runs a file top to bottom; Java runs the `main` method of the class
you name.

=== "Python"

    ```python
    # hello.py — the file itself is the program
    print("Hello!")
    ```

=== "Java"

    ```java
    // Hello.java — code must live in a class; main is the entry point
    public class Hello {
        public static void main(String[] args) {
            System.out.println("Hello!");
        }
    }
    ```

Run with `python hello.py` versus `javac Hello.java` then `java Hello` —
Java's separate compile step is explained in
[Chapter 0.3](../ch00-machine/03-programs.md).

## Printing

| What | Python | Java |
| --- | --- | --- |
| Print with newline | `print("hi")` | `System.out.println("hi");` |
| Print without newline | `print("hi", end="")` | `System.out.print("hi");` |
| Print several values | `print(x, y)` (space-separated) | `System.out.println(x + " " + y);` |
| Formatted print | `print(f"{x:.2f}")` | `System.out.printf("%.2f%n", x);` |

## Variables and types

| What | Python | Java |
| --- | --- | --- |
| Declare + assign | `x = 7` | `int x = 7;` (or `var x = 7;` for locals) |
| Reassign to another type | `x = "hi"` — allowed | compile error — the type is fixed |
| Integer | `int` — unlimited size | `int` — 32-bit (`long` — 64-bit) |
| Real number | `float` (64-bit) | `double` (64-bit); `float` is the 32-bit one |
| Boolean | `True` / `False` (type `bool`) | `true` / `false` (type `boolean`) |
| Text | `str` — `"hi"` or `'hi'` | `String` — `"hi"` only |
| Single character | no such type — a length-1 `str` | `char` — `'h'` with single quotes |
| "Nothing" | `None` | `null` |
| Constant | `TAX_RATE = 0.08` (convention only) | `final double TAX_RATE = 0.08;` (enforced) |
| Comment | `# comment` | `// comment` or `/* block */` |
| Doc comment | `"""docstring"""` | `/** Javadoc */` |

Typing styles — dynamic versus static — are contrasted in
[Chapter 2.1](../ch02-data/01-variables-types.md); integer size limits and
overflow in [Chapter 5.1](../ch05-under-the-hood/01-numeric-pitfalls.md).

## Conversions and casting

| What | Python | Java |
| --- | --- | --- |
| String → int | `int("42")` | `Integer.parseInt("42")` |
| String → real | `float("3.5")` | `Double.parseDouble("3.5")` |
| Number → string | `str(42)` | `String.valueOf(42)` or `"" + 42` |
| Real → int (truncate) | `int(3.9)` → `3` | `(int) 3.9` → `3` |
| Int → real | `float(7)` | happens implicitly: `double d = 7;` |
| Rounding | `round(2.7)` → `3` | `Math.round(2.7)` → `3` |
| Failed parse raises | `ValueError` | `NumberFormatException` |

Beware `round()` on halves — see [false friends](#false-friends) below.

## Operators

| What | Python | Java |
| --- | --- | --- |
| Add, subtract, multiply | `+  -  *` | `+  -  *` |
| Division (see false friends!) | `/` always real; `//` floors | `/` truncates for ints, real for doubles |
| Remainder / modulo | `%` (sign follows the divisor) | `%` (sign follows the dividend) |
| Power | `x ** 2` | `Math.pow(x, 2)` (returns `double`) |
| Increment | `x += 1` (no `++`) | `x++` or `x += 1` |
| Compound assign | `+=  -=  *=  /=` | same |
| Comparison | `==  !=  <  <=  >  >=` | same spelling — but see `==` below |
| Logical and, or, not | `and` `or` `not` | <code>&amp;&amp;</code> <code>&#124;&#124;</code> <code>!</code> |
| Ternary / conditional | `a if cond else b` | `cond ? a : b` |
| Bitwise | <code>&amp; &#124; ^ ~ &lt;&lt; &gt;&gt;</code> | same, plus `>>>` (unsigned shift) |
| Chained comparison | `0 <= x < 10` | not allowed — write `0 <= x && x < 10` |

Precedence and modulo behaviour:
[Chapter 2.3](../ch02-data/03-operators.md); short-circuiting:
[Chapter 5.2](../ch05-under-the-hood/02-shortcuts-gotchas.md); bitwise
operators: [Chapter 6.4](../ch06-loops/04-bitwise-enums.md).

## Strings

Immutable in both languages: every "change" builds a new string
([Chapter 3.2](../ch03-functions/02-strings.md)).

| What | Python | Java |
| --- | --- | --- |
| Length | `len(s)` | `s.length()` |
| Character at index | `s[0]` | `s.charAt(0)` |
| Substring (end exclusive) | `s[2:5]` | `s.substring(2, 5)` |
| Upper / lower case | `s.upper()` / `s.lower()` | `s.toUpperCase()` / `s.toLowerCase()` |
| Trim whitespace | `s.strip()` | `s.strip()` (or older `s.trim()`) |
| Find position | `s.find("ab")` → `-1` if absent | `s.indexOf("ab")` → `-1` if absent |
| Contains | `"ab" in s` | `s.contains("ab")` |
| Starts / ends with | `s.startswith("a")` / `s.endswith("z")` | `s.startsWith("a")` / `s.endsWith("z")` |
| Replace all | `s.replace("a", "b")` | `s.replace("a", "b")` |
| Split | `s.split(",")` | `s.split(",")` — the argument is a *regex*! |
| Join | `", ".join(parts)` | `String.join(", ", parts)` |
| Interpolation | `f"{name}: {score:.1f}"` | `String.format("%s: %.1f", name, score)` |
| Value equality | `s == t` | `s.equals(t)` — **never** `==` |
| Compare order | `s < t` | `s.compareTo(t) < 0` |

Formatting mini-language: [Chapter 3.4](../ch03-functions/04-output-formatting.md).

## Control flow

| What | Python | Java |
| --- | --- | --- |
| If | `if x > 0:` + indent | `if (x > 0) { ... }` |
| Else-if | `elif x < 0:` | `else if (x < 0) { ... }` |
| Else | `else:` | `else { ... }` |
| Blocks marked by | indentation | braces `{ }`; statements end with `;` |
| Multi-way on a value | `match x:` / `case 1:` | `switch (x)` / `case 1 ->` (or `case 1:` + `break`) |
| Condition must be | anything truthy | a real `boolean` — `if (x)` with `int x` won't compile |

Branching details and `match`:
[Chapter 4.2](../ch04-branching/02-if-else.md) and
[Chapter 4.4](../ch04-branching/04-switch-style-debug.md).

## Loops

| What | Python | Java |
| --- | --- | --- |
| While | `while n > 0:` | `while (n > 0) { ... }` |
| Do-while | none — use `while True:` + `break` | `do { ... } while (n > 0);` |
| Counted loop | `for i in range(5):` | `for (int i = 0; i < 5; i++) { ... }` |
| Counted from a to b−1 | `for i in range(a, b):` | `for (int i = a; i < b; i++)` |
| Step / countdown | `range(10, 0, -1)` | `for (int i = 10; i > 0; i--)` |
| For-each | `for x in xs:` | `for (int x : xs) { ... }` |
| With index and value | `for i, x in enumerate(xs):` | index loop + `xs[i]` / `xs.get(i)` |
| Exit / skip | `break` / `continue` | `break;` / `continue;` |

Both `range(a, b)` and the C-style condition `i < b` are half-open: they
stop *before* `b` ([Chapter 6.2](../ch06-loops/02-for.md)).

## Collections

Dynamic array — `list` vs `ArrayList`
([Chapter 9.2](../ch09-collections/02-dynamic-lists.md)):

| What | Python `list` | Java `ArrayList` |
| --- | --- | --- |
| Create | `xs = [1, 2, 3]` | `var xs = new ArrayList<>(List.of(1, 2, 3));` |
| Add at end | `xs.append(4)` | `xs.add(4)` |
| Read / write at index | `xs[0]` / `xs[0] = 9` | `xs.get(0)` / `xs.set(0, 9)` |
| Length | `len(xs)` | `xs.size()` |
| Insert at index | `xs.insert(1, 9)` | `xs.add(1, 9)` |
| Remove by value | `xs.remove(9)` | `xs.remove(Integer.valueOf(9))` — `remove(9)` means *index 9*! |
| Membership | `9 in xs` | `xs.contains(9)` |
| Sort in place | `xs.sort()` | `Collections.sort(xs)` |
| Plain fixed array | (use a list) | `int[] a = new int[10];`, length `a.length` |

Dictionary / map — `dict` vs `HashMap`
([Chapter 14.1](../ch14-beyond/01-collections-tour.md)):

| What | Python `dict` | Java `HashMap` |
| --- | --- | --- |
| Create | `d = {"a": 1}` | `var d = new HashMap<String, Integer>();` |
| Put | `d["b"] = 2` | `d.put("b", 2)` |
| Get (missing key!) | `d["b"]` — raises `KeyError` | `d.get("b")` — returns `null` |
| Get with default | `d.get("b", 0)` | `d.getOrDefault("b", 0)` |
| Contains key | `"b" in d` | `d.containsKey("b")` |
| Delete | `del d["b"]` | `d.remove("b")` |
| Size | `len(d)` | `d.size()` |
| Loop over pairs | `for k, v in d.items():` | `for (var e : d.entrySet())` then `e.getKey()`, `e.getValue()` |

Set — `set` vs `HashSet`:

| What | Python `set` | Java `HashSet` |
| --- | --- | --- |
| Create | `s = {1, 2}` (empty: `set()`) | `var s = new HashSet<Integer>();` |
| Add / remove | `s.add(3)` / `s.discard(3)` | `s.add(3)` / `s.remove(3)` |
| Membership | `3 in s` | `s.contains(3)` |
| Union / intersection | <code>a &#124; b</code> / `a & b` | `a.addAll(b)` / `a.retainAll(b)` — these *mutate* `a` |

## Functions and methods

| What | Python | Java |
| --- | --- | --- |
| Define | `def area(w, h):` | `static double area(double w, double h) { ... }` |
| Return | `return w * h` | `return w * h;` |
| No return value | returns `None` implicitly | declare `void` |
| Default argument | `def greet(name="world"):` | none — write overloads instead |
| Same name, different params | not allowed (last `def` wins) | overloading — resolved by parameter types |
| Keyword arguments | `area(h=2, w=3)` | none — arguments are positional |
| Variable arg count | `def f(*args):` | `static int f(int... args)` |
| Return two things | `return lo, hi` (a tuple) | one value only — wrap in a small class/record |

Why Python trades overloading for defaults:
[Chapter 5.4](../ch05-under-the-hood/04-overloading-imports.md); function
anatomy: [Chapter 3.3](../ch03-functions/03-writing-functions.md).

## Object-oriented programming

| What | Python | Java |
| --- | --- | --- |
| Class | `class Dog:` | `public class Dog { ... }` |
| Constructor | `def __init__(self, name):` | `public Dog(String name) { ... }` |
| Instance variable | `self.name = name` (created on assignment) | `private String name;` (declared up front) |
| Create object | `d = Dog("Rex")` | `Dog d = new Dog("Rex");` |
| Current object | `self` — explicit first parameter | `this` — implicit |
| Method | `def bark(self):` | `public void bark() { ... }` |
| To-string | `def __str__(self):` | `@Override public String toString()` |
| Value equality | `def __eq__(self, other):` | override `equals()` *and* `hashCode()` |
| Inheritance | `class Puppy(Dog):` | `class Puppy extends Dog` |
| Call parent constructor | `super().__init__(name)` | `super(name);` |
| Override method | just redefine it — no keyword needed | redefine it; annotate `@Override` |
| Abstract class | `class Shape(abc.ABC):` + `@abstractmethod` | `abstract class Shape` + `abstract` methods |
| Interface | closest: ABCs and duck typing | `interface Walker { ... }` + `implements` |
| Access control | convention: `_protected`, `__mangled` | keywords: `private`, `protected`, `public` |
| Static method | `@staticmethod` decorator | `static` keyword |
| Getter/setter style | `@property` decorator | explicit `getX()` / `setX(...)` methods |

Encapsulation: [Chapter 13.1](../ch13-design/01-encapsulation.md);
inheritance and interfaces:
[Chapter 15.1](../ch15-inheritance/01-inheritance.md) and
[Chapter 15.3](../ch15-inheritance/03-interfaces.md).

## Exceptions

| What | Python | Java |
| --- | --- | --- |
| Guard risky code | `try:` | `try { ... }` |
| Handle | `except ValueError as e:` | `catch (NumberFormatException e) { ... }` |
| Handle any | `except Exception as e:` | `catch (Exception e)` |
| Always run | `finally:` | `finally { ... }` |
| Throw | `raise ValueError("bad input")` | `throw new IllegalArgumentException("bad input");` |
| Define your own | `class TooCold(Exception): pass` | `class TooCold extends Exception { ... }` |
| Checked exceptions | none — any code may raise anything | `IOException` etc. must be caught or declared with `throws` |
| Error report | traceback — read *bottom-up* | stack trace — read *top-down* |

The full model: [Chapter 10.2](../ch10-exceptions/02-exceptions.md);
reading the reports: [Chapter 10.3](../ch10-exceptions/03-stack-traces.md).

## File I/O

| What | Python | Java |
| --- | --- | --- |
| Read whole file | `Path("f.txt").read_text()` | `Files.readString(Path.of("f.txt"))` |
| Read lines | `with open("f.txt") as f:` then `for line in f:` | `for (String line : Files.readAllLines(Path.of("f.txt")))` |
| Write (overwrite) | `Path("f.txt").write_text(data)` | `Files.writeString(Path.of("f.txt"), data)` |
| Append | `open("f.txt", "a")` | `Files.writeString(path, data, StandardOpenOption.APPEND)` |
| Auto-close | `with open(...) as f:` | try-with-resources: `try (var r = ...)` |
| Missing file raises | `FileNotFoundError` | `NoSuchFileException` (checked!) |

Paths and the `with` habit: [Chapter 11](../ch11-files/index.md).

## Naming conventions

| Thing | Python | Java |
| --- | --- | --- |
| Variables, functions/methods | `snake_case` | `camelCase` |
| Classes | `PascalCase` | `PascalCase` |
| Constants | `UPPER_SNAKE` | `UPPER_SNAKE` |
| Files | any name; `hello_utils.py` | must match the public class: `HelloUtils.java` |
| Packages/modules | short, lowercase | lowercase, dot-separated |

## False friends

The dangerous rows: code that *looks* identical in the two languages but
means something different. These cause more real bugs than everything
else on this page combined.

| Looks the same | In Python | In Java |
| --- | --- | --- |
| `a == b` | compares **values** (calls `__eq__`) | compares **references** for objects — use `.equals()` for values ([Ch 4.3](../ch04-branching/03-equality-identity.md)) |
| `7 / 2` | `3.5` — `/` is always real division | `3` — int ÷ int truncates; you wanted `7 / 2.0` |
| `-7 // 2` vs `-7 / 2` | `-4` — floor division rounds *down* | `-3` — truncation rounds *toward zero* |
| `-7 % 3` | `2` — result has the divisor's sign | `-1` — result has the dividend's sign |
| `round(2.5)` | `2` — ties round to the *even* neighbour | `Math.round(2.5)` → `3` — ties round up |
| `'x'` | a `str` of length 1 — same as `"x"` | a `char`, a 16-bit number in disguise |
| `case` fallthrough | `match` never falls through | classic `switch` falls through without `break;` (arrow `->` form doesn't) |
| `x = y` for objects | copies the **reference** — both names share one object | same! — this one is a *true* friend; primitives are copied by value ([Ch 9.1](../ch09-collections/01-references.md)) |
| Passing an argument | object reference passed by value ("sharing") | identical rule — but Java primitives are pure copies |
| `1000000 * 1000000` | correct — ints never overflow | overflows `int` silently ([Ch 5.1](../ch05-under-the-hood/01-numeric-pitfalls.md)) |
| "length" of things | `len(x)` for everything | `a.length` (array), `s.length()` (String), `xs.size()` (collection) |
| `if (items):` truthiness | empty list/string/dict counts as false | won't compile — conditions must be `boolean` |

!!! tip "When in doubt"

    Translate the *idea*, not the line. Write what you mean in plain
    English ("divide, keeping the fraction", "compare the contents"),
    then express that in the target language. Line-by-line transliteration
    is exactly how the false friends above sneak in.
