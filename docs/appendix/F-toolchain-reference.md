# Appendix F · Toolchain quick reference

Everything from [Chapter 40](../ch40-toolchain/index.md) on one page, plus the
Git and regex cards you will want beside it. This page is for looking things
up, not for learning them — each section links back to the page that explains
why. Commands are version-neutral; where GNU and BSD (macOS) tools differ,
the difference is noted.

## Shell: navigation and files

Full explanation: [Section 1.1](../ch01-tools/01-command-line.md).

| Command | Does |
|---|---|
| `pwd` | print the working directory |
| `ls -lah` | list: long form, all (including dotfiles), human-readable sizes |
| `cd DIR` / `cd ..` / `cd ~` / `cd -` | change directory / up one / home / back to the previous one |
| `mkdir -p a/b/c` | create a directory and any missing parents |
| `cp SRC DST` / `cp -r DIR DST` | copy a file / a directory tree |
| `mv SRC DST` | move **or** rename (same operation) |
| `rm FILE` / `rm -r DIR` / `rm -f` | delete; recursively; without prompting. No trash, no undo |
| `ln -s TARGET LINK` | create a symbolic link |
| `touch FILE` | create an empty file, or update an existing file's timestamp |
| `cat FILE` / `less FILE` | print a whole file / page through it (++q++ quits) |
| `head -n 20 F` / `tail -n 20 F` | first / last 20 lines |
| `tail -f app.log` | follow a file as it grows (++ctrl+c++ to stop) |
| `du -sh *` | size of each entry here, human-readable |
| `df -h` | free space per file system |
| `which CMD` / `type -a CMD` | where a command lives / everything that name resolves to |
| `file FILE` | what kind of file this actually is |
| `stat FILE` | size, permissions, and timestamps |
| `chmod 644 FILE` / `chmod +x FILE` | set permissions / make executable |
| `chown user:group FILE` | change owner (usually needs `sudo`) |
| `open .` (macOS) / `xdg-open .` (Linux) | open the current directory in the file manager |

## Shell: redirection and pipes

Full explanation: [Section 40.1](../ch40-toolchain/01-bash.md);
the streaming model is in
[Section 39.3](../ch39-streams/03-pipelines.md).

| Written | Effect |
|---|---|
| `cmd > file` | stdout to `file`, replacing its contents |
| `cmd >> file` | stdout appended to `file` |
| `cmd < file` | `file` becomes stdin |
| `cmd 2> file` | stderr only |
| `cmd > file 2>&1` | stdout **and** stderr to `file` (order matters) |
| `cmd &> file` | bash shorthand for the line above |
| `cmd > /dev/null 2>&1` | discard all output |
| <code>cmd1 &#124; cmd2</code> | cmd1's stdout becomes cmd2's stdin |
| <code>cmd &#124;&amp; cmd2</code> | pipe stdout *and* stderr (bash 4+) |
| <code>cmd &#124; tee file</code> | to the screen and to `file` |
| <code>cmd &#124; tee -a file</code> | ... appending instead of replacing |
| `cmd1 <(cmd2)` | process substitution: cmd2's output as a filename |
| `cmd &` | run in the background |

| FD | Stream | Default |
|---|---|---|
| `0` | stdin | keyboard |
| `1` | stdout | terminal |
| `2` | stderr | terminal |

## The text toolkit

One canonical example each; `man CMD` for the rest.

| Command | Canonical example | Reads as |
|---|---|---|
| `grep` | `grep -n ERROR app.log` | matching lines, with line numbers |
| | `grep -i -w cat notes.txt` | case-insensitive, whole word only |
| | `grep -v '^#' config.ini` | *invert*: everything except comments |
| | `grep -rl TODO src/` | recursive; list only the filenames |
| | `grep -c ERROR app.log` | count matching lines |
| | `grep -A2 -B2 panic log` | 2 lines of context after and before |
| | <code>grep -E 'WARN&#124;ERROR' log</code> | extended regex, so <code>&#124;</code> means alternation |
| `sed` | `sed 's/old/new/g' f` | substitute, globally on each line |
| | `sed -n '5,10p' f` | print only lines 5–10 |
| | `sed -i.bak 's/a/b/g' f` | edit in place, keeping `f.bak` |
| `awk` | `awk '{print $2}' f` | field 2 of each line (splits on any whitespace) |
| | `awk -F, '$3 > 100 {print $1}' s.csv` | comma-separated; filter on a field |
| | `awk '{sum += $1} END {print sum}' f` | running total, printed at the end |
| `cut` | `cut -d, -f1,3 s.csv` | fields 1 and 3, comma-delimited |
| | `cut -c1-8 f` | characters 1–8 of each line |
| `sort` | `sort -k2 -rn scores.txt` | by field 2, numeric, descending |
| | `sort -u names.txt` | sorted, duplicates removed |
| | `sort -h sizes.txt` | human-readable sizes (`2K` before `1M`) |
| `uniq` | <code>sort f &#124; uniq -c</code> | count **adjacent** duplicates — always sort first |
| | <code>sort f &#124; uniq -d</code> | only the lines that appear more than once |
| `wc` | `wc -l *.py` | line counts (`-w` words, `-c` bytes) |
| `find` | `find . -name '*.py'` | by name, recursively |
| | `find . -newer Makefile` | changed more recently than a file |
| | `find . -size +100M -type f` | files over 100 MB |
| | `find . -name '*.tmp' -delete` | ... and remove them |
| `xargs` | <code>find . -name '*.py' -print0 &#124; xargs -0 wc -l</code> | turn lines into arguments, safely |
| | `xargs -n1 -P4 CMD` | one argument per call, 4 in parallel |
| `tr` | `tr 'A-Z' 'a-z' < f` | translate characters |
| | `tr -d '\r' < f > unix.txt` | delete carriage returns (CRLF to LF) |
| `diff` | `diff -u old new` | unified diff, the format patches use |
| `tee` | <code>cmd &#124; tee out.log</code> | copy the stream to a file mid-pipeline |

!!! tip "Two habits"
    Always `sort` before `uniq`. Always pair `find -print0` with `xargs -0`
    when filenames might contain spaces.

## Bash scripting syntax card

Full explanation: [Section 40.1](../ch40-toolchain/01-bash.md).

```text
#!/usr/bin/env bash          # shebang: which interpreter runs this file
set -euo pipefail            # -e stop on error, -u error on unset var,
                             # pipefail: a pipeline fails if ANY stage fails
IFS=$'\n\t'                  # split words on newline/tab only
trap 'rm -rf "$tmp"' EXIT    # cleanup on any exit, including Ctrl-C
```

| Form | Meaning |
|---|---|
| `name=value` | assignment — **no spaces** around `=` |
| `"$name"` | expansion, quoted. Quote every expansion |
| `${name}s` | braces where the name would run into following text |
| `${name:-default}` | value, or `default` if unset or empty |
| `${name:?message}` | value, or abort with `message` if unset |
| `${#name}` | length of the string |
| `${name%.txt}` / `${name#pre}` | strip a suffix / a prefix |
| `${name/old/new}` | replace the first `old` (`//` for all) |
| `$(command)` | command substitution: the command's output |
| `$((a + b))` | arithmetic expansion |
| `$?` `$$` `$!` | last exit status / this PID / last background PID |
| `$0 $1 $#` `"$@"` | script name / first argument / count / all arguments |
| `shift` | drop `$1`, renumbering the rest |

| Test | True when |
|---|---|
| `[[ -f p ]]` `[[ -d p ]]` `[[ -e p ]]` | file / directory / anything exists |
| `[[ -s p ]]` `[[ -x p ]]` | non-empty / executable |
| `[[ -z "$s" ]]` `[[ -n "$s" ]]` | empty / non-empty string |
| `[[ "$a" == "$b" ]]` `[[ "$a" != "$b" ]]` | string equality |
| `[[ "$a" == *.log ]]` | glob match |
| `[[ "$a" =~ ^v[0-9]+$ ]]` | regex match |
| `[[ $n -lt 10 ]]` | integers: `-eq -ne -lt -le -gt -ge` |
| `(( n > 10 ))` | arithmetic context; no `$` needed on names |

```text
if [[ -f "$f" ]]; then ...; elif ...; then ...; else ...; fi

for f in *.log; do ...; done
for i in {1..5}; do ...; done
while IFS= read -r line; do ...; done < input.txt
until CONDITION; do ...; done

case "$1" in
    build)  make ;;
    *.log)  less "$1" ;;
    *)      echo "usage: $0 ..." >&2; exit 2 ;;
esac

name() {
    local x="$1"        # local, or it leaks into the whole script
    echo "$x"           # print to return DATA
    return 0            # return a STATUS (0-255)
}

cat <<'EOF'             # here-doc; quoted EOF means no expansion
literal $text
EOF
```

| Operator | Runs the right side |
|---|---|
| `a ; b` | always |
| `a && b` | only if `a` succeeded (exit 0) |
| <code>a &#124;&#124; b</code> | only if `a` failed (exit non-zero) |

## SSH and file transfer

Full explanation: [Section 40.2](../ch40-toolchain/02-ssh-remote.md).

| Command | Does |
|---|---|
| `ssh-keygen -t ed25519 -C "kim@laptop"` | create a key pair (use a passphrase) |
| `ssh-copy-id user@host` | install your **public** key on the server |
| `ssh user@host` | interactive shell |
| `ssh host 'cmd'` | run one command; quote it so it expands remotely |
| `ssh -v host` | verbose: why authentication failed |
| `ssh -p 2222 host` | non-standard port |
| `ssh -i ~/.ssh/other_key host` | a specific key |
| `ssh -J bastion host` | jump through a bastion host |
| `ssh -L 8888:localhost:8888 host` | local forward: reach a remote service |
| `ssh -R 9000:localhost:3000 host` | reverse forward: expose a local service |
| `ssh -D 1080 host` | SOCKS proxy |
| `ssh -N -f -L ...` | tunnel only: no shell, background |
| `ssh-add ~/.ssh/id_ed25519` / `ssh-add -l` | load a key into the agent / list loaded keys |
| `ssh-keygen -R host` | forget a host key (only after checking why it changed) |
| `scp f host:~/dir/` / `scp host:~/f .` | copy up / down (`-r` for directories) |
| `rsync -avz src/ host:dst/` | sync only the differences, resumable |
| `rsync -avz --delete src/ host:dst/` | make the destination match exactly |
| `rsync -avz --exclude '.git' src/ host:dst/` | skip paths |
| `rsync -avzn src/ host:dst/` | `-n` dry run: show what would transfer |

`~/.ssh/config`:

```text
Host cluster
    HostName            cluster.example.edu
    User                kim
    IdentityFile        ~/.ssh/id_ed25519
    AddKeysToAgent      yes
    ServerAliveInterval 60

Host gpu-*
    User        kim
    ProxyJump   cluster
```

!!! warning "The trailing slash in rsync"
    `rsync -a src/ dest/` copies the *contents* of `src` into `dest`.
    `rsync -a src dest/` creates `dest/src`. Nearly every rsync surprise is
    that one character.

## tmux

The prefix is ++ctrl+b++: press it, release, then press the second key.

| Command line | Does |
|---|---|
| `tmux new -s name` | start a named session |
| `tmux ls` | list sessions |
| `tmux attach -t name` | reattach |
| `tmux kill-session -t name` | end a session |

| Keys | Does |
|---|---|
| ++ctrl+b++ then ++d++ | detach — everything keeps running |
| ++ctrl+b++ then ++c++ | new window |
| ++ctrl+b++ then ++n++ / ++p++ | next / previous window |
| ++ctrl+b++ then a digit | jump to window *n* |
| ++ctrl+b++ then ++w++ | choose a window from a list |
| ++ctrl+b++ then `,` | rename the window |
| ++ctrl+b++ then `%` | split left/right |
| ++ctrl+b++ then `"` | split top/bottom |
| ++ctrl+b++ then an arrow key | move between panes |
| ++ctrl+b++ then ++z++ | zoom the pane full-screen (and back) |
| ++ctrl+b++ then ++space++ | cycle pane layouts |
| ++ctrl+b++ then `[` | scrollback / copy mode (++q++ to leave) |
| ++ctrl+b++ then ++x++ | kill the pane (asks first) |
| ++ctrl+b++ then ++question++ | list every binding |

## Permissions and numeric modes

| Octal digit | Bits | Symbolic | Means |
|---|---|---|---|
| `0` | `000` | `---` | nothing |
| `1` | `001` | `--x` | execute / enter a directory |
| `2` | `010` | `-w-` | write |
| `4` | `100` | `r--` | read |
| `5` | `101` | `r-x` | read and execute |
| `6` | `110` | `rw-` | read and write |
| `7` | `111` | `rwx` | everything |

Three digits, in order: **owner**, **group**, **others**.

| Mode | Symbolic | Typical use |
|---|---|---|
| `755` | `rwxr-xr-x` | scripts and directories everyone may use |
| `644` | `rw-r--r--` | ordinary files, public keys |
| `700` | `rwx------` | `~/.ssh`, private directories |
| `600` | `rw-------` | private keys, `authorized_keys`, `.env` |
| `400` | `r--------` | read-only secret |
| `775` / `664` | `rwxrwxr-x` / `rw-rw-r--` | group-writable shared project |

`chmod` also takes symbolic changes: `chmod +x f`, `chmod u+w,go-rwx f`,
`chmod -R g+r dir`. The `umask` (usually `022`) subtracts bits from the
default mode of newly created files.

A converter you can run both ways:

```python
FLAGS = "rwxrwxrwx"


def to_symbolic(mode):
    """0o755 -> 'rwxr-xr-x'"""
    return "".join(FLAGS[i] if mode & (1 << (8 - i)) else "-"
                   for i in range(9))


def to_mode(symbolic):
    """'rwxr-xr-x' -> 0o755"""
    mode = 0
    for i, ch in enumerate(symbolic):
        if ch != "-":
            mode |= 1 << (8 - i)
    return mode


for mode in [0o755, 0o644, 0o700, 0o600, 0o400, 0o664, 0o777]:
    print(f"chmod {mode:03o}  ->  {to_symbolic(mode)}")

print()
for symbolic in ["rwxr-x---", "rw-rw----", "r-xr-xr-x"]:
    print(f"{symbolic}  ->  chmod {to_mode(symbolic):03o}")
```

```text
chmod 755  ->  rwxr-xr-x
chmod 644  ->  rw-r--r--
chmod 700  ->  rwx------
chmod 600  ->  rw-------
chmod 400  ->  r--------
chmod 664  ->  rw-rw-r--
chmod 777  ->  rwxrwxrwx

rwxr-x---  ->  chmod 750
rw-rw----  ->  chmod 660
r-xr-xr-x  ->  chmod 555
```

## Make

Full explanation: [Section 40.3](../ch40-toolchain/03-make.md).

```makefile
target: prerequisite1 prerequisite2
	recipe line          # <- MUST begin with a real TAB, never spaces
```

| Syntax | Means |
|---|---|
| `VAR := value` | assign, expanding the right side now (usually what you want) |
| `VAR = value` | assign, expanding each time `VAR` is used |
| `VAR ?= value` | assign only if not already set |
| `VAR += more` | append |
| `$(VAR)` | use a variable |
| `$(SRCS:.c=.o)` | substitution reference: swap the suffix |
| `$(wildcard src/*.c)` | expand a glob at parse time |
| `$(patsubst %.c,%.o,$(SRCS))` | general pattern substitution |
| `%.o: %.c` | pattern rule; `%` matches the same stem on both sides |
| `.PHONY: all clean` | these targets are commands, not files |
| `-include deps.d` | include if it exists; do not fail if it does not |
| `@echo hi` | `@` suppresses echoing the command itself |
| `-rm f` | leading `-` ignores a failure in that line |

| Automatic variable | Is |
|---|---|
| `$@` | the target |
| `$<` | the first prerequisite |
| `$^` | all prerequisites, duplicates removed |
| `$?` | prerequisites newer than the target |
| `$*` | the stem matched by `%` |

| Invocation | Does |
|---|---|
| `make` | build the **first** target in the file |
| `make target` | build one target |
| `make -n` | dry run: print commands, run nothing |
| `make -j8` | up to 8 recipes in parallel |
| `make -B` | rebuild everything, ignoring timestamps |
| `make -C dir` | run in another directory |
| `make VAR=value` | override a variable |
| `make -p` | dump every rule and variable make knows |

## Git, grouped by task

Full explanation: [Section 24.1](../ch24-practice/01-git-workflow.md) and
[Section 1.3](../ch01-tools/03-git.md).

| Task | Command |
|---|---|
| **Start** | `git init` · `git clone URL` |
| **Look** | `git status` · `git diff` (unstaged) · `git diff --staged` |
| | `git log --oneline --graph --decorate --all` |
| | `git show COMMIT` · `git show COMMIT:path/file` |
| **Save** | `git add PATH` · `git add -p` (choose hunk by hunk) |
| | `git commit -m "message"` · `git commit --amend` (fix the last one) |
| **Branch** | `git switch -c feature/x` (create) · `git switch main` |
| | `git branch` · `git branch -d name` · `git branch -m newname` |
| **Combine** | `git merge feature/x` · `git rebase main` |
| | `git merge --abort` · `git rebase --continue` |
| **Share** | `git push -u origin feature/x` · `git push` |
| | `git fetch` (download only) · `git pull --rebase` |
| **Set aside** | `git stash` · `git stash pop` · `git stash list` |
| **Undo, unstaged** | `git restore FILE` (discard changes — irreversible) |
| **Undo, staged** | `git restore --staged FILE` |
| **Undo, committed, local** | `git reset --soft HEAD~1` (keep changes staged) |
| | `git reset --hard HEAD~1` (discard them — irreversible) |
| **Undo, already pushed** | `git revert COMMIT` (a new, opposite commit) |
| **Investigate** | `git blame FILE` · `git log -S "text"` (when did this appear?) |
| | `git log --follow FILE` · `git bisect start / good / bad` |
| **Rescue** | `git reflog` (every HEAD you have had — recovers "lost" commits) |
| **Clean** | `git clean -nd` (preview) · `git clean -fd` (delete untracked) |

!!! warning "The irreversible four"
    `git restore FILE`, `git reset --hard`, `git clean -fd`, and
    `git push --force` all destroy work that Git cannot get back for you.
    `git reflog` rescues committed work; it cannot rescue anything that was
    never committed.

## JUnit 5

Full explanation: [Section 40.4](../ch40-toolchain/04-junit.md).
Imports: `org.junit.jupiter.api.*` and
`static org.junit.jupiter.api.Assertions.*`.

| Annotation | Does |
|---|---|
| `@Test` | marks a test method |
| `@BeforeEach` / `@AfterEach` | runs before / after **every** test |
| `@BeforeAll` / `@AfterAll` | runs once per class — must be `static` unless the class is `@TestInstance(PER_CLASS)` |
| `@DisplayName("...")` | a readable name in the report |
| `@Disabled("reason")` | skip; always give a reason |
| `@Nested` | a grouped inner class with its own fixtures (non-static) |
| `@Tag("slow")` | label for including/excluding whole groups |
| `@RepeatedTest(10)` | run the same test repeatedly |
| `@ParameterizedTest` | one body, many inputs; pair with a source below |
| `@ValueSource(ints = {1, 2, 3})` | one argument per case |
| `@CsvSource({"1, A", "2, B"})` | several arguments per case |
| `@MethodSource("cases")` | arguments from a method |
| `@EnumSource(Season.class)` | one case per enum constant |
| `@Timeout(2)` | fail if the test takes over 2 seconds |

| Assertion | Passes when |
|---|---|
| `assertEquals(expected, actual)` | `.equals()` — **expected first** |
| `assertEquals(exp, act, delta)` | doubles within `delta` |
| `assertEquals(exp, act, "message")` | ... with a failure message |
| `assertNotEquals(a, b)` | they differ |
| `assertTrue(c)` / `assertFalse(c)` | the condition holds |
| `assertNull(x)` / `assertNotNull(x)` | reference is / is not null |
| `assertSame(a, b)` | the *same object*, not merely equal |
| `assertArrayEquals(a, b)` | element by element |
| `assertIterableEquals(a, b)` | same elements, same order |
| `assertThrows(E.class, exec)` | `exec` throws `E`; returns the exception |
| `assertDoesNotThrow(exec)` | nothing is thrown |
| `assertAll("label", exec...)` | every assertion is evaluated and reported |
| `assertTimeout(Duration, exec)` | finished in time (runs to completion first) |
| `assertTimeoutPreemptively(...)` | ... aborting it instead |
| `fail("reason")` | unconditional failure |

| Running | Command |
|---|---|
| Maven, everything | `mvn test` |
| Maven, one class / method | `mvn -Dtest=FooTest test` · `mvn -Dtest=FooTest#bar test` |
| Maven reports | `target/surefire-reports/` |
| Gradle, everything | `./gradlew test` |
| Gradle, a pattern | `./gradlew test --tests "*Foo*"` |
| Gradle reports | `build/reports/tests/test/index.html` |

## pytest

Full explanation: [Section 24.2](../ch24-practice/02-testing.md) and
[Section 8.4](../ch08-grids/04-unit-testing.md).

| Flag | Does |
|---|---|
| `-q` / `-v` | quiet / verbose output |
| `-x` | stop at the first failure |
| `--maxfail=3` | stop after 3 failures |
| `-k "add and not slow"` | select tests by name expression |
| `-m slow` | select by `@pytest.mark.slow` |
| `-s` | do not capture stdout (let `print` through) |
| `--lf` / `--ff` | rerun last-failed only / failed ones first |
| `--tb=short` | shorter tracebacks (`long`, `line`, `no` also exist) |
| `--durations=10` | list the 10 slowest tests |
| `--collect-only` | list what would run, run nothing |
| `-p no:randomly` | disable a plugin for one run |
| `--junitxml=results.xml` | write a JUnit-format XML report for CI |
| `-W error` | turn warnings into errors |
| `--cov=pkg` | coverage (needs the `pytest-cov` plugin) |

Conventions: files named `test_*.py`, functions named `test_*`, classes named
`Test*` with no `__init__`. Fixtures are functions decorated with
`@pytest.fixture` and requested by parameter name;
`@pytest.mark.parametrize("a,b", [(1, 2), (3, 4)])` is the table-driven form.

## Regex

Full explanation: [Section 41.1](../ch41-regex/01-fundamentals.md) and
[Section 41.2](../ch41-regex/02-groups-parsing.md). In Python always write
patterns as raw strings: `r"\d+"`.

| Pattern | Matches |
|---|---|
| `.` | any character except a newline (`re.S` includes it) |
| `\d` `\D` | a digit / a non-digit |
| `\w` `\W` | word character `[A-Za-z0-9_]` (Unicode-aware) / its opposite |
| `\s` `\S` | whitespace / non-whitespace |
| `[abc]` `[^abc]` `[a-z]` | one of / none of / a range |
| `^` `$` | start / end of the string (of each line with `re.M`) |
| `\b` `\B` | word boundary / non-boundary |
| `\A` `\Z` | start / end of the string, whatever the flags |
| `*` `+` `?` | 0 or more / 1 or more / 0 or 1 |
| `{3}` `{2,}` `{2,5}` | exactly / at least / between |
| `*?` `+?` `??` `{2,5}?` | the lazy versions: match as little as possible |
| <code>a&#124;b</code> | either side |
| `(...)` | group **and** capture |
| `(?:...)` | group without capturing |
| `(?P<name>...)` | named capture group |
| `(?=...)` `(?!...)` | lookahead: followed by / not followed by |
| `(?<=...)` `(?<!...)` | lookbehind: preceded by / not preceded by |
| `\1` / `\g<name>` | back-reference to an earlier group |

| Function | Returns |
|---|---|
| `re.search(p, s)` | the first match anywhere, or `None` |
| `re.match(p, s)` | a match anchored at the start, or `None` |
| `re.fullmatch(p, s)` | a match only if the whole string matches |
| `re.findall(p, s)` | a list of strings (or tuples, if the pattern has groups) |
| `re.finditer(p, s)` | an iterator of match objects — usually the better choice |
| `re.sub(p, repl, s)` | a copy with replacements (`repl` may be a function) |
| `re.split(p, s)` | split on the pattern |
| `re.compile(p)` | a reusable pattern object |

| Flag | Effect |
|---|---|
| `re.I` | case-insensitive |
| `re.M` | `^` and `$` match at every line break |
| `re.S` | `.` also matches a newline |
| `re.X` | verbose: whitespace and `#` comments allowed in the pattern |

!!! warning "Reach for a parser instead"
    HTML, JSON, YAML, and CSV-with-quoted-commas are not regular languages.
    A regex will handle 95% of the input and then silently mangle the rest.
    Use `json`, `csv`, or a real HTML parser.

## When things go wrong

| Message | Usual cause | First thing to check |
|---|---|---|
| `permission denied` running a script | the execute bit is not set | `ls -l script.sh`, then `chmod +x script.sh` |
| `Permission denied (publickey)` | the server did not accept your key | `ssh -v host` (which keys were offered?), `ssh-add -l`, `chmod 600 ~/.ssh/id_*` |
| `Permission denied` writing a file | you do not own the directory | `ls -ld .` — do not reach for `sudo` before you know why |
| `command not found` | not installed, not on `PATH`, or a local script needs `./` | `type -a cmd`, `echo $PATH`, and `./script.sh` rather than `script.sh` |
| `No such file or directory` — but the file is right there | wrong working directory, or the **shebang** names an interpreter that does not exist, or the file has Windows CRLF line endings | `pwd`, `head -1 script.sh`, `file script.sh` (says "CRLF"), then `tr -d '\r'` |
| `Address already in use` | something is already listening on that port | `lsof -i :8080` (macOS/Linux) or `ss -ltnp` (Linux); stop it, or use another port |
| `No space left on device` | the disk is full — or the *inodes* are | `df -h`, then `df -i`, then <code>du -sh * &#124; sort -h</code> in the biggest directory |
| `make: *** missing separator. Stop.` | spaces where a recipe needs a tab | make your editor show whitespace in `Makefile`s |
| `Killed` with no other message | the kernel ran you out of memory | <code>dmesg &#124; tail</code> on Linux; process the data in chunks ([Section 39.3](../ch39-streams/03-pipelines.md)) |
| Tests pass alone, fail in the suite | shared mutable state, or a real clock | [Section 40.4](../ch40-toolchain/04-junit.md) — give each test its own state |
| Build works, `make -j8` fails | a prerequisite you never declared | add it; run `make -n` to see the intended order |
| `REMOTE HOST IDENTIFICATION HAS CHANGED` | the server's host key is different | ask the administrator **before** running `ssh-keygen -R host` |
