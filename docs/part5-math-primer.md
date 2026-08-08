# The math you'll actually need

Part V is engineering, not mathematics — but a handful of small mathematical
ideas run through every chapter, and a formula you cannot read is a wall. This
page tears that wall down. It teaches, from scratch, **only** the ideas Part V
actually uses: vectors, probability, softmax, logarithms, expectation,
gradients, and KL divergence. There is no calculus prerequisite and no proofs.
Every idea gets a plain sentence, an everyday analogy, and a tiny runnable
block so you can see the numbers move.

If you have finished Parts I–IV — Python, functions, classes, dictionaries,
loops, and Big-O — you have everything you need to start. Read it once
top-to-bottom, run every block, and come back to any section the moment a
formula in a later chapter bites. It is a course *and* a reference.

!!! tip "How to use this page"
    Each section is short on purpose. Skim the **In plain words** box, run the
    block, read the two lines under it. The only way math stops being scary is
    to watch it print small, concrete numbers — which is exactly what every
    block here does.

## Vectors and the dot product

!!! abstract "In plain words"

    - **What it is.** A *vector* is just a fixed-length list of numbers. The
      *dot product* of two vectors is a single number saying how aligned they
      are — big when they point the same way, near zero when they are
      unrelated.
    - **Picture it.** Two friends each rate the same films 0–5. Line the
      ratings up and multiply-then-add: the total is large when they agree on
      what is good, small when their tastes have nothing in common.
    - **Why it matters.** Every model turns each token into a vector, and asks
      "how relevant is this token to that one?" by taking a dot product. It is
      the single most-used operation in Part V.

A vector is a row of numbers with a fixed number of slots (its **dimension**).
The **dot product** lines two vectors up slot by slot, multiplies each pair,
and adds the results into one number. Divide that number by both vectors'
lengths and you get **cosine similarity**, which ignores magnitude and reports
pure direction: `+1` means "same way", `0` means "unrelated".

```python
import numpy as np

# Four films: two action, two comedy. Each person rates them 0 (hated)..5 (loved).
#             MadMax  JohnWick  Barbie  Paddington
ann  = np.array([5,     5,        0,       0])   # loves action
bob  = np.array([4,     5,        1,       0])   # also loves action
cara = np.array([0,     1,        5,       5])   # loves comedy instead

# Dot product BY HAND: multiply matching slots, then add them all up.
by_hand = 0
for a, b in zip(ann, bob):
    by_hand += a * b
print("dot product by hand :", by_hand)
print("dot product in numpy:", int(ann @ bob))   # the @ operator does the same

def cosine(u, v):
    """Dot product with both lengths divided out: +1 same way, 0 unrelated."""
    return float(u @ v / (np.linalg.norm(u) * np.linalg.norm(v)))

print(f"\ncosine(Ann, Bob)  = {cosine(ann, bob):+.3f}   <- agree, so close to +1")
print(f"cosine(Ann, Cara) = {cosine(ann, cara):+.3f}   <- no overlap, so near 0")
```

Ann and Bob agree, so their cosine is close to `+1`. Ann and Cara love
different genres — the slots where one is high, the other is zero — so their
dot product is tiny and the cosine is near `0`. That is the whole trick behind
[embeddings and attention](ch26-llm-internals/02-attention.md): meaning becomes
a direction in space, and "related" becomes "points the same way".

## Probability distributions

!!! abstract "In plain words"

    - **What it is.** A probability distribution is a list of non-negative
      numbers that add up to exactly 1, giving the chance of each option.
    - **Picture it.** How you would split a $1 bet across the horses in a race:
      more on the favourite, a little on the long shots, and the pieces have to
      add up to the whole dollar.
    - **Why it matters.** A language model's output *is* one of these — a
      probability for every possible next token. Everything the sampler does
      (Chapter 26.4) is reshape and draw from this list.

Two rules make a list of numbers a distribution: every entry is `>= 0`, and the
entries **sum to 1**. That is it. A fair die spreads its dollar evenly; a "next
word" distribution piles most of it on a few likely words.

```python
import numpy as np

# A fair six-sided die: six options, each equally likely.
die = np.ones(6) / 6
print("die probabilities:", np.round(die, 3))
print("they sum to      :", round(float(die.sum()), 6))

# A made-up "what word comes next after 'the'?" distribution.
words  = ["cat", "dog", "sky", "idea", "banana"]
p_next = np.array([0.40, 0.30, 0.20, 0.07, 0.03])
print("\nnext-word distribution:")
for w, p in zip(words, p_next):
    print(f"   P(next = {w:<7}) = {p:.2f}")
print("all non-negative :", bool((p_next >= 0).all()))
print("sum of probs     :", p_next.sum())
```

Each die face gets `1/6`, and the six pieces add to `1`. The word distribution
is lopsided — `cat` and `dog` hold most of the mass — but it still obeys the
same two rules. When Chapter 26 says a model "returns a distribution over the
vocabulary", this is the object it means.

## Softmax

!!! abstract "In plain words"

    - **What it is.** Softmax turns any list of scores into a probability
      distribution: a bigger score gets a bigger share, but every option keeps
      some.
    - **Picture it.** Converting raw exam marks into "share of the prize pot".
      The top mark takes the largest slice, weaker marks take smaller slices,
      and the slices add up to the whole pot.
    - **Why it matters.** It is how the model's raw scores (**logits**) become
      the next-token probabilities in
      [Section 26.4](ch26-llm-internals/04-sampling.md), and the `temperature`
      knob lives right inside it.

Softmax does two things at once: it makes every number positive (via $e^x$,
which is always positive) and it divides by the total so the results sum to 1.
The **temperature** $T$ divides the scores *before* softmax: a small $T$
sharpens the distribution toward the top score (bold), a large $T$ flattens it
toward equal shares (timid).

$$
\operatorname{softmax}(z)_i = \frac{e^{z_i / T}}{\sum_j e^{z_j / T}}
$$

Read aloud: *each option's share is its own $e^{\text{score}/T}$ divided by the
sum of everyone's $e^{\text{score}/T}$.*

```python
import numpy as np

def softmax(scores, temperature=1.0):
    z = np.array(scores) / temperature
    z = z - z.max()             # subtract the max first: avoids overflow, same answer
    e = np.exp(z)
    return e / e.sum()

#          cat  dog  sky  idea  banana
scores = [3.0, 2.0, 1.0, 0.5, -1.0]
words  = ["cat", "dog", "sky", "idea", "banana"]

cool = softmax(scores, temperature=0.5)   # bold: sharpen toward the top score
warm = softmax(scores, temperature=2.0)   # timid: spread the mass out

print(f"{'word':<8}{'score':>7}{'T=0.5':>9}{'T=2.0':>9}")
for w, s, c, h in zip(words, scores, cool, warm):
    print(f"{w:<8}{s:>7.1f}{c:>9.3f}{h:>9.3f}")
print(f"\nboth columns are real distributions, summing to "
      f"{cool.sum():.3f} and {warm.sum():.3f}")
```

Same scores, two personalities. At `T = 0.5` the distribution is sharp — `cat`
takes the lion's share. At `T = 2.0` it is flatter — `cat` still leads, but the
others get a real look-in. Both columns sum to 1, because softmax always
returns a genuine distribution. That single knob is the entire idea behind
sampling temperature.

## Logarithms and log-probabilities

!!! abstract "In plain words"

    - **What it is.** A logarithm turns multiplication into addition:
      $\log(a \times b) = \log a + \log b$. Models add **log-probabilities**
      instead of multiplying probabilities.
    - **Picture it.** Multiplying hundreds of tiny fractions is like folding a
      sheet of paper again and again — it shrinks past what any calculator can
      hold. Adding their logs is like counting the folds instead: the number
      stays comfortable.
    - **Why it matters.** The probability of a whole sentence is the product of
      its per-token probabilities. Multiply enough small numbers and the result
      **underflows** to exactly `0.0`; logs are the standard fix, used
      everywhere in training and evaluation.

A probability is at most 1, so a product of many of them races toward zero.
A computer's floating-point numbers cannot go below roughly $10^{-308}$ — past
that, the value becomes a literal `0.0` and all information is lost. Because
$\log$ converts each multiply into an add, the log of the product is just the
**sum of the logs** — a moderate negative number that never underflows.

```python
import numpy as np

# A 50-token sentence. Each token was rare — about 1 chance in 10 million.
probs = [1e-7] * 50

# Probability of the WHOLE sentence = the product of all 50.
product = 1.0
for p in probs:
    product *= p
print("multiply all 50 probabilities:", product, " <- underflowed to exactly 0.0")

# Add the LOGS instead. log turns 'multiply' into 'add', and never underflows.
log_total = sum(np.log(p) for p in probs)
print("add all 50 log-probabilities :", round(log_total, 2))

# Why that is allowed: log(a * b) = log(a) + log(b).
print("check log(a*b)=log a+log b   :",
      np.isclose(np.log(0.2 * 0.3), np.log(0.2) + np.log(0.3)))
```

The product prints as `0.0` — the true value ($10^{-350}$) is smaller than any
number the machine can store, so it vanishes. The sum of logs is a perfectly
usable negative number, and the identity check confirms adding logs is exactly
the same computation. This is why loss functions, perplexity, and the DPO and
PPO objectives of Chapter 31 are all written in terms of log-probabilities.

## Expectation (a weighted average)

!!! abstract "In plain words"

    - **What it is.** The *expectation* is the average outcome when each
      outcome has its own probability — a weighted average, weighting each
      value by how likely it is.
    - **Picture it.** Your expected winnings on a bet: multiply each possible
      payout by its chance, add them up, and you have the average you would
      collect if you played it forever.
    - **Why it matters.** "Average reward" in reinforcement learning (Chapter
      31) is an expectation. When you see $\mathbb{E}[\cdots]$ in a formula, it
      just means "the probability-weighted average of the thing in brackets".

Expectation is the dot product from the first section, wearing a different hat:
line up the outcomes and their probabilities, multiply pair by pair, and add.

$$
\mathbb{E}[X] = \sum_i x_i \, p_i
$$

Read aloud: *add up each outcome $x_i$ times its probability $p_i$.*

```python
import numpy as np

# A spinner bet. Each outcome has a dollar payout and a probability.
payouts = np.array([100, 20, 0, -10])          # last one: you lose $10
probs   = np.array([0.05, 0.25, 0.40, 0.30])
print("probabilities sum to:", probs.sum())

# Expectation = sum of (outcome * its probability) = a weighted average.
by_hand = 0.0
for x, p in zip(payouts, probs):
    by_hand += x * p
print("expected payout by hand :", by_hand)
print("expected payout in numpy:", float(payouts @ probs))   # same as a dot product
print(f"so on average each spin is worth ${float(payouts @ probs):.2f}")
```

The `100` payout is worth a lot but almost never happens; the small losses
happen often. Weigh each by its probability and the average spin is worth a few
dollars — not the jackpot, not the loss, but the blend. Notice the whole thing
is one dot product: expectation and the dot product are the same arithmetic.

## Gradients without calculus

!!! abstract "In plain words"

    - **What it is.** A *gradient* answers two questions about a number you are
      trying to shrink: *which way is downhill*, and *how steep is it here?*
    - **Picture it.** You are standing on a foggy hillside and want the valley
      floor. You cannot see it, but you can feel the slope under your feet —
      so you step downhill, feel again, step again. That loop is **gradient
      descent**, and it is exactly how models train.
    - **Why it matters.** Training a model *is* this loop: define a "loss" that
      is small when the model is right, then repeatedly nudge the numbers
      downhill. Chapter 31's policy-gradient methods are this idea applied to
      language models.

You do not need calculus to find a slope — you can *measure* it. Nudge the
input a tiny bit right, see how much the loss went up, and divide: that ratio
is the slope (a **finite difference**). A positive slope means "uphill to the
right", so you step left; a steep slope means take a bigger step. Repeat, and
you slide to the bottom.

```python
import numpy as np
import matplotlib.pyplot as plt

# A bowl-shaped "loss". Its lowest point is at x = 3 — but pretend we don't know that.
def loss(x):
    return (x - 3.0) ** 2

def slope_at(x, h=1e-4):
    """Measure the slope by nudging x a hair each way. No calculus needed."""
    return (loss(x + h) - loss(x - h)) / (2 * h)

x = 8.0                 # start far from the bottom
lr = 0.1                # step size, the 'learning rate'
history = [x]
for _ in range(40):
    g = slope_at(x)     # which way is UPhill, and how steep
    x = x - lr * g      # step the OPPOSITE way: downhill
    history.append(x)

print(f"started at x = {history[0]:.2f}, loss = {loss(history[0]):.2f}")
print(f"ended   at x = {x:.4f}, loss = {loss(x):.4f}   (true bottom is x = 3)")

fig, ax = plt.subplots(figsize=(6, 3.4))
ax.plot([loss(v) for v in history], marker="o", markersize=3)
ax.set_xlabel("gradient-descent step")
ax.set_ylabel("loss  =  (x - 3)^2")
ax.set_title("Each step walks downhill; the loss falls toward 0")
fig.tight_layout()
```

Starting at `x = 8`, the loop slides `x` to almost exactly `3` and the loss
drops to essentially `0` — without ever being told where the bottom was. It
only ever felt the slope and stepped downhill. **This is exactly what training
a neural network does**, with one difference of scale: instead of one number
`x`, a real model adjusts millions or billions of them at once, and instead of
a finite-difference nudge it uses a faster bookkeeping trick called
backpropagation to get every slope in one pass. The loop — measure the slope,
step downhill, repeat — is identical. That downhill direction is what the
symbol $\nabla$ (nabla) means in [Chapter 31](ch31-rl/index.md).

## KL divergence

!!! abstract "In plain words"

    - **What it is.** KL divergence is one number for how different two
      probability distributions are: `0` when they are identical, and larger
      the more they disagree.
    - **Picture it.** How far a weather forecast strayed from what actually
      happened. Nail it and the score is zero; confidently predict sun on a day
      it pours and the score is large.
    - **Why it matters.** Post-training needs a leash: keep the new model close
      to the old one so it improves without going haywire. KL divergence *is*
      that leash — it measures the drift, and Chapter 31 penalises it.

KL divergence compares a reference distribution `p` (what is true, or the old
model) against a second distribution `q` (a forecast, or the new model). It is
zero exactly when they match, and it grows as they pull apart. It is not
symmetric — `KL(p, q)` and `KL(q, p)` differ — which is why the order is always
written out.

$$
\operatorname{KL}(p \,\|\, q) = \sum_i p_i \, \log \frac{p_i}{q_i}
$$

Read aloud: *for each option, weight the log of "how many times more likely
$p$ thinks it is than $q$ does" by $p$'s own probability, then add them up.*

```python
import numpy as np

def kl(p, q):
    """How different is forecast q from reality p? 0 if identical, else larger."""
    p, q = np.array(p), np.array(q)
    return float(np.sum(p * np.log2(p / q)))     # log2 -> the answer is in 'bits'

truth = [0.7, 0.2, 0.1]          # what actually happens: rain, cloud, sun
same  = [0.7, 0.2, 0.1]          # a forecast that nails it
close = [0.6, 0.25, 0.15]        # a decent forecast
wild  = [0.1, 0.2, 0.7]          # a forecast that bets on the wrong thing

print(f"KL(truth || identical) = {kl(truth, same):.3f}   <- exactly 0")
print(f"KL(truth || close)     = {kl(truth, close):.3f}   <- small")
print(f"KL(truth || wild)      = {kl(truth, wild):.3f}   <- large")
```

Identical distributions score exactly `0`. A forecast that is a little off
scores a small number; one that bets on the wrong outcome scores a big one.
That single number is why Part V can *hold a model on a leash*: the PPO penalty
in [Section 31.2](ch31-rl/02-policy-gradient-ppo.md) adds KL divergence to the
loss so the model cannot drift far from a trusted reference, and DPO's $\beta$
in [Section 31.3](ch31-rl/03-dpo-grpo.md) tunes the strength of the same pull.
Keep new-versus-old distributions close, and you improve behaviour without
breaking what already worked.

## Symbol → plain name → where it shows up

When a Part V formula throws a Greek letter at you, come back here. Every symbol
below means something you have now run code for.

| Symbol | Say it | Plain meaning | Shows up in |
| --- | --- | --- | --- |
| $\mathbf{a} \cdot \mathbf{b}$ | "a dot b" | one number for how aligned two vectors are | Ch 26 (attention scores) |
| $\sum_i$ | "sum over i" | add these up across all the options | everywhere |
| $\operatorname{softmax}$ | "softmax" | turn scores into a distribution that sums to 1 | Ch 26 (logits → probabilities) |
| $T$ | "temperature" | how bold vs. timid the sampler is | Ch 26.4 |
| $\log$ | "log" | turns multiply into add; keeps tiny probabilities usable | Ch 31, evaluation |
| $\mathbb{E}[\,\cdot\,]$ | "expected value of" | the probability-weighted average | Ch 31 (average reward) |
| $\nabla$ | "nabla" / "the gradient" | the downhill direction — which way to nudge, and how hard | Ch 31 |
| $\operatorname{KL}(p \,\|\, q)$ | "the KL from p to q" | how far distribution $q$ has drifted from $p$ | Ch 31 (PPO penalty) |
| $\pi$ | "pi" | the model itself — its probability of producing a response | Ch 31 |
| $\pi_{\text{ref}}$ | "pi-ref" | a frozen copy of the starting model, used as the reference | Ch 31 |
| $\beta$ | "beta" | how hard we hold the new model near the reference | Ch 31 |

None of these is more than the arithmetic on this page dressed up in notation.
When a chapter shows a formula, find its symbols here, and it turns back into
something you can run.

[Back to the Part V overview](part5-overview.md){ .md-button }
