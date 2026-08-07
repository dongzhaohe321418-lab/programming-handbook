# Resume plan — Parts V and VI

Parts I–IV are **shipped and live**: <https://dongzhaohe321418-lab.github.io/programming-handbook/>
(26 chapters, 143 pages, 868 CI-tested Python blocks, 6 JupyterLite notebooks,
4 projects, appendices A–D).

Parts V and VI are planned but only partially written. Their nav entries were
removed from `mkdocs.yml` so the strict build stays green; **re-add each
chapter's nav block only when all of that chapter's files exist in `docs/`.**

`WRITING_GUIDE.md` holds the binding contract, including the
"Part V (AI Engineering)" and "Part VI (Programming III)" rule sections.
`staging/` holds interrupted drafts (gitignored) — reuse or discard.

## Part V · AI Engineering (chapters 26–34)

| Chapter | Pages | Status |
| --- | --- | --- |
| `part5-overview.md` | 1 | **done** |
| 26 · How Language Models Work | index, 01-tokenization, 02-attention, 03-decoder-stack, 04-sampling, exercises | **done** |
| 27 · Serving Models — Inference Infrastructure | index, 01-kv-cache, 02-batching, 03-latency-streaming, 04-quantization-deploy, exercises | in progress |
| 28 · Tools, Schemas, and MCP | index, 01-function-calling, 02-structured-output, 03-mcp-protocol, 04-building-mcp-server, exercises | pending |
| 29 · Memory, Retrieval, and Knowledge | index, 01-embeddings-vector-search, 02-rag-pipeline, 03-agent-memory, 04-graphrag, exercises | pending |
| 30 · Agent Architectures | index, 01-agent-loop-react, 02-planning-reflection, 03-multi-agent, 04-frameworks, exercises | pending |
| 31 · Reinforcement Learning for LLMs | index, 01-rl-basics, 02-policy-gradient-ppo, 03-dpo-grpo, 04-reward-models, exercises | pending |
| 32 · Data-Centric AI | index, 01-why-data, 02-synthetic-data, 03-trajectories, 04-filtering, exercises | pending |
| 33 · Evaluation | index, 01-benchmarks, 02-eval-harness, 03-llm-as-judge, exercises | pending |
| 34 · Becoming an AI Engineer | index, 01-learning-path, 02-portfolio | pending |
| Projects 5–8 | mcp-server, react-agent, dpo-alignment, eval-harness | pending |
| Appendix E · AI engineering glossary | 1 | pending |

## Part VI · Programming III (chapters 35–42)

| Chapter | Pages | Status |
| --- | --- | --- |
| `part6-overview.md` | 1 | **done** |
| 35 · Balanced Search Trees | index, 01-rotations, 02-avl, 03-red-black, 04-b-trees, exercises | **done** |
| 36 · Hashing, Tries, and Skip Lists | index, 01-hash-tables, 02-collisions-resizing, 03-tries, 04-skip-lists, exercises | pending |
| 37 · Graphs | index, 01-representations, 02-traversal, 03-shortest-paths, 04-mst, exercises | in progress |
| 38 · Sorting in Linear Time | index, 01-lower-bound, 02-counting-radix-bucket, exercises | in progress |
| 39 · Functional Style, Streams, and Pipes | index, 01-lambdas, 02-map-filter-reduce, 03-pipelines, exercises | pending |
| 40 · The Developer Toolchain | index, 01-bash, 02-ssh-remote, 03-make, 04-junit, exercises | pending |
| 41 · Regular Expressions | index, 01-fundamentals, 02-groups-parsing, exercises | pending |
| 42 · Web and GUI Development | index, 01-html-css, 02-http-server, 03-javascript, 04-desktop-gui, exercises | pending |
| Projects 9–10 | route-finder, fullstack-app | pending |
| Appendix F · Toolchain quick reference | 1 | pending |

## Integration checklist for each finished chapter

1. Add its nav block back to `mkdocs.yml` (titles must match each page's H1).
2. `mkdocs build --strict` — no warnings.
3. `python -m pytest tests/ -q` — every Python block runs.
4. Commit and push; the deploy workflow publishes automatically.

## Also pending once both parts land

- `docs/index.md`: add Parts V and VI to the structure table, and add a
  Programming III course-mapping table alongside the Programming I/II ones.
- `docs/learning-path.md`: add entry points for Part V and Part VI, and extend
  the mermaid prerequisite graph.
- `README.md`: extend the structure table.
- `docs/ch25-next/01-cs400-preview.md`: it previews balanced trees, hashing,
  and graphs as future topics — once chapters 35–37 exist, point it at them.
- `notebooks/`: consider companion notebooks for Parts V and VI, and add any
  new ones to the table in `docs/try-in-jupyter.md`.
