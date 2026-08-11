# 23.5.2 · The instruction set up close

[Section 0.4](../ch00-machine/04-machine-instructions.md) gave you a postcard
of RISC-V: a handful of registers, about ten instructions, a tiny CPU you ran
in your browser, and one `addi x1, x2, 5` taken apart into fields. This section
is the full letter. It follows **Chapter 2 of Patterson & Hennessy's *Computer
Organization and Design*** — the chapter every architecture course spends weeks
on — and answers the questions the postcard raised: *why* do instructions only
touch registers, *how* are all of them shaped (not just `addi`), and *how does
a function call actually work* in the silicon. By the end you will name all six
RISC-V instruction formats, decode a 32-bit word into its fields by running
code, and watch a function call push and pop a stack frame — the same call
stack you already met in [recursion](../ch17-recursion/01-call-stack.md), now at
the level of the hardware.

## What 0.4 established — and what this section adds

Quick recap of the ground [0.4](../ch00-machine/04-machine-instructions.md)
already covered, so we can build on it instead of repeating it:

- **A machine instruction is just a number** — a bit pattern in memory, made an
  "instruction" only because the program counter (PC) points at it.
- **The CPU runs a fetch–decode–execute loop** — read the word at the PC, work
  out what it means, do it, advance the PC (or branch).
- **Registers are the CPU's scratch slots**, and RISC-V computes on them with a
  small vocabulary: `add`, `addi`, `lw`, `sw`, `beq`, `jal`, and a few more.
- **Decode is masks and shifts** — you unpacked `addi x1, x2, 5` (the number
  `5308563`) into `opcode`, `rd`, `funct3`, `rs1`, `imm`.

This section adds the depth underneath that:

- **The operand model** — why RISC machines compute *only* in registers and
  must `load`/`store` to reach memory, and what all 32 registers are *for*.
- **All six instruction formats** — R, I, S, B, U, J — with an encoder/decoder
  you run to see every field, and the design reasoning behind the layout.
- **Immediates and PC-relative addressing** — how constants and jump targets
  ride inside a fixed 32-bit word, and how sign-extension works.
- **Procedures and the stack** — the calling convention as a hardware protocol,
  built and torn down frame by frame.
- **Arrays, pointers, and the RISC-vs-CISC contrast** to close.

This is the middle rung of the chapter: [23.5.1](01-performance.md) measured how
*fast* instructions run; here we see *what they are*; [23.5.4](04-datapath.md)
builds the datapath that executes them.

## Operands: registers, not memory

!!! abstract "In plain words"

    - **What it is.** A RISC machine does arithmetic *only* on a tiny fixed set
      of registers. To use a value in RAM it must first `load` it into a
      register; to save a result it must `store` it back.
    - **Picture it.** A workbench with exactly 32 labelled slots. You can only
      work on parts that are *on* the bench; anything in the warehouse (RAM)
      has to be carried over first and carried back when you are done.
    - **Why it matters.** Registers are the fastest storage in the machine — the
      very top of the [memory hierarchy](../ch23-os/04-memory-hierarchy.md).
      Keeping instructions register-only makes them small, uniform, and quick
      to decode, and forces the slow trips to memory to be *explicit* so the
      compiler can minimise them.

Why not just let `add` read straight from RAM, like some older machines did?

- **Speed.** A register read is effectively free (part of the CPU core); a RAM
  read can cost tens to hundreds of times more (see the
  [memory hierarchy](../ch23-os/04-memory-hierarchy.md)). If every `add` could
  touch memory, every `add` might pay that price.
- **Simplicity.** With operands always in registers, each instruction names its
  inputs with a few bits (5 bits pick one of 32 registers) — so the whole
  instruction fits in a fixed 32-bit slot that is trivial to decode.
- **This is the "load–store architecture"** at the heart of RISC: *compute in
  registers, move to and from memory only with `lw`/`sw`*.

RISC-V has **32 integer registers**, `x0`–`x31`. By hardware, only one is
special: `x0` is wired to zero and ignores writes. The rest are
interchangeable to the CPU — but software agrees on a set of **roles** so that
separately-compiled functions can call each other. That agreement is the
**Application Binary Interface (ABI)**, and it gives each register a name:

| Register(s) | ABI name | Role | Preserved across a call? |
| --- | --- | --- | --- |
| `x0` | `zero` | hard-wired constant 0 | — (never changes) |
| `x1` | `ra` | return address | **no** (caller-saved) |
| `x2` | `sp` | stack pointer | **yes** (callee-saved) |
| `x3` | `gp` | global pointer | (special) |
| `x4` | `tp` | thread pointer | (special) |
| `x5`–`x7` | `t0`–`t2` | temporaries | **no** (caller-saved) |
| `x8` | `s0`/`fp` | saved reg / frame pointer | **yes** (callee-saved) |
| `x9` | `s1` | saved register | **yes** (callee-saved) |
| `x10`–`x11` | `a0`–`a1` | arguments **and** return values | **no** (caller-saved) |
| `x12`–`x17` | `a2`–`a7` | more arguments | **no** (caller-saved) |
| `x18`–`x27` | `s2`–`s11` | saved registers | **yes** (callee-saved) |
| `x28`–`x31` | `t3`–`t6` | temporaries | **no** (caller-saved) |

"Caller-saved" vs "callee-saved" is a promise about who protects a register
across a function call; we make it concrete in
[Procedures and the stack](#procedures-and-the-stack) below. A small model of
the register file:

```python
# RISC-V has exactly 32 integer registers. x0 is hard-wired to 0: writes to it
# are silently dropped. Everything else is general-purpose; the ABI names below
# are a *software* convention, invisible to the hardware.
reg = [0] * 32

def write(x, value):
    if x != 0:            # x0 ignores writes -- this is the whole special case
        reg[x] = value

write(5, 42)              # t0 = 42
write(0, 999)             # try to overwrite x0 ... hardware refuses
print("x5 (t0) =", reg[5])
print("x0 (zero) =", reg[0], " -- still zero, as always")

abi = {0: "zero", 1: "ra", 2: "sp", 8: "s0/fp",
       10: "a0", 11: "a1", 17: "a7", 27: "s11", 31: "t6"}
print("a few ABI roles:")
for x in sorted(abi):
    print(f"  x{x:<2} = {abi[x]}")
```

Having `x0` always read as zero is a quiet trick that saves instructions: a "no
operation" is just `addi x0, x0, 0`, and "copy `x5` into `x6`" is `addi x6, x5,
0` — no dedicated `nop` or `mov` instruction needed.

## The six instruction formats

!!! abstract "In plain words"

    - **What it is.** Every RISC-V instruction is exactly 32 bits, and those 32
      bits are carved into fields in one of just **six standard layouts** —
      named R, I, S, B, U, and J. The layout tells the CPU where to find the
      registers, the operation, and any constant.
    - **Picture it.** Six paper forms, all the same size. Whatever the form, the
      "destination" box and the "source register" boxes are always printed in
      the *same place* — so a clerk (the decoder) can read them without first
      figuring out which form it is.
    - **Why it matters.** Fixed width and fixed field positions are what make
      RISC-V decode fast and cheap in hardware: the CPU can pull out the
      register numbers *before* it has even finished identifying the
      instruction, because they never move.

The formats differ in one thing: **what kind of operands the instruction
carries** (two registers and a destination? one register and a constant? a
branch target?). Here is each, field by field. Field widths always sum to 32.

- **R-type** — register–register arithmetic (`add`, `sub`, `and`, `or`, `sll`,
  `slt`, …).
    - Fields: `funct7`(7) · `rs2`(5) · `rs1`(5) · `funct3`(3) · `rd`(5) ·
      `opcode`(7).
    - No immediate — all three operands are registers.
    - `opcode` = `0110011` (OP); `funct3`+`funct7` pick the exact operation
      (`add` is `funct3=000, funct7=0000000`; `sub` reuses `funct3=000` with
      `funct7=0100000`).
    - Example: `add x1, x2, x3` → `x1 = x2 + x3`.
- **I-type** — an immediate plus one register: immediate arithmetic (`addi`,
  `andi`, `slli`), **loads** (`lw`, `lb`), and `jalr`.
    - Fields: `imm[11:0]`(12) · `rs1`(5) · `funct3`(3) · `rd`(5) · `opcode`(7).
    - One 12-bit signed immediate occupies the whole top of the word.
    - `opcode` = `0010011` (OP-IMM) for `addi`; `0000011` (LOAD) for `lw`.
    - Example: `addi x1, x2, 5` → `x1 = x2 + 5`; `lw x6, 8(x10)` →
      `x6 = memory[x10 + 8]`.
- **S-type** — **stores** (`sw`, `sb`, `sh`).
    - Fields: `imm[11:5]`(7) · `rs2`(5) · `rs1`(5) · `funct3`(3) ·
      `imm[4:0]`(5) · `opcode`(7).
    - The 12-bit immediate is **split in two** so that `rs1` and `rs2` stay in
      their usual positions (more on why below).
    - `opcode` = `0100011` (STORE).
    - Example: `sw x1, 8(x2)` → `memory[x2 + 8] = x1`.
- **B-type** — conditional **branches** (`beq`, `bne`, `blt`, `bge`).
    - Fields: `imm[12]` · `imm[10:5]`(6) · `rs2`(5) · `rs1`(5) · `funct3`(3) ·
      `imm[4:1]`(4) · `imm[11]` · `opcode`(7).
    - A 13-bit signed offset with bit 0 always 0 (targets are even), scattered
      so the register fields never move.
    - `opcode` = `1100011` (BRANCH).
    - Example: `beq x5, x6, LABEL` → if `x5 == x6`, jump to `LABEL`.
- **U-type** — a 20-bit **upper immediate** (`lui`, `auipc`).
    - Fields: `imm[31:12]`(20) · `rd`(5) · `opcode`(7).
    - Loads a big constant into the top 20 bits of a register.
    - `opcode` = `0110111` (LUI). Example: `lui x5, 0x12345` → `x5 =
      0x12345000`. Pairing `lui` with an `addi` builds any 32-bit constant.
- **J-type** — the unconditional **jump-and-link** (`jal`).
    - Fields: `imm[20]` · `imm[10:1]`(10) · `imm[11]` · `imm[19:12]`(8) ·
      `rd`(5) · `opcode`(7).
    - A 21-bit signed offset (bit 0 always 0), even more scattered than B.
    - `opcode` = `1101111` (JAL). Example: `jal ra, LABEL` → jump to `LABEL` and
      save the return address in `ra`.

All six at a glance:

| Format | Carries | Immediate | Typical instructions | opcode |
| --- | --- | --- | --- | --- |
| **R** | `rd, rs1, rs2` | none | `add`, `sub`, `sll`, `slt` | `0110011` |
| **I** | `rd, rs1, imm` | 12-bit signed | `addi`, `lw`, `jalr` | `0010011` / `0000011` |
| **S** | `rs1, rs2, imm` | 12-bit split | `sw`, `sb`, `sh` | `0100011` |
| **B** | `rs1, rs2, imm` | 13-bit split | `beq`, `bne`, `blt` | `1100011` |
| **U** | `rd, imm` | 20-bit upper | `lui`, `auipc` | `0110111` |
| **J** | `rd, imm` | 21-bit split | `jal` | `1101111` |

### Encode and decode them yourself

This is the deep version of the single-instruction demo from
[0.4](../ch00-machine/04-machine-instructions.md). Below we encode three real
instructions — one R-type, one I-type (both an `addi` and an `lw`), and one
S-type — into their 32-bit words, **assert each against the value the RISC-V
spec requires**, then decode every field back and print the binary with labels.

```python
# --- RISC-V encoder/decoder for the R, I, and S formats -------------------
OP     = 0b0110011   # 0x33  R-type register arithmetic
OP_IMM = 0b0010011   # 0x13  I-type arithmetic with an immediate
LOAD   = 0b0000011   # 0x03  I-type loads
STORE  = 0b0100011   # 0x23  S-type stores

def field(word, hi, lo):
    """Pull bits [hi:lo] (inclusive) out of a 32-bit word -- decode is masks
    and shifts, exactly as the hardware does it."""
    return (word >> lo) & ((1 << (hi - lo + 1)) - 1)

def enc_r(funct7, rs2, rs1, funct3, rd, opcode):
    return (funct7 << 25) | (rs2 << 20) | (rs1 << 15) | (funct3 << 12) | (rd << 7) | opcode

def enc_i(imm, rs1, funct3, rd, opcode):
    return ((imm & 0xFFF) << 20) | (rs1 << 15) | (funct3 << 12) | (rd << 7) | opcode

def enc_s(imm, rs2, rs1, funct3, opcode):
    imm &= 0xFFF
    return ((imm >> 5) << 25) | (rs2 << 20) | (rs1 << 15) | (funct3 << 12) | ((imm & 0x1F) << 7) | opcode

# Encode four real instructions:
add_  = enc_r(0b0000000, 3, 2, 0b000, 1, OP)     # add  x1, x2, x3
addi_ = enc_i(5,             2, 0b000, 1, OP_IMM) # addi x1, x2, 5
lw_   = enc_i(8,            10, 0b010, 6, LOAD)    # lw   x6, 8(x10)
sw_   = enc_s(8, 1,          2, 0b010, STORE)      # sw   x1, 8(x2)

# Verify every word against the encodings the RISC-V spec pins down. If any of
# these is wrong the block fails loudly -- so the page cannot lie about them.
assert add_  == 0x003100B3, hex(add_)
assert addi_ == 0x00510093, hex(addi_)   # == 5308563, the very number from 0.4
assert lw_   == 0x00852303, hex(lw_)
assert sw_   == 0x00112423, hex(sw_)
print("all four words match the RISC-V specification\n")

def show(title, word, fields):
    """Print a labelled field breakdown of a 32-bit instruction word.
    `fields` runs from the most-significant field to the least."""
    labels, bitrows = [], []
    for label, nbits, value in fields:
        b = format(value & ((1 << nbits) - 1), f"0{nbits}b")
        w = max(len(label), len(b))
        labels.append(label.center(w))
        bitrows.append(b.center(w))
    print(f"{title:<16} {word:#010x}  = {word}")
    print("   " + "  ".join(labels))
    print("   " + "  ".join(bitrows))
    print()

show("add  x1,x2,x3", add_, [
    ("funct7", 7, field(add_, 31, 25)), ("rs2", 5, field(add_, 24, 20)),
    ("rs1", 5, field(add_, 19, 15)),    ("f3", 3, field(add_, 14, 12)),
    ("rd", 5, field(add_, 11, 7)),      ("opcode", 7, field(add_, 6, 0))])

show("addi x1,x2,5", addi_, [
    ("imm[11:0]", 12, field(addi_, 31, 20)), ("rs1", 5, field(addi_, 19, 15)),
    ("f3", 3, field(addi_, 14, 12)),         ("rd", 5, field(addi_, 11, 7)),
    ("opcode", 7, field(addi_, 6, 0))])

show("lw   x6,8(x10)", lw_, [
    ("imm[11:0]", 12, field(lw_, 31, 20)), ("rs1", 5, field(lw_, 19, 15)),
    ("f3", 3, field(lw_, 14, 12)),         ("rd", 5, field(lw_, 11, 7)),
    ("opcode", 7, field(lw_, 6, 0))])

show("sw   x1,8(x2)", sw_, [
    ("imm[11:5]", 7, field(sw_, 31, 25)), ("rs2", 5, field(sw_, 24, 20)),
    ("rs1", 5, field(sw_, 19, 15)),       ("f3", 3, field(sw_, 14, 12)),
    ("imm[4:0]", 5, field(sw_, 11, 7)),   ("opcode", 7, field(sw_, 6, 0))])

# The S-type immediate is split across two fields. Reassemble it:
imm = (field(sw_, 31, 25) << 5) | field(sw_, 11, 7)
print("sw's split immediate, glued back together:", imm, "(the '8' in sw x1, 8(x2))")
```

Read any block of bits above and you are doing exactly what the CPU's decode
stage does. Notice the payoff of the design:

- In **every** format, `opcode` is the same 7 low bits, and where a register
  field exists, `rd` sits at bits 11–7 and `rs1`/`rs2` at 19–15 / 24–20.
- That is why the S-type and B-type immediates look *scattered*: rather than
  disturb the register fields, RISC-V chops the immediate into whatever bits are
  left over. The hardware pays nothing for this — it just routes fixed wires —
  and gains a decoder that can read register numbers before it knows the
  instruction. This is one of COD's signature insights.
- **Fixed 32-bit width** means the next instruction is always at `PC + 4`; the
  fetch unit never has to parse an instruction to know where the next one
  begins. (This is the opposite of x86 — see [RISC vs CISC](#risc-vs-cisc).)

## Immediates and addressing

Constants do not live in registers or memory — small ones ride *inside the
instruction word* as the immediate field. Two facts make them work:

- **Sign-extension.** A 12-bit immediate is *signed*: if its top bit (bit 11) is
  1, the value is negative, and the CPU extends that 1 across all the upper bits
  before using it. So `addi x5, x0, -1` really does put `-1` in `x5`.
- **PC-relative addressing for branches and jumps.** A branch does not store the
  absolute address of its target. It stores a *signed offset*, and the CPU
  computes `target = PC + offset`. Positive offsets jump forward; negative
  offsets jump backward — and a backward branch is exactly how a loop is built
  (as the tiny CPU's `BNE` did in
  [0.4](../ch00-machine/04-machine-instructions.md)).

Here we assemble two branches — one forward, one backward — decode the scattered
B-type offset back out, sign-extend it, and compute the target:

```python
# --- B-type branch: encode an offset, decode it, resolve the target -------
BRANCH = 0b1100011   # 0x63

def field(word, hi, lo):
    return (word >> lo) & ((1 << (hi - lo + 1)) - 1)

def enc_b(imm, rs2, rs1, funct3, opcode):
    imm &= 0x1FFF                       # 13-bit signed offset; bit 0 is always 0
    return ((((imm >> 12) & 1) << 31) | (((imm >> 5) & 0x3F) << 25) |
            (rs2 << 20) | (rs1 << 15) | (funct3 << 12) |
            (((imm >> 1) & 0xF) << 8) | (((imm >> 11) & 1) << 7) | opcode)

def dec_b_offset(word):
    imm = ((field(word, 31, 31) << 12) | (field(word, 7, 7) << 11) |
           (field(word, 30, 25) << 5)  | (field(word, 11, 8) << 1))
    if imm & (1 << 12):                 # top bit set -> negative: sign-extend
        imm -= (1 << 13)
    return imm

fwd  = enc_b(12, 6, 5, 0b000, BRANCH)   # beq x5, x6, +12  (skip three instructions)
back = enc_b(-8, 6, 5, 0b000, BRANCH)   # beq x5, x6, -8   (top of a loop)
assert fwd == 0x00628663, hex(fwd)      # matches the RISC-V spec

for name, word, pc in [("beq x5,x6,+12", fwd, 0x1000),
                       ("beq x5,x6,-8",  back, 0x2000)]:
    off = dec_b_offset(word)
    print(f"{name:<14} word={word:#010x}  offset={off:+d}  "
          f"PC={pc:#06x} -> target = PC{off:+d} = {pc + off:#06x}")
```

The forward branch lands at `0x1000 + 12 = 0x100c`; the backward branch lands at
`0x2000 - 8 = 0x1ff8`, earlier in the program. The negative offset survived the
trip because we sign-extended it — drop that step and `-8` would read as a huge
positive jump. This is [two's complement from 0.2](../ch00-machine/02-binary.md)
doing real work inside the decoder.

## Procedures and the stack

!!! abstract "In plain words"

    - **What it is.** A **function call** in hardware is a protocol: jump to the
      callee while remembering where to come back, hand over arguments in
      agreed registers, get a result back in an agreed register, and leave every
      "saved" register exactly as you found it.
    - **Picture it.** Borrowing a colleague's desk. The contract: note where you
      came from so you can return, only mess up the drawers you agreed are
      "scratch", and if you *do* need a "keep this" drawer, photograph its
      contents first and put them back before you leave. The **stack** is the
      pile of these photographs, one per active call.
    - **Why it matters.** This protocol is what lets separately-written
      functions — including a function calling *itself* — compose without
      clobbering each other. It is the hardware reality beneath the call stack
      you met in [Chapter 5](../ch05-under-the-hood/03-stack-heap.md) and
      [recursion](../ch17-recursion/01-call-stack.md).

The instructions and registers that make the protocol:

- **`jal rd, LABEL`** ("jump and link") — jump to `LABEL` and store the *return
  address* (the address of the following instruction, `PC + 4`) into `rd`,
  conventionally `ra`.
- **`jalr rd, offset(rs1)`** — jump to `rs1 + offset`, saving the return address
  in `rd`. Returning from a function is just `jalr x0, 0(ra)` (jump to `ra`,
  discard the link) — usually written `ret`.
- **Arguments** go in `a0`–`a7`; **return values** come back in `a0`(–`a1`).
- **`sp` (the stack pointer)** points at the top of the stack, which grows
  *downward* toward lower addresses. A function makes room by *subtracting* from
  `sp`.
- **Caller-saved (`t*`, `a*`, `ra`)** — if the caller wants these preserved
  across a call, *the caller* must save them first; the callee may trash them.
- **Callee-saved (`s*`, `sp`)** — the callee promises to leave these as it found
  them, so if it wants to use one, *the callee* must save and restore it.

A non-leaf function (one that itself calls something) must save `ra` — otherwise
the inner call's `jal` overwrites it and the function forgets how to return. It
does that by building a **stack frame**: a slice of stack memory it owns for the
duration of the call. The choreography:

```text
# prologue -- make a 2-word (8-byte) frame and save what we must preserve
addi sp, sp, -8        # grow the stack downward by one frame
sw   ra, 4(sp)         # save the return address (we are about to make a call)
sw   s0, 0(sp)         # save callee-saved s0, because we want to use it
# ... body: use s0 freely, make nested calls ...
# epilogue -- restore and hand the frame back
lw   s0, 0(sp)         # restore s0 for our caller
lw   ra, 4(sp)         # restore our own return address
addi sp, sp, 8         # pop the frame (shrink the stack back)
ret                    # jalr x0, 0(ra): jump back to the caller
```

Now watch it run. We simulate `sum_to(n) = n + sum_to(n-1)` (with
`sum_to(0) = 0`) as the hardware would: each recursive call builds a frame that
saves `ra` and the callee-saved slot holding `n`, and the stack pointer marches
down and back up. This is the [recursion call
stack](../ch17-recursion/01-call-stack.md) with the register-and-memory
machinery made visible.

```python
# --- a hardware-level model of the RISC-V calling convention --------------
# We count the stack in WORDS for readability; real RISC-V counts bytes, so a
# 2-word frame is the `addi sp, sp, -8` from the assembly above.
STACK = 16
mem = [None] * STACK                       # stack memory, one slot per word
reg = {"sp": STACK, "ra": "<program>"}     # sp starts at the top; grows downward

def dump(tag):
    live = list(range(reg["sp"], STACK))   # slots from sp up to the top are in use
    cells = "  ".join(f"mem[{i}]={mem[i]!r}" for i in live) or "(empty)"
    print(f"{tag:<22} sp={reg['sp']:<2} | {cells}")

def sum_to(n):
    # PROLOGUE: addi sp,sp,-8 ; sw ra,4(sp) ; sw s0,0(sp)
    reg["sp"] -= 2
    base = reg["sp"]
    mem[base + 1] = reg["ra"]              # save the return address
    mem[base + 0] = n                      # save n in the callee-saved slot (s0)
    dump(f"call sum_to({n})")

    if n == 0:
        result = 0                         # base case: a leaf, makes no call
    else:
        reg["ra"] = f"resume(n={n})"       # jal sets ra; the nested call will clobber it
        inner = sum_to(n - 1)              # recurse -- this trashes ra and s0 ...
        n = mem[base + 0]                  # ... so reload our own n: lw s0, 0(sp)
        result = n + inner

    # EPILOGUE: lw s0,0(sp) ; lw ra,4(sp) ; addi sp,sp,8 ; ret
    reg["ra"] = mem[base + 1]              # restore the caller's return address
    reg["sp"] += 2                         # pop the frame
    dump(f"ret  sum_to({n})={result}")
    return result

print("running sum_to(3) on a simulated stack (grows downward):\n")
answer = sum_to(3)
print(f"\nsum_to(3) = {answer}")
print("stack fully unwound, sp back at the top:", reg["sp"] == STACK)
```

What the trace shows, tied back to what you already know:

- **`sp` marches down on every call and back up on every return** — four frames
  deep at the base case, then unwound in reverse. That is the call stack of
  [Chapter 17](../ch17-recursion/01-call-stack.md), except here you can point at
  the exact memory word each frame lives in.
- **`ra` is saved into the frame and restored on the way out.** Without that
  save, the innermost `jal` would leave `ra` pointing at the wrong place and the
  recursion could never find its way home — the hardware reason recursion needs
  a stack at all.
- **The frame is private to one call.** Each `sum_to` reads its *own* `n` back
  from its *own* frame after the nested call returns, so the values never
  collide. `sum_to(3)` returns `3 + 2 + 1 + 0 = 6`, and `sp` ends exactly where
  it started.

If a frame is never popped — say, unbounded recursion — `sp` keeps marching down
until it collides with the heap: a **stack overflow**, the concrete meaning of
the error from [Chapter 5](../ch05-under-the-hood/03-stack-heap.md).

## Arrays and pointers, briefly

An array access like `a[i]` looks atomic in source code, but the hardware has no
"index" operation — it can only load or store at a computed address. The
compiler turns `a[i]` into **base + i × element-size**, the same address formula
behind [arrays vs lists](../ch07-arrays/01-arrays-vs-lists.md):

- The array's base address (`&a[0]`) sits in a register.
- The index `i` sits in another.
- Multiply `i` by the element size (4 bytes for a 32-bit `int`), add the base,
  then `lw` from that address.

For `int a[]` with the base in `x10` and `i` in `x11`, `total += a[i]` becomes:

```text
slli x5, x11, 2      # x5 = i * 4      (multiply by 4 == shift left by 2)
add  x5, x10, x5     # x5 = &a[0] + i*4  ==  &a[i]
lw   x6, 0(x5)       # x6 = a[i]
add  x12, x12, x6    # total += a[i]
```

- This is why array indexing is **O(1)**: it is a fixed shift-add-load, no
  matter how large the array or how big `i` — the cost model from
  [Chapter 16](../ch16-complexity/index.md).
- It is also why the element *size* matters: doubling to 8-byte elements changes
  the `slli` shift from 2 to 3. A "pointer" is nothing more mysterious than a
  register holding one of these addresses.

## RISC vs CISC

RISC-V is a **RISC** (Reduced Instruction Set Computer); Intel/AMD **x86** is
the archetypal **CISC** (Complex Instruction Set Computer). The contrast, kept
honest:

- **Instruction length.** RISC-V base instructions are a **fixed 32 bits** (with
  an optional 16-bit "compressed" extension); x86 instructions are **variable
  length**, from 1 to 15 bytes. Fixed width makes RISC-V trivial to fetch and
  decode; variable width lets x86 pack common operations tightly.
- **Operands.** RISC-V is **load–store**: arithmetic touches only registers.
  x86 arithmetic can operate **directly on memory** (`add [addr], eax`), so one
  x86 instruction may do the work of several RISC-V ones.
- **Registers.** RISC-V exposes **32** general-purpose integer registers; x86-64
  exposes **16**. More architectural registers means fewer trips to the stack.
- **Formats.** RISC-V has the **six regular formats** above; x86 has many
  encodings with prefixes, mod-R/M bytes, and optional fields.
- **No myth, though.** RISC is not universally "faster," and x86 is not
  obsolete: modern x86 chips **decode their complex instructions into simple
  RISC-like micro-operations (μops)** internally and execute those, so the two
  worlds meet inside the core. x86 still dominates desktops and servers; RISC
  designs (ARM, RISC-V) dominate phones and embedded devices. The real
  trade-off is *decoder simplicity and code density*, not raw speed.

!!! warning "Common mistakes"

    - **Thinking `add` can read from memory.** In a load–store architecture it
      cannot. You must `lw` a value into a register first, compute, then `sw`
      the result back. Only loads and stores touch memory.
    - **Reading a scattered immediate straight off the bit positions.** The
      S-, B-, and J-type immediates are split across non-adjacent fields. You
      must reassemble the pieces (and, for signed offsets, sign-extend) before
      the number means anything — as the decoder in this section does.
    - **Forgetting to sign-extend a negative immediate.** A 12-bit `-1` is
      `0xFFF`; taken as unsigned that is `4095`, not `-1`. The CPU extends the
      top bit; your mental model must too.
    - **Assuming a callee preserves every register.** Only the callee-saved
      registers (`s0`–`s11`, `sp`) survive a call untouched. Anything you keep
      in a temporary (`t0`–`t6`) or an argument register can be gone after a
      `jal`; save it yourself if you need it.
    - **Believing a `while` loop exists in hardware.** There is no loop
      instruction — only a conditional **backward branch** whose PC-relative
      offset is negative.

## Check your understanding

1. Why does a RISC machine forbid arithmetic instructions from reading operands
   directly out of memory?

    ??? success "Answer"
        So every instruction stays small, uniform, and fast to decode, and so
        the expensive trips to memory are *explicit*. Registers are the fastest
        storage in the machine (top of the [memory
        hierarchy](../ch23-os/04-memory-hierarchy.md)); computing only on them
        keeps each instruction to a fixed 32 bits (a register needs just 5 bits
        to name) and lets the compiler minimise slow `lw`/`sw` traffic. This is
        the load–store architecture at the core of RISC.

2. The S-type (store) and B-type (branch) formats split their immediate across
   two non-adjacent fields. Why go to that trouble instead of using one
   contiguous field?

    ??? success "Answer"
        To keep the register fields (`rs1`, `rs2`, `rd`) in the *same bit
        positions* across all formats. The decoder can then extract register
        numbers before it has even identified the instruction, because those
        fields never move. RISC-V pays nothing in hardware for the scattered
        immediate — it is just fixed wiring — and gains a simpler, faster
        decoder. It is a deliberate COD-highlighted trade.

3. A non-leaf function's very first instructions save `ra` onto the stack. What
   goes wrong if it skips that step and then calls another function?

    ??? success "Answer"
        The nested call's `jal` overwrites `ra` with *its* return address, so
        the outer function loses the address it was supposed to return to. When
        it finally executes `ret`, it jumps back to the wrong place. Saving `ra`
        in the stack frame — and restoring it in the epilogue — is exactly what
        lets calls nest, and is why recursion needs a stack
        ([Chapter 17](../ch17-recursion/01-call-stack.md)).

4. Decode this 32-bit word into its fields and name the instruction:
   `0x00A5_8533`. (Hint: the low 7 bits are the opcode; `0110011` is R-type.)

    ??? success "Answer"
        Running the decoder confirms it is `add x10, x11, x10` — an R-type
        instruction (`opcode = 0110011`, `funct3 = 000`, `funct7 = 0000000`)
        with `rd = x10`, `rs1 = x11`, `rs2 = x10`.

        ```python
        def field(w, hi, lo):
            return (w >> lo) & ((1 << (hi - lo + 1)) - 1)

        w = 0x00A58533
        print("opcode:", format(field(w, 6, 0), "07b"))    # 0110011  -> R-type
        print("rd    : x%d" % field(w, 11, 7))              # x10
        print("funct3:", format(field(w, 14, 12), "03b"))   # 000
        print("rs1   : x%d" % field(w, 19, 15))             # x11
        print("rs2   : x%d" % field(w, 24, 20))             # x10
        print("funct7:", format(field(w, 31, 25), "07b"))   # 0000000 -> add
        print("=> add x%d, x%d, x%d" %
              (field(w, 11, 7), field(w, 19, 15), field(w, 24, 20)))
        ```

!!! info "Where to go deeper — Patterson & Hennessy, Chapter 2"

    Everything here — the operand model, all six instruction formats and their
    exact encodings, immediates and addressing modes, and the full procedure
    calling convention — is **Chapter 2 of Patterson & Hennessy's *Computer
    Organization and Design* (RISC-V edition)**, "Instructions: Language of the
    Computer." COD develops the encodings bit for bit, walks a C function down
    to RISC-V assembly, and lays out the ABI in full. From here, continue in
    this chapter to [23.5.3 arithmetic](03-arithmetic.md) (how `add` and friends
    are built), [23.5.4 the datapath](04-datapath.md) (the silicon that fetches
    and executes these words), and [23.5.5 pipelining](05-pipelining.md) (why
    real CPUs run several instructions at once), and see
    [23.5.6 parallelism](06-parallelism.md) and the chapter
    [overview](index.md) for the bigger picture.
