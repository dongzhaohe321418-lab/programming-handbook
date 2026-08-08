---
title: Try in Jupyter (in browser)
---

# Try the handbook in JupyterLab

The ▶ Run buttons on every page are the fastest way to execute one example
— but sometimes you want a real workspace: notebooks you can edit, cells
you can rearrange, experiments that outlive a single click. For that, a
full **JupyterLab runs directly in your browser** via Pyodide (the same
WebAssembly Python that powers the Run buttons). No installation, no
account, no server — the "kernel" is your own browser tab.

[Launch JupyterLab](/programming-handbook/lite/lab/index.html){ .md-button .md-button--primary }
[Open the file browser](/programming-handbook/lite/index.html){ .md-button }

The first launch downloads the runtime (roughly the same ~40 MB as the Run
button, cached afterwards), so give it a moment.

## What is preloaded

- **Python 3.11+** (Pyodide)
- **NumPy** and **Matplotlib**
- Eleven companion notebooks that follow the book, ready to open:

| Part | Notebook | What it covers |
| --- | --- | --- |
| I | [part1-the-machine.ipynb](/programming-handbook/lite/lab/index.html?path=part1-the-machine.ipynb) | Chapter 0 · bits, binary, and floating point |
| II | [part2-python-basics.ipynb](/programming-handbook/lite/lab/index.html?path=part2-python-basics.ipynb) | Chapters 2–6 · variables to loops |
| II | [part2-collections-and-oop.ipynb](/programming-handbook/lite/lab/index.html?path=part2-collections-and-oop.ipynb) | Chapters 7–14 · lists, dicts, and classes |
| III | [part3-algorithms.ipynb](/programming-handbook/lite/lab/index.html?path=part3-algorithms.ipynb) | Chapters 16–17 and 22 · Big-O, recursion, sorting |
| III | [part3-data-structures.ipynb](/programming-handbook/lite/lab/index.html?path=part3-data-structures.ipynb) | Chapters 18–21 · linked lists to heaps |
| IV | [part4-systems.ipynb](/programming-handbook/lite/lab/index.html?path=part4-systems.ipynb) | Chapter 23 · bytecode, memory, references |
| V | [part5-llm-internals.ipynb](/programming-handbook/lite/lab/index.html?path=part5-llm-internals.ipynb) | Chapters 26–27 · a BPE trainer, attention built step by step, causal masking, sampling knobs, KV-cache arithmetic |
| V | [part5-agents-and-rag.ipynb](/programming-handbook/lite/lab/index.html?path=part5-agents-and-rag.ipynb) | Chapters 28–30 · JSON Schema, a tool dispatcher, a JSON-RPC/MCP server, TF-IDF search, chunking, budgeted memory, a ReAct loop |
| V | [part5-rl-and-eval.ipynb](/programming-handbook/lite/lab/index.html?path=part5-rl-and-eval.ipynb) | Chapters 31–33 · gradients, bandits, REINFORCE, PPO's clip, a DPO trainer, reward hacking, pass@k, bootstrap intervals, judge bias |
| VI | [part6-advanced-structures.ipynb](/programming-handbook/lite/lab/index.html?path=part6-advanced-structures.ipynb) | Chapters 35–36 · rotations, AVL, red-black validation, hash functions, tombstones, tries, skip lists |
| VI | [part6-graphs-and-tools.ipynb](/programming-handbook/lite/lab/index.html?path=part6-graphs-and-tools.ipynb) | Chapters 37–41 · BFS/DFS, topological sort, Dijkstra, Bellman-Ford, Kruskal, counting and radix sort, regex, generator pipelines |

Each notebook is a working companion to its chapters: run the cells top to
bottom, change values, break things on purpose. Every one runs start to
finish with no errors, every random draw is seeded, and each ends with a
"Try it yourself" section whose scaffolds run as-is so you can fill them in
without first fixing them. Nothing you do can damage anything — worst case,
reload and start clean.

A few chapters deliberately have no notebook, because their subject cannot
run in a browser tab at all: the shell, SSH and Make (Chapter 40), the web
and GUI chapter (Chapter 42), and the capstone projects, which you build in
files on your own machine. Those pages give you a runnable Python *model* of
the idea instead — a shell-pipeline simulator, a dependency resolver, an HTTP
parser — so the concept is still executable even when the tool is not.

## What runs and what does not

**Works:** everything this book needs — the pure-Python standard library,
NumPy, and Matplotlib (plots render inline in the notebook, exactly as on
the site). Files work too: Pyodide has an in-memory filesystem, so a cell
can write a file and the next cell can read it back.

**Does not work:** anything that needs to leave the browser sandbox.

- `tkinter` or any desktop GUI toolkit — there is no desktop here
- network access (`requests`, sockets, APIs) and `input()`
- subprocesses, threads, and shell commands
- heavyweight pip installs — packages with native code that Pyodide has not
  ported will not import. That includes **PyTorch**, `transformers`,
  `pandas`, and `scipy`.

If an import fails inside JupyterLab, it is almost certainly on this list —
not a bug in your code.

!!! note "Part V has no PyTorch, on purpose"

    The AI-engineering notebooks build attention, softmax sampling, KV-cache
    arithmetic, REINFORCE, PPO's clipped objective and a full DPO trainer
    **by hand in NumPy**, on arrays of four to sixteen dimensions and
    sequences of five to ten tokens. That is not a workaround for the missing
    GPU — it is the pedagogy. A DPO update on eight preference pairs with ten
    parameters is a *correct* DPO update, and at that scale you can print
    every number and check the gradient against a finite difference. Where a
    snippet needs a language model it uses a deterministic rule-based
    `FakeLLM` stand-in, so every trace is identical on every machine, with no
    API key involved. Each notebook says plainly what is toy (the scale) and
    what is faithful (the update rules and the losses).

## Privacy and persistence

Your notebooks and edits are saved in your **browser's local storage** —
they never leave your machine, and no account or server is involved. Two
consequences:

- **Clearing your browser's site data wipes your work.** So does switching
  browsers or devices — the storage belongs to that one browser.
- **Download anything you want to keep** (right-click a file → *Download*,
  or *File → Download* in an open notebook) and you have an ordinary
  `.ipynb` file, usable in any Jupyter installation.

Once loaded, JupyterLab keeps working offline, like the rest of the site.

## Reporting issues

If a notebook fails to open, a cell errors unexpectedly, or JupyterLab
misbehaves, please
[open an issue](https://github.com/dongzhaohe321418-lab/programming-handbook/issues)
— include your browser name and what you clicked. It genuinely helps.
