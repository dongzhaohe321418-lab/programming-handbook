# Chapter 23.5 · Computer Architecture

You have already run a CPU in your browser. Back in
[0.4](../ch00-machine/04-machine-instructions.md) you decoded a real RISC-V
instruction by hand and watched a tiny fetch–decode–execute loop sum the
numbers 1 to 5. This chapter opens that box all the way. It is the beginner's
tour of the standard undergraduate architecture course —
**Patterson & Hennessy, *Computer Organization and Design* (RISC-V edition)**,
"COD" for short — rebuilt in the handbook's style: bullet-first, and with a
small runnable model for every idea so you never have to take the hardware on
faith.

Why should a programmer who writes Python care how a processor is built?

- **You will stop guessing about speed.** Once you know the CPU performance
  equation and Amdahl's law, "why is my code slow?" becomes a question you can
  *compute an answer to* instead of superstition about clock speed.
- **The tower finally connects.** Your source code → assembly → machine code →
  the datapath that runs it is one continuous ladder. Parts I–IV climbed the
  top rungs; this chapter walks the bottom ones.
- **The AI hardware makes sense.** Why GPUs suit deep learning, why models are
  quantized, why "8 cores" rarely means "8× faster" — all of it falls out of
  the ideas here, and Part V's inference chapters lean on them directly.

This chapter is deliberately a **hub**: nearly every section links back out to
where the idea already lives elsewhere in the book, so architecture stops being
an island and becomes the floor everything else stands on.

## The sections — and what you'll build in each

- **[23.5.1 What makes a computer fast](01-performance.md)** — the CPU
  performance equation and Amdahl's law. *You'll build* a two-design
  performance calculator and plot the diminishing-returns curve that explains
  why "make the common case fast" is the whole game.
- **[23.5.2 The instruction set up close](02-instruction-set.md)** — RISC-V
  instruction formats, registers, and addressing. *You'll build* an
  encoder/decoder that packs and unpacks real instructions bit by bit.
- **[23.5.3 Hardware arithmetic](03-arithmetic.md)** — how silicon adds,
  multiplies, and stores fractions. *You'll build* a shift-and-add multiplier
  and an IEEE-754 float inspector that shows where the rounding lives.
- **[23.5.4 The datapath](04-datapath.md)** — the circuit that executes one
  instruction. *You'll build* a single-cycle datapath that fetches, decodes,
  and executes, wiring together the pieces from 23.5.1–23.5.3.
- **[23.5.5 Pipelining](05-pipelining.md)** — overlapping instructions like an
  assembly line. *You'll build* a pipeline simulator that exposes hazards,
  stalls, and the speed-up (and the surprises) they bring.
- **[23.5.6 Parallelism and modern hardware](06-parallelism.md)** — SIMD,
  multicore, GPUs, and domain-specific chips. *You'll build* a scalar-vs-numpy
  timing race and a multicore speed-up curve that revisits Amdahl.

## How this connects to the rest of the book

- **[0.2 Bits and binary](../ch00-machine/02-binary.md)** — two's complement
  and "a bit pattern has no meaning until something interprets it." Hardware
  arithmetic (23.5.3) is that idea made physical.
- **[0.4 Machine instructions](../ch00-machine/04-machine-instructions.md)** —
  the ISA taste and the tiny CPU you already ran; 23.5.2 and 23.5.4 zoom in on
  exactly that machine.
- **[5.1 Numeric pitfalls](../ch05-under-the-hood/01-numeric-pitfalls.md)** —
  why `0.1 + 0.2 != 0.3`. 23.5.3 shows the IEEE-754 format that causes it.
- **[Chapter 16 · Complexity](../ch16-complexity/index.md)** — Big-O counts
  *operations*; this chapter counts *cycles*. They are the two halves of "how
  long will this take?"
- **[Chapter 23 · OS and memory](../ch23-os/index.md)**, especially the
  **[memory hierarchy](../ch23-os/04-memory-hierarchy.md)** — caches and
  virtual memory are the memory side of architecture; this chapter is the
  compute side, and 23.5.6 ends back at the memory wall.
- **Part V — [inference](../ch27-inference/index.md) and
  [neural networks](../ch25b-neural-networks/index.md)** — the GPUs and
  tensor engines that run modern models are the parallel hardware of 23.5.6.

## Prerequisites

- **[Chapter 0 · The machine](../ch00-machine/index.md)** is the real
  prerequisite — hardware, the fetch–decode–execute loop, binary, and the
  machine-instruction section. If you can read the tiny CPU in
  [0.4](../ch00-machine/04-machine-instructions.md), you are ready.
- **Helpful but optional:** [Chapter 16](../ch16-complexity/index.md) (Big-O,
  for the "counting work" mindset) and
  [Chapter 23](../ch23-os/index.md) (the OS and memory hierarchy).
- **No calculus, no electronics.** Every model here is plain arithmetic in
  Python and numpy on small numbers you can check by hand.

!!! info "Where this comes from — Patterson & Hennessy"

    This chapter follows the arc of **Patterson & Hennessy, *Computer
    Organization and Design* (RISC-V edition)** ("COD"), the standard
    undergraduate text: performance (Ch. 1), instructions (Ch. 2), arithmetic
    (Ch. 3), the processor and datapath (Ch. 4), the memory hierarchy (Ch. 5,
    covered in [23.4](../ch23-os/04-memory-hierarchy.md)), and parallelism
    (Ch. 6). We match its framing and facts and keep everything runnable; COD
    is the place to go for the full encodings, circuits, and proofs.

**After this chapter you can …**

- read the **CPU performance equation** and say why clock speed alone is a
  liar's metric;
- compute a weighted-average **CPI** from an instruction mix, and apply
  **Amdahl's law** to decide what is worth optimizing;
- encode and decode a **RISC-V instruction** into its bit fields, and explain
  what registers and addressing modes buy you;
- describe how hardware **adds, multiplies, and stores floating-point** numbers,
  and locate the rounding error from [5.1](../ch05-under-the-hood/01-numeric-pitfalls.md);
- trace a **single-cycle datapath** and explain what **pipelining** overlaps —
  and where hazards force it to stall;
- name the four kinds of **parallelism** (instruction-, data-, thread-, and
  request-level), explain why the industry turned to **multicore** and
  **GPUs**, and connect all of it to the AI hardware in Part V.
