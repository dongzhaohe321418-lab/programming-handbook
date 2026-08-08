# 6.4 Bitwise operators and enums

Back in [Chapter 0](../ch00-machine/02-binary.md) you learned that every
integer is stored as a pattern of bits, and in
[Chapter 2](../ch02-data/02-number-systems.md) you learned to read those
patterns. The **bitwise operators** finally let you *work* on them —
testing, setting, and clearing individual bits — which is how programs pack
many yes/no facts into a single integer (file permissions, hardware
registers, game states). We close with **enums**, the tool for the opposite
kind of constant: a small fixed set of named options where raw numbers or
strings would invite bugs.

## Six operators, one table

Bitwise operators treat an integer as a column of bits and combine the
columns position by position. Using $a = 12$ (`1100`) and $b = 10$ (`1010`):

| operator | name | rule per bit position | example | binary view | result |
| -------- | ---- | --------------------- | ------- | ----------- | ------ |
| `&` | AND | 1 only if **both** bits are 1 | `12 & 10` | `1100 & 1010` | `1000` = 8 |
| <code>&#124;</code> | OR | 1 if **either** bit is 1 | <code>12 &#124; 10</code> | <code>1100 &#124; 1010</code> | `1110` = 14 |
| `^` | XOR | 1 if the bits **differ** | `12 ^ 10` | `1100 ^ 1010` | `0110` = 6 |
| `~` | NOT | flip every bit | `~12` | see below | −13 |
| `<<` | left shift | slide bits left, fill with 0 | `12 << 1` | `11000` | 24 |
| `>>` | right shift | slide bits right, drop the end | `12 >> 2` | `11` | 3 |

The built-in `format(x, '04b')` renders an integer as binary padded to 4
digits — the ideal microscope for this section:

```python
a, b = 0b1100, 0b1010          # 12 and 10, written in binary
print("a     =", format(a, '04b'))
print("b     =", format(b, '04b'))
print("a & b =", format(a & b, '04b'), "=", a & b)
print("a | b =", format(a | b, '04b'), "=", a | b)
print("a ^ b =", format(a ^ b, '04b'), "=", a ^ b)
```

Read each output column by column: `&` keeps a 1 only where *both* inputs
have one (just the 8s place), `|` where *either* does, `^` where they
*disagree*. These are the same AND/OR ideas as `and`/`or` from
[Chapter 4](../ch04-branching/01-booleans-logic.md), applied to each bit
pair instead of to whole `True`/`False` values — but they are different
operators, and mixing them up is a classic bug (see the warning below).

### Why `~` looks strange in Python

`~` needs its own note. Python integers have no fixed width, so "flip every
bit" is defined by arithmetic instead: `~x` is exactly `-x - 1`. To *see*
the flipped pattern, mask the result down to a fixed width:

```python
x = 12
print(~x)                            # -13, because ~x == -x - 1
print(format(x, '08b'))              # 00001100
print(format(~x & 0xFF, '08b'))      # 11110011 — the low 8 bits, flipped
```

`& 0xFF` keeps only the lowest 8 bits (0xFF is `11111111`), turning the
"infinite" flipped number into the byte-sized view you expected.

!!! info "Java corner"
    Java's `int` is exactly 32 bits, so `~12` is the same −13 but the flip
    is literal, and Java adds a third shift `>>>` (unsigned right shift)
    that Python doesn't need. Also mind precedence: in Java,
    `(perms & READ) != 0` **requires** the parentheses because `!=` binds
    tighter than `&`. Python groups `perms & READ != 0` the way you'd hope
    — but write the parentheses anyway, for every reader who knows C or
    Java.

## Masks: test, set, clear

A **mask** is an integer whose bit pattern selects the positions you care
about. Three moves cover almost every real use:

- **Test** a bit: `value & mask` — nonzero if the bit is on.
- **Set** a bit: `value | mask` — turns it on, leaves the rest alone.
- **Clear** a bit: `value & ~mask` — turns it off, leaves the rest alone.

```python
flags = 0b0101
print("start:", format(flags, '04b'))

print("bit 2 on?", bool(flags & 0b0100))   # test

flags = flags | 0b0010                      # set bit 1
print("set:  ", format(flags, '04b'))

flags = flags & ~0b0001                     # clear bit 0
print("clear:", format(flags, '04b'))
```

The pattern walks `0101` → `0111` → `0110`, one surgical bit at a time.
Note the shapes: OR with the mask can only *add* 1s, AND with the
*inverted* mask can only *remove* the masked 1 — neither touches any other
position. (XOR with a mask *toggles* the selected bits — the fourth move,
used less often.)

## Two classic tricks

### Even or odd in one operation

The lowest bit of any integer is its "ones place" in binary, so `n & 1` is 1
exactly for odd numbers:

```python
for n in range(6):
    kind = "odd" if n & 1 else "even"
    print(f"{n} ({format(n, '03b')}) is {kind}")
```

Scan the binary column: the last bit alternates 0, 1, 0, 1, … and the
verdict follows it exactly.

### Shifting is scaling by powers of two

Sliding the bits one place left doubles the value, because every bit moves
into a column worth twice as much; sliding right halves it, rounding down. So
`x << k` equals $x \times 2^k$ and `x >> k` equals
$\lfloor x / 2^k \rfloor$:

```python
value = 1
for p in range(9):
    print(f"2**{p} = {value:>3}   binary {format(value, '09b')}")
    value <<= 1     # shift left by one: double it
```

A single 1-bit marching leftward through the number, doubling at every
step — the whole powers-of-two table from Chapter 0, generated by one loop
and one shift.

## Worked example: permission flags

Unix file systems famously pack three permissions — read, write, execute —
into three bits (that is what `chmod 755` manipulates). Here is the whole
system in miniature:

```python
READ, WRITE, EXECUTE = 0b100, 0b010, 0b001

def describe(perms):
    letters = "r" if perms & READ else "-"
    letters += "w" if perms & WRITE else "-"
    letters += "x" if perms & EXECUTE else "-"
    return letters

perms = READ | WRITE            # grant read and write
print(describe(perms))          # rw-
perms |= EXECUTE                # grant execute too
print(describe(perms))          # rwx
perms &= ~WRITE                 # revoke write
print(describe(perms))          # r-x
print("can read?", bool(perms & READ))
```

One small integer carries three independent yes/no facts, and each
operation touches exactly one of them: `|` grants, `& ~` revokes, `&`
checks. This is why the operators survive in modern code — a million file
records with an int of flags each is vastly cheaper than a million objects
holding three booleans.

## Enums: names for a fixed set of values

Now the opposite problem: your program has a handful of *named options* —
days of the week, card suits, traffic-light states — and you are tempted to
represent them as strings (`"monday"`) or magic numbers (`3`). Python's
`enum.Enum` creates a proper type whose members are the only legal values:

```python
from enum import Enum

class Day(Enum):
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6
    SUNDAY = 7

today = Day.WEDNESDAY
print(today)                     # Day.WEDNESDAY
print(today.name, "|", today.value)
print(today == Day.WEDNESDAY)    # True — compare member to member
print(today == 3)                # False! an enum member is NOT its number

weekend = {Day.SATURDAY, Day.SUNDAY}
for day in Day:                  # iterates in definition order
    kind = "weekend" if day in weekend else "weekday"
    print(f"{day.name:<9} {kind}")
```

Three facts do most of the work:

- **Every member carries a `.name`** (the identifier you wrote) **and a
  `.value`** (the number you assigned it).
- **Members compare equal only to themselves**, never to a bare number.
- **Iterating the class visits every member in definition order** — perfect
  for building menus or tables.

The `today == 3` line is the philosophy in one comparison: a `Day`
deliberately refuses to equal a bare int, so days can never silently mix with
arithmetic. When you *want* int behaviour, Python offers `IntEnum` — opt-in,
never the default.

Java's `enum` is a core language keyword with the same intent:

=== "Python"

    ```python
    from enum import Enum

    class Light(Enum):
        RED = 1
        YELLOW = 2
        GREEN = 3

    print(list(Light))
    ```

=== "Java"

    ```java
    enum Light { RED, YELLOW, GREEN }

    Light l = Light.RED;
    System.out.println(l);              // RED
    for (Light x : Light.values()) {    // like iterating the class in Python
        System.out.println(x);
    }
    ```

## When to use an enum instead of a string

Strings *work* for named options — until someone mistypes one. The string
`"wendsday"` sails through every line of code and produces quietly wrong
behaviour at a distance; the same typo on an enum explodes immediately, at
the exact line that is wrong:

```python
# raises AttributeError
from enum import Enum

class Day(Enum):
    MONDAY = 1
    WEDNESDAY = 3

print(Day.WENDSDAY)   # typo — Python stops us on the spot
```

That eager failure is the selling point. Which tool fits comes down to one
question — can you list every possible value while writing the program?

| Prefer an enum when… | Stay with plain strings when… |
| --- | --- |
| the set of values is **fixed and known in advance** — days, suits, states, directions | the values are **open-ended data** — user names, file paths |
| you want typos to become errors, and the options discoverable by iterating the class | you cannot enumerate the possibilities while writing the program |

The bonus of the enum column: each member is one honest object rather than a
loose string that any part of the program can misspell.

!!! warning "Common mistakes"

    - **`^` is XOR, not "to the power of."** `2 ^ 3` is 1 (binary `10 ^ 11
      = 01`), while `2 ** 3` is 8. This typo produces working code with
      wrong numbers — the worst kind.
    - **Mixing `&` with `and`.** `6 and 2` is 2 (truthiness logic), while
      `6 & 2` is 2 by luck but `6 & 1` is 0. Use `and`/`or` for booleans,
      `&`/`|` for bit patterns — they are not interchangeable.
    - **Expecting `~x` to look like flipped bits.** In Python `~x` is
      `-x - 1`; mask with `& 0xFF` (or the width you mean) to view the
      flipped pattern.
    - **Comparing an enum member to its raw value.** `Day.MONDAY == 1` is
      `False` for a plain `Enum`. Compare members to members, or use
      `Day.MONDAY.value` when you truly need the number.

## Check your understanding

1. Compute `0b0110 | 0b0011` and `0b0110 & 0b0011` by hand, then give both
   answers in decimal.

    ??? success "Answer"
        OR: `0110 | 0011 = 0111` = **7** (a 1 wherever either input has
        one). AND: `0110 & 0011 = 0010` = **2** (only the 2s place is 1 in
        both).

2. A classmate writes `2 ^ 10` expecting 1024. What does Python actually
   return, and why?

    ??? success "Answer"
        **8**. `^` is bitwise XOR: `2` is `0010`, `10` is `1010`, and they
        differ only in the 8s place, giving `1000` = 8. Powers use `**`:
        `2 ** 10` is 1024.

3. Write one expression that clears bit 3 (the mask `0b1000`) of an integer
   `flags` without disturbing any other bit.

    ??? success "Answer"
        `flags & ~0b1000` — inverting the mask makes every position 1
        *except* bit 3, so the AND preserves all other bits and forces
        bit 3 to 0.

4. Your code stores card suits as `"hearts"`, `"spades"`, … and a bug
   report shows `"herats"` slipped into the database. How would an enum
   have changed the story?

    ??? success "Answer"
        With `class Suit(Enum): HEARTS = ...`, the typo `Suit.HERATS`
        raises `AttributeError` the moment that line first runs — during
        development, at the guilty line — instead of storing bad data that
        surfaces as a mystery later. Fixed, known-in-advance sets of
        values are exactly the case for enums.
