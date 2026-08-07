# 11.2 Reading and writing files

This is the section where your programs gain a memory. Writing a file lets a
program leave something behind; reading one lets it pick up where another
program — or an earlier run of itself — left off. The mechanics are small
(one function, `open`, and one keyword, `with`), but they power everything
from configuration files to hundred-gigabyte data pipelines, and the habits
you build here scale all the way up.

!!! note "The convention on this page: create, then read"
    The browser sandbox starts empty — there are no files until you make
    them. So **every runnable block below follows the same two-step
    pattern: first it writes a file, then it reads that file back.** In real
    life the file often already exists (someone emailed you `grades.csv`);
    here, the first half of each example plays the role of "someone". Keep
    that in mind and the examples read naturally.

## Opening a file: `open` and its modes

`open(path, mode)` asks the operating system for access to a file and
returns a **file object** — your handle for reading or writing. The **mode**
string says what you intend to do:

| Mode  | Meaning | If the file exists | If it doesn't |
|-------|---------|--------------------|---------------|
| `"r"` | read (the default) | opens it | `FileNotFoundError` |
| `"w"` | write | **erases it** and starts fresh | creates it |
| `"a"` | append | keeps it, adds at the end | creates it |

The one to respect is `"w"`: opening a file for writing wipes its contents
*immediately*, before you have written a single character. There is no
confirmation dialog. Choose `"w"` for "replace whatever is there" and `"a"`
for "add to what is there".

Here is the whole life cycle at its most explicit — open, use, close — done
once for writing and once for reading:

```python
f = open("first.txt", "w", encoding="utf-8")
f.write("my first file\n")
f.close()                     # don't forget me!

f = open("first.txt", "r", encoding="utf-8")
print(f.read(), end="")
f.close()
```

```text
my first file
```

It works, but those `close()` calls are load-bearing, and code has a way of
jumping over them — an early `return`, an exception — leaving files dangling
open. Python has a construct that makes forgetting impossible.

## The `with` statement: files that close themselves

An open file is a live connection to the operating system, and it must be
**closed** when you are done: closing flushes any buffered text to disk and
releases the handle. You could call `f.close()` yourself — but if an
exception jumps over that line, the file stays open and written data can be
lost. Python's `with` statement makes closing automatic and unconditional:

```python
with open("greeting.txt", "w", encoding="utf-8") as f:
    f.write("Hello from a file!\n")
    f.write("This is line two.\n")

print("closed?", f.closed)   # True — closed the moment the block ended
```

However the indented block ends — normally, by `return`, or by an exception
— the file is closed. This is the same guarantee your Java course delivers
with try-with-resources:

=== "Python"

    ```python
    with open("greeting.txt", "w", encoding="utf-8") as f:
        f.write("Hello from a file!\n")
    print("done")
    ```

=== "Java"

    ```java
    try (PrintWriter out = new PrintWriter("greeting.txt")) {
        out.println("Hello from a file!");
    }   // out.close() happens here, no matter what
    System.out.println("done");
    ```

Notice one small difference hiding in there: Java's `println` adds the line
break for you; Python's `write` writes *exactly* the string you give it, so
you supply the `"\n"` yourself. Forgetting it is the classic way to produce a
file that is one enormous line.

## A word on `encoding="utf-8"`

Text must be translated to bytes on the way to disk, and the translation
table is called an **encoding**. UTF-8 is the encoding of the modern world —
it handles plain English, `café`, `π`, and `你好` alike — but Python's
default can vary between systems. Passing `encoding="utf-8"` every time you
open a text file makes your programs behave identically everywhere. It is
three seconds of typing for complete portability; every example in this book
does it, and you should too.

```python
with open("unicode.txt", "w", encoding="utf-8") as f:
    f.write("café, π, 你好\n")

with open("unicode.txt", encoding="utf-8") as f:
    print(f.read(), end="")
```

```text
café, π, 你好
```

Written as UTF-8 and read back as UTF-8, every character survives the round
trip. Mix encodings between the writer and the reader and you get mojibake —
`cafÃ©` and worse — which is why the habit is *always*, not *sometimes*.

## Writing a file, then reading it back

`f.read()` slurps the whole file into one string:

```python
with open("greeting.txt", "w", encoding="utf-8") as f:
    f.write("Hello from a file!\n")
    f.write("This is line two.\n")

with open("greeting.txt", "r", encoding="utf-8") as f:
    content = f.read()

print(repr(content))
```

```text
'Hello from a file!\nThis is line two.\n'
```

We printed the `repr` so you can *see* the newlines: the file is one long
string of characters in which `\n` marks the line breaks — files have no
deeper notion of "lines" than that. `read` is perfect for small files you
want in one piece; for files you want line by line, read on.

## Reading line by line — the idiomatic loop

A Python file object is iterable, and iterating yields one line at a time.
This is *the* standard way to process a text file:

```python
with open("shopping.txt", "w", encoding="utf-8") as f:
    f.write("milk\neggs\nbread\n")

with open("shopping.txt", encoding="utf-8") as f:
    for line in f:
        print("item:", line.strip())
```

```text
item: milk
item: eggs
item: bread
```

Two details make this loop idiomatic. First, it reads one line at a time
rather than the whole file, so it works just as happily on a million-line
log. Second, the `strip()`: each `line` arrives *with its trailing `"\n"`
still attached*, and since `print` adds a newline of its own, forgetting to
strip gives mysteriously double-spaced output. `line.strip()` (or
`line.rstrip()`) removes it.

=== "Python"

    ```python
    with open("scores.txt", "w", encoding="utf-8") as f:
        f.write("12\n31\n7\n")

    total = 0
    with open("scores.txt", encoding="utf-8") as f:
        for line in f:
            total += int(line.strip())
    print("total:", total)
    ```

=== "Java"

    ```java
    int total = 0;
    try (Scanner in = new Scanner(new File("scores.txt"))) {
        while (in.hasNextInt()) {
            total += in.nextInt();
        }
    }
    System.out.println("total: " + total);
    ```

Where Python says "loop over the file, convert each line", Java's `Scanner`
says "while there is another token, take it". Different rhythm, same song:
read until the data runs out.

## Appending: growing a log

Mode `"a"` positions every write at the end of the file, which is exactly
what a diary, journal, or log needs:

```python
with open("log.txt", "w", encoding="utf-8") as f:      # start the log
    f.write("day 1: set up the project\n")

with open("log.txt", "a", encoding="utf-8") as f:      # later: append
    f.write("day 2: wrote the first class\n")

with open("log.txt", "a", encoding="utf-8") as f:      # later still
    f.write("day 3: everything is on fire\n")

with open("log.txt", encoding="utf-8") as f:
    print(f.read(), end="")
```

```text
day 1: set up the project
day 2: wrote the first class
day 3: everything is on fire
```

Now the cautionary version. Replace those `"a"`s with `"w"` and each open
would erase the previous entries — only day 3 would survive:

```python
with open("oops.txt", "w", encoding="utf-8") as f:
    f.write("years of research notes\n")

with open("oops.txt", "w", encoding="utf-8") as f:     # "w" wipes it here
    f.write("hello\n")

with open("oops.txt", encoding="utf-8") as f:
    print(f.read(), end="")                            # the notes are gone
```

```text
hello
```

In this sandbox that is a shrug; on a real disk it is a very bad afternoon.
Check your mode before you run.

## A real worked example: grades in, averages out

Here is the shape of a thousand real programs: data arrives as a **CSV**
(comma-separated values) file — the plain-text format spreadsheets export —
and we want a computed summary. One line per student, columns separated by
commas:

```python
csv_text = """name,quiz1,quiz2,quiz3
Amara,88,92,79
Ben,75,81,90
Chloe,95,89,94
"""
with open("grades.csv", "w", encoding="utf-8") as f:
    f.write(csv_text)

with open("grades.csv", encoding="utf-8") as f:
    header = f.readline()                 # consume the column-name row
    for line in f:
        parts = line.strip().split(",")   # ["Amara", "88", "92", "79"]
        name = parts[0]
        scores = [int(s) for s in parts[1:]]
        average = sum(scores) / len(scores)
        print(f"{name}: {average:.1f}")
```

```text
Amara: 86.3
Ben: 82.0
Chloe: 92.7
```

Read the loop body slowly, because it is a template you will reuse for the
exercises and far beyond: **strip** the newline, **split** on the delimiter,
**convert** the numeric columns with `int` (everything read from a file is a
string until you say otherwise), then compute. The `f.readline()` before the
loop reads exactly one line — here, the header — so the `for` loop sees only
data rows.

## When the file isn't there

Opening a missing file for reading raises `FileNotFoundError`. Run it and
meet the message you will see many times in your career:

```python
# raises FileNotFoundError
with open("no_such_file.txt", encoding="utf-8") as f:
    print(f.read())
```

The traceback names the exception and the file it looked for. Because you
studied [exceptions in Chapter 10](../ch10-exceptions/02-exceptions.md), you
already know the recovery tool — `try`/`except` — and missing files are its
most natural use case:

```python
try:
    with open("settings.txt", encoding="utf-8") as f:
        settings = f.read()
except FileNotFoundError:
    settings = "theme=light"        # sensible default on first run
print(settings)
```

```text
theme=light
```

This "use the file if it exists, fall back if it doesn't" pattern is how real
applications handle their first launch, before any settings file exists.

!!! warning "Common mistakes"
    - **`"w"` when you meant `"a"`.** Opening with `"w"` erases the file on
      the spot. If the old contents should survive, append.
    - **Forgetting `"\n"` in `write`.** Unlike `print`, `write` adds
      nothing. Leave the newlines out and the whole file becomes one line.
    - **Not stripping on the way in.** Lines you read keep their trailing
      `"\n"`; printing them unstripped double-spaces your output, and
      comparing them (`line == "STOP"`) mysteriously fails because the line
      is really `"STOP\n"`.
    - **Reading twice from the same handle.** After `f.read()`, the file's
      position is at the end, so a second `f.read()` returns `""`. Re-open
      the file (or store the first result in a variable).

## Check your understanding

1. What is the difference between opening a file with `"w"` and with `"a"`,
   for a file that already has contents?

    ??? success "Answer"
        `"w"` erases the existing contents immediately and starts from an
        empty file; `"a"` keeps them and places every write at the end. Both
        create the file if it does not exist.

2. A loop prints each line of a file, but the output has a blank line after
   every real line. Why, and what is the fix?

    ??? success "Answer"
        Each line read from a file keeps its trailing `"\n"`, and `print`
        adds another newline. Fix: `print(line.strip())` (or
        `line.rstrip()`), or `print(line, end="")`.

3. Predict the output, then check by reasoning through the modes:

    ```text
    with open("d.txt", "w", encoding="utf-8") as f: f.write("A\n")
    with open("d.txt", "w", encoding="utf-8") as f: f.write("B\n")
    with open("d.txt", "a", encoding="utf-8") as f: f.write("C\n")
    with open("d.txt", encoding="utf-8") as f: print(f.read(), end="")
    ```

    ??? success "Answer"
        `B` then `C`. The second `"w"` erased the `A` line; the `"a"` added
        `C` after `B`.

4. Why does the grades example call `int(s)` on the score columns before
   averaging them?

    ??? success "Answer"
        Everything read from a text file is a string. `"88"` and `"92"`
        would concatenate, not add — `sum` on strings fails outright — so
        each column must be converted to a number first.
