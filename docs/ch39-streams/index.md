# Chapter 39 · Functional Style, Streams, and Pipes

Almost every program you have written so far follows the same rhythm: make a
container, loop over some data, mutate the container, print it. That rhythm
works, and you should never feel bad about it. But there is a second rhythm,
and once you can hear it you will find it everywhere — in Java's Streams API,
in the `|` character that glues Unix commands together, in the query languages
of databases, and in the data pipelines that feed every machine-learning
system on earth. The idea is to stop describing *how to walk the data* and
start describing *what transformation you want*: take these records, keep the
interesting ones, reshape each one, combine them into an answer. The loop is
still there; you just stopped writing it by hand.

This chapter builds that style from the ground up. It starts with a fact you
have been using without noticing since [Chapter 3](../ch03-functions/index.md):
in Python a function is an ordinary value. It can live in a variable, ride
along as an argument, and be handed back as a return value. Once functions are
values you can write functions that *take* functions, which is all a
"higher-order function" ever was. From there the three classic operations —
`map`, `filter`, and `reduce` — fall out naturally, and we implement each one
by hand in a few lines before touching the built-in, so no step feels like
magic.

The last section is where the chapter earns its title. Generators, which you
met in [section 19.1](../ch19-stacks-queues/01-iterators.md), turn out to be
the perfect building block for **pipelines**: chains of small stages that each
pull one item from the stage before them. That is exactly what a Unix shell
does when you type `cat log | grep ERROR | sort | uniq -c`, and it is exactly
why such a command can process a file far larger than your memory. We will
build the same pipeline twice — once in the shell, once in Python — and you
will see that they are the same idea wearing different clothes.

## After this chapter you can …

- explain what it means that functions are first-class values, and store,
  pass, and return them deliberately;
- read and write `lambda` expressions, and say precisely what a lambda can and
  cannot contain;
- use `sorted(key=...)`, `min`/`max` with keys, and callbacks — the three
  places lambdas genuinely pay for themselves;
- write higher-order functions of your own (`apply_twice`, `compose`,
  factories) and explain how a **closure** captures a variable;
- recognise and fix the late-binding-in-a-loop bug that catches everyone once;
- implement and then use `map`, `filter`, and `functools.reduce`, and explain
  why comprehensions are the preferred Python spelling;
- explain **laziness**: why `map` and `filter` compute nothing until consumed,
  and predict the order in which a lazy pipeline evaluates;
- build a multi-stage generator pipeline that processes a large input in
  constant memory, and measure that it does;
- read a Unix pipeline stage by stage and explain streaming and backpressure;
- map every Java Stream operation onto its Python equivalent, and say when
  `parallelStream()` is actually worth it;
- state clearly when *not* to stream — random access, multiple passes, and
  whole-input sorting.

## Prerequisites

- [Chapter 3 · Functions](../ch03-functions/03-writing-functions.md) — you
  define and call functions; this chapter treats them as data.
- [Chapter 7](../ch07-arrays/index.md) and
  [Chapter 9](../ch09-collections/index.md) — lists, dicts, and the
  comprehension syntax, which turns out to be `map` and `filter` in disguise.
- [Chapter 11 · Files](../ch11-files/index.md) — reading a file line by line
  is the canonical pipeline source.
- [Section 19.1 · Iterators](../ch19-stacks-queues/01-iterators.md) — the
  `iter`/`next`/`StopIteration` protocol and a first look at generators.
  Section 39.3 assumes it.
- Helpful but optional: [Chapter 16](../ch16-complexity/index.md) for the
  memory arguments and [Chapter 23](../ch23-os/index.md) for the Unix-pipe
  section.

## Sections

1. [39.1 Lambdas and higher-order functions](01-lambdas.md) — functions as
   values, `lambda` and its deliberate limits, sorting by key, closures and
   the factory pattern, the late-binding trap and its fix,
   `functools.partial`, Java's functional interfaces and method references,
   and why pure functions are easier to test.
2. [39.2 Map, filter, reduce, and Java Streams](02-map-filter-reduce.md) —
   the three operations that cover most data work, each written by hand and
   then used properly; laziness demonstrated; comprehensions with a
   translation table; a four-stage pipeline over records; the everyday
   toolkit (`sum`, `any`, `all`, `sorted`, `enumerate`, `zip`); and the Java
   Streams API mapped operation by operation onto Python.
3. [39.3 Generators, pipelines, and Unix pipes](03-pipelines.md) — `yield` as
   the pipeline primitive, constant memory measured for real over 200 000
   items, a composable four-stage ETL pipeline, `itertools` highlights
   (`islice`, `chain`, `groupby`, `takewhile`), the Unix pipe explained stage
   by stage and then simulated runnably in Python, and when *not* to stream.
4. [Exercises](exercises.md) — rewrite loops as comprehensions and back,
   predict lazy-evaluation output, fix the closure bug, implement `my_reduce`,
   build a four-stage pipeline, translate a Java Stream chain, and write a
   grouped aggregation from scratch.
