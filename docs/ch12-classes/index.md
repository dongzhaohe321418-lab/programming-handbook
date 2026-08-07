# Chapter 12 · Writing Your Own Classes

You have been *using* objects since almost your first line of Python: every
string that answered `.upper()`, every list that obeyed `.append()`, every
file object from the last chapter was an instance of a class that somebody
designed. This chapter is the moment you cross the counter — from customer to
chef. You will write the class yourself: decide what data an object carries,
what it can do, and how it introduces itself when printed.

The mechanics are honestly small — a `class` statement, an `__init__` method,
and the ever-present `self` — but the shift in thinking is big. A class lets
you invent a *new kind of value* that matches your problem: a `Dog` that
knows its own name, a `WeatherStation` that can summarize its own readings, a
`DogHouse` that enforces its own capacity rule. Once data and the operations
on that data travel together, programs stop being loose piles of variables
and start being collections of little machines, each responsible for itself.
This is the heart of object-oriented programming, and it is the foundation
everything in [Chapter 13](../ch13-design/index.md) and
[Chapter 15](../ch15-inheritance/index.md) builds on.

We take it gently: first the anatomy of a class, one piece at a time, with
the Java equivalents beside each piece so the two courses reinforce each
other; then two complete worked examples grown stage by stage, ending with
the design questions — *how do you decide what should be a class at all?*

**After this chapter you can …**

- explain the difference between a class (the blueprint) and an instance
  (one object built from it);
- write a class with `__init__`, instance attributes, and methods, and
  explain what `self` refers to;
- create several instances and show that each keeps its own separate state;
- add a `__repr__` so your objects print something informative;
- distinguish class attributes (shared) from instance attributes (per-object);
- grow a small class stage by stage, and combine classes with composition
  (a `DogHouse` *has* `Dog`s).

**Prerequisites.** You should be comfortable calling methods on objects
([Chapter 3](../ch03-functions/01-using-objects.md)), writing your own
functions ([Chapter 3](../ch03-functions/03-writing-functions.md)), and
picturing objects living on the heap with variables as references to them
([Chapter 9](../ch09-collections/03-objects-in-memory.md)).

**Sections**

1. [12.1 Anatomy of a class](01-class-anatomy.md) — `class`, `__init__`,
   `self`, attributes, methods, `__repr__`, and class vs instance
   attributes.
2. [12.2 Worked examples — Dog, WeatherStation](02-worked-examples.md) —
   two complete classes grown in stages, composition, and how designers
   choose their classes.
3. [Exercises](exercises.md) — bank accounts, rectangles, playlists, and a
   prediction puzzle.
