# 26.2 Embeddings and attention

Section 26.1 left you with a list of integers. Integers are useless on their
own — token 40 is not "twice" token 20 — so the first thing a model does is
turn every ID into a **vector**, and then let those vectors *look at each
other*. That looking-at-each-other is **attention**, the idea that made
modern language models possible. This section builds it from nothing: a
vector, a dot product, a softmax, a matrix multiply. By the end you will
have computed a real attention matrix by hand, in numpy, and be able to read
it. Nothing here is a metaphor — it is the actual arithmetic.

## Vectors, and why a token becomes one

A **vector** is just a fixed-length list of numbers, e.g. `[0.9, 0.0, 0.0,
0.3]`. That is all. The number of slots is the **dimension** (here 4; real
models use 2,048–16,384). A vector is useful because each slot can carry a
different aspect of meaning, and because vectors can be compared with
arithmetic instead of string matching.

The **embedding matrix** is the lookup table that turns token IDs into
vectors: one row per vocabulary entry. Getting a token's vector is literally
indexing a row. Below the four columns have been given human-readable
meanings so you can see what is happening — in a real model these columns
are learned from data and nobody labels them.

```python
import numpy as np

vocab = ["the", "cat", "chased", "a", "kitten"]
#                    animal  action  determiner  small
E = np.array([[0.0,   0.0,    1.0,       0.0],   # 0 the
              [0.9,   0.0,    0.0,       0.3],   # 1 cat
              [0.0,   1.0,    0.0,       0.0],   # 2 chased
              [0.0,   0.0,    0.9,       0.0],   # 3 a
              [0.9,   0.0,    0.0,       0.9]])  # 4 kitten

token_ids = [0, 1, 2, 3, 4]          # "the cat chased a kitten"
X = E[token_ids]                     # <- the whole embedding step: row lookup
print("embedding matrix shape:", E.shape, "(vocab_size, d_model)")
print("sequence shape        :", X.shape, "(n_tokens, d_model)")
print("vector for 'kitten'   :", E[4])
```

`X` is now a $5 \times 4$ block of numbers: five tokens, four dimensions
each. Everything from here on is arithmetic on that block.

### Similar words, similar vectors

Two vectors point in similar directions when their **cosine similarity** is
near 1:

$$
\cos(\mathbf{a}, \mathbf{b}) =
\frac{\mathbf{a} \cdot \mathbf{b}}{\lVert \mathbf{a} \rVert \, \lVert \mathbf{b} \rVert},
\qquad
\mathbf{a} \cdot \mathbf{b} = \sum_{i} a_i b_i
$$

The numerator is the **dot product** — multiply matching slots, add them up.
The denominator divides out length, leaving only direction.

```python
# continues
def cosine(a, b):
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))

pairs = [("cat", "kitten"), ("cat", "chased"), ("the", "a"), ("kitten", "a")]
for w1, w2 in pairs:
    a, b = E[vocab.index(w1)], E[vocab.index(w2)]
    print(f"cos({w1:>6}, {w2:<6}) = {cosine(a, b):+.3f}")
```

`cat` and `kitten` score $+0.894$ — they share the *animal* direction.
`cat` and `chased` score exactly $0.000$: their vectors have no dimension in
common, so they are unrelated. `the` and `a` score $+1.000$: as far as this
tiny model is concerned they are interchangeable. That is the whole point of
embeddings — meaning becomes geometry, and "related" becomes "points the
same way".

## The dot product is a similarity meter

Before attention, get comfortable with the one operation it is built from.
For vectors of equal length, $\mathbf{a} \cdot \mathbf{b} = \lVert
\mathbf{a}\rVert \lVert \mathbf{b}\rVert \cos\theta$ — so with fixed
lengths, the dot product *is* alignment:

```python
import numpy as np

a = np.array([1.0, 0.0])                      # points along the x-axis
for degrees in [0, 45, 90, 135, 180]:
    t = np.radians(degrees)
    b = np.array([np.cos(t), np.sin(t)])      # unit vector at this angle
    print(f"angle {degrees:>3}deg   b = [{b[0]:+.2f}, {b[1]:+.2f}]   "
          f"a . b = {a @ b:+.2f}")
```

Same direction, dot product $+1$. Perpendicular, $0$. Opposite, $-1$. When a
model asks "how much should token 3 care about token 1?", it computes a dot
product. That is the entire scoring mechanism.

## Attention, one step at a time

Here is the formula the rest of this section unpacks. It is from *Attention
Is All You Need* (Vaswani et al., 2017), and it is the beating heart of
every LLM you have used:

$$
\operatorname{Attention}(Q, K, V) =
\operatorname{softmax}\!\left(\frac{QK^{\top}}{\sqrt{d_k}}\right) V
$$

The idea in one sentence: **every token builds a query saying what it is
looking for, every token builds a key advertising what it offers, we match
queries against keys with dot products, turn the matches into weights, and
each token's output becomes a weighted blend of the other tokens' values.**

### Step 1 — Q, K, V projections

Each token's embedding is multiplied by three learned matrices to produce
three different views of itself: a **query** ($Q$), a **key** ($K$), and a
**value** ($V$). The weights below are random because our model is untrained
— the *shapes and arithmetic* are exactly a real model's.

```python
# continues
rng = np.random.default_rng(0)
d_model = 4
W_q = rng.normal(0, 0.5, size=(d_model, d_model))
W_k = rng.normal(0, 0.5, size=(d_model, d_model))
W_v = rng.normal(0, 0.5, size=(d_model, d_model))

Q = X @ W_q          # (5, 4) — one query per token
K = X @ W_k          # (5, 4) — one key per token
V = X @ W_v          # (5, 4) — one value per token
print("X shape:", X.shape, " Q/K/V shapes:", Q.shape, K.shape, V.shape)
print("\nquery vector of token 1 ('cat'):", np.round(Q[1], 3))
print("key   vector of token 4 ('kitten'):", np.round(K[4], 3))
```

Three matrices, three views. Note that no token has looked at any other yet
— every row was computed independently. That is the next step.

### Step 2 — scores: every query against every key

$QK^{\top}$ is an $n \times n$ table: entry $(i, j)$ is the dot product of
token $i$'s query with token $j$'s key, i.e. *how much token $i$ finds token
$j$ relevant*.

```python
# continues
scores = Q @ K.T
print("scores shape:", scores.shape, "(one row per token, one column per token)")
print("\n      " + "".join(f"{w:>9}" for w in vocab))
for i, w in enumerate(vocab):
    print(f"{w:>6}" + "".join(f"{s:>9.3f}" for s in scores[i]))
```

Read row `cat`: those five numbers are how relevant `cat` finds each token
including itself. They are meaningless right now (random weights), but the
*structure* is the real thing. Notice also the cost: $n$ tokens produce
$n^2$ scores. Double the context, quadruple this table — the reason long
contexts are expensive.

### Step 3 — why divide by $\sqrt{d_k}$

Dot products of $d_k$-dimensional random vectors have a standard deviation
that grows like $\sqrt{d_k}$. Feed big numbers into softmax and it saturates:
one token gets essentially all the weight and the rest get zero, which
destroys learning. Dividing by $\sqrt{d_k}$ keeps the spread around 1
regardless of dimension.

```python
import numpy as np

def softmax(v):
    e = np.exp(v - v.max())          # subtract max: avoids overflow, same result
    return e / e.sum()

rng = np.random.default_rng(1)
for d_k in [4, 64, 512]:
    q = rng.normal(size=d_k)
    k = rng.normal(size=(6, d_k))
    raw = k @ q
    print(f"d_k={d_k:>4}  raw scores std {raw.std():>6.2f}  "
          f"max softmax weight: unscaled {softmax(raw).max():.3f}  "
          f"scaled {softmax(raw / np.sqrt(d_k)).max():.3f}")
```

At $d_k = 4$ scaling barely matters. At $d_k = 512$ the raw scores have a
spread of about 17, and the unscaled softmax puts essentially *all* the
weight on one token — it prints as `1.000`, a hard spike with no gradient
left to learn from. Scaled by $\sqrt{d_k}$, the very same scores give a
soft distribution peaking at 0.377. One `/ np.sqrt(d_k)` is the whole
difference.

### Step 4 — softmax turns scores into weights

**Softmax** converts any list of numbers into positive numbers that sum to
1, preserving order and exaggerating differences:

$$
\operatorname{softmax}(z)_i = \frac{e^{z_i}}{\sum_j e^{z_j}}
$$

```python
# continues
def softmax(v):
    e = np.exp(v - v.max())
    return e / e.sum()

d_k = d_model
A = np.array([softmax(row / np.sqrt(d_k)) for row in scores])   # attention weights

print("row sums (must all be 1):", np.round(A.sum(axis=1), 6))
print("\n      " + "".join(f"{w:>9}" for w in vocab))
for i, w in enumerate(vocab):
    print(f"{w:>6}" + "".join(f"{a:>9.3f}" for a in A[i]))
print("\n'chased' pays most attention to:", vocab[int(A[2].argmax())])
```

Every row sums to 1: each token distributes exactly 100% of its attention
across the sequence. That matrix `A` — five rows of five weights — *is* the
attention pattern.

### Step 5 — the weighted sum of values

Finally, each token's output is the blend of every token's value vector,
weighted by that row of `A`:

```python
# continues
out = A @ V
print("output shape:", out.shape, "(same shape as the input X)")
print("\noutput for 'chased':", np.round(out[2], 3))

# the same row, computed by hand as an explicit weighted sum
manual = sum(A[2, j] * V[j] for j in range(len(vocab)))
print("hand-computed      :", np.round(manual, 3))
print("identical:", np.allclose(out[2], manual))
```

That is attention, complete. Input: five vectors that knew nothing about
each other. Output: five vectors, each a mixture of the whole sequence,
mixed according to learned relevance. Stack this operation dozens of times
(Section 26.3) and you have a language model.

## Seeing the pattern

Numbers in a grid are hard to read; a heatmap is not. Bright means "this
row's token attends strongly to this column's token".

```python
# continues
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(4.2, 3.6))
im = ax.imshow(A, cmap="viridis", vmin=0, vmax=A.max())
ax.set_xticks(range(len(vocab)), vocab, rotation=45)
ax.set_yticks(range(len(vocab)), vocab)
ax.set_xlabel("attended to (keys)")
ax.set_ylabel("attending from (queries)")
ax.set_title("Attention weights (untrained, random weights)")
for i in range(len(vocab)):
    for j in range(len(vocab)):
        ax.text(j, i, f"{A[i, j]:.2f}", ha="center", va="center",
                color="white" if A[i, j] < 0.5 else "black", fontsize=8)
fig.colorbar(im, ax=ax, shrink=0.8)
fig.tight_layout()
```

This is the picture you will see in every interpretability paper. In a
trained model these rows are startlingly meaningful: pronouns light up on
the noun they refer to, closing brackets light up on their opening bracket,
and the last token of a sentence gathers from everything relevant.

## Causal masking: no peeking at the future

A decoder-only model is trained to predict the next token. If token 2 could
see token 3, the answer would be sitting right there in the input and the
model would learn nothing. So before the softmax we set every "future"
score to $-\infty$; $e^{-\infty} = 0$, so those weights vanish and each row
renormalises over the past only.

```python
# continues
n = len(vocab)
mask = np.triu(np.ones((n, n), dtype=bool), k=1)     # True strictly above diagonal
masked_scores = np.where(mask, -np.inf, scores)

A_causal = np.array([softmax(row / np.sqrt(d_k)) for row in masked_scores])

print("masked scores (row 'chased'):", np.round(masked_scores[2], 2))
print("\ncausal attention weights")
print("      " + "".join(f"{w:>9}" for w in vocab))
for i, w in enumerate(vocab):
    print(f"{w:>6}" + "".join(f"{a:>9.3f}" for a in A_causal[i]))
print("\nrow sums:", np.round(A_causal.sum(axis=1), 6))
print("first token can only see itself:", np.round(A_causal[0], 3))
```

The result is lower-triangular: token 0 attends only to itself (weight
1.000), token 1 to tokens 0–1, and so on. This one line of masking is what
makes the model *causal* — and it is also what makes the **KV cache** of
[Section 26.3](03-decoder-stack.md) possible: because token 2 never looks at
token 3, token 2's key and value never change once computed, so they can be
stored and reused instead of recalculated.

## Multi-head attention: several relationships at once

One attention pattern per layer would be a bottleneck — a token often needs
to track several relationships simultaneously ("what noun am I about?",
"what verb governs me?"). So the model runs $h$ smaller attention
computations in parallel — **heads** — each with its own $Q/K/V$ matrices
projecting into $d_{\text{head}} = d_{\text{model}} / h$ dimensions, then
concatenates their outputs and mixes them with an output matrix $W_O$.

To show what "each head learns a different relationship" actually means, we
hand-build two heads instead of using random weights. Head A projects onto
the *animal* and *small* features, so it matches things by meaning. Head B
is wired so that every query looks for the *action* feature, so every token
that can see the verb attends to it.

```python
# continues
h, d_head = 2, d_model // 2

# Head A: "who is like me?"  — keeps the animal (0) and small (3) dimensions
Wq_A = Wk_A = np.array([[1.0, 0.0], [0.0, 0.0], [0.0, 0.0], [0.0, 1.0]])
# Head B: "where is the verb?" — every query asks for the action dim (1)
Wq_B = np.array([[0.0, 1.0]] * d_model)
Wk_B = np.array([[0.0, 0.0], [0.0, 1.0], [0.0, 0.0], [0.0, 0.0]])

def head(Xin, Wq, Wk, Wv):
    q, k, v = Xin @ Wq, Xin @ Wk, Xin @ Wv
    s = np.where(mask, -np.inf, q @ k.T) / np.sqrt(Wq.shape[1])
    weights = np.array([softmax(r) for r in s])
    return weights, weights @ v

Wv_A = rng.normal(0, 0.5, size=(d_model, d_head))
Wv_B = rng.normal(0, 0.5, size=(d_model, d_head))
A_A, out_A = head(X, Wq_A, Wk_A, Wv_A)
A_B, out_B = head(X, Wq_B, Wk_B, Wv_B)

print("head A ('similar meaning') — 'kitten' attends to:",
      {vocab[j]: round(float(A_A[4, j]), 2) for j in range(n)})
print("head B ('find the verb')   — 'kitten' attends to:",
      {vocab[j]: round(float(A_B[4, j]), 2) for j in range(n)})

concat = np.concatenate([out_A, out_B], axis=1)   # (5, 2) + (5, 2) -> (5, 4)
W_o = rng.normal(0, 0.5, size=(d_model, d_model))
multi_out = concat @ W_o
print("\nconcatenated heads:", concat.shape, "-> after W_o:", multi_out.shape)
```

Same input, same layer, two completely different attention patterns. Head A
spreads `kitten`'s attention over the two *animal* words — itself (0.38) and
`cat` (0.26) — while the three non-animal tokens split the rest evenly at
0.12 each. Head B ignores meaning entirely and dumps 0.47 on `chased`.
Neither head was told to do that by a human in a real model —
training discovers such roles, and interpretability researchers have found
and named recurring ones ("previous-token heads", "induction heads"). The
concatenate-then-project step is what lets the layer use both answers at
once, and the output shape is unchanged, which is why these blocks stack.

!!! warning "Common mistakes"
    - **Thinking attention "understands" words.** It computes dot products
      between learned vectors. Meaning is a *consequence* of training, not
      something in the mechanism.
    - **Forgetting the mask.** An unmasked decoder trivially "predicts" the
      next token by reading it, gets near-zero training loss, and generates
      garbage at inference time.
    - **Dropping the $\sqrt{d_k}$.** Everything still runs; the softmax
      just saturates and gradients die. Silent bugs like this are the norm
      in ML — nothing crashes, the model just fails to learn.
    - **Mixing up the axes.** In $QK^{\top}$, rows are queries (who is
      looking) and columns are keys (who is being looked at). Transposing
      by accident produces plausible-looking, entirely wrong heatmaps.
    - **Assuming heads see the full width.** Each head works in
      $d_{\text{model}}/h$ dimensions; the *concatenation* restores the
      width. Total compute is roughly the same as one big head.

## Check your understanding

1. Why can the attention scores be computed for all token pairs in one
   matrix multiply, but a recurrent network must process tokens one at a
   time?

    ??? success "Answer"

        Because every query and key is computed from its own token
        independently, so $QK^{\top}$ is one big matrix product with no
        sequential dependency. That parallelism — not accuracy alone — is
        why transformers displaced RNNs: they use a GPU fully during
        training.

2. A sequence has 1,000 tokens. How many entries does the attention score
   matrix have? At 4,000 tokens?

    ??? success "Answer"

        $1000^2 = 1{,}000{,}000$ and $4000^2 = 16{,}000{,}000$. Four times
        the tokens, sixteen times the score entries — attention is
        $O(n^2)$ in sequence length, which is exactly the pressure behind
        FlashAttention and the long-context tricks of Section 26.3.

3. What would happen if we masked the *past* instead of the future?

    ??? success "Answer"

        Each token could only see itself and later tokens — the reverse of
        causal order. The model could no longer be used for left-to-right
        generation, since at inference time future tokens do not exist yet.
        (Encoder models like BERT use *no* mask at all, which is why they
        read whole sentences but do not generate text this way.)

4. Every row of the attention matrix sums to 1. Do the columns sum to 1 too?
   What does a large column sum mean?

    ??? success "Answer"

        No — columns can sum to anything from 0 to $n$. A large column sum
        means many tokens are attending to that one token: it is acting as
        a hub of information for the sequence.
