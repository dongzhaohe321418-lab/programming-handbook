# Chapter 14 · Beyond the Basics

This chapter closes Part II, and it does so by widening the lens. So far
your programs have stored nearly everything in lists — a fine default,
but only one tool from a larger kit. Here you meet the rest of the
everyday collections: **sets** that refuse duplicates and answer "have I
seen this?" almost instantly, **dictionaries** that map keys to values
and quietly power most real Python programs, and **tuples**, the little
immutable records that hold structured data together. Choosing the right
one is a design decision, and you will leave with a decision table for
making it.

The second theme is a question you could not even ask a few chapters
ago: when *two* correct programs solve the same problem, which is
better? You will race a list against a set, count the steps of linear
versus binary search, and learn the professional habit that settles such
arguments — *measure, don't guess*. That experiment is the doorway to
[Part III](../ch16-complexity/index.md), where the measuring becomes a
theory.

Finally, the chapter looks outward. Every program you have written so
far talks through `print`; real applications talk through windows,
buttons, and events. You will see how graphical programs are structured
around an **event loop**, why that flips the flow of control upside
down, and what other directions — the web, games, data science, audio —
are now within your reach with the foundations you have built.

**After this chapter you can …**

- use a `set` for uniqueness and fast membership, and combine sets with
  union, intersection, and difference;
- use a `dict` to map keys to values: store, look up with a default,
  and iterate over its items;
- explain what makes an object a valid dictionary key, and use tuples
  as compound keys;
- pick the right collection for a job using three questions (ordered?
  duplicates? lookup by key?);
- reach for `Counter` and `defaultdict` when they save real work;
- time two solutions with `time.perf_counter` and interpret the ratio;
- predict how running time grows when the input doubles, and tell
  linear growth from quadratic growth by experiment;
- describe the event-loop model of a GUI program and explain what a
  callback is.

**Prerequisites:** [Chapter 7](../ch07-arrays/index.md) (lists and
traversal), [Chapter 9](../ch09-collections/index.md) (references), and
the sort-and-search ideas from
[Chapter 8](../ch08-grids/03-first-algorithms.md).

**Sections**

- [14.1 Sets, maps, and dictionaries](01-collections-tour.md) — the
  collections beyond lists, Java's `HashSet`/`HashMap` counterparts, and
  how to choose.
- [14.2 Comparing algorithms](02-choosing-algorithms.md) — the same
  problem solved twice, timed honestly; step counting; growth by
  doubling.
- [14.3 GUIs and other directions](03-guis-and-beyond.md) — the event
  loop, callbacks, a taste of text processing, and the map of where to
  go next.
- [Exercises](exercises.md) — phone books, set puzzles, a refactor that
  earns a speedup, and a top-five word counter.
