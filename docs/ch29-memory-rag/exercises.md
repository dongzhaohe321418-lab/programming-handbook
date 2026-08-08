# Chapter 29 · Exercises

## The chapter in brief

- Keyword search matches **strings**, and strings are not meanings — which is
  why "automobile" finds nothing in a corpus that says "car"
  ([29.1](01-embeddings-vector-search.md)).
- An **embedding** is a vector chosen so that similar meanings land in similar
  directions, and **cosine similarity** is the angle between two of them.
- Normalizing every vector once, at insert time, turns cosine similarity into a
  plain dot product — so a whole search is one matrix multiply.
- **TF-IDF** gives you the entire machinery of vector search — vectors,
  weighting, top-$k$ — with none of the semantics; real embeddings keep the
  machinery and replace the vectorizer.
- Brute-force search is $O(n \cdot d)$ per query, and **IVF** and **HNSW** buy
  speed by giving up exactness, measured as **recall@k** and steered by one
  knob (`nprobe`, `ef_search`).
- **Hybrid search** fuses a lexical and a semantic retriever with **reciprocal
  rank fusion**, which combines *ranks* rather than incomparable scores.
- **RAG** is architecturally humble: look the answer up, paste it into the
  prompt, and ask ([29.2](02-rag-pipeline.md)).
- **Chunking is the whole ballgame** — a boundary through the middle of a fact
  destroys it for every value of $k$, and overlap is the cheapest insurance
  against that.
- A **bi-encoder** retrieves wide because its vectors were computed offline; a
  **cross-encoder** reranks narrow because it reads the query and the chunk
  together.
- RAG has two scoreboards: retrieval (**recall@k** and **MRR**) and generation
  (faithfulness and answer relevance), and the fixes for them are unrelated.
- Agent memory splits into **working, episodic, semantic and procedural**, and
  only the first lives in the context window for free
  ([29.3](03-agent-memory.md)).
- Context is a budget paid every turn — and keeping the prompt's stable prefix
  byte-identical is what makes **prefix caching** pay.
- A sliding window ranks by recency and loses the user's name; a **score over
  recency, relevance and importance** keeps it, and forgetting must be weighted
  by importance too.
- Similarity search cannot **chain**, so multi-hop and corpus-wide questions
  need a **knowledge graph**: triples, an adjacency map, BFS with a citation
  trail, and communities for global answers ([29.4](04-graphrag.md)).
- Extraction costs a model call per chunk and the graph goes stale globally, so
  measure vector RAG first and add structure when the metrics demand it.

### Key terms

| Term | One-line reminder |
| --- | --- |
| [embedding](../appendix/E-ai-glossary.md#e) | a vector standing for a piece of text, where nearby means similar in meaning |
| [cosine similarity](../concept-index.md#c) | the cosine of the angle between two vectors; on unit vectors, just a dot product |
| TF-IDF / BM25 | lexical vectors weighted by word rarity — unbeatable on rare exact tokens |
| approximate nearest neighbour (ANN) | an index that returns *almost always* the right top-$k$, far faster |
| [recall@k](../concept-index.md#r) | of the chunks that should have been retrieved, the fraction in the top $k$ |
| MRR | mean of one over the rank of the first correct hit — the reranker's metric |
| [hybrid search](../appendix/E-ai-glossary.md#h) | run a lexical and a semantic retriever, then merge them |
| [reciprocal rank fusion](../concept-index.md#r) | merge ranked lists by $\sum 1/(k + \text{rank})$, using ranks only |
| [chunking](../appendix/E-ai-glossary.md#c) | splitting a document into the passages you embed, retrieve and cite |
| [RAG](../appendix/E-ai-glossary.md#r) | retrieve relevant text, put it in the prompt, then generate |
| [cross-encoder](../appendix/E-ai-glossary.md#c) | scores a `(query, chunk)` pair jointly; accurate, and too slow for a corpus |
| working / episodic / semantic / procedural memory | now, what happened, what is true, and how to do it |
| [prefix caching](../appendix/E-ai-glossary.md#p) | the server skips prefilling an exact token prefix it has already seen |
| [knowledge graph](../concept-index.md#k) | entities as nodes, labelled relations as edges, stored as triples |
| [GraphRAG](../appendix/E-ai-glossary.md#g) | extract a graph, traverse it for multi-hop answers, summarize communities for global ones |

Now the drills — work them in order, because the retrieval problems build the
intuitions the memory and graph problems assume.

Eight problems on retrieval, RAG, memory, and knowledge graphs. They build on
[29.1](01-embeddings-vector-search.md), [29.2](02-rag-pipeline.md),
[29.3](03-agent-memory.md), and [29.4](04-graphrag.md), and every solution runs
in the browser. Exercise 29.3 asks you to *predict* the output before running
it — write your prediction down first; the gap between it and the printed
result is where the learning is.

Nothing here calls a model or touches the network. Where a model would be
needed it is a scripted stand-in, and every solution is self-contained: you can
run any one of them without having run the others.

---

### Exercise 29.1 — Cosine by hand, then verified (●)

Here is a query vector and four document vectors in a four-dimensional space:

```text
q  = [ 1,  2,  2,  0]
d1 = [ 2,  4,  4,  0]
d2 = [ 0,  0,  3,  4]
d3 = [ 3,  0,  0,  4]
d4 = [10, 20, 20,  0]
```

On paper, for each document:

1. compute the dot product $\mathbf{q}\cdot\mathbf{d}$;
2. compute the two lengths $\lVert\mathbf{q}\rVert$ and $\lVert\mathbf{d}\rVert$;
3. divide to get the cosine similarity.

(The numbers are chosen so every length is a whole number.) Then rank the four
documents by cosine, rank them again by Euclidean distance from $\mathbf{q}$,
and explain the disagreement. Finally, write the code that checks your
arithmetic.

??? success "Solution"

    By hand, $\lVert\mathbf{q}\rVert = \sqrt{1 + 4 + 4} = 3$.

    - $\mathbf{d_1} = 2\mathbf{q}$: dot $= 2 + 8 + 8 = 18$, $\lVert\mathbf{d_1}\rVert = 6$,
      so $\cos = 18 / (3 \times 6) = 1$.
    - $\mathbf{d_2}$: dot $= 0 + 0 + 6 + 0 = 6$, $\lVert\mathbf{d_2}\rVert = \sqrt{9+16} = 5$,
      so $\cos = 6 / 15 = 0.4$.
    - $\mathbf{d_3}$: dot $= 3 + 0 + 0 + 0 = 3$, $\lVert\mathbf{d_3}\rVert = 5$,
      so $\cos = 3 / 15 = 0.2$.
    - $\mathbf{d_4} = 10\mathbf{q}$: dot $= 90$, $\lVert\mathbf{d_4}\rVert = 30$,
      so $\cos = 90 / 90 = 1$.

    ```python
    import numpy as np

    q = np.array([1.0, 2.0, 2.0, 0.0])
    DOCS = {"d1": [2.0, 4.0, 4.0, 0.0],
            "d2": [0.0, 0.0, 3.0, 4.0],
            "d3": [3.0, 0.0, 0.0, 4.0],
            "d4": [10.0, 20.0, 20.0, 0.0]}

    def cosine(a, b):
        a, b = np.asarray(a, float), np.asarray(b, float)
        return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))

    print(f"|q| = {np.linalg.norm(q):.0f}\n")
    print(f"{'doc':>4} {'dot':>6} {'|d|':>6} {'cosine':>8} {'euclidean':>10}")
    rows = []
    for name, d in DOCS.items():
        d = np.array(d)
        rows.append((name, float(q @ d), float(np.linalg.norm(d)),
                     cosine(q, d), float(np.linalg.norm(q - d))))
        print(f"{name:>4} {rows[-1][1]:>6.1f} {rows[-1][2]:>6.1f} "
              f"{rows[-1][3]:>8.4f} {rows[-1][4]:>10.4f}")

    print("\nby cosine   :", [r[0] for r in sorted(rows, key=lambda r: -r[3])])
    print("by euclidean:", [r[0] for r in sorted(rows, key=lambda r: r[4])])
    ```

    `d1` and `d4` both score a cosine of exactly 1.0 — they are $\mathbf{q}$
    scaled by 2 and by 10, so they point in *exactly* the same direction and
    differ only in length. Euclidean distance ranks `d4` **last**, 27.0 away,
    behind two documents pointing somewhere else entirely. If these were
    documents, `d4` would be the long article on precisely your topic, and
    Euclidean distance would bury it for the crime of being long. That is why
    retrieval uses cosine.

---

### Exercise 29.2 — Choose $k$ for a scenario (●)

You are building a support bot over a small policy handbook. The
constraints: chunks average around 16 tokens (they are short policy
sentences), the model call is billed per input token, and a product manager
has asked for "the highest recall we can get without wasting context".

Below is the handbook and a labelled evaluation set. Build a TF-IDF retriever,
print recall@k and the average context size for $k = 1 \dots 6$, and recommend
a value of $k$ with a one-sentence justification.

```text
LABELLED = [
    ("how long does a refund take?",                 {0}),
    ("what is the deadline for requesting a refund?", {1}),
    ("do I get my shipping fee back if I cancel?",    {3, 8}),
    ("when does express delivery arrive?",            {5}),
    ("can I refund a gift card?",                     {7}),
]
```

??? success "Solution"

    ```python
    import re
    import numpy as np

    CHUNKS = [
        "Refunds are issued to the original payment method within 5 business days.",
        "A refund request must be filed within 30 days of delivery.",
        "Damaged items are replaced free of charge; no refund is required.",
        "Shipping fees are not refunded unless the order was cancelled before dispatch.",
        "Orders are dispatched from the Rotterdam warehouse on weekdays.",
        "Express delivery arrives the next working day for orders placed before 16:00.",
        "The support desk answers email between 09:00 and 17:00 CET.",
        "Gift cards cannot be refunded but never expire.",
        "A cancelled order is refunded in full, including shipping.",
        "International orders may be delayed by customs inspection.",
    ]
    LABELLED = [
        ("how long does a refund take?", {0}),
        ("what is the deadline for requesting a refund?", {1}),
        ("do I get my shipping fee back if I cancel?", {3, 8}),
        ("when does express delivery arrive?", {5}),
        ("can I refund a gift card?", {7}),
    ]

    def tokenize(t):
        return re.findall(r"[a-z0-9]+", t.lower())

    vocab = sorted({w for c in CHUNKS for w in tokenize(c)})
    col = {w: i for i, w in enumerate(vocab)}
    N = len(CHUNKS)
    doc_freq = np.zeros(len(vocab))
    for c in CHUNKS:
        for w in set(tokenize(c)):
            doc_freq[col[w]] += 1
    idf = np.log((1 + N) / (1 + doc_freq)) + 1.0

    def vec(text):
        v = np.zeros(len(vocab))
        for w in tokenize(text):
            if w in col:
                v[col[w]] += 1.0
        v *= idf
        n = np.linalg.norm(v)
        return v / n if n else v

    INDEX = np.stack([vec(c) for c in CHUNKS])

    def retrieve(query, k):
        return [int(i) for i in np.argsort(-(INDEX @ vec(query)))[:k]]

    def n_tokens(text):
        return max(1, round(len(text) / 4))

    print(f"{'k':>3} {'recall@k':>9} {'avg context tokens':>20}")
    for k in range(1, 7):
        recall = np.mean([len(set(retrieve(q, k)) & gold) / len(gold)
                          for q, gold in LABELLED])
        tokens = np.mean([sum(n_tokens(CHUNKS[i]) for i in retrieve(q, k))
                          for q, _ in LABELLED])
        print(f"{k:>3} {recall:>9.3f} {tokens:>20.1f}")
    ```

    Recall jumps from 0.300 at $k=1$ to 0.800 at $k=2$, sits flat through
    $k=3$, reaches 1.000 at $k=4$, and never improves again — while context
    keeps growing by roughly 16 tokens per extra chunk. **Recommend $k=4$**: it
    is the smallest $k$ with perfect recall on this set, and every chunk beyond
    it is pure cost. If the budget were tight you could argue for $k=2$, which
    buys 80% of the recall for half the tokens; what you cannot justify is
    $k=6$, which costs 57% more context than $k=4$ for nothing at all.

---

### Exercise 29.3 — Repair a broken chunker (●● — predict first)

A colleague ships this configuration:

```text
chunk_size = 40 characters, overlap = 0, split on character count
```

over this paragraph:

```text
The night shift starts at 22:00 and ends at 06:00. The escalation number is
555-0143. Do not call it before 22:00.
```

**Predict before running.** Write down your answers to these three questions:

1. How many chunks does this produce?
2. Does any single chunk contain the complete phone number `555-0143`?
3. If a user asks "what is the escalation number?", which chunk will a
   keyword retriever rank first, and what would a model answer from it?

Then write the code to check, and fix the configuration so that no chunk ever
splits a sentence.

??? success "Solution"

    ```python
    import re

    DOC = ("The night shift starts at 22:00 and ends at 06:00. The escalation "
           "number is 555-0143. Do not call it before 22:00.")
    NUMBER = "555-0143"

    def fixed_size(text, size, overlap=0):
        step = size - overlap
        return [text[i:i + size] for i in range(0, len(text), step) if text[i:i + size]]

    def by_sentence(text, max_chars):
        """Never cut inside a sentence; pack sentences until the budget is full."""
        out, cur = [], ""
        for s in re.findall(r"[^.]+\.", text):
            s = s.strip()
            if cur and len(cur) + 1 + len(s) > max_chars:
                out.append(cur)
                cur = s
            else:
                cur = f"{cur} {s}".strip()
        return out + ([cur] if cur else [])

    broken = fixed_size(DOC, 40)
    print(f"broken config: {len(broken)} chunks")
    for i, c in enumerate(broken):
        print(f"  [{i}] {c!r}")
    print("complete phone number in some chunk?", any(NUMBER in c for c in broken))

    print("\nwith overlap=15:")
    patched = fixed_size(DOC, 40, overlap=15)
    print(f"  {len(patched)} chunks; number intact in",
          [i for i, c in enumerate(patched) if NUMBER in c])

    print("\nsentence chunking (max 80):")
    fixed = by_sentence(DOC, 80)
    for i, c in enumerate(fixed):
        print(f"  [{i}] {len(c):>2}ch {c!r}")
    print("  number intact in", [i for i, c in enumerate(fixed) if NUMBER in c])
    ```

    Three chunks, and **no chunk contains the whole number**: chunk 1 ends
    `'...The escalation number is 555-'` and chunk 2 begins
    `'0143. Do not call...'`. A keyword retriever asked for "the escalation
    number" ranks chunk 1 first — it is the only chunk containing both
    *escalation* and *number* — and hands the model a passage that trails off
    at `555-`. The model either says it does not know, or completes the number
    itself, which is the worst outcome available.

    Two repairs, in increasing order of quality. An overlap of 15 characters
    restores the number to a whole chunk (two of them, in fact), at the cost of
    5 chunks instead of 3 — about two-thirds more storage. Chunking on sentence
    boundaries is better: it produces two chunks, neither of which cuts a
    sentence, so the failure cannot recur for *any* fact in the paragraph
    rather than being patched for this one. For real documents use recursive
    chunking (paragraph, then sentence, then word) with a small overlap, and
    always print twenty chunks before you trust the config.

---

### Exercise 29.4 — Implement the retrieval metrics (●●)

Given a set of retrieval runs — each a ranked list of chunk ids plus the set of
ids that are actually relevant — implement `recall_at_k`, `precision_at_k`, and
`mrr`, and print them.

```text
RUNS = [
    ([3, 1, 7, 0], {1}),        # relevant item found at rank 2
    ([2, 5, 4, 9], {5, 4}),     # two relevant items, at ranks 2 and 3
    ([8, 6, 0, 3], {1}),        # relevant item not retrieved at all
    ([0, 2, 9, 7], {0}),        # relevant item found at rank 1
]
```

Then answer: which metric would move if you added a reranker that reorders each
run's four results but never fetches new ones — and which would not?

??? success "Solution"

    ```python
    import numpy as np

    RUNS = [
        ([3, 1, 7, 0], {1}),
        ([2, 5, 4, 9], {5, 4}),
        ([8, 6, 0, 3], {1}),
        ([0, 2, 9, 7], {0}),
    ]

    def recall_at_k(runs, k):
        """Of the relevant items, what fraction are in the top k?"""
        return float(np.mean([len(set(ranked[:k]) & gold) / len(gold)
                              for ranked, gold in runs]))

    def precision_at_k(runs, k):
        """Of the k items returned, what fraction are relevant?"""
        return float(np.mean([len(set(ranked[:k]) & gold) / k
                              for ranked, gold in runs]))

    def mrr(runs):
        """Mean of 1/(rank of the first relevant hit); 0 if there is none."""
        scores = []
        for ranked, gold in runs:
            hit = next((rank for rank, doc in enumerate(ranked, start=1)
                        if doc in gold), None)
            scores.append(1.0 / hit if hit else 0.0)
        return float(np.mean(scores))

    print(f"{'k':>3} {'recall@k':>9} {'precision@k':>12}")
    for k in (1, 2, 3, 4):
        print(f"{k:>3} {recall_at_k(RUNS, k):>9.3f} {precision_at_k(RUNS, k):>12.3f}")
    print(f"\nMRR = {mrr(RUNS):.3f}")

    for i, (ranked, gold) in enumerate(RUNS):
        hit = next((r for r, d in enumerate(ranked, 1) if d in gold), None)
        print(f"  run {i}: first relevant hit at rank {hit}, "
              f"reciprocal {0 if hit is None else round(1 / hit, 3)}")
    ```

    MRR is exactly 0.500: reciprocal ranks of 0.5, 0.5, 0 and 1.0. Note that
    recall@4 is 0.750, not 1.000 — run 2's relevant item was never retrieved,
    and no amount of reordering will produce it.

    That is the answer to the question. A reranker permutes the four results it
    was given, so **recall@4 cannot change** (the set is the same) but
    **recall@1, recall@2, precision@1 and MRR all can**, because they depend on
    position. This is why the two numbers are reported together: recall@k tells
    you whether retrieval found the answer, MRR tells you whether it put it
    near the top, and only the second one is a reranker's business.

---

### Exercise 29.5 — Design a memory schema for a personal assistant (●●)

A personal assistant hears the ten statements below. Decide which memory store
each belongs in — **working**, **episodic**, **semantic**, or **procedural** —
then implement a router that files each one, and print the resulting stores.
Give semantic memories a stable key so a later contradiction can overwrite
them.

```text
1.  "My name is Dara."
2.  "I'm vegetarian."
3.  "Book me a table for Friday at 8."
4.  "Last week you booked Trattoria Sole and I liked it."
5.  "Actually, make that Saturday."
6.  "When I ask for a restaurant, always check it has vegetarian options first."
7.  "My sister's birthday is on 3 March."
8.  "What was that place called again?"
9.  "I've moved to Lisbon."
10. "I'm vegan now, not vegetarian."
```

??? success "Solution"

    ```python
    STATEMENTS = [
        "My name is Dara.",
        "I'm vegetarian.",
        "Book me a table for Friday at 8.",
        "Last week you booked Trattoria Sole and I liked it.",
        "Actually, make that Saturday.",
        "When I ask for a restaurant, always check it has vegetarian options first.",
        "My sister's birthday is on 3 March.",
        "What was that place called again?",
        "I've moved to Lisbon.",
        "I'm vegan now, not vegetarian.",
    ]

    # (matching substring, store, semantic key or None, importance)
    ROUTES = [
        ("my name is",        "semantic",   "user.name",        0.95),
        ("vegetarian options", "procedural", "rule.restaurant",  0.90),
        ("i'm vegetarian",    "semantic",   "user.diet",        0.90),
        ("i'm vegan",         "semantic",   "user.diet",        0.90),
        ("moved to",          "semantic",   "user.city",        0.90),
        ("birthday",          "semantic",   "contact.sister.birthday", 0.80),
        ("last week",         "episodic",   None,               0.60),
    ]

    class Memory:
        def __init__(self):
            self.working, self.episodic = [], []
            self.semantic, self.procedural = {}, {}
            self.log = []

        def route(self, text):
            low = text.lower()
            for needle, store, key, importance in ROUTES:
                if needle in low:
                    return store, key, importance
            return "working", None, 0.3        # default: it is just this turn

        def file(self, text):
            store, key, importance = self.route(text)
            if store in ("semantic", "procedural"):
                target = self.semantic if store == "semantic" else self.procedural
                old = target.get(key)
                target[key] = {"text": text, "importance": importance,
                               "superseded": old["text"] if old else None}
                verdict = "UPDATED " if old else "new     "
            else:
                (self.episodic if store == "episodic" else self.working).append(text)
                verdict = "appended"
            self.log.append((store, key, verdict, text))
            return store

    mem = Memory()
    for s in STATEMENTS:
        mem.file(s)

    for store, key, verdict, text in mem.log:
        print(f"{store:<11} {str(key):<26} {verdict}  {text[:44]}")

    print("\nsemantic store:")
    for key, rec in sorted(mem.semantic.items()):
        extra = f"   (was: {rec['superseded']!r})" if rec["superseded"] else ""
        print(f"  {key:<26} {rec['text']}{extra}")
    print("\nprocedural store:")
    for key, rec in mem.procedural.items():
        print(f"  {key:<26} {rec['text']}")
    print(f"\nworking: {len(mem.working)} turns, episodic: {len(mem.episodic)}")
    ```

    The interesting rows are 2 and 10. Both are diet statements, both map to
    the key `user.diet`, and the second **supersedes** the first — the store
    prints `(was: "I'm vegetarian.")` so the change is auditable rather than
    silent. Statements 3, 5 and 8 stay in working memory: a table booking for
    Friday, its correction to Saturday, and a question about "that place" are
    all about *this* conversation and will be worthless next month. Statement 6
    is procedural because it is a *rule for how to act*, not a fact about the
    world, and it belongs in the system prompt on every future call. Statement
    4 is episodic — a specific past event, useful when recalled but not worth
    permanent prompt space.

    Note that the router is a substring table, which is a caricature: a real
    assistant asks a model "does this statement contain a durable fact about
    the user? Return JSON." The *schema* — four stores, keys for the
    overwritable ones, importance on every row — is the part that transfers.

---

### Exercise 29.6 — Fit a context into 4000 tokens (●●)

You have a system prompt, a tool block, twelve retrieved chunks with relevance
scores, and thirty conversation turns. Altogether they are far more than 4000
tokens. Build the context under that hard budget, following the rules from
[Section 29.3](03-agent-memory.md): stable material first, spend at most 60% of
the budget on retrieved chunks, fill the rest with the most recent turns, and
leave 40 tokens of headroom. Print a budget report showing what got in and what
was dropped.

??? success "Solution"

    ```python
    def tok(text):
        return [text[i:i + 4] for i in range(0, len(text), 4)]

    def n_tokens(text):
        return len(tok(text))

    SYSTEM = ("You are a helpful assistant for the ACME support desk. "
              "Answer only from the policy excerpts provided. "
              "Cite them by number. ") * 12
    TOOLS = ("TOOL lookup_order(id) -> order | "
             "TOOL start_refund(id, reason) -> ticket | "
             "TOOL escalate(id, note) -> case ") * 6
    RETRIEVED = [(round(0.92 - 0.05 * i, 2),
                  f"[{i}] Policy excerpt {i}. "
                  + "Refunds are handled by the finance team under policy 7. " * 12)
                 for i in range(12)]
    TURNS = [f"{'User' if i % 2 == 0 else 'Assistant'}: turn {i}. "
             + "We went back and forth about the order status here. " * 9
             for i in range(30)]

    BUDGET, CHUNK_SHARE, HEADROOM = 4000, 0.60, 40

    def build_context(budget=BUDGET):
        blocks = [("system", SYSTEM), ("tools", TOOLS)]     # stable prefix first
        used = sum(n_tokens(t) for _, t in blocks)
        if used > budget * CHUNK_SHARE:
            raise ValueError("the stable prefix alone exceeds the chunk share")

        chunks, dropped_chunks = [], 0
        for _, text in sorted(RETRIEVED, reverse=True):     # best score first
            if used + n_tokens(text) > budget * CHUNK_SHARE:
                dropped_chunks += 1
                continue
            chunks.append(text)
            used += n_tokens(text)

        window, dropped_turns = [], 0
        for text in reversed(TURNS):                        # newest first
            if used + n_tokens(text) > budget - HEADROOM:
                dropped_turns = len(TURNS) - len(window)
                break
            window.append(text)
            used += n_tokens(text)
        window.reverse()                                    # back to chronological

        parts = [t for _, t in blocks] + chunks + window
        context = "\n".join(parts)
        while n_tokens(context) > budget and window:        # newlines cost tokens
            window.pop(0)
            dropped_turns += 1
            context = "\n".join([t for _, t in blocks] + chunks + window)
        return context, chunks, window, dropped_chunks, dropped_turns

    context, chunks, window, dc, dt = build_context()
    supply = (n_tokens(SYSTEM) + n_tokens(TOOLS)
              + sum(n_tokens(t) for _, t in RETRIEVED)
              + sum(n_tokens(t) for t in TURNS))

    print(f"material available     {supply:>6} tokens")
    print(f"budget                 {BUDGET:>6} tokens\n")
    print(f"  system + tools       {n_tokens(SYSTEM) + n_tokens(TOOLS):>6}")
    print(f"  {len(chunks):>2}/12 chunks kept     {sum(n_tokens(t) for t in chunks):>6}"
          f"   ({dc} dropped, lowest-scoring)")
    print(f"  {len(window):>2}/30 turns kept      {sum(n_tokens(t) for t in window):>6}"
          f"   ({dt} dropped, oldest)")
    print(f"  assembled context    {n_tokens(context):>6}"
          f"   headroom {BUDGET - n_tokens(context)}")
    assert n_tokens(context) <= BUDGET
    ```

    6263 tokens of material go in and 3849 come out, keeping 10 of 12 chunks
    and the 13 most recent turns. Three details are the exercise. **Order:**
    system and tools go first so a prefix cache can reuse them
    ([Section 27.1](../ch27-inference/01-kv-cache.md)); the volatile turns go
    last. **What gets dropped:** chunks are dropped from the *bottom of the
    relevance ranking*, turns from the *oldest end* — two different notions of
    "least valuable", which is exactly why they are budgeted separately.
    **The final loop:** measuring the parts is an estimate; the joined string
    is the truth, so we trim until the real count fits and assert it.

---

### Exercise 29.7 — Extract triples from text (●●)

Write a rule-based extractor that turns these six sentences into
`(subject, relation, object)` triples, resolving the obvious aliases, and
prints the entity list. One of the sentences states no relation between two
things — your extractor must produce nothing for it rather than inventing
something.

```text
"Dr Okafor leads the materials group."
"The materials group uses the Helios diffractometer."
"The Helios diffractometer sits in Building C."
"Building C is managed by facilities."
"Priya reports to Dr Okafor."
"The weather has been unusually mild."
```

??? success "Solution"

    ```python
    import re

    SENTENCES = [
        "Dr Okafor leads the materials group.",
        "The materials group uses the Helios diffractometer.",
        "The Helios diffractometer sits in Building C.",
        "Building C is managed by facilities.",
        "Priya reports to Dr Okafor.",
        "The weather has been unusually mild.",
    ]

    # (pattern, relation, flip) — flip=True for passive phrasings like "is managed by"
    RULES = [
        (r"^(?:The )?(.+?) leads (?:the )?(.+?)\.?$", "leads", False),
        (r"^(?:The )?(.+?) uses (?:the )?(.+?)\.?$", "uses", False),
        (r"^(?:The )?(.+?) sits in (?:the )?(.+?)\.?$", "located_in", False),
        (r"^(?:The )?(.+?) is managed by (?:the )?(.+?)\.?$", "manages", True),
        (r"^(?:The )?(.+?) reports to (?:the )?(.+?)\.?$", "reports_to", False),
    ]
    ALIAS = {"materials group": "Materials Group",
             "Helios diffractometer": "Helios"}

    def canonical(name):
        name = name.strip()
        return ALIAS.get(name, name)

    def extract(sentences):
        triples = []
        for i, sentence in enumerate(sentences):
            for pattern, relation, flip in RULES:
                m = re.match(pattern, sentence)
                if not m:
                    continue
                a, b = canonical(m.group(1)), canonical(m.group(2))
                triples.append((b, relation, a, i) if flip else (a, relation, b, i))
                break
            else:
                print(f"  no relation found in sentence {i}: {sentence!r}")
        return triples

    TRIPLES = extract(SENTENCES)
    print()
    for s, r, o, src in TRIPLES:
        print(f"  ({s!r}, {r!r}, {o!r})   from sentence {src}")

    entities = sorted({s for s, _, _, _ in TRIPLES} | {o for _, _, o, _ in TRIPLES})
    print(f"\n{len(TRIPLES)} triples, {len(entities)} entities: {entities}")
    print("\nrelation vocabulary used:", sorted({r for _, r, _, _ in TRIPLES}))
    ```

    Five triples, six entities, and sentence 5 correctly yields nothing — an
    extractor that always finds *something* is worse than useless, because a
    fabricated edge is indistinguishable from a real one once it is in the
    graph. Two design points are worth naming. The `flip` column turns the
    passive *"Building C is managed by facilities"* into the active triple
    `("facilities", "manages", "Building C")`, so one relation type covers both
    phrasings instead of two half-empty ones. And `ALIAS` normalizes
    `"Helios diffractometer"` and `"materials group"` — without it the graph
    would contain near-duplicate nodes that never connect.

---

### Exercise 29.8 — A three-hop graph query, with the path explained (●●●)

Build the graph below, then implement `paths(start, goal, max_hops)` that
returns **every simple path** (no repeated node) of at most `max_hops` edges,
ignoring edge direction. Use it to answer *"how is Rosa connected to the
Postgres cluster?"* with `max_hops=3`, printing each path as a numbered chain
of labelled relations plus the ids of the source notes that justify it. Then
print a plain-English explanation of the shortest path.

```text
NOTES = [
    "Rosa maintains the Atlas ingestion service.",     # 0
    "Atlas writes to the vector store.",               # 1
    "Atlas reads from the staging bucket.",            # 2
    "The vector store runs on the Postgres cluster.",  # 3
    "Priya maintains the Beacon search API.",          # 4
    "Beacon queries the vector store.",                # 5
    "Ivan maintains the Cinder billing job.",          # 6
    "Cinder reads from the Postgres cluster.",         # 7
    "Sam administers the Postgres cluster.",           # 8
    "The staging bucket runs on the Postgres cluster.",# 9
]
```

*Hint:* depth-first recursion ([Section 17.1](../ch17-recursion/01-call-stack.md))
carrying the path so far is the natural shape; a set of visited nodes on the
current path is what makes the paths *simple*.

??? success "Solution"

    ```python
    import re

    NOTES = [
        "Rosa maintains the Atlas ingestion service.",
        "Atlas writes to the vector store.",
        "Atlas reads from the staging bucket.",
        "The vector store runs on the Postgres cluster.",
        "Priya maintains the Beacon search API.",
        "Beacon queries the vector store.",
        "Ivan maintains the Cinder billing job.",
        "Cinder reads from the Postgres cluster.",
        "Sam administers the Postgres cluster.",
        "The staging bucket runs on the Postgres cluster.",
    ]
    RULES = [
        (r"^(.+?) maintains (?:the )?(.+?)\.?$", "maintains"),
        (r"^(.+?) administers (?:the )?(.+?)\.?$", "administers"),
        (r"^(?:The )?(.+?) writes to (?:the )?(.+?)\.?$", "writes_to"),
        (r"^(?:The )?(.+?) reads from (?:the )?(.+?)\.?$", "reads_from"),
        (r"^(?:The )?(.+?) runs on (?:the )?(.+?)\.?$", "runs_on"),
        (r"^(?:The )?(.+?) queries (?:the )?(.+?)\.?$", "queries"),
    ]
    ALIAS = {"Atlas ingestion service": "Atlas", "Beacon search API": "Beacon",
             "Cinder billing job": "Cinder"}

    def canonical(n):
        return ALIAS.get(n.strip(), n.strip())

    TRIPLES = []
    for note_id, note in enumerate(NOTES):
        for pattern, relation in RULES:
            m = re.match(pattern, note)
            if m:
                TRIPLES.append((canonical(m.group(1)), relation,
                                canonical(m.group(2)), note_id))
                break

    edges = {}          # node -> list of (neighbour, label, note id)
    for s, r, o, note_id in TRIPLES:
        edges.setdefault(s, []).append((o, f"{s} --{r}--> {o}", note_id))
        edges.setdefault(o, []).append((s, f"{s} --{r}--> {o}", note_id))

    def paths(start, goal, max_hops):
        """Every simple path from start to goal using at most max_hops edges."""
        found = []

        def walk(node, trail, visited):
            if node == goal and trail:
                found.append(list(trail))
                return                      # a simple path stops at the goal
            if len(trail) == max_hops:
                return
            for nxt, label, note_id in edges.get(node, []):
                if nxt in visited:
                    continue
                trail.append((label, note_id))
                walk(nxt, trail, visited | {nxt})
                trail.pop()

        walk(start, [], {start})
        return sorted(found, key=len)

    START, GOAL = "Rosa", "Postgres cluster"
    results = paths(START, GOAL, max_hops=3)
    print(f"{len(results)} path(s) from {START!r} to {GOAL!r} within 3 hops\n")
    for n, trail in enumerate(results, start=1):
        cites = sorted({note_id for _, note_id in trail})
        print(f"path {n} ({len(trail)} hops), sources {cites}")
        for step, (label, note_id) in enumerate(trail, start=1):
            print(f"   {step}. {label:<44} [note {note_id}]")

    shortest = results[0]
    reasons = " and ".join(NOTES[note_id].rstrip(".") for _, note_id in shortest)
    print(f"\nExplanation ({len(shortest)} hops): {START} is connected to {GOAL} "
          f"because {reasons}.")
    ```

    Two paths of three hops each, through the vector store and through the
    staging bucket, and both are printed with the notes that justify every
    single edge. That trail is the reason to bother with a graph at all: a
    vector retriever asked "how is Rosa connected to the Postgres cluster?"
    would return the notes containing *Postgres*, none of which mention Rosa,
    and would offer no way to say *why* any answer follows.

    Three implementation details are worth studying. The `visited` set is
    passed *by value* into the recursive call while `trail` is mutated and
    popped — the standard backtracking pattern from
    [Section 17.1](../ch17-recursion/01-call-stack.md), and the reason no path
    revisits a node. The `return` after appending a found path is what makes
    the paths simple in the useful sense: once you have arrived, walking
    onwards and coming back would only produce longer paths through the same
    place. And the edge list stores each relation label *once*, in its original
    direction, even though the edge is walked both ways — so the printed
    explanation still says `vector store --runs_on--> Postgres cluster` rather
    than inventing a backwards relation that nobody wrote down.
