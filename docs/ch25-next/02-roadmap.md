# 25.2 Your roadmap

Finishing a book is a strange moment: you know more than you ever have, and
you can feel how much is left. This page turns that feeling into a plan.
It is organised by *goal*, not by topic — pick the goal that matches where
you are, start with its first step, and ignore the rest until you want it.
Nobody does all of this at once; everybody who keeps programming does some
of it every week.

## Goal: solidify what you know

Before reaching for new material, squeeze the material you have. The single
most effective exercise: **redo the four [projects](../projects/01-number-tool/README.md)
without looking at your old code**. If you can rebuild the number-systems
toolkit or the data-structures library from a blank file, you own it; every
place you get stuck is a precise map of what to re-read. Re-implementation
feels slower than new tutorials — it is faster, because it converts
"recognise" into "recall", and recall is the thing exams, interviews, and
real work actually demand.

A miniature version of the same test takes five minutes: pick any small
function you have written this year and rebuild it cold.

```python
# The "closed book" test: rebuild something small, from memory, right now.
def reverse(text):
    out = ""
    for ch in text:
        out = ch + out    # prepend each character as it arrives
    return out

print(reverse("handbook"))
assert reverse("racecar") == "racecar"
assert reverse("") == ""
print("all checks passed")
```

If writing that took thought, good — that thought was the workout. (The
`assert` lines are a habit worth stealing from
[Chapter 24.2](../ch24-practice/02-testing.md): every rebuilt function
deserves two or three instant checks.)

## Goal: practise deliberately

Practice sites give you an endless supply of small, self-contained problems
with instant feedback:

- **LeetCode** and **HackerRank** — start firmly in the *easy* tier, and
  stay there longer than your pride wants. Easy problems are where loops,
  dictionaries, and two-pointer patterns become reflexes.
- **Advent of Code** — a December calendar of story-driven puzzles (all
  past years stay playable). Less interview-flavoured, more fun, and
  wonderful for file parsing and honest problem decomposition.

*How* you practise matters more than where. The loop that works:

1. **Predict.** Read the problem, write your plan in one sentence *before*
   coding. When reading anyone's code, say what it prints before running it.
2. **Write.** Your own attempt, however clumsy, for at least 20–30 minutes
   before peeking at anything.
3. **Compare.** Read two or three other solutions afterwards and name the
   difference out loud: "they used a set for membership, I scanned a list —
   that is the $O(1)$ vs $O(n)$ trade from
   [Chapter 16](../ch16-complexity/01-big-o.md)."

What does *not* work is memorising solutions. A memorised answer decays in
a week; a compared one leaves a pattern behind.

```python
# Step 1 is PREDICT: what does this print? Decide before you run it.
nums = [3, 1, 4, 1, 5, 9, 2, 6]
seen = set()
for x in nums:
    if x in seen:
        print("first repeated value:", x)
        break
    seen.add(x)
```

If you predicted `first repeated value: 1` — and, better, said "the set
makes each membership test $O(1)$" — the habit is already forming.

## Goal: build things

Problems teach syntax; projects teach *programming* — the ambiguity, the
plumbing, the joy of something that works because you made it.

**Start with a command-line tool.** You already know everything required:
[arguments](../ch10-exceptions/01-cli-programs.md),
[files](../ch11-files/02-read-write.md), and
[exceptions](../ch10-exceptions/02-exceptions.md). First step: pick one
tiny chore from your real life — count words in notes, rename photos by
date, tally hours from a log — and write the twenty-line version tonight.
Real users (you) and real data beat any tutorial.

```python
# A whole useful CLI tool. (In a real terminal, argv comes from sys.argv.)
argv = ["wordcount", "the quick brown fox"]   # simulates: wordcount "the quick brown fox"

text = argv[1]
print(f"{len(text.split())} words, {len(text)} characters")
```

**Then a small web app.** A to-do list or flash-card site built with a
micro-framework (Flask is the classic) teaches you requests, responses,
and templates — the shape of most modern software. First step: follow the
official Flask quickstart until "hello world" appears in your browser, then
change *one thing* and reload. That edit–reload loop is the whole game.

**Then contribute to open source.** Not to be noble — because reading a
real codebase, running its tests, and getting a review from a stranger is
the closest thing to a free apprenticeship that exists. First step: find a
library you already use, read its issue tracker for labels like
`good first issue`, and start with documentation or a failing-test fix.
Your [Git workflow from Chapter 24](../ch24-practice/01-git-workflow.md) —
branch, commit, pull request — is exactly what maintainers expect.

## Goal: read great code

Writers read; programmers should too. The Python standard library is
literature that ships with the interpreter — written by experts, argued
over for decades, and sitting on your disk right now.

Two recommended first reads: **`pathlib`**, to see how a clean
object-oriented API is layered over messy operating-system reality, and
**`heapq`**, famous for comments so good they amount to a free textbook
chapter. You do not even need to find the file — the essay is importable:

```python
import heapq

essay = heapq.__about__          # yes, the module ships with an essay
print(essay[:420], "...")
print("...", len(essay.splitlines()), "more-or-less glorious lines in total")
```

Read whichever module you just used — every module page on
docs.python.org links its source at the top ("Source code: Lib/…"), and the
same files live on GitHub under `cpython/Lib/`. Ask of every
surprising line: *why this way and not the obvious way?* The answer is
usually a bug you have not met yet.

## Books and courses

A short list — each entry earns its place, and the full annotated versions
live in [Appendix D](../appendix/D-reading.md), so details are not repeated
here:

- **Think Python** — the gentlest serious second pass over Part II.
- **Sedgewick & Wayne, *Algorithms*** — the natural full meal after the
  Part III appetizers.
- **CS:APP (Bryant & O'Hallaron)** — for the brave: Chapter 23's machinery
  at professional depth.
- **CS50** — a free, superbly produced course if you want lectures and a
  community around the same ideas.
- **The Pragmatic Programmer** — habits and judgement; best read once some
  code of yours has already gone wrong in production-ish conditions.

## Keep this handbook on your desk

You are done reading this book front to back; you are not done *using* it.
The [Python ↔ Java cheat sheet](../appendix/A-python-java.md) earns a
browser bookmark for as long as you run both languages side by side, the
[Big-O reference](../appendix/B-big-o.md) answers "wait, what does `pop(0)`
cost?" faster than a search engine, and the
[glossary](../appendix/C-glossary.md) is there for the day "invariant"
stops feeling obvious. Reference use is not cheating; it is what references
are for.

## The only three habits that matter

Strip away every list above and three habits remain. They are boring, and
they are the entire difference between people who learned to program once
and people who can program.

1. **Code daily.** Twenty minutes counts. Contact beats intensity: the
   person who writes a little every day laps the person who binges monthly.
2. **Read errors slowly.** A [stack trace](../ch10-exceptions/03-stack-traces.md)
   is not an insult, it is a letter: read it bottom line first, top frame
   next, and resist touching the code until you can say what it claims.
3. **Ask why, not just what.** "It works now" is a fact; "it works because
   the reference was shared and I copied it" is knowledge. Only the second
   survives contact with the next bug.

!!! warning "Common mistakes"

    - **Tutorial hell.** Watching a fourth course on loops feels like
      progress and is not. The moment content feels familiar, close it and
      build something without it.
    - **Memorising practice-site solutions.** You are training recall of
      *patterns*, not answers. If you cannot explain why a solution works,
      the problem is not done.
    - **Starting a project too big to finish.** "A game" dies; "a
      twenty-line word counter I use on my own notes" ships, and shipping
      is the habit being trained.
    - **Skipping fundamentals to chase frameworks.** Frameworks change
      yearly; the reasons this book gave you — references, complexity,
      invariants — transfer to every one of them.

## Check your understanding

1. Why does redoing an old project without looking beat starting a new
    tutorial, if the goal is retention?

    ??? success "Answer"
        Rebuilding forces *recall* (producing the knowledge from nothing),
        while tutorials mostly exercise *recognition* (nodding along to
        someone else's production). Recall is the skill you actually need
        when facing a blank editor, and each point where you get stuck
        tells you precisely what to review.

2. What are the three steps of the practice loop recommended here, and
    which one do most people skip?

    ??? success "Answer"
        Predict, write, compare. Most people skip *compare* — reading
        other solutions after solving and naming the difference — which is
        where new patterns actually enter your toolbox. (A close second:
        skipping *predict* and running code to find out what it does.)

3. Your first open-source contribution probably should not be a new
    feature. What should it be, and why?

    ??? success "Answer"
        A documentation fix, a `good first issue`, or a test for a known
        bug. These teach the project's workflow — cloning, branching,
        tests, review — with low stakes, and maintainers merge them
        readily, which gets you the full pull-request experience quickly.
