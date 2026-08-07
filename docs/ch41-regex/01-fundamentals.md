# 41.1 Regex fundamentals

The string methods from [section 3.2](../ch03-functions/02-strings.md) —
`split`, `strip`, `startswith`, `find`, `replace` — handle text whose shape
you already know. They start to buckle the moment the question becomes
*fuzzy*: "a four-digit year, then a hyphen, then two digits", "a word that
ends in `ing`", "an address, wherever it appears in this line". A regular
expression describes that shape directly, in a notation shared by almost
every language and tool you will ever use. This section builds the notation
one construct at a time, and runs every single one of them against real text.

## When string methods run out of road

Here is a genuinely ordinary task: decide whether a string looks like an
ISO date, `YYYY-MM-DD`. First the string-method version, written the way you
would actually have to write it:

```python
def looks_like_date(text):
    parts = text.split("-")
    if len(parts) != 3:
        return False
    year, month, day = parts
    if len(year) != 4 or not year.isdigit():
        return False
    if len(month) != 2 or not month.isdigit():
        return False
    if len(day) != 2 or not day.isdigit():
        return False
    return True

samples = ["2024-03-01", "2024-3-1", "24-03-01", "2024-03-01x", "not a date"]
for s in samples:
    print(f"{s!r:<16} {looks_like_date(s)}")
```

```text
'2024-03-01'     True
'2024-3-1'       False
'24-03-01'       False
'2024-03-01x'    False
'not a date'     False
```

Fifteen lines, four `if` statements, and a bug waiting to happen every time
the format changes. Now the same function as a pattern:

```python
import re

def looks_like_date(text):
    return re.fullmatch(r"\d{4}-\d{2}-\d{2}", text) is not None

samples = ["2024-03-01", "2024-3-1", "24-03-01", "2024-03-01x", "not a date"]
for s in samples:
    print(f"{s!r:<16} {looks_like_date(s)}")
```

```text
'2024-03-01'     True
'2024-3-1'       False
'24-03-01'       False
'2024-03-01x'    False
'not a date'     False
```

Identical results. Read the pattern aloud and it is the specification:
`\d{4}` four digits, `-` a hyphen, `\d{2}` two digits, `-`, `\d{2}`.

!!! warning "Shape is not validity"

    Both versions above accept `2024-13-45`, because both check the *shape*
    and neither checks that months stop at 12. Regex is a shape language: it
    has no idea what a month is. For real dates, use the shape check as a
    cheap first pass and then `datetime.strptime(text, "%Y-%m-%d")` inside a
    `try` for the truth. Reaching for a pattern that encodes "01 to 12, and
    31 days except February" is how patterns become unreadable.

## The first pattern, and the match object

`re.search(pattern, text)` scans the whole string for the first place the
pattern fits. It returns a **match object** if it finds one and `None` if it
does not — and `None` is falsy, which is why `if re.search(...)` reads
naturally.

```python
import re

text = "Order A-42 shipped on 2024-03-01 to Ada."

m = re.search(r"\d{4}-\d{2}-\d{2}", text)
print("match object :", m)
print("matched text :", m.group())
print("start, end   :", m.start(), m.end())
print("span         :", m.span())
print("slice check  :", text[m.start():m.end()])

missing = re.search(r"\d{4}-\d{2}-\d{2}", "no date here")
print("no match     :", missing)
print("truthiness   :", bool(m), bool(missing))
```

```text
match object : <re.Match object; span=(22, 32), match='2024-03-01'>
matched text : 2024-03-01
start, end   : 22 32
span         : (22, 32)
slice check  : 2024-03-01
no match     : None
truthiness   : True False
```

A match object carries *where* as well as *what*, which is what makes regex a
parsing tool rather than a yes/no test.

## Literals, and the characters that are not

Most characters in a pattern stand for themselves: `cat` matches the letters
c, a, t. Fourteen characters are special — the **metacharacters** — and mean
something else:

```text
.  ^  $  *  +  ?  {  }  [  ]  \  |  (  )
```

To match one of those literally, put a backslash in front of it, or let
`re.escape` do it for you:

```python
import re

price = "Sale: $5.99 (was $9.99)"

print("unescaped dot:", re.findall(r"5.99", price))     # . matches any char
print("escaped dot  :", re.findall(r"5\.99", price))
print("dollar sign  :", re.findall(r"\$\d+\.\d\d", price))
print("re.escape    :", re.escape("$5.99 (sale)"))
print("used         :", re.findall(re.escape("$5.99"), price))
```

```text
unescaped dot: ['5.99']
escaped dot  : ['5.99']
dollar sign  : ['$5.99', '$9.99']
re.escape    : \$5\.99\ \(sale\)
used         : ['$5.99']
```

The first two lines happen to agree here, which is exactly why unescaped dots
survive testing: `5.99` also matches `5x99`, `5-99`, and `5 99`. When you
mean a literal dot, escape it.

`re.escape` is the right tool whenever the "pattern" comes from data — a user
search box, a filename, a configuration value. Interpolating raw user input
into a pattern is a small security hole and a large source of crashes.

## Character classes

Square brackets mean "any one character from this set". Inside them, a
hyphen makes a **range** and a leading `^` **negates** the whole set.

```python
import re

def show(pattern, text):
    """Run one pattern against one string and print every match."""
    print(f"{pattern:<16} on {text!r:<30} -> {re.findall(pattern, text)}")

show(r"[aeiou]", "regular expressions")
show(r"[a-f]", "the big fade")
show(r"[0-9]", "room 237, floor 4")
show(r"[A-Za-z]", "R2-D2")
show(r"[^0-9]", "R2-D2")
show(r"gr[ae]y", "grey and gray")
show(r"[.$*]", "a.b$c*d")
```

```text
[aeiou]          on 'regular expressions'          -> ['e', 'u', 'a', 'e', 'e', 'i', 'o']
[a-f]            on 'the big fade'                 -> ['e', 'b', 'f', 'a', 'd', 'e']
[0-9]            on 'room 237, floor 4'            -> ['2', '3', '7', '4']
[A-Za-z]         on 'R2-D2'                        -> ['R', 'D']
[^0-9]           on 'R2-D2'                        -> ['R', '-', 'D']
gr[ae]y          on 'grey and gray'                -> ['grey', 'gray']
[.$*]            on 'a.b$c*d'                      -> ['.', '$', '*']
```

Two rules worth memorising from that last line: **inside a class, most
metacharacters lose their powers**, so `[.$*]` needs no backslashes. The
exceptions are `]`, `\`, `^` (only first), and `-` (only between two
characters) — put a hyphen first or last when you want it literally, as in
`[-+]` or `[a-z-]`.

## The shorthand classes

Five of these come up constantly, and each has an upper-case negation:

| Shorthand | Means | Roughly equal to |
|---|---|---|
| `\d` | a digit | `[0-9]` |
| `\D` | not a digit | `[^0-9]` |
| `\w` | a "word" character | `[a-zA-Z0-9_]` |
| `\W` | not a word character | `[^a-zA-Z0-9_]` |
| `\s` | whitespace | `[ \t\n\r\f\v]` |
| `\S` | not whitespace | `[^ \t\n\r\f\v]` |

"Roughly" is doing real work in that table: by default Python's `\d`, `\w`,
and `\s` are **Unicode-aware**, so `\d` also matches Arabic-Indic and
Devanagari digits and `\w` matches accented letters. Pass `re.ASCII` when you
want the strict ASCII meaning.

```python
import re

sample = "Order #A-42\tshipped 2024-03-01"

print("digits    :", re.findall(r"\d", sample))
print("non-digits:", re.findall(r"\D", sample)[:6], "...")
print("words     :", re.findall(r"\w+", sample))
print("whitespace:", re.findall(r"\s", sample))
print("non-space :", re.findall(r"\S+", sample))

# Unicode by default; re.ASCII narrows it back to [0-9] and [a-zA-Z0-9_]
mixed = "42 and ٤٢ and café"
print("\\d unicode:", re.findall(r"\d+", mixed))
print("\\d ascii  :", re.findall(r"\d+", mixed, re.ASCII))
print("\\w unicode:", re.findall(r"\w+", mixed))
print("\\w ascii  :", re.findall(r"\w+", mixed, re.ASCII))
```

```text
digits    : ['4', '2', '2', '0', '2', '4', '0', '3', '0', '1']
non-digits: ['O', 'r', 'd', 'e', 'r', ' '] ...
words     : ['Order', 'A', '42', 'shipped', '2024', '03', '01']
whitespace: [' ', '\t', ' ']
non-space : ['Order', '#A-42', 'shipped', '2024-03-01']
\d unicode: ['42', '٤٢']
\d ascii  : ['42']
\w unicode: ['42', 'and', '٤٢', 'and', 'café']
\w ascii  : ['42', 'and', 'and', 'caf']
```

Look at the last line: with `re.ASCII`, `café` matches as `caf` and the `é`
is silently dropped. That is a real bug in a real system — the fix is to
leave Unicode mode on unless you have a specific reason not to.

## The dot, and what it does not match

`.` means "any single character **except a newline**". That exception is not
a detail; it is what makes line-oriented patterns work.

```python
import re

print(re.findall(r"a.c", "abc a c a-c a\nc"))
print(re.findall(r"a.c", "abc a c a-c a\nc", re.DOTALL))
print(re.findall(r"a.c", "abc a c a-c a\nc", re.S))     # re.S is short for DOTALL

# Inside a class, a dot is just a dot
print(re.findall(r"[.]", "3.14 vs 3x14"))
print(re.findall(r".", "hi\nyo"))
```

```text
['abc', 'a c', 'a-c']
['abc', 'a c', 'a-c', 'a\nc']
['abc', 'a c', 'a-c', 'a\nc']
['.']
['h', 'i', 'y', 'o']
```

## Anchors: `^`, `$`, and `\b`

Anchors match a **position**, not a character. They consume nothing.

- `^` — the start of the string (or of a line, with `re.M`)
- `$` — the end of the string, or just before a trailing newline
- `\b` — a **word boundary**: the edge between a `\w` and a non-`\w`
- `\B` — not a word boundary

`\b` is the one that turns a false-positive machine into a working search:

```python
import re

text = "The cat sat, but concatenate is not a cat, and cats scatter."

print("no anchors:", re.findall(r"cat", text))
print("word cat  :", re.findall(r"\bcat\b", text))
print("cat prefix:", re.findall(r"\bcat\w*", text))
print("positions :", [m.span() for m in re.finditer(r"\bcat\b", text)])

print("starts    :", bool(re.search(r"^The", text)))
print("ends      :", bool(re.search(r"scatter\.$", text)))
print("^ mid-str :", bool(re.search(r"^cat", text)))
```

```text
no anchors: ['cat', 'cat', 'cat', 'cat', 'cat']
word cat  : ['cat', 'cat']
cat prefix: ['cat', 'cat', 'cats']
positions : [(4, 7), (38, 41)]
starts    : True
ends      : True
^ mid-str : False
```

Five hits without anchors — including the `cat` hiding inside
"con**cat**enate" — and exactly two real ones with `\b` on each side. Any
time a search returns matches inside longer words, `\b` is the answer.

With the `re.MULTILINE` flag, `^` and `$` match at every line break instead
of only at the ends of the string:

```python
import re

log = "INFO start\nERROR disk full\nINFO retry\nERROR timeout"

print("without M:", re.findall(r"^ERROR .*", log))
print("with    M:", re.findall(r"^ERROR .*", log, re.M))
print("line ends:", re.findall(r".*full$", log, re.M))
```

```text
without M: []
with    M: ['ERROR disk full', 'ERROR timeout']
line ends: ['ERROR disk full']
```

## Quantifiers: how many

A quantifier applies to the thing immediately before it — one character, one
class, or one group.

| Quantifier | Meaning |
|---|---|
| `*` | zero or more |
| `+` | one or more |
| `?` | zero or one (optional) |
| `{n}` | exactly `n` |
| `{n,}` | `n` or more |
| `{n,m}` | between `n` and `m` |

```python
import re

def show(pattern, text):
    print(f"{pattern:<14} on {text!r:<26} -> {re.findall(pattern, text)}")

show(r"go*gle", "ggle gogle google gooogle")
show(r"go+gle", "ggle gogle google gooogle")
show(r"colou?r", "color colour colouur")
show(r"\d{4}", "1 22 333 4444 55555")
show(r"\d{2,3}", "1 22 333 4444 55555")
show(r"\d{2,}", "1 22 333 4444")
show(r"[a-z]+\d*", "ab12 cd x9")
```

```text
go*gle         on 'ggle gogle google gooogle' -> ['ggle', 'gogle', 'google', 'gooogle']
go+gle         on 'ggle gogle google gooogle' -> ['gogle', 'google', 'gooogle']
colou?r        on 'color colour colouur'     -> ['color', 'colour']
\d{4}          on '1 22 333 4444 55555'      -> ['4444', '5555']
\d{2,3}        on '1 22 333 4444 55555'      -> ['22', '333', '444', '555', '55']
\d{2,}         on '1 22 333 4444'            -> ['22', '333', '4444']
[a-z]+\d*      on 'ab12 cd x9'               -> ['ab12', 'cd', 'x9']
```

Two lines deserve a second look. `\d{4}` on `55555` matched `5555` and left a
lone `5` behind — a quantifier takes what it can and does not care about what
remains, which is why you so often need anchors or `\b` around it. And
`\d{2,3}` split `55555` into `555` + `55`, while it took `444` out of `4444`
and then discarded the leftover single `4` (one digit is fewer than the two
the pattern demands). Quantifiers are **greedy**: at each attempt they take
the most they can, then move on and never look back at the debris.

Greediness has a lazy counterpart (`*?`, `+?`, `??`) that takes the least it
can. It matters most when a quantifier is followed by something else, so
[section 41.2](02-groups-parsing.md) develops it properly with the classic
HTML example.

## Alternation and grouping

`|` means "or", and it has the **lowest precedence of everything** — it
splits the entire pattern unless parentheses stop it. Parentheses group a
sub-pattern so that a quantifier or an alternation applies to the whole
thing.

```python
import re

print(re.findall(r"cat|dog", "a cat, a dog, a catfish"))
print(re.findall(r"\b(?:cat|dog)s?\b", "one cat, two dogs, three cats"))

# Precedence trap: this is  ^cat  OR  dog$  -- almost never what is meant
print("wrong:", bool(re.search(r"^cat|dog$", "catdog")))
print("right:", bool(re.search(r"^(cat|dog)$", "catdog")))
print("right:", bool(re.search(r"^(cat|dog)$", "dog")))

# A quantifier applies to the group
print(re.search(r"(ab)+", "ababab xyz").group())
print(re.search(r"(?:\d{3}-){2}\d{4}", "call 555-867-5309 now").group())

# Alternation tries left to right and takes the FIRST that works
print(re.search(r"Jan|January", "January").group())
print(re.search(r"January|Jan", "January").group())
```

```text
['cat', 'dog', 'cat']
['cat', 'dogs', 'cats']
wrong: True
right: False
right: True
ababab
555-867-5309
Jan
January
```

Three lessons in one block. The `^cat|dog$` line matches `catdog` because it
means "starts with cat, or ends with dog" — bracket your alternatives. The
`(?:...)` spelling is a **non-capturing group**: it groups without
remembering, which matters for `findall` (a capturing group would make it
return group contents instead of whole matches) and is explained fully in
[41.2](02-groups-parsing.md). And alternation is ordered: put the longer
alternative first, or `Jan|January` will happily stop at `Jan`.

## The `re` API

### `search` vs `match` vs `fullmatch`

This is the single most common source of confusion in the module, and the
rule is one sentence each:

| Function | Where the pattern must fit |
|---|---|
| `re.search(p, s)` | **anywhere** in the string |
| `re.match(p, s)` | at the **start** (the rest of the string is ignored) |
| `re.fullmatch(p, s)` | the **whole** string, start to end |

```python
import re

pattern = r"\d+"
for text in ["42", "42abc", "abc42", "abc"]:
    s = re.search(pattern, text)
    m = re.match(pattern, text)
    f = re.fullmatch(pattern, text)
    print(f"{text!r:<9} search={str(s and s.group()):<7}"
          f" match={str(m and m.group()):<7} fullmatch={f and f.group()}")
```

```text
'42'      search=42      match=42      fullmatch=42
'42abc'   search=42      match=42      fullmatch=None
'abc42'   search=42      match=None    fullmatch=None
'abc'     search=None    match=None    fullmatch=None
```

Read the `'42abc'` row carefully, because it is where the bugs live:
`re.match` says yes. `match` is *not* "does this string match" — it is "does
the pattern fit at position zero", and it does not care what follows. A
validator built on `re.match(r"\d+", user_input)` happily accepts
`42; DROP TABLE`. **For validation, use `fullmatch`.** For finding
something inside text, use `search`. `match` is rarely the one you want;
`re.match(p, s)` does the same job as `re.search(r"\A" + p, s)` — `\A` means
"the very start of the string" and, unlike `^`, is unaffected by `re.M`.

### `findall` and `finditer`

`findall` returns a list of **strings**; `finditer` returns an iterator of
**match objects**, which is what you want as soon as you care about position
or about groups.

```python
import re

text = "Errors: 3 at 09:15, 12 at 10:40, 7 at 11:05"

print("findall :", re.findall(r"\d+", text))
print("count   :", len(re.findall(r"\d+", text)))
print("sum     :", sum(int(n) for n in re.findall(r"\d+", text)))

print("finditer:")
for m in re.finditer(r"\d{2}:\d{2}", text):
    print(f"   {m.group()!r} at {m.span()}")

# findall changes its return type when the pattern has capturing groups
print("no group :", re.findall(r"\d{2}:\d{2}", text))
print("one group:", re.findall(r"(\d{2}):\d{2}", text))
print("two group:", re.findall(r"(\d{2}):(\d{2})", text))

# a pattern matches SHAPE, not meaning
print("shapes   :", re.findall(r"\d{2}:\d{2}", "ratio 16:9, odds 20:80, at 10:40"))
```

```text
findall : ['3', '09', '15', '12', '10', '40', '7', '11', '05']
count   : 9
sum     : 112
finditer:
   '09:15' at (13, 18)
   '10:40' at (26, 31)
   '11:05' at (38, 43)
no group : ['09:15', '10:40', '11:05']
one group: ['09', '10', '11']
two group: [('09', '15'), ('10', '40'), ('11', '05')]
shapes   : ['20:80', '10:40']
```

Two traps in one output. `findall` with one capturing group returns *only
that group*, and with several returns *tuples* — surprising the first time,
and the reason `(?:...)` exists. And look at the last line: the "time"
pattern happily reports `20:80`, which is not a time, and misses `16:9`,
which was not meant to be one. A pattern describes the *shape* of text and
knows nothing about what it means; when the meaning matters, validate after
matching.

`finditer` is also the memory-friendly one: it is lazy, exactly like the
generators of [section 39.3](../ch39-streams/03-pipelines.md), so it can walk
a huge document without building a list.

### `sub` and `split`

```python
import re

messy = "too    many\t\tspaces   here"
print("squeeze  :", re.sub(r"\s+", " ", messy))
print("first 1  :", repr(re.sub(r"\s+", " ", messy, count=1)))
print("subn     :", re.subn(r"\s+", " ", messy))

print("redact   :", re.sub(r"\b\d{3}-\d{2}-\d{4}\b", "[REDACTED]",
                           "ssn 123-45-6789 on file"))

record = "ada;36 , grace;45,linus;29"
print("split    :", re.split(r"\s*[,;]\s*", record))
print("keep sep :", re.split(r"(\d+)", "a1b22c"))
print("maxsplit :", re.split(r",", "a,b,c,d", maxsplit=2))
```

```text
squeeze  : too many spaces here
first 1  : 'too many\t\tspaces   here'
subn     : ('too many spaces here', 3)
redact   : ssn [REDACTED] on file
split    : ['ada', '36', 'grace', '45', 'linus', '29']
keep sep : ['a', '1', 'b', '22', 'c']
maxsplit : ['a', 'b', 'c,d']
```

`re.split` with a *capturing* group keeps the separators in the result, which
is occasionally exactly what you want — a tokenizer, for instance, which is
the last exercise of this chapter.

### `compile`

`re.compile` turns a pattern string into a reusable **pattern object** with
the same methods. Use it when a pattern is used more than once, when it
deserves a name, or when you want to attach flags permanently.

```python
import re

TIME = re.compile(r"\b(\d{1,2}):(\d{2})\b")
ERROR_LINE = re.compile(r"^ERROR\b.*$", re.MULTILINE)

log = "INFO 9:05 start\nERROR 10:40 disk full\nERROR 11:05 timeout"

print("times  :", TIME.findall(log))
print("errors :", ERROR_LINE.findall(log))
print("first  :", TIME.search(log).group())
print("pattern:", TIME.pattern)
print("flags M:", bool(ERROR_LINE.flags & re.MULTILINE))
```

```text
times  : [('9', '05'), ('10', '40'), ('11', '05')]
errors : ['ERROR 10:40 disk full', 'ERROR 11:05 timeout']
first  : 9:05
pattern: \b(\d{1,2}):(\d{2})\b
flags M: True
```

Python caches recently used patterns internally, so `compile` is mostly about
**clarity**, not speed: a named constant at the top of a module beats an
inline pattern buried in a loop.

### Flags

| Flag | Short | Effect |
|---|---|---|
| `re.IGNORECASE` | `re.I` | case-insensitive matching |
| `re.MULTILINE` | `re.M` | `^` and `$` match at every line break |
| `re.DOTALL` | `re.S` | `.` also matches newline |
| `re.VERBOSE` | `re.X` | ignore whitespace and allow `#` comments in the pattern |

```python
import re

print(re.findall(r"error", "Error ERROR error"))
print(re.findall(r"error", "Error ERROR error", re.I))

# Verbose mode: the same pattern, laid out and commented
DATE = re.compile(r"""
    \b
    (\d{4})      # year:  four digits
    -            # separator
    (\d{2})      # month: two digits
    -            # separator
    (\d{2})      # day:   two digits
    \b
""", re.VERBOSE)

print(DATE.findall("due 2024-03-01, shipped 2024-04-15"))

# In verbose mode a literal space must be escaped or bracketed
GAP = re.compile(r"a \  b [ ] c", re.X)          # matches 'a b c'? see below
print("verbose spaces:", bool(GAP.fullmatch("a b c")), repr(GAP.pattern.strip()))
print("combined flags:", re.findall(r"^error.*", "Error: a\nerror: b", re.I | re.M))
```

```text
['error']
['Error', 'ERROR', 'error']
[('2024', '03', '01'), ('2024', '04', '15')]
verbose spaces: True 'a \\  b [ ] c'
combined flags: ['Error: a', 'error: b']
```

Verbose mode is how a long pattern stays maintainable: whitespace and
anything after a `#` are ignored, so you can lay the pattern out like code
and explain each piece. The price is that a literal space must be written
`\ ` or `[ ]`, as the `GAP` pattern shows. Flags combine with `|`.

## Raw strings and the backslash plague

Regex uses backslashes constantly. So do Python string literals. Without care
the two fight, and the reason patterns are written `r"..."` in every example
above is to stop the fight before it starts.

```python
import re

# Python's own escapes happen FIRST, before re ever sees the string
print("len('\\b') =", len("\b"), "-> the backspace character, chr(8)")
print("len(r'\\b') =", len(r"\b"), "-> a backslash and a b, which is what re wants")

text = "the cat sat"
print("plain string:", re.search("\bcat\b", text))     # looking for backspace-cat
print("raw string  :", re.search(r"\bcat\b", text))

# Doubling works too, but nobody enjoys reading it
print("equal?      :", "\\b" == r"\b")

# And matching a literal backslash is where it gets silly
path = r"C:\Users\ada"
print("path        :", path)
print("raw pattern :", re.findall(r"\\", path))
print("plain patt. :", re.findall("\\\\", path))
```

```text
len('\b') = 1 -> the backspace character, chr(8)
len(r'\b') = 2 -> a backslash and a b, which is what re wants
plain string: None
raw string  : <re.Match object; span=(4, 7), match='cat'>
equal?      : True
path        : C:\Users\ada
raw pattern : ['\\', '\\']
plain patt. : ['\\', '\\']
```

The middle two lines are the plague in miniature: `"\bcat\b"` is a
*backspace*, `c`, `a`, `t`, *backspace* — a pattern that will never match
normal text, with no error message to tell you so. The rule is absolute and
costs nothing:

!!! tip "Always write patterns as raw strings"

    `r"\d+"`, not `"\d+"`. There is no downside — a raw string is a normal
    string, built by a different rule — and one exception: a raw string
    cannot end in a single backslash. Python 3.12 and later also emit a
    `SyntaxWarning` for unrecognised escapes like `"\d"`, which is the
    interpreter trying to warn you about exactly this bug.

## Every construct, on one page — and all of it executed

Here is the cumulative reference. Every row is a real pattern run against a
real sample, and the third column is the actual result, not a description of
one.

```python
import re

ROWS = [
    (r"cat",        "literal characters",          "the cat scattered"),
    (r"[aeiou]",    "any one of these",            "regex"),
    (r"[a-f]",      "a range",                     "deadbeef99"),
    (r"[^0-9]",     "negated class",               "a1b2"),
    (r"\d",         "digit",                       "R2-D2"),
    (r"\D",         "non-digit",                   "R2-D2"),
    (r"\w+",        "word characters",             "hi there_42!"),
    (r"\s",         "whitespace",                  "a b"),
    (r"a.c",        "dot: any char but newline",   "abc a-c ac"),
    (r"^\w+",       "anchored at the start",       "first second"),
    (r"\w+$",       "anchored at the end",         "first second"),
    (r"\bcat\b",    "whole word only",             "cat concatenate cat"),
    (r"go*d",       "zero or more",                "gd god goood"),
    (r"go+d",       "one or more",                 "gd god goood"),
    (r"colou?r",    "optional character",          "color colour"),
    (r"\d{3}",      "exactly three",               "12 345 6789"),
    (r"\d{2,3}",    "two to three",                "12 345 6789"),
    (r"cat|dog",    "alternation",                 "a dog and a cat"),
    (r"(?:ab)+",    "grouped repetition",          "ababab ab x"),
    (r"\$\d+\.\d{2}", "escaped metacharacters",    "cost $12.50 today"),
]

print(f"{'pattern':<16}{'means':<28}{'matches'}")
print("-" * 74)
for pattern, meaning, sample in ROWS:
    print(f"{pattern:<16}{meaning:<28}{re.findall(pattern, sample)}")
```

```text
pattern         means                       matches
--------------------------------------------------------------------------
cat             literal characters          ['cat', 'cat']
[aeiou]         any one of these            ['e', 'e']
[a-f]           a range                     ['d', 'e', 'a', 'd', 'b', 'e', 'e', 'f']
[^0-9]          negated class               ['a', 'b']
\d              digit                       ['2', '2']
\D              non-digit                   ['R', '-', 'D']
\w+             word characters             ['hi', 'there_42']
\s              whitespace                  [' ']
a.c             dot: any char but newline   ['abc', 'a-c']
^\w+            anchored at the start       ['first']
\w+$            anchored at the end         ['second']
\bcat\b         whole word only             ['cat', 'cat']
go*d            zero or more                ['gd', 'god', 'goood']
go+d            one or more                 ['god', 'goood']
colou?r         optional character          ['color', 'colour']
\d{3}           exactly three               ['345', '678']
\d{2,3}         two to three                ['12', '345', '678']
cat|dog         alternation                 ['dog', 'cat']
(?:ab)+         grouped repetition          ['ababab', 'ab']
\$\d+\.\d{2}    escaped metacharacters      ['$12.50']
```

Check two rows against your own reading before moving on. `\d{3}` on
`"12 345 6789"` finds `345` and `678` — it takes the first three digits of
`6789` and abandons the `9`, exactly as the quantifier section warned. And
`a.c` never matches the bare `ac`, because the dot demands one character and
will not accept none.

!!! warning "Common mistakes"

    - **Forgetting the `r` prefix.** `"\b"` is a backspace and `"\d"` is a
      deprecated escape. Write `r"\b"` and `r"\d"` — always.
    - **Using `re.match` for validation.** It anchors only the start, so
      `re.match(r"\d+", "42abc")` succeeds. Use `re.fullmatch`.
    - **An unescaped dot.** `r"3.14"` also matches `"3x14"`. Escape it:
      `r"3\.14"`.
    - **Alternation without a group.** `r"^cat|dog$"` means "starts with cat
      or ends with dog". Write `r"^(cat|dog)$"`.
    - **Expecting `findall` to return whole matches when the pattern has
      groups.** It returns the groups instead. Use `(?:...)` or `finditer`.
    - **Matching across the wrong boundary.** `\d{2}:\d{2}` found `12:10` in
      "12 at 10:40". Anchor with `\b` or match more context.

## Check your understanding

??? success "1. What does `re.findall(r'\\d+', 'a1bb22ccc333')` return?"

    `['1', '22', '333']`. The `+` is greedy, so each match takes as many
    consecutive digits as it can before stopping at the first non-digit; the
    letters are skipped over because `findall` scans forward for the next
    place the pattern fits. Note the return type: a list of **strings**, not
    numbers — `int()` them if you want arithmetic.

??? success "2. Which of these accept `'42abc'`, and why?"

    ```python
    import re
    print(bool(re.search(r"\d+", "42abc")))
    print(bool(re.match(r"\d+", "42abc")))
    print(bool(re.fullmatch(r"\d+", "42abc")))
    ```

    `search` → True (digits appear somewhere), `match` → True (digits appear
    at position 0; the trailing `abc` is simply not examined), `fullmatch` →
    False (the pattern must consume the entire string). Any validator built
    on the first two will accept garbage with a valid prefix.

??? success "3. Why does `r'\bcat\b'` fail to find `cat` in `'concatenate'` but `r'cat'` succeeds?"

    `\b` matches a position where a word character meets a non-word
    character. Inside `concatenate` the letters on both sides of `cat` are
    word characters, so neither boundary exists and the pattern cannot fit.
    Without the anchors the pattern only asks for three consecutive letters,
    which are certainly there. This is the fix for essentially every
    substring false positive.

??? success "4. Rewrite `r'(\\d{4})-(\\d{2})'` so `findall` returns whole matches instead of tuples."

    Make the groups non-capturing: `r"(?:\d{4})-(?:\d{2})"`, or drop them
    entirely — `r"\d{4}-\d{2}"` — since neither group is doing anything here.
    `findall` returns the capturing groups when there are any, so the way to
    get whole matches back is to have no capturing groups at all (or to use
    `finditer` and read `m.group(0)`).
