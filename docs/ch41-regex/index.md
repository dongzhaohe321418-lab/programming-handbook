# Chapter 41 · Regular Expressions

Somewhere in every program that touches text there is a function that has
grown too big: fifteen lines of `split`, `strip`, `startswith`, and index
arithmetic, all to answer one question — is this a valid date? which of these
lines is an error? what is the customer id inside this message? A **regular
expression** answers that class of question in a single line, and it does so
in a notation that is nearly identical in Python, Java, JavaScript, Go, Ruby,
C#, `grep`, `sed`, your editor's search box, and the query language of most
log-analysis tools. It is the highest-leverage small language a programmer
can learn.

The catch is that regex has a reputation, and it is partly deserved. A
pattern is dense — `^\d{4}-\d{2}-\d{2}$` is a whole program in nineteen
characters — and dense notation read too fast becomes noise. This chapter
therefore refuses to show you a pattern you have not seen run. Every single
construct on these pages is executed against real strings with its matches
printed, because the only way to trust a pattern is to watch what it does to
text you chose. Python's `re` module is in the standard library, so unlike
the shell and the build tools of Chapter 40, **all of this runs right here**.

[Section 41.1](01-fundamentals.md) builds the notation from literals up to
anchors and quantifiers, then teaches the `re` API properly — including the
`search`/`match`/`fullmatch` distinction that causes more confusion than any
other part of the module, and the raw-string rule that prevents the
backslash plague. [Section 41.2](02-groups-parsing.md) turns matching into
**parsing**: capturing groups pull fields out of a log line, named groups
give them names, replacement functions rewrite text programmatically, and
lookaround expresses conditions that plain matching cannot. It ends with the
two things a professional needs and a tutorial usually skips: why a badly
written pattern can hang a server (and how to avoid writing one), and when to
put the regex away and use a parser instead.

## After this chapter you can …

- recognise the kind of problem regex is for, and write the pattern instead of
  fifteen lines of string methods;
- read and write character classes, ranges, negation, `\d \w \s`, the dot,
  anchors `^ $ \b`, quantifiers `* + ? {m,n}`, alternation, and grouping;
- choose correctly between `search`, `match`, and `fullmatch`, and explain
  what each one anchors;
- use `findall`, `finditer`, `sub`, `split`, and `compile`, and know which one
  gives you match objects and which gives you strings;
- apply the flags `re.I`, `re.M`, `re.S`, and `re.X`, and lay out a long
  pattern in verbose mode with comments;
- explain the backslash plague and why every pattern belongs in a raw string;
- capture fields with numbered groups, name them with `(?P<name>...)`, and
  pull a dict straight out of a match with `groupdict()`;
- say why `(?:...)` exists and when to reach for it;
- write a backreference, and find doubled words with one;
- replace text with `sub`, using both a template and a **function**, and mask
  sensitive data with the function form;
- explain greedy versus lazy quantifiers and predict which one swallows too
  much;
- use lookahead and lookbehind for password rules and quote-aware splitting;
- explain catastrophic backtracking and ReDoS, recognise the nested-quantifier
  shape that causes it, and write patterns that cannot;
- parse a realistic multi-line log into structured records and report on it;
- state plainly why HTML, JSON, and other nested formats need a parser rather
  than a pattern;
- carry your patterns to Java, JavaScript, `grep`, and `sed`, and know which
  parts do not travel.

## Prerequisites

- [Chapter 3 · Strings](../ch03-functions/02-strings.md) — the string methods
  regex extends: `split`, `strip`, `startswith`, `replace`, and slicing.
- [Chapter 6 · Loops](../ch06-loops/index.md) — `finditer` is consumed with a
  `for` loop.
- [Chapter 9 · Collections](../ch09-collections/index.md) — matches are
  collected into lists and dicts.
- [Chapter 11 · Files](../ch11-files/index.md) — the log-parsing project reads
  a file line by line.
- Helpful: [Chapter 39](../ch39-streams/index.md) — a regex stage drops
  straight into a generator pipeline, and the log project is exactly that
  shape. Not required.

## Sections

1. [41.1 Regex fundamentals](01-fundamentals.md) — where string methods run
   out of road, the notation built one construct at a time with every piece
   executed, `search` versus `match` versus `fullmatch`, `findall`,
   `finditer`, `sub`, `split`, `compile`, the four flags including verbose
   mode, raw strings and the backslash plague, and a cumulative reference
   table whose every row is run on the page.
2. [41.2 Groups, greediness, and real parsing](02-groups-parsing.md) —
   numbered and named capturing groups on a log parser, `groups()` and
   `groupdict()`, non-capturing groups, backreferences, `sub` with a template
   and with a function (masking card numbers), greedy versus lazy side by
   side, lookahead and lookbehind, catastrophic backtracking and ReDoS
   explained safely, a full multi-line log-parsing project, when *not* to use
   regex, and the same patterns in Java, JavaScript, `grep`, and `sed`.
3. [Exercises](exercises.md) — predict what a pattern matches, write and
   validate patterns for phone numbers and hex colours, fix a greedy pattern,
   extract with named groups, rewrite text with a replacement function, debug
   a pattern that fails on edge cases, and build a tokenizer for a small
   arithmetic language with `finditer`.
