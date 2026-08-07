# Chapter 26 · Exercises

Eight problems, easiest first. Attempt each one before opening the solution
— especially Exercise 26.2, which asks you to *predict* an output, and
Exercise 26.8, which asks you to extend working code rather than read it.
Every solution is a complete runnable block; the arithmetic ones print the
numbers so you can check your paper answer against the machine's.

### Exercise 26.1 — BPE by hand, then verified (●)

Take this corpus, where each word appears the number of times shown:

```text
sun    x4        sunny  x2        run    x3
runner x1        fun    x3
```

Following the byte-pair-encoding rules from
[Section 26.1](01-tokenization.md) — every word starts split into single
characters with `_` marking the end of the word, and each step merges the
single most frequent adjacent pair across the whole corpus — work out the
**first three merges** on paper, with their counts. Then run the trainer and
check yourself.

??? success "Solution"

    Count every adjacent pair, weighted by word frequency.

    **Merge 1.** `u + n` appears in *every* word: $4 + 2 + 3 + 1 + 3 = 13$
    times, more than `n + _` ($4 + 3 + 3 = 10$) or `s + u` ($6$). So
    `un` is born.

    **Merge 2.** The words are now `s un _`, `s un n y _`, `r un _`,
    `r un n e r _`, `f un _`. The pair `un + _` occurs in `sun_`, `run_`,
    and `fun_`: $4 + 3 + 3 = 10$, beating `s + un` ($6$). So `un_` — the
    whole ending "-un" of a word — becomes one symbol.

    **Merge 3.** Now `s + un_` occurs 4 times (in `sun_`), which beats
    `r + un_` ($3$), `f + un_` ($3$), and `un + n` ($3$). So `sun_` becomes
    a single token: the tokenizer has learned the whole word.

    ```python
    from collections import Counter

    CORPUS = "sun sun sun sun sunny sunny run run run runner fun fun fun"

    def symbols(word):
        return tuple(list(word) + ["_"])

    def pair_counts(vocab):
        counts = Counter()
        for syms, freq in vocab.items():
            for pair in zip(syms, syms[1:]):
                counts[pair] += freq
        return counts

    def merge_pair(vocab, pair):
        out = {}
        for syms, freq in vocab.items():
            new, i = [], 0
            while i < len(syms):
                if i + 1 < len(syms) and (syms[i], syms[i + 1]) == pair:
                    new.append(syms[i] + syms[i + 1])
                    i += 2
                else:
                    new.append(syms[i])
                    i += 1
            out[tuple(new)] = freq
        return out

    vocab = {symbols(w): f for w, f in Counter(CORPUS.split()).items()}
    for step in range(1, 4):
        counts = pair_counts(vocab)
        pair = min(counts.items(), key=lambda kv: (-kv[1], kv[0]))[0]
        print(f"merge {step}: {pair[0]} + {pair[1]:<4} -> "
              f"{pair[0] + pair[1]:<6} (seen {counts[pair]}x)")
        vocab = merge_pair(vocab, pair)

    print("\nwords after three merges:")
    for syms, freq in vocab.items():
        print(f"   x{freq}  {list(syms)}")
    ```

    Notice the shape of what was learned: a shared suffix first, then a
    whole common word. Nobody supplied a dictionary — frequency did all of
    it.

### Exercise 26.2 — Predict the attention weights (●)

**Do not run this yet.** Below is a causal attention step on three tokens.
The scores have already been divided by $\sqrt{d_k}$, and the mask has
already been applied. Write down, on paper, (a) the full $3 \times 3$
weight matrix `A` after softmax and (b) the three output vectors `A @ V`.

```text
scores =  [[ 4.0,  -inf,  -inf],
           [ 0.0,   0.0,  -inf],
           [ 2.0,   2.0,   2.0]]

V      =  [[1.0, 0.0],
           [0.0, 1.0],
           [1.0, 1.0]]
```

Then run the block to check.

??? success "Solution"

    The trick is that softmax only cares about *differences*, so any row of
    equal finite values comes out uniform, and $e^{-\infty} = 0$ removes the
    masked entries entirely.

    - Row 0: only one live entry, so it takes all the weight — `[1, 0, 0]`.
      The first token can attend only to itself, whatever its score was.
    - Row 1: two equal live entries — `[0.5, 0.5, 0]`.
    - Row 2: three equal entries — `[1/3, 1/3, 1/3]`, about `0.333` each.

    The outputs follow: row 0 is $V_0 = [1, 0]$; row 1 is the midpoint of
    $V_0$ and $V_1$, $[0.5, 0.5]$; row 2 averages all three, giving
    $[2/3, 2/3] \approx [0.667, 0.667]$.

    ```python
    import numpy as np

    scores = np.array([[4.0, -np.inf, -np.inf],
                       [0.0,     0.0, -np.inf],
                       [2.0,     2.0,     2.0]])
    V = np.array([[1.0, 0.0],
                  [0.0, 1.0],
                  [1.0, 1.0]])

    def softmax(z):
        e = np.exp(z - z.max(axis=-1, keepdims=True))
        return e / e.sum(axis=-1, keepdims=True)

    A = softmax(scores)
    print("attention weights:\n", np.round(A, 3))
    print("\nrow sums:", np.round(A.sum(axis=1), 6))
    print("\noutputs A @ V:\n", np.round(A @ V, 3))
    ```

    The lesson worth keeping: the *absolute* size of a score never matters,
    only its gap from the other scores in the same row. A row of all-4.0s
    and a row of all-0.0s produce identical attention.

### Exercise 26.3 — Implement causal masked attention (●●)

Write a function `causal_attention(X, Wq, Wk, Wv)` that performs one head of
masked self-attention and returns `(weights, output)`. It must build $Q$,
$K$, $V$, score with $QK^{\top}$, divide by $\sqrt{d_k}$, mask the strict
upper triangle to $-\infty$, softmax each row, and return the weighted sum
of $V$. Then prove it is correct with three checks: every row of `weights`
sums to 1, the strict upper triangle is exactly 0, and row 0 of the output
equals $V_0$.

??? success "Solution"

    ```python
    import numpy as np

    def softmax_rows(z):
        e = np.exp(z - z.max(axis=-1, keepdims=True))
        return e / e.sum(axis=-1, keepdims=True)

    def causal_attention(X, Wq, Wk, Wv):
        n = X.shape[0]
        Q, K, V = X @ Wq, X @ Wk, X @ Wv
        d_k = Q.shape[1]
        scores = Q @ K.T / np.sqrt(d_k)
        mask = np.triu(np.ones((n, n), dtype=bool), k=1)   # strictly above diagonal
        weights = softmax_rows(np.where(mask, -np.inf, scores))
        return weights, weights @ V

    rng = np.random.default_rng(4)
    n, d = 6, 4
    X = rng.normal(size=(n, d))
    Wq, Wk, Wv = (rng.normal(0, 0.5, size=(d, d)) for _ in range(3))

    A, out = causal_attention(X, Wq, Wk, Wv)
    print("attention weights:\n", np.round(A, 3))

    upper = np.triu(A, k=1)
    print("\ncheck 1 — every row sums to 1 :", np.allclose(A.sum(axis=1), 1.0))
    print("check 2 — upper triangle is 0 :", np.all(upper == 0.0),
          f"(largest value there: {upper.max():.1e})")
    print("check 3 — row 0 output == V[0]:",
          np.allclose(out[0], X[0] @ Wv))
    ```

    Check 3 is the one that proves the mask really works: token 0 has
    nothing in its past, so its entire output must be its own value vector,
    untouched by the other five tokens.

### Exercise 26.4 — RMSNorm versus LayerNorm (●●)

Most current models replaced LayerNorm with **RMSNorm**, which skips the
mean subtraction entirely:

$$
\operatorname{RMSNorm}(x) = \gamma \odot \frac{x}{\sqrt{\frac{1}{d}\sum_i x_i^2 + \epsilon}}
$$

Implement it, then answer with code: for which kind of input do RMSNorm and
LayerNorm agree, and for which do they differ? Also count the parameters
each one needs.

??? success "Solution"

    ```python
    import numpy as np

    def layer_norm(x, gamma, beta, eps=1e-5):
        mu = x.mean(axis=-1, keepdims=True)
        var = x.var(axis=-1, keepdims=True)
        return gamma * (x - mu) / np.sqrt(var + eps) + beta

    def rms_norm(x, gamma, eps=1e-5):
        rms = np.sqrt((x ** 2).mean(axis=-1, keepdims=True) + eps)
        return gamma * x / rms

    d = 4
    gamma, beta = np.ones(d), np.zeros(d)
    centred = np.array([2.0, -1.0, -3.0, 2.0])       # mean is exactly 0
    shifted = centred + 10.0                          # same shape, mean 10

    for name, x in [("mean 0 ", centred), ("mean 10", shifted)]:
        ln = layer_norm(x, gamma, beta)
        rn = rms_norm(x, gamma)
        print(f"{name}  LN: {np.round(ln, 3)}")
        print(f"{name}  RMS:{np.round(rn, 3)}   same? "
              f"{np.allclose(ln, rn, atol=1e-3)}")

    print(f"\nLayerNorm parameters per layer: {2 * d}  (gamma and beta)")
    print(f"RMSNorm   parameters per layer: {d}    (gamma only)")
    ```

    They agree whenever the input already has mean 0, because then
    subtracting the mean does nothing and the variance equals the mean
    square. They diverge as soon as the input has an offset: LayerNorm
    removes it, RMSNorm keeps it. Modern models get away with the cheaper
    version because the residual stream stays roughly centred anyway — and
    RMSNorm saves one pass over the data plus half the parameters.

### Exercise 26.5 — Parameter arithmetic for a 70B model (●●)

A model has 80 layers, $d_{\text{model}} = 8192$, $d_{\text{ff}} = 28672$, a
32,000-token vocabulary, 64 query heads, 8 key/value heads (GQA), a gated
(three-matrix) feed-forward, and separate input and output embeddings. Using
the per-block formula from [Section 26.3](03-decoder-stack.md):

1. How many parameters does one block hold, and what fraction is
   feed-forward?
2. What is the total parameter count?
3. At fp16 (2 bytes per parameter), does it fit on one 80 GiB GPU? What
   about 8-bit and 4-bit?

??? success "Solution"

    ```python
    def block_params(d_model, d_ff, n_heads, n_kv_heads, gated=True):
        d_head = d_model // n_heads
        attn = 2 * d_model * d_model + 2 * d_model * (n_kv_heads * d_head)
        mlp = (3 if gated else 2) * d_model * d_ff
        norms = 2 * d_model
        return attn, mlp, norms

    L, d_model, d_ff, vocab = 80, 8192, 28672, 32000
    attn, mlp, norms = block_params(d_model, d_ff, 64, 8)
    per_block = attn + mlp + norms
    total = 2 * vocab * d_model + L * per_block + d_model   # in + out + final norm

    print(f"attention per block : {attn:>15,}")
    print(f"feed-forward        : {mlp:>15,}  ({mlp / per_block:.0%} of the block)")
    print(f"norms               : {norms:>15,}")
    print(f"per block           : {per_block:>15,}")
    print(f"total               : {total:>15,}  (~{total / 1e9:.0f} billion)\n")

    print(f"{'precision':<12}{'bytes/param':>12}{'weights':>12}{'fits in 80 GiB?':>18}")
    for name, nbytes in [("fp16", 2), ("int8", 1), ("int4", 0.5)]:
        gib = total * nbytes / 2 ** 30
        print(f"{name:<12}{nbytes:>12}{gib:>9.1f} GiB{str(gib < 80):>18}")
    ```

    Three things to take away. The feed-forward holds 82% of every block —
    attention is where the ideas are, the FFN is where the parameters are.
    The total, 68,976,648,192, is what "70B" rounds to; you can now derive
    that number from a config file instead of trusting a label. And the
    memory table is the whole reason quantization exists: the same weights
    need 128.5 GiB in fp16 (two 80 GiB GPUs, minimum) but 32.1 GiB in 4-bit,
    which fits on one card with room left over for the KV cache.

### Exercise 26.6 — How many users fit on one GPU? (●●)

Same model as Exercise 26.5: 80 layers, 8 KV heads, head dimension 128,
fp16 cache. Using

$$
\text{bytes} = 2 \times L \times H_{kv} \times d_{\text{head}} \times
n_{\text{tokens}} \times b
$$

compute (a) the KV-cache bytes for **one token**, (b) the cache for one
8,192-token conversation, and (c) how many such conversations fit
simultaneously on an 80 GiB GPU if the weights are stored in 8-bit. Then
say what changes if the model used plain MHA with 64 KV heads.

??? success "Solution"

    ```python
    def kv_bytes(layers, n_kv_heads, d_head, n_tokens, bytes_per_number=2):
        return 2 * layers * n_kv_heads * d_head * n_tokens * bytes_per_number

    L, d_head, seq = 80, 128, 8192
    total_params = 68_976_648_192
    weights_gib = total_params * 1 / 2 ** 30          # int8

    print(f"weights (int8): {weights_gib:.1f} GiB of the 80 GiB card")
    free_gib = 80 - weights_gib
    print(f"free for cache: {free_gib:.1f} GiB\n")

    print(f"{'scheme':<6}{'KV heads':>9}{'per token':>12}{'per 8k seq':>13}"
          f"{'concurrent':>12}")
    for scheme, n_kv in [("GQA", 8), ("MHA", 64)]:
        per_token = kv_bytes(L, n_kv, d_head, 1)
        per_seq = kv_bytes(L, n_kv, d_head, seq)
        concurrent = int(free_gib * 2 ** 30 // per_seq)
        print(f"{scheme:<6}{n_kv:>9}{per_token / 2**10:>9.0f} KiB"
              f"{per_seq / 2**30:>10.2f} GiB{concurrent:>12}")
    ```

    With GQA the cache costs 320 KiB per token and 2.5 GiB per full-length
    conversation, so about six users share the card. Plain MHA would cost
    eight times as much — 20 GiB per conversation — and *no* full-length
    conversation would fit alongside the weights at all. That ratio, not
    model quality, is why grouped-query attention became standard: it is the
    difference between serving several users per GPU and serving none.

### Exercise 26.7 — Tune the sampler to hit a target (●●)

Using the toy model from [Section 26.4](04-sampling.md), the target is
**reliable stopping**: at least 80% of 200 seeded runs should emit `<eos>`
within 18 tokens. Sweep the temperature over `[0.5, 0.8, 1.0, 1.3, 1.6]` at
`top_p=0.9`, print the stop rate for each, and report the smallest
temperature that hits the target. Explain *why* low temperature fails.

??? success "Solution"

    ```python
    import numpy as np

    VOCAB = ["<bos>", "the", "cat", "sat", "on", "mat",
             "and", "a", "dog", "ran", "fast", "<eos>"]
    STOI = {t: i for i, t in enumerate(VOCAB)}
    TABLE = {
        "<bos>": {"the": 3.0, "a": 2.0},
        "the":   {"cat": 3.0, "mat": 2.5, "dog": 2.0},
        "cat":   {"sat": 3.0, "ran": 2.0},
        "sat":   {"on": 3.5},
        "on":    {"the": 3.5, "a": 2.0},
        "mat":   {"and": 2.5, "<eos>": 2.0},
        "and":   {"the": 3.0, "a": 2.0},
        "a":     {"dog": 3.0, "cat": 2.5},
        "dog":   {"ran": 3.0, "sat": 2.0},
        "ran":   {"fast": 3.0, "<eos>": 1.5},
        "fast":  {"and": 2.5, "<eos>": 2.8},
        "<eos>": {"<eos>": 5.0},
    }

    def next_logits(token):
        z = np.full(len(VOCAB), -6.0)
        for tok, score in TABLE[token].items():
            z[STOI[tok]] = score
        return z

    def softmax(z):
        e = np.exp(z - z.max())
        return e / e.sum()

    def top_p_filter(z, p_threshold):
        probs = softmax(z)
        order = np.argsort(-probs)
        n_keep = int(np.searchsorted(np.cumsum(probs[order]), p_threshold) + 1)
        keep = set(order[:n_keep].tolist())
        return np.array([zi if j in keep else -np.inf for j, zi in enumerate(z)])

    def run(seed, T, top_p=0.9, max_new=18):
        rng = np.random.default_rng(seed)
        out = ["<bos>"]
        for _ in range(max_new):
            z = top_p_filter(next_logits(out[-1]) / T, top_p)
            out.append(VOCAB[int(rng.choice(len(VOCAB), p=softmax(z)))])
            if out[-1] == "<eos>":
                break
        return out

    print(f"{'T':>5}{'stop rate':>12}{'avg length':>12}{'target':>9}")
    for T in [0.5, 0.8, 1.0, 1.3, 1.6]:
        runs = [run(s, T) for s in range(200)]
        stopped = np.mean([r[-1] == "<eos>" for r in runs])
        length = np.mean([len(r) for r in runs])
        print(f"{T:>5.1f}{stopped:>11.0%}{length:>12.1f}"
              f"{'  hit' if stopped >= 0.80 else '  miss':>9}")
    ```

    $T = 1.0$ is the smallest temperature on the list that reaches the
    target (82%); $T = 0.8$ misses at 79% and $T = 0.5$ manages only 55%.
    The reason is structural rather than statistical: `<eos>` is never the
    top-scoring token anywhere in the table, so a low temperature crushes
    its probability towards zero and the run gets trapped in the
    `the → cat → sat → on` cycle until it hits the token limit. Raising the
    temperature is not making the model "more creative" here — it is the
    only thing giving the stop token a realistic chance of being drawn.

### Exercise 26.8 — Add a second attention head (●●●)

Here is a working **single-head** causal attention layer. Extend it to a
general `multi_head(X, n_heads)` that splits $d = 8$ into `n_heads` heads of
width $d / n_{\text{heads}}$, runs attention independently in each,
concatenates the results, and projects with `Wo`. Two requirements: the
output shape must be unchanged, and calling it with `n_heads=1` must
reproduce the original function *exactly*. Then print both heads' attention
matrices for `n_heads=2` and confirm they differ.

```python
import numpy as np

rng = np.random.default_rng(11)
n, d = 5, 8
X = rng.normal(size=(n, d))
Wq, Wk, Wv, Wo = (rng.normal(0, 0.5, size=(d, d)) for _ in range(4))
mask = np.triu(np.ones((n, n), dtype=bool), k=1)

def softmax(z):
    e = np.exp(z - z.max(axis=-1, keepdims=True))
    return e / e.sum(axis=-1, keepdims=True)

def single_head(X):
    q, k, v = X @ Wq, X @ Wk, X @ Wv
    scores = np.where(mask, -np.inf, q @ k.T / np.sqrt(d))
    A = softmax(scores)
    return A, (A @ v) @ Wo

A, out = single_head(X)
print("weights:", A.shape, " output:", out.shape)
print("token 4 attends:", np.round(A[4], 3))
```

??? success "Solution"

    The whole trick is reshaping `(n, d)` into `(n, n_heads, d_head)` and
    moving the head axis to the front, so numpy's `@` batches over it. Note
    the scaling changes too: each head divides by $\sqrt{d_{\text{head}}}$,
    not $\sqrt{d}$ — which is exactly why `n_heads=1` still matches.

    ```python
    import numpy as np

    rng = np.random.default_rng(11)
    n, d = 5, 8
    X = rng.normal(size=(n, d))
    Wq, Wk, Wv, Wo = (rng.normal(0, 0.5, size=(d, d)) for _ in range(4))
    mask = np.triu(np.ones((n, n), dtype=bool), k=1)

    def softmax(z):
        e = np.exp(z - z.max(axis=-1, keepdims=True))
        return e / e.sum(axis=-1, keepdims=True)

    def single_head(X):
        q, k, v = X @ Wq, X @ Wk, X @ Wv
        scores = np.where(mask, -np.inf, q @ k.T / np.sqrt(d))
        A = softmax(scores)
        return A, (A @ v) @ Wo

    def multi_head(X, n_heads):
        d_head = d // n_heads
        def split(M):                       # (n, d) -> (n_heads, n, d_head)
            return M.reshape(n, n_heads, d_head).transpose(1, 0, 2)
        q, k, v = split(X @ Wq), split(X @ Wk), split(X @ Wv)
        scores = q @ k.transpose(0, 2, 1) / np.sqrt(d_head)
        A = softmax(np.where(mask, -np.inf, scores))          # (n_heads, n, n)
        heads = A @ v                                          # (n_heads, n, d_head)
        concat = heads.transpose(1, 0, 2).reshape(n, d)        # back to (n, d)
        return A, concat @ Wo

    A1, out1 = single_head(X)
    Am, outm = multi_head(X, 1)
    print("n_heads=1 reproduces single_head:",
          np.allclose(A1, Am[0]), np.allclose(out1, outm))

    A2, out2 = multi_head(X, 2)
    print("\nshapes — weights:", A2.shape, " output:", out2.shape,
          "(unchanged)")
    print("\nhead 0, token 4 attends:", np.round(A2[0, 4], 3))
    print("head 1, token 4 attends:", np.round(A2[1, 4], 3))
    print("the two heads agree:", np.allclose(A2[0], A2[1]))
    print("both still causal (row 0 = [1,0,0,0,0]):",
          np.allclose(A2[:, 0, 0], 1.0))
    ```

    Token 4 splits its attention completely differently in the two heads —
    and these are *random* weights, so the difference comes purely from the
    heads looking at different slices of the vector. In a trained model that
    divergence is the whole point: one head can track the subject of the
    sentence while another tracks the nearest open bracket, and the
    concatenate-then-`Wo` step lets the block use both answers at once.

    One last thing worth noticing: the output shape never changed. That is
    the invariant that makes a transformer stackable — you can swap 1 head
    for 2, 8, or 64 without touching a single line of the surrounding code.
