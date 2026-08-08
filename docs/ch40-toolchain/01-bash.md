# 40.1 Bash scripting

[Section 1.1](../ch01-tools/01-command-line.md) taught you to *type* commands.
This page teaches you to *save* them. The moment a sequence of commands is
worth running twice, it is worth putting in a file — and a file full of shell
commands is a program, with variables, conditionals, loops, and functions,
written in a language whose one job is to start other programs and wire their
inputs and outputs together. Bash is not elegant. It has a famous trap in its
most basic feature, it is easy to write badly, and every experienced engineer
has a story about a script that deleted the wrong directory. It is also on
every server you will ever log into, it is what your build pipeline runs, and
being able to read forty lines of it is the difference between understanding
a deployment and guessing at one.

!!! info "Nothing on this page has a Run button — except the models"
    Bash cannot execute in a browser, so shell sessions appear in grey
    `console` blocks (`$` is the prompt, don't type it) and script files in
    `text` blocks. But every idea on this page — word splitting, exit-code
    logic, pipelines — is modelled in a **runnable Python block** so you can
    watch the mechanism work. Run those, then go type the real thing in a
    terminal.

## From typing commands to writing a program

A shell script is a text file whose lines are commands. Three things turn it
into something you can run by name.

```text
#!/usr/bin/env bash
# backup.sh — copy today's notes into the archive folder

echo "Backing up notes..."
mkdir -p archive
cp notes.txt archive/notes-$(date +%F).txt
echo "Done."
```

### 1. The shebang line

The first line is the **shebang** (`#!`), and it is read by the operating
system, not by bash: it says which interpreter should run the rest of the
file.

`#!/usr/bin/env bash` asks the environment to find whichever `bash` is first on
the user's `PATH`, which is more portable than hard-coding `#!/bin/bash` — on
macOS, for instance, `/bin/bash` is an ancient version while a modern one lives
elsewhere.

### 2. The executable bit

A file is not runnable just because it contains commands. The file system
stores a permission flag that says "this may be executed", and `chmod +x` sets
it ([Section 40.2](02-ssh-remote.md) decodes those permission bits in detail):

```console
$ ls -l backup.sh
-rw-r--r--  1 kim  staff  164 Mar  4 09:12 backup.sh
$ chmod +x backup.sh
$ ls -l backup.sh
-rwxr-xr-x  1 kim  staff  164 Mar  4 09:12 backup.sh
```

### 3. Knowing how to invoke it

Typing `backup.sh` alone fails, because the shell only searches the
directories listed in `PATH` — and the current directory is deliberately not
one of them. Say where the file is:

```console
$ backup.sh
bash: backup.sh: command not found
$ ./backup.sh          # "the backup.sh in this directory"
Backing up notes...
Done.
$ bash backup.sh       # also works, and ignores the executable bit entirely
Backing up notes...
Done.
```

## Variables, and the bug that defines the language

Assignment has no spaces around the `=`, and no `$`. Reading the variable
back needs a `$`:

```text
name="Ada"
count=3
greeting="Hello, $name"        # expansion happens inside double quotes
literal='Hello, $name'         # single quotes expand nothing

echo "$greeting"               # Hello, Ada
echo "$literal"                # Hello, $name
echo "${name}s notebook"       # braces where the name would run into text
```

`name = "Ada"` with spaces is a *different command*: bash reads `name` as a
program to run with the arguments `=` and `"Ada"`. That is a beginner's first
bash error, and it is a good introduction to how the language thinks — **every
line is a command line, split into words**.

### Word splitting, the bug that defines bash

That splitting is the source of **the** bash bug. When bash expands `$var`, it
substitutes the text and *then* splits the result on whitespace into separate
arguments. If the value contains a space, one argument becomes two:

```text
file="my notes.txt"

rm $file          # BUG: runs  rm "my" "notes.txt"  -- two wrong files
rm "$file"        # correct: runs  rm "my notes.txt"  -- one right file
```

Python's `shlex` module applies the same splitting rules, so you can watch
the bug happen for real:

```python
import shlex

# Bash splits a command line into words BEFORE running anything, and an
# expanded variable is split too. shlex.split follows the same rules.
file = "my notes.txt"          # imagine: file="my notes.txt" in a script

broken = f"rm {file}"          # what bash sees for:  rm $file
fixed = f'rm "{file}"'         # what bash sees for:  rm "$file"

print('rm $file    ->', shlex.split(broken))
print('rm "$file"  ->', shlex.split(fixed))
print()

for label, line in [("unquoted", broken), ("quoted", fixed)]:
    words = shlex.split(line)
    print(f"{label:>8}: rm receives {len(words) - 1} argument(s): {words[1:]}")

print()
# The same failure with an EMPTY variable, this time inside a test:
file = ""                      # imagine: file="" because a lookup failed
print('[ -f $file ]   ->', shlex.split(f"[ -f {file} ]"))
print('[ -f "$file" ] ->', shlex.split(f'[ -f "{file}" ]'))
```

```text
rm $file    -> ['rm', 'my', 'notes.txt']
rm "$file"  -> ['rm', 'my notes.txt']

unquoted: rm receives 2 argument(s): ['my', 'notes.txt']
  quoted: rm receives 1 argument(s): ['my notes.txt']

[ -f $file ]   -> ['[', '-f', ']']
[ -f "$file" ] -> ['[', '-f', '', ']']
```

Look hard at the last two lines. With an empty unquoted variable the test
loses an argument entirely — `[ -f ]` is not "test an empty filename", it is
a *differently shaped command*, and old-style `[ ]` happily reports success
for it. The quoted version keeps the empty string as a real argument and
correctly reports failure.

**Quoting is the one bash habit that prevents most bash bugs.** It is worth
more than everything else on this page combined:

!!! tip "Quote every expansion"
    Write `"$var"`, `"$1"`, `"$(command)"`, `"${array[@]}"` — always, unless
    you have a specific reason to want splitting. Filenames with spaces are
    normal on every desktop operating system, and a script that breaks on
    `My Documents` will break in production.

## Command substitution and arithmetic

`$(command)` runs the command and substitutes its **output** into the line.
It is how a script asks the system a question:

```text
today=$(date +%F)                    # 2024-03-04
here=$(pwd)
branch=$(git rev-parse --abbrev-ref HEAD)
count=$(grep -c ERROR app.log)       # -c counts matching lines

echo "On $branch at $here there were $count errors on $today"
```

The older backtick form `` `command` `` means the same thing but cannot be
nested and is easy to misread; use `$( )`. Arithmetic gets its own syntax,
because bash variables are strings by default:

```text
count=$((count + 1))         # arithmetic expansion: $(( ))
if (( count > 10 )); then    # arithmetic context: no $ needed on names
    echo "too many"
fi
```

## Exit codes: how the shell knows what failed

Every command returns an **exit status**: an integer where `0` means success
and anything from 1 to 255 means some kind of failure. It is not printed —
the shell stores it in the special variable `$?`. This is the single most
important concept in shell scripting, because *all* of the control flow is
built on it.

```console
$ grep ERROR app.log
2024-03-04 10:31:03 ERROR upstream timeout
$ echo $?
0
$ grep NOTHING app.log
$ echo $?
1
```

Three operators join commands, and two of them look at that status:

| Written | Meaning |
|---|---|
| `a ; b` | run `a`, then run `b` — whatever `a` returned |
| `a && b` | run `b` **only if** `a` succeeded (status 0) |
| <code>a &#124;&#124; b</code> | run `b` **only if** `a` failed (status non-zero) |

Which gives the two idioms you will see everywhere: `make && ./run` ("build,
and only if that worked, run it") and `command || echo "failed"` ("do this,
or complain"). Here is the logic as a runnable model:

```python
# A model of the shell's exit-status logic. Each "command" is just a name
# and the status it will return.
EXIT_STATUS = {
    "make": 0,          # success
    "run-tests": 1,     # failure: one test failed
    "deploy": 0,
    "alert-team": 0,
}


def run(name):
    status = EXIT_STATUS[name]
    print(f"    running {name:<10} -> exit {status}")
    return status


def run_chain(chain):
    """chain: [name, op, name, op, name, ...] with op in ';', '&&', '||'."""
    print("$ " + " ".join(chain))
    status = run(chain[0])
    i = 1
    while i < len(chain):
        op, name = chain[i], chain[i + 1]
        if op == "&&" and status != 0:
            print(f"    skipping {name:<9} (previous command failed)")
        elif op == "||" and status == 0:
            print(f"    skipping {name:<9} (previous command succeeded)")
        else:
            status = run(name)
        i += 2
    print(f"    $? = {status}\n")
    return status


run_chain(["make", "&&", "run-tests", "&&", "deploy"])
run_chain(["make", "&&", "run-tests", "||", "alert-team"])
run_chain(["make", ";", "run-tests", ";", "deploy"])
```

```text
$ make && run-tests && deploy
    running make       -> exit 0
    running run-tests  -> exit 1
    skipping deploy    (previous command failed)
    $? = 1

$ make && run-tests || alert-team
    running make       -> exit 0
    running run-tests  -> exit 1
    running alert-team -> exit 0
    $? = 0

$ make ; run-tests ; deploy
    running make       -> exit 0
    running run-tests  -> exit 1
    running deploy     -> exit 0
    $? = 0
```

The second chain deserves a second look: the *chain* succeeds (`$? = 0`)
even though the tests failed, because `alert-team` ran and returned 0.

That is exactly how a `|| echo failed` line can accidentally hide a failure
from a CI system that only checks the final status.

Your own script sets its status with `exit`:

```text
if [[ ! -f config.yml ]]; then
    echo "config.yml is missing" >&2      # error messages go to stderr
    exit 1
fi
```

## Conditionals: `if`, `test`, and `[[ ]]`

`if` does not test a boolean; it runs a command and branches on its exit
status. The thing that *looks* like a condition is a command called `test`,
whose other name is `[`:

```text
if [ -f config.yml ]; then           # POSIX test, works in every shell
    echo "found it"
elif [ -d config/ ]; then
    echo "found a config directory"
else
    echo "nothing" >&2
    exit 1
fi
```

Bash adds `[[ ... ]]`, which is part of the language rather than a command.
Prefer it: it does not word-split its arguments (so an unquoted empty
variable cannot change the shape of the test), and it supports pattern and
regex matching.

| Test | True when |
|---|---|
| `[[ -f path ]]` | `path` exists and is a regular file |
| `[[ -d path ]]` | `path` exists and is a directory |
| `[[ -e path ]]` | `path` exists (file, directory, anything) |
| `[[ -z "$s" ]]` / `[[ -n "$s" ]]` | `$s` is empty / is non-empty |
| `[[ "$a" == "$b" ]]` | strings equal (`!=` for not equal) |
| `[[ "$a" == *.log ]]` | `$a` matches the glob pattern |
| `[[ "$a" =~ ^v[0-9]+$ ]]` | `$a` matches the regex ([Chapter 41](../ch41-regex/01-fundamentals.md)) |
| `[[ $n -lt 10 ]]` | integer comparison: `-eq -ne -lt -le -gt -ge` |
| `[[ -f a && -f b ]]` | both — inside `[[ ]]`, `&&` and <code>&#124;&#124;</code> work directly |

The integer operators are spelled with letters because in the older `[ ]` test
`<` and `>` would be read as redirection. Inside `[[ ]]` they do work — but
they compare *text*, so `[[ 10 > 9 ]]` is **false**, because `"10"` sorts
before `"9"`. Use `-gt`/`-lt` for numbers; that mix-up is a real and quiet
source of wrong answers.

## Loops

### `for` — over a list of words

The list is usually a glob, an array, or the output of a command:

```text
for file in *.log; do
    echo "== $file =="
    tail -n 3 "$file"
done

for i in {1..5}; do echo "attempt $i"; done

for host in web-01 web-02 web-03; do
    ssh "$host" 'uptime'
done
```

### `while` — as long as a command succeeds

The canonical use is reading a file line by line, and it has a canonical
spelling worth memorising:

```text
while IFS= read -r line; do
    echo "line: $line"
done < input.txt
```

`IFS=` stops leading and trailing whitespace being stripped, and `-r` stops
backslashes being interpreted as escapes. Without both, `read` quietly
mangles data.

### `case` — the shell's `match` statement

It matches glob patterns, not just literals:

```text
case "$1" in
    build)        make ;;
    test)         make test ;;
    deploy)       ./deploy.sh ;;
    *.log)        less "$1" ;;          # patterns, not just literals
    "")           echo "usage: $0 {build|test|deploy}" >&2; exit 2 ;;
    *)            echo "unknown command: $1" >&2; exit 2 ;;
esac
```

Each branch ends with `;;`, and `*)` is the default. Note there is no
fall-through by default — unlike Java's `switch`, one branch runs and the
`case` ends.

## Functions, arguments, and here-documents

### Functions, and why `local` matters

A function is a named block. Inside it, `$1`, `$2`, … are *its* arguments,
`$@` is all of them, and `local` keeps a variable from leaking into the rest
of the script (bash variables are global by default — this bites people):

```text
log() {
    local level="$1"; shift               # shift drops $1, renumbering the rest
    echo "[$(date +%T)] $level: $*" >&2
}

require_file() {
    local path="$1"
    if [[ ! -f "$path" ]]; then
        log ERROR "missing file: $path"
        return 1                          # a status, not a value
    fi
}

log INFO "starting"
require_file config.yml || exit 1
result=$(basename "$PWD")                 # capture OUTPUT with $( )
log INFO "project is $result"
```

**A shell function returns a *status*, not a value.** To hand data back, print
it and let the caller capture it with `$( )`.

### The script's own arguments

The script itself has the same positional parameters:

| Variable | Meaning |
|---|---|
| `$0` | the script's own name |
| `$1`, `$2`, … | first, second argument |
| `$#` | how many arguments were passed |
| `"$@"` | all arguments, each kept as one word — almost always what you want |
| `$*` | all arguments joined into a single word |
| `${1:-default}` | `$1`, or `default` if it is unset or empty |

### Here-documents

A **here-document** feeds a literal block of text to a command's standard
input — the readable way to write usage messages, SQL, or config files:

```text
usage() {
    cat <<'EOF'
usage: deploy.sh [-n] ENVIRONMENT

  -n    dry run: print the commands without running them

Environments: staging, production
EOF
}
```

`<<'EOF'` with quotes means "no expansion at all" — `$1` inside stays
literal. Plain `<<EOF` expands variables and `$( )` inside the block, which
is what you want when generating a config file from values.

## Redirection, file descriptors, and pipes

### The three streams every process starts with

They are identified by small integers called **file descriptors**:

| FD | Name | Default |
|---|---|---|
| 0 | standard input (`stdin`) | your keyboard |
| 1 | standard output (`stdout`) | your terminal |
| 2 | standard error (`stderr`) | your terminal |

### Redirecting them

Streams 1 and 2 both land on your screen, which hides the fact that they are
separate channels — until you redirect one of them:

```console
$ ./build.sh > build.log            # stdout to a file (truncating it first)
error: missing header stdio.h       # ... stderr still comes to the screen
$ ./build.sh >> build.log           # append instead of truncate
$ ./build.sh 2> errors.log          # stderr only
$ ./build.sh > build.log 2>&1       # stderr joins wherever stdout is going
$ ./build.sh &> build.log           # bash shorthand for the same thing
$ ./build.sh > /dev/null 2>&1       # discard everything: the "quiet" idiom
$ ./build.sh 2>&1 | tee build.log   # to the screen AND a file
```

### `2>&1`, and why the order matters

`2>&1` reads as "make descriptor 2 point at whatever descriptor 1 currently
points at". Redirections are applied strictly left to right, so:

- `> file 2>&1` — stdout goes to the file, then stderr is aimed at wherever
  stdout goes. **Both end up in the file.**
- `2>&1 > file` — stderr is aimed at wherever stdout goes *right now*, which
  is still the terminal, and only then is stdout moved. **Errors stay on
  screen.**

That reversal is a classic interview question and a classic real-world bug.

### The pipe

The `|` operator connects one process's descriptor 1 directly to the next
process's descriptor 0, with no temporary file. That is the machinery behind
[Section 39.3](../ch39-streams/03-pipelines.md)'s streaming and backpressure
discussion — and the reason `grep pattern huge.log | head -3` finishes
instantly on a file bigger than memory.

## `set -euo pipefail`, line by line

By default, bash is dangerously forgiving: a failing command does not stop
the script, and a misspelled variable expands to the empty string. A script
that deletes `"$TARGET_DIR"/*` where `TARGET_DIR` was never set will happily
delete `/*`.

Three settings fix most of that, and one line at the top of every serious
script turns them on:

```text
#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'
```

| Setting | Long name | What it does |
|---|---|---|
| `set -e` | `errexit` | exit the whole script as soon as any command returns non-zero |
| `set -u` | `nounset` | using an unset variable is an error, not an empty string |
| `set -o pipefail` | — | a pipeline fails if **any** stage fails, not just the last one |
| `IFS=$'\n\t'` | — | split words on newlines and tabs only, not spaces |

Why each one earns its place, in the order they appear on the line:

1. **`-e` stops the script at the first failure.** It turns "the copy failed
   but we carried on and deployed anyway" into an immediate stop. Without it,
   every single command needs its own `|| exit 1`.
2. **`-u` catches typos.** `rm -rf "$BUILD_DIR/"` where the variable is
   actually called `BUILDDIR` becomes an error instead of `rm -rf /`.
3. **`pipefail` stops a pipeline hiding a failure.** A pipeline's exit status
   is normally the status of its *last* command only, so
   `curl -f https://example.com/data | wc -l` reports success whenever `wc`
   succeeds — which it always does, even when `curl` failed and fed it
   nothing. With `pipefail` the pipeline reports the rightmost non-zero
   status, and the failure surfaces.
4. **`IFS=$'\n\t'` is optional but common.** It stops unquoted expansions
   being split on spaces, which makes filenames with spaces survive a little
   longer. It is a seatbelt, not a substitute for quoting.

!!! warning "`set -e` is not as strong as it looks"
    Be honest about its limits, because people over-trust it. `set -e` does
    **not** trigger for a command that is part of a condition
    (`if failing_command; then`), for any command in a `&&`/`||` chain except
    the last, for a command negated with `!`, or in some subshell and
    function contexts. It also does not fire on an *unset* variable — that is
    `-u`'s job. Treat it as a large improvement, not a guarantee, and still
    check the statuses that matter.

A companion habit is `trap`, which runs cleanup when the script exits for any
reason, including an error:

```text
work_dir=$(mktemp -d)
trap 'rm -rf "$work_dir"' EXIT       # runs on success, failure, or Ctrl-C
```

## The text toolkit

These are the commands you will combine with pipes. One canonical example
each is enough to recognise them; the full card is in
[Appendix F](../appendix/F-toolchain-reference.md).

| Command | One-line example | What it does |
|---|---|---|
| `grep` | `grep -n ERROR app.log` | print matching lines, with line numbers |
| `grep -r` | `grep -rl TODO src/` | search a tree; `-l` lists filenames only |
| `sed` | `sed 's/localhost/prod-db/g' config.ini` | stream-edit: substitute text |
| `awk` | `awk -F, '$3 > 100 {print $1}' sales.csv` | field-aware filter and report |
| `cut` | `cut -d, -f1,3 sales.csv` | keep chosen fields of each line |
| `sort` | `sort -k2 -rn scores.txt` | sort by field 2, numeric, descending |
| `uniq` | <code>sort names.txt &#124; uniq -c</code> | collapse **adjacent** duplicates, count them |
| `wc` | `wc -l *.py` | count lines (`-w` words, `-c` bytes) |
| `find` | `find . -name '*.py' -newer Makefile` | walk a tree, filter by name/time/size |
| `xargs` | <code>find . -name '*.py' -print0 &#124; xargs -0 wc -l</code> | turn input lines into arguments |
| `tr` | `tr 'A-Z' 'a-z' < notes.txt` | translate or delete characters |
| `head` / `tail` | `tail -n 50 -f app.log` | first/last lines; `-f` follows a growing file |

Two notes that save real time:

- **`uniq` only collapses *adjacent* duplicates**, so it is nearly always
  preceded by `sort` — the same gotcha as `itertools.groupby` in
  [Section 39.3](../ch39-streams/03-pipelines.md).
- **`find ... -print0 | xargs -0` exists because filenames can contain spaces
  and newlines.** The `-print0`/`-0` pair separates names with a zero byte
  instead, which no filename can contain.

## A complete build-and-test runner, dissected

Here is a realistic script of the kind you will meet in a repository's
`scripts/` directory. Read it once, then read the numbered notes.

```text
#!/usr/bin/env bash                                              # 1
set -euo pipefail                                                # 2

readonly PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"   # 3
readonly BUILD_DIR="$PROJECT_ROOT/build"
DRY_RUN=false                                                    # 4

usage() {                                                        # 5
    cat <<'EOF'
usage: run-checks.sh [-n] [TARGET ...]

  -n            dry run: print each step, run nothing
  TARGET        one or more of: lint test build   (default: all three)
EOF
}

log()  { echo "[$(date +%T)] $*" >&2; }                          # 6
fail() { log "FAILED: $*"; exit 1; }

step() {                                                         # 7
    log "--> $*"
    if [[ "$DRY_RUN" == true ]]; then return 0; fi
    "$@" || fail "$1"
}

while getopts ":nh" opt; do                                      # 8
    case "$opt" in
        n) DRY_RUN=true ;;
        h) usage; exit 0 ;;
        *) usage >&2; exit 2 ;;
    esac
done
shift $((OPTIND - 1))

targets=("$@")                                                   # 9
if [[ ${#targets[@]} -eq 0 ]]; then
    targets=(lint test build)
fi

work_dir="$(mktemp -d)"                                          # 10
trap 'rm -rf "$work_dir"' EXIT

cd "$PROJECT_ROOT"                                               # 11

for target in "${targets[@]}"; do                                # 12
    case "$target" in
        lint)
            step python -m flake8 src/
            ;;
        test)
            step python -m pytest -q --junitxml="$work_dir/results.xml"
            cp "$work_dir/results.xml" "$BUILD_DIR/" 2>/dev/null || true
            ;;
        build)
            mkdir -p "$BUILD_DIR"
            step python -m build --outdir "$BUILD_DIR"
            ;;
        *)
            fail "unknown target: $target"
            ;;
    esac
done

log "all checks passed"                                          # 13
```

1. Portable shebang, so the script uses whichever bash the user has.
2. The safety line. Any failing command stops everything.
3. Find the project root **relative to the script**, not to wherever the user
   happened to be standing. `BASH_SOURCE[0]` is this file's path; `dirname`
   strips the filename; `cd ... && pwd` turns it absolute. `readonly` makes
   later reassignment an error.
4. A flag with an explicit default — with `set -u`, an unset variable would
   abort the script the first time it is read.
5. Usage as a here-document with quoted `'EOF'`, so nothing inside expands.
6. Two one-line helpers. Both write to stderr (`>&2`) so that log noise never
   contaminates output that something else might be capturing.
7. The core trick: `step` takes a whole command as its arguments and runs it
   with `"$@"`, which preserves each argument exactly. This is what makes
   `-n` (dry run) possible without duplicating every command.
8. `getopts` parses single-letter options properly — better than hand-written
   `if [[ "$1" == "-n" ]]` chains. `shift $((OPTIND - 1))` then removes the
   options, leaving only the positional arguments.
9. Arrays: `("$@")` copies the remaining arguments, `${#targets[@]}` is the
   length, and `"${targets[@]}"` expands to one word per element. Every part
   of that is quoted for the reasons you saw earlier.
10. A temporary directory plus a `trap` that removes it however the script
    ends — success, failure, or ++ctrl+c++.
11. `cd` once, at the top, after the paths are absolute. Scripts that assume
    the caller's working directory are the ones that break in CI.
12. The dispatch loop. Note `2>/dev/null || true` on the `cp`: that line is
    genuinely optional, so its failure is deliberately swallowed — and saying
    so explicitly is much better than turning `set -e` off.
13. If execution reaches here, every step succeeded, because any failure
    would have exited at step 7.

## The pipeline, simulated in Python

[Section 39.3](../ch39-streams/03-pipelines.md) built a shell pipeline as
nested generator calls. Now build it as a **composable pipeline runner** —
stages with options, applied left to right in the order you read them, with
the source instrumented so you can watch backpressure happen. The shell
command being modelled is:

```console
$ grep ERROR app.log | cut -d' ' -f2 | sort | uniq -c | sort -rn | head -3
      4 web-02
      3 web-03
      2 web-04
```

Each stage below is a generator taking an iterable and yielding an iterable —
the same contract a Unix filter has, where the iterable is a byte stream.

```python
from functools import partial

LOG = """\
10:31:02 web-01 INFO  GET /index 200
10:31:03 web-02 ERROR GET /cart 500 upstream timeout
10:31:04 web-03 INFO  GET /about 200
10:31:07 web-03 ERROR GET /cart 500 pool exhausted
10:31:09 web-02 WARN  GET /search 200 slow 1.9s
10:31:11 web-02 ERROR POST /login 500 upstream timeout
10:31:14 web-04 ERROR GET /cart 503 pool exhausted
10:31:15 web-01 INFO  GET /index 200
10:31:16 web-02 ERROR GET /cart 500 upstream timeout
10:31:19 web-03 ERROR GET /cart 503 pool exhausted
10:31:21 web-01 ERROR GET /report 500 slow query
10:31:22 web-04 ERROR POST /login 500 upstream timeout
10:31:25 web-02 ERROR GET /login 500 upstream timeout
10:31:28 web-03 ERROR GET /cart 503 pool exhausted
10:31:31 web-05 INFO  GET /health 200
10:31:33 web-01 INFO  GET /index 200
"""

stats = {"lines_read": 0}


def source(text):                              # the file, read line by line
    for line in text.splitlines():
        stats["lines_read"] += 1
        yield line


def grep(pattern, lines, invert=False):        # grep PATTERN  /  grep -v
    for line in lines:
        if (pattern in line) != invert:
            yield line


def cut(field, lines, sep=" "):                # cut -d' ' -fN   (1-based)
    for line in lines:
        parts = line.split(sep)
        if len(parts) >= field:
            yield parts[field - 1]


def sort_(lines, key=None, reverse=False):     # sort   (BLOCKING stage)
    yield from sorted(lines, key=key, reverse=reverse)


def uniq_c(items):                             # uniq -c  (adjacent only!)
    previous, n = None, 0
    for item in items:
        if item == previous:
            n += 1
        else:
            if previous is not None:
                yield (n, previous)
            previous, n = item, 1
    if previous is not None:
        yield (n, previous)


def head(n, items):                            # head -N
    if n <= 0:
        return
    for i, item in enumerate(items, start=1):
        yield item
        if i >= n:
            return                             # stop pulling: backpressure


def run(text, *stages):
    """The | operator: hand each stage the stream the previous one produced."""
    stream = source(text)
    for stage in stages:
        stream = stage(stream)
    return stream


# grep ERROR | cut -d' ' -f2 | sort | uniq -c | sort -rn | head -3
pipeline = run(
    LOG,
    partial(grep, "ERROR"),
    partial(cut, 2),
    sort_,
    uniq_c,
    partial(sort_, key=lambda pair: pair[0], reverse=True),
    partial(head, 3),
)

for count, host in pipeline:
    print(f"{count:>7} {host}")

print(f"\nsource read {stats['lines_read']} of {len(LOG.splitlines())} lines")

# The same source, but a pipeline that stops early:  grep ERROR | head -2
stats["lines_read"] = 0
for line in run(LOG, partial(grep, "ERROR"), partial(head, 2)):
    print(line)
print(f"\nsource read {stats['lines_read']} of {len(LOG.splitlines())} lines")
```

```text
      4 web-02
      3 web-03
      2 web-04

source read 16 of 16 lines
10:31:03 web-02 ERROR GET /cart 500 upstream timeout
10:31:07 web-03 ERROR GET /cart 500 pool exhausted

source read 4 of 16 lines
```

Three things this makes concrete:

- **The mapping from `|` to `stage(stream)` is exact.** The output is identical
  to the real shell command, produced by six generators instead of six
  processes.
- **`partial` does the job command-line flags do.** `partial(head, 3)` *is*
  `head -3`: a stage with its option baked in.
- **Early exit is real, and the counters prove it.** The full ranking had to
  read all sixteen lines because `sort` cannot emit anything until it has seen
  everything — but `grep ERROR | head -2` read only **four** lines before
  stopping. On a forty-gigabyte log that difference is the whole ball game.

!!! note "One honest difference from the real `cut`"
    Real `cut -d' '` does not collapse runs of spaces: two consecutive
    delimiters produce an empty field. The `cut` above behaves the same way
    (`line.split(" ")`), which is why the log's columns are single-spaced.
    When fields are separated by *variable* whitespace, shell users reach for
    `awk '{print $2}'` instead, which splits on runs of whitespace exactly
    like Python's `line.split()` with no argument.

## When to stop writing bash

Bash is superb at one thing: starting programs and connecting their inputs
and outputs. It is bad at almost everything else. Switch to Python when you
hit any of these:

- **You need a data structure.** Bash has strings, integers, indexed arrays,
  and (in bash 4+) associative arrays. Anything nested — a list of records, a
  dictionary of lists, JSON — is painful and fragile.
- **You are parsing structured data.** JSON, XML, YAML, and CSV with quoted
  commas all defeat line-oriented tools. Reaching for a regex to parse JSON
  is a warning sign; so is a pipeline of five `sed` calls.
- **The script has passed ~100 lines**, or has grown more than a handful of
  functions. The cost of bash's traps (quoting, `set -e`'s exceptions, global
  variables by default) grows faster than the code does.
- **You need real error handling, tests, or types.** Bash has no exceptions,
  no stack traces worth reading, and no practical unit-testing story for most
  teams.
- **It must run on Windows** without a compatibility layer.

Stay in bash when the script is mostly a list of commands with a little
control flow — which is most build scripts, deploy scripts, and glue. The two
worlds also mix well: a bash script that calls a Python script for the hard
part is a perfectly good design, and far better than either extreme.

!!! warning "Common mistakes"
    - **Unquoted expansions.** `rm $file`, `cd $dir`, `[ -f $path ]`. One
      space in a filename and you are operating on the wrong things. Write
      `"$file"` every time.
    - **Spaces around `=`.** `name = "Ada"` is not an assignment; bash tries
      to run a program called `name`.
    - **Assuming `$?` survives.** `$?` holds the status of the *previous*
      command only. `command; echo "done"; if [[ $? -ne 0 ]]` tests `echo`,
      which always succeeds. Capture it immediately: `status=$?`.
    - **Getting `2>&1 > file` backwards.** Put the redirection of stdout
      first: `> file 2>&1`.
    - **`uniq` without `sort`.** It only collapses adjacent duplicates, so
      unsorted input yields fragments and no error.
    - **Trusting `set -e` completely.** It does not fire inside `if`
      conditions, in `&&`/`||` chains, or after `!`. It is a seatbelt, not
      an airbag.
    - **`cd` without checking.** `cd "$dir"` followed by `rm -rf ./*` is a
      catastrophe if the `cd` failed. Write `cd "$dir" || exit 1` — or turn
      on `set -e` and quote the variable.

## Check your understanding

??? success "1. Why does this script delete the wrong file, and what is the fix?"

    ```text
    backup="my report.txt"
    cp $backup /tmp/
    ```

    Bash expands `$backup` and then splits the result on whitespace, so `cp`
    receives three arguments: `my`, `report.txt`, and `/tmp/`. It tries to
    copy two files that do not exist. The fix is `cp "$backup" /tmp/` — the
    double quotes suppress word splitting, so `cp` gets exactly two
    arguments. Run the `shlex` block above with your own filename to see the
    argument list either way.

??? success "2. What is the exit status of this line, and why is that a problem?"

    ```text
    curl -f https://example.com/data.csv | wc -l
    ```

    Normally the status is `wc`'s, which is 0 — `wc` succeeds even when it
    counts zero lines. So a dead URL looks like a successful command, and a
    script guarded by `&&` will happily carry on with an empty file. Adding
    `set -o pipefail` makes the pipeline report the rightmost non-zero
    status, so `curl`'s failure surfaces.

??? success "3. What is the difference between these two lines?"

    ```text
    ./build.sh > log.txt 2>&1
    ./build.sh 2>&1 > log.txt
    ```

    Redirections are applied left to right. In the first, stdout is pointed
    at `log.txt`, then stderr is pointed at "wherever stdout goes" — the
    file. Both end up in `log.txt`. In the second, stderr is pointed at
    wherever stdout goes *at that moment*, which is still the terminal, and
    only then is stdout moved to the file. Errors appear on screen, output
    goes to the file.

??? success "4. Predict the output of this pipeline before running the model."

    ```console
    $ printf 'b\na\nb\nc\na\nb\n' | sort | uniq -c | sort -rn | head -2
    ```

    Sorting gives `a a b b b c`; `uniq -c` collapses adjacent runs into
    `2 a`, `3 b`, `1 c`; `sort -rn` orders by the leading number descending
    into `3 b`, `2 a`, `1 c`; `head -2` keeps the first two. So:

    ```text
          3 b
          2 a
    ```

    You can check it by editing `LOG` in the pipeline model above — replace
    the log with the six letters, drop the `grep` and `cut` stages, and the
    remaining four stages produce exactly this.
