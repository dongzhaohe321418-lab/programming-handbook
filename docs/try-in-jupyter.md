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
- Six companion notebooks that follow the book, ready to open:

| Notebook | What it covers |
| --- | --- |
| [part1-the-machine.ipynb](/programming-handbook/lite/lab/index.html?path=part1-the-machine.ipynb) | Part I · bits, binary, and floating point |
| [part2-python-basics.ipynb](/programming-handbook/lite/lab/index.html?path=part2-python-basics.ipynb) | Chapters 2–6 · variables to loops |
| [part2-collections-and-oop.ipynb](/programming-handbook/lite/lab/index.html?path=part2-collections-and-oop.ipynb) | Chapters 7–14 · lists, dicts, and classes |
| [part3-data-structures.ipynb](/programming-handbook/lite/lab/index.html?path=part3-data-structures.ipynb) | Chapters 18–21 · linked lists to heaps |
| [part3-algorithms.ipynb](/programming-handbook/lite/lab/index.html?path=part3-algorithms.ipynb) | Chapters 16–17 and 22 · Big-O, recursion, sorting |
| [part4-systems.ipynb](/programming-handbook/lite/lab/index.html?path=part4-systems.ipynb) | Chapter 23 · bytecode, memory, references |

Each notebook is a working companion to its chapters: run the cells top to
bottom, change values, break things on purpose. Nothing you do can damage
anything — worst case, reload and start clean.

## What runs and what does not

**Works:** everything this book needs — the pure-Python standard library,
NumPy, and Matplotlib (plots render inline in the notebook, exactly as on
the site).

**Does not work:** anything that needs to leave the browser sandbox.

- `tkinter` or any desktop GUI toolkit — there is no desktop here
- network access (`requests`, sockets, APIs)
- heavyweight pip installs — packages with native code that Pyodide has not
  ported will not import

If an import fails inside JupyterLab, it is almost certainly on this list —
not a bug in your code.

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
