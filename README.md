# Programming & Computer Systems Handbook

**A zero-foundation, textbook-grade open handbook on programming and computer
systems — from bits and binary to data structures and algorithms — with
Python code that runs in your browser.**

**Live site:** <https://dongzhaohe321418-lab.github.io/programming-handbook/>

## What makes it different

- **▶ Run buttons everywhere.** Every Python snippet executes in the browser
  via [Pyodide](https://pyodide.org/) (WebAssembly CPython) — no install, no
  server, no account. Plots render inline via Matplotlib.
- **A full in-browser JupyterLab** ([JupyterLite](https://jupyterlite.readthedocs.io/))
  with one ready-made notebook per part.
- **Follows the standard university sequence.** Chapters 2–14 mirror a
  typical Programming I course (15 modules); chapters 15–22 mirror
  Programming II (5 units: OOP design, Big-O, recursion, linked lists,
  stacks/queues, trees, heaps, sorting); chapters 35–42 mirror Programming
  III (balanced trees, hashing, graphs, linear-time sorting, plus the
  engineering toolchain and web/GUI track). Python is the teaching language,
  with side-by-side Java tabs wherever the two genuinely differ.
- **A full AI-engineering track.** Chapters 26–34 build a BPE tokenizer,
  attention, a decoder stack, a KV cache, an MCP server, a RAG pipeline, a
  ReAct agent, DPO and GRPO, a data pipeline, and an eval harness — all from
  scratch in numpy and the standard library, all running in the browser.
- **Computer systems included.** Part I explains what a computer *is*
  (hardware, binary, compilers vs interpreters) and Part IV goes deeper
  (OS, memory layout, virtual machines, Git, testing) — the context most
  beginner courses skip.
- **Every snippet is CI-tested.** `tests/test_snippets.py` extracts and
  executes every Python block in `docs/` on every push, so the Run buttons
  can't silently rot.

## Structure

| Part | Chapters | Content |
| --- | --- | --- |
| I · The Machine | 0–1 | Hardware, binary, programs, command line, Git |
| II · Programming I | 2–14 | Types → branching → loops → arrays → exceptions → files → classes → UML |
| III · Programming II | 15–22 | Inheritance, Big-O, recursion, linked lists, stacks/queues, BSTs, heaps, sorting |
| IV · Systems & Practice | 23–25 | OS & memory, interpreters/VMs, engineering practice, roadmap |
| V · AI Engineering | 26–34 | LLM internals, inference/serving, tools & MCP, RAG & agent memory, agent architectures, RL (PPO/DPO/GRPO), data-centric AI, evaluation, career path |
| VI · Programming III | 35–42 | Balanced trees, hashing/tries/skip lists, graphs, linear-time sorting, streams, toolchain (bash/SSH/Make/JUnit), regex, web & GUI |
| Projects | 10 | Number-systems toolkit, text adventure, data-structures library, sorting visualizer, MCP server, ReAct agent, DPO alignment, eval harness, route finder, full-stack app |
| Appendix | A–F | Python↔Java cheat sheet, Big-O reference, glossary, further reading, AI glossary, toolchain reference |

Parts V and VI are independent of each other. Part VI continues directly
from Part III (Chapter 22); Part V needs only Parts I–IV.

## Local development

```bash
pip install -r requirements.txt
mkdocs serve          # http://127.0.0.1:8000
```

Run the snippet test-suite (executes every Python block in docs/):

```bash
pip install pytest numpy matplotlib
python -m pytest tests/ -q
```

Build the JupyterLite site:

```bash
pip install -r requirements-lite.txt
jupyter lite build --contents notebooks --output-dir _output/lite
```

Deployment is automatic: pushing to `main` builds MkDocs + JupyterLite and
publishes to GitHub Pages (see `.github/workflows/deploy.yml`).

## Writing conventions

All content rules live in [WRITING_GUIDE.md](WRITING_GUIDE.md) — page
anatomy, the self-containment contract for runnable blocks, snippet markers
(`# raises`, `# widget`, `# continues`), and the accuracy bar.

## License

Text: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) ·
Code: [MIT](LICENSE)

## Sibling project

[materials-simulation-handbook](https://github.com/dongzhaohe321418-lab/materials-simulation-handbook) —
the same philosophy applied to computational materials science.
