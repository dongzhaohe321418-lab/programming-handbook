---
title: Home
---

# Programming & Computer Systems Handbook

**A zero-foundation, open handbook that takes you from "what is a bit?" to
building and analysing your own data structures — with Python code you can
run right on the page.**

Every Python block in this handbook has a **▶ Run** button. Click it and the
code executes in *your browser* (via [Pyodide](https://pyodide.org/), a
WebAssembly build of real CPython) — no installation, no account, no server.
Edit nothing, break nothing: just read, run, and understand.

[Start with Chapter 0](ch00-machine/index.md){ .md-button .md-button--primary }
[How to use this book](how-to-use.md){ .md-button }
[Open JupyterLab in your browser](try-in-jupyter.md){ .md-button }

---

## What's inside

| Part | Chapters | What you learn |
| --- | --- | --- |
| **I · The Machine** | 0–1 | How computers actually work: hardware, binary, what a program is, the command line, Git |
| **II · Programming I** | 2–14 | The full first-semester arc: variables, branching, loops, arrays, exceptions, files, and writing your own classes |
| **III · Programming II** | 15–22 | The second-semester arc: inheritance, Big-O analysis, recursion, linked lists, stacks, queues, trees, heaps, sorting |
| **IV · Systems & Practice** | 23–25 | The OS, memory layout, interpreters and VMs, real Git workflows, testing, and where to go next |

Plus four [projects](projects/01-number-tool/README.md) that tie everything
together, and an [appendix](appendix/A-python-java.md) with a Python ↔ Java
cheat sheet, a Big-O reference, and a glossary.

## Who this is for

- **Complete beginners** — Part I assumes nothing at all. Not "we'll go fast
  over the basics" — genuinely nothing.
- **Students in a Java-based Programming I / II course.** The chapter
  sequence deliberately mirrors the standard university sequence
  (Programming I → Programming II). Python is the teaching language because
  it runs in your browser, and wherever Java genuinely differs — types,
  compilation, `==` vs `equals()`, interfaces — you'll find side-by-side
  Python/Java tabs so nothing is lost in translation.
- **Self-learners** who want one coherent path instead of scattered
  tutorials.

## Course mapping

If you're following a university Programming I course (15 modules) or
Programming II course (5 units), here is where each topic lives:

| Programming I module | Chapter here |
| --- | --- |
| 0 · Orientation, tools | [Ch 0](ch00-machine/index.md), [Ch 1](ch01-tools/index.md) |
| 1 · The programming process | [Ch 0.3](ch00-machine/03-programs.md) |
| 2 · Data types and expressions | [Ch 2](ch02-data/index.md) |
| 3 · Objects and methods | [Ch 3](ch03-functions/index.md) |
| 4 · Branching | [Ch 4](ch04-branching/index.md) |
| 5 · Deeper mechanics | [Ch 5](ch05-under-the-hood/index.md) |
| 6 · Loops | [Ch 6](ch06-loops/index.md) |
| 7 · Arrays | [Ch 7](ch07-arrays/index.md) |
| 8 · 2-D arrays, sorting, unit tests | [Ch 8](ch08-grids/index.md) |
| 9 · ArrayList and objects | [Ch 9](ch09-collections/index.md) |
| 10 · Command line and exceptions | [Ch 10](ch10-exceptions/index.md) |
| 11 · File I/O | [Ch 11](ch11-files/index.md) |
| 12 · Writing classes | [Ch 12](ch12-classes/index.md) |
| 13 · More classes and UML | [Ch 13](ch13-design/index.md) |
| 14 · Extension topics | [Ch 14](ch14-beyond/index.md) |

| Programming II unit | Chapter here |
| --- | --- |
| 1 · Java review, exceptions | [Ch 10](ch10-exceptions/index.md), [Ch 15](ch15-inheritance/index.md) |
| 2 · Inheritance, interfaces, Big-O | [Ch 15](ch15-inheritance/index.md), [Ch 16](ch16-complexity/index.md) |
| 3 · Recursion, generics/ADTs, linked lists | [Ch 17](ch17-recursion/index.md), [Ch 18](ch18-linked-lists/index.md) |
| 4 · Iterators, stacks, queues | [Ch 19](ch19-stacks-queues/index.md) |
| 5 · BSTs, heaps, sorting and searching | [Ch 20](ch20-bst/index.md), [Ch 21](ch21-heaps/index.md), [Ch 22](ch22-sorting/index.md) |

## The three rules of this handbook

1. **Run everything.** Reading about code teaches you *about* code. Running
   it teaches you code. The Run button exists so you never have an excuse.
2. **Predict before you run.** Before clicking Run, say out loud what the
   code will print. Being wrong is the fastest way to learn.
3. **Do the exercises.** Every chapter ends with exercises and full
   solutions. Attempt first; peek second.

---

*Text licensed under CC BY 4.0, code under MIT.
Found a mistake? [Open an issue](https://github.com/dongzhaohe321418-lab/programming-handbook/issues).*
