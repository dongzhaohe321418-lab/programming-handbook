# Chapter 1 · Tools of the Trade

[Chapter 0](../ch00-machine/index.md) looked at the machine itself — hardware,
bits, and what a program really is. This chapter is about the workshop.
Programmers everywhere, whatever language or company or operating system,
share three daily tools: a **command line** for talking to the computer
directly, a **language toolchain** (for us: Python, and its cousin Java) for
turning text into running programs, and **version control** (Git) for keeping
every version of everything without drowning in copies named `final_v2_REAL`.

Strictly speaking you need none of this to read on: every Python example in
this handbook runs in your browser with the **Run** button. But the goal is
not to read about programming — it is to become someone who programs, and
real programs live on real machines.

The three tools here look plain, even old-fashioned: text in, text out, no
buttons. That plainness is the point. A text command can be:

- **typed faster** than a menu can be clicked;
- **repeated exactly**, with no chance of a mis-click;
- **saved in a script** and replayed a hundred times;
- **sent over a network** to a server on the other side of the world.

Every professional tool you will meet later — compilers, test runners,
package managers, deployment systems — assumes you can use them.

A practical note on how to read this chapter: sections
[1.1](01-command-line.md), [1.3](03-git.md), and [1.4](04-git-remotes.md)
teach concepts you can practice right here in the browser — the Git sections
even let you run a small model of Git's staging areas — while
[1.2](02-python-setup.md) is partly a setup guide for your own computer —
read it once now, then come back to it the day you install Python for real.

## After this chapter you can …

- Explain what a terminal and a shell are, and read a prompt like
  `kim@laptop:~/projects$` without blinking.
- Move around the file system with `pwd`, `ls`, and `cd`, and manage files
  with `mkdir`, `cp`, `mv`, and `rm` — including knowing why `rm` deserves
  respect.
- Predict how absolute paths, relative paths, `..`, and `~` resolve.
- Install Python on your own machine and run the same program four ways:
  the REPL, a script file, a notebook, and this site's Run buttons.
- Explain what a virtual environment is for and create one with
  `python -m venv`.
- Create a Git repository, and name — for any command — which of Git's areas
  (working directory, staging area, local repository, remote) it changes.
- Stage and commit changes, undo safely with `restore` and `reset`, and read
  `git log` and `git diff` output.
- Sync with a remote using `clone`, `push`, `fetch`, and `pull`, and explain
  how GitHub relates to Git and what a `README` and `.gitignore` are for.

## Prerequisites

Just [Chapter 0](../ch00-machine/index.md) — in particular
[0.3 What is a program](../ch00-machine/03-programs.md), because this chapter
keeps referring to the difference between *source code* and a *running
program*.

## Sections

1. [1.1 The command line](01-command-line.md) — the terminal, the shell,
   paths, and the dozen commands that cover 90% of daily use.
2. [1.2 Installing and running Python](02-python-setup.md) — getting Python
   onto your machine, the four ways to run code, virtual environments, and
   the Java parallel.
3. [1.3 Git and the staging model](03-git.md) — the working directory,
   staging area, and local repository; how `add`, `commit`, `restore`, and
   `reset` move work between them, with a runnable stage simulator.
4. [1.4 Working with remotes](04-git-remotes.md) — the fourth area: `clone`,
   `push`, the `fetch`-versus-`pull` distinction, and how GitHub fits in.
5. [Exercises](exercises.md) — path puzzles, command matching, and a mini
   version-control system you can build yourself.
