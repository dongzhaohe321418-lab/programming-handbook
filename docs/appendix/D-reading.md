# D · Further reading

A short shelf, not a library. Every entry here earned its place by being
genuinely worth your hours, and each comes with an honest one-line *why* —
including, where deserved, an honest warning. Quality over completeness: if
something famous is missing, it is missing on purpose. Start with whatever
matches your next goal from [the roadmap](../ch25-next/02-roadmap.md).

## Books

- **Think Python** (Allen Downey, free online) — the gentlest serious
  second pass over Parts I–II; short chapters, good exercises, zero fluff.
- **Automate the Boring Stuff with Python** (Al Sweigart, free online) —
  the fastest route from "I know loops" to "I wrote a script my family
  actually uses"; motivation in book form.
- **Code** (Charles Petzold) — [Chapter 0](../ch00-machine/index.md)
  expanded into a whole beautiful book: from flashlight signals and relays
  all the way up to a working computer, no prior knowledge assumed.
- **Grokking Algorithms** (Aditya Bhargava) — Part III retold in cartoons
  and friendly diagrams; the ideal bridge if Sedgewick feels like a wall.
- **Algorithms, 4th edition** (Sedgewick & Wayne) — the natural full
  course after this book, *in Java*, so it doubles as course-parallel
  reading; superb website with visualizations and code.
- **Computer Systems: A Programmer's Perspective** (Bryant & O'Hallaron)
  — for the brave: everything [Chapter 23](../ch23-os/index.md) waved at —
  memory, caches, linking, processes — at professional depth. Slow going
  and worth it, but not as a first systems exposure.
- **The Pragmatic Programmer** (Hunt & Thomas, 20th-anniversary edition)
  — judgement, habits, and taste; lands best once at least one project of
  yours has already turned into a mess you had to live with.
- **Clean Code** (Robert C. Martin) — *with caveats*: the chapters on
  naming and small functions are valuable, but treat it as one strong
  opinion, not law; read it critically, and skip anything that starts
  feeling like ritual.
- **Fluent Python** (Luciano Ramalho) — for later, when Python feels
  easy: the definitive tour of what the language is really doing under
  your code. Rewards a year of experience; punishes impatience.

## Free online

- **The official Python tutorial** ([docs.python.org/3/tutorial](https://docs.python.org/3/tutorial/))
  — terse where this book is chatty, which makes it the perfect
  second telling of the same story.
- **CS50x** ([cs50.harvard.edu/x](https://cs50.harvard.edu/x/)) —
  Harvard's famously well-produced intro course; starts in C, which will
  make everything [Chapter 5](../ch05-under-the-hood/index.md) said about
  memory suddenly feel very concrete.
- **Python Tutor** ([pythontutor.com](https://pythontutor.com)) — paste
  code, press forward, and *watch* the frames, references, and objects
  draw themselves. The perfect companion to the memory diagrams of
  [Chapter 5.3](../ch05-under-the-hood/03-stack-heap.md) and
  [Chapter 9.1](../ch09-collections/01-references.md) — if you internalise
  one external tool from this page, make it this one.
- **VisuAlgo** ([visualgo.net](https://visualgo.net)) — animated data
  structures: watch a BST rebalance and a heap sift in real time. Best
  used *alongside* [Chapters 20–22](../ch20-bst/index.md), one animation
  per topic.
- **Real Python** ([realpython.com](https://realpython.com)) — deep,
  well-edited tutorials on almost any Python topic; quality varies less
  than most tutorial sites, and the free tier covers plenty.
- **Exercism** ([exercism.org](https://exercism.org)) — small practice
  problems with *human mentor feedback*, free; a different (and gentler)
  muscle than the interview-prep sites in
  [the roadmap](../ch25-next/02-roadmap.md).

## Java-specific, for course-parallel readers

- **Dev.java and the Oracle Java tutorials** ([dev.java](https://dev.java))
  — the official learning path; dry but correct, and the natural place to
  double-check anything in [Appendix A](A-python-java.md).
- **Head First Java** (Sierra, Bates & Gee) — a full first Java course in
  deliberately silly clothing; the humour is a delivery mechanism for
  genuinely careful pedagogy.
- **Effective Java** (Joshua Bloch) — *later*: 90 short essays on writing
  Java well, best appreciated after a semester or two of writing Java
  badly. The single most respected book in the Java world.

## Reading documentation — the skill itself

Documentation is a genre, and like any genre it gets easy once you know
its conventions. Three habits turn the reference manuals from walls of
text into your fastest resource:

1. **Know which book you're in.** Python's docs are really three
   documents: the *tutorial* (teaches), the *library reference* (looks up
   what `str.split` does), and the *language reference* (defines what the
   words mean — rarely needed at first). Most frustration comes from
   reading one while expecting another. Java's *Javadoc* API pages are a
   pure library reference: one page per class, every method listed.
2. **Read signatures the way this book taught.** `list.insert(i, x)` plus
   one sentence tells you the parameter order, and phrases like "raises
   `ValueError`" tell you the failure mode —
   [Chapter 10.2](../ch10-exceptions/02-exceptions.md) taught you to treat
   those as part of the contract.
3. **Let the interpreter be documentation too.** `help(str.split)` and
   `dir(some_object)` answer half of all "what was that method called?"
   questions faster than any search engine.

The habit to build: when a method surprises you, look it up *even though
the code now works*. Two minutes of reference reading converts "it works"
into "I know why" — which, as [the roadmap](../ch25-next/02-roadmap.md)
argued, is the whole game.
