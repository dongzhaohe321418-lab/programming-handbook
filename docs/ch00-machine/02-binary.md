# 0.2 Bits, binary, and how data is stored

Everything in a computer — this sentence, your photos, the program that
displays them — is stored as numbers, and every number is stored in
**binary**: patterns of 0s and 1s. This is not an implementation detail you
can skip. It explains why numbers overflow in Java, why `0.1 + 0.2` is not
quite `0.3`, what a "64-bit" processor is, and what those `#FF7F00` colour
codes on the web mean. Half an hour with binary now will pay for itself for
the rest of the book.

## Bits and bytes

A **bit** (short for *binary digit*) is the smallest possible unit of
information: something that is either 0 or 1, off or on. Hardware loves
bits because they are easy to build — a voltage is either low or high, a
tiny capacitor charged or not. Reliable two-state devices are cheap;
reliable ten-state devices are not, which is why computers do not count in
decimal the way we do.

One bit can distinguish only two things, so bits are used in groups. A
group of 8 bits is a **byte**, the standard unit of memory — the numbered
cells of RAM from [section 0.1](01-hardware.md) each hold one byte.
How many different patterns can a group of bits form? Each added bit
doubles the possibilities, so $n$ bits give $2^n$ patterns:

```python
print("patterns in 1 bit  :", 2 ** 1)
print("patterns in 1 byte :", 2 ** 8)     # 8 bits
print("patterns in 2 bytes:", 2 ** 16)
print("patterns in 4 bytes:", 2 ** 32)

n = 1000
print(f"the number {n} needs {n.bit_length()} bits")
```

A single byte has $2^8 = 256$ patterns — enough for a small number or one
English character. Four bytes (32 bits) already give about 4.3 billion
patterns. The method `bit_length()` asks a Python integer how many bits it
needs; we will use it to check our hand conversions.

## Counting in base 2

Our everyday numbers are **base 10** (decimal): ten digit symbols, 0–9, and
place values that are powers of ten. The numeral 4703 means

$$4703 = 4 \cdot 10^3 + 7 \cdot 10^2 + 0 \cdot 10^1 + 3 \cdot 10^0 .$$

Binary is the same game with two symbols and powers of two. The binary
numeral $1101_2$ (the little 2 marks the base) means

$$1101_2 = 1 \cdot 2^3 + 1 \cdot 2^2 + 0 \cdot 2^1 + 1 \cdot 2^0
        = 8 + 4 + 0 + 1 = 13 .$$

### From binary to decimal, by hand

Two steps, no arithmetic beyond addition:

1. Write the place values $\dots, 8, 4, 2, 1$ under the bits, from right to
   left.
2. Add up the places that hold a 1.

| bit | 1 | 1 | 0 | 1 |
| --- | --- | --- | --- | --- |
| place value | 8 | 4 | 2 | 1 |
| contributes | 8 | 4 | 0 | 1 |

Total: $8 + 4 + 0 + 1 = 13$. Python agrees — `int(text, base)` converts a
string of digits in any base, and the loop below shows the same place-value
arithmetic spelled out:

```python
pattern = "1101"

total = 0
for position, digit in enumerate(reversed(pattern)):
    contribution = int(digit) * 2 ** position
    print(f"digit {digit} in place {position} (value {2 ** position}) adds {contribution}")
    total += contribution

print("total:", total)
print("int('1101', 2) says:", int("1101", 2))
```

### From decimal to binary, by hand

This one is a loop:

1. Divide the number by 2; write down the quotient and the remainder.
2. Repeat with the quotient, until the quotient reaches 0.
3. Read the column of remainders **bottom to top** — that is the answer.

Each remainder (0 or 1) is one binary digit, produced from the *least*
significant end first, which is why step 3 reads upwards. Converting 13:

| step | division | quotient | remainder |
| --- | --- | --- | --- |
| 1 | $13 \div 2$ | 6 | **1** |
| 2 | $6 \div 2$ | 3 | **0** |
| 3 | $3 \div 2$ | 1 | **1** |
| 4 | $1 \div 2$ | 0 | **1** |

Read the remainders bottom-to-top: $1101_2$. Here is the same procedure as
code, next to Python's built-in `bin()`:

```python
original = 13        # try your own number and press Run again
n = original
digits = []
while n > 0:
    digits.append(str(n % 2))   # % gives the remainder after division
    n = n // 2                  # // divides and drops the remainder
binary = "".join(reversed(digits)) if digits else "0"

print(f"{original} in binary is {binary}")
print("bin() says:", bin(original))   # the 0b prefix means "binary"
```

Python also lets you *write* numbers directly in binary with the `0b`
prefix: `0b1101` is just another way to spell `13`. You will meet base
conversion again, in more depth, in
[Chapter 2](../ch02-data/02-number-systems.md).

## Hexadecimal: binary for humans

Long bit strings are unreadable — try telling `11010111` and `11010011`
apart at a glance. Programmers compress them using **hexadecimal** (base 16,
"hex"): sixteen digit symbols, 0–9 then A–F, where A means 10 and F means
15. Hex is popular for one beautiful reason: $16 = 2^4$, so **one hex digit
is exactly four bits**. Convert by chopping the bit string into groups of
four — no arithmetic required:

| binary | 0000 | 0001 | 0010 | 0011 | 0100 | 0101 | 0110 | 0111 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| hex | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |

| binary | 1000 | 1001 | 1010 | 1011 | 1100 | 1101 | 1110 | 1111 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| hex | 8 | 9 | A | B | C | D | E | F |

So $11010111_2$ splits into $1101\,0111$, which the tables say is
$\mathrm{D7}_{16}$ — two characters instead of eight.

A byte is always exactly two hex digits, which is why hex shows up wherever
raw bytes do:

- **memory addresses** — long numbers nobody wants to read in decimal;
- **error codes** — often a byte or two of packed flags;
- **web colour codes** — `#FF7F00` packs three bytes (red, green, blue).

In Python, hex literals take a `0x` prefix, `hex()` converts to hex text,
and `int(text, 16)` converts back:

```python
print(0xD7)                 # write a number in hex directly
print(hex(215), hex(255))   # convert to hex text
print(int("d7", 16))        # convert hex text to a number
print(0xFF == 255)          # same value, two spellings

print(bin(0xD7))            # hex and binary line up in groups of 4 bits
```

To convert hex → decimal by hand, use place values that are powers of 16:
$\mathrm{D7}_{16} = 13 \cdot 16 + 7 = 215$.

## Negative numbers: two's complement

Patterns of bits are just patterns — nothing about `11111011` is inherently
negative. To store negative numbers, computers need a *convention*, and the
one essentially all hardware uses is called **two's complement**. Fix a
width, say 8 bits. Then:

- Patterns starting with **0** mean ordinary positive numbers: `00000101`
  is 5.
- Patterns starting with **1** mean negative numbers. The leading bit — the
  **sign bit** — counts as $-128$ (that is $-2^7$) instead of $+128$, and
  every other place keeps its usual value.

So `11111011` means $-128 + 64 + 32 + 16 + 8 + 0 + 2 + 1 = -5$. Eight bits
then cover $-128$ to $+127$: still 256 patterns, just relabelled.

!!! note "Why hardware designers chose this"
    Under two's complement, *addition needs no special cases* — the same
    circuit that adds positive numbers adds negative ones correctly, with
    overflow bits simply falling off the end.

### Negating by hand: flip, then add one

To find the pattern for $-n$ from the pattern for $n$:

1. Write $n$ in binary, padded to the full width — 5 is `00000101`.
2. Flip every bit — `11111010`.
3. Add 1 — `11111011`, which is $-5$.

Here is a converter you can experiment with — it works for any width:

```python
def to_twos_complement(value, bits=8):
    """The bit pattern that stores `value` in `bits` bits."""
    lowest = -(2 ** (bits - 1))
    highest = 2 ** (bits - 1) - 1
    if not lowest <= value <= highest:
        raise ValueError(f"{value} does not fit in {bits} bits")
    pattern = value % 2 ** bits          # negatives wrap around
    return format(pattern, f"0{bits}b")  # as a padded bit string

def from_twos_complement(pattern):
    """Decode a bit string back into a signed integer."""
    bits = len(pattern)
    value = int(pattern, 2)
    if pattern[0] == "1":                # sign bit set: subtract 2**bits
        value -= 2 ** bits
    return value

for n in [5, -5, 0, -1, 127, -128]:
    p = to_twos_complement(n)
    print(f"{n:>5}  <->  {p}  (decodes to {from_twos_complement(p)})")
```

Look at $-1$: it is all ones, `11111111`. And $-128$ is the lone pattern
`10000000` with no positive partner — which is why the range is lopsided,
$-128$ to $+127$.

!!! info "Java corner"
    This matters enormously in Java, where `int` is *exactly* 32 bits of
    two's complement — range $-2\,147\,483\,648$ to $2\,147\,483\,647$ —
    and arithmetic that exceeds the range silently wraps around to the
    other end. Python integers instead grow as many bits as they need, so
    they never overflow. The full story, with demonstrations, is in
    [Chapter 5](../ch05-under-the-hood/01-numeric-pitfalls.md).

## Text is numbers too

If memory holds only bit patterns, what is the letter `A`? A number, by
convention. The 1960s **ASCII** standard assigned codes 0–127 to English
letters, digits, and punctuation: `A` is 65, `a` is 97, `0` (the character)
is 48. Its modern successor **Unicode** extends the same idea to every
writing system — well over one hundred thousand characters, each with a
numeric **code point**.

Python lets you look up both directions: `ord()` gives the code point of a
character, and `chr()` turns a code point back into a character.

```python
print(ord("A"), ord("B"), ord("a"))    # letters are consecutive numbers
print(chr(72), chr(105), chr(33))      # numbers back to characters

for ch in "Bit":
    print(ch, "is stored as", ord(ch), "=", bin(ord(ch)))

print(ord("é"), ord("雪"))             # Unicode covers all writing systems
```

A text file is nothing more than a long sequence of these numbers, encoded
as bytes. That single fact explains a lot of everyday behaviour — for
instance, comparing strings compares code points, which is why Python
considers `"Zebra"` smaller than `"apple"` (90 < 97).

## Bits have no inherent meaning — the program decides the type

You have now seen the *same kind of bit pattern* stand for several different
things: a plain positive number, a two's-complement negative number, a
character. That is not a coincidence to gloss over — it is one of the deepest
facts about computers, and *Computer Organization and Design* makes a whole
point of it.

!!! abstract "In plain words"

    - **What it is.** A bit pattern carries no built-in meaning. Whether
      `01100101` is the number 101, or the letter `e`, or part of a colour, is
      decided *entirely by the program that reads it* — never by the bits.
    - **Picture it.** The tally mark `IIII`. Is it the number four, four fence
      posts, or four days in jail scratched on a wall? The marks don't say;
      the *context* does. Bits are the same: identical marks, meaning supplied
      by whoever reads them.
    - **Why it matters.** It is why a **type** exists in every programming
      language. A type is the label that tells the computer how to *interpret*
      a pattern. Get the label wrong and the bits are read as something you
      never intended — a classic source of bugs and security holes.

Let us take one 32-bit pattern — four bytes — and deliberately read it three
different ways. Python's `int.from_bytes` interprets a group of bytes as an
integer (signed or unsigned), and `bytes.decode` reads them as text:

```python
pattern = bytes([0x63, 0x6F, 0x64, 0x65])      # one 32-bit pattern, four bytes
print("the raw bits:", " ".join(format(b, "08b") for b in pattern))

# Reading 1: an unsigned 32-bit integer (big-endian: first byte most significant)
print("as unsigned int:", int.from_bytes(pattern, "big", signed=False))

# Reading 2: a signed 32-bit two's-complement integer
print("as signed int  :", int.from_bytes(pattern, "big", signed=True))

# Reading 3: four ASCII characters, one byte each
print("as characters  :", pattern.decode("ascii"))
```

The identical 32 bits `01100011 01101111 01100100 01100101` come back as the
number `1668244581` *and* as the word `code`. Nothing changed but the
question we asked. (The unsigned and signed readings agree here only because
the top bit is 0, so the value is positive — recall from two's complement
above that the top bit is the sign.) Turn the top bit on and the two number
readings split apart:

```python
allones = bytes([0xFF, 0xFF, 0xFF, 0xFF])      # every bit set to 1
print("as unsigned int:", int.from_bytes(allones, "big", signed=False))
print("as signed int  :", int.from_bytes(allones, "big", signed=True))
```

Same 32 bits, read as `4294967295` unsigned or `-1` signed — the two's
complement rule from earlier, in action. This "bits plus an interpretation"
idea is the whole reason your programs declare types; it is also why a file
that is secretly a JPEG opens as garbage in a text editor, and why the *next*
section's puzzle — `0.1 + 0.2` — is really a question about *which*
interpretation the hardware puts on 32 or 64 bits. That floating-point
interpretation is involved enough to have its own home in
[Chapter 5](../ch05-under-the-hood/01-numeric-pitfalls.md).

## A first look at fractions: why 0.1 + 0.2 is not 0.3

One puzzle before we close, because you will trip over it soon. Run this:

```python
print(0.1 + 0.2)
print(0.1 + 0.2 == 0.3)
```

The output is `0.30000000000000004` and `False`. Nothing is broken.

Just as decimal cannot write $1/3$ exactly ($0.3333\ldots$ forever),
*binary* cannot write $1/10$ exactly — it becomes an infinitely repeating
binary fraction, and the computer stores only the first 53 bits or so. You
are seeing a microscopic rounding error, baked in by the base-2 storage this
whole section is about.

!!! tip "The rule of thumb to carry forward"
    **Never test two floating-point numbers for exact equality.** Compare
    with a tolerance instead: `abs(a - b) < 1e-9`.

The full story — what those 53 bits are and how to compare safely — is in
[Chapter 5](../ch05-under-the-hood/01-numeric-pitfalls.md).

!!! warning "Common mistakes"

    - **Mixing up bits and bytes.** A bit is one 0/1; a byte is 8 bits.
      Download speeds are usually quoted in bits (Mb), file sizes in bytes
      (MB) — an eight-fold difference.
    - **Forgetting the base argument.** `int("101")` is one hundred and
      one; only `int("101", 2)` reads the string as binary (5).
    - **Reading two's complement as "a minus sign plus a normal number".**
      The leading 1 is not a detachable sign flag — the whole pattern
      encodes the value, with the top bit worth $-2^{n-1}$. `10000001` in
      8 bits is $-127$, not $-1$.
    - **Expecting decimal fractions to be exact.** `0.1` is already rounded
      the moment it is stored. Test with `abs(a - b) < 1e-9`, not `==`.

## Check your understanding

1. Convert $10110_2$ to decimal by hand. Which Python call checks your
   answer?

    ??? success "Answer"
        Place values from the right: $16, 8, 4, 2, 1$. Ones sit in the 16,
        4, and 2 places: $16 + 4 + 2 = 22$. Check with `int("10110", 2)`.

2. Why do programmers prefer hex over decimal for showing raw bytes?

    ??? success "Answer"
        Because $16 = 2^4$, each hex digit corresponds to exactly four
        bits, so conversion is mechanical digit-by-digit substitution and
        one byte is always two hex digits. Decimal digits do not line up
        with bit boundaries at all.

3. What is the 8-bit two's-complement pattern for $-1$, and why does that
   make sense?

    ??? success "Answer"
        `11111111`. The sign bit contributes $-128$ and the remaining ones
        contribute $64+32+16+8+4+2+1 = 127$; $-128 + 127 = -1$. Or: flip
        the bits of 1 (`00000001` → `11111110`) and add 1.

4. True or false: `0.1 + 0.2 == 0.3` is `False` because Python has a bug
   in its addition.

    ??? success "Answer"
        False. The addition is performed correctly — but `0.1`, `0.2`, and
        `0.3` are each stored as the *nearest representable binary
        fraction*, and those tiny rounding differences make the two sides
        differ in the last binary digit. Every language using standard
        floating-point hardware behaves the same way.
