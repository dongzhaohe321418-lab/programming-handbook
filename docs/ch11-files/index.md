# Chapter 11 · Files

Every program you have written so far has had a peculiar kind of amnesia: the
moment it finishes, every variable it built vanishes. Run it again and it
starts from nothing. Real software remembers — your browser keeps bookmarks,
a game keeps save files, a lab instrument logs a reading every minute. The
mechanism behind all of it is the same: **files**, data that lives on disk and
survives after the program ends. This chapter teaches you to create, read, and
process files from Python.

We start with the *file system* itself: how files and directories form a tree,
what a path is, and how Python's `pathlib` module lets you name any location
on any operating system without worrying about slashes and backslashes. Then
we open files for real: writing text into them, reading it back whole or line
by line, appending to logs, and processing a small comma-separated data file
into a report — the pattern behind an enormous amount of practical
programming. Along the way you will meet the `with` statement, Python's
guarantee that a file gets closed no matter what, which mirrors the
try-with-resources idiom from your Java course.

Everything here runs directly in your browser. The Run buttons use a private,
in-memory file system, so you can create and delete files freely — nothing
touches your actual computer, and it all resets when you reload the page. It
is the safest possible place to practice.

**After this chapter you can …**

- explain how files and directories form a tree, and read both absolute and
  relative paths;
- build and inspect paths with `pathlib.Path` instead of gluing strings;
- write, read, and append text files using `open` and the `with` statement;
- iterate over a file line by line and clean up the trailing newlines;
- process a simple CSV file with `split(",")` and compute results from it;
- anticipate and handle `FileNotFoundError`.

**Prerequisites.** You should be comfortable with loops
([Chapter 6](../ch06-loops/index.md)), string methods such as `split` and
`strip` ([Chapter 3](../ch03-functions/02-strings.md)), and the basics of
exceptions ([Chapter 10](../ch10-exceptions/02-exceptions.md)) — files are
where exceptions stop being theoretical.

**Sections**

1. [11.1 Paths and the file system](01-paths.md) — the directory tree,
   absolute vs relative paths, and `pathlib`.
2. [11.2 Reading and writing files](02-read-write.md) — `open`, `with`,
   modes, line-by-line reading, and a worked CSV example.
3. [Exercises](exercises.md) — word counters, line numberers, log filters,
   and CSV crunching.
