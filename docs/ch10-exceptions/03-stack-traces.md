# 10.3 Reading stack traces

Ask a professional programmer what separates beginners from everyone else
and "reads the error message" will be near the top of the list. A Python
**traceback** (or *stack trace* — the terms are interchangeable) is not
punishment. It is a precision instrument: a snapshot of the entire call
chain, taken at the exact instant an exception ran out of handlers, with
the failing line pinpointed to the character. Beginners scroll past it with
a groan; professionals read it and usually know the fix before touching the
keyboard. This page teaches you to read it their way — bottom line first.

## A failure three calls deep

The [previous section](02-exceptions.md) showed an exception flying up
through `c` → `b` → `a` into a handler. Remove the handler and the flight
goes all the way to the top, where Python prints the flight recorder. Run
it and look at the red output:

```python
# raises ZeroDivisionError
def a(n):
    return b(n)

def b(n):
    return c(n)

def c(n):
    return 100 / n

print(a(0))
```

Saved as `ratio.py` (comment line included) and run from a terminal, that
program prints this — the browser runner shows the same structure with a
different file name:

```text
Traceback (most recent call last):
  File "ratio.py", line 11, in <module>
    print(a(0))
          ^^^^
  File "ratio.py", line 3, in a
    return b(n)
           ^^^^
  File "ratio.py", line 6, in b
    return c(n)
           ^^^^
  File "ratio.py", line 9, in c
    return 100 / n
           ~~~~^~~
ZeroDivisionError: division by zero
```

## Read the bottom line first

Everything about a traceback is arranged for bottom-up reading, and the
header even warns you: *most recent call **last***. So start at the last
line — it answers **what** went wrong:

```text
ZeroDivisionError: division by zero
```

Left of the colon, the exception's *type* (`ZeroDivisionError`); right of
it, the *message* (`division by zero`). Those two together are the single
highest-value line of output your program will ever produce. Say it as a
sentence: "a division by zero happened somewhere."

Now move **up one entry** to answer **where**:

```text
  File "ratio.py", line 9, in c
    return 100 / n
           ~~~~^~~
```

Each two-to-three-line group like this is one **frame** — one entry of the
call stack you met in
[Section 5.3](../ch05-under-the-hood/03-stack-heap.md). Read its anatomy:
the file (`ratio.py`), the line number (9), the function (`c`), the source
line itself, and — on Python 3.11 and later — little markers underneath
pinpointing the failing operation: tildes under the operands, a caret at
the `/` itself. (The exact shape of those markers varies slightly between
Python versions; the information does not.) The *bottom frame is where the
exception was born.*

Keep walking **up** to answer **how we got there**: `b` line 6 called `c`;
`a` line 3 called `b`; the module's `print(a(0))` on line 11 started it
all. The full story, bottom-up: *the division in `c` failed; `c` was
called by `b`, which was called by `a`, which was called at the top level
with the argument 0.* The traceback is the call stack, printed root-first
— which is exactly why the freshest, most useful information is at the
bottom.

!!! tip "The three-step read"
    1. **Bottom line** — what kind of failure, and what message?
    2. **Bottom frame** — which file, line, and function did it happen in?
    3. **Walk upward** — how did execution get there, and which call
       supplied the bad value?

    For the trace above: (1) division by zero; (2) `c`, line 9;
    (3) the `0` came all the way from `print(a(0))`.

## Your frames, not the library's

Real tracebacks often end inside code you did not write — the standard
library or an installed package. Here is one from a program that asked
`statistics.mean` for the mean of an empty list (paths and line numbers
will differ on your machine):

```text
Traceback (most recent call last):
  File "report.py", line 4, in <module>
    print(average_score([]))
  File "report.py", line 2, in average_score
    return statistics.mean(scores)
  File "/usr/lib/python3.12/statistics.py", line 486, in mean
    raise StatisticsError('mean requires at least one data point')
statistics.StatisticsError: mean requires at least one data point
```

The bottom frame is inside `statistics.py`. Does that mean the standard
library is broken? Almost never. **The bug is usually in *your* frames —
the library frame merely reports it.** The professional move: scan upward
from the bottom until you hit the *last frame that belongs to your own
files* (`report.py`, line 2) — that is where your code handed something
unreasonable to somebody else's. The library did its job: it refused
loudly, with a clear message, instead of inventing an answer.

## The common exception types

Seven types cover the overwhelming majority of beginner tracebacks. Learn
to translate each name into the question it is asking you:

| Exception | What it means | Typical cause |
| --- | --- | --- |
| `ValueError` | right type, impossible value | `int("abc")`, `list.index` on a missing value |
| `TypeError` | wrong type entirely | adding `str` to `int`, calling `len(42)` |
| `IndexError` | sequence index out of range | off-by-one loops, indexing an empty list |
| `KeyError` | dict key not present | misspelled key, data missing a field |
| `AttributeError` | object has no such method/attribute | typo in a method name, wrong type of object |
| `ZeroDivisionError` | division or modulo by zero | unvalidated denominator |
| `NameError` | name never defined | typo in a variable name, use before assignment |

One-line proof of each — run any of them and practise the three-step read
on the result:

```python
# raises ValueError
int("twelve")             # right type (str), impossible value
```

```python
# raises TypeError
"loading" + 3             # str plus int — wrong type entirely
```

```python
# raises IndexError
[10, 20, 30][3]           # valid indexes are 0, 1, 2
```

```python
# raises KeyError
{"name": "Ada"}["age"]    # no such key in this dict
```

```python
# raises AttributeError
"hello".append("!")       # strings have no append method
```

```python
# raises ZeroDivisionError
100 / 0
```

```python
# raises NameError
print(mesage)             # 'mesage' was never defined — a typo
```

Recent Pythons go one step further with `NameError` and friends and often
append a suggestion like `Did you mean: 'message'?` — read those; they are
usually right.

## A glimpse of exception chaining

Sometimes a traceback contains *two* stories separated by this line:

```text
During handling of the above exception, another exception occurred:
```

That means an exception was raised **while a handler was already dealing
with an earlier one** — commonly, code catching a low-level failure and
re-raising it with a more helpful message:

```python
# raises KeyError
settings = {}

try:
    mode = settings["mode"]
except KeyError:
    raise KeyError("no 'mode' in settings — did you load the config file?")
```

Run it: the traceback shows the original `KeyError: 'mode'` first, the
chaining sentence, then the friendlier re-raise. Read chained tracebacks
the same way as ever — **the bottom-most story is the most recent**, and
the ones above it are the history that led there. (The variant
`raise ... from error` prints `The above exception was the direct cause
of the following exception:` instead — same reading order.)

## Java reads the other way

Your Java course's stack traces contain identical information — exception
type, message, and one line per frame — with one flip that trips up
everyone who switches languages:

```text
Exception in thread "main" java.lang.ArithmeticException: / by zero
        at Ratio.c(Ratio.java:11)
        at Ratio.b(Ratio.java:7)
        at Ratio.a(Ratio.java:3)
        at Ratio.main(Ratio.java:15)
```

Java prints **most recent call first**: the *what* is on the top line, and
the frame where the failure happened (`Ratio.c`) comes immediately after
it, with `main` at the bottom. Python prints most recent call *last*. So
the universal rule is not "read the bottom" but "**start where the
exception is named and read outward**" — bottom-up in Python, top-down in
Java.

!!! warning "Common mistakes"

    - **Reading the traceback top-down and stopping.** In Python the top
      frame is just where the program *started*. The exception type,
      message, and birthplace are all at the bottom.
    - **Ignoring the message after the colon.** `KeyError: 'age'` tells
      you *which* key was missing; `ValueError: invalid literal for
      int() with base 10: 'abc'` tells you *which* text failed to parse.
      Half your debugging is done by that one clause.
    - **Blaming the library because the bottom frame is theirs.** Walk up
      to your own bottom-most frame — that call is almost always the one
      that passed the impossible argument.
    - **Fixing the symptom's line instead of the value's source.** The
      failing line is where the bad value *arrived*, not necessarily where
      it was *created*. Walk the frames upward until you find who supplied
      it — in `ratio.py`, the real culprit was the `0` in `a(0)`.

## Check your understanding

1. In the `ratio.py` traceback, which function does the *top* frame belong
   to, and which does the *bottom* frame belong to? Which of the two tells
   you where the exception was raised?

    ??? success "Answer"
        The top frame is the module level (`<module>`, the `print(a(0))`
        line — where execution began); the bottom frame is `c`, and it is
        the bottom one that marks where the exception was born. Python
        prints the call chain oldest-first, newest-last.

2. A traceback's last line reads `KeyError: 'temperture'`. Without seeing
   any code, what is your best guess at the bug, and which single frame
   would you look at first?

    ??? success "Answer"
        The message names the exact key: `'temperture'` is almost
        certainly a misspelling of `'temperature'` at the place that
        *reads* the dict. Look at the bottom-most frame that is in your
        own file — the source line printed there contains the misspelled
        lookup.

3. Your friend says: "The traceback ends inside `statistics.py`, so the
   bug is in the standard library." Give the two-sentence professional
   rebuttal.

    ??? success "Answer"
        The bottom frame only shows where the failure was *detected* —
        the library checked its input and refused it. The bug is almost
        certainly in the last frame belonging to our own code, which
        handed the library an empty list; that is the call to fix.

4. In a Java trace, where do you find the exception type and message —
   and where in the frame list is the function that failed?

    ??? success "Answer"
        Both are on the *first* line (`java.lang.ArithmeticException: /
        by zero`), and the failing function is the first `at ...` entry
        right below it. Java lists frames most-recent-first — the mirror
        image of Python's ordering.
