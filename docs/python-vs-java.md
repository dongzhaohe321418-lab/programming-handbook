---
title: Python and Java
---

# Python and Java

A fair question deserves a straight answer: *if the typical university
course teaches Java, why does this handbook teach in Python?* Because the
two decisions solve different problems — and used together, they teach you
more than either would alone.

## Why this book teaches in Python

- **It runs in your browser.** Python (via Pyodide) gives every example on
  this site a ▶ Run button — no compiler, no IDE, no setup. Java has no
  practical equivalent, and a book you can *run* beats a book you can only
  read.
- **Less ceremony.** Printing a line in Python is one line; in Java it is a
  class, a `main` method, and a semicolon before you reach the idea. When
  you are learning *loops*, every extra keyword is noise.
- **The concepts transfer.** Variables, branching, loops, arrays, objects,
  recursion, linked lists, trees, Big-O — these are ideas about
  computation, not about any language. Learn them once in Python and you
  will recognise them immediately in Java, C, or JavaScript.

## What Java gives you that Python hides — the honest costs

Python's convenience is real, but so is what it postpones. Three genuine
differences matter, and this book confronts each where it counts:

1. **Static typing.** Java makes you declare `int x` and refuses to compile
   `x = "hello"`. That strictness catches whole categories of bugs before
   the program ever runs; Python only discovers them *at* runtime. Both
   mindsets are worth having.
2. **Compilation.** Java is explicitly compiled (`javac` → bytecode → JVM),
   and the compile step is a visible gate where errors are caught. Python
   compiles to bytecode silently and interprets it — see
   [Chapter 0.3](ch00-machine/03-programs.md) and
   [Chapter 23](ch23-os/index.md) for what actually happens.
3. **Overloading.** Java lets one method name have several parameter lists
   and picks between them by type. Python allows one `def` per name and
   reaches for default arguments instead — a real design difference,
   unpacked in [Chapter 5](ch05-under-the-hood/index.md).

Smaller differences — `==` versus `equals()`, explicit interfaces, generics
— get the same treatment: a side-by-side comparison exactly where the topic
comes up.

## The core mental mapping

Keep this table in your head and most Java code reads itself. The full
version lives in [Appendix A](appendix/A-python-java.md).

| Python | Java |
| --- | --- |
| `print("hi")` | `System.out.println("hi");` |
| `x = 7` | `int x = 7;` |
| `def area(w, h):` | `static double area(double w, double h) { ... }` |
| `list` — `[1, 2, 3]` | array `int[]`, or `ArrayList<Integer>` |
| `dict` — `{"a": 1}` | `HashMap<String, Integer>` |
| `None` | `null` |
| `True` / `False` | `true` / `false` |
| `str` | `String` |
| `elif` | `else if` |
| `for item in items:` | `for (int item : items) { ... }` |
| `len(xs)` | `xs.length` (array) / `xs.size()` (`ArrayList`) |
| `==` compares values | `==` compares references; `.equals()` compares values |
| indentation defines blocks | braces `{ }` define blocks; `;` ends statements |
| `# comment` | `// comment` |

## One program, both languages

The same temperature converter, twice. Run the Python; *read* the Java —
notice that every moving part corresponds.

=== "Python"

    ```python
    def celsius_to_fahrenheit(c):
        return c * 9 / 5 + 32

    celsius = 25.0   # imagine the user typed this
    fahrenheit = celsius_to_fahrenheit(celsius)
    print(f"{celsius:.1f} C = {fahrenheit:.1f} F")
    ```

=== "Java"

    ```java
    public class TempConverter {
        public static double celsiusToFahrenheit(double c) {
            return c * 9.0 / 5.0 + 32.0;
        }

        public static void main(String[] args) {
            double celsius = 25.0;
            double fahrenheit = celsiusToFahrenheit(celsius);
            System.out.printf("%.1f C = %.1f F%n", celsius, fahrenheit);
        }
    }
    ```

Both print `25.0 C = 77.0 F`. The logic is identical; Java simply declares
every type and wraps everything in a class. Once you see that the wrapping
is *only* wrapping, switching languages stops being scary.

## The rule this book follows

**Java appears in tabs wherever the contrast teaches something** — typing,
compilation, `==` vs `equals()`, interfaces, generics — and in short *Java
corner* boxes for quick asides. Where the two languages are essentially the
same (a `for` loop is a `for` loop), you get Python only; tabbing everything
would just double the reading. Java blocks never have a Run button: they
are there to mirror what your coursework looks like, not to execute.

## Use both — deliberately

If you are taking a Java course, **write your assignments in Java** and use
this handbook for the concepts underneath them. Better yet, after solving
an exercise here in Python, redo it in Java: translating a solution between
languages is the single best test that you understood the idea and not just
the syntax. The [learning path](learning-path.md) page shows how to pace
this alongside a course.
