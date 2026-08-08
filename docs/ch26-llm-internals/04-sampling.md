# 26.4 Sampling — how text is chosen

Section 26.3 ended with a row of numbers: one score per vocabulary entry,
the model's opinion about what comes next. But a model does not "write" —
it *scores*, and then a completely separate piece of ordinary code decides
which token to actually emit. That code is the **sampler**, it is maybe
fifty lines long, it contains no learned parameters at all, and it is
responsible for most of the difference between output that feels alive and
output that feels like a broken record. Every knob you have ever seen in a
playground UI — temperature, top-k, top-p, penalties — lives here, not in
the model. This section implements all of them.

## Logits are not probabilities

The model's final layer produces **logits**: unbounded real numbers, one per
token in the vocabulary. A logit of $3.4$ is not a probability — it is not
even between 0 and 1. Softmax (which you already implemented in Section
26.2) is what turns the row into a distribution:

$$
p_i = \frac{e^{z_i}}{\sum_j e^{z_j}}
$$

```python
import numpy as np

vocab = ["the", "cat", "sat", "mat", "banana"]
logits = np.array([2.1, 3.4, 0.7, 1.9, -2.5])   # straight out of the model

def softmax(z):
    e = np.exp(z - z.max())        # subtract the max: no overflow, same answer
    return e / e.sum()

probs = softmax(logits)
print(f"{'token':<9}{'logit':>8}{'probability':>13}")
for tok, z, p in zip(vocab, logits, probs):
    print(f"{tok:<9}{z:>8.2f}{p:>13.4f}")
print(f"\nprobabilities sum to {probs.sum():.6f}")
print(f"the gap 3.4 - 2.1 = 1.3 in logit space becomes a "
      f"{probs[1] / probs[0]:.2f}x ratio in probability space")
```

Two properties of softmax are worth keeping in mind:

- **It is shift-invariant.** Adding 5 to every logit changes nothing, so only
  the *gaps* between logits matter.
- **It is exponential.** A modest logit gap becomes a large probability
  ratio: the 1.3-point lead of `cat` over `the` makes `cat` 3.67 times more
  likely.

## A toy model to sample from

To study samplers we need something that produces logits. Instead of running
a transformer for every step, here is a hand-written table that plays the
same role: given the current token, it returns a row of scores. It is not
learned and it is not a neural network — but it emits exactly what the last
row of Section 26.3's `logits` array emits, which is all a sampler needs.

```python
import numpy as np

VOCAB = ["<bos>", "the", "cat", "sat", "on", "mat",
         "and", "a", "dog", "ran", "fast", "<eos>"]
STOI = {t: i for i, t in enumerate(VOCAB)}

# Hand-made "model": what each token thinks should follow it, as raw scores.
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
    """One 'forward pass': a score for every vocabulary entry."""
    z = np.full(len(VOCAB), -6.0)      # everything is possible, most of it unlikely
    for tok, score in TABLE[token].items():
        z[STOI[tok]] = score
    return z

z = next_logits("the")
order = np.argsort(-z)[:4]
print("logits after 'the':")
for j in order:
    print(f"   {VOCAB[j]:<7}{z[j]:>6.1f}")
print("\nvocabulary size:", len(VOCAB))
```

## Greedy decoding: always take the biggest

The simplest possible sampler takes the `argmax` every step. No randomness,
no parameters, fully deterministic:

```python
# continues
def greedy_generate(start="<bos>", max_new=16):
    out = [start]
    for _ in range(max_new):
        z = next_logits(out[-1])
        nxt = VOCAB[int(z.argmax())]
        out.append(nxt)
        if nxt == "<eos>":
            break
    return " ".join(out)

print(greedy_generate())
```

Look at what came out: `<bos> the cat sat on the cat sat on the cat sat on
the cat sat on`. Greedy decoding has two problems, and this output shows the
first one.

**Problem 1 — it gets stuck.** The model walked into a four-token cycle,
`the → cat → sat → on → the`, and because greedy decoding is deterministic
and depends only on the current token, it can *never* leave. This is not a
quirk of our toy. Greedy and low-temperature decoding on real models produce
exactly this failure: the paragraph that starts repeating itself and never
stops.

**Problem 2 — locally best is not globally best.** Taking the
highest-probability token at every step does **not** produce the
highest-probability *sentence*. A slightly worse first token can open onto a
much better continuation, and greedy decoding has no lookahead at all with
which to notice.

## Temperature: flattening or sharpening the distribution

The fix is to *sample* instead of maximise. **Temperature** $T$ divides every
logit before the softmax:

$$
p_i = \frac{e^{z_i / T}}{\sum_j e^{z_j / T}}
$$

Three cases, and they are the whole of it:

- **$T < 1$** spreads the logits further apart, so softmax concentrates: the
  distribution sharpens and the output becomes more predictable.
- **$T = 1$** leaves the model's own distribution untouched.
- **$T > 1$** squashes the logits together, so the distribution flattens and
  rarer tokens get a real chance.

```python
# continues
row = next_logits("the")
print(f"{'T':>5}{'cat':>8}{'mat':>8}{'dog':>8}{'tail':>9}{'entropy':>11}")
for T in [0.2, 1.0, 2.0]:
    p = np.exp((row - row.max()) / T)
    p = p / p.sum()
    tail = float(p.sum() - p[[2, 5, 8]].sum())     # the nine "wrong" tokens
    entropy = float(-(p * np.log2(p + 1e-12)).sum())
    print(f"{T:>5.1f}{p[2]:>8.3f}{p[5]:>8.3f}{p[8]:>8.3f}{tail:>9.4f}"
          f"{entropy:>8.2f} bits")
```

Read the table row by row:

- **$T = 0.2$** — `cat` takes 91.8% of the mass and the model is nearly
  deterministic, at 0.44 bits of entropy: less than one coin flip's worth of
  uncertainty.
- **$T = 1.0$** — `cat` takes 50.6%.
- **$T = 2.0$** — `cat` is down to 40.2% and entropy has risen to 1.86 bits.

Watch the `tail` column especially. It holds the nine tokens our table scored
at $-6.0$, the ones the model considers *wrong*. They carry 0.06% of the mass
at $T = 1$ and 4% at $T = 2$ — a one-in-twenty-five chance of nonsense on
every single step, compounding over a whole paragraph.

### Temperature in one picture

```python
# continues
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(7.0, 3.4))
width = 0.27
xs = np.arange(len(VOCAB))
for offset, T in zip([-width, 0.0, width], [0.2, 1.0, 2.0]):
    p = np.exp((row - row.max()) / T)
    p = p / p.sum()
    ax.bar(xs + offset, p, width=width, label=f"T = {T}")
ax.set_xticks(xs, VOCAB, rotation=45, ha="right")
ax.set_xlabel("next token")
ax.set_ylabel("probability")
ax.set_title("Temperature reshapes the same logits")
ax.legend()
fig.tight_layout()
```

Three bars per token, one per temperature. The $T = 0.2$ series is a single
spike over `cat`; the $T = 2.0$ series is three near-equal columns with a
visible fringe on every other token. Same model, same logits, three
different personalities.

!!! warning "High temperature does not mean 'more creative'"
    It means *more probability mass on tokens the model thinks are wrong*.
    Below about $T = 1$ you trade variety for reliability; above it you buy
    variety with correctness. Past roughly $T = 1.5$ most models begin
    emitting genuine nonsense, because the flattened tail contains tens of
    thousands of tokens that were rejected for good reasons.

## Top-k: keep only the k best candidates

Temperature has one bad property: it never removes anything. At $T = 2$, a
vocabulary of 128,000 tokens contributes 128,000 small probabilities, and
their *sum* can be large enough that something absurd gets picked. **Top-k**
truncation fixes this bluntly — keep the $k$ highest logits, set the rest to
$-\infty$, renormalise:

```python
# continues
def top_k_filter(z, k):
    if k is None or k >= len(z):
        return z
    kth = np.sort(z)[-k]                 # the k-th largest value
    return np.where(z < kth, -np.inf, z)

row = next_logits("the")
for k in [1, 3, 12]:
    filt = top_k_filter(row.copy(), k)
    survivors = [VOCAB[j] for j in np.argsort(-filt) if np.isfinite(filt[j])]
    p = softmax(filt)
    print(f"k={k:>2}  survivors: {str(survivors[:4]):<42} "
          f"kept {len(survivors):>2}/{len(VOCAB)}")
    print(f"      probabilities: " +
          ", ".join(f"{VOCAB[j]}={p[j]:.3f}" for j in np.argsort(-p)[:3]))
```

With $k = 3$ only `cat`, `mat`, and `dog` survive; every other token is
mathematically impossible this step. Note that `k=1` is exactly greedy
decoding — one survivor, with probability 1.000.

**The weakness of top-k is that $k$ is fixed while the model's confidence is
not.** When the model is sure (after `sat`, only `on` makes sense) $k = 50$
drags in 49 bad options. When the model is genuinely uncertain, $k = 50$
amputates good ones.

## Top-p (nucleus): keep the smallest set that covers p

**Top-p**, also called **nucleus sampling**, adapts automatically: sort the
tokens by probability, walk down the list accumulating mass, and stop as
soon as the running total reaches $p$. Confident steps keep two tokens;
uncertain steps keep two hundred.

```python
# continues
def top_p_filter(z, p_threshold):
    if p_threshold is None or p_threshold >= 1.0:
        return z
    probs = softmax(z)
    order = np.argsort(-probs)                    # most likely first
    cumulative = np.cumsum(probs[order])
    n_keep = int(np.searchsorted(cumulative, p_threshold) + 1)
    keep = set(order[:n_keep].tolist())
    return np.array([zi if j in keep else -np.inf for j, zi in enumerate(z)])

for context in ["the", "sat"]:
    row = next_logits(context)
    for p_threshold in [0.5, 0.9]:
        filt = top_p_filter(row, p_threshold)
        survivors = [VOCAB[j] for j in np.argsort(-filt) if np.isfinite(filt[j])]
        print(f"after {context!r:>7}, top-p={p_threshold}: kept {len(survivors)} "
              f"-> {survivors}")
```

This is the adaptivity top-k lacks. After `the` — where the model is
undecided between `cat`, `mat`, and `dog` — top-p 0.9 keeps three tokens.
After `sat`, where `on` is overwhelming, the *same setting* keeps just one.

The nucleus grows and shrinks with the model's own confidence, which is why
top-p (typically 0.9–0.95) is the common default, sometimes combined with a
generous top-k as a safety net.

### The four strategies side by side

| Strategy | What it does | Adapts to confidence? | Reach for it when |
| --- | --- | --- | --- |
| **Greedy** ($T=0$) | Always take the `argmax` | — (no randomness at all) | You want determinism: extraction, classification, tests |
| **Temperature** | Rescale every logit by $1/T$ before softmax | No — it reshapes, never removes | You want a global dial from cautious to wild |
| **Top-k** | Keep the $k$ best logits, drop the rest | No — $k$ is fixed | You need a hard cap on how many tokens are reachable |
| **Top-p** (nucleus) | Keep the smallest set whose mass reaches $p$ | **Yes** — the set grows and shrinks | The general-purpose default, usually with $T$ |

They compose rather than compete: a typical production setting is a
temperature *and* a top-p, with top-k as a backstop.

## Repetition penalty: taxing what you already said

Sampling reduces loops but does not abolish them. A **repetition penalty**
attacks them directly by pushing down the logits of tokens already present
in the text. The standard formulation divides positive logits by the penalty
$\rho > 1$ and multiplies negative ones (so the change always moves the score
*down*):

$$
z_i \leftarrow \begin{cases}
z_i / \rho & \text{if } z_i > 0 \\
z_i \times \rho & \text{if } z_i \le 0
\end{cases}
\qquad \text{for every token } i \text{ already generated}
$$

```python
# continues
def repetition_penalty(z, used_ids, rho):
    if rho == 1.0:
        return z
    z = z.copy()
    for i in set(used_ids):
        z[i] = z[i] / rho if z[i] > 0 else z[i] * rho
    return z

so_far = ["<bos>", "the", "cat", "sat", "on"]
row = next_logits("on")
used = [STOI[t] for t in so_far]
print(f"{'token':<8}{'logit':>8}{'penalised':>11}{'p before':>10}{'p after':>9}")
before, after = softmax(row), softmax(repetition_penalty(row, used, 1.5))
pen = repetition_penalty(row, used, 1.5)
for j in [1, 7]:                              # 'the' (already used) and 'a' (new)
    print(f"{VOCAB[j]:<8}{row[j]:>8.2f}{pen[j]:>11.2f}"
          f"{before[j]:>10.3f}{after[j]:>9.3f}")
print("\n'the' was already used, so its lead over 'a' shrinks from "
      f"{before[1] / before[7]:.2f}x to {after[1] / after[7]:.2f}x")
```

Used with a light hand ($\rho \approx 1.05$–$1.2$) this breaks loops. Used
heavily it is actively harmful, because it penalises the words a text
legitimately needs to repeat: the names of the characters, the keyword in a
piece of code, the word "the".

Variants exist — **frequency** and **presence** penalties count *how often* a
token appeared rather than merely whether it did — and all of them share that
same failure mode.

## The complete generation loop

Everything above assembles into one function, and the *order* of the stages
is part of the design:

1. **Get the logits** for the current token — one forward pass.
2. **Apply the repetition penalty** to tokens already generated.
3. **Divide by the temperature** (or shortcut to `argmax` if $T = 0$).
4. **Truncate by rank** with top-k.
5. **Truncate by mass** with top-p.
6. **Softmax and draw** one token.
7. **Stop** on `<eos>` or the token budget.

This is genuinely the whole sampler. A real implementation adds batching,
streaming, and stop sequences, but the decision logic is exactly this:

```python
# continues
def generate(start="<bos>", max_new=18, temperature=1.0, top_k=None,
             top_p=None, rho=1.0, seed=0):
    rng = np.random.default_rng(seed)
    out = [start]
    for _ in range(max_new):
        z = next_logits(out[-1]).astype(float)       # 1. the model's scores
        z = repetition_penalty(z, [STOI[t] for t in out], rho)   # 2. penalties
        if temperature <= 0:                          # 3. greedy shortcut
            nxt = int(z.argmax())
        else:
            z = z / temperature                       # 4. temperature
            z = top_k_filter(z, top_k)                # 5. truncate by rank
            z = top_p_filter(z, top_p)                # 6. truncate by mass
            nxt = int(rng.choice(len(VOCAB), p=softmax(z)))   # 7. draw
        out.append(VOCAB[nxt])
        if VOCAB[nxt] == "<eos>":                     # 8. stop
            break
    return " ".join(out)

settings = [
    ("greedy (T=0)             ", dict(temperature=0.0)),
    ("T=0.7, top-p=0.9         ", dict(temperature=0.7, top_p=0.9)),
    ("T=1.0, top-k=3           ", dict(temperature=1.0, top_k=3)),
    ("T=1.0, top-p=0.9, rho=1.2", dict(temperature=1.0, top_p=0.9, rho=1.2)),
    ("T=3.0 (chaos)            ", dict(temperature=3.0)),
]
for label, kwargs in settings:
    print(f"{label} | {generate(seed=49, **kwargs)}")
```

Read the five lines against each other. Same model, same seed, five
different texts:

| Setting | What it produced |
| --- | --- |
| greedy ($T = 0$) | Stuck in its cycle, never emits `<eos>`, runs to the token limit |
| $T = 0.7$, top-p 0.9 | Stays inside the table's sensible transitions and stops properly |
| $T = 1.0$, top-k 3 | A different draw at the same branch — `a dog` rather than `the dog` |
| $T = 1.0$, top-p 0.9, $\rho = 1.2$ | The longest tour, pushed away from words it just used |
| $T = 3.0$ | Lets the $-6.0$ tail through: `<bos>` mid-sentence, which no path through the table allows |

That last row is precisely what a real model at temperature 3 looks like.

### Does the repetition penalty actually work?

Or does it just feel like it should? Run 300 seeds and count:

```python
# continues
def repeated_bigram(tokens):
    """True if any adjacent pair of tokens occurs twice — the loop signature."""
    pairs = [tuple(tokens[i:i + 2]) for i in range(len(tokens) - 1)]
    return len(pairs) != len(set(pairs))

print(f"{'rho':>5}{'distinct tokens':>17}{'runs that loop':>16}{'avg length':>12}")
for rho in [1.0, 1.2, 1.5, 2.0]:
    runs = [generate(seed=s, temperature=1.0, top_p=0.9, rho=rho).split()
            for s in range(300)]
    distinct = np.mean([len(set(r)) for r in runs])
    looped = np.mean([repeated_bigram(r) for r in runs])
    length = np.mean([len(r) for r in runs])
    print(f"{rho:>5.1f}{distinct:>17.2f}{looped:>15.0%}{length:>12.1f}")
```

The claim checks out and the size of the effect is worth noting: going from
no penalty to $\rho = 2.0$ takes looping runs from 48% down to 26% and
raises the distinct-token count from 7.59 to 8.17. Real, but not a cure —
which is why the penalty is a nudge you combine with sampling, never a
substitute for it.

!!! note "What is toy, what is faithful"
    Toy: the 12-token vocabulary and the hand-written `TABLE` standing in
    for a trained network. Faithful: every line of `generate` — the order of
    operations (penalty, temperature, top-k, top-p, draw), the softmax, the
    `-inf` masking, and the `<eos>` stop condition are exactly what a
    production sampler does, on rows of 128,000 logits instead of 12.

## What streaming actually is

You have watched a chatbot type its answer out word by word. That is not a
typewriter animation — it is the loop above, made visible. Each pass through
the loop produces exactly one token, and the server sends it onward the
moment it exists instead of waiting for the `<eos>`.

```text
POST /v1/chat/completions   {"stream": true, ...}

data: {"delta": {"content": "The"}}
data: {"delta": {"content": " cat"}}
data: {"delta": {"content": " sat"}}
data: {"delta": {"content": " on"}}
data: {"delta": {"content": " the"}}
data: {"delta": {"content": " mat"}}
data: [DONE]
```

Streaming changes nothing about the maths and everything about how the wait
*feels*: the reader starts reading after the first token rather than after
the last. It also explains two things you may have noticed:

- **The first token takes noticeably longer than the rest.** The model has to
  process your whole prompt before it can produce anything.
- **The pieces that arrive are *tokens*, not words.** That is why a streamed
  reply sometimes jerks forward in half-words, or splits an emoji across two
  chunks.

[Section 27.3](../ch27-inference/03-latency-streaming.md) names those two
delays properly and puts the wire format under a microscope.

## Why temperature = 0 is not perfectly deterministic

Setting temperature to 0 makes the *sampler* deterministic — `argmax` has no
randomness in it — and yet sending the same prompt twice to a real API at
temperature 0 can still return different text. This is not a lie in the
documentation. It is floating-point arithmetic meeting parallel hardware, in
four steps:

1. **GPUs sum long lists of numbers in whatever order the work was
   scheduled.**
2. **Floating-point addition is not associative**: $(a + b) + c$ can differ
   from $a + (b + c)$ in the last bit.
3. **That scheduling changes with the batch size**, which changes with how
   many other users hit the server at that instant.
4. **A near-tie amplifies the difference.** When the top two logits are
   nearly equal, a discrepancy of $10^{-7}$ flips the `argmax` — and from
   that token onward the two outputs diverge completely.

Add the fact that providers update model weights, quantization, and kernels
without changing the model's name, and the honest summary is short:
**temperature 0 gives you *greedy* decoding, not *reproducible* decoding.**

If you need reproducibility, pin it in your own evaluation harness. The
[testing discipline of Chapter 24](../ch24-practice/02-testing.md) applies
here exactly as it does anywhere else.

!!! warning "Common mistakes"
    - **Thinking the sampler is part of the model.** It is not, and it has
      no learned parameters. Two products with wildly different "voices"
      may be the same weights with different temperature and top-p.
    - **Stacking every knob at once.** Temperature 1.2 *and* top-k 40 *and*
      top-p 0.8 *and* a 1.5 repetition penalty interact in ways nobody can
      predict. Change one at a time and keep the seed fixed.
    - **Using high temperature for factual work.** Extraction,
      classification, and code generation want $T$ near 0. Brainstorming
      and creative writing want variety. The knob is a task decision, not
      a quality setting.
    - **Forgetting `<eos>` is a token like any other.** Truncation can
      remove it: an aggressive top-k or a repetition penalty applied to
      `<eos>` can make a model physically unable to stop, which is one real
      cause of replies that run to the token limit.

## Check your understanding

1. Adding 10 to every logit leaves the sampled distribution unchanged, but
   dividing every logit by 10 changes it completely. Why?

    ??? success "Answer"

        Softmax is shift-invariant: $e^{z_i + c}$ has the constant factor
        $e^{c}$ in both numerator and denominator, and it cancels. Only
        *differences* between logits matter. Dividing scales those
        differences, which is exactly what temperature does — it is
        division by $T$, and $T = 0.1$ means multiplying every gap by 10.

2. A model is very confident (one token holds 95% of the mass). What do
   top-k = 50 and top-p = 0.9 each keep?

    ??? success "Answer"

        Top-k keeps 50 tokens no matter what, so 49 near-zero candidates
        stay in the running. Top-p walks down the sorted list and stops as
        soon as the cumulative mass passes 0.9 — the first token alone
        reaches 0.95, so it keeps exactly one. That adaptivity is the whole
        argument for nucleus sampling.

3. Your model repeats a phrase forever. You have temperature, top-p, and a
   repetition penalty available. Which do you reach for, and what does each
   cost you?

    ??? success "Answer"

        Raising temperature (or top-p) restores randomness so the loop can
        be escaped, at the cost of accuracy. A small repetition penalty
        ($\rho \approx 1.1$) targets the loop directly and costs less
        fluency, but too much of it makes the text avoid words it
        legitimately needs. Try the penalty first, in small steps, with a
        fixed seed so you can see the effect.

4. Two identical requests at temperature 0 return different answers. Give
   the mechanism, in one sentence, and say what it implies about
   reproducible evaluation.

    ??? success "Answer"

        GPU floating-point reductions happen in a non-deterministic order
        depending on batching, so logits differ in their last bits and a
        near-tie flips the `argmax` — meaning temperature 0 buys you greedy
        decoding, not reproducibility, so evaluation harnesses must record
        the exact model version and average over repeated runs rather than
        assuming a single run is the answer.
