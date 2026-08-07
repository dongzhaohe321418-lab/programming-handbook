# Chapter 10 · The Command Line and Exceptions

So far, every program in this book has lived in a friendly bubble: the input
was hard-coded, nothing unexpected ever arrived, and when something *did* go
wrong, Python printed a wall of red text and stopped. This chapter pops the
bubble twice. First, your programs grow up into **command-line tools** —
programs that a user launches from a terminal with arguments
(`python add.py 3 4`), the way real utilities like `git` and `python` itself
are launched. Second, you learn what that wall of red text actually is: an
**exception**, an object describing a failure, travelling up through your
function calls in search of someone prepared to handle it.

The two topics arrive together for a reason. The moment a program accepts
arguments from a stranger, "the input is always valid" stops being true —
users pass too few arguments, misspell units, and type `"seven"` where a
number belongs. Exceptions are the machinery a professional program uses to
meet that reality without collapsing: `try`/`except` to handle failures you
can recover from, `raise` to report ones you cannot, and precise, *narrow*
handlers so genuine bugs are never swallowed in the process.

The chapter ends with a skill that repays its cost faster than almost
anything else in programming: reading a **stack trace** properly. A
traceback is not an insult from the interpreter — it is a map, drawn at the
instant of failure, showing exactly what went wrong and the entire chain of
calls that led there. Learn to read it bottom-up and most "mystery" bugs
stop being mysteries before you have even reopened your editor.

**After this chapter you can …**

- explain what `sys.argv` contains, including why every element is a
  string and what sits at index 0;
- convert and validate command-line arguments, print a proper usage
  message, and explain what an exit code tells the shell;
- say precisely what an exception is, and trace its flight up the call
  chain toward a handler;
- write `try`/`except`/`else`/`finally` blocks, and catch specific
  exception types instead of using a bare `except`;
- raise your own exceptions from validating functions with helpful
  messages;
- read any Python traceback bottom-up: the *what* on the last line, the
  *where* in the frames above it;
- recognise the seven most common exception types on sight, and know what
  each one is telling you;
- compare all of the above with Java: `String[] args`,
  `try`/`catch`/`finally`, checked versus unchecked exceptions, and
  Java's top-first stack traces.

**Prerequisites:** functions and the call stack
([Chapter 3](../ch03-functions/index.md),
[Section 5.3](../ch05-under-the-hood/03-stack-heap.md)), lists and
indexing ([Chapter 7](../ch07-arrays/index.md)), and a first look at the
terminal from [Section 1.1](../ch01-tools/01-command-line.md).

**Sections**

- [10.1 Command-line programs and arguments](01-cli-programs.md) —
  `sys.argv`, argument conversion and validation, usage messages, exit
  codes, and a complete mini-tool.
- [10.2 Exceptions — try, except, finally](02-exceptions.md) — what an
  exception is, handling it narrowly, `else`/`finally`, raising your own,
  and the non-linear flight of an exception up the call chain.
- [10.3 Reading stack traces](03-stack-traces.md) — dissecting a real
  traceback line by line, the common exception types, and exception
  chaining.
- [Exercises](exercises.md) — handler predictions, validators that raise,
  traceback comprehension, and a robust command-line tool.
