# Chapter 29 · Memory, Retrieval, and Knowledge

A language model is a fixed function with a frozen head. Everything it knows
was baked into its weights months before you called it, and everything it
"remembers" about your conversation is text your program pasted into the
prompt. [Chapter 26](../ch26-llm-internals/index.md) built that function,
[Chapter 27](../ch27-inference/index.md) made it fast, and
[Chapter 28](../ch28-tools-mcp/index.md) let it call your code. This chapter
answers the question all three leave open: **how does an AI system look things
up, and how does it remember?**

The answer turns out to be a data-structures problem wearing a machine-learning
costume. You will build a vector index and a similarity metric; a chunker, a
retriever, a reranker, and an evaluation harness; a memory manager that fits a
conversation into a token budget; and a knowledge graph you traverse with
breadth-first search. Not one of these requires a neural network to
*understand*, and every one of them runs in your browser. Where a model is
genuinely needed — to embed text, to summarize, to answer — we substitute a
deterministic `FakeLLM` and say so, because the interesting engineering is
always on your side of the API call.

The chapter has a shape worth knowing in advance. Section 29.1 builds
retrieval from geometry: meaning as a direction, similarity as an angle,
search as a matrix multiply, and then the index structures that keep it fast
when there are fifty million vectors. Section 29.2 assembles those pieces into
**RAG** — the standard architecture for making a model answer from documents it
was never trained on — and, more importantly, teaches you to measure it.
Section 29.3 turns from facts to *continuity*: what an agent should carry
between turns and between sessions, and how to fit it in a context window you
pay for by the token. Section 29.4 covers the questions vector search
structurally cannot answer — multi-hop connections and corpus-wide summaries —
and builds a knowledge graph to answer them.

**After this chapter you can …**

- explain why keyword search fails on synonyms, and what an embedding is as a
  geometric object;
- derive and implement cosine similarity, say exactly when it differs from
  Euclidean distance, and explain why vectors are normalized at insert time;
- build a working TF-IDF search index and a BM25 retriever, and fuse them with
  reciprocal rank fusion;
- describe brute-force search as $O(n \cdot d)$ and explain how IVF and HNSW
  trade recall for speed — with the trade-off measured, not asserted;
- chunk a document four different ways and say what each one protects;
- assemble a cited prompt and verify every citation mechanically;
- measure retrieval with recall@k and MRR, and name what generation metrics
  can and cannot tell you;
- distinguish working, episodic, semantic, and procedural memory, and choose
  the right store for a given fact;
- compute what a context window costs in money, latency, and KV cache, and
  keep a prompt prefix cacheable;
- implement sliding-window, summarization, score-based, and hierarchical
  context strategies, and a complete `AgentMemory` that respects a budget;
- extract a knowledge graph from text, traverse it to answer multi-hop
  questions with citable paths, and say honestly when a graph is *not* worth
  the cost.

**Prerequisites:** [Chapter 26](../ch26-llm-internals/index.md) for tokens and
transformer internals, [Section 27.1](../ch27-inference/01-kv-cache.md) for the
KV cache and prefix caching (Section 29.3 does arithmetic on both), and
[Chapter 28](../ch28-tools-mcp/index.md) for the `FakeLLM` convention and the
habit of validating model output. From Parts II–IV you need
[Section 9.1](../ch09-collections/01-references.md) (dictionaries — every index
and store here is one), [Section 16.1](../ch16-complexity/01-big-o.md) (Big-O,
because the whole ANN story is a complexity trade),
[Section 21.2](../ch21-heaps/02-priority-queues.md) (heaps, for top-$k$), and
[Section 12.1](../ch12-classes/01-class-anatomy.md) (classes). Section 29.4
leans on [Section 37.1](../ch37-graphs/01-representations.md) and
[Section 37.2](../ch37-graphs/02-traversal.md); it re-explains what it needs,
but reading them first makes it easy.

**Sections**

- [29.1 Embeddings and vector search](01-embeddings-vector-search.md) — the
  synonym problem, a hand-made embedding space you can plot, cosine similarity
  from scratch, a TF-IDF index over twelve sentences, IVF and HNSW, the vector
  database landscape, and hybrid search with reciprocal rank fusion.
- [29.2 The RAG pipeline](02-rag-pipeline.md) — why retrieval beats retraining,
  the ingest and query pipelines, four chunking strategies and the fact a bad
  boundary destroys, choosing $k$, reranking, cited prompts with a citation
  verifier, and recall@k / MRR.
- [29.3 Agent memory and context management](03-agent-memory.md) — the four
  memory types, what a context window costs, sliding windows versus
  summarization versus scoring versus summary trees, keeping the prefix
  cacheable, writing and forgetting memories, and a complete `AgentMemory`
  class.
- [29.4 Knowledge graphs and GraphRAG](04-graphrag.md) — the multi-hop question
  top-$k$ cannot answer, triple extraction with rules and with a model,
  adjacency storage, BFS traversal with citation trails, communities and
  global summaries, graph + vector fusion, and an honest cost table.
- [Exercises](exercises.md) — compute cosine by hand, choose $k$, repair a
  chunker, implement retrieval metrics, design a memory schema, fit a context
  into 4000 tokens, extract triples, and answer a three-hop graph query.

!!! note "What is real and what is simulated here"

    Every algorithm on these pages is the real one: cosine similarity, TF-IDF,
    BM25, k-means, reciprocal rank fusion, breadth-first search, label
    propagation, recall@k, MRR. What is simulated is the *model*: embeddings
    come from hand-built vectors instead of a trained encoder, and every
    generation, summarization, and extraction call is a deterministic
    `FakeLLM`. The scale is toy — a dozen documents, a twenty-turn
    conversation, a fourteen-node graph — so that you can read every number.
    Swap in a real embedding API and a real model and the code around them does
    not change.
