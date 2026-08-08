# 29.1 Embeddings and vector search

Every retrieval system starts with the same question: *given a query, which
stored items are relevant?* For fifty years the answer was "the ones
containing the query's words", and that answer breaks the moment a user writes
"automobile" and the document says "car".

This section builds the modern answer from scratch — meaning as a *direction in
space*, similarity as an angle, and search as a numerical operation — and then
makes it fast. Comparing a query against ten million vectors one at a time is
exactly the kind of $O(n)$ problem
[Section 16.1](../ch16-complexity/01-big-o.md) taught you to be suspicious of.

## Where keyword search gives up

Here is the whole problem in twelve lines. We store four sentences and search
them the obvious way: a document matches if it literally contains the query
word.

```python
docs = [
    "The automobile industry is shifting to electric drivetrains.",
    "She parked her car outside the library.",
    "The recipe calls for two cups of flour.",
    "Motor vehicles must be inspected every two years.",
]

def keyword_search(query, docs):
    """Return indexes of documents containing the query word."""
    hits = []
    for i, d in enumerate(docs):
        words = d.lower().replace(".", "").split()
        if query.lower() in words:
            hits.append(i)
    return hits

for q in ["car", "automobile", "vehicle"]:
    print(f"query {q!r:14} -> documents {keyword_search(q, docs)}")
```

Three queries that a human would call *the same question* return three
disjoint answers: `car` finds only document 1, `automobile` only document 0,
and `vehicle` finds **nothing at all** — even though document 3 is about
vehicles, using the plural. Keyword search matches **strings**, and strings
are not meanings.

You could patch this with a synonym list. People did, for decades. The list is
never finished: "EV", "motorcar", "ride", "wheels", "Fahrzeug". What we want
instead is a representation in which "car" and "automobile" *are already close
together*, without anyone writing the pair down.

## Meaning as a direction: a hand-made embedding space

!!! abstract "In plain words"

    - **What it is.** An embedding turns a piece of text into a *point in
      space*, chosen so that texts with similar meaning land close together.
    - **Picture it.** Imagine a library where books are shelved not by title
      but by *what they are about*: everything about cars ends up in the same
      corner, whether its spine reads "automobile", "vehicle", or "motorcar".
      The shelf position *is* the meaning.
    - **Why it matters.** Keyword search matches letters, so to it "automobile"
      and "car" look as unrelated as "automobile" and "avocado". Embeddings put
      synonyms next to each other *by construction*, so "close together" finally
      means "similar in meaning" — with no synonym list to maintain.

An **embedding** is a list of numbers — a vector — assigned to a piece of text
so that similar meanings get similar vectors. That is the entire definition.
The magic is in *how* the numbers are chosen, but you do not need magic to
understand the idea: you can assign them by hand.

Below is a three-dimensional space where we decided, by hand, what each axis
means: how *alive* a thing is, how *machine-like* it is, and how *edible* it
is. Every word gets a coordinate on each axis.

```python
import numpy as np
import matplotlib.pyplot as plt

# axes: (alive-ness, machine-ness, edible-ness) — hand-assigned, no model
SPACE = {
    "dog":        [0.95, 0.05, 0.10],
    "cat":        [0.92, 0.04, 0.06],
    "horse":      [0.90, 0.20, 0.15],
    "salmon":     [0.65, 0.03, 0.70],
    "car":        [0.05, 0.95, 0.03],
    "automobile": [0.04, 0.96, 0.02],
    "truck":      [0.06, 0.93, 0.05],
    "bicycle":    [0.12, 0.72, 0.02],
    "bread":      [0.08, 0.02, 0.92],
    "apple":      [0.30, 0.02, 0.88],
    "pizza":      [0.03, 0.04, 0.95],
    "soup":       [0.05, 0.03, 0.90],
}

fig = plt.figure(figsize=(7, 6))
ax = fig.add_subplot(111, projection="3d")
groups = {
    "animals": ["dog", "cat", "horse", "salmon"],
    "vehicles": ["car", "automobile", "truck", "bicycle"],
    "foods": ["bread", "apple", "pizza", "soup"],
}
for name, words in groups.items():
    pts = np.array([SPACE[w] for w in words])
    ax.scatter(pts[:, 0], pts[:, 1], pts[:, 2], s=70, label=name)
    for w in words:
        x, y, z = SPACE[w]
        ax.text(x, y, z + 0.04, w, fontsize=8)

ax.set_xlabel("alive-ness")
ax.set_ylabel("machine-ness")
ax.set_zlabel("edible-ness")
ax.set_title("A hand-made 3-dimensional embedding space")
ax.legend(loc="upper left")
```

Three clusters appear, and they appear *because of the coordinates*, not
because we labelled them — the labels are only there so you can read the plot.
Notice `salmon`: it floats between the animals and the foods, which is exactly
right, and exactly the kind of nuance a synonym list cannot express.

!!! note "Toy scale, real idea"

    Three hand-chosen axes is toy. A real embedding has hundreds or thousands
    of axes and nobody chooses what they mean — a neural network does, by
    being trained on enormous amounts of text. But "meaning is a location, and
    similar meanings are nearby locations" is the whole idea, and it is
    already fully present in these twelve points.

## Cosine similarity: comparing directions, not positions

!!! abstract "In plain words"

    - **What it is.** Cosine similarity scores how alike two vectors are by the
      *angle* between them — pointing the same way scores 1, at right angles
      scores 0 — and ignores how long each one is.
    - **Picture it.** Two people pointing at the same distant mountain are
      "aligned" even if one has a longer arm; what matters is the *direction*,
      not the reach. A five-page essay and a one-line note on the same topic
      point the same way, and cosine calls them similar even though one vector
      is far bigger.
    - **Why it matters.** Once each vector is scaled to length 1, cosine reduces
      to a single [**dot product**](../part5-math-primer.md) — multiply matching
      entries and add them up — so the whole of retrieval becomes one cheap
      multiply per document.

To *use* the space we need a number for "how similar are these two vectors?".
The standard answer in retrieval is **cosine similarity**: the cosine of the
angle between the two vectors.

$$
\cos\theta \;=\; \frac{\mathbf{a}\cdot\mathbf{b}}{\lVert\mathbf{a}\rVert\,\lVert\mathbf{b}\rVert}
\qquad\text{where}\qquad
\mathbf{a}\cdot\mathbf{b}=\sum_{i} a_i b_i,
\quad
\lVert\mathbf{a}\rVert=\sqrt{\sum_i a_i^2}
$$

The symbols, named:

| Symbol | Meaning |
| --- | --- |
| $\mathbf{a}, \mathbf{b}$ | the two vectors being compared |
| $\mathbf{a}\cdot\mathbf{b}$ | their **dot product** — multiply matching entries, add the results |
| $\lVert\mathbf{a}\rVert$ | the **length** (norm) of $\mathbf{a}$ — Pythagoras in $d$ dimensions |
| $\theta$ | the angle between the two vectors |

Read the formula in two steps, because that is how it is implemented:

1. **Normalize.** Divide each vector by its own length, producing a *unit
   vector* — same direction, length exactly 1.
2. **Dot product.** Multiply the two unit vectors element-wise and add up.

The result lies in $[-1, 1]$:

| Cosine | Means |
| --- | --- |
| $1$ | same direction — as similar as the metric can say |
| $0$ | at right angles: unrelated |
| $-1$ | opposite directions |

(Embeddings with only non-negative coordinates, like our toy space, can never
actually reach $-1$.)

```python
import numpy as np

SPACE = {
    "dog": [0.95, 0.05, 0.10], "cat": [0.92, 0.04, 0.06],
    "salmon": [0.65, 0.03, 0.70], "car": [0.05, 0.95, 0.03],
    "automobile": [0.04, 0.96, 0.02], "truck": [0.06, 0.93, 0.05],
    "bicycle": [0.12, 0.72, 0.02], "bread": [0.08, 0.02, 0.92],
    "apple": [0.30, 0.02, 0.88], "pizza": [0.03, 0.04, 0.95],
}

def normalize(v):
    """Scale a vector to length 1 (a 'unit vector')."""
    v = np.asarray(v, dtype=float)
    length = np.sqrt(np.sum(v * v))       # == np.linalg.norm(v)
    return v / length

def cosine(a, b):
    return float(normalize(a) @ normalize(b))   # @ is the dot product

pairs = [("car", "automobile"), ("car", "truck"), ("car", "bicycle"),
         ("car", "dog"), ("car", "pizza"),
         ("bread", "pizza"), ("apple", "bread"),
         ("salmon", "cat"), ("salmon", "pizza")]
for a, b in pairs:
    print(f"cos({a:>10}, {b:<11}) = {cosine(SPACE[a], SPACE[b]):.4f}")
```

The synonym problem is solved *by construction*: `car` and `automobile` score
**0.9999**, and nobody wrote a synonym rule. `car` and `truck` score 0.9997,
`car` and `dog` only 0.1076. And `salmon` sits at 0.7270 from `cat` and
0.7542 from `pizza` — genuinely, measurably between two clusters.

### Why not Euclidean distance?

Euclidean distance $\lVert \mathbf{a}-\mathbf{b}\rVert$ measures how far apart
two points are; cosine measures whether they *point the same way*. They
disagree whenever one vector is longer than the other — which, for text, is
exactly what happens when one document is longer than another.

```python
import numpy as np

def cosine(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))

def euclidean(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    return float(np.linalg.norm(a - b))

short = np.array([1.0, 2.0, 1.0])     # a one-line note about a topic
longer = np.array([5.0, 10.0, 5.0])   # a five-paragraph essay, same topic
other = np.array([2.0, 1.0, 0.0])     # a short note about something else

for name, v in [("same topic, longer", longer), ("different topic", other)]:
    print(f"{name:20} cosine={cosine(short, v): .3f}"
          f"   euclidean={euclidean(short, v): .3f}")
```

Euclidean distance calls the *same-topic* document (9.798) more than five
times farther away than the *unrelated* one (1.732), purely because it is
longer. Cosine gives the same-topic pair 1.000 and the unrelated pair 0.730 —
it ignores length and gets it right. That is why retrieval systems default to
cosine, or, equivalently, to a plain dot product on vectors that were
normalized once at insert time.

Note the corollary. Once every vector has length 1,
$\lVert a-b\rVert^{2} = 2 - 2\cos\theta$, so Euclidean distance and cosine rank
*identically*. The disagreement above is entirely a disagreement about length.

!!! tip "Normalize once, not every query"

    On unit vectors, cosine similarity *is* the dot product. Production
    indexes normalize every vector as it is stored, then use dot products
    forever after: one `@` per comparison instead of a dot product plus two
    square roots.

## An index you can actually build offline: TF-IDF

Hand-assigning coordinates does not scale past a blackboard. Before neural
embeddings existed, information retrieval used a computable recipe that turns
any document into a vector — and it is still the backbone of half of
production search.

### The recipe: counts, weighted by rarity

Start from a **bag of words**: one dimension per vocabulary word, and the value
is how often that word occurs. Order is thrown away — hence "bag".

Raw counts are dominated by "the" and "of", so we weight each count by how
*rare* the word is across the corpus:

$$
\text{tf-idf}(w, d) \;=\; \underbrace{\text{count of } w \text{ in } d}_{\text{term frequency}}
\;\times\; \underbrace{\left(\ln\frac{1+N}{1+\text{df}(w)} + 1\right)}_{\text{inverse document frequency}}
$$

Two symbols to name:

| Symbol | Meaning |
| --- | --- |
| $N$ | how many documents there are in total |
| $\text{df}(w)$ | the **document frequency** of $w$ — how many documents contain it at least once |

The second factor is the clever half. A word appearing in every document gets a
weight near 1, while a rare word gets a large one. **Rare words carry the
signal.**

```python
import re
import numpy as np

CORPUS = [
    "Electric cars store energy in a large lithium battery pack.",
    "Battery range drops noticeably in very cold winter weather.",
    "A petrol engine burns fuel and wastes most of it as heat.",
    "Charging a battery at home overnight is cheaper than a fast charger.",
    "Sourdough bread needs a starter culture of wild yeast.",
    "Bread dough rises because yeast produces carbon dioxide gas.",
    "Cold weather slows down yeast, so dough rises much more slowly.",
    "A hot oven sets the crust of the bread in the first ten minutes.",
    "Python lists store references to objects, not the objects themselves.",
    "A dictionary looks up a key in constant time using a hash.",
    "Sorting a list of one million items takes a fraction of a second.",
    "Reading a large file line by line keeps memory usage small.",
]

def tokenize(text):
    return re.findall(r"[a-z]+", text.lower())

vocab = sorted({w for doc in CORPUS for w in tokenize(doc)})
column = {w: i for i, w in enumerate(vocab)}
N = len(CORPUS)

doc_freq = np.zeros(len(vocab))
for doc in CORPUS:
    for w in set(tokenize(doc)):        # set(): count each document once
        doc_freq[column[w]] += 1
idf = np.log((1 + N) / (1 + doc_freq)) + 1.0

def vectorize(text):
    v = np.zeros(len(vocab))
    for w in tokenize(text):
        if w in column:
            v[column[w]] += 1.0         # term frequency
    v *= idf                            # weight by rarity
    length = np.linalg.norm(v)
    return v / length if length > 0 else v   # normalize -> cosine == dot

INDEX = np.stack([vectorize(d) for d in CORPUS])
print("index shape (documents x vocabulary):", INDEX.shape)
print("idf of 'a':", round(float(idf[column["a"]]), 3),
      "  idf of 'lithium':", round(float(idf[column["lithium"]]), 3))

def search(query, k=3):
    q = vectorize(query)
    scores = INDEX @ q                  # one dot product per document
    order = np.argsort(-scores)[:k]
    return [(int(i), float(scores[i])) for i in order]

for query in ["cold weather battery", "why does dough rise", "automobile"]:
    print(f"\nquery: {query!r}")
    for rank, (i, s) in enumerate(search(query), start=1):
        print(f"  {rank}. score={s:.4f}  {CORPUS[i]}")
```

The index is a $12 \times 96$ matrix: twelve documents, ninety-six vocabulary
words. The word `a` sits in 8 of the 12 sentences and earns an idf of
**1.368**; `lithium` sits in exactly one and earns **2.872**, more than twice
the weight. (A word present in *every* document would score exactly 1.0.)

That is a working search engine, ranked by cosine similarity. `'cold weather
battery'` puts the cold-battery sentence first at 0.5224 and the cold-yeast
sentence second at 0.3338 — reasonable.

### Where lexical vectors run out

Read the other two queries in the output and you will see both of TF-IDF's
limits:

- `'why does dough rise'` ranks the dough sentences first — but only because
  of the word *dough*. The query word `rise` never matches the document word
  `rises`; TF-IDF compares exact strings. (Classic search engines patch this
  with **stemming**, chopping words back to a common root.)
- `'automobile'` scores **0.0000** on every single document. The word is not
  in the vocabulary, so its vector is all zeros, so every dot product is zero.
  The ranking you see is just `argsort` breaking a twelve-way tie.

TF-IDF gives you the *machinery* of vector search — vectors, normalization,
dot products, top-$k$ — with none of the semantics. Real embeddings keep the
machinery and replace the vectorizer.

## Where real embeddings come from

An embedding model is a neural network — usually a transformer encoder, the
same family of machinery you built in
[Section 26.2](../ch26-llm-internals/02-attention.md). Using one is three
steps:

1. **Feed it text.** The text is tokenized exactly as in
   [Section 26.1](../ch26-llm-internals/01-tokenization.md).
2. **Read out one hidden-state vector per token.** That is one vector per
   *token*, not yet one per document.
3. **Pool.** A **pooling** step collapses those into a single vector for the
   whole text — mean-pooling across tokens, or the hidden state of one special
   leading token.

Training is what makes the geometry mean something: it pushes vectors of texts
that *should* match toward each other and everything else apart. Nobody chooses
what an axis means, and after training nobody can say.

Practical facts worth memorising:

| Question | Answer |
| --- | --- |
| How many dimensions? | Typically **384 to 3072**. Small open models are often 384; many API models are 1536; the largest are 3072. |
| Is bigger better? | Slightly better quality, linearly more storage and search cost. Most systems do fine in the 384–1024 range. |
| Can two models be mixed? | **No.** Vectors from two different models live in unrelated spaces; cosine between them is noise. Re-embed *everything* when you switch models. |
| Normalize? | Yes, once, at insert time. Some models emit unit vectors already — check rather than assume. |
| What does it cost? | Far less than generation: one forward pass over the text, no token-by-token decoding. Batch it. |
| Symmetric or asymmetric? | Many models want a prefix such as `"query: "` versus `"passage: "`. Using the wrong one silently degrades recall. |

Calling one looks like the sketch below — and because it needs a network, it
gets no Run button:

```text
# Conceptual shape of an embedding API call (not runnable here)
vectors = embed(model="some-embedding-model",
                input=["Electric cars store energy in a battery pack.",
                       "Bread dough rises because yeast makes gas."])
len(vectors)      -> 2
len(vectors[0])   -> 1536      # this model's dimension
```

Everything else on this page — cosine, top-$k$, indexing, fusion — works
identically whether the vectors came from a trained model or from our
hand-made table. That is why we can teach all of it offline.

## Brute force, and why it eventually stops working

Our `search` did one dot product per document. With $n$ documents of $d$
dimensions each that is $O(n \cdot d)$ arithmetic per query, plus $O(n \log n)$
to sort the scores — or $O(n \log k)$ if you keep the best $k$ in a heap, the
trick from [Section 21.2](../ch21-heaps/02-priority-queues.md).

At $n = 12$ that is instant. At $n = 50{,}000{,}000$ and $d = 1536$ it is
roughly $7.7 \times 10^{10}$ multiply-adds *per query*, which no amount of
numpy will make interactive.

The escape is the same trade you have made since
[Section 16.1](../ch16-complexity/01-big-o.md) — spend memory and
preprocessing to buy query time — with one new twist: **we also give up
*exactness*.** **Approximate nearest neighbour** (ANN) indexes return *almost
always the right* top-$k$, orders of magnitude faster.

The metric for "almost always" is **recall@k**: of the $k$ true nearest
neighbours, what fraction did we actually return?

!!! abstract "In plain words"

    - **What it is.** A vector index (an ANN index) organises the stored vectors
      ahead of time so that a query only has to compare itself against a
      promising *neighbourhood*, not against all ten million documents.
    - **Picture it.** To find the nearest coffee shop you do not measure the
      distance to every café on Earth — you look in your own neighbourhood
      first. An index pre-sorts the documents into neighbourhoods so the search
      can do the same.
    - **Why it matters.** Checking every vector is $O(n)$ and dies at scale;
      checking one neighbourhood is orders of magnitude faster. The catch is
      that a true match sitting just over the neighbourhood's edge can be
      missed. That near-miss risk is the price — measured as *recall* — and
      every index gives you a knob to trade speed against it.

### Two families of index

**IVF (inverted file)** clusters the vectors once, with k-means, and keeps one
list per cluster. At query time you compare the query against the few hundred
*centroids*, then scan only the closest one or two lists.

Search cost drops by roughly the number of clusters — until the centroid scan
itself starts to dominate, which happens once the cluster count approaches
$\sqrt{n}$. The tunable knob is `nprobe`: how many lists to scan.

**HNSW (hierarchical navigable small world)** builds a *graph* — the structure
of [Section 37.1](../ch37-graphs/01-representations.md) — in which every
vector is a vertex linked to a handful of near neighbours, plus a few
long-range "express" links, arranged in layers.

Searching it is greedy walking: start at an entry point, repeatedly hop to
whichever neighbour is closer to the query, drop a layer, repeat. The
long-range links are what keep the path short — the "small world" effect behind
six-degrees-of-separation.

| | Brute force (flat) | IVF | HNSW |
| --- | --- | --- | --- |
| **Structure** | none — one array of vectors | k-means clusters, one list each | layered proximity graph |
| **Query work** | every vector, $O(n \cdot d)$ | centroids, then `nprobe` lists | a greedy walk of a few hundred hops |
| **Exact?** | yes | no | no |
| **Recall knob** | — | `nprobe` (lists scanned) | `ef_search` (candidates kept) |
| **Build cost** | zero | one k-means pass | high — the graph is built incrementally |
| **Memory** | the vectors | vectors plus centroids | vectors plus the edge lists, noticeably more |
| **Updates** | trivial | fine, until clusters drift | awkward in bulk |
| **Use it when** | up to a few million vectors | large corpora, memory matters | you need the fastest search at high recall |

### A tiny IVF index, with the trade-off printed

Let us build the IVF idea for real: k-means on 2-D toy data, then search only
the nearest cluster or clusters. We count *how many vectors were compared*,
which is deterministic and therefore honest — a wall-clock number would depend
on your machine.

```python
import numpy as np

rng = np.random.default_rng(0)
CENTRES = np.array([[0., 0.], [6., 1.], [1., 7.], [7., 8.], [-5., 4.], [3., -6.]])
DATA = np.vstack([c + rng.normal(0, 1.0, size=(200, 2)) for c in CENTRES])  # 1200 pts
QUERIES = rng.uniform(-6, 9, size=(200, 2))
K = 5

def brute_force(q, k=K):
    d = np.linalg.norm(DATA - q, axis=1)
    return np.argsort(d)[:k]

def kmeans(data, n_clusters, iters=15, seed=1):
    """Lloyd's algorithm: assign to nearest centroid, move centroid to mean."""
    r = np.random.default_rng(seed)
    centroids = data[r.choice(len(data), n_clusters, replace=False)].copy()
    for _ in range(iters):
        dists = np.linalg.norm(data[:, None, :] - centroids[None, :, :], axis=2)
        assign = np.argmin(dists, axis=1)
        for c in range(n_clusters):
            members = data[assign == c]
            if len(members):
                centroids[c] = members.mean(axis=0)
    return centroids, assign

N_CLUSTERS = 8
centroids, assign = kmeans(DATA, N_CLUSTERS)
lists = {c: np.flatnonzero(assign == c) for c in range(N_CLUSTERS)}
print("cluster sizes:", [len(lists[c]) for c in range(N_CLUSTERS)])

def ivf_search(q, k=K, nprobe=1):
    centroid_d = np.linalg.norm(centroids - q, axis=1)
    probes = np.argsort(centroid_d)[:nprobe]
    candidates = np.concatenate([lists[int(c)] for c in probes])
    d = np.linalg.norm(DATA[candidates] - q, axis=1)
    compared = len(centroids) + len(candidates)     # centroids count too
    return candidates[np.argsort(d)[:k]], compared

for nprobe in (1, 2, 3):
    recalls, compares = [], []
    for q in QUERIES:
        truth = set(brute_force(q).tolist())
        got, compared = ivf_search(q, nprobe=nprobe)
        recalls.append(len(truth & set(got.tolist())) / K)
        compares.append(compared)
    mean_cmp = float(np.mean(compares))
    print(f"nprobe={nprobe}: recall@{K}={np.mean(recalls):.3f}  "
          f"vectors compared={mean_cmp:6.1f} (brute force: {len(DATA)})  "
          f"speedup={len(DATA) / mean_cmp:.1f}x")
```

There is the whole ANN bargain in three lines of output:

- **`nprobe=1`** compares 174.9 vectors instead of 1200 — **6.9× cheaper** —
  and finds **89.4%** of the true neighbours.
- **`nprobe=2`** lifts recall to 0.982, at 3.8×.
- **`nprobe=3`** finds all of them (recall 1.000) but saves only 2.5×.

The misses at `nprobe=1` are the queries that land near a cluster *boundary*,
where some true neighbours live on the other side of the line. Every ANN index
has a knob like this — `nprobe` for IVF, `ef_search` for HNSW — and tuning it
is tuning exactly this curve.

!!! warning "1200 vectors do not need an index"

    Brute force in numpy is a single matrix multiply, and it is *fast*. Reach
    for an ANN index when you have millions of vectors and a latency budget,
    not before. An exact search that is fast enough beats an approximate one
    you have to tune, monitor, and explain to the next engineer.

## The vector database landscape

You will rarely write the index yourself. What you choose between, as of
today's ecosystem — treat this as a snapshot, not a law, because the field
moves fast:

| System | What it is | Index types | Notes |
| --- | --- | --- | --- |
| **FAISS** | A *library* from Meta, not a server | Flat (exact), IVF, HNSW, PQ compression | The reference implementation many others build on. No metadata store, no persistence, no network API — you write those. |
| **Chroma** | Embedded, local-first database for Python and JS | HNSW | Easiest start: install it, no server to run. Good for prototypes and small apps. |
| **Qdrant** | Standalone server written in Rust | HNSW | Metadata ("payload") filtering integrated into the graph search; runs as one binary or managed. |
| **Milvus** | Distributed, cluster-scale system | IVF, HNSW, DiskANN, GPU indexes | Built for billions of vectors and horizontal scaling; heaviest to operate. |
| **pgvector** | An extension to PostgreSQL | IVFFlat, HNSW | Vectors live *in your existing database*: SQL joins, transactions, one backup story. Usually the pragmatic first choice if you already run Postgres. |

The honest summary: for anything under a few million vectors, pick whatever
sits closest to the database you already operate. The index is rarely the
interesting part of your system; the chunking and the evaluation are, and
those are [Section 29.2](02-rag-pipeline.md).

## Metadata filtering and hybrid search

Two features separate a demo from a product.

### Metadata filtering

**Metadata filtering** attaches structured fields to each vector — author,
date, language, tenant, permissions — and restricts search to matching rows.

It is not optional. In a multi-user system, "only search documents this user is
allowed to read" is a correctness requirement, not a feature.

There is one subtlety, and it is the thing to interrogate when you evaluate a
vector database — *when* the filter is applied:

- **Filter first, then search.** Can wreck the index's assumptions: the HNSW
  graph may have no path at all through the surviving vertices.
- **Search first, then filter.** Safe for the index, but may leave you with
  three results when you asked for ten.

### Hybrid search

**Hybrid search** runs two retrievers and merges them, because lexical and
semantic search fail in *different* directions:

- **Lexical search** — BM25, the industrial refinement of TF-IDF — is
  unbeatable on exact rare tokens: product codes, error numbers, surnames,
  function names.
- **Semantic search** is unbeatable on paraphrase, where the words differ and
  the meaning does not.

Below we run both. Our "semantic" retriever is a hand-built topic embedding — a
small lexicon mapping words onto three topic axes — which stands in for a real
model exactly the way our 3-D animal space did. The *fusion* code is what
matters, and it is identical in production.

```python
import re
import numpy as np

CORPUS = [
    "Electric cars store energy in a large lithium battery pack.",
    "Battery range drops noticeably in very cold winter weather.",
    "A petrol engine burns fuel and wastes most of it as heat.",
    "Charging a battery at home overnight is cheaper than a fast charger.",
    "Sourdough bread needs a starter culture of wild yeast.",
    "Bread dough rises because yeast produces carbon dioxide gas.",
    "Cold weather slows down yeast, so dough rises much more slowly.",
    "A hot oven sets the crust of the bread in the first ten minutes.",
    "The replacement battery pack, part number LFP-4820, ships in two weeks.",
]

def tokenize(t):
    return re.findall(r"[a-z0-9]+", t.lower())   # keep digits: part numbers matter

# ---- retriever A: BM25, the industrial refinement of TF-IDF ----------
TOKS = [tokenize(d) for d in CORPUS]
N = len(CORPUS)
avgdl = sum(len(t) for t in TOKS) / N
df = {}
for toks in TOKS:
    for w in set(toks):
        df[w] = df.get(w, 0) + 1

def bm25_scores(query, k1=1.5, b=0.75):
    out = []
    for toks in TOKS:
        s = 0.0
        for w in tokenize(query):
            f = toks.count(w)
            if w in df and f:
                idf = np.log((N - df[w] + 0.5) / (df[w] + 0.5) + 1)
                s += idf * f * (k1 + 1) / (f + k1 * (1 - b + b * len(toks) / avgdl))
        out.append(s)
    return np.array(out)

# ---- retriever B: a topic embedding, standing in for a real model ----
TOPICS = ["vehicle", "baking", "weather"]
LEXICON = {
    "vehicle": "car cars automobile automobiles vehicle vehicles engine petrol "
               "fuel battery charging charger lithium range pack".split(),
    "baking": "bread dough yeast sourdough oven crust starter loaf flour".split(),
    "weather": "cold winter weather hot freezing temperature snow".split(),
}
WORD_TOPIC = {}
for i, topic in enumerate(TOPICS):
    for w in LEXICON[topic]:
        WORD_TOPIC.setdefault(w, np.zeros(len(TOPICS)))[i] = 1.0

def embed(text):
    v = np.zeros(len(TOPICS))
    for w in tokenize(text):
        if w in WORD_TOPIC:
            v += WORD_TOPIC[w]
    n = np.linalg.norm(v)
    return v / n if n else v

EMB = np.stack([embed(d) for d in CORPUS])

def ranked(scores):
    """Documents best-first, dropping those with no evidence at all.

    Keeping zero-score documents would feed the fusion a meaningless tie
    order and let noise outvote a retriever that actually found something.
    """
    return [int(i) for i in np.argsort(-scores) if scores[i] > 0]

# ---- the merge: reciprocal rank fusion, about ten lines ---------------
def rrf(rankings, k=60):
    """Combine ranked lists using ranks only. Returns (order, scores)."""
    fused = {}
    for ranking in rankings:
        for rank, doc in enumerate(ranking, start=1):
            fused[doc] = fused.get(doc, 0.0) + 1.0 / (k + rank)
    return sorted(fused, key=lambda d: -fused[d]), fused

for query in ["automobile", "LFP-4820", "cold battery"]:
    lex_s, sem_s = bm25_scores(query), EMB @ embed(query)
    lex, sem = ranked(lex_s), ranked(sem_s)
    order, score = rrf([lex, sem])
    print(f"\nquery {query!r}")
    print(f"  BM25     top3 {str(lex[:3]):<12} best score {lex_s.max():.3f}")
    print(f"  semantic top3 {str(sem[:3]):<12} best score {sem_s.max():.3f}")
    for i in order[:3]:
        print(f"  fused rrf={score[i]:.4f}  {CORPUS[i]}")
```

Three queries, three regimes, and that is the entire argument for hybrid
search:

- `'automobile'` — BM25's best score is **0.000**. It has no lexical evidence
  whatsoever and returns an empty ranking. The topic embedding carries the
  query alone.
- `'LFP-4820'` — now the roles reverse. BM25 pins the exact rare token with a
  score of **3.628**; the topic embedding has never seen that string, returns
  the zero vector, and contributes nothing.
- `'cold battery'` — both fire, and disagree about second place. BM25 puts the
  *yeast* sentence second because "cold" is lexically strong there; the
  embedding puts the electric-car sentence second because it is about
  batteries. Fusion promotes the electric-car sentence (rrf 0.0320) above the
  yeast sentence (0.0313), which is the answer a human would have given.

### Reciprocal rank fusion

**Reciprocal rank fusion** (RRF) is the merge rule, and it is startlingly
simple:

$$
\text{RRF}(d) \;=\; \sum_{r \in \text{rankings}} \frac{1}{k + \text{rank}_r(d)},
\qquad k \approx 60
$$

In words: *for each ranked list, give the document one over sixty-plus-its-rank
points, and add the points up.* A document that is 1st in both lists scores
twice $1/61$; a document that appears in neither scores nothing.

| Symbol | Meaning |
| --- | --- |
| $d$ | one document, being scored |
| $\text{rank}_r(d)$ | where $d$ finished in ranked list $r$ — 1 for first place |
| $k$ | a damping constant, conventionally 60 |

**RRF uses only *ranks*, never scores, and that is the whole point.** BM25
scores are unbounded and depend on corpus statistics; cosine scores live in
$[-1, 1]$. Any attempt to add them requires a calibration that drifts the
moment you change a model.

Ranks are always comparable — being first means the same thing in both lists.
The constant $k$ damps the influence of the very top ranks, so a document
ranked 1st by one retriever and 40th by the other does not automatically win.

!!! warning "Common mistakes"

    - **Mixing embedding models.** Vectors from model A and model B are not
      comparable, even at the same dimension. If you re-embed with a new
      model, re-embed *everything* — a half-migrated index returns confident
      nonsense with no error message.
    - **Forgetting to normalize.** If you store raw vectors and compare with a
      dot product, long documents win every query simply for being long, as
      the Euclidean demo showed. Store unit vectors, or use a real cosine.
    - **Treating similarity scores as probabilities.** A cosine of 0.82 does
      not mean "82% relevant". Scores are meaningful only *relative to other
      scores from the same model on the same query*, which is why absolute
      thresholds like `score > 0.8` break the day you change models.
    - **Reaching for an ANN index too early.** Approximate search adds a recall
      knob you must tune and a failure mode you must monitor. Brute force over
      fifty thousand vectors is one matrix multiply and is almost certainly
      fast enough.
    - **Assuming semantic search subsumes keyword search.** It does not. Order
      numbers, function names, and rare identifiers are exactly where
      embeddings blur and BM25 shines — which is why hybrid retrieval is the
      default in serious systems.

## Check your understanding

1. Why does this handbook normalize vectors at insert time rather than at
   query time?

    ??? success "Answer"
        Because cosine similarity on unit vectors is just a dot product. If
        every stored vector already has length 1 and the query is normalized
        once, a search over $n$ documents is a single matrix–vector multiply
        with no per-document square roots. The mathematics is identical; the
        work is done once per document instead of once per document *per
        query*.

2. Our TF-IDF index scored 0.0000 on every document for the query
   `'automobile'`. Would a real embedding model have the same problem?

    ??? success "Answer"
        No. TF-IDF's dimensions *are* vocabulary words, so a word outside the
        vocabulary produces the zero vector and every dot product is zero. An
        embedding model has no vocabulary axis: it maps the text through a
        network into a dense space where "automobile" lands near "car"
        because the training data used them in similar contexts. The failure
        is structural to lexical vectors, not a bug in our implementation.

3. The IVF index with 8 clusters and `nprobe=1` gave recall@5 = 0.894. Where
   do the missing 10.6% come from, and name two ways to recover them.

    ??? success "Answer"
        From queries near a cluster *boundary*: some of their true nearest
        neighbours sit in the adjacent cluster, which `nprobe=1` never scans.
        Recover them by raising `nprobe` (probing three clusters gave recall
        1.000, at 2.5× rather than 6.9× speedup), or by using fewer, larger
        clusters so that fewer neighbourhoods straddle a boundary. Both trade
        speed for recall — the only currency ANN indexes deal in.

4. Why does reciprocal rank fusion combine ranks instead of scores?

    ??? success "Answer"
        Because scores from different retrievers are on incomparable scales —
        BM25 is unbounded and depends on corpus statistics, cosine is bounded
        in $[-1,1]$ — so adding or averaging them needs a calibration that
        breaks whenever a model or corpus changes. Ranks are scale-free:
        being 1st means the same thing in both lists. RRF costs about ten
        lines and needs no tuning beyond the constant $k$.
