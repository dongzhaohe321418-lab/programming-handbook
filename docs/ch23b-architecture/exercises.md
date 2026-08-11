# Chapter 23.5 · Exercises

## The chapter in brief

- Speed is not one number: **response time** (one task) and **throughput**
  (tasks per second) answer different questions, and clock rate is only one of
  three factors ([23.5.1](01-performance.md)).
- The **CPU performance equation** — CPU time = instructions × CPI × cycle
  time — means a design can win on clock rate and still lose the race
  ([23.5.1](01-performance.md)).
- **CPI** is a weighted average over the program's instruction mix, so the
  *same* chip shows different CPI on different code
  ([23.5.1](01-performance.md)).
- **Amdahl's law** caps overall speed-up at $1/(1-p)$: the fraction you do not
  accelerate sets the floor, which is why you "make the common case fast"
  ([23.5.1](01-performance.md)).
- RISC-V is **load–store**: arithmetic touches only the 32 registers, whose ABI
  roles split into caller-saved and callee-saved
  ([23.5.2](02-instruction-set.md)).
- Every instruction is 32 bits in one of **six formats** — R, I, S, B, U, J —
  with the opcode and register fields pinned to fixed positions so decode is
  cheap ([23.5.2](02-instruction-set.md)).
- A **function call** is a hardware protocol: `jal` saves the return address,
  the **stack frame** preserves `ra` and callee-saved registers, and `sp` grows
  downward ([23.5.2](02-instruction-set.md)).
- The **ALU** adds with a ripple-carry chain, reuses that same adder for
  subtraction via two's complement, and flags **overflow** with a one-gate test
  ([23.5.3](03-arithmetic.md)).
- **Multiply** is a loop of shift-and-adds and **divide** a loop of
  shift-and-subtracts — which is why multiply costs a few cycles and divide tens
  ([23.5.3](03-arithmetic.md)).
- **IEEE-754** packs a float as sign + biased exponent + fraction; most decimals
  round to fit, the hardware mechanism behind `0.1 + 0.2 != 0.3`
  ([23.5.3](03-arithmetic.md)).
- The **single-cycle datapath** runs every instruction through the same five
  steps, steered by one-bit **control signals** (RegWrite, ALUSrc, MemRead,
  MemWrite, Branch, MemToReg) ([23.5.4](04-datapath.md)).
- Single-cycle wastes time because the clock is pinned to the slowest
  instruction (`lw`) — the whole motivation for pipelining
  ([23.5.4](04-datapath.md)).
- **Pipelining** overlaps the five stages: one instruction's *latency* is
  unchanged, but *throughput* approaches one instruction per cycle (≈5×)
  ([23.5.5](05-pipelining.md)).
- Three **hazards** hold it back — structural, data, control; **forwarding**
  covers most data hazards, a **load-use** still needs one **stall**, and
  **branch prediction** hides control hazards ([23.5.5](05-pipelining.md)).
- Parallelism comes in four kinds (**ILP, DLP, TLP, RLP**); **SIMD**/numpy,
  **multicore**, **GPUs**, and the **TPU**'s systolic array each exploit one,
  and Amdahl still caps multicore ([23.5.6](06-parallelism.md)).
- Past a machine's ridge point the **memory wall** leaves extra compute lanes
  idle, waiting for data — compute is this chapter, memory is
  [23.4](../ch23-os/04-memory-hierarchy.md) ([23.5.6](06-parallelism.md)).

### Key terms

| Term | Reminder |
| --- | --- |
| [CPI](01-performance.md) | cycles per instruction — the average clock cycles one instruction costs |
| [clock cycle time](01-performance.md) | seconds per tick, equal to $1/\text{clock rate}$ |
| [Amdahl's law](01-performance.md) | overall speed-up when only a fraction $p$ is accelerated; capped at $1/(1-p)$ |
| [instruction format](02-instruction-set.md) | one of the six 32-bit RISC-V layouts: R, I, S, B, U, J |
| [opcode / funct](02-instruction-set.md) | the bit fields that say *which* operation an instruction performs |
| [immediate](02-instruction-set.md) | a constant carried inside the instruction word, sign-extended before use |
| [calling convention](02-instruction-set.md) | the ABI protocol for arguments, return values, and who saves which register |
| [caller / callee-saved](02-instruction-set.md) | the promise about which registers survive a call (`t*`/`a*` vs `s*`/`sp`) |
| [ALU](03-arithmetic.md) | arithmetic logic unit — the block that adds, subtracts, and compares |
| [ripple-carry adder](03-arithmetic.md) | full adders chained so each carry feeds the next column |
| [overflow](../concept-index.md) | a true result too big for the fixed-width box; flagged when the sign-bit carries disagree |
| [shift-and-add](03-arithmetic.md) | multiply built from shifted copies of one operand, added up |
| [IEEE-754 / mantissa / exponent bias](03-arithmetic.md) | float = sign · (1.fraction) · $2^{\text{raw exp} - \text{bias}}$ |
| [floating point](../concept-index.md) | the format itself, and the rounding it forces on most decimals |
| [datapath](04-datapath.md) | the fixed units (PC, register file, ALU, memories, muxes) that carry out any instruction |
| [control signal](04-datapath.md) | a one-bit switch decoded from the opcode that routes data through the datapath |
| [pipeline stage](05-pipelining.md) | one of IF, ID, EX, MEM, WB — five instructions can be in flight at once |
| [structural / data / control hazard](05-pipelining.md) | the three reasons the next instruction cannot always run in the next cycle |
| [forwarding](05-pipelining.md) | routing a result from a pipeline register straight back to the ALU, avoiding a stall |
| [stall (bubble)](05-pipelining.md) | an idle cycle inserted when forwarding cannot deliver a value in time |
| [branch prediction](05-pipelining.md) | guessing a branch outcome to keep fetching; only a wrong guess costs cycles |
| [ILP / DLP / TLP](06-parallelism.md) | instruction-, data-, and thread-level parallelism — three of the four scales |
| [SIMD](06-parallelism.md) | one instruction over many data lanes; numpy's vectorization *is* SIMD |
| [systolic array](06-parallelism.md) | the TPU's grid of multiply-accumulate cells that reuse each loaded value $N$ times |
| [memory wall](06-parallelism.md) | the point past which more compute lanes just wait on memory bandwidth |

On to the practice.

These exercises walk the chapter in order — performance, the ISA, arithmetic,
the datapath, pipelining, parallelism — easiest first. Every solution runs in
your browser; three of them (marked *predict first*) ask you to write down the
answer before you press **▶ Run**. Reach for the CPU performance equation and
Amdahl's law the way the chapter did: with arithmetic, not a hunch.

### Exercise 23.5.1 — Pick the faster chip ● *(predict first)*

Two chips run the *same* program. Chip A runs at **4 GHz**, executes
**4 billion** instructions at **CPI 1.5**. Chip B runs at **2 GHz**, executes
**2 billion** instructions at **CPI 1.0**. Using
$\text{CPU time} = \text{Instructions} \times \text{CPI} \times \text{cycle time}$
(with cycle time $= 1/\text{clock}$), **predict which finishes first** before
you run it. Does the higher clock win?

??? success "Solution"

    Chip A: $4\times10^9 \times 1.5 / 4\times10^9 = 1.5$ s.
    Chip B: $2\times10^9 \times 1.0 / 2\times10^9 = 1.0$ s. Chip **B** wins —
    despite *half* the clock rate — because it runs fewer instructions at a
    lower CPI. Clock speed is only one of three factors.

    ```python
    def cpu_time(instructions, cpi, clock_hz):
        return instructions * cpi / clock_hz     # cycle time = 1/clock

    t_a = cpu_time(4e9, 1.5, 4e9)     # the 4 GHz chip
    t_b = cpu_time(2e9, 1.0, 2e9)     # the 2 GHz chip
    print(f"Chip A (4 GHz): {t_a:.2f} s")
    print(f"Chip B (2 GHz): {t_b:.2f} s")
    print(f"Chip B wins, {t_a / t_b:.2f}x faster -- despite HALF the clock rate")
    ```

    Prints `1.50 s`, `1.00 s`, and a `1.50x` win for B. This is the lesson of
    [23.5.1](01-performance.md): judge speed by *time on a real workload*, never
    by gigahertz alone.

### Exercise 23.5.2 — Weighted CPI from a mix ●

A program's instruction mix is **40% ALU** (CPI 1), **25% loads** (CPI 4),
**10% stores** (CPI 3), and **25% branches** (CPI 2). Compute the program's
overall CPI as the frequency-weighted average, and work out what share of all
cycles the loads consume.

??? success "Solution"

    The overall CPI is the dot product of frequencies and per-class costs:
    $0.40(1) + 0.25(4) + 0.10(3) + 0.25(2) = 0.40 + 1.00 + 0.30 + 0.50 = 2.20$.
    Loads contribute $1.00$ of those $2.20$ cycles.

    ```python
    import numpy as np

    kinds  = ["ALU", "Load", "Store", "Branch"]
    freq   = np.array([0.40, 0.25, 0.10, 0.25])   # fractions, must sum to 1
    cpi_of = np.array([1.0,  4.0,  3.0,  2.0])     # cycles per instruction
    assert np.isclose(freq.sum(), 1.0)

    avg_cpi = float(freq @ cpi_of)                 # weighted average = dot product
    for k, f, c in zip(kinds, freq, cpi_of):
        print(f"  {k:<7} {f:>4.0%}  CPI {c:>3.0f}  -> contributes {f * c:.2f} cycles")
    print(f"overall CPI = {avg_cpi:.2f} cycles/instruction")

    load_share = (freq[1] * cpi_of[1]) / avg_cpi
    print(f"loads are {freq[1]:.0%} of instructions but {load_share:.0%} of all cycles")
    ```

    The weighted CPI is **2.20**, and loads are only **25%** of the instructions
    yet **45%** of the cycles — the signpost that says *speed up the loads, not
    the cheap ALU ops*, and the seed of Amdahl's law
    ([23.5.1](01-performance.md)).

### Exercise 23.5.3 — Amdahl's ceiling ●●

Three-quarters of a program ($p = 0.75$) can be accelerated; the rest is stuck
serial. Compute the overall speed-up when the accelerated part is sped up by
$s = 2$, $3$, and $10$, and state the absolute ceiling no $s$ can beat. Explain
*why* the ceiling exists.

??? success "Solution"

    Amdahl's law is $\text{speedup} = 1 / \bigl((1-p) + p/s\bigr)$. The
    $(1-p) = 0.25$ term never shrinks, so as $s \to \infty$ the speed-up tends
    to $1/(1-p) = 4\times$ — the serial quarter caps everything.

    ```python
    def amdahl(p, s):
        return 1.0 / ((1 - p) + p / s)

    p = 0.75
    for s in [2, 3, 10]:
        print(f"  s = {s:>2}x  ->  overall speedup = {amdahl(p, s):.2f}x")
    print(f"  s -> infinity  ->  {1 / (1 - p):.2f}x   (the hard ceiling)")
    ```

    A $2\times$ boost yields `1.60x`, a $3\times$ boost `2.00x`, a $10\times$
    boost only `3.08x`, and no $s$ ever beats **4.00x**. The un-accelerated 25%
    still costs its full time, so it dominates once the fast part is nearly free
    — the honest brake on every optimization ([23.5.1](01-performance.md)).

### Exercise 23.5.4 — Decode a 32-bit instruction ●●

Decode the 32-bit word `0x02A00793` into its RISC-V fields and name the
instruction. The low 7 bits are the opcode; `0010011` is an I-type
(OP-IMM). Pull each field out with the same masks-and-shifts the decode stage
uses.

??? success "Solution"

    The opcode is `0010011` (I-type), `rd = x15`, `funct3 = 000`, `rs1 = x0`,
    and the 12-bit immediate is `42` — so the instruction is `addi x15, x0, 42`,
    i.e. "load the constant 42 into `x15`."

    ```python
    def field(w, hi, lo):
        """Pull bits [hi:lo] inclusive out of a 32-bit word."""
        return (w >> lo) & ((1 << (hi - lo + 1)) - 1)

    w = 0x02A00793
    opcode = field(w, 6, 0)
    rd     = field(w, 11, 7)
    funct3 = field(w, 14, 12)
    rs1    = field(w, 19, 15)
    imm    = field(w, 31, 20)

    print("opcode :", format(opcode, "07b"), "-> I-type (OP-IMM)")
    print(f"rd     : x{rd}")
    print(f"funct3 : {funct3:03b}")
    print(f"rs1    : x{rs1}")
    print(f"imm    : {imm}")
    assert (opcode, rd, funct3, rs1, imm) == (0b0010011, 15, 0b000, 0, 42)
    print(f"=> addi x{rd}, x{rs1}, {imm}   (x{rd} = x{rs1} + {imm} = {imm})")
    ```

    Every field is masked and shifted out of the one word, exactly as the
    hardware's decode stage does it ([23.5.2](02-instruction-set.md)) — and the
    `assert` makes the page unable to lie about the answer.

### Exercise 23.5.5 — Trace a stack frame ●● *(predict first)*

`sum_to(n) = n + sum_to(n-1)` with `sum_to(0) = 0`. Run the hardware-level model
of `sum_to(2)`: each call builds a 2-word frame saving `ra` and its own `n`, and
`sp` marches down then back up. **Predict the answer and how many words of stack
it uses at its deepest** before running.

??? success "Solution"

    `sum_to(2) = 2 + 1 + 0 = 3`. Three frames are live at the base case, each
    2 words, so the deepest stack use is **6 words**, after which the stack
    unwinds and `sp` returns exactly to the top.

    ```python
    STACK = 8
    mem = [None] * STACK                 # stack memory, one slot per word
    reg = {"sp": STACK, "ra": "<main>"}  # sp starts at the top; grows downward
    deepest = 0

    def dump(tag):
        print(f"{tag:<20} sp={reg['sp']}  words used={STACK - reg['sp']}")

    def sum_to(n):
        global deepest
        reg["sp"] -= 2                   # prologue: addi sp, sp, -8
        base = reg["sp"]
        mem[base + 1] = reg["ra"]        # sw ra, 4(sp)
        mem[base + 0] = n                # sw s0, 0(sp)  -- save our n
        deepest = max(deepest, STACK - reg["sp"])
        dump(f"call sum_to({n})")
        if n == 0:
            result = 0                   # base case: a leaf, makes no call
        else:
            reg["ra"] = f"resume({n})"   # jal sets ra; the nested call clobbers it
            inner = sum_to(n - 1)
            n = mem[base + 0]            # reload our n: lw s0, 0(sp)
            result = n + inner
        reg["ra"] = mem[base + 1]        # epilogue: restore caller's ra
        reg["sp"] += 2                   # pop the frame
        dump(f"ret  sum_to={result}")
        return result

    ans = sum_to(2)
    print(f"\nsum_to(2) = {ans};  deepest stack use = {deepest} words")
    print("sp back at the top:", reg["sp"] == STACK)
    ```

    The trace shows `sp` descending `8 -> 6 -> 4 -> 2` and climbing back, with
    each frame restoring its own `ra`. Skip the `ra` save and the innermost
    return address would be lost — the hardware reason recursion needs a stack
    ([23.5.2](02-instruction-set.md), [17.1](../ch17-recursion/01-call-stack.md)).

### Exercise 23.5.6 — Shift-and-add multiply ●● *(predict first)*

The shift-and-add multiplier adds a shifted copy of `a` for each **1-bit** of
`b`. For `11 × 6`, **predict which partial products appear** (write `6` in
binary first) before running the multiplier.

??? success "Solution"

    `6` is `110`, so bits 1 and 2 are set (bit 0 is 0). The partial products are
    `11 << 1 = 22` and `11 << 2 = 44`; bit 0 contributes nothing. They sum to
    `22 + 44 = 66 = 11 × 6`.

    ```python
    def multiply(a, b):
        product, i = 0, 0
        print(f"multiplying {a} x {b}  (b = {b:b} in binary)")
        while (b >> i):                       # while 1-bits of b remain
            if (b >> i) & 1:
                partial = a << i              # a shifted left i = a * 2**i
                product += partial
                print(f"  bit {i} of b is 1 -> add {a}<<{i} = {partial:>3}   total {product}")
            else:
                print(f"  bit {i} of b is 0 -> add nothing          total {product}")
            i += 1
        return product

    result = multiply(11, 6)
    print(f"11 x 6 = {result}   (partial products were 22 and 44)")
    assert result == 11 * 6
    ```

    The two partial products `22` and `44` sum to `66`, exactly `11 * 6`. Because
    multiply is a *loop* over addition it costs more than a single add — the
    per-operation side of CPI ([23.5.3](03-arithmetic.md),
    [23.5.1](01-performance.md)).

### Exercise 23.5.7 — Decode a float ●●

Decode the single-precision float `-6.0` into its sign, exponent, and fraction
fields, then rebuild the value from those fields alone. Check your hand
arithmetic: `6.0 = 1.5 × 2²`, so the mantissa is `1.5` and the un-biased
exponent is `2`.

??? success "Solution"

    `6.0 = 1.5 × 2²`, so with a negative sign: sign bit `1`, raw exponent
    $2 + 127 = 129$, and fraction $0.5 \times 2^{23} = 4194304$ (the `.5` after
    the hidden `1.`). Rebuilt: $(-1)^1 \times 1.5 \times 2^2 = -6.0$.

    ```python
    import struct

    def inspect32(x):
        bits = struct.unpack(">I", struct.pack(">f", x))[0]   # exact 32-bit pattern
        sign = (bits >> 31) & 1
        exp_raw = (bits >> 23) & 0xFF
        frac = bits & 0x7FFFFF
        exp = exp_raw - 127                                   # un-bias
        value = (-1) ** sign * (1 + frac / 2 ** 23) * 2 ** exp
        print(f"{x!r}")
        print(f"  bits     : {bits:032b}")
        print(f"  sign     : {sign}  ({'-' if sign else '+'})")
        print(f"  exponent : raw {exp_raw} - bias 127 = {exp}")
        print(f"  fraction : {frac}  (= {frac}/2^23 = {frac / 2 ** 23})")
        print(f"  rebuilt  : (-1)^{sign} * (1 + {frac}/2^23) * 2^{exp} = {value}")
        return sign, exp, frac

    s, e, f = inspect32(-6.0)
    assert (s, e, f) == (1, 2, 4194304)
    print("hand decode agrees: -1 * 1.5 * 4 = -6.0")
    ```

    The sign lives in one isolated bit, the exponent scales by a power of two,
    and the fraction supplies the digits after the hidden `1.` — the whole
    IEEE-754 mechanism behind [5.1](../ch05-under-the-hood/01-numeric-pitfalls.md)'s
    `0.1 + 0.2` surprise ([23.5.3](03-arithmetic.md)).

### Exercise 23.5.8 — Fill in the control signals ●●

For the single-cycle datapath, write down the seven control signals for
`lw x6, 0(x5)` and for `beq x3, x4, LABEL`. Which signals does a `lw` assert
that a `beq` does not, and why does `beq` set `ALUOp = sub`?

??? success "Solution"

    `lw` writes a register from memory, so it needs `RegWrite=1`, `ALUSrc=1`
    (address = register + immediate), `MemRead=1`, `MemToReg=1`, `ALUOp=add`.
    `beq` writes nothing (`RegWrite=0`), reads two registers (`ALUSrc=0`), sets
    `Branch=1`, and uses `ALUOp=sub` so the **Zero** flag reports equality.

    ```python
    def control(op):
        table = {
            "add":  dict(RegWrite=1, ALUSrc=0, MemRead=0, MemWrite=0, Branch=0, MemToReg=0, ALUOp="add"),
            "addi": dict(RegWrite=1, ALUSrc=1, MemRead=0, MemWrite=0, Branch=0, MemToReg=0, ALUOp="add"),
            "lw":   dict(RegWrite=1, ALUSrc=1, MemRead=1, MemWrite=0, Branch=0, MemToReg=1, ALUOp="add"),
            "sw":   dict(RegWrite=0, ALUSrc=1, MemRead=0, MemWrite=1, Branch=0, MemToReg=0, ALUOp="add"),
            "beq":  dict(RegWrite=0, ALUSrc=0, MemRead=0, MemWrite=0, Branch=1, MemToReg=0, ALUOp="sub"),
        }
        return table[op]

    for op in ["lw", "beq"]:
        c = control(op)
        print(f"{op:<4} " + "  ".join(f"{k}={v}" for k, v in c.items()))

    assert control("lw")["MemRead"] == 1 and control("lw")["MemToReg"] == 1
    assert control("beq")["Branch"] == 1 and control("beq")["ALUOp"] == "sub"
    print("lw reads memory and writes the value back; beq subtracts to test equality")
    ```

    Only `lw` sets `MemRead` and `MemToReg` (it is the sole instruction that
    routes a memory value to a register); `beq` subtracts and, if the **Zero**
    flag fires, throws the branch mux — `Branch AND Zero`
    ([23.5.4](04-datapath.md)).

### Exercise 23.5.9 — Hazards and stalls ●●●

Take this three-instruction stream in the five-stage pipeline:

```text
lw   x1, 0(x2)     # loads x1
add  x3, x1, x4    # uses x1 right away
sub  x5, x3, x6    # uses x3
```

Predict, for each dependency, whether **forwarding** covers it or a **stall** is
needed, then count the total cycles. (Hint: a value from `lw` is not ready until
after MEM; an ALU result is ready after EX.)

??? success "Solution"

    `add` needs `x1` in its EX, but the `lw` only has it after MEM — a
    **load-use hazard**, so one bubble, then forward. `sub` needs `x3` from the
    immediately preceding `add`, whose result exists after EX — pure
    **forwarding**, no stall. So exactly **1 stall cycle**, and the stream takes
    $\text{fill}(4) + 3 + 1 = 8$ cycles.

    ```python
    prog = [
        dict(name="lw  x1, 0(x2)", op="lw",  dst=1, src=[2]),
        dict(name="add x3, x1, x4", op="add", dst=3, src=[1, 4]),
        dict(name="sub x5, x3, x6", op="sub", dst=5, src=[3, 6]),
    ]
    stalls = 0
    for i, ins in enumerate(prog):
        notes = []
        for j in range(i - 1, -1, -1):               # look back at in-flight instrs
            prod = prog[j]
            d = i - j                                # pipeline distance
            if prod["dst"] in ins["src"] and d <= 2:
                if prod["op"] == "lw" and d == 1:
                    notes.append(f"x{prod['dst']} load-use -> STALL 1, then forward")
                    stalls += 1
                else:
                    notes.append(f"x{prod['dst']} -> FORWARD (no stall)")
        print(f"{ins['name']:<16} " + ("; ".join(notes) if notes else "no hazard"))

    n, S = len(prog), 5
    print(f"\ntotal stall cycles = {stalls}")
    print(f"cycles = fill(S-1) + n + stalls = {S - 1} + {n} + {stalls} = {S - 1 + n + stalls}")
    ```

    The detector reports the `add` as a load-use **STALL** and the `sub` as a
    **FORWARD**, giving one bubble and 8 cycles total. Forwarding removes almost
    every ALU-to-ALU stall, but no wire can forward a load's value into the very
    next instruction's EX — the one hazard that always costs a bubble
    ([23.5.5](05-pipelining.md)).

### Exercise 23.5.10 — Multicore speed-up ●●● *(predict first)*

A program is **90% parallelizable**. **Predict** its speed-up on 2, 4, and 8
cores — and the ceiling for infinitely many cores — before running Amdahl's law
with $s = n$. Why does 8 cores give nowhere near 8×?

??? success "Solution"

    With $p = 0.90$, Amdahl gives $1/((1-0.9) + 0.9/n)$: **2 cores → 1.82×**,
    **4 cores → 3.08×**, **8 cores → 4.71×**, and even infinite cores only
    **10×**, because the serial 10% never speeds up. Efficiency (speed-up ÷
    cores) falls the more cores you add.

    ```python
    def multicore(p, n):
        return 1.0 / ((1 - p) + p / n)     # Amdahl with s = n cores

    p = 0.90
    for n in [2, 4, 8]:
        sp = multicore(p, n)
        print(f"  {n} cores -> {sp:.2f}x   ({sp / n:.0%} efficiency)")
    print(f"  infinite cores -> {1 / (1 - p):.1f}x   (the serial 10% is the ceiling)")
    ```

    The prints — `1.82x`, `3.08x`, `4.71x` (only 59% efficient), ceiling
    `10.0x` — show why "more cores" has sharply diminishing returns: the fix is
    to **shrink the serial fraction**, not buy cores. The same shortfall bites
    SIMD too — swapping a Python loop for numpy runs many times faster, but
    interpreter and memory overhead keep it below the raw lane count
    ([23.5.6](06-parallelism.md)).

!!! info "Where to go deeper"

    These exercises consolidate the whole chapter; each links back to the
    section that develops the idea in full, and all of it follows **Patterson &
    Hennessy, *Computer Organization and Design* (RISC-V edition)**. Return to
    the [chapter overview](index.md) for the map, or carry on to the memory side
    of the story in [23.4 the memory hierarchy](../ch23-os/04-memory-hierarchy.md)
    and the AI hardware of [Part V](../ch27-inference/index.md).
