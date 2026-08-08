# Chapter 9 · Collections and Memory

You have been using lists since Chapter 7, and they have quietly been hiding
the single most important idea in this half of the book: **a variable does not
contain a value — it refers to one.** As long as your programs used only
numbers and short strings, the difference was invisible. The moment two
variables point at the *same* list, it becomes the difference between a
program that works and a bug that takes you an afternoon to find.

This chapter drags that idea into the light, names it (the *reference model*),
and gives you the tools to reason about it: aliasing, `==` versus `is`,
shallow versus deep copies, and what actually happens when you pass a list to
a function.

The chapter also completes your collection toolkit. Java courses introduce
`ArrayList` at this point — a list that grows and shrinks on demand, unlike
the fixed-length arrays of Chapter 7. Python's `list` has been dynamic all
along, so here we make the correspondence exact: every `ArrayList` method
mapped, one by one, to its Python equivalent, and put to work in a small
to-do-list manager.

Finally, we look at *objects in memory*. Once you can picture stack frames
holding names and the heap holding objects, a "list of objects" stops being
mysterious: it is a list of references, and mutating through any one of them
changes the single shared object. That picture sets up the two views of
object-oriented programming — the *user's* view (what an object can do) and
the *author's* view (how it does it) — which is exactly the doorway into
[Chapter 12](../ch12-classes/index.md), where you start writing classes of
your own.

**After this chapter you can …**

- explain what a variable really stores in Python, and predict when two
  names refer to one object;
- use `==` and `is` correctly, and say in one sentence how they differ;
- make a genuine copy of a list — and know when a shallow copy is not
  enough and `copy.deepcopy` is required;
- state how Java's primitive types differ from its reference types, and why
  Python's immutable numbers *behave* like primitives even though they are
  objects;
- translate fluently between Java's `ArrayList` API and Python's `list`
  methods, in both directions;
- reason about the cost of inserting into the middle of a list;
- draw the stack-and-heap picture for a running program with several
  frames sharing objects;
- describe the external view and the internal view of an object, and say
  which one you have been using since Chapter 3.

**Prerequisites:** [Chapter 7](../ch07-arrays/index.md) (lists and
traversal), [Chapter 8](../ch08-grids/index.md) (passing arrays to
functions), and the stack-and-heap picture from
[Section 5.3](../ch05-under-the-hood/03-stack-heap.md).

**Sections**

- [9.1 Values vs references](01-references.md) — the reference model:
  aliasing, `==` vs `is`, shallow and deep copies, and why an `int` feels
  like a value even though it is an object.
- [9.2 Dynamic lists — ArrayList and list](02-dynamic-lists.md) — growable
  collections: the full `ArrayList` ↔ `list` method map, the cost of
  inserting in the middle, and a to-do-list manager.
- [9.3 Objects in memory — two views of OOP](03-objects-in-memory.md) —
  stack frames, heap objects, lists of references, and the user's view
  versus the author's view of an object.
- [Exercises](exercises.md) — aliasing predictions, copy puzzles,
  translation drills, and to-do manager extensions.
