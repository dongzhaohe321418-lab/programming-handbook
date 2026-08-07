# 10.1 Command-line programs and arguments

Every tool you met in [Section 1.1](../ch01-tools/01-command-line.md) —
`ls`, `cd`, `python` itself — follows the same recipe: a name, then
*arguments* that tell it what to work on. `python add.py 3 4` is you passing
`3` and `4` to your own program the same way you pass `report.txt` to `ls`.
Writing programs that accept arguments is the moment your scripts stop being
private experiments and become **tools** — things that other people (and
other programs!) can run without opening an editor. This page shows where
the arguments land, why they always arrive as strings, and how a
professional tool responds when they are wrong.

## Running a program with arguments

Suppose the file `add.py` adds two numbers. From a terminal, a user runs:

```console
$ python add.py 3 4
7
```

Everything after `python` is split on spaces into a list of words:
`add.py`, `3`, `4`. Python collects those words and hands them to your
program as `sys.argv` — a plain, ordinary **list of strings**:

```text
# add.py — as you would write it for the terminal
import sys

a = int(sys.argv[1])
b = int(sys.argv[2])
print(a + b)
```

Two facts to memorise about `sys.argv`:

1. **`sys.argv[0]` is the script's own name** (`"add.py"`). The user's
   first *real* argument is `sys.argv[1]`.
2. **Every element is a string.** The shell has no idea that `3` is meant
   to be a number — it passes the characters, and converting them is your
   job.

## The handbook convention: simulating `argv` in the browser

The Run button on this page executes code in your browser, where there is
no terminal and no command line — so `sys.argv` would be meaningless here.
Throughout the handbook we therefore *simulate* it with one honest line at
the top, and everything else stays exactly as it would be in the real file:

```python
argv = ["add.py", "3", "4"]   # what sys.argv would contain

a = int(argv[1])
b = int(argv[2])
print(a + b)                  # 7
```

To "rerun with different arguments", edit the `argv` line and press Run
again — that is the browser's version of typing a new command.

## Everything is a string — convert before you compute

Forget the conversion and Python will not warn you; it will cheerfully do
*string* arithmetic instead:

```python
argv = ["add.py", "3", "4"]   # what sys.argv would contain

print(argv[0])                # add.py — the program's own name
print(argv[1] + argv[2])      # 34  — string concatenation! not addition
print(int(argv[1]) + int(argv[2]))   # 7 — convert first, then compute
```

`"3" + "4"` gluing into `"34"` is the single most classic command-line bug,
and it is silent — no error, just a wrong answer. Convert every argument
deliberately: `int()` for whole numbers, `float()` for measurements, and
leave genuine text alone.

## Validating arguments and printing usage

A tool cannot control what its user types. The bare-minimum professional
courtesy is: *check the argument count, and if it is wrong, print a usage
message* — a one-line reminder of how the program is meant to be called.
Try this block as-is, then fix the `argv` line and run it again:

```python
argv = ["add.py", "3"]        # what sys.argv would contain — one number short!

if len(argv) != 3:
    print(f"usage: python {argv[0]} NUMBER NUMBER")
else:
    a = int(argv[1])
    b = int(argv[2])
    print(a + b)
```

The usage line names the program via `argv[0]` and shows placeholders in
capitals — the same convention you see when you run real tools with wrong
arguments (try `git commit` with no message some time).

## Exit codes: how programs report success to the shell

When a terminal program finishes, it hands the shell one integer — its
**exit code**. The convention is universal: **0 means success, anything
non-zero means failure**, with different numbers optionally naming
different failures. Shells and build scripts read the code to decide what
to do next:

```console
$ python add.py 3 4
7
$ echo $?
0
$ python add.py 3
usage: python add.py NUMBER NUMBER
$ echo $?
1
```

In a real file, you exit early with a code using `sys.exit`:

```text
# add.py — terminal version with a proper exit code
import sys

if len(sys.argv) != 3:
    print("usage: python add.py NUMBER NUMBER")
    sys.exit(1)          # stop now; tell the shell "I failed"

print(int(sys.argv[1]) + int(sys.argv[2]))
```

We show this as text rather than a runnable block for a reason:
`sys.exit(1)` works by raising a special exception (`SystemExit`) that
shuts the whole program down — and in the browser there is no shell waiting
to receive the code, so the runner would just report the `SystemExit`
instead of quietly ending. In handbook examples we simulate the same logic
with `if`/`else`; in your real terminal programs, use `sys.exit`.

## Java: `String[] args`

Your Java course covers the same ideas through the `main` method's
parameter — with one off-by-one difference that catches everyone at least
once:

=== "Python"

    ```python
    argv = ["Add.py", "3", "4"]   # what sys.argv would contain

    # argv[0] is the PROGRAM NAME; arguments start at argv[1]
    a = int(argv[1])
    b = int(argv[2])
    print(a + b)                  # 7
    ```

=== "Java"

    ```java
    public class Add {
        public static void main(String[] args) {
            // args[0] is the FIRST ARGUMENT — no program name!
            int a = Integer.parseInt(args[0]);
            int b = Integer.parseInt(args[1]);
            System.out.println(a + b);
        }
    }
    ```

Run as `java Add 3 4`, Java's `args` is `{"3", "4"}` — the program's name
is *not* included, so everything shifts down one index compared with
Python. Both languages agree on the important part: arguments arrive as
strings (`String[]`), and `Integer.parseInt` is Java's `int()`.

## Worked example: a unit-converting mini-tool

Here is a complete tool, `convert.py`, that converts between kilometres
and miles: `python convert.py 42 km` prints the distance in miles. It
checks the argument count, validates the unit, converts the number, and
formats the answer — the full life of a small command-line program. Edit
the `argv` line to try `mi`, a wrong unit, or a missing argument:

```python
argv = ["convert.py", "42", "km"]   # what sys.argv would contain

KM_PER_MILE = 1.609344

def to_miles(km):
    return km / KM_PER_MILE

def to_km(miles):
    return miles * KM_PER_MILE

if len(argv) != 3:
    print(f"usage: python {argv[0]} VALUE UNIT   (UNIT is km or mi)")
else:
    value = float(argv[1])
    unit = argv[2]
    if unit == "km":
        print(f"{value} km = {to_miles(value):.2f} mi")
    elif unit == "mi":
        print(f"{value} mi = {to_km(value):.2f} km")
    else:
        print(f"unknown unit: {unit} (expected km or mi)")
```

One case is still unguarded: `float(argv[1])` when the user types
`python convert.py fast km`. That call fails with a `ValueError` — and
handling it gracefully instead of crashing is exactly what the
[next section](02-exceptions.md) teaches. Real tools are built from both
halves: argument plumbing from this page, failure handling from the next.

!!! warning "Common mistakes"

    - **Doing arithmetic on raw arguments.** `argv[1] + argv[2]` is string
      concatenation — `"3" + "4"` is `"34"`, silently. Convert with
      `int()`/`float()` first, every time.
    - **Off-by-one on `argv[0]`.** In Python, index 0 is the script name
      and user arguments start at 1; in Java, `args[0]` *is* the first
      argument. Translating between the two shifts every index.
    - **Indexing before checking.** If the user passes no arguments,
      `argv[1]` raises `IndexError` before your validation ever runs.
      Check `len(argv)` *first*, then index.
    - **Testing only the happy path.** Run your tool with too few
      arguments, too many, and nonsense values — that is what your users
      will do within the first minute.

## Check your understanding

1. The user runs `python stats.py scores.txt 10`. What is `sys.argv`,
   exactly — length, contents, and types?

    ??? success "Answer"
        `["stats.py", "scores.txt", "10"]` — a list of three elements,
        every one a string. The `10` is the string `"10"` until the
        program calls `int()` on it; the script name occupies index 0.

2. Why do the runnable examples on this page write
   `argv = ["add.py", "3", "4"]` instead of using `sys.argv` directly?

    ??? success "Answer"
        The blocks run in your browser, where no shell launched the
        program, so `sys.argv` holds nothing useful. The convention
        simulates exactly what `sys.argv` *would* contain for a given
        command line, and the rest of the code is identical to the real
        file's.

3. A build script runs your program and then checks the exit code. Your
   program printed the correct usage message when called wrongly — but the
   build script carried on as if everything succeeded. What did your
   program forget?

    ??? success "Answer"
        To exit with a non-zero code (`sys.exit(1)`). Printing a message
        informs the *human*; the exit code informs the *shell*. A program
        that ends normally reports 0 — success — no matter what it
        printed along the way.
