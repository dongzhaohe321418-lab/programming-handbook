# Project 1 · Number-Systems Toolkit

Your first real program: a command-line-style toolkit that converts numbers
between bases, encodes negative numbers the way hardware does, and reads
Unix-style permission masks — all using nothing but digit arithmetic. If you
can build this, binary is no longer a mystery.

## What you'll build

A small library of conversion functions plus a driver that exercises all of
them and prints a report like this (excerpt):

```text
Round trips (value -> base -> value):
  42 -> base 2: 101010 -> 42  [ok]
  255 -> base 16: FF -> 255  [ok]

 decimal      binary   hex
--------------------------
      42      101010    2A
     127     1111111    7F
     255    11111111    FF

Two's complement, 8 bits:
      5 -> 00000101 -> 5
     -5 -> 11111011 -> -5

Overflow detection:
  caught OverflowError: 200 does not fit in 8 bits (range -128..127)

Permission masks:
  101 -> r-x
```

The rules of the game: **no `bin()`, no `hex()`, no `int(text, base)`** for
the core conversions. You build them from `%`, `//`, and multiplication —
because the point is to understand what those built-ins do.

## What it exercises

- [2.2 Number systems](../../ch02-data/02-number-systems.md) — bases, digits,
  and place value: the heart of this project.
- [3.3 Writing your own functions](../../ch03-functions/03-writing-functions.md)
  and [3.4 Formatting output](../../ch03-functions/04-output-formatting.md) —
  small functions, aligned tables.
- [5.1 Overflow and floating-point pitfalls](../../ch05-under-the-hood/01-numeric-pitfalls.md)
  — why fixed-width integers overflow and Python ints don't.
- [6.4 Bitwise operators and enums](../../ch06-loops/04-bitwise-enums.md) —
  `&`, `|`, and shifts for the permissions demo and the wrap-around trick.
- [10.2 Exceptions](../../ch10-exceptions/02-exceptions.md) — raising and
  catching `ValueError` and `OverflowError`.

## Milestones

### Milestone 1 — decimal to any base

**Goal:** write `to_base(value, base)` that turns a non-negative integer into
a string of digits in any base from 2 to 16, using repeated division.

**Done when...** `to_base(42, 2)` returns `"101010"`, `to_base(255, 16)`
returns `"FF"`, `to_base(0, 2)` returns `"0"`, and a bad base raises
`ValueError`.

??? tip "Hint"

    Repeated division hands you the digits *last first*. Watch it happen,
    then collect the remainders in a list and reverse it at the end:

    ```python
    value = 42
    while value > 0:
        print(f"{value:>3} % 2 = {value % 2}")
        value //= 2
    # read the remainders bottom-to-top: 101010
    ```

    For digits above 9, index into the string `"0123456789ABCDEF"` —
    remainder 10 picks out `"A"`.

### Milestone 2 — and back again

**Goal:** write `from_base(text, base)` that parses a digit string back into
an integer, and reject characters that are not valid digits in that base.

**Done when...** `from_base("101010", 2)` returns `42`,
`from_base("ff", 16)` returns `255` (accept lowercase), round trips like
`from_base(to_base(n, b), b) == n` hold for a whole batch of values, and
`from_base("102", 2)` raises `ValueError`.

??? tip "Hint"

    Process the text left to right with one accumulator. Each new digit
    multiplies what you have by the base, then adds on:

    ```python
    text = "7EA"          # 2026 in hex
    value = 0
    for ch in text:
        value = value * 16 + "0123456789ABCDEF".index(ch)
        print(ch, "->", value)
    ```

    Validity check: a character is a legal base-`b` digit exactly when it
    appears in the first `b` characters of the digit string.

### Milestone 3 — two's complement, with overflow detection

**Goal:** write `encode_twos_complement(value, bits)` and
`decode_twos_complement(bit_string)` so that negative numbers round-trip
through a fixed bit width — and refuse values that don't fit.

**Done when...** `-5` encodes to `"11111011"` at 8 bits and decodes back to
`-5`; `127` and `-128` both fit in 8 bits but `128` and `200` raise
`OverflowError` with a message naming the legal range.

??? tip "Hint"

    Two facts do all the work. First, Python's `&` gives you the wrapped
    bit pattern of a negative number for free:

    ```python
    print((-5) & 0xFF)    # 251 — and 251 is the 8-bit pattern for -5
    ```

    So encode with `value & ((1 << bits) - 1)`, then reuse your Milestone 1
    `to_base(..., 2)` and pad with `.rjust(bits, "0")`. Second, decoding is
    plain binary parsing followed by one correction: if the first bit is
    `1`, subtract `1 << bits`.

    Python has to be *taught* to overflow — its own ints grow forever, so
    check the range yourself and `raise OverflowError(...)`. The built-in
    exception mostly appears when floats blow up:

    ```python
    # raises OverflowError
    import math

    math.exp(1000)    # floats have a fixed width, so THEY can overflow
    ```

### Milestone 4 — bit-mask permissions

**Goal:** define `READ`, `WRITE`, `EXECUTE` as single-bit constants and write
`permission_string(mask)` that renders any 3-bit mask the way `ls -l` does.

**Done when...** `0b111` gives `"rwx"`, `0b101` gives `"r-x"`, `0b000` gives
`"---"`, and combining flags with `|` then testing with `&` behaves as
expected (`(READ | WRITE) & EXECUTE` is falsy).

??? tip "Hint"

    One bit per flag, `|` to grant, `&` to test:

    ```python
    READ, WRITE, EXECUTE = 0b100, 0b010, 0b001
    mask = READ | EXECUTE
    print("can read?", bool(mask & READ))
    print("can write?", bool(mask & WRITE))
    ```

### Milestone 5 — the conversion table and the driver

**Goal:** write `print_conversion_table(values)` producing aligned
decimal/binary/hex columns, then a `main()` that runs round-trip checks, the
table, the two's-complement suite (including a *caught* overflow), and the
permissions demo.

**Done when...** the driver output matches the sample at the top of this
page: columns line up for values from `0` to `255`, every round trip reports
`ok`, and the deliberate overflow prints the caught error instead of
crashing.

??? tip "Hint"

    F-string alignment does the tidying: `f"{value:>8}"` right-aligns in 8
    characters, and it works on the *strings* your converters return too:

    ```python
    for v in [5, 42, 255]:
        print(f"{v:>8}  {'?':>10}")   # replace '?' with to_base(v, 2)
    ```

## Reference implementation

Try the milestones yourself first — the whole point is the struggle with
digits and remainders. Then compare.

??? success "Full reference implementation"

    ```python
    """Number-Systems Toolkit — convert, encode, and inspect binary data."""

    DIGITS = "0123456789ABCDEF"


    def to_base(value, base):
        """Return non-negative `value` written in `base` (2-16), as a string.

        Repeated division does the work: each remainder is one digit,
        produced last-digit-first, so we reverse at the end.
        """
        if not 2 <= base <= 16:
            raise ValueError(f"base must be between 2 and 16, got {base}")
        if value < 0:
            raise ValueError("to_base expects a non-negative value")
        if value == 0:
            return "0"
        digits = []
        while value > 0:
            digits.append(DIGITS[value % base])
            value //= base
        return "".join(reversed(digits))


    def from_base(text, base):
        """Parse `text` as an unsigned number written in `base` (2-16)."""
        if not 2 <= base <= 16:
            raise ValueError(f"base must be between 2 and 16, got {base}")
        value = 0
        for ch in text.upper():
            if ch not in DIGITS[:base]:
                raise ValueError(f"{ch!r} is not a base-{base} digit")
            value = value * base + DIGITS.index(ch)
        return value


    def encode_twos_complement(value, bits):
        """Return `value` as a `bits`-wide two's-complement bit string.

        Raises OverflowError when the value cannot fit in `bits` bits.
        """
        low, high = -(2 ** (bits - 1)), 2 ** (bits - 1) - 1
        if not low <= value <= high:
            raise OverflowError(
                f"{value} does not fit in {bits} bits (range {low}..{high})")
        pattern = value & ((1 << bits) - 1)   # wraps negatives around
        return to_base(pattern, 2).rjust(bits, "0")


    def decode_twos_complement(bit_string):
        """Read a two's-complement bit string back into a signed int."""
        raw = from_base(bit_string, 2)
        if bit_string[0] == "1":              # sign bit set -> negative
            raw -= 1 << len(bit_string)
        return raw


    # --- bit-mask permissions, like one digit of Unix `chmod` --------------
    READ, WRITE, EXECUTE = 0b100, 0b010, 0b001


    def permission_string(mask):
        """Render a 3-bit permission mask the way `ls -l` would (e.g. 'rw-')."""
        return ("r" if mask & READ else "-") + \
               ("w" if mask & WRITE else "-") + \
               ("x" if mask & EXECUTE else "-")


    def print_conversion_table(values):
        """Print a decimal / binary / hex table for each value."""
        print(f"{'decimal':>8}  {'binary':>10}  {'hex':>4}")
        print("-" * 26)
        for v in values:
            print(f"{v:>8}  {to_base(v, 2):>10}  {to_base(v, 16):>4}")


    # --- driver -------------------------------------------------------------
    def main():
        print("Round trips (value -> base -> value):")
        for value, base in [(42, 2), (255, 16), (100, 8), (2026, 16)]:
            text = to_base(value, base)
            back = from_base(text, base)
            status = "ok" if back == value else "BROKEN"
            print(f"  {value} -> base {base}: {text} -> {back}  [{status}]")

        print()
        print_conversion_table([0, 5, 10, 42, 127, 128, 255])

        print("\nTwo's complement, 8 bits:")
        for value in [5, -5, 127, -128, -1]:
            bits = encode_twos_complement(value, 8)
            print(f"  {value:>5} -> {bits} -> {decode_twos_complement(bits)}")

        print("\nOverflow detection:")
        try:
            encode_twos_complement(200, 8)
        except OverflowError as err:
            print(f"  caught OverflowError: {err}")

        print("\nPermission masks:")
        for mask in [0b111, 0b101, 0b110, 0b000]:
            print(f"  {to_base(mask, 2).rjust(3, '0')} -> {permission_string(mask)}")


    main()
    ```

## Going further

- **IEEE-754 inspector.** Floats have bit patterns too. `struct.pack` turns a
  Python float into its raw 4 bytes; split the 32 bits into sign, exponent,
  and fraction fields and print them. (After building your own converter you
  have earned the `format(raw, "032b")` shortcut.) A starter:

    ```python
    import struct


    def inspect_float(x):
        """Show the sign, exponent, and fraction bits of a 32-bit float."""
        (raw,) = struct.unpack(">I", struct.pack(">f", x))
        bits = format(raw, "032b")
        sign, exponent, fraction = bits[0], bits[1:9], bits[9:]
        print(f"{x!r:>6}  sign={sign}  exponent={exponent}  fraction={fraction}")


    for x in [1.0, -1.0, 0.5, 0.1, float("inf")]:
        inspect_float(x)
    ```

    Look at `0.1` — the fraction bits repeat `1001` forever and get cut off,
    which is exactly why `0.1 + 0.2 != 0.3`.

- **Fractional bases.** Extend `to_base` to handle a fractional part
  (`to_base(2.625, 2)` giving `"10.101"`) by repeatedly *multiplying* the fraction
  by the base.
- **Base-N arithmetic.** Add two digit strings in any base without converting
  to decimal first — carry propagation, exactly like column addition in
  school.
- **A real CLI.** Running locally, wrap the toolkit in
  `argv`-style dispatch (`convert 42 --to 2`) using what you learned in
  [10.1 Command-line programs](../../ch10-exceptions/01-cli-programs.md).
