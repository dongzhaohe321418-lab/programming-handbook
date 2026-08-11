# Chapter 0 · How Computers Work

Before you write a single line of code, it pays to know what you are actually
talking *to*. A computer is not a magic box that understands English, and it
is not intelligent. It is an astonishingly fast, astonishingly literal machine
that does exactly one small thing at a time — billions of times per second.

Every program you will ever write, from a two-line script to a game engine,
is ultimately a long list of tiny instructions fed to that machine. This
chapter shows you the machine.

We start with the physical parts — the processor, memory, and storage — and
the simple loop the processor repeats forever: fetch an instruction, decode
it, execute it. Then we go one level deeper and meet the *only* alphabet the
machine knows: bits, the 0s and 1s that encode every number, every letter,
and every photo on your phone. Finally we connect the two worlds and answer
the question this whole handbook is built on: what *is* a program, and what
happens between the text you type and the electrons that move?

Nothing in this chapter requires any programming experience. Every code
example runs in your browser with the **▶ Run** button, and you are warmly
encouraged to press it, change something, and press it again — that habit
will serve you for the rest of the book.

## After this chapter you can …

- name the main hardware components (CPU, RAM, storage, input/output) and
  explain what each one does;
- describe the fetch–decode–execute cycle and the von Neumann idea that
  *programs are stored in memory just like data*;
- explain why RAM is fast but forgetful, and storage slow but permanent;
- count in binary, convert between decimal, binary, and hexadecimal — by
  hand and with Python;
- represent negative numbers with two's complement and text with
  Unicode code points;
- explain the difference between a compiler and an interpreter, and what
  Python actually does with your source code;
- trace a short program by hand, line by line, and predict its output;
- explain what an **instruction set** is, read a line of **assembly**, and
  decode a single machine instruction into its opcode and register fields;
- run a tiny CPU that fetches, decodes, and executes machine instructions in
  a loop — and watch it build a `while` loop out of a branch.

## Prerequisites

None. This is the very first chapter. If you have not yet read
[How to use this book](../how-to-use.md), it takes two minutes and explains
the Run buttons.

## Sections

- [0.1 What is a computer, really](01-hardware.md) — the hardware tour:
  CPU, memory, storage, and the speed hierarchy that shapes all of computing.
- [0.2 Bits, binary, and how data is stored](02-binary.md) — base 2,
  base 16, negative numbers, and text as numbers.
- [0.3 What is a program — compilers and interpreters](03-programs.md) —
  from source code to machine code, and how to trace code by hand.
- [0.4 From code to machine instructions](04-machine-instructions.md) — the
  instruction set, assembly versus machine code, decoding one instruction into
  its fields, and a tiny CPU you can run.
- [Exercises](exercises.md) — conversions, predictions, decoding an
  instruction, and a race against the interpreter.
