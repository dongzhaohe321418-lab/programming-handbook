# Writing Guide — Programming & Computer Systems Handbook

Contract for every content page in `docs/`. Follow it exactly; the site build
(`mkdocs build --strict`) and the snippet test-suite both enforce parts of it.

## Audience and voice

- Reader: a true beginner in programming and computer systems. Assume zero
  prior coding experience for Part I–II; Part III may assume Part II.
- Voice: plain English, encouraging, concrete. Define every piece of jargon
  the first time it appears. Prefer a worked example over an abstract claim.
- The handbook parallels a university Programming I / Programming II sequence
  that is taught in Java. **Python is the primary teaching language** (it runs
  in the browser); Java appears in side-by-side comparisons where the concepts
  genuinely differ (typing, compilation, overloading, interfaces, etc.).

## Page anatomy

Every **section page** (`NN-*.md`):

1. `# H1 title` matching the nav entry.
2. One-paragraph *why this matters* opener (no heading).
3. Concept sections (`## H2`) — each idea introduced with prose, then at least
   one **runnable Python block**, then interpretation of the output.
4. A `!!! warning "Common mistakes"` admonition near the end listing 2–4
   realistic beginner errors for this topic.
5. `## Check your understanding` — 2–4 questions, each with the answer in a
   collapsible `??? success "Answer"` block.

Every **chapter overview** (`index.md`): 2–3 paragraphs on what the chapter
covers and why, a bullet list "After this chapter you can …", prerequisites
(link to earlier chapters), and a short list of the sections.

Every **exercises page** (`exercises.md`): 6–10 exercises, easiest first,
labelled `### Exercise N.M — title` with a difficulty tag (●, ●●, ●●●). Every
exercise has a full solution in `??? success "Solution"` with a runnable
Python block and a sentence explaining the idea. At least one exercise per
chapter asks the reader to *predict* what code prints before running it.

Section pages: roughly 150–350 lines. Don't pad; don't stub.

## Code blocks — the rules that keep the site working

Every ` ```python ` block automatically gets a **Run button** that executes it
with Pyodide in the reader's browser, and is also executed by the CI test
harness. Therefore every Python block MUST:

- be **self-contained**: it runs top-to-bottom in a fresh namespace with no
  undefined names. If a block deliberately continues the previous block on the
  same page, its first line must be `# continues` (the harness then prepends
  the earlier blocks).
- use only the **standard library, numpy, and matplotlib**. No pandas, scipy,
  requests, tkinter, network, threads, or pip installs.
- never call `input()` — hard-code the "user input" into a variable and say so
  in a comment (e.g. `text = "42"   # imagine the user typed this`).
- avoid `sys.argv` reliance — simulate: `argv = ["prog", "5", "7"]`.
- finish in **under ~2 seconds** (keep n small in timing/sorting demos).
- for plots: use matplotlib normally (`plt.plot(...)`); do **not** call
  `plt.show()` — the runner captures the current figure automatically. Still
  label axes.
- file I/O is allowed and encouraged in the Files chapter: Pyodide has an
  in-memory filesystem, so *create the file first, then read it* within the
  same block.
- randomness: seed it (`random.seed(3)` / `np.random.default_rng(0)`) so
  output is reproducible.

Special first-line markers (the CI harness reads these):

- `# raises ValueError` (any exception name) — the block is *expected* to
  raise; use for teaching error messages and tracebacks.
- `# widget` — the block is bound to sliders (see below); CI skips it.
- `# no-test` — CI skips it (use sparingly, e.g. a deliberately infinite loop
  shown for discussion must instead be a ```text block — never make a real
  python block loop forever).

Code that must NOT get a Run button (pseudo-code, shell sessions, deliberately
incomplete fragments): use ` ```text `, ` ```console `, or ` ```java ` fences.

### Java comparisons

Where Java genuinely differs, use content tabs:

```markdown
=== "Python"

    ```python
    x = 7
    ```

=== "Java"

    ```java
    int x = 7;
    ```
```

Java blocks are illustrative only (they don't run). Keep them short and
correct — they mirror what the reader's Java course looks like. Do not tab
every snippet; only where the contrast teaches something.

### Interactive widgets (optional, at most 1–2 per chapter)

A slider-driven demo: put a yaml config block immediately before the python
block. The python block's first line must be `# widget`.

```markdown
    ```yaml
    # widget-config
    sliders:
      n: {min: 1, max: 50, step: 1, default: 10, label: "n items"}
    ```

    ```python
    # widget — n is bound from the slider above
    total = sum(range(int(n) + 1))
    print(f"1 + 2 + ... + {int(n)} = {total}")
    ```
```

## Formatting toolbox

- Math: inline `$O(n \log n)$`, display `$$ ... $$` (MathJax). Always LaTeX,
  never Unicode look-alikes.
- Diagrams: Mermaid fences (` ```mermaid `) — flowcharts for control flow,
  `classDiagram` for UML, simple graphs for linked lists/trees. No external
  images; no image files exist in this repo.
- Admonitions: `!!! note`, `!!! tip`, `!!! example`, `!!! warning`,
  `!!! info "Java corner"` for short Java asides that don't need tabs.
  Collapsible: `??? success "Solution"` / `??? success "Answer"`.
- Tables for compact comparisons (operators, complexity classes, methods).
- Cross-links are relative: `[Chapter 4](../ch04-branching/index.md)`,
  `[booleans](../ch04-branching/01-booleans-logic.md)`. Only link to files
  that exist in the nav (see mkdocs.yml). `--strict` fails on broken links.
- Keys: `++ctrl+c++` renders keyboard keys.

## Accuracy bar

- Every factual claim about Python semantics must be true for CPython 3.11+
  (Pyodide is 3.11/3.12). Every Java claim true for Java 17.
- Every runnable block's printed output must match what the prose claims.
  When you show expected output in prose, show it exactly.
- Big-O claims, data-structure invariants, and algorithm behaviour must be
  textbook-correct. When simplifying, say "roughly" — never state a falsehood.

## Part V (AI Engineering) — extra rules

Chapters 26–34 teach LLMs, agents, RL, data, and inference infrastructure.
The reader arrives having finished Parts I–IV: they know Python, classes,
data structures, Big-O, and files. They know **no** machine learning. Every
ML idea must be built up from that base.

The Run-button contract still holds — which means **none of the real stack is
importable**: no torch, transformers, vllm, openai, langchain, requests, no
network, no GPU. This is a feature, not a limitation. Teach the mechanism by
building a small honest version of it:

- **Numpy is the tensor library.** Attention, softmax, embeddings, gradient
  steps — all written by hand in numpy on tiny arrays (dimensions like 4–16,
  sequences of 5–10 tokens). Hand-rolled implementations are the point;
  the reader sees every number.
- **Simulate the model, don't call one.** Where a snippet needs an LLM, use a
  deterministic stand-in and name it `FakeLLM` (a class) or `fake_llm(prompt)`
  (a function) — scripted/rule-based responses keyed off the prompt. State in
  prose that this stands in for a real API call. Anything that would need a
  network, an API key, or a GPU (`client.messages.create(...)`, `vllm serve`,
  `ollama run`) goes in a ```text or ```console fence so it gets no Run
  button and is never executed by CI.
- **Toy scale, real algorithm.** A DPO update on 6 preference pairs with a
  2-parameter policy is a *correct* DPO update. Say explicitly what is toy
  (scale, dimensions) and what is faithful (the update rule, the loss).
- **Verify the claim in the block.** If the prose says "the loss decreases",
  print the loss curve. If it says "GQA cuts KV memory 4×", compute both
  numbers and print the ratio.
- **Arithmetic is the best teacher for infra.** KV-cache size, TTFT/TPOT,
  throughput, quantization footprints, context-window costs: write the
  formula in LaTeX, then a runnable calculator with realistic model numbers
  (7B/70B, 32 layers, hidden 4096, fp16), and print a readable table.
- **Name real systems accurately.** vLLM, Ollama, llama.cpp, MCP, LangGraph,
  SGLang, DeepSpeed, TRL, verl. Describe what they do; never invent APIs.
  When showing real library usage, use a non-python fence and keep it short
  and version-neutral. Prefer describing the concept over pinning an API that
  will drift.
- **Be honest about the frontier.** This field moves fast: mark what is
  settled (attention, KV cache, PPO/DPO math) versus what is current practice
  and may change (specific frameworks, benchmark leaderboards). Never state a
  leaderboard number as timeless fact.
- **No fabricated citations or metrics.** If you name a paper, name it
  correctly (Attention Is All You Need, InstructGPT, DPO, GRPO/DeepSeekMath,
  ReAct, Toolformer, Self-Instruct, Evol-Instruct, LoRA, FlashAttention,
  PagedAttention/vLLM, SWE-bench, GAIA, HumanEval, MMLU). If unsure of a
  number, describe the direction ("roughly an order of magnitude") instead.

Java tabs are **not** used in Part V. Where a second language helps, use
TypeScript (the other language of the LLM ecosystem) — for MCP servers,
tool schemas, and streaming — in ```typescript fences (not runnable).

## Part VI (Programming III) — extra rules

Chapters 35–42 are the third-course arc: advanced data structures (balanced
trees, hashing, tries, skip lists, graphs, linear-time sorting) plus the
full working toolchain (bash, SSH, Make, JUnit, lambdas/streams, regex, web,
GUI). The reader has finished Parts I–IV. Part V is **not** a prerequisite.

- **Numbering.** These chapters are numbered 35–42 because they were added
  after Part V. Say plainly in the Part VI overview that Part VI continues
  directly from Part III (Chapter 22) and that Parts IV–V are independent.
- **Data-structure chapters follow the Part III house style**: draw the
  structure in mermaid *before* the code, trace every operation on a small
  example, then implement it runnably, then state the costs. Every invariant
  gets stated explicitly and verified by a runnable checker function.
- **Toolchain chapters cannot run their subject in the browser.** Bash, SSH,
  Make, JUnit, JavaFX, and browser JavaScript go in ```console, ```text,
  ```java, ```javascript, ```html, ```css, or ```makefile fences — never a
  ```python fence. But *do* give the reader something runnable on each such
  page: teach the underlying concept with a Python model they can execute.
  Examples that work well — a Make-style dependency resolver with topological
  sort and timestamp staleness checks; an HTTP request/response parser and a
  route dispatcher; a tiny shell-pipeline simulator; a JUnit-style assertion
  library; a CSS-selector matcher over a parsed DOM-like dict tree.
- **Regex is fully runnable** — `re` is in the standard library. Use it
  heavily: every pattern shown should be executed against real strings with
  the matches printed. Warn about catastrophic backtracking *conceptually*;
  never write a snippet that actually hangs.
- **Java appears here as it does in Parts II–III** (tabs / ```java fences)
  because the parallel university course is Java-based: JUnit 5, lambdas,
  the Streams API, and JavaFX are Java topics. Keep Java snippets short,
  correct for Java 17, and non-runnable.
- **Web pages**: show real HTML/CSS/JS in their own fences, and be explicit
  that the reader should save the file locally and open it in a browser —
  the Run button cannot render a page.

## What not to do

- No placeholder text, no "TODO", no "coming soon".
- No content copied from zyBooks, textbooks, or any copyrighted course
  material — all prose original, all examples original (the *topics* follow
  the standard curriculum; the *words and code* are yours).
- No first-person singular; use "we" and "you".
- Don't reference page numbers, weeks, exams, Canvas, zyBooks, or any
  specific university logistics. This is a standalone handbook.
