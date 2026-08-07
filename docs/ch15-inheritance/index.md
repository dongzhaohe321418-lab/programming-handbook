# Chapter 15 · Inheritance and Interfaces

Part II ended with you designing multi-class systems — and, if you worked
through the Shapes example in [Chapter 13](../ch13-design/03-multi-class.md),
with a nagging feeling that something was wrong: three classes that were
90% identical, and no clean way to treat "a circle, a rectangle, and a
triangle" as three examples of the same thing. This chapter resolves that
tension with the last two pillars of object-oriented programming:
**inheritance** (a class can be built *on top of* another class, receiving
all of its behaviour for free) and **polymorphism** (code written against a
general type automatically does the right thing for each specific type).

These two ideas are the heart of a typical Programming II course, and they
are where Python and Java diverge most visibly. Java enforces the rules with
its type system — `extends`, `implements`, casts, `instanceof` — while
Python gets the same effects with lighter machinery and one extra idea of
its own, *duck typing*. We show both throughout, because seeing the same
design in two languages is the fastest way to separate the *concept* from
the *syntax*. The chapter closes with contracts: Java's interfaces and
Python's abstract base classes, which let you promise *what* a class will do
without saying *how*.

After this chapter you can:

- move duplicated behaviour into a base class and inherit it with
  `class Child(Parent)`,
- override a method, and *extend* rather than replace it using `super()`,
- chain constructors correctly with `super().__init__(...)`,
- write one loop that processes many different types of object
  (polymorphism), and explain how Python decides which method runs,
- use the *is-a* test to decide between inheritance and composition,
- define a contract with `abc.ABC` and `@abstractmethod`, and say honestly
  when duck typing is the better tool.

**Prerequisites:** writing classes
([Chapter 12](../ch12-classes/index.md)) and designing groups of classes
([Chapter 13](../ch13-design/index.md)). The collection types from
[Chapter 14](../ch14-beyond/index.md) appear in examples.

**Sections**

1. [15.1 Inheritance](01-inheritance.md) — base classes, overriding,
   `super()`, and when *not* to inherit.
2. [15.2 Polymorphism and casting](02-polymorphism.md) — one loop, many
   shapes; dynamic dispatch; Java's casts vs Python's ducks.
3. [15.3 Interfaces and abstract classes](03-interfaces.md) — contracts
   without implementation; a plug-in payment system.
4. [Exercises](exercises.md)
