# Chapter 13 · Class Design and UML

In [Chapter 12](../ch12-classes/index.md) you built your first classes and
watched objects come to life. That was the mechanical part: `__init__`,
attributes, methods, `self`. This chapter is about the part that makes
someone a software *designer* rather than a typist of classes — deciding
what each class should protect, what it should reveal, and how a handful of
classes should share the work of a real program. Almost every interesting
program is a *team* of objects, and teams need rules.

The first rule is **encapsulation**: an object's data is its own business,
and the rest of the program should go through the front door. You will see
what happens when a bank account leaves its balance lying around in public
(nothing good), how Java bolts the door shut with `private`, and how Python
achieves the same goal with naming conventions and *properties* — a
difference in philosophy that is worth understanding honestly, not
memorising blindly.

The second rule is **think before you type**. Programmers sketch designs in
a compact visual language called **UML** (Unified Modeling Language), and
this handbook draws UML with mermaid — the same tool that renders the
diagrams on these pages — so you can draw your own designs in any Markdown
file, README, or notebook. The chapter closes by putting both rules to
work: starting from four plain-English requirement sentences, we design and
build a complete airline-reservation system, one class at a time.

**After this chapter you can …**

- explain what an *invariant* is and defend one with encapsulation;
- read Java's `public` / `private` / `protected` and map each to Python's
  convention system (`name`, `_name`, `__name`);
- turn a plain attribute into a guarded `@property` without changing a
  single line of calling code;
- read the three compartments of a UML class box, including `+` and `-`
  visibility markers;
- write mermaid `classDiagram` code yourself — classes, members, and all
  five relationship arrows;
- choose correctly between association, aggregation, composition,
  inheritance, and dependency;
- translate a UML diagram into skeleton Python, and working Python back
  into a diagram;
- take a paragraph of requirements, extract classes from its nouns and
  methods from its verbs, and grow a working multi-class system.

**Prerequisites:** [Chapter 12](../ch12-classes/index.md) (writing your own
classes) and [Chapter 9](../ch09-collections/index.md) (how objects and
references behave in memory). If `self` still feels mysterious, revisit
[12.1](../ch12-classes/01-class-anatomy.md) first.

**Sections**

- [13.1 Encapsulation and access control](01-encapsulation.md) — invariants
  under attack, Java's access modifiers, Python's underscores, and
  properties that guard attribute access.
- [13.2 UML class diagrams](02-uml.md) — the class box, mermaid
  `classDiagram` syntax from scratch, the five arrows, and round-trip
  translation between diagrams and code.
- [13.3 Multi-class systems](03-multi-class.md) — from requirements to
  nouns and verbs, to a diagram, to a working airline-reservation
  system, plus the design lessons that generalise.
- [Exercises](exercises.md) — leak hunts, property drills, diagrams from
  prose, and an airline waitlist.
