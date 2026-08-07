---
title: How to use
---

# How to use this handbook

This handbook is a small laboratory: every Python example runs, every
exercise has a checkable solution, and every page is built around one habit
— *run the code, don't just read it*. Five minutes here shows you how all
the machinery works.

## The ▶ Run button

Every Python block on the site has a **▶ Run** button. Click it and the code
executes inside *your browser*, using [Pyodide](https://pyodide.org/) — a
WebAssembly build of real CPython. Nothing is installed on your computer and
nothing is sent to a server. Three things to know:

1. **The first click downloads the Python runtime (about 40 MB).** This
   happens once; your browser caches it. Expect a short wait the first time.
2. **After that, runs are effectively instant.**
3. **Plots appear right below the code**, and once the runtime is cached,
   everything keeps working even when you are offline.

Try it now:

```python
greeting = "Hello, reader!"
print(greeting)
```

All the blocks on a page **share one namespace**, like cells in a notebook:
a name defined in one block still exists in the next, so work down the page
in order. If a block complains that a name is not defined, run the earlier
blocks first (or reload the page to start fresh).

```python
# continues
# `greeting` still exists — it was defined in the block above.
print(greeting.upper())
```

Plots need no extra steps — run this and a chart appears below it:

```python
import matplotlib.pyplot as plt

xs = list(range(11))
ys = [x ** 2 for x in xs]
plt.plot(xs, ys, marker="o")
plt.xlabel("x")
plt.ylabel("x squared")
plt.title("Plots render right on the page")
```

## Read, predict, run, explain

The Run button only teaches if you use it *actively*. For every example:

1. **Read** the code line by line.
2. **Predict** — say out loud (or write down) exactly what it will print.
3. **Run** it and compare.
4. **Explain** any difference. A wrong prediction is not a failure; it is
   the exact moment your mental model gets corrected.

Practise on this one — commit to a number *before* you click Run:

```python
x = 10
x = x + 5
print(x * 2)
```

If you predicted `30`, your model of assignment is solid. If you predicted
`40` or `25`, even better — you just found something worth rereading.

## What the boxes mean

Colour-coded boxes (*admonitions*) flag different kinds of information:

| Box | What it tells you |
| --- | --- |
| **Note** | A detail worth remembering, slightly aside from the main thread |
| **Tip** | A practical shortcut or habit that makes your life easier |
| **Example** | A fuller worked example applying the idea just introduced |
| **Warning — Common mistakes** | Real errors beginners make on this topic; read these, they save hours |
| **Info — Java corner** | A short aside on how the same idea looks in Java |

## Exercises and solutions

Every chapter ends with an exercises page, ordered easiest first and tagged
with difficulty dots: ● (warm-up), ●● (solid practice), ●●● (stretch). Each
hides its full solution in a collapsible box — click the title to open it:

??? success "Solution"

    This is where the solution lives. **Attempt the exercise first, peek
    second.** Reading a solution you haven't fought with teaches almost
    nothing; reading one after ten minutes of honest effort teaches a lot.

The same collapsible boxes, titled *Answer*, follow the short *Check your
understanding* questions at the end of most sections.

## The Python / Java tabs

This handbook teaches in Python but deliberately runs alongside university
courses taught in Java. Wherever the two genuinely differ — types,
compilation, `==` versus `equals()`, interfaces — you get side-by-side tabs:

=== "Python"

    ```python
    x = 7
    ```

=== "Java"

    ```java
    int x = 7;
    ```

Python tabs run; Java tabs are for reading — they mirror what your course
code looks like. The full story of why we teach this way is on
[Python and Java](python-vs-java.md).

## When you're stuck

Being stuck is the normal state of programming; here is the escape routine.

1. **Read the error aloud, starting from the last line.** Python's final
   line names the problem and usually the fix. Try it on this one:

    ```python
    # raises TypeError
    age = "21"        # a string, not a number
    print(age + 4)    # you cannot add a number to a string
    ```

    The last line names `TypeError` and says a `str` and an `int` don't mix
    — the entire diagnosis, free of charge.

2. **Reduce the example.** Delete lines until the error disappears; the last
   thing you deleted is the culprit. The Run button makes this loop fast.
3. **Rubber-duck it.** Explain the code, line by line, to anything — a duck,
   a pet, an empty chair. Where your explanation goes vague is the bug.

## Prefer a notebook?

Everything here also works in a full **JupyterLab** in your browser — the
same zero-install Python, plus editable notebooks: [Try in Jupyter](try-in-jupyter.md).
