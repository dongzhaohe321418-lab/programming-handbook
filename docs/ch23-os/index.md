# Chapter 23 · Memory, Processes, and the OS

You have spent twenty-two chapters learning to *write* programs. This chapter
answers the question that has been quietly waiting the whole time: what
actually *runs* them? When you press ▶ Run, your code does not touch the
processor directly. It is handed to an interpreter, which is itself a program,
which is managed by an operating system, which shares one physical machine
among dozens of programs at once, each living inside its own carefully fenced
patch of memory. Most programming courses never open this box. We are going
to open it.

The payoff is practical, not just philosophical. Once you know what a
*process* is, error messages about permissions and crashed programs make
sense. Once you have seen the memory layout of a running program — stack,
heap, and the segments in between — the stack traces from
[Chapter 10](../ch10-exceptions/03-stack-traces.md) and the recursion limits
from [Chapter 17](../ch17-recursion/01-call-stack.md) stop being folklore and
become geometry. And once you follow your Python source through the
interpreter's pipeline — text to syntax tree to bytecode to execution — you
will finally see, end to end, the tower of machinery between the characters
you type and the electrons that move. The last section closes a loop this
handbook opened on page one: the Run buttons on this very site work because a
Python interpreter has been compiled to run inside your browser — a virtual
machine running inside a virtual machine.

**After this chapter you can …**

- explain what an operating system does: sharing the CPU, protecting memory,
  and abstracting hardware behind processes, files, and system calls;
- define a process and describe how one core runs many programs by
  time-slicing;
- state the difference between processes and threads, and describe what a
  race condition is and why shared memory makes it possible;
- draw the memory layout of a running program — code, static data, heap,
  stack — and say which way each part grows;
- explain how CPython manages memory: reference counting, the cycle
  collector, and why "garbage-collected" does not mean "leak-proof";
- trace the CPython pipeline from source code to bytecode to execution, and
  read simple `dis` output;
- place C, Java, and Python correctly on the compiled-versus-interpreted
  spectrum, and explain what a virtual machine is;
- describe the full stack of software that runs the code on this page, from
  your Python down to the hardware.

**Prerequisites:** [Chapter 0](../ch00-machine/index.md) (hardware and the
fetch–decode–execute cycle), [Chapter 5](../ch05-under-the-hood/03-stack-heap.md)
(first look at the stack and heap), [Chapter 10](../ch10-exceptions/index.md)
(exceptions and stack traces), and [Chapter 17](../ch17-recursion/01-call-stack.md)
(the call stack in action). [Chapter 16](../ch16-complexity/index.md) helps
for one aside about amortized cost.

**Sections**

- [23.1 What an operating system does](01-os-processes.md) — the OS as
  landlord and illusionist: processes, time-slicing, threads, race
  conditions, and system calls.
- [23.2 The memory layout of a program](02-memory-layout.md) — the address
  space: code, static data, heap, and stack; measuring object sizes; how
  Python's garbage collector really works.
- [23.3 Interpreters and virtual machines](03-interpreters-vms.md) — from
  source to bytecode to execution in CPython and on the JVM; the
  compiled/interpreted spectrum; and the virtual-machine tower under this
  very page.
- [Exercises](exercises.md) — match responsibilities to the right layer,
  read bytecode, predict memory growth, and explain the tower.
