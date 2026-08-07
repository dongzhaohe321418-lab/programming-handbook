# Chapter 41 · Exercises

Regex is learned at the keyboard: write the pattern, run it against text you
chose, and be wrong a few times. Every solution here is runnable, and several
of them print the *failing* version alongside the fixed one, because seeing
what a broken pattern does is more instructive than being told. Start with
the prediction exercise before you touch the Run button — the gap between
what you expected and what happened is where the learning is.

### Exercise 41.1 — Predict what these patterns match ●

**Write down your answers before running anything.** For each pattern and
sample, what does `re.findall` return?

```python
# (a) r"\d+"          on "a1bb22ccc333"
# (b) r"\bcat\b"      on "cat catalog concat cat."
# (c) r"go*d"         on "gd god goood gd"
# (d) r"[^aeiou\s]"   on "hi you"
# (e) r"\w+@\w+"      on "ada@lab and grace@navy"
# (f) r"a.c"          on "abc a-c ac a\nc"
```

??? success "Solution"

    ```python
    import re

    cases = [
        (r"\d+",        "a1bb22ccc333"),
        (r"\bcat\b",    "cat catalog concat cat."),
        (r"go*d",       "gd god goood gd"),
        (r"[^aeiou\s]", "hi you"),
        (r"\w+@\w+",    "ada@lab and grace@navy"),
        (r"a.c",        "abc a-c ac a\nc"),
    ]
    for label, (pattern, text) in zip("abcdef", cases):
        print(f"({label}) {pattern:<12} on {text!r:<26} -> {re.findall(pattern, text)}")
    ```

    ```text
    (a) \d+          on 'a1bb22ccc333'             -> ['1', '22', '333']
    (b) \bcat\b      on 'cat catalog concat cat.'  -> ['cat', 'cat']
    (c) go*d         on 'gd god goood gd'          -> ['gd', 'god', 'goood', 'gd']
    (d) [^aeiou\s]   on 'hi you'                   -> ['h', 'y']
    (e) \w+@\w+      on 'ada@lab and grace@navy'   -> ['ada@lab', 'grace@navy']
    (f) a.c          on 'abc a-c ac a\nc'          -> ['abc', 'a-c']
    ```

    The three that catch people: **(b)** `catalog` and `concat` both fail
    because `\b` needs a non-word character on *both* sides — `cat.` passes
    because a full stop is not a word character. **(c)** `gd` matches, since
    `o*` is happy with zero `o`s. **(f)** `ac` is missing (the dot demands one
    character) and so is `a\nc` (the dot excludes newlines unless you pass
    `re.DOTALL`).

### Exercise 41.2 — Choose the right function ●

For each task, say which of `re.search`, `re.match`, `re.fullmatch`,
`re.findall`, `re.finditer`, `re.sub`, or `re.split` you would use, then
write the call.

1. Is this entire string a valid four-digit year?
2. Does this log line contain an IP address anywhere?
3. Collect every hashtag in a social-media post.
4. Report each hashtag *and the position it starts at*.
5. Replace every run of whitespace with a single space.
6. Break `"a1b22c"` into its letter and number parts.

??? success "Solution"

    ```python
    import re

    print("1.", bool(re.fullmatch(r"\d{4}", "2024")),
              bool(re.fullmatch(r"\d{4}", "2024x")))

    line = "203.0.113.7 requested /index.html"
    print("2.", bool(re.search(r"\b\d{1,3}(?:\.\d{1,3}){3}\b", line)))

    post = "loving #regex and #python, but not #regexgolf"
    print("3.", re.findall(r"#\w+", post))

    print("4.", [(m.group(), m.start()) for m in re.finditer(r"#\w+", post)])

    print("5.", re.sub(r"\s+", " ", "too    many \t spaces"))
    print("6.", re.split(r"(\d+)", "a1b22c"))
    ```

    ```text
    1. True False
    2. True
    3. ['#regex', '#python', '#regexgolf']
    4. [('#regex', 7), ('#python', 18), ('#regexgolf', 35)]
    5. too many spaces
    6. ['a', '1', 'b', '22', 'c']
    ```

    The decisions in one line each: **whole string → `fullmatch`**
    (never `match`, which ignores whatever follows); **somewhere → `search`**;
    **all of them → `findall`**, unless you need positions or groups, in which
    case **`finditer`**; **rewrite → `sub`**; **break apart → `split`**, with
    a capturing group when you want the separators back.

### Exercise 41.3 — Validate phone numbers and hex colours ●●

Write two patterns and test each against valid and invalid input.

1. A North-American phone number in any of these shapes:
   `555-867-5309`, `(555) 867-5309`, `555.867.5309`, `+1 555 867 5309`.
   Reject anything with the wrong number of digits.
2. A CSS hex colour: `#fff`, `#FFFFFF`, `#1a2b3c` — exactly three or six hex
   digits after the `#`, and nothing else.

??? success "Solution"

    ```python
    import re

    PHONE = re.compile(r"""
        ^
        (?:\+1[ .-]?)?         # optional country code
        \(?\d{3}\)?            # area code, optionally in parentheses
        [ .-]?
        \d{3}                  # exchange
        [ .-]?
        \d{4}                  # line number
        $
    """, re.VERBOSE)

    HEX = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")

    phones = ["555-867-5309", "(555) 867-5309", "555.867.5309",
              "+1 555 867 5309", "5558675309",
              "555-8675-309", "55-867-5309", "555-867-530x"]
    for p in phones:
        print(f"{p:<18} {bool(PHONE.fullmatch(p))}")

    print()
    colours = ["#fff", "#FFFFFF", "#1a2b3c", "#ff", "#12345", "fff", "#gggggg"]
    for c in colours:
        print(f"{c:<10} {bool(HEX.fullmatch(c))}")
    ```

    ```text
    555-867-5309       True
    (555) 867-5309     True
    555.867.5309       True
    +1 555 867 5309    True
    5558675309         True
    555-8675-309       False
    55-867-5309        False
    555-867-530x       False

    #fff       True
    #FFFFFF    True
    #1a2b3c    True
    #ff        False
    #12345     False
    fff        False
    #gggggg    False
    ```

    Both patterns are anchored, and `fullmatch` makes that doubly sure — a
    validator without anchors accepts `"call 555-867-5309 now"` as a phone
    number. The hex pattern puts the longer alternative *second* only because
    the anchors make order irrelevant here; without `$`, `[0-9a-f]{3}` would
    match the first three characters of a six-digit colour and stop.

    !!! warning "Do not try this with email addresses"

        The same exercise for email is a trap. The real grammar (RFC 5322)
        allows quoted local parts, comments, and characters you would never
        guess; every compact "email regex" rejects addresses that are legal
        and accepts some that are not. Check that there is an `@` with
        something on either side, then **send a confirmation message** —
        delivery is the only real validation.

### Exercise 41.4 — Fix a greedy pattern ●●

This function is supposed to strip HTML tags from a string. It removes far
too much. Explain why, then fix it two ways.

```python
import re

def strip_tags(html):
    return re.sub(r"<.+>", "", html)

print(strip_tags("<p>Hello <b>there</b>, friend</p>"))
```

??? success "Solution"

    ```python
    import re

    html = "<p>Hello <b>there</b>, friend</p>"

    print("broken :", repr(re.sub(r"<.+>", "", html)))
    print("lazy   :", repr(re.sub(r"<.+?>", "", html)))
    print("class  :", repr(re.sub(r"<[^>]+>", "", html)))

    # what the greedy pattern actually matched
    m = re.search(r"<.+>", html)
    print("greedy match:", repr(m.group()))
    ```

    ```text
    broken : ''
    lazy   : 'Hello there, friend'
    class  : 'Hello there, friend'
    greedy match: '<p>Hello <b>there</b>, friend</p>'
    ```

    `.+` is greedy: it runs to the end of the string, then gives characters
    back until the pattern can finish, and the first `>` it meets on the way
    back is the *last* one in the whole string. So the "tag" it matched was
    the entire input, and substituting it away left nothing.

    Both fixes work; `<[^>]+>` is the better one, because "characters that
    are not `>`" says exactly what a tag body is and cannot backtrack, while
    `<.+?>` has to extend one character at a time. And the honest footnote:
    neither is a safe HTML stripper for untrusted input — comments, `<script>`
    contents, and attributes containing `>` all break it. Use a real parser
    (`html.parser`) when the input is not yours.

### Exercise 41.5 — Extract with named groups ●●

Parse these configuration lines into a list of dictionaries with the keys
`section`, `key`, `value`, and `unit` (the unit is optional). Skip comments
and blank lines, and report anything you could not parse.

```text
# server settings
http.timeout = 30s
http.retries = 5
db.pool_size = 20
db.idle_timeout = 300s
this line is broken
cache.ttl = 15m
```

??? success "Solution"

    ```python
    import re

    CONFIG = re.compile(r"""
        ^\s*
        (?P<section>\w+)\.(?P<key>\w+)      # section.key
        \s*=\s*
        (?P<value>\d+)(?P<unit>[a-z]+)?     # a number and an optional unit
        \s*$
    """, re.VERBOSE)

    text = """\
    # server settings
    http.timeout = 30s
    http.retries = 5
    db.pool_size = 20
    db.idle_timeout = 300s
    this line is broken
    cache.ttl = 15m
    """

    records, bad = [], []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        m = CONFIG.match(line)
        if m is None:
            bad.append(line)
            continue
        record = m.groupdict()
        record["value"] = int(record["value"])
        records.append(record)

    for r in records:
        unit = r["unit"] or "-"
        print(f"{r['section']:<7}{r['key']:<14}{r['value']:>5}  unit={unit}")
    print("unparsed:", bad)

    seconds = {"s": 1, "m": 60, "h": 3600}
    total = sum(r["value"] * seconds[r["unit"]] for r in records if r["unit"])
    print("total configured time:", total, "seconds")
    ```

    ```text
    http   timeout          30  unit=s
    http   retries           5  unit=-
    db     pool_size        20  unit=-
    db     idle_timeout    300  unit=s
    cache  ttl              15  unit=m
    unparsed: ['this line is broken']
    total configured time: 1230 seconds
    ```

    Three things to copy from this. An optional group that does not
    participate yields `None`, not `""` — hence `r["unit"] or "-"`. Failures
    are collected rather than ignored, so a format change announces itself.
    And `groupdict()` plus one `int()` conversion turns a line of text into a
    record the rest of the program can compute with.

### Exercise 41.6 — Rewrite with a replacement function ●●

Write a `sub` whose replacement is a **function**, to convert every Celsius
temperature in a report to Fahrenheit, keeping one decimal place. Then write a
second one that partially masks email addresses: keep the first character of
the local part and the whole domain.

??? success "Solution"

    ```python
    import re

    report = "Highs of 21C in Oslo, 35.5C in Cairo, and -3C in Tromso."

    def to_fahrenheit(m):
        celsius = float(m.group("value"))
        return f"{celsius * 9 / 5 + 32:.1f}F"

    TEMP = re.compile(r"(?P<value>-?\d+(?:\.\d+)?)C\b")
    print(TEMP.sub(to_fahrenheit, report))

    contacts = "write to ada@lab.example or grace.hopper@navy.mil today"

    def mask_email(m):
        local, domain = m.group("local"), m.group("domain")
        return f"{local[0]}{'*' * (len(local) - 1)}@{domain}"

    EMAIL = re.compile(r"\b(?P<local>[\w.+-]+)@(?P<domain>[\w.-]+\.\w+)\b")
    print(EMAIL.sub(mask_email, contacts))
    print("addresses found:", [m.group() for m in EMAIL.finditer(contacts)])
    ```

    ```text
    Highs of 69.8F in Oslo, 95.9F in Cairo, and 26.6F in Tromso.
    write to a**@lab.example or g***********@navy.mil today
    addresses found: ['ada@lab.example', 'grace.hopper@navy.mil']
    ```

    The replacement function receives the match object, so it can do
    arithmetic, look things up, or decide to change nothing (return
    `m.group()`). Note `-?` in the temperature pattern — without it, `-3C`
    converts to `37.4F` instead of `26.6F`, and nothing warns you. And the
    email pattern here is *deliberately* loose: it is fine for finding
    addresses in prose, and it is not a validator.

### Exercise 41.7 — Find the bug in a pattern ●●

A colleague's version-number matcher passes their tests and fails in
production. Find both bugs, then fix the pattern.

```python
import re

VERSION = r"\d.\d.\d"

for s in ["1.2.3", "1.10.2", "release 1x2y3 build"]:
    print(s, "->", re.findall(VERSION, s))
```

??? success "Solution"

    ```python
    import re

    BROKEN = r"\d.\d.\d"
    FIXED = r"\d+\.\d+\.\d+"

    tests = ["1.2.3", "1.10.2", "release 1x2y3 build", "v2.0.15 shipped",
             "phone 5551234567"]
    print(f"{'input':<24}{'broken':<24}{'fixed'}")
    for s in tests:
        print(f"{s:<24}{str(re.findall(BROKEN, s)):<24}{re.findall(FIXED, s)}")
    ```

    ```text
    input                   broken                  fixed
    1.2.3                   ['1.2.3']               ['1.2.3']
    1.10.2                  []                      ['1.10.2']
    release 1x2y3 build     ['1x2y3']               []
    v2.0.15 shipped         ['2.0.1']               ['2.0.15']
    phone 5551234567        ['55512', '34567']      []
    ```

    **Bug one: unescaped dots.** `.` means "any character", so `1x2y3` looks
    like a version number, and a plain phone number splits into two bogus
    "versions" — the pattern really means "digit, any, digit, any, digit".
    Escape them: `\.`

    **Bug two: single digits.** `\d` matches exactly one digit, so `2.0.15`
    loses its final `5`, and `1.10.2` fails entirely: after `1`, any, `1`,
    any (`0`), the fifth character must be a digit and it is a dot.

    One tempting extra "fix" is wrong: wrapping the pattern in `\b…\b` looks
    tidier but breaks on `v2.0.15`, because `v` and `2` are both word
    characters and there is no boundary between them. If you need to stop the
    pattern reporting a fragment of something longer, guard it with
    lookaround instead — `(?<![\d.])\d+\.\d+\.\d+(?![\d.])`. The general
    lesson is that a pattern which passes on the happy path can still be
    wrong in two independent ways: test the edge cases (two-digit components,
    adjacent text, no separators) deliberately.

### Exercise 41.8 — A tokenizer for arithmetic expressions ●●●

Write a tokenizer for a small expression language using a single
`re.finditer` over an alternation of **named** groups. The token kinds are:

- `NUMBER` — an integer or decimal, e.g. `42`, `3.14`
- `NAME` — an identifier starting with a letter or underscore
- `OP` — one of `+ - * / ^`
- `LPAREN`, `RPAREN` — parentheses
- whitespace, which is skipped
- anything else, which is a syntax error reporting its position

Tokenize `3 + 4.5*(x_1 - 2)^2 / rate` and verify the token stream. Then show
what happens on input containing an illegal character.

??? success "Solution"

    ```python
    import re

    TOKEN = re.compile(r"""
          (?P<NUMBER>\d+(?:\.\d+)?)     # 42 or 3.14 -- integer part required
        | (?P<NAME>[A-Za-z_]\w*)        # x, rate, x_1
        | (?P<OP>[-+*/^])               # a single operator character
        | (?P<LPAREN>\()
        | (?P<RPAREN>\))
        | (?P<SKIP>\s+)                 # whitespace: recognised, then dropped
        | (?P<BAD>.)                    # anything else is an error
    """, re.VERBOSE)

    def tokenize(source):
        """Yield (kind, text, position) triples; raise on an illegal char."""
        for m in TOKEN.finditer(source):
            kind = m.lastgroup                 # the name of the group that matched
            if kind == "SKIP":
                continue
            if kind == "BAD":
                raise ValueError(
                    f"illegal character {m.group()!r} at position {m.start()}"
                )
            yield (kind, m.group(), m.start())

    source = "3 + 4.5*(x_1 - 2)^2 / rate"
    tokens = list(tokenize(source))

    print(f"{len(tokens)} tokens from {source!r}\n")
    for kind, text, pos in tokens:
        print(f"  {pos:>3}  {kind:<7} {text!r}")

    expected = ["NUMBER", "OP", "NUMBER", "OP", "LPAREN", "NAME", "OP",
                "NUMBER", "RPAREN", "OP", "NUMBER", "OP", "NAME"]
    print("\nkinds match expectation:", [k for k, _, _ in tokens] == expected)
    print("text round-trips        :",
          "".join(t for _, t, _ in tokens) == source.replace(" ", ""))

    try:
        list(tokenize("2 + $x"))
    except ValueError as e:
        print("error case              :", e)
    ```

    ```text
    13 tokens from '3 + 4.5*(x_1 - 2)^2 / rate'

        0  NUMBER  '3'
        2  OP      '+'
        4  NUMBER  '4.5'
        7  OP      '*'
        8  LPAREN  '('
        9  NAME    'x_1'
       13  OP      '-'
       15  NUMBER  '2'
       16  RPAREN  ')'
       17  OP      '^'
       18  NUMBER  '2'
       20  OP      '/'
       22  NAME    'rate'

    kinds match expectation: True
    text round-trips        : True
    error case              : illegal character '$' at position 4
    ```

    This is how real tokenizers are written, and three details make it work.
    `m.lastgroup` gives the **name** of whichever alternative matched, so one
    pass over the input classifies every token — no chain of `if` statements.
    **Order matters** inside the alternation: `NUMBER` comes before `NAME` so
    that `42` is not read as an identifier, and the catch-all `BAD` comes
    last so it only fires when nothing else fits. And `finditer` scans left to
    right without skipping, so `BAD` reports the exact position of the
    offending character, which is what turns "syntax error" into a message a
    user can act on.

    From here, a parser turns this flat token stream into a tree — which is
    exactly the step regex cannot take for you, for the reason
    [41.2](02-groups-parsing.md) gave: nesting requires counting, and a
    regular language cannot count.
