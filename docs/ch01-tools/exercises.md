# Exercises

## The chapter in brief

- The **terminal** is the window; the **shell** (bash, zsh, PowerShell) is
  the program inside it that reads and runs your commands
  ([1.1](01-command-line.md)).
- A prompt like `kim@laptop:~/projects$` names the user, the machine, and the
  **working directory** every command runs relative to.
- `pwd`, `ls`, and `cd` answer *where am I*, *what is here*, and *take me
  elsewhere* — and `ls -a` reveals the dot-files `ls` hides.
- **Absolute paths** start at `/` and mean the same thing anywhere;
  **relative paths** start from where you stand, with `..` for up and `~` for
  home.
- `mkdir`, `cp`, `mv`, and `rm` create, copy, rename, and delete — and `rm`
  has no undo, no Trash, and no confirmation.
- Python installs from python.org, and `python --version` confirms the shell
  can find it ([1.2](02-python-setup.md)).
- The same program runs four ways — the REPL for questions, a script file for
  keeping, a notebook for narrative, and this site's Run button for reading.
- A **virtual environment** gives each project its own private set of
  packages, so one project's upgrade never breaks another.
- **Git** stores your project as a chain of **commits** — snapshots with an
  author, a date, a message, and a content-derived hash ID
  ([1.3](03-git.md)).
- Work flows through areas: working directory → staging area (index) → local
  repository → remote. `git add` and `git commit` move it forward; `git
  restore` and `git reset` move it back, each changing a specific area.
- A file is **untracked**, **modified**, or **staged** — and can be *both*
  staged and modified at once, which is why a commit captures the version you
  `add`-ed, not the one on disk.
- `git log` shows the history; `git diff` shows working-vs-index changes and
  `git diff --staged` shows index-vs-`HEAD`, in the unified-diff format you
  will read for the rest of your career.
- The fourth area is a **remote** ([1.4](04-git-remotes.md)): `git push`
  uploads, `git fetch` downloads into `origin/main` only, and `git pull` =
  `fetch` + merge into your branch.
- **GitHub** hosts copies of repositories; nothing you commit locally is
  backed up or shared until you `git push`.

### Key terms

| Term | What it means |
| --- | --- |
| [**shell**](../concept-index.md#s) | The program that reads your typed commands and carries them out |
| [**command line**](../concept-index.md#c) | Talking to the computer by typing commands rather than clicking |
| [**working directory**](../concept-index.md#w) | The folder you are "standing in"; every relative path starts here |
| [**path**](../concept-index.md#p) | A route to a file — absolute from `/`, or relative from where you are |
| **flag** | An option after a command that changes its behaviour, like `ls -a` |
| **REPL** | Python's interactive prompt: read a line, evaluate, print, repeat |
| **virtual environment** | A private per-project package set, created with `python -m venv` |
| [**Git**](../concept-index.md#g) | The version-control tool that stores your project's full history |
| [**commit**](../concept-index.md#c) | One snapshot of the whole project, with a message and a hash ID |
| [**staging area**](../concept-index.md#s) | The drafting table (the *index*) where you assemble the *next* commit |
| [**repository**](../concept-index.md#r) | The project plus its history, kept in the hidden `.git` folder |
| **HEAD** | The commit you are currently on — the last page of the album |
| **remote** | A full copy of the repository on another machine, nicknamed `origin` by default |
| **GitHub** | A website that hosts repositories — Git works fine without it |

Tools become skills only through use. Work through these in order — they
start with pure path-thinking and end with you building a miniature version
control system. Attempt each one before opening the solution; being wrong
first is the fastest way to be right later.

!!! note "About the solution code"
    Some solutions use `def` (writing functions, Chapter 3) and `for` loops
    (Chapter 6) before this book has formally introduced them. Treat them
    as a preview: read the solutions for the *ideas*, and come back after
    those chapters if the syntax looks alien.

### Exercise 1.1 — Where do you end up? (●)

Your working directory is `/Users/kim/projects`, and your home folder is
`/Users/kim`. *Without running anything*, predict the working directory
after each of these commands (each starts fresh from `/Users/kim/projects`):

1. `cd ..`
2. `cd ../music`
3. `cd ~/Desktop`
4. `cd /`
5. `cd ./notes`

??? success "Solution"
    Python can check your predictions — `posixpath.normpath` collapses `..`
    and `.` exactly the way a shell does:

    ```python
    import posixpath

    home = "/Users/kim"
    start = "/Users/kim/projects"

    def cd(cwd, target):
        if target.startswith("~"):
            target = home + target[1:]
        if not target.startswith("/"):
            target = posixpath.join(cwd, target)
        return posixpath.normpath(target)

    for command in ["..", "../music", "~/Desktop", "/", "./notes"]:
        print(f"cd {command:<10} ->", cd(start, command))
    ```

    The answers: `/Users/kim`, `/Users/kim/music`, `/Users/kim/Desktop`,
    `/`, and `/Users/kim/projects/notes`. The rule being exercised:
    absolute paths (starting `/`) and home paths (starting `~`) ignore
    where you are; everything else starts from the working directory, with
    `..` meaning "up one" and `.` meaning "right here".

### Exercise 1.2 — Match the command to the job (●)

Match each command (left) to what it does (right). One description is left
over — which command from Section [1.1](01-command-line.md) does it belong
to?

| Command | | Job |
| --- | --- | --- |
| `pwd` | | A. copy a file, keeping the original |
| `ls -a` | | B. delete a file permanently |
| `mkdir drafts` | | C. print the current working directory |
| `cp a.txt b.txt` | | D. rename or move a file |
| `mv a.txt b.txt` | | E. list everything, including hidden files |
| `rm a.txt` | | F. create a new directory |
| | | G. print a file's contents |

??? success "Solution"
    ```python
    matches = {
        "pwd": "C. print the current working directory",
        "ls -a": "E. list everything, including hidden files",
        "mkdir drafts": "F. create a new directory",
        "cp a.txt b.txt": "A. copy a file, keeping the original",
        "mv a.txt b.txt": "D. rename or move a file",
        "rm a.txt": "B. delete a file permanently",
        "cat a.txt": "G. print a file's contents (the leftover)",
    }
    for command, job in matches.items():
        print(f"{command:<15} -> {job}")
    ```

    The leftover description G belongs to `cat`. Worth repeating: B says
    *permanently* — `rm` has no trash can.

### Exercise 1.3 — Predict the output (●)

Read this code and write down the four lines it will print *before* you run
it. Then run it and check.

```python
from pathlib import PurePosixPath

p = PurePosixPath("/home/ana/code/game/main.py")
print(p.name)
print(p.suffix)
print(p.parent.name)
print(len(p.parts))
```

??? success "Solution"
    ```python
    from pathlib import PurePosixPath

    p = PurePosixPath("/home/ana/code/game/main.py")
    print(p.name)         # main.py  - the last component
    print(p.suffix)       # .py      - the extension, dot included
    print(p.parent.name)  # game     - last component of the parent path
    print(len(p.parts))   # 6        - ('/', 'home', 'ana', 'code', 'game', 'main.py')
    ```

    The one that surprises most people is `6`: the root `/` counts as a
    part, so four folders plus a file name plus the root makes six.

### Exercise 1.4 — Which way would you run it? (●)

For each situation, pick the best of the four ways to run Python from
Section [1.2](02-python-setup.md) — REPL, script file, notebook, or this
site's Run button — and say why in one sentence.

1. Checking whether `round(2.5)` rounds up or down.
2. A program that renames 300 photo files, to be reused every month.
3. Exploring a semester's worth of weather measurements, mixing plots with
   notes for your write-up.
4. Working through this handbook on a library computer where you cannot
   install anything.

??? success "Solution"
    ```python
    answers = [
        ("1", "REPL", "one throwaway question, instant answer"),
        ("2", "script file", "a keepable, rerunnable program"),
        ("3", "notebook", "code, plots, and prose in one document"),
        ("4", "Run button", "real Python with zero installation"),
    ]
    for number, way, reason in answers:
        print(f"{number}. {way:<12} - {reason}")
    ```

    The tool follows the job: conversations in the REPL, programs in
    files, narratives in notebooks, and the browser when installing is not
    an option. (For the curious: `round(2.5)` is `2` — Chapter 5 explains
    that surprise.)

### Exercise 1.5 — Write your own `ls` (●●)

Using `pathlib`, build a small folder tree (a few files and two
sub-folders), then write a function `list_dir(path)` that prints one entry
per line — **directories first**, each with a trailing `/`, both groups in
alphabetical order. This mirrors how many file browsers sort.

??? success "Solution"
    ```python
    from pathlib import Path

    base = Path("ls-practice")
    (base / "b-folder").mkdir(parents=True, exist_ok=True)
    (base / "a-folder").mkdir(parents=True, exist_ok=True)
    (base / "zebra.txt").write_text("z")
    (base / "apple.txt").write_text("a")

    def list_dir(path):
        entries = sorted(Path(path).iterdir(),
                         key=lambda entry: (not entry.is_dir(), entry.name))
        for entry in entries:
            print(entry.name + ("/" if entry.is_dir() else ""))

    list_dir(base)
    ```

    The sort key is the trick: each entry becomes a pair
    `(not is_dir, name)`. Directories give `(False, name)` and files give
    `(True, name)`, and since `False` sorts before `True`, directories come
    first — alphabetical within each group.

### Exercise 1.6 — The `cd` machine (●●)

Write a function `follow(start, commands)` that takes a starting absolute
path and a list of `cd` targets, applies them in order, and returns the
final working directory. It must handle relative paths, absolute paths,
`..`, and `~` (assume home is `/home/ana`). Test it with:

```text
start:    /home/ana
commands: code, game, .., ../music, /tmp, ~
```

Predict the answer before you run your solution.

??? success "Solution"
    ```python
    import posixpath

    HOME = "/home/ana"

    def follow(start, commands):
        cwd = start
        for target in commands:
            if target.startswith("~"):
                target = HOME + target[1:]
            if not target.startswith("/"):
                target = posixpath.join(cwd, target)
            cwd = posixpath.normpath(target)
        return cwd

    trail = ["code", "game", "..", "../music", "/tmp", "~"]
    print(follow("/home/ana", trail))
    ```

    Step by step: `/home/ana` → `/home/ana/code` → `/home/ana/code/game` →
    `/home/ana/code` → `/home/ana/music` → `/tmp` → `/home/ana`. The final
    answer is `/home/ana`: the absolute jump to `/tmp` discarded everything
    before it, and `~` discarded that. Only the *last* absolute or home
    jump ever matters.

### Exercise 1.7 — Design a commit history (●●)

You are building a personal website. Over one week you: create the
homepage; add a photo gallery; fix a broken link a friend spotted on the
gallery page; and add a contact form. Write, on paper, the Git commands for
the *first* commit (from `git init` onward) and then the commit messages
for all four snapshots. Rules: one logical change per commit, and messages
that finish the sentence "This commit will …".

??? success "Solution"
    The first commit takes three commands, and each later change repeats
    the add/commit pair:

    ```console
    $ git init
    $ git add index.html
    $ git commit -m "Add homepage"
    ```

    A tidy history, as `git log --oneline` would show it (newest first):

    ```python
    log = [
        ("e91f3ab", "Add contact form"),
        ("57d20c4", "Fix broken link on gallery page"),
        ("b3a9e01", "Add photo gallery"),
        ("a1c8f52", "Add homepage"),
    ]
    print("$ git log --oneline")
    for commit_id, message in log:
        print(commit_id, message)
    ```

    Two things to check against your version: the bug fix is its *own*
    commit (not folded into "Add contact form"), and every message
    completes "This commit will …" — which is why "Add homepage" beats
    "changed some stuff" or "monday work".

### Exercise 1.8 — Build a mini version control system (●●●)

Time to demystify Git by rebuilding its core in about thirty lines. Write
three functions around a list called `snapshots`:

- `commit(message, content)` — append the snapshot;
- `show_log()` — print numbered messages, **newest first**, like `git log`;
- `diff(a, b)` — print a unified diff between two snapshots (the `difflib`
  module from Section [1.3](03-git.md) does the hard part).

Then commit three versions of a shopping list and print the log and the
diff from the first version to the last.

??? success "Solution"
    ```python
    import difflib

    snapshots = []   # each entry: (message, content)

    def commit(message, content):
        snapshots.append((message, content))

    def show_log():
        for number in range(len(snapshots) - 1, -1, -1):
            print(f"[{number}] {snapshots[number][0]}")

    def diff(a, b):
        old = snapshots[a][1].splitlines()
        new = snapshots[b][1].splitlines()
        labels = f"version {a}", f"version {b}"
        for line in difflib.unified_diff(old, new, *labels, lineterm=""):
            print(line)

    commit("Add shopping list", "eggs\nmilk\n")
    commit("Add bread", "eggs\nmilk\nbread\n")
    commit("Remove milk", "eggs\nbread\n")

    show_log()
    print()
    diff(0, 2)
    ```

    Each "commit" stores a full snapshot plus a message — exactly Git's
    mental model — and `diff` recomputes changes between any two snapshots
    on demand. Real Git adds hashes (Exercise: bolt on the `commit_id`
    function from Section [1.3](03-git.md)), parents, branches, and very
    clever storage, but the idea in these thirty lines is the same one
    underneath all of it.
