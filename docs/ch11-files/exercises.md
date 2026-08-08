# Exercises

## The chapter in brief

- An operating system stores files in a **tree** of directories, and a
  **path** is simply the walk through that tree ([11.1](01-paths.md)).
- An absolute path starts at the root and means the same thing anywhere; a
  relative path is resolved from the **current working directory**, which is
  why the same program can work from one folder and fail from another.
- Always write forward slashes in paths: inside a Python string a backslash
  begins an escape sequence such as `\n`.
- `pathlib.Path` joins pieces with the `/` operator and answers questions
  about itself — `name`, `suffix`, `stem`, `parent`, `exists()`.
- A `Path` is only an address; nothing exists on disk until something is
  actually written there.
- `open(path, mode)` hands back a file object, and the **mode** decides the
  fate of an existing file: `"r"` reads it, `"w"` erases it, `"a"` appends to
  it ([11.2](02-read-write.md)).
- The `with` statement closes the file however the block ends — Python's
  equivalent of Java's try-with-resources.
- Passing `encoding="utf-8"` on every open makes the same characters come
  back on every machine.
- `f.read()` returns the whole file as one string, while iterating the file
  yields one line at a time — each still carrying its trailing `"\n"`.
- The CSV template is **strip, split, convert, compute**, because everything
  read from a text file is a string until you convert it.
- Opening a missing file for reading raises `FileNotFoundError`, and
  `try`/`except` turns that into a sensible default instead of a crash.

### Key terms

| Term | Reminder |
| --- | --- |
| [path (absolute and relative)](../concept-index.md) | the recorded walk to a file, from the root or from where you stand |
| [working directory](../concept-index.md) | the "here" that every relative path is measured from |
| `pathlib.Path` | an object that builds and inspects paths without string surgery |
| [file mode (`"r"`, `"w"`, `"a"`)](../concept-index.md) | read, erase-then-write, or append |
| [`with` statement](../concept-index.md) | a block whose file is closed no matter how the block ends |
| [Unicode](../concept-index.md) | why `encoding="utf-8"` belongs on every `open` |
| CSV | comma-separated text, one record per line — the format spreadsheets export |
| `FileNotFoundError` | the exception raised by reading a file that is not there |

Now to the keyboard.

Every exercise below runs in the browser sandbox, so follow the chapter's
convention: **create the file first, then process it** — each solution block
is self-contained and does exactly that. Try each one yourself before opening
the solution.

### Exercise 11.1 — Path anatomy (●)

Using `pathlib`, build the path `projects/report/final.txt` with the `/`
operator, then print its name, its suffix, its stem, and its parent — one per
line.

??? success "Solution"

    ```python
    from pathlib import Path

    p = Path("projects") / "report" / "final.txt"
    print(p.name)
    print(p.suffix)
    print(p.stem)
    print(p.parent)
    ```

    A `Path` answers questions about its own structure without anything
    needing to exist on disk — it is an address, and `name`, `suffix`,
    `stem`, and `parent` just read different parts of that address.

### Exercise 11.2 — Write it, read it (●)

Write a file `haiku.txt` containing three lines of your choice, then read it
back **in one call** and print it. There should be no doubled blank lines in
the output.

??? success "Solution"

    ```python
    with open("haiku.txt", "w", encoding="utf-8") as f:
        f.write("an old silent pond\n")
        f.write("a frog jumps into the pond\n")
        f.write("splash - silence again\n")

    with open("haiku.txt", encoding="utf-8") as f:
        print(f.read(), end="")
    ```

    The file's own `"\n"` characters already end each line, so we pass
    `end=""` to stop `print` from adding one more.

### Exercise 11.3 — Word counter (●)

Create a file `speech.txt` with a few sentences spread over several lines,
then count the total number of words in it. Recall from
[Chapter 3](../ch03-functions/02-strings.md) that `text.split()` with no
arguments splits on any whitespace, including newlines.

??? success "Solution"

    ```python
    with open("speech.txt", "w", encoding="utf-8") as f:
        f.write("Four score and seven bugs ago\n")
        f.write("our programs brought forth\n")
        f.write("a new file format\n")

    with open("speech.txt", encoding="utf-8") as f:
        text = f.read()

    words = text.split()
    print("word count:", len(words))
    ```

    Prints `word count: 14`. Because `split()` treats newlines as
    whitespace, reading the whole file and splitting once is simpler than
    counting line by line.

### Exercise 11.4 — Line numberer (●●)

Editors show line numbers; so can you. Create `poem.txt` with four lines,
then print it with each line prefixed by its number and a colon, like
`1: ...`. Use `enumerate(f, start=1)` — `enumerate` works on file objects
just as it does on lists.

??? success "Solution"

    ```python
    with open("poem.txt", "w", encoding="utf-8") as f:
        f.write("roses are red\n")
        f.write("violets are blue\n")
        f.write("my code has no bugs\n")
        f.write("well... maybe a few\n")

    with open("poem.txt", encoding="utf-8") as f:
        for number, line in enumerate(f, start=1):
            print(f"{number}: {line.strip()}")
    ```

    Iterating the file yields lines; `enumerate` pairs each with a counter
    starting at 1. Stripping removes the trailing newline so the numbering
    stays single-spaced.

### Exercise 11.5 — Predict the output (●●)

Read this code carefully and write down exactly what it prints **before**
running it. Pay attention to the modes.

```text
with open("diary.txt", "w", encoding="utf-8") as f:
    f.write("Monday\n")
with open("diary.txt", "w", encoding="utf-8") as f:
    f.write("Tuesday\n")
with open("diary.txt", "a", encoding="utf-8") as f:
    f.write("Wednesday\n")
with open("diary.txt", encoding="utf-8") as f:
    print(f.read(), end="")
```

??? success "Solution"

    ```python
    with open("diary.txt", "w", encoding="utf-8") as f:
        f.write("Monday\n")
    with open("diary.txt", "w", encoding="utf-8") as f:
        f.write("Tuesday\n")
    with open("diary.txt", "a", encoding="utf-8") as f:
        f.write("Wednesday\n")
    with open("diary.txt", encoding="utf-8") as f:
        print(f.read(), end="")
    ```

    It prints `Tuesday` then `Wednesday`. The second `"w"` open erased
    Monday's entry before writing Tuesday's; the `"a"` open preserved
    Tuesday and added Wednesday at the end. If you predicted three days, the
    write mode's silent erasure is the lesson.

### Exercise 11.6 — Coldest and hottest (●●)

Create `temps.csv` where each line is `day,temperature` (no header). Read it
and print the minimum and maximum temperature. Remember: columns come out of
`split(",")` as strings.

??? success "Solution"

    ```python
    with open("temps.csv", "w", encoding="utf-8") as f:
        f.write("mon,18.5\ntue,21.0\nwed,16.2\nthu,24.8\nfri,19.9\n")

    temps = []
    with open("temps.csv", encoding="utf-8") as f:
        for line in f:
            day, value = line.strip().split(",")
            temps.append(float(value))

    print("coldest:", min(temps))
    print("hottest:", max(temps))
    ```

    Prints `coldest: 16.2` and `hottest: 24.8`. Collecting the converted
    numbers into a list first lets the built-ins `min` and `max` do the
    comparing for us.

### Exercise 11.7 — Log-file filter (●●)

Servers write logs mixing routine messages with errors. Create `server.log`
containing lines that start with either `INFO` or `ERROR`, then print **only**
the `ERROR` lines, and finish with a count of how many there were. The string
method `startswith` is your friend.

??? success "Solution"

    ```python
    with open("server.log", "w", encoding="utf-8") as f:
        f.write("INFO server started\n")
        f.write("ERROR disk almost full\n")
        f.write("INFO user logged in\n")
        f.write("ERROR connection lost\n")
        f.write("INFO nightly backup done\n")

    errors = 0
    with open("server.log", encoding="utf-8") as f:
        for line in f:
            if line.startswith("ERROR"):
                print(line.strip())
                errors += 1

    print("total errors:", errors)
    ```

    Prints the two `ERROR` lines and `total errors: 2`. Filter-while-reading
    is the standard shape for log processing: one pass, one `if`, constant
    memory no matter how huge the log grows.

### Exercise 11.8 — Grade report writer (●●●)

Combine everything: create `grades.csv` with a header row and three students'
quiz scores (as in the [worked example](02-read-write.md)), compute each
student's average, and **write** a new file `report.txt` with one line per
student in the form `Amara: 86.3`. Then read `report.txt` back and print it,
proving the report really landed on disk.

??? success "Solution"

    ```python
    with open("grades.csv", "w", encoding="utf-8") as f:
        f.write("name,quiz1,quiz2,quiz3\n")
        f.write("Amara,88,92,79\n")
        f.write("Ben,75,81,90\n")
        f.write("Chloe,95,89,94\n")

    with open("grades.csv", encoding="utf-8") as f_in:
        with open("report.txt", "w", encoding="utf-8") as f_out:
            f_in.readline()                       # skip the header
            for line in f_in:
                parts = line.strip().split(",")
                name = parts[0]
                scores = [int(s) for s in parts[1:]]
                f_out.write(f"{name}: {sum(scores) / len(scores):.1f}\n")

    with open("report.txt", encoding="utf-8") as f:
        print(f.read(), end="")
    ```

    Prints `Amara: 86.3`, `Ben: 82.0`, `Chloe: 92.7`. This is a complete
    read–transform–write pipeline: two files open at once (nesting the
    `with` statements is fine), strings converted to numbers on the way in,
    formatted text on the way out.
