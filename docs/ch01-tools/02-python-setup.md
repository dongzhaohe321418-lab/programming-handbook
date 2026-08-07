# 1.2 Installing and running Python

Every Python block in this handbook runs in your browser, so you could — in
principle — finish the whole book without installing anything. But the day
you want to write a program that outlives the page, reads your own files, or
runs while you sleep, you need Python on your own machine. This section gets
you there, shows the four different ways one and the same program can be run,
and takes a first look at how the Java world does the same job — because if
you are following a Java course alongside this book, the contrast is half the
lesson.

## Getting Python onto your machine

There are three common routes, and beginners regularly lose an afternoon
choosing between them. Here is the honest comparison:

| Route | What you get | Best for |
| --- | --- | --- |
| **python.org installer** | The official CPython, nothing else | Almost everyone — our recommendation |
| **Anaconda** | Python plus hundreds of pre-installed scientific packages (several GB) | Courses that explicitly require it |
| **OS package manager** (Homebrew, `apt`, `winget`) | Python managed like any other system package | People already fluent in the terminal |

!!! tip "Our recommendation: python.org + VS Code"
    Download the latest **Python 3** installer from
    [python.org/downloads](https://www.python.org/downloads/), and install
    the free **Visual Studio Code** editor with its official Python
    extension. That pair is light, standard, and matches what most
    tutorials assume. On **Windows**, tick the box labelled
    *"Add python.exe to PATH"* during installation — it is the single most
    important checkbox of your programming career, because it is what lets
    the shell find Python when you type `python`.

Once installed, verify from the command line (Section
[1.1](01-command-line.md)) that the shell can find it:

```console
$ python --version
Python 3.12.5
```

On macOS and Linux the command is often `python3` (plain `python` may be
missing or point elsewhere); on Windows, `py` also works. Any version 3.10
or newer is fine for this book.

You can ask the same question *from inside* Python — this block reports the
version of the Python that is executing it, right now, in your browser:

```python
import sys

print(sys.version)
print(f"This is Python {sys.version_info.major}.{sys.version_info.minor}")
```

Run it: the browser's Python is a full CPython 3.11+ compiled to
WebAssembly. Version numbers matter because language features arrive over
time — code using `match` (Chapter 4) needs 3.10+, for example.

## Four ways to run the same program

Take the one-line program `print("Hello, world!")`. There are four standard
places to run it, and knowing which to reach for is a small professional
skill of its own.

### 1 · The REPL: a conversation

Typing `python` with no arguments starts the **REPL**
(*read–evaluate–print loop*): an interactive session that evaluates each
line as you enter it. The `>>>` prompt means Python — not the shell — is
listening.

```console
$ python
Python 3.12.5 (main, Aug  6 2024, 19:08:49) [Clang 15.0.0] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> print("Hello, world!")
Hello, world!
>>> 2 + 3
5
>>> exit()
$
```

The REPL is for *experiments*: checking what a function returns, testing one
line before it goes into a program. Nothing you type is saved. Leave with
`exit()` (or ++ctrl+d++ on macOS/Linux, ++ctrl+z++ then ++enter++ on
Windows).

### 2 · A script file: a program you can keep

Save the line in a file called `hello.py` using any editor, then hand the
file to Python from the shell:

```console
$ python hello.py
Hello, world!
```

This is how real programs are run and shared — a `.py` file is just text,
and `python file.py` executes it top to bottom. From Chapter 2 on, this is
the form to imagine all our examples in.

### 3 · A notebook: code with a narrative

A **notebook** (the Jupyter kind) is a document made of cells — some prose,
some runnable code with the output shown beneath. Notebooks shine for data
exploration and teaching, which is why this site offers a
[browser-based JupyterLab](../try-in-jupyter.md) if you want that
experience without installing anything.

### 4 · This handbook's Run button

Every `python` block on this site is live. Under the hood the page loads
**Pyodide**, a build of real CPython for the browser, so what you run here
is genuinely Python — with one visible difference you can detect:

```python
import sys

print("Hello, world!")
print("This Python is running on:", sys.platform)
```

On your own machine `sys.platform` reports `win32`, `darwin` (macOS), or
`linux`. In the browser it reports `emscripten` — the name of the
WebAssembly toolchain. Same language, different home.

## Virtual environments: one toolbox per project

Real projects use **packages** — libraries other people wrote, installed
with the `pip` command. And two projects soon disagree: one needs version 1
of some library, another needs version 2. Installing everything into one
global Python turns into a junk drawer where fixing one project breaks
another.

A **virtual environment** (*venv*) is the fix: a private, per-project copy
of the Python setup. Packages installed while a venv is *active* go into
that project's own folder and are invisible everywhere else. One project,
one toolbox. The ritual, run inside your project folder:

=== "macOS / Linux"

    ```console
    $ cd ~/projects/weather-app
    $ python3 -m venv .venv          # create the environment (once)
    $ source .venv/bin/activate      # switch it on for this shell
    (.venv) $ pip install requests   # installs go into .venv only
    (.venv) $ deactivate             # switch it off
    $
    ```

=== "Windows (PowerShell)"

    ```console
    PS C:\Users\kim\projects\weather-app> py -m venv .venv
    PS C:\Users\kim\projects\weather-app> .venv\Scripts\Activate.ps1
    (.venv) PS C:\Users\kim\projects\weather-app> pip install requests
    (.venv) PS C:\Users\kim\projects\weather-app> deactivate
    ```

The `(.venv)` prefix on the prompt is the tell: it means "this shell is
using the project's private Python". Python can even report whether it is
inside one:

```python
import sys

in_venv = sys.prefix != sys.base_prefix
print("Inside a virtual environment?", in_venv)
```

Here in the browser this prints `False` — the page's Python is not in a
venv. On your machine, run it before and after `activate` and watch the
answer flip. Nothing in this handbook requires a venv (the browser is its
own sandbox), but essentially every real Python project starts with one, so
file the ritual away now.

## The Java parallel: a compile stop on the way

If you are taking a Java-based course, your "install Python" step is
"install a **JDK**" (Java Development Kit — the compiler plus the runtime;
Java 17 from [Adoptium](https://adoptium.net/) is a standard choice), and
your `hello.py` looks rather different:

=== "Python"

    ```python
    print("Hello, world!")
    ```

    One file, any name, run directly:

    ```console
    $ python hello.py
    Hello, world!
    ```

=== "Java"

    ```java
    // Hello.java — the file name MUST match the class name
    public class Hello {
        public static void main(String[] args) {
            System.out.println("Hello, world!");
        }
    }
    ```

    Two steps — compile, then run:

    ```console
    $ javac Hello.java     # produces Hello.class (bytecode)
    $ java Hello           # the JVM executes the bytecode
    Hello, world!
    ```

The extra ceremony is real but shallow: `javac` translates your source into
`Hello.class`, a file of **bytecode**, and `java` starts the **JVM** (Java
Virtual Machine) to execute it — the compile/interpret story from
[Chapter 0.3](../ch00-machine/03-programs.md), with the seams showing.
Python performs a similar translation to bytecode too; it just does it
invisibly, every time you run. We return to virtual machines properly in
[Chapter 23](../ch23-os/03-interpreters-vms.md).

!!! info "Java corner"
    Check a Java installation the same way:  `java -version` and
    `javac -version` must *both* work (the second one is missing if you
    installed only a runtime, not a JDK). Since Java 11, small single-file
    programs can also skip the visible compile step:
    `java Hello.java` compiles in memory and runs — handy for
    experiments, though classwork usually expects the two-step form.

!!! warning "Common mistakes"
    - **`python: command not found` (or "not recognized").** The shell
      cannot find Python — on Windows, re-run the installer and tick *Add
      python.exe to PATH* (or use `py`); on macOS/Linux, try `python3`.
    - **Typing shell commands at the `>>>` prompt.** `python hello.py`
      typed *inside* the REPL is a `SyntaxError` — that command belongs to
      the shell. Watch the prompt: `$` means shell, `>>>` means Python.
    - **Running an unsaved file.** You edit `hello.py`, forget to save,
      re-run it, and see the old behaviour. Editors mark unsaved files with
      a dot — save first, then run.
    - **Installing every package globally.** It works for months, then two
      projects collide. One venv per project, from day one.

## Check your understanding

1. You want to quickly check what `"hello".upper()` returns. Which of the
   four ways of running Python fits best, and why?

    ??? success "Answer"
        The REPL. It evaluates one line at a time and shows the result
        immediately — perfect for throwaway experiments. A script file
        would be overkill for a question with a one-line answer.

2. What does `javac Hello.java` produce, and what program actually executes
   it?

    ??? success "Answer"
        It produces `Hello.class`, a file of JVM bytecode. The `java`
        command starts the Java Virtual Machine, which executes that
        bytecode. Nothing runs the `.java` source file directly.

3. A friend's prompt reads `(.venv) $`. What does that prefix tell you, and
   what happens if they run `pip install` right now?

    ??? success "Answer"
        A virtual environment named `.venv` is active in that shell. Any
        `pip install` goes into that project's private environment, not
        into the system-wide Python — so other projects are unaffected.

4. Why might `python --version` and the version shown by this page's Run
   button differ?

    ??? success "Answer"
        They are two separate installations of Python. The page runs
        Pyodide, a CPython built for the browser; `python --version`
        reports whatever is installed on your machine. Each is a complete,
        independent Python.
