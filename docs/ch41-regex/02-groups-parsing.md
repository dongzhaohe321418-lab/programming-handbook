# 41.2 Groups, greediness, and real parsing

[Section 41.1](01-fundamentals.md) taught matching: does this text have this
shape? That is half of what regex is for. The other half is **extraction** —
pulling the year out of a date, the IP address out of a log line, the amount
out of an invoice — and it all rests on one construct: a pair of parentheses
that says "remember what matched here". This section turns patterns into
parsers, covers the two features that fix the mistakes everybody makes
(lazy quantifiers and lookaround), explains the failure mode that can take a
web server offline, and ends by drawing the line where regex should stop and
a real parser should start.

## Capturing groups

Parentheses do two jobs at once: they group (so a quantifier or alternation
applies to the whole thing) and they **capture** (the matched text is saved
and numbered). Group numbers are assigned by counting opening parentheses
from the left, starting at 1. Group 0 is always the entire match.

```python
import re

line = ('203.0.113.7 - - [05/Feb/2024:10:12:44] '
        '"GET /index.html HTTP/1.1" 200 5120')

pattern = r'^(\S+) \S+ \S+ \[([^\]]+)\] "([A-Z]+) (\S+)[^"]*" (\d{3}) (\d+)$'
m = re.match(pattern, line)

print("group(0) — the whole match:")
print("  ", m.group(0)[:46], "...")
print("group(1) — ip     :", m.group(1))
print("group(2) — time   :", m.group(2))
print("group(3) — method :", m.group(3))
print("group(4) — path   :", m.group(4))
print("group(5) — status :", m.group(5))
print("group(6) — bytes  :", m.group(6))
print("groups()          :", m.groups())
print("several at once   :", m.group(1, 3, 5))
print("where was group 1 :", m.span(1))
print("how many groups   :", len(m.groups()))
```

```text
group(0) — the whole match:
   203.0.113.7 - - [05/Feb/2024:10:12:44] "GET /i ...
group(1) — ip     : 203.0.113.7
group(2) — time   : 05/Feb/2024:10:12:44
group(3) — method : GET
group(4) — path   : /index.html
group(5) — status : 200
group(6) — bytes  : 5120
groups()          : ('203.0.113.7', '05/Feb/2024:10:12:44', 'GET', '/index.html', '200', '5120')
several at once   : ('203.0.113.7', 'GET', '200')
where was group 1 : (0, 11)
how many groups   : 6
```

One line of text, six fields, no `split` gymnastics.

Note `[^\]]+` for the timestamp. "One or more characters that are not a
closing bracket" is the standard way to say "everything up to the next
delimiter", and it is both clearer and faster than the lazy `.+?` we will meet
below.

### Named groups are better

Counting parentheses is a chore, and every time someone adds a group in the
middle, all the later numbers shift and your code breaks silently.
`(?P<name>...)` gives a group a name; `groupdict()` hands you the whole match
as a dictionary.

```python
import re

LOG = re.compile(r"""
    ^(?P<ip>\S+)\s+\S+\s+\S+\s+          # client address, then two ignored fields
    \[(?P<time>[^\]]+)\]\s+              # timestamp inside square brackets
    "(?P<method>[A-Z]+)\s(?P<path>\S+)[^"]*"\s+   # request line
    (?P<status>\d{3})\s+(?P<size>\d+)$   # status code and response size
""", re.VERBOSE)

line = ('203.0.113.7 - - [05/Feb/2024:10:12:44] '
        '"GET /index.html HTTP/1.1" 200 5120')

m = LOG.match(line)
record = m.groupdict()
print("record :", record)
print("by name:", m.group("status"), m.group("path"))
print("by number still works:", m.group(5))
print("status as int:", int(record["status"]) // 100, "xx family")
```

```text
record : {'ip': '203.0.113.7', 'time': '05/Feb/2024:10:12:44', 'method': 'GET', 'path': '/index.html', 'status': '200', 'size': '5120'}
by name: 200 /index.html
by number still works: 200
status as int: 2 xx family
```

`groupdict()` is the bridge from text to data: one call and the line has
become a record you can put in a list, sort, or count.

Combined with verbose mode, a named-group pattern is genuinely readable six
months later — which is the real reason to prefer it.

### Non-capturing groups `(?:...)`

Sometimes you need parentheses only for grouping, and capturing the text
would be noise. `(?:...)` groups without capturing.

```python
import re

text = "cats, dogs, and a dogcatcher"

# Capturing version: findall returns the GROUP, not the match
print("capturing    :", re.findall(r"\b(cat|dog)s\b", text))
print("non-capturing:", re.findall(r"\b(?:cat|dog)s\b", text))

# It also keeps your numbering stable
m1 = re.match(r"(\d{4})-(\d{2})", "2024-03")
m2 = re.match(r"(?:\d{4})-(\d{2})", "2024-03")
print("with capture   , group 1 =", m1.group(1))
print("without capture, group 1 =", m2.group(1))
print("group counts:", len(m1.groups()), "vs", len(m2.groups()))
```

```text
capturing    : ['cat', 'dog']
non-capturing: ['cats', 'dogs']
with capture   , group 1 = 2024
without capture, group 1 = 03
group counts: 2 vs 1
```

Use `(?:...)` whenever the parentheses exist for structure rather than for
extraction. It buys three things:

- `findall` keeps returning **whole matches** instead of group contents;
- group **numbers stay meaningful**, and stop shifting when someone edits the
  pattern;
- it tells the next reader "nothing to see here".

## Backreferences: matching what you already matched

Inside a pattern, `\1` means "the exact text that group 1 captured". This
lets a pattern require a repeat — something no amount of character classes
can express.

```python
import re

text = "this this is a a test, but but not not a problem"

print("doubled words:", re.findall(r"\b(\w+)\s+\1\b", text))
print("with position:")
for m in re.finditer(r"\b(\w+)\s+\1\b", text):
    print(f"   {m.group(0)!r:<12} at {m.span()}")

# Fix them: \1 in the REPLACEMENT means the same group
print("repaired:", re.sub(r"\b(\w+)\s+\1\b", r"\1", text))

# Named backreferences: (?P=name) in the pattern, \g<name> in the replacement
QUOTED = re.compile(r"(?P<q>['\"])(?P<body>.*?)(?P=q)")
sample = """say 'hi' and "bye" now"""
print("quoted  :", [m.group("body") for m in QUOTED.finditer(sample)])
print("swapped :", QUOTED.sub(r"<\g<body>>", sample))
```

```text
doubled words: ['this', 'a', 'but', 'not']
with position:
   'this this'  at (0, 9)
   'a a'        at (13, 16)
   'but but'    at (23, 30)
   'not not'    at (31, 38)
repaired: this is a test, but not a problem
quoted  : ['hi', 'bye']
swapped : say <hi> and <bye> now
```

The `\1` in the replacement string is how the repair works: match two copies,
put back one.

The `QUOTED` pattern is worth a second look. `(?P<q>['\"])` captures
*whichever* quote character opened the string, and `(?P=q)` demands the same
one to close it, so a single quote cannot be closed by a double quote. **That
is a genuine parsing rule expressed in eight characters.**

## `sub`: rewriting text

`re.sub(pattern, replacement, text)` replaces every match. The replacement
can be a **template string** — where `\1`, `\2`, and `\g<name>` insert
captured groups — or, far more powerfully, a **function**.

```python
import re

dates = "due 2024-03-01, shipped 2024-04-15"

print("reorder :", re.sub(r"(\d{4})-(\d{2})-(\d{2})", r"\3/\2/\1", dates))

NAMED = r"(?P<y>\d{4})-(?P<m>\d{2})-(?P<d>\d{2})"
print("by name :", re.sub(NAMED, r"\g<d>.\g<m>.\g<y>", dates))
print("wrap    :", re.sub(NAMED, r"[\g<0>]", dates))     # \g<0> = the whole match
```

```text
reorder : due 01/03/2024, shipped 15/04/2024
by name : due 01.03.2024, shipped 15.04.2024
wrap    : due [2024-03-01], shipped [2024-04-15]
```

When the replacement needs *logic*, pass a function instead. `sub` calls it
once per match with the match object and substitutes whatever string comes
back. Here is the canonical use: masking sensitive numbers while keeping the
last four digits, the way a receipt does.

```python
import re

CARD = re.compile(r"\b\d(?:[ -]?\d){12,18}\b")   # 13-19 digits, spaced or hyphenated

def mask(m):
    """Replace all but the last four digits with asterisks."""
    digits = re.sub(r"\D", "", m.group())
    return "*" * (len(digits) - 4) + digits[-4:]

text = ("Card 4111-1111-1111-1111 charged; backup 5500 0000 0000 0004; "
        "phone 555-1234.")

print("found :", [m.group() for m in CARD.finditer(text)])
print("masked:", CARD.sub(mask, text))

# The function receives a full match object, so it can branch on the content
def shout_long_words(m):
    word = m.group()
    return word.upper() if len(word) > 5 else word

print("branch:", re.sub(r"\b\w+\b", shout_long_words,
                        "the quick brown foxes jumped over"))
```

```text
found : ['4111-1111-1111-1111', '5500 0000 0000 0004']
masked: Card ************1111 charged; backup ************0004; phone 555-1234.
branch: the quick brown foxes JUMPED over
```

The phone number is untouched because seven digits are fewer than the
thirteen the pattern requires — the `{12,18}` bound is doing exactly the work
a hand-written masker would need an `if` for.

A replacement function is the escape hatch that makes `sub` able to do
anything: look values up in a dictionary, format numbers, count as it goes, or
leave a match alone by returning `m.group()` unchanged.

## Greedy versus lazy

Every quantifier you have met is **greedy**: it takes as much as it can and
gives characters back only if the rest of the pattern fails. Adding `?` after
a quantifier makes it **lazy**: it takes as little as possible and asks for
more only when forced.

| | Greedy | Lazy |
|---|---|---|
| Spelling | `*` `+` `?` `{n,m}` | `*?` `+?` `??` `{n,m}?` |
| Strategy | take the most, then give back | take the least, then extend |
| `a+` / `a+?` on `"aaaa"` | `aaaa` | `a` |
| `<.+>` / `<.+?>` on `"<b>hi</b>"` | the whole string | `<b>` |
| Typical use | the default; what you usually want | a terminator of more than one character |
| Better alternative | — | a negated class such as `<[^>]+>` |

The classic demonstration is HTML tags.

```python
import re

html = "<b>bold</b> and <i>italic</i>"

print("greedy <.+>  :", re.findall(r"<.+>", html))
print("lazy   <.+?> :", re.findall(r"<.+?>", html))
print("class  <[^>]+>:", re.findall(r"<[^>]+>", html))

print()
print("greedy content:", re.findall(r"<b>(.+)</b>", "<b>one</b> x <b>two</b>"))
print("lazy   content:", re.findall(r"<b>(.+?)</b>", "<b>one</b> x <b>two</b>"))

print()
print("all quantifiers have a lazy twin:")
print("  a+  ->", re.match(r"a+", "aaaa").group(),
      "   a+? ->", re.match(r"a+?", "aaaa").group())
print("  \\d{2,4} ->", re.match(r"\d{2,4}", "12345").group(),
      "   \\d{2,4}? ->", re.match(r"\d{2,4}?", "12345").group())
```

```text
greedy <.+>  : ['<b>bold</b> and <i>italic</i>']
lazy   <.+?> : ['<b>', '</b>', '<i>', '</i>']
class  <[^>]+>: ['<b>', '</b>', '<i>', '</i>']

greedy content: ['one</b> x <b>two']
lazy   content: ['one', 'two']

all quantifiers have a lazy twin:
  a+  -> aaaa    a+? -> a
  \d{2,4} -> 1234    \d{2,4}? -> 12
```

The greedy `<.+>` swallowed the entire string: `.+` grabbed everything to the
end, then backed up just far enough to find a `>` — the *last* one. The lazy
`<.+?>` stops at the first `>`, which is what a human means by "a tag".

But notice the third line. `<[^>]+>` gives the same answer as the lazy
version, and it is the better pattern: "characters that are not `>`" states
the intent directly and cannot backtrack, where `.+?` has to try, fail, and
extend one character at a time.

**Prefer a negated character class to a lazy dot** when you can. Save laziness
for when the terminator is more than one character, as in `<!--.*?-->`.

## Lookahead and lookbehind

Lookaround asserts that something is (or is not) next to the current
position, **without consuming it**. The match keeps its position; only the
condition is checked.

| Syntax | Name | Means |
|---|---|---|
| `(?=...)` | lookahead | what follows must match |
| `(?!...)` | negative lookahead | what follows must **not** match |
| `(?<=...)` | lookbehind | what precedes must match |
| `(?<!...)` | negative lookbehind | what precedes must **not** match |

Two practical uses.

### Use 1 — rules that must all hold

The classic password policy, where each lookahead is an independent
requirement checked from the same starting position:

```python
import re

PASSWORD = re.compile(r"""
    ^                 # from the very start
    (?=.*[a-z])       # somewhere ahead: a lowercase letter
    (?=.*[A-Z])       # somewhere ahead: an uppercase letter
    (?=.*\d)          # somewhere ahead: a digit
    (?=.*[^\w\s])     # somewhere ahead: a symbol
    .{10,}            # and the whole thing is at least 10 characters
    $
""", re.VERBOSE)

for pw in ["short1A!", "alllowercase1!", "NoDigits!!!!", "Str0ng!Passw0rd"]:
    print(f"{pw:<18} {bool(PASSWORD.fullmatch(pw))}")
```

```text
short1A!           False
alllowercase1!     False
NoDigits!!!!       False
Str0ng!Passw0rd    True
```

Without lookahead you would need four separate patterns and four `if`s; with
it, the four rules stack up at one position and the `.{10,}` then does the
actual consuming. (In production, report *which* rule failed — a single
boolean is a poor user experience.)

### Use 2 — matching in context

Extract a number only when it follows a currency symbol, or split on a
delimiter that is not inside quotes:

```python
import re

invoice = "subtotal $42.50, shipping $7, discount 15 percent, total $49.50"

print("after $ only :", re.findall(r"(?<=\$)\d+(?:\.\d{2})?", invoice))
print("not after $  :", re.findall(r"(?<!\$)\b\d+(?= percent)", invoice))

# A comma is a field separator only when the quotes are balanced ahead of it
row = 'name,"Lovelace, Ada",1815,"mathematician, first programmer"'
FIELD_COMMA = r',(?=(?:[^"]*"[^"]*")*[^"]*$)'
print("naive split  :", row.split(","))
print("quote-aware  :", re.split(FIELD_COMMA, row))
```

```text
after $ only : ['42.50', '7', '49.50']
not after $  : ['15']
naive split  : ['name', '"Lovelace', ' Ada"', '1815', '"mathematician', ' first programmer"']
quote-aware  : ['name', '"Lovelace, Ada"', '1815', '"mathematician, first programmer"']
```

The lookahead reads "from here to the end of the line, quotes come in pairs",
which is true exactly when this comma is *outside* a quoted field.

It is a lovely trick — and you should still use the `csv` module for real CSV,
which handles doubled quotes, embedded newlines, and encodings that this
one-liner does not.

!!! warning "Python's lookbehind must be fixed width"

    `(?<=\$)` is fine; `(?<=\$+)` and `(?<=cat|elephant)` raise
    `re.error: look-behind requires fixed-width pattern`, because the engine
    has to know how far back to step. Alternatives of the *same* length are
    allowed (`(?<=cat|dog)`). .NET permits arbitrary variable-length lookbehind
    and JavaScript has since ES2018; Java allows only a *bounded* one —
    `(?<=a{1,5})` compiles, `(?<=a+)` does not. Go's RE2 has no lookaround
    at all — this is one of the least portable corners of regex.

## Catastrophic backtracking, and why it matters

Here is the one regex failure mode that can take down a service. Consider
this pattern and this input — **do not run them**:

```text
pattern:  (a+)+b
input:    "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"      (30 a's, no b)
```

The pattern says: "one or more groups, each of one or more `a`s, then a `b`."
There is no `b`, so the match must fail — but before failing the engine has to
prove that *no* arrangement works.

And the number of arrangements is the number of ways to split 30 `a`s into
groups: $2^{29}$, over five hundred million. Each one is tried. A 30-character
input hangs the process; a 40-character input outlives the universe's
patience. This is **catastrophic backtracking**, and when the input comes from
a user it is a denial-of-service vulnerability with its own name: **ReDoS**.

**The shape to fear is a quantifier inside another quantifier where the two
can match the same text**: `(a+)+`, `(a*)*`, `(\w+\s?)*`, `(.*,)*`. Real
outages have been caused by patterns exactly this innocent-looking —
including one that took a large content-delivery network offline in 2019.

Three defences, in order of preference:

1. **Do not nest quantifiers.** `(a+)+b` and `a+b` accept precisely the same
   strings, and `a+b` cannot blow up. Ask of every nested quantifier: is
   there more than one way for this to match the same text? If yes, rewrite.
2. **Be specific instead of using `.*`.** `"[^"]*"` cannot backtrack into
   another field the way `".*"` can.
3. **Anchor, and bound.** `^` stops the engine from retrying at every
   position, and `{1,20}` puts a ceiling on the work.

The cost of the missing anchor is easy to measure — with a **safe** pattern,
so nothing hangs:

```python
import re, time

print(f"{'n':>7}{'unanchored a+b (ms)':>22}{'anchored ^a+b (ms)':>22}")
for n in (2_000, 4_000, 8_000, 16_000):
    text = "a" * n                      # no 'b': both patterns must fail

    t0 = time.perf_counter()
    re.search(r"a+b", text)             # retries at every start position
    t1 = time.perf_counter()
    re.search(r"^a+b", text)            # can only start at position 0
    t2 = time.perf_counter()

    print(f"{n:>7}{(t1 - t0) * 1000:>22.2f}{(t2 - t1) * 1000:>22.3f}")
```

```text
      n   unanchored a+b (ms)    anchored ^a+b (ms)
   2000                  1.20                 0.011
   4000                  4.61                 0.003
   8000                 18.12                 0.005
  16000                 72.17                 0.011
```

The absolute milliseconds depend on your machine; the shape does not. Double
$n$ and the unanchored version takes four times as long — quadratic, because
it retries the whole scan from every starting position. The anchored version
is flat: it fails once, at position 0, and stops.

Neither is catastrophic — there is no nested quantifier here. But the same
arithmetic that turns $n$ into $n^2$ is what turns $n$ into $2^n$ when
quantifiers nest.

!!! tip "Atomic groups and possessive quantifiers"

    Python 3.11 added `(?>...)` (atomic group) and `a*+`, `a++`, `a?+`
    (possessive quantifiers). They tell the engine "having matched this,
    never give any of it back", which structurally forbids the backtracking
    explosion: `(?>a+)b` and `a++b` fail immediately on a string of `a`s.
    Java has had both for years. They are a good safety belt for patterns fed
    by untrusted input — but the first defence remains the best one: do not
    write the nested quantifier in the first place.

## A worked project: parsing a log into records

Everything so far, applied at once. The block writes a small log file, parses
it with one verbose named-group pattern, turns the matches into records, and
reports. This is the shape of a real log-analysis script.

```python
import re

# --- create the log file so the parser has something to read -------------
with open("server_access.log", "w", encoding="utf-8") as f:
    f.write("""\
203.0.113.7 - - [05/Feb/2024:10:12:44] "GET /index.html HTTP/1.1" 200 5120
198.51.100.22 - - [05/Feb/2024:10:12:45] "GET /admin HTTP/1.1" 403 210
203.0.113.7 - - [05/Feb/2024:10:12:46] "POST /api/login HTTP/1.1" 200 88
-- corrupt line, no fields at all --
198.51.100.22 - - [05/Feb/2024:10:13:01] "GET /admin HTTP/1.1" 403 210
192.0.2.66 - - [05/Feb/2024:10:13:09] "GET /cart HTTP/1.1" 500 0
203.0.113.7 - - [05/Feb/2024:10:14:22] "GET /index.html HTTP/1.1" 200 5120
198.51.100.22 - - [05/Feb/2024:10:15:00] "DELETE /api/user/7 HTTP/1.1" 500 0
""")

LOG = re.compile(r"""
    ^(?P<ip>\d{1,3}(?:\.\d{1,3}){3})\s+\S+\s+\S+\s+   # dotted-quad address
    \[(?P<time>[^\]]+)\]\s+                           # [timestamp]
    "(?P<method>[A-Z]+)\s(?P<path>\S+)[^"]*"\s+       # "METHOD /path HTTP/x"
    (?P<status>\d{3})\s+(?P<size>\d+)$                # status and byte count
""", re.VERBOSE)

records, skipped = [], []
with open("server_access.log", encoding="utf-8") as f:
    for line in f:
        m = LOG.match(line.strip())
        if m is None:
            skipped.append(line.strip())
            continue
        record = m.groupdict()
        record["status"] = int(record["status"])
        record["size"] = int(record["size"])
        records.append(record)

print(f"parsed {len(records)} records, skipped {len(skipped)}")
print("skipped:", skipped)
print()

by_status = {}
by_path = {}
for r in records:
    by_status[r["status"]] = by_status.get(r["status"], 0) + 1
    by_path[r["path"]] = by_path.get(r["path"], 0) + 1

print("status counts:", dict(sorted(by_status.items())))
print("busiest paths:", sorted(by_path.items(), key=lambda kv: (-kv[1], kv[0]))[:3])

failures = [r for r in records if r["status"] >= 400]
print(f"failure rate : {len(failures)}/{len(records)}"
      f" = {100 * len(failures) / len(records):.0f}%")

offenders = {}
for r in failures:
    offenders[r["ip"]] = offenders.get(r["ip"], 0) + 1
print("failing IPs  :", sorted(offenders.items(), key=lambda kv: -kv[1]))
print("bytes served :", sum(r["size"] for r in records))
```

```text
parsed 7 records, skipped 1
skipped: ['-- corrupt line, no fields at all --']

status counts: {200: 3, 403: 2, 500: 2}
busiest paths: [('/admin', 2), ('/index.html', 2), ('/api/login', 1)]
failure rate : 4/7 = 57%
failing IPs  : [('198.51.100.22', 3), ('192.0.2.66', 1)]
bytes served : 10748
```

Three habits from that code are worth copying:

1. **The pattern is a named constant in verbose mode, with comments** — not an
   inline mystery string.
2. **Non-matching lines are collected, not ignored.** A parser that silently
   drops what it does not understand will hide the day the log format changes.
3. **Conversion to `int` happens at the boundary**, right after matching, so
   the rest of the program works with numbers rather than strings.

Drop this loop into a generator pipeline from
[section 39.3](../ch39-streams/03-pipelines.md) and it will stream a
multi-gigabyte log in constant memory.

## When *not* to use regex

Regular expressions are named after **regular** languages, and the core
notation describes exactly those — a regular language cannot count.
(Backreferences and lookaround push real engines a little past that line, but
nowhere near far enough to track nesting depth.) It has no memory of how deep it
is, which means it fundamentally cannot match nested structure. Here is that
theory as an experiment:

```python
import re

html = "<div><div>a</div></div><div>b</div>"

print("greedy:", re.findall(r"<div>(.*)</div>", html))
print("lazy  :", re.findall(r"<div>(.*?)</div>", html))
print("neither of those is 'the contents of each outer div'")

import json
raw = '{"name": "Ada, \\"the countess\\"", "id": 7}'
print()
print("regex :", re.search(r'"name":\s*"([^"]*)"', raw).group(1))
print("json  :", json.loads(raw)["name"])
```

```text
greedy: ['<div>a</div></div><div>b']
lazy  : ['<div>a', 'b']
neither of those is 'the contents of each outer div'

regex : Ada, \
json  : Ada, "the countess"
```

The greedy pattern ran to the last `</div>` in the string; the lazy one
stopped at the first. Neither is right, and **no amount of tweaking makes it
right**, because "the matching close tag" requires counting how many opens are
still outstanding — precisely what a regular language cannot do.

The JSON example fails the same way: the pattern stops at the first `"`, which
here is an *escaped* quote inside the value.

Use a parser for anything with nesting or escaping:

| Format | Use this instead | Not this |
|---|---|---|
| HTML / XML | `html.parser`, an XML library | a tag-matching pattern |
| JSON | `json.loads` | a key-matching pattern |
| CSV | the `csv` module | `line.split(",")` or a lookahead |
| URLs | `urllib.parse` | a mega-pattern |
| Dates | `datetime.strptime` | month-range arithmetic in a pattern |
| Email addresses | send a confirmation message | any "validating" pattern |

That last row is not a joke. The grammar for a legal email address runs for
pages; every short "email regex" on the internet rejects addresses that are
valid and accepts some that are not. Check for an `@` with something on both
sides, then prove the address exists by mailing it.

**Regex remains the right tool for flat, line-oriented, shape-defined text:**
log lines, identifiers, tokens, phone numbers, hex colours, search-and-replace
across a codebase, and the first pass of a hand-written tokenizer — which is
[the last exercise](exercises.md) of this chapter.

## The same patterns elsewhere

The core syntax — classes, quantifiers, anchors, groups, alternation — is the
same everywhere. The API around it is not.

### The flavours, side by side

| | Python `re` | Java | JavaScript | POSIX `grep -E` / `sed -E` | Go / RE2 |
|---|---|---|---|---|---|
| Search anywhere | `re.search` | `matcher.find()` | `str.match(/…/)` | the default | `FindString` |
| Match the whole string | `re.fullmatch` | `String.matches()` | `/^…$/` | `^…$` | `^…$` |
| All matches | `re.findall` / `finditer` | `while (m.find())` | needs the `g` flag | the default | `FindAllString` |
| Escaping in source | raw strings: `r"\d"` | doubled: `"\\d"` | literal: `/\d/` | shell-quoted | backticks |
| `\d`, `\w`, `\s` | yes, Unicode-aware | yes | yes | **no** — use `[0-9]`, `[[:digit:]]` | yes |
| Named groups | `(?P<name>…)` | `(?<name>…)` | `(?<name>…)`, read via `m.groups` | none | `(?P<name>…)` |
| Lookbehind | fixed width only | bounded (`a{1,5}`) | any width, since ES2018 | none | **none** |
| Backreferences | yes | yes | yes | with `-E`, yes | **none, by design** |
| Worst-case time | exponential | exponential | exponential | exponential | **linear, guaranteed** |

Two of those rows deserve a sentence each. `grep` **without** `-E` is POSIX
*basic* regex, where `+`, `?`, `|`, and `()` must be backslashed
(`grep 'a\+'`) — use `grep -E` for the syntax this chapter taught. And RE2,
used by Go and by several log platforms, drops backreferences and lookaround
precisely so that matching is guaranteed linear time: no ReDoS is possible, at
the price of expressiveness.

=== "Java"

    ```java
    Pattern LOG = Pattern.compile("(\\d{4})-(\\d{2})-(\\d{2})");
    Matcher m = LOG.matcher("due 2024-03-01");

    if (m.find()) {                       // find() == Python's search()
        System.out.println(m.group(1));   // "2024"
        System.out.println(m.group(0));   // the whole match
    }
    while (m.find()) { /* every subsequent match */ }

    // Careful: String.matches() is FULL-match, like Python's fullmatch()
    boolean ok = "2024-03-01".matches("\\d{4}-\\d{2}-\\d{2}");

    // Named groups exist, with a different spelling than Python's
    Pattern p = Pattern.compile("(?<year>\\d{4})");
    ```

=== "JavaScript"

    ```javascript
    // Patterns are a literal type, delimited by slashes
    const DATE = /(\d{4})-(\d{2})-(\d{2})/g;   // g = find all

    "due 2024-03-01".match(DATE);              // ["2024-03-01"]
    [..."2024-03-01".matchAll(DATE)];          // match objects with groups

    const m = /(?<year>\d{4})/.exec("2024-03-01");
    m.groups.year;                             // "2024"

    "a   b".replace(/\s+/g, " ");              // sub() with the g flag
    ```

=== "Shell"

    ```console
    $ grep -E '^ERROR' app.log
    $ grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}' app.log | sort | uniq -c
    $ sed -E 's/[0-9]{3}-[0-9]{2}-[0-9]{4}/[REDACTED]/g' people.txt
    ```

!!! warning "The trap the table cannot show"

    **Java's `matches()` is a full match while `find()` is a search** — the
    opposite trap to Python's `match`, which anchors only the start. Carrying
    a pattern between the two without noticing is a real and quiet source of
    wrong answers.

    When a pattern must travel, stick to the common core: classes,
    quantifiers, anchors, groups, alternation. Leave lookbehind, named
    groups, and possessive quantifiers to the places you control.

!!! warning "Common mistakes"

    - **Renumbering groups by accident.** Adding `(...)` in the middle shifts
      every later number. Use `(?:...)` for grouping and names for capture.
    - **`.*` where `[^x]*` is meant.** The greedy dot crosses delimiters,
      quotes, and tags. Say what you actually allow.
    - **Nesting quantifiers.** `(\w+\s*)+` on untrusted input is a ReDoS
      waiting to happen. Flatten it.
    - **Forgetting that `sub` returns a new string.** Python strings are
      immutable; `re.sub(...)` does not modify anything in place.
    - **A replacement template that eats backslashes.** Write replacements as
      raw strings too: `r"\1-\2"`, never `"\1-\2"`.
    - **Parsing nested formats.** HTML, JSON, and YAML need parsers. A
      pattern that seems to work is a pattern that has not met real input.

## Check your understanding

??? success "1. What does `re.findall(r'(\\w+)@(\\w+)', 'ada@lab, grace@navy')` return?"

    `[('ada', 'lab'), ('grace', 'navy')]` — a list of **tuples**, because the
    pattern has two capturing groups and `findall` returns the groups rather
    than the whole match. To get `['ada@lab', 'grace@navy']`, make the groups
    non-capturing or use `finditer` and read `m.group(0)`.

??? success "2. Why does `r'<.+>'` match the entire string `'<b>hi</b>'`?"

    `.+` is greedy: it consumes to the end of the string, then gives
    characters back one at a time until the pattern can finish. The first `>`
    it finds while backing up is the *last* one in the string, so the match
    covers everything. `<.+?>` (lazy) or `<[^>]+>` (a negated class, and the
    better choice) both stop at the first `>`.

??? success "3. Why is `(a+)+b` dangerous while `a+b` is not?"

    They accept exactly the same strings, but `(a+)+` can split a run of
    `a`s into groups in exponentially many ways. On input that fails — a
    string of `a`s with no `b` — the engine tries every split before giving
    up: about $2^{\,n-1}$ attempts, which hangs the process. `a+b` has one way to match
    and fails in linear time. Never put a quantifier inside a quantifier when
    both can match the same characters.

??? success "4. When should you reach for a parser instead of a pattern?"

    When the format nests (HTML, XML, JSON, YAML, source code), when it has
    escaping rules (quoted CSV fields, JSON string escapes), or when the
    grammar is genuinely complicated (email addresses, URLs). Regex cannot
    count nesting depth — that is a property of regular languages, not a
    limitation of any particular engine — so a pattern for nested input is
    always a pattern that fails on some real input. Use the pattern for flat,
    line-oriented text, and hand the nested formats to `json`,
    `html.parser`, `csv`, or `urllib.parse`.
