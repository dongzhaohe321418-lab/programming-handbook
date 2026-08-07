# 1.1 The command line

Watch any experienced programmer work and you will notice a plain window full
of text that they keep coming back to. That window is the **terminal**, and
programmers live in it for a simple reason: it is the fastest, most precise
way to tell a computer exactly what to do. Menus and buttons offer you the
actions someone else thought of; the command line lets you *say* what you
want — and then repeat it, script it, or run it on a server that has no
screen at all. Python itself, Git, and nearly every tool in this handbook are
command-line programs, so learning to read a shell session is learning to
read the rest of the book.

## A window into the machine

Two words get mixed up constantly, so let us pin them down first:

- The **terminal** is the window program — the thing with the blinking
  cursor. (macOS: *Terminal* or *iTerm*; Windows: *Windows Terminal*;
  Linux: many, all similar.)
- The **shell** is the program *running inside* that window. It reads each
  line you type, carries it out, prints the result, and waits for the next
  line. Common shells are `bash` and `zsh` on macOS and Linux, and
  **PowerShell** on Windows.

A useful analogy: the terminal is the telephone handset; the shell is the
person on the other end who actually does things when you ask.

!!! info "Grey `console` blocks do not run in your browser"
    Shell sessions in this handbook appear in grey blocks like the ones
    below. They have **no Run button** — they are transcripts of a terminal,
    not Python. Lines starting with `$` are what *you type* (without the
    `$`); the other lines are the computer's replies. Later in this page
    there is a Python-powered simulator so you can practice the ideas right
    here.

## Anatomy of a prompt

When the shell is ready for a command, it prints a **prompt**:

```console
kim@laptop:~/projects$
```

Reading left to right:

- `kim` — the user who is logged in.
- `laptop` — the computer's name (matters when you are logged in to a remote
  server and need to know *which* machine will obey you).
- `~/projects` — the folder you are currently "standing in", called the
  **working directory**. `~` is shorthand for your home folder.
- `$` — "your turn". (zsh often shows `%`, PowerShell shows `>`; same idea.)

Every command you type runs *relative to* that working directory, which is
why the first three commands below are the ones you will use most.

## Finding your way: `pwd`, `ls`, `cd`

`pwd` (*print working directory*) answers "where am I?":

```console
$ pwd
/Users/kim/projects
```

`ls` (*list*) answers "what is here?":

```console
$ ls
docs    notes.txt    shopping.txt
```

Commands accept **flags** — extra options starting with `-` that change
behaviour. `ls -l` gives a *long* listing with sizes and dates; `ls -a`
lists *all* entries, including hidden ones (names starting with a dot):

```console
$ ls -l
total 16
drwxr-xr-x  3 kim  staff   96 Mar  4 10:02 docs
-rw-r--r--  1 kim  staff  120 Mar  4 09:58 notes.txt
-rw-r--r--  1 kim  staff  310 Mar  3 17:41 shopping.txt
$ ls -a
.    ..    .hidden-config    docs    notes.txt    shopping.txt
```

The `d` at the start of the `docs` line marks a directory; `.` means "this
folder" and `..` means "the folder above". Flags can be combined: `ls -la`.

`cd` (*change directory*) moves you. Its argument is a **path**, and paths
come in two flavours:

- An **absolute path** starts with `/` (the *root*, the top of the whole
  file system) and names the full route: `/Users/kim/projects`.
  It means the same thing no matter where you stand.
- A **relative path** starts from *where you are now*:
  `docs`, `../music`, `./notes.txt`. Two special names help:
  `..` is the parent folder, `~` is your home folder.

```console
$ pwd
/Users/kim
$ cd projects/handbook     # relative: starts from where you are
$ pwd
/Users/kim/projects/handbook
$ cd ..                    # up one level
$ pwd
/Users/kim/projects
$ cd /Users/kim/music      # absolute: starts with /
$ pwd
/Users/kim/music
$ cd ~                     # home, from anywhere
$ pwd
/Users/kim
```

Python can dissect paths the same way your head should. This block *does*
run — try it:

```python
from pathlib import PurePosixPath

p = PurePosixPath("/Users/kim/projects/handbook/notes.txt")
print("name:  ", p.name)
print("parent:", p.parent)
print("suffix:", p.suffix)
print("parts: ", p.parts)
```

The output shows exactly the pieces a shell user sees at a glance: the file
name at the end, everything before it as the parent folder, and the whole
path as a tuple of steps from the root `/` down.

## Making and moving things: `mkdir`, `cp`, `mv`, `rm`

Four commands cover creating, copying, renaming, and deleting:

```console
$ mkdir recipes                       # make a new (empty) directory
$ cp notes.txt recipes/pancakes.txt   # copy: the original stays put
$ mv shopping.txt groceries.txt       # mv renames ...
$ mv groceries.txt recipes/           # ... and also moves into a folder
$ ls recipes
groceries.txt    pancakes.txt
$ rm recipes/pancakes.txt             # delete a file
$ rm -r recipes                       # delete a folder and all its contents
```

!!! warning "`rm` is forever"
    `rm` does **not** move things to a Trash or Recycle Bin. The file is
    gone the moment you press ++enter++ — there is no undo, no
    confirmation, no safety net. Before any `rm`, and especially before
    `rm -r` (which deletes a folder *and everything inside it*), run `pwd`
    and `ls` first so you are certain about where you are and what you are
    about to remove.

## Looking inside files: `cat` and `less`

`cat` prints a file's entire contents into the terminal; `less` opens a
full-screen viewer for longer files (arrow keys scroll, ++q++ quits):

```console
$ cat notes.txt
buy flour
call the library
finish chapter 1
$ less server.log      # scroll with arrows / space, press q to quit
```

## Typing less: tab completion and history

The shell helps you far more than it first appears:

- **Tab completion.** Type the first letters of a file or command and press
  ++tab++ — the shell finishes the name for you. Press ++tab++ twice to see
  all possibilities. Experienced users almost never type a full filename.
- **History.** ++up++ recalls previous commands, ready to edit and re-run.
- **Panic button.** ++ctrl+c++ cancels the command that is currently
  running and gives you a fresh prompt.

!!! note "On Windows"
    Windows speaks the same language with an accent. Use **PowerShell**
    (inside the *Windows Terminal* app) rather than the ancient `cmd.exe`.
    The commands in this section — `pwd`, `ls`, `cd`, `mkdir`, `cp`, `mv`,
    `rm`, `cat` — all work in PowerShell as aliases of its own longer
    commands (`ls` is really `Get-ChildItem`), though some *flags* differ:
    hidden files, for instance, appear with `ls -Force` rather than
    `ls -a`. Paths use backslashes and drive letters
    (`C:\Users\kim\projects`), but PowerShell accepts forward slashes too,
    and `~` still means home. Python's `pathlib`, which you are about to
    meet, papers over the slash difference automatically.

## A shell simulator you can run

Shell fluency is really *path* fluency, and paths you can practice right
here. Python's `pathlib` module gives every program the same powers you just
saw — ask where it is, list folders, build paths. First, where are we?

```python
from pathlib import Path

cwd = Path.cwd()
print("You are here:", cwd)
print("One level up:", cwd.parent)
```

The answer depends on where the code runs: on your machine it would be the
folder you started Python from; in this browser it is a private, in-memory
file system that Pyodide creates just for you (deleting things here is
harmless — refresh the page and it is all reset).

That private file system starts nearly empty, so let us *build* something to
explore — a folder tree — and then list it, indented like a map:

```python
from pathlib import Path

base = Path("practice")
(base / "photos" / "cats").mkdir(parents=True, exist_ok=True)
(base / "notes").mkdir(parents=True, exist_ok=True)
(base / "notes" / "todo.txt").write_text("learn the shell\n")
(base / "photos" / "cats" / "whiskers.txt").write_text("a very good cat\n")

for path in sorted(base.rglob("*")):
    depth = len(path.relative_to(base).parts) - 1
    marker = "/" if path.is_dir() else ""
    print("    " * depth + path.name + marker)
```

```text
notes/
    todo.txt
photos/
    cats/
        whiskers.txt
```

`mkdir(parents=True)` is the shell's `mkdir -p` — create the whole chain of
folders at once — and `rglob("*")` visits everything below `base`, like a
recursive `ls`.

Now the real exercise: a **shell simulator**. The block below walks through a
scripted terminal session on the tree we just made — `pwd`, `ls`, `cd`, and
`cat`, implemented in a few lines of Python each. Run it, then *edit the
script list* at the bottom and re-run: try `cd ..`, try `ls` from other
folders, try `cd nowhere` to see the error path.

```python
# continues — builds on the practice/ tree from the previous block
root = base.resolve()
cwd = root

def run(command):
    global cwd
    name, _, arg = command.partition(" ")
    print("$", command)
    if name == "pwd":
        print(cwd.relative_to(root.parent))
    elif name == "ls":
        for entry in sorted(cwd.iterdir()):
            print(entry.name + ("/" if entry.is_dir() else ""))
    elif name == "cd":
        target = (cwd / arg).resolve()
        if target.is_dir():
            cwd = target
        else:
            print(f"cd: no such file or directory: {arg}")
    elif name == "cat":
        print((cwd / arg).read_text(), end="")

for command in ["pwd", "ls", "cd photos/cats", "pwd", "ls",
                "cd ../../notes", "cat todo.txt"]:
    run(command)
```

```text
$ pwd
practice
$ ls
notes/
photos/
$ cd photos/cats
$ pwd
practice/photos/cats
$ ls
whiskers.txt
$ cd ../../notes
$ cat todo.txt
learn the shell
```

Notice `cd ../../notes`: two `..` steps climb from `cats` up through
`photos` back to `practice`, then descend into `notes` — exactly the mental
arithmetic a relative path asks of you. The `.resolve()` call is what turns
that dotted route into a clean absolute path.

One more thing worth seeing on purpose: what happens when a path is wrong.
The shell says `No such file or directory`; Python raises an exception that
says the very same thing.

```python
# raises FileNotFoundError
from pathlib import Path

Path("does-not-exist.txt").read_text()
```

You will learn to *read* messages like this in
[Chapter 10](../ch10-exceptions/01-cli-programs.md); for now the takeaway is
that "file not found" errors — in the shell or in Python — usually mean
*you are not in the directory you think you are in*. `pwd` first, then look
again. Paths return in force in
[Chapter 11 · Files](../ch11-files/01-paths.md).

!!! warning "Common mistakes"
    - **Typing the `$`.** The `$` (or `%`, or `>`) is the shell's prompt,
      not part of the command. Type what comes *after* it.
    - **Spaces in names.** `cd My Documents` looks like the command `cd`
      with *two* arguments. Quote it (`cd "My Documents"`) or let ++tab++
      completion escape it for you.
    - **Being in the wrong directory.** `python notes.py` failing with
      "No such file or directory" almost never means the file vanished — it
      means your working directory is not where the file lives. `pwd` and
      `ls` before you panic.
    - **Reaching for `rm -r` casually.** It deletes whole folder trees,
      silently and permanently. Read the path twice; there is no undo.

## Check your understanding

1. Your working directory is `/Users/kim/projects`. Where are you after
   `cd ../music`? And after `cd ~`?

    ??? success "Answer"
        `cd ../music` goes *up* one level to `/Users/kim`, then *down* into
        `music`: you end at `/Users/kim/music`. `cd ~` jumps straight to
        the home folder, `/Users/kim`, no matter where you started.

2. What is the difference between the terminal and the shell?

    ??? success "Answer"
        The terminal is the window program that displays text and takes
        keystrokes; the shell is the command interpreter running inside it
        (bash, zsh, PowerShell) that actually reads and executes your
        commands. You can swap either independently of the other.

3. `ls` shows nothing suspicious, but a friend says the folder contains a
   configuration file. What command reveals it, and why was it invisible?

    ??? success "Answer"
        `ls -a`. Files whose names begin with a dot (like `.hidden-config`)
        are *hidden* by convention, and plain `ls` skips them; the `-a`
        (all) flag lists them.
