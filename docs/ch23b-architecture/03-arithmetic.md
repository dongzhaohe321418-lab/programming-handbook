# 23.5.3 · How hardware does arithmetic

Every `+`, `*`, and `/` your program runs eventually reaches the **ALU**
(*arithmetic logic unit*), a small block of circuitry inside the CPU that does
the actual number-crunching. It has no idea what your numbers *mean* — it just
shuffles bits according to fixed rules. This section opens the ALU and shows,
with runnable models, exactly how it adds, subtracts, multiplies, divides, and
stores fractions. It is the hardware floor beneath two pages you have already
read: the two's-complement and "bits have no meaning" ideas from
[0.2 Bits and binary](../ch00-machine/02-binary.md), and the overflow and
`0.1 + 0.2` puzzles from
[5.1 Numeric pitfalls](../ch05-under-the-hood/01-numeric-pitfalls.md). Those
pages told you *what* goes wrong; this one shows *why*, at the level of the
gates. It follows Chapter 3 of *Computer Organization and Design*.

- **What the ALU works on.** Fixed-width bit patterns — 8, 32, or 64 of them —
  with no built-in sign or type. The *operation* decides how they are read.
- **The four basics, cheapest first.** Add and subtract (one pass), multiply
  (a loop of shifts and adds), divide (a loop of shifts and subtracts).
- **Why this ranking matters.** It flows straight into the cost of an
  instruction — the CPI idea in [23.5.1 Performance](01-performance.md) — and
  into why some code is slow.

---

## Addition and subtraction

!!! abstract "In plain words"

    - **What it is.** Binary addition is grade-school column addition with only
      two digits. You add a column, write down a bit, and carry into the next
      column — over and over, right to left.
    - **Picture it.** Adding `47 + 28` in decimal: `7 + 8 = 15`, write `5`,
      carry `1`; then `4 + 2 + 1 = 7`. Binary is identical, but a column can
      only hold `0` or `1`, so it carries far more often.
    - **Why it matters.** This "ripple" of carries is a real chain of gates in
      the ALU. Understanding it explains both how subtraction reuses the *same*
      circuit and how the CPU detects overflow.

**The rule for a single column.** Each column takes three inputs — a bit of
`a`, a bit of `b`, and the carry coming in — and produces two outputs:

- **Sum bit** = the three inputs XOR-ed together (odd number of 1s → 1).
- **Carry out** = 1 when *at least two* of the three inputs are 1.

A circuit that does one column is a **full adder**. Wire eight of them in a
row, each carry feeding the next, and you have an 8-bit **ripple-carry adder**.
Here it is in code — watch the carry ripple upward, then watch it agree with
Python's `+` on many inputs:

```python
def to_bits(n, width):
    """The bits of n, least-significant first: bits[0] is the 1s place."""
    return [(n >> i) & 1 for i in range(width)]

def from_bits(bits):
    """Rebuild an integer from a least-significant-first bit list."""
    return sum(bit << i for i, bit in enumerate(bits))

def ripple_add(a, b, width=8, show=False):
    """Add a and b one column at a time, low bit first, carrying as we go."""
    abits, bbits = to_bits(a, width), to_bits(b, width)
    out = [0] * width
    carry = 0
    if show:
        print(f"  adding {a} + {b} in {width} bits, column by column:")
        print("   bit  a  b  cin | sum  cout")
    for i in range(width):
        s = abits[i] ^ bbits[i] ^ carry                                # sum bit
        cout = (abits[i] & bbits[i]) | (carry & (abits[i] ^ bbits[i]))  # carry out
        out[i] = s
        if show:
            print(f"    {i}   {abits[i]}  {bbits[i]}   {carry}  |  {s}    {cout}")
        carry = cout
    return from_bits(out), carry           # (sum within the box, carry off the top)

# Watch the carry ripple through one addition:
ripple_add(13, 11, width=5, show=True)

# Now verify the adder against Python's + on many pairs:
ok = all(ripple_add(a, b, width=9)[0] == a + b
         for a in range(0, 256, 17) for b in range(0, 256, 17))
print("matches Python's + on every test pair:", ok)
```

- `13` is `01101` and `11` is `01011`; the sum `24` is `11000`. Follow the
  `cout` column: a carry is born at bit 0 and rides all the way up — that is
  the *ripple*, and it is why a naive adder gets slower as it gets wider.
- Real CPUs replace the long ripple with a **carry-lookahead adder** that
  computes the carries in parallel, so a 64-bit add still finishes in about one
  clock cycle.

### Subtraction is addition in disguise

The ALU has **no separate subtractor**. To compute `a - b` it adds `a` to the
*negative* of `b`, and the negative is built with the two's-complement trick you
met in [0.2](../ch00-machine/02-binary.md): **flip every bit, then add 1**.

```python
def neg8(x):
    """The 8-bit two's-complement pattern for -x: flip the bits, add 1."""
    return (~x + 1) & 0xFF

def signed8(pattern):
    """Read an 8-bit pattern as a signed value (top bit worth -128)."""
    return pattern - 256 if pattern & 0x80 else pattern

for a, b in [(50, 20), (20, 50), (7, 7)]:
    minus_b = neg8(b)                          # -b as an 8-bit pattern
    raw = (a + minus_b) & 0xFF                 # ADD it — no subtractor needed
    print(f"  {a} - {b}: add {a} + (pattern for -{b} = {minus_b:08b}) "
          f"= {signed8(raw)}   (python: {a - b})")
```

- This is *the* reason two's complement won: one adder circuit handles both
  signs and both operations. Hardware designers love not building things twice.
- In RISC-V this is literally two instructions built on one datapath, `add`
  and `sub`, sharing the same ALU — see
  [23.5.2 Instruction sets](02-instruction-set.md) and the datapath in
  [23.5.4](04-datapath.md).

### Overflow: how the CPU knows the answer is wrong

!!! abstract "In plain words"

    - **What it is.** Overflow is when a true answer is too big for the box —
      like an odometer rolling past its last digit. The bits that fall off give
      a wrong, wrapped result.
    - **Picture it.** Two people each 100 cm tall stand on each other's
      shoulders; a ruler that only goes to 127 cm reports a nonsense height. The
      ruler didn't break — the answer just didn't fit.
    - **Why it matters.** The ALU can *detect* this in one gate, and languages
      like Java/C (and NumPy's fixed-width ints) let it happen **silently** —
      the wrapped bug from [5.1](../ch05-under-the-hood/01-numeric-pitfalls.md).

For **signed** addition the hardware uses one beautifully simple test:

- Look at the **carry into** the sign bit (the top bit) and the **carry out**
  of it.
- **If they differ, the add overflowed.** If they match, it did not.

Equivalently: two positives that sum to a negative, or two negatives that sum
to a positive, must have overflowed — there was no room to hold the true sign.
Here is that exact flag, computed the way an ALU wires it:

```python
def signed(pattern, bits=8):
    """Interpret an unsigned bit pattern as a signed two's-complement value."""
    return pattern - (1 << bits) if pattern >> (bits - 1) else pattern

def add8_signed(a, b):
    """Add two 8-bit signed values; report the hardware overflow flag.
    Overflow flags when the carry INTO the sign bit differs from the carry
    OUT of it — the exact test a real ALU performs."""
    ua, ub = a & 0xFF, b & 0xFF                 # the stored 8-bit patterns
    low = (ua & 0x7F) + (ub & 0x7F)             # add the low 7 bits
    carry_in = low >> 7                         # carry entering the sign bit
    sign_sum = (ua >> 7) + (ub >> 7) + carry_in # add the sign bits + that carry
    carry_out = sign_sum >> 1                   # carry leaving the sign bit
    overflow = carry_in ^ carry_out             # differ  ->  overflow
    result = (ua + ub) & 0xFF                   # the 8-bit result the CPU keeps
    return signed(result), overflow, carry_in, carry_out

print(" a    b  | result | cin cout | overflow?")
for a, b in [(40, 50), (100, 50), (-100, -50), (-1, 1), (127, 1), (-128, -1)]:
    res, ovf, cin, cout = add8_signed(a, b)
    flag = "OVERFLOW" if ovf else "ok"
    print(f"{a:>4} {b:>4} | {res:>6} |  {cin}   {cout}  | {flag}")
```

- `100 + 50` should be `150`, but 8-bit signed only reaches `127`; the result
  wraps to `-106`, and `cin=1, cout=0` differ — **overflow flagged**.
- `-1 + 1` gives `0` with `cin=1, cout=1`: carries happen, but they *match*, so
  no overflow. A carry is not the same thing as an overflow.
- The CPU parks this bit in a **status flag** (the "V" / overflow flag). Your
  language chooses whether to check it. Python's big integers sidestep the whole
  issue by growing wider; `np.int32` does not — precisely the split described in
  [5.1](../ch05-under-the-hood/01-numeric-pitfalls.md).

---

## Multiplication

!!! abstract "In plain words"

    - **What it is.** Binary multiplication is long multiplication, but every
      "times a digit" step is trivial: a binary digit is `0` or `1`, so you
      either add a shifted copy of the first number or add nothing.
    - **Picture it.** `13 × 1011₂` = `13×1 + 13×0×10 + 13×1×100 + 13×1×1000`
      (binary places). Multiplying by a power of two is just sliding the number
      left, so the whole thing is **shifts and adds**.
    - **Why it matters.** It reveals that multiply is a *loop* over addition —
      inherently more work than a single add, which is why it costs more cycles.

The **shift-and-add** algorithm, one bit of `b` at a time:

1. Start the running product at `0`.
2. For bit `i` of `b`: if it is `1`, add `a` shifted left by `i` (that is
   `a × 2ⁱ`). If it is `0`, add nothing.
3. Move to the next bit. Stop when no bits of `b` remain.

```python
def multiply(a, b):
    """Multiply by the grade-school method in binary: for each 1-bit of b, add
    a shifted left by that bit's position. Shifting left by i multiplies by
    2**i, so every partial product is just a shift — no multiply needed."""
    product = 0
    i = 0
    print(f"  multiplying {a} x {b}   (b = {b:b} in binary)")
    while (b >> i):                       # while 1-bits of b remain
        bit = (b >> i) & 1
        if bit:
            partial = a << i              # a shifted left i places = a * 2**i
            product += partial
            print(f"    bit {i} of b is 1  ->  add {a} << {i} = {partial:>4}"
                  f"   running total {product}")
        else:
            print(f"    bit {i} of b is 0  ->  add nothing"
                  f"              running total {product}")
        i += 1
    return product

result = multiply(13, 11)
print(f"  final product: {result},  Python says {13 * 11}")
print("  match:", result == 13 * 11)
```

- The partial products `13`, `26`, and `104` sum to `143` — exactly what long
  multiplication on paper would give, and exactly `13 * 11`.
- **Real hardware parallelizes this.** A dedicated multiplier does not loop; it
  forms all the partial products at once and sums them in a tree of adders
  (a *Wallace tree*), finishing in a few cycles instead of one-per-bit.
- **Multiply still costs more than add.** Even parallelized, it needs many more
  gates and typically a few clock cycles, whereas add is ~1. That per-operation
  cost is exactly the CPI factor in the CPU performance equation
  ([23.5.1](01-performance.md)), and it is why complexity analysis
  ([16.1 Big-O](../ch16-complexity/01-big-o.md)) counts a multiply-heavy inner
  loop as pricier than an add-heavy one on the same $n$.

---

## Division

!!! abstract "In plain words"

    - **What it is.** Binary long division — the same "how many times does the
      divisor go in, subtract, bring down the next digit" ritual you did in
      school, but each digit of the answer is only `0` or `1`.
    - **Picture it.** Dividing `143` by `11` on paper: you march through the
      digits of `143`, and at each step you ask a yes/no question — *does 11 fit
      right now?* In binary that question has a one-bit answer.
    - **Why it matters.** Division cannot be parallelized the way multiplication
      can — each step depends on the previous subtraction — so it is the
      **slowest** of the four basic operations.

The **shift-and-subtract** algorithm builds the quotient one bit at a time,
most-significant bit first:

1. Keep a running **remainder**, starting at `0`.
2. Shift the remainder left and pull down the next bit of the dividend.
3. If the divisor now *fits* (`remainder ≥ divisor`), subtract it and put a `1`
   in the quotient at this place; otherwise put a `0`.
4. Repeat for every bit. What's left in the remainder is the true remainder.

```python
def divide(dividend, divisor, width=8):
    """Long division in binary: walk the dividend's bits from the top, pull each
    one down into a running remainder, and at every step ask 'does the divisor
    fit?' If yes, subtract it and put a 1 in the quotient; else a 0."""
    quotient = 0
    remainder = 0
    print(f"  dividing {dividend} by {divisor}")
    print("   bit | bring down | fits? | remainder | quotient so far")
    for i in reversed(range(width)):        # most-significant bit first
        remainder = (remainder << 1) | ((dividend >> i) & 1)   # shift in next bit
        if remainder >= divisor:
            remainder -= divisor            # subtract: the divisor fit
            quotient |= (1 << i)            # record a 1 in this quotient place
            fits = "yes"
        else:
            fits = "no "
        print(f"    {i}  |     {(dividend >> i) & 1}      |  {fits}"
              f"  |    {remainder:>3}    |   {quotient}")
    return quotient, remainder

q, r = divide(143, 11)
print(f"  143 = {q} x 11 + {r}")
print(f"  Python's divmod(143, 11) = {divmod(143, 11)}")
print("  match:", (q, r) == divmod(143, 11))
```

- The answer `13` remainder `0` undoes the multiplication above (`13 × 11 =
  143`) — multiply and divide are mirror images.
- **Why division is slowest:** each row's subtraction must finish before the
  next row's compare can start, so the steps are *sequential*. Multipliers dodge
  this by adding partial products in parallel; dividers cannot. On real CPUs an
  integer divide can take tens of cycles — far more than add or multiply, which
  is why compilers turn `x / 2` into a shift whenever they can.

---

## Floating point — IEEE-754 in depth

!!! abstract "In plain words"

    - **What it is.** A float is **binary scientific notation** packed into a
      fixed number of bits: a sign, an exponent (which power of two to scale
      by), and a fraction (the significant digits).
    - **Picture it.** Decimal scientific notation writes `6.022 × 10²³` as
      *sign, digits, exponent*. IEEE-754 does the same in base 2:
      `±1.fraction × 2^exponent`. Only a fixed number of fraction bits fit, so
      most numbers get rounded — like writing $1/3$ as `0.3333` and stopping.
    - **Why it matters.** This rounding is the hardware reason behind every
      float surprise in [5.1](../ch05-under-the-hood/01-numeric-pitfalls.md) —
      `0.1 + 0.2 ≠ 0.3` is not a bug, it is this format doing its job.

**The three fields.** A `float` is split into sign, biased exponent, and
fraction. Single precision (32 bits) and double precision (64 bits) differ only
in how many bits each field gets:

| Precision | Sign | Exponent | Fraction | Bias | Python / Java |
| --- | --- | --- | --- | --- | --- |
| single (32-bit) | 1 | 8 | 23 | 127 | numpy `float32`, Java `float` |
| double (64-bit) | 1 | 11 | 52 | 1023 | Python `float`, Java `double` |

- **Normalized form.** A nonzero value is written `1.fraction × 2^E`. That
  leading `1` is *always* there, so it is **not stored** — the "hidden bit" buys
  you one extra bit of precision for free.
- **Biased exponent.** The exponent field holds `E + bias`, a plain unsigned
  number, so the same circuitry can compare exponents of huge and tiny values.
  To read the true exponent you subtract the bias.
- **Fraction (mantissa).** The bits after the hidden `1.`, each worth
  $2^{-1}, 2^{-2}, \dots$

$$ \text{value} \;=\; (-1)^{\text{sign}} \times \Bigl(1 + \tfrac{\text{fraction}}{2^{\,\text{fraction bits}}}\Bigr) \times 2^{\,(\text{raw exponent} - \text{bias})} $$

Read aloud: *take the fraction bits as a number below 1, add the hidden 1,
attach the sign, and scale by two raised to the un-biased exponent.*

**The inspector.** This model takes a real float, uses `struct.pack('>f', x)`
to grab its *exact* 32 bits, splits out the three fields, and then
**reconstructs** the value from those fields alone — proving the decode is
faithful:

```python
import struct

def inspect32(x):
    """Take a float, get its exact 32-bit IEEE-754 pattern with struct, split it
    into sign / exponent / fraction, then rebuild the value from those fields to
    prove the decode is faithful."""
    bits = struct.unpack(">I", struct.pack(">f", x))[0]   # the 32 bits as an int
    sign = (bits >> 31) & 1
    exp_raw = (bits >> 23) & 0xFF          # 8 exponent bits
    frac = bits & 0x7FFFFF                 # 23 fraction bits
    bias = 127

    if exp_raw == 0:                       # subnormal (or zero): no hidden 1
        value = (-1)**sign * (frac / 2**23) * 2**(1 - bias)
        exp_shown = 1 - bias
    elif exp_raw == 255:                   # inf / NaN
        value = float("inf") if frac == 0 else float("nan")
        exp_shown = None
    else:                                  # normal: implied leading 1.
        value = (-1)**sign * (1 + frac / 2**23) * 2**(exp_raw - bias)
        exp_shown = exp_raw - bias

    stored = struct.unpack(">f", struct.pack(">f", x))[0]  # value after f32 rounding
    print(f"  {x!r}")
    print(f"    bits      : {bits:032b}")
    print(f"    sign      : {sign}  ({'-' if sign else '+'})")
    print(f"    exponent  : raw {exp_raw} - bias {bias} = {exp_shown}")
    print(f"    fraction  : {frac}  (= {frac}/2^23)")
    print(f"    rebuilt   : {value}")
    print(f"    matches stored value: {value == stored}")
    print()

for x in [1.0, 0.5, -2.5, 0.1]:
    inspect32(x)
```

Read the four outputs:

- **`1.0`** → sign `+`, exponent `0` (raw `127`), fraction `0`: literally
  `1.0 × 2⁰`. Clean.
- **`0.5`** → exponent `-1`: `1.0 × 2⁻¹`. Halving just drops the exponent.
- **`-2.5`** → sign `-`, exponent `1`, fraction `2097152/2²³ = 0.25`, so
  `1.25 × 2¹ = 2.5`, negated. The sign lives in one isolated bit.
- **`0.1`** → the fraction bits fall into a repeating `...11001100...` pattern.
  `0.1` is `1/10`, and `10 = 2 × 5`; that factor of 5 makes it an **infinite**
  repeating binary fraction, so the hardware keeps only 23 bits and rounds. The
  rebuilt value is `0.10000000149011612`, **not** `0.1` — and it matches the
  stored value exactly, proving the tiny error is baked into the *storage*, not
  introduced by our decode. This is the mechanism under
  [5.1](../ch05-under-the-hood/01-numeric-pitfalls.md)'s warnings.

### Special values and rounding

IEEE-754 reserves the extreme exponent fields for special citizens:

- **±0** — sign bit `0` or `1`, everything else zero. Two zeros that compare
  equal but carry different signs (`-0.0` remembers "we approached from below").
- **±∞** — exponent all `1`s, fraction `0`. What a float *saturates* to instead
  of wrapping (`1e308 * 10` → `inf`).
- **NaN** ("not a number") — exponent all `1`s, fraction **nonzero**. The result
  of `0/0` or `inf - inf`; it is unequal to everything, even itself (test with
  `math.isnan`, per [5.1](../ch05-under-the-hood/01-numeric-pitfalls.md)).
- **Subnormals** — exponent all `0`s. These drop the hidden `1` to represent
  numbers *smaller* than the normal minimum, letting values fade gradually
  toward zero instead of snapping to it.

```python
import struct

def fields32(x):
    bits = struct.unpack(">I", struct.pack(">f", x))[0]
    return (bits >> 31) & 1, (bits >> 23) & 0xFF, bits & 0x7FFFFF

print("special IEEE-754 patterns (single precision):")
print("   value       sign  exp   fraction   note")
specials = [
    (0.0,           "positive zero"),
    (-0.0,          "negative zero (a distinct bit pattern)"),
    (float("inf"),  "exponent all 1s, fraction 0"),
    (float("-inf"), "same, sign bit set"),
    (float("nan"),  "exponent all 1s, fraction nonzero"),
    (1.4e-45,       "smallest subnormal (exponent all 0s)"),
]
for x, note in specials:
    s, e, f = fields32(x)
    print(f"  {x!s:>9}   {s}    {e:>3}   {f:>8}   {note}")
```

- **Rounding modes.** When a result lands between two representable floats, the
  hardware must pick one. The default is **round to nearest, ties to even**
  (round half to the neighbour whose last bit is `0`); IEEE-754 also defines
  round toward zero, and toward $+\infty$ or $-\infty$. Every basic operation is
  defined to give the *correctly rounded* result — the true answer rounded once.

### Single vs double: the bit budget

More fraction bits means a finer grid of representable numbers, so double
precision sits far closer to any given decimal:

```python
import struct
from decimal import Decimal

d = struct.unpack(">d", struct.pack(">d", 0.1))[0]     # 64-bit double
f = struct.unpack(">f", struct.pack(">f", 0.1))[0]     # 32-bit single
true = Decimal("0.1")
err_d = abs(Decimal(d) - true)
err_f = abs(Decimal(f) - true)
print(f"  single (23 fraction bits) is off from 0.1 by ~ {float(err_f):.1e}")
print(f"  double (52 fraction bits) is off from 0.1 by ~ {float(err_d):.1e}")
print(f"  double is closer by about {err_f / err_d:.1e}x")
```

- Single precision carries ~7 decimal digits; double carries ~15–16. Double is
  the default for Python `float` and Java `double` for exactly this reason.
- Single precision is not a mistake — it halves memory and bandwidth, which is
  why GPUs and machine-learning inference lean on 32-bit (and 16-bit) floats.
  That trade-off returns in [23.5.6 Parallelism](06-parallelism.md) and the
  inference chapters.

---

## Why this matters to a programmer

The ALU's design leaks directly into everyday bugs and performance choices:

- **Integer overflow is silent and wraps.** Fixed-width signed integers roll
  over with no error (`127 + 1 → -128`). The CPU raises an overflow flag, but
  Java, C, and NumPy leave it unchecked. Reach for a wider type — or Python's
  unbounded `int` — *before* values get large.
  ([5.1](../ch05-under-the-hood/01-numeric-pitfalls.md))
- **Float equality is unsafe.** Because almost every decimal is rounded to fit
  the fraction field, `a == b` on computed floats is a coin toss. Compare with a
  tolerance (`math.isclose`) instead.
  ([5.1](../ch05-under-the-hood/01-numeric-pitfalls.md))
- **Multiply and divide cost more than add.** Add is ~1 cycle; multiply is a
  few; divide is tens. A hot loop full of divisions is a real performance smell —
  this is the per-operation side of CPI ([23.5.1](01-performance.md)).
- **Choosing `int` vs `float` is choosing a hardware representation.** `int` is
  exact but bounded (or, in Python, slower-but-unbounded); `float` is wide-range
  but approximate. There is no "just a number" type — you are always picking a
  bit layout, a lesson that starts back in
  [0.2 Bits and binary](../ch00-machine/02-binary.md).

!!! warning "Common mistakes"

    - **Confusing a carry with an overflow.** A carry *out* of the top bit is
      normal; signed overflow is when the carry *into* the sign bit disagrees
      with the carry *out*. `-1 + 1` carries but does not overflow.
    - **Thinking multiply and divide are "one operation" like add.** They are
      loops (or trees) of adds/subtracts. Divide especially can cost tens of
      cycles — don't scatter `/` through an inner loop when a shift or a
      reciprocal-multiply would do.
    - **Blaming the language for `0.1 + 0.2`.** The rounding happens in the
      IEEE-754 hardware format, identically in Python, Java, C, and your GPU.
      The inspector above shows `0.1` is stored as `0.10000000149011612` (single)
      before any arithmetic runs.
    - **Assuming `float` has more range *and* more precision than `int`.** It
      trades precision for range: a 64-bit `float` cannot represent every
      integer a 64-bit `int` can — past $2^{53}$ consecutive integers start to
      collide.

## Check your understanding

1. An 8-bit signed add reports `carry_in = 0` into the sign bit and
   `carry_out = 1`. Did it overflow, and what kind of inputs produce this?

    ??? success "Answer"
        Yes — the two carries differ, so the hardware overflow flag fires. A
        carry *out* of the sign bit with no carry *in* happens when two
        **negative** numbers are added and their true sum is more negative than
        $-128$ (e.g. `-100 + -50`): the result wraps up into the positive range.

2. Using the shift-and-add view, write out the partial products for `6 × 5` in
   binary and add them. Does it match the multiplier's output?

    ??? success "Answer"
        `5` is `101₂`, so bits 0 and 2 are set: partial products are
        `6 << 0 = 6` and `6 << 2 = 24`; bit 1 is `0` and contributes nothing.
        `6 + 24 = 30 = 6 × 5`. Running `multiply(6, 5)` prints exactly these two
        additions.

3. A single-precision float has sign bit `1`, raw exponent `128`, and fraction
   `0`. What value is it? Decode it by hand.

    ??? success "Answer"
        Un-bias the exponent: `128 - 127 = 1`. The fraction is `0`, so the
        mantissa is the hidden `1.0`. Value `= (-1)¹ × 1.0 × 2¹ = -2.0`. You can
        confirm with `inspect32(-2.0)`, which shows the same three fields.

4. Why is integer division typically the slowest of the four basic operations,
   even on a modern CPU with a fast multiplier?

    ??? success "Answer"
        Division is inherently **sequential**: each step subtracts the divisor
        and the *next* step's compare depends on that subtraction's result, so
        the bits of the quotient must be produced one after another.
        Multiplication avoids this by forming all partial products up front and
        summing them in parallel (a Wallace tree); division has no equivalent
        shortcut, so it costs tens of cycles versus a few for multiply.

!!! info "Where this comes from"
    This section follows **Chapter 3, "Arithmetic for Computers," of Patterson
    & Hennessy, _Computer Organization and Design_ (RISC-V edition)** — full
    adders and overflow, the shift-and-add multiplier and shift-and-subtract
    divider, and the IEEE-754 single/double formats with their special values
    and rounding. Go there for the gate-level circuits, Booth's multiplication,
    and faster division algorithms. For the everyday programmer's view of the
    same facts, see [5.1 Numeric pitfalls](../ch05-under-the-hood/01-numeric-pitfalls.md);
    for where these operations sit in the CPU, continue to
    [23.5.4 The datapath](04-datapath.md). Return to the
    [chapter overview](index.md) for the full map.
