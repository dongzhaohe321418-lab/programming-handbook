# 3.2 Strings

Most of the data your programs will ever touch is text: names, file paths,
messages, web pages, CSV rows. Python's string type, `str`, is the most
heavily used object in the language and the richest in behaviour. This
section gives you the full toolkit — how string values are written, how to
reach inside them with indexing and slicing, the methods you will use daily —
plus one rule that governs everything: strings can never be changed, only
replaced.

## Literals, quotes, and escapes

A **string literal** is text written directly in your code, wrapped in
matching quotes. Python accepts single `'...'` or double `"..."` quotes —
they mean exactly the same thing, which is handy when your text itself
contains a quote character. For characters you cannot type directly, an
**escape sequence** — a backslash followed by a code letter — stands in:
`\n` is a newline, `\t` a tab, `\\` a literal backslash, and `\"` a quote
mark inside a double-quoted string.

```python
single = 'He said, "amazing!"'      # double quotes inside single quotes
double = "It's a fine day"          # apostrophe inside double quotes
layout = "One\tTwo\tThree\nNext line"
windows = "The file lives in C:\\temp"

print(single)
print(double)
print(layout)
print(windows)
```

```text
He said, "amazing!"
It's a fine day
One	Two	Three
Next line
The file lives in C:\temp
```

The quotes and backslashes you *wrote* are not the characters the string
*contains*: `\n` is one character (a newline), not two, and the quotes
around a literal are packaging, not content.

## Strings are immutable

Here is the rule that explains half of string behaviour: strings are
**immutable** — once created, a string object can never be altered. Every
string method that "changes" a string actually builds and returns a **new**
string, leaving the original untouched:

```python
word = "python"
loud = word.upper()

print(loud)    # the new string
print(word)    # the original — completely unchanged
```

```text
PYTHON
python
```

Calling a string method and ignoring its result therefore does nothing at
all; the idiom you want is *reassignment* — `word = word.upper()` — which
points the variable at the new string. And if you try to edit a string in
place, Python refuses outright:

```python
# raises TypeError
word = "python"
word[0] = "P"    # strings do not support item assignment
```

The error — `TypeError: 'str' object does not support item assignment` — is
Python enforcing immutability. To "change" one character, build a new string
from pieces of the old one (slicing, below, makes this easy).

## Indexing — including from the end

A string is a *sequence*: its characters sit in numbered positions called
**indexes**, starting from `0`, and `len(s)` reports how many characters it
has. Square brackets fetch the character at a position. Negative indexes
count from the end, with `-1` as the last character:

```text
  +---+---+---+---+---+---+
  | p | y | t | h | o | n |
  +---+---+---+---+---+---+
    0   1   2   3   4   5      index
   -6  -5  -4  -3  -2  -1      negative index
```

```python
word = "python"
print(word[0])      # first character
print(word[5])      # last character (indexes run 0..len-1)
print(word[-1])     # also the last character
print(word[-6])     # also the first
print(len(word))
```

```text
p
n
n
p
6
```

Because indexes start at 0, the last valid index is `len(word) - 1`, not
`len(word)`. Step past the end and Python raises an error rather than guess:

```python
# raises IndexError
word = "python"
print(word[6])    # positions run 0..5 only
```

`IndexError: string index out of range` is one of the most common beginner
errors — it almost always means an off-by-one mistake in your arithmetic.

## Slicing: `[start:stop:step]`

Indexing fetches one character; **slicing** fetches a substring. The form is
`s[start:stop:step]` — begin at `start`, stop *just before* `stop`, taking
every `step`-th character. Each part is optional: `start` defaults to the
beginning, `stop` to the end, `step` to 1.

```python
word = "programming"
print(word[0:3])     # positions 0, 1, 2 — stop is NOT included
print(word[3:7])
print(word[:3])      # from the start
print(word[8:])      # to the end
print(word[::2])     # every second character
print(word[::-1])    # step -1: the whole string, reversed
```

```text
pro
gram
pro
ing
pormig
gnimmargorp
```

Two things to internalise. First, `stop` is **excluded** — a half-open
range, so `word[0:3]` has exactly $3 - 0 = 3$ characters and
`word[:k] + word[k:]` always reassembles the original. Second, slicing is
forgiving where indexing is strict: `word[8:1000]` quietly returns `"ing"`
instead of raising `IndexError`.

## The method tour

Strings have nearly fifty public methods. You do not need them all — the dozen
below cover almost everything you will do this year. Grouped by task:

| Task | Methods |
| --- | --- |
| Change case | `upper()`, `lower()`, `title()`, `capitalize()` |
| Search | `find(sub)`, `index(sub)`, `count(sub)`, the `in` operator |
| Clean up | `strip()`, `lstrip()`, `rstrip()` |
| Split & join | `split(sep)`, `sep.join(parts)` |
| Replace & test | `replace(old, new)`, `startswith(s)`, `endswith(s)` |

### Changing case

```python
s = "monty python"
print(s.upper())         # every letter uppercase
print(s.title())         # Each Word Capitalised
print(s.capitalize())    # only the first letter
print("LOUD".lower())
```

```text
MONTY PYTHON
Monty Python
Monty python
loud
```

### Searching

```python
line = "to be or not to be"
print(line.find("be"))        # index of the first match
print(line.find("question"))  # -1 means "not found"
print(line.index("be"))       # like find, but raises ValueError if absent
print(line.count("be"))
print("not" in line)          # the in operator: True/False membership test
print("maybe" in line)
```

```text
3
-1
3
2
True
False
```

Choose deliberately: `find` reports failure with the sentinel `-1`, which
your code must remember to check; `index` raises `ValueError` immediately —
safer when "not found" would be a bug. For a plain yes/no answer, `in` is
clearest of all.

### Cleaning up

`strip()` removes **whitespace** (spaces, tabs, newlines) from both ends —
the standard first step when handling anything a user typed. Its one-sided
siblings `lstrip()` and `rstrip()` trim only the left or right end. The
brackets in this demo make the invisible spaces visible:

```python
raw = "   ada@example.com   "
print("[" + raw + "]")
print("[" + raw.strip() + "]")     # both ends
print("[" + raw.rstrip() + "]")    # right end only
```

```text
[   ada@example.com   ]
[ada@example.com]
[   ada@example.com]
```

### Splitting and joining

`split` cuts a string into a **list** of pieces — lists get their full
treatment in [Chapter 7](../ch07-arrays/index.md); for now, you can `print`
one and pick items out with `[0]`, `[1]`, `[-1]`. With no argument, `split`
cuts on any run of whitespace; given a separator, on exactly that. `join` is
its inverse — it glues a list of strings together with the separator you
call it on:

```python
sentence = "the quick brown fox"
words = sentence.split()
print(words)
print(words[0], words[-1])

print("Lovelace,Ada,1815".split(","))
print(" | ".join(["one", "two", "three"]))
```

```text
['the', 'quick', 'brown', 'fox']
the fox
['Lovelace', 'Ada', '1815']
one | two | three
```

### Replacing and testing

```python
path = "report_draft.txt"
print(path.replace("draft", "final"))
print(path.startswith("report"))
print(path.endswith(".txt"))
```

```text
report_final.txt
True
True
```

Like every string method, `replace` returns a new string — `path` itself
still says `draft` afterwards.

## Comparing strings

The `==` operator asks "do these two strings contain exactly the same
characters?", and the ordering operators (`<`, `>`, `<=`, `>=`) compare
strings the way a dictionary would — character by character, by each
character's code number:

```python
print("apple" == "apple")
print("apple" == "Apple")     # case matters
print("apple" < "banana")     # a comes before b
print("ant" < "anteater")     # a prefix comes first
print("Zebra" < "apple")      # surprise! see below
print(ord("Z"), ord("a"))     # the code numbers being compared
```

```text
True
False
True
True
True
90 97
```

That last comparison is the classic gotcha: *all* uppercase letters have
smaller code numbers than *all* lowercase letters, so `"Zebra"` sorts before
`"apple"`. When you want human-style ordering, compare lowered copies:
`a.lower() < b.lower()`.

If you are also learning Java, string comparison is the single biggest trap
between the two languages:

=== "Python"

    ```python
    a = "hello"
    b = "hel" + "lo"
    print(a == b)     # True — == compares the characters
    ```

=== "Java"

    ```java
    String a = "hello";
    String b = new String("hello");
    System.out.println(a.equals(b));      // true  — same characters
    System.out.println(a == b);           // false — different objects!
    System.out.println(a.compareTo(b));   // 0 — equal in dictionary order
    ```

In Java, `==` between strings compares *object identity* — "are these the
very same object in memory?" — almost never the question you mean; Java code
must use `.equals()` for content and `.compareTo()` for ordering. Python's
`==` compares content directly. (Python's identity operator, `is`, has its
own trap — see
[Section 4.3](../ch04-branching/03-equality-identity.md).)

## Worked example: parsing "Last, First"

Directories and citation lists often store names as `"Last, First"` — with
unpredictable spacing. Let's turn `"  Lovelace ,  Ada  "` into a clean
`Ada Lovelace`. The plan: find the comma, slice off each side, strip the
mess.

```python
entry = "  Lovelace ,  Ada  "

comma = entry.find(",")            # 1. locate the separator
last = entry[:comma].strip()       # 2. everything before it, tidied
first = entry[comma + 1:].strip()  # 3. everything after it, tidied

print("First:", first)
print("Last: ", last)
print("Full: ", first + " " + last)
```

```text
First: Ada
Last:  Lovelace
Full:  Ada Lovelace
```

Note `comma + 1` in step 3: the slice must start *after* the comma itself.
`split` gives an even shorter version of the same idea — cut on the comma,
then tidy each piece:

```python
entry = "  Lovelace ,  Ada  "
parts = entry.split(",")
print(parts[1].strip() + " " + parts[0].strip())
```

```text
Ada Lovelace
```

Real text-processing code is mostly this: locate, slice, strip, reassemble.

!!! warning "Common mistakes"

    - **Expecting methods to modify the string**: `name.strip()` on its own
      line does nothing visible. Strings are immutable — capture the result:
      `name = name.strip()`.
    - **Off-by-one in slices**: `s[2:5]` contains positions 2, 3, 4 — the
      stop index is excluded. If a slice is one character short, this is why.
    - **Treating `find`'s `-1` as a position**: `-1` means "not found", but
      it is also a *valid index* (the last character!). Using an unchecked
      `find` result in a slice produces silently wrong answers — prefer
      `index` or test for `-1` first.
    - **Assuming comparisons ignore case**: `"Apple" == "apple"` is `False`,
      and `"Zebra" < "apple"` is `True`. Normalise with `.lower()` when you
      want human-style, case-blind comparisons.

## Check your understanding

1. Without running it, what does `"immutable"[2:5]` evaluate to?

    ??? success "Answer"
        `"mut"` — positions 2, 3, and 4; the character at stop index 5 is
        excluded.

2. Why does `word[0] = "P"` raise a `TypeError`, and what should you write
   instead to get a capitalised copy of `word = "python"`?

    ??? success "Answer"
        Strings are immutable, so item assignment is forbidden. Build a new
        string instead: `word = "P" + word[1:]` (or simply
        `word.capitalize()`), and reassign it to the variable.

3. `line.find("x")` returned `-1` and your code then evaluated
   `line[:line.find("x")]`. What substring did you actually get?

    ??? success "Answer"
        `line[:-1]` — everything except the last character. `-1` is a legal
        (negative) index, so no error occurs; the code is just quietly wrong.
        Check for `-1`, or use `index` so failure raises `ValueError`.

4. What does `print("Banana" < "apple")` output, and why?

    ??? success "Answer"
        `True`. Comparison uses character code numbers, and every uppercase
        letter (`B` is 66) is smaller than every lowercase letter (`a` is
        97), so `"Banana"` sorts first — regardless of alphabet intuition.
