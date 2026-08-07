# Project 7 · Preference Alignment with DPO

[31.3](../../ch31-rl/03-dpo-grpo.md) derived the DPO loss and trained a
ten-parameter policy on eight hand-written pairs. This project turns that
into a pipeline: a synthetic *annotator* that generates the preference data
from a rule you can read, a train/held-out split so "it learned" becomes a
number, a gradient you verify with a ruler before you trust it, an eval that
compares DPO against the rejection-sampling baseline it has to beat, and a
$\beta$ sweep with a plot.

Everything is toy in *scale* — twenty parameters, four prompts, twelve
pairs — and faithful in *algorithm*. `dpo_loss` and `dpo_grad` below are the
objective from the paper and its exact gradient; a run on a 7B model
computes the same two quantities over a great many more numbers.

## What you'll build

A full alignment run you can read end to end:

```text
5. training
  step      loss   mean margin  train ranking
     0    0.6931        0.0000           0/12
    50    0.6471        0.0946          12/12
   300    0.4780        0.4987          12/12

train-set agreement     100.0%
held-out agreement       88.6%   (the reference scores 50.0%: every implicit reward is 0)
KL from the reference    1.622 nats

  'explain recursion'   (rank = the annotator's order)
   response                     rank  reference   policy   change  implicit r
   worked example                  1      0.164    0.652   +0.487       0.138
   one-line definition             2      0.085    0.294   +0.209       0.124
   curt 'just look it up'          3      0.075    0.028   -0.047      -0.097
   wall of jargon                  4      0.404    0.015   -0.390      -0.332
   off-topic ramble                5      0.271    0.011   -0.260      -0.319

6. what DPO buys you, against a rejection-sampling baseline
method                    P(top answer)  KL from ref   held-out  generations / query
reference (untuned)               14.4%        0.000      50.0%                    0
best-of-4 sampling                46.2%        0.571     100.0%                    4
best-of-64 sampling              100.0%        1.945     100.0%                   64
DPO, 12 pairs                     87.8%        1.622      88.6%                    1
```

The reference model's favourite response for *every* prompt is its longest
one. After twelve comparisons the policy's favourite is the annotator's
favourite for every prompt, and the `implicit r` column is the reward
function DPO learned without ever building one.

## What it exercises

- [31.3 DPO and GRPO](../../ch31-rl/03-dpo-grpo.md) — the loss, the implicit
  reward, the role of $\beta$, and the failure modes you will reproduce here
  on purpose.
- [31.4 Reward models](../../ch31-rl/04-reward-models.md) — why annotators
  compare instead of scoring, and what Bradley-Terry does with a comparison.
- [31.1 RL basics](../../ch31-rl/01-rl-basics.md) — softmax policies,
  log-probabilities, and checking a gradient with finite differences.
- [26.4 Sampling](../../ch26-llm-internals/04-sampling.md) — the softmax
  that turns logits into the probabilities every table here prints.
- [32.2 Synthetic data](../../ch32-data/02-synthetic-data.md) — a rule-based
  labeller is synthetic data with the generating rule left visible, which is
  exactly what makes the experiment readable.
- [Chapter 16 · Algorithm Analysis](../../ch16-complexity/index.md) — the
  finite-difference check costs $2n$ loss evaluations for $n$ parameters,
  which is why you can afford it at 20 parameters and not at 7 billion.

## Milestones

### Milestone 1 — the policy and its frozen reference

**Goal:** four prompts, five candidate responses each, and a policy
`theta` of shape `(4, 5)` whose rows are softmax logits. Build the frozen
reference `REF_LOGITS` from a deliberate flaw — make it proportional to
response length, so the untuned model prefers the longest answer every time.

**Done when...** `softmax(theta[p])` sums to 1 for every prompt; the
reference's favourite is the longest response for all four prompts; and you
can print the correlation between a response's log-probability under the
reference and its word count and get something close to $+1$.

??? tip "Hint"

    Give every response the *attributes* your annotator will later care
    about, so the ground truth is a table you can read rather than a set of
    numbers you have to trust:

    ```python
    import numpy as np

    #  name                 words  polite  on-topic
    OPTIONS = [("worked example",  45, 1, 1),
               ("wall of jargon",  90, 1, 1),
               ("off-topic ramble", 70, 1, 0)]
    words = np.array([w for _, w, _, _ in OPTIONS], dtype=float)
    ref_logits = 0.02 * words                     # a pure length bias

    e = np.exp(ref_logits - ref_logits.max())
    print("reference probabilities:", np.round(e / e.sum(), 3))
    print("favourite:", OPTIONS[int(np.argmax(ref_logits))][0])
    ```

    Building the flaw in on purpose is what makes the whole project
    legible: at the end you can point at the exact behaviour that changed
    and say which twelve comparisons caused it.

### Milestone 2 — the annotator and the preference data

**Goal:** `annotator_score(prompt, response)` combining the three
attributes — concise (a penalty that grows either side of about thirty
words), polite, on-topic — then all pairwise comparisons, with near-ties
dropped, shuffled and split into 12 training pairs and the rest held out.

**Done when...** every pair is `(prompt, winner, loser)` with the winner
genuinely scoring higher; pairs whose scores differ by less than a margin
are excluded; and the split is reproducible (`np.random.default_rng(0)`)
so two runs produce identical data.

??? tip "Hint"

    A quadratic penalty says "about this long", where a linear one says "as
    short as possible" — and the difference decides whether a three-word
    brush-off wins:

    ```python
    for words in (4, 12, 30, 45, 90):
        linear = -0.02 * words
        quadratic = -((words - 30.0) / 40.0) ** 2
        print(f"{words:>4} words   linear {linear:+.2f}   "
              f"quadratic {quadratic:+.2f}")
    ```

    Then read your generated pairs before training on them. Ours contains
    `asks about lunch instead` beating `long apology tour`, because a
    95-word answer is punished harder than being off-topic. That is not a
    bug in the code — it is the rule saying something you did not mean, and
    it is exactly how a real preference dataset acquires the flaw that
    later shows up as model behaviour nobody can explain.

### Milestone 3 — the DPO loss

**Goal:** `margins(theta, pairs, beta)` returning
$\beta\left(\hat r(y_w) - \hat r(y_l)\right)$ for each pair, and
`dpo_loss` returning the mean of $-\log \sigma(\text{margin})$:

$$
\mathcal{L}_{\text{DPO}} = -\,\mathbb{E}_{(x,\,y_w,\,y_l)}
\left[\log \sigma\!\left(
\beta \log \frac{\pi_\theta(y_w \mid x)}{\pi_{\text{ref}}(y_w \mid x)}
- \beta \log \frac{\pi_\theta(y_l \mid x)}{\pi_{\text{ref}}(y_l \mid x)}
\right)\right]
$$

**Done when...** the loss at `theta = REF_LOGITS` is exactly
$\log 2 = 0.693147$ — every margin is zero because the policy *is* the
reference — and the loss is finite for margins of $\pm 50$, which a naive
`-log(1 / (1 + exp(-s)))` is not.

??? tip "Hint"

    `np.logaddexp(0, -s)` is $\log(1 + e^{-s})$ computed without
    overflowing, and it is exactly $-\log \sigma(s)$:

    ```python
    import numpy as np

    def naive(s):
        return -np.log(1.0 / (1.0 + np.exp(-s)))

    def stable(s):
        return np.logaddexp(0.0, -s)

    for s in (0.0, 2.0, -50.0, -800.0):
        print(f"margin {s:>7}: naive {naive(s):>12.6f}   "
              f"stable {stable(s):>12.6f}")
    ```

    At $s = -800$ the naive form overflows to `inf` and takes your whole
    training run with it. The stable form is one call and never does. There
    is no reason to write the fragile version even once.

### Milestone 4 — verify the gradient

**Goal:** the analytic gradient
$-\beta\,(1 - \sigma(\text{margin}))$ applied `+` to the winner's logit and
`-` to the loser's, checked against a central finite difference
$\left(\mathcal{L}(\theta + h) - \mathcal{L}(\theta - h)\right) / 2h$.

**Done when...** the largest disagreement over all 20 parameters is below
$10^{-6}$ and an `assert` enforces it, so the check fails loudly rather than
printing two similar-looking arrays nobody reads.

??? tip "Hint"

    Twenty parameters means forty extra loss evaluations, and it catches
    every sign error you will ever make:

    ```python
    import numpy as np

    def loss(theta):
        return float(np.sum(theta ** 3))          # d/dx = 3x^2

    def finite_difference(theta, h=1e-6):
        grad = np.zeros_like(theta)
        for i in range(theta.size):
            up, down = theta.copy(), theta.copy()
            up[i] += h
            down[i] -= h
            grad[i] = (loss(up) - loss(down)) / (2 * h)
        return grad

    theta = np.array([1.0, -2.0, 0.5])
    print("analytic:", 3 * theta ** 2)
    print("numeric :", np.round(finite_difference(theta), 6))
    ```

    Use the *central* difference, not the one-sided one: its error shrinks
    like $h^2$ instead of $h$, which buys about six extra digits for the
    same effort. And read the analytic numbers as well as the check — a
    response that wins three pairs and loses none should have the most
    negative gradient, because descent subtracts it.

### Milestone 5 — train, then evaluate honestly

**Goal:** 300 steps of plain gradient descent from `theta = REF_LOGITS`,
recording the loss and mean margin; then a before/after probability table
per prompt and an **agreement** metric — the fraction of pairs whose winner
gets the higher implicit reward, ties counting as half.

**Done when...** the loss falls monotonically, the training pairs are all
ranked correctly, the reference scores exactly **50.0%** agreement (its
implicit reward is zero everywhere, so every pair is a tie), and you report
held-out agreement separately from training agreement.

??? tip "Hint"

    Do not judge the run by the loss reaching zero — it will not, and it
    should not. With $\beta = 0.1$, a loss of $0.2$ needs a log-ratio gap of
    about 15, which is a policy astronomically far from the reference:

    ```python
    import numpy as np

    print(f"{'target loss':>12}{'margin needed':>15}{'log-ratio gap':>15}")
    for target in (0.50, 0.30, 0.20, 0.05):
        margin = -np.log(np.expm1(target))        # invert -log sigmoid
        print(f"{target:>12.2f}{margin:>15.3f}{margin / 0.1:>15.1f}")
    ```

    Judge it by the margin, the ranking accuracy, and — the only number that
    generalises — agreement on pairs the training never saw.

### Milestone 6 — the baseline DPO has to beat

**Goal:** best-of-$n$ rejection sampling on the *same* reference and the
*same* annotator: draw $n$ responses, keep the highest-scoring one. Compute
its distribution in closed form rather than by sampling, so the baseline is
exact.

**Done when...** you can put reference, best-of-4, best-of-16, best-of-64
and DPO in one table with four columns — probability mass on the annotator's
favourite, KL from the reference, held-out agreement, and generations
required per query — and explain why best-of-$n$ scores 100% on held-out
agreement while being the *worse* option in production.

??? tip "Hint"

    Order the responses by score. The chance that best-of-$n$ returns $y$ is
    the chance all $n$ draws land in "$y$ or worse" minus the chance they
    all land strictly below $y$:

    ```python
    import numpy as np

    p_ref = np.array([0.5, 0.3, 0.2])
    scores = np.array([0.1, 0.9, 0.5])            # response 1 is the best

    for n in (1, 4, 16):
        best = np.array([p_ref[scores <= s].sum() ** n
                         - p_ref[scores < s].sum() ** n for s in scores])
        print(f"best-of-{n:<3}", np.round(best / best.sum(), 3))
    ```

    Two ceilings are hiding in that formula. Best-of-$n$ can never return a
    response the reference would not have sampled, and its cost is $n$
    generations *and one scorer call* on every query, for ever. DPO pays
    once, offline, and ships a model that is 1 generation per query with no
    scorer at all.

### Milestone 7 — sweep $\beta$ and plot it

**Goal:** retrain at $\beta \in \{0.02, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0\}$
with everything else fixed, and record final loss, KL from the reference,
train and held-out agreement, and probability mass on the top answer. Plot
KL and that probability against $\beta$ on a log axis.

**Done when...** the table shows both failure modes — a $\beta$ too small
that has barely moved after 300 steps, and a $\beta$ too large whose loss
crashes to near zero while the policy stops improving — and you can say in
one sentence what $\beta$ controls and what it does not.

??? tip "Hint"

    The gradient carries a factor of $\beta$ *and* a factor of
    $1 - \sigma(\text{margin})$, and those two pull in opposite directions:

    ```python
    import numpy as np

    log_ratio_gap = 30.0            # the same policy movement in every row
    print(f"{'beta':>6}{'step scale':>13}{'1 - sigma(margin)':>20}")
    for beta in (0.02, 0.1, 0.5, 2.0):
        margin = beta * log_ratio_gap
        print(f"{beta:>6.2f}{beta:>13.2f}"
              f"{1 - 1 / (1 + np.exp(-margin)):>20.6f}")
    ```

    Small $\beta$ shrinks every step, so 300 steps go almost nowhere. Large
    $\beta$ saturates the sigmoid after a handful of steps, after which
    $1 - \sigma \approx 0$ and training simply stops wherever it happens to
    be. $\beta = 0.1$ is the value most implementations default to, and the
    middle of that spread is why.

## Reference implementation

Read it as seven labelled regions matching the seven milestones. The
`assert` in region 4 is load-bearing: everything after it is only meaningful
because the gradient was checked.

??? success "Full reference implementation"

    ```python
    """Preference alignment with DPO: data, loss, gradient check, training, eval."""
    import numpy as np
    import matplotlib.pyplot as plt

    # ===================== 1. the policy and its reference ====================
    # Four prompts, five candidate responses each. Every response carries the
    # three attributes our synthetic annotator cares about, so the "true"
    # preference is a rule we can read rather than a mystery we must trust.
    #            name                      words  polite  on-topic
    CANDIDATES = [
        ("explain recursion", [
            ("one-line definition",           12, 1, 1),
            ("worked example",                45, 1, 1),
            ("wall of jargon",                90, 1, 1),
            ("curt 'just look it up'",         6, 0, 1),
            ("off-topic ramble",              70, 1, 0)]),
        ("apologise for the outage", [
            ("sorry + cause + fix",           40, 1, 1),
            ("just 'sorry'",                   4, 1, 1),
            ("blames the customer",           30, 0, 1),
            ("corporate word salad",          85, 1, 1),
            ("changelog dump",                60, 1, 0)]),
        ("decline a meeting invitation", [
            ("polite decline + reason",       28, 1, 1),
            ("one word: no",                   3, 0, 1),
            ("long apology tour",             95, 1, 1),
            ("polite decline, no reason",     12, 1, 1),
            ("asks about lunch instead",      20, 1, 0)]),
        ("summarise the release notes", [
            ("three-bullet summary",          35, 1, 1),
            ("verbatim changelog",           120, 1, 1),
            ("'read the docs'",                4, 0, 1),
            ("one-line summary",              14, 1, 1),
            ("marketing pitch",               50, 1, 0)]),
    ]

    PROMPTS = [prompt for prompt, _ in CANDIDATES]
    RESPONSES = [[name for name, *_ in options] for _, options in CANDIDATES]
    WORDS = np.array([[w for _, w, _, _ in options] for _, options in CANDIDATES],
                     dtype=float)
    POLITE = np.array([[p for *_, p, _ in options] for _, options in CANDIDATES],
                      dtype=float)
    ON_TOPIC = np.array([[t for *_, t in options] for _, options in CANDIDATES],
                        dtype=float)
    N_PROMPTS, N_RESPONSES = WORDS.shape

    # The frozen reference: an untuned checkpoint with a length bias, which is
    # what supervised fine-tuning on scraped text tends to produce. Its logits
    # are proportional to response length and to nothing else.
    REF_LOGITS = 0.02 * WORDS
    BETA = 0.1


    def softmax(z):
        e = np.exp(z - z.max())
        return e / e.sum()


    def log_softmax(z):
        m = z.max()
        return z - m - np.log(np.exp(z - m).sum())


    # ================== 2. the annotator and the preference data ==============
    def annotator_score(prompt_i, response_i):
        """A rule-based stand-in for a human labeller: concise, polite,
        on-topic.

        Concise means *about thirty words*, not "as short as possible" — a
        quadratic penalty either side, so a three-word brush-off loses too. The
        weights are the whole ground truth of this project: everything DPO
        learns has to come through the pairs this function labels.
        """
        words = WORDS[prompt_i, response_i]
        length_penalty = -((words - 30.0) / 40.0) ** 2
        return (length_penalty
                + 1.0 * POLITE[prompt_i, response_i]
                + 1.5 * ON_TOPIC[prompt_i, response_i])


    TRUE_SCORES = np.array([[annotator_score(p, j) for j in range(N_RESPONSES)]
                            for p in range(N_PROMPTS)])


    def build_pairs(n_train=12, margin=0.30, seed=0):
        """Every decisive comparison, shuffled, split into train and held-out.

        Pairs whose scores are within `margin` are dropped: real annotators
        disagree on close calls, and a coin-flip label is noise you would be
        training on with total confidence.
        """
        everything = [(p, a, b) if TRUE_SCORES[p, a] > TRUE_SCORES[p, b]
                      else (p, b, a)
                      for p in range(N_PROMPTS)
                      for a in range(N_RESPONSES)
                      for b in range(a + 1, N_RESPONSES)
                      if abs(TRUE_SCORES[p, a] - TRUE_SCORES[p, b]) >= margin]
        order = np.random.default_rng(seed).permutation(len(everything))
        shuffled = [everything[i] for i in order]
        return shuffled[:n_train], shuffled[n_train:]


    TRAIN_PAIRS, HELD_OUT_PAIRS = build_pairs()


    # ============================ 3. the DPO loss =============================
    def margins(theta, pairs, beta=BETA):
        """beta * (r_hat(winner) - r_hat(loser)) for each pair.

        r_hat is the *implicit* reward: beta times the policy's log-ratio
        against the frozen reference. No reward model computes this — the
        policy is the reward model, viewed sideways.
        """
        out = []
        for p, win, lose in pairs:
            policy, reference = log_softmax(theta[p]), log_softmax(REF_LOGITS[p])
            out.append(beta * ((policy[win] - reference[win])
                               - (policy[lose] - reference[lose])))
        return np.array(out)


    def dpo_loss(theta, pairs, beta=BETA):
        """-log sigmoid(margin), averaged: ordinary binary cross-entropy."""
        s = margins(theta, pairs, beta)
        return float(np.mean(np.logaddexp(0.0, -s)))       # stable -log sigmoid


    def dpo_grad(theta, pairs, beta=BETA):
        """Analytic gradient: -(1 - sigma(margin)) * beta * (push up, pull down).

        Pairs the policy already ranks correctly have sigma near 1 and so
        contribute almost nothing — descent spends its budget on what is wrong.
        """
        grad = np.zeros_like(theta)
        for (p, win, lose), s in zip(pairs, margins(theta, pairs, beta)):
            sigma = 1.0 / (1.0 + np.exp(-s))
            coefficient = -(1.0 - sigma) * beta
            grad[p, win] += coefficient          # raise the winner's log-prob
            grad[p, lose] -= coefficient         # lower the loser's
        return grad / len(pairs)


    # ========================= 4. the gradient check ==========================
    def finite_difference_grad(theta, pairs, beta=BETA, h=1e-6):
        """The ruler you measure the analytic gradient against."""
        grad = np.zeros_like(theta)
        for i in range(theta.shape[0]):
            for j in range(theta.shape[1]):
                up, down = theta.copy(), theta.copy()
                up[i, j] += h
                down[i, j] -= h
                grad[i, j] = (dpo_loss(up, pairs, beta)
                              - dpo_loss(down, pairs, beta)) / (2 * h)
        return grad


    # ============================ 5. evaluation ===============================
    def implicit_reward(theta, beta=BETA):
        """beta * log(policy / reference), the reward DPO never had to build."""
        return beta * np.array([np.log(softmax(theta[p]))
                                - np.log(softmax(REF_LOGITS[p]))
                                for p in range(N_PROMPTS)])


    def agreement(reward, pairs):
        """Fraction of pairs this reward ranks the way the annotator did.

        Ties count as half, so a policy identical to the reference — whose
        implicit reward is exactly zero everywhere — scores 50%: chance.
        """
        votes = []
        for p, win, lose in pairs:
            gap = reward[p, win] - reward[p, lose]
            votes.append(1.0 if gap > 1e-12 else (0.5 if abs(gap) <= 1e-12 else 0.0))
        return float(np.mean(votes))


    def kl_from_reference(theta):
        """Mean KL(policy || reference) over the prompts: the price of moving."""
        total = 0.0
        for p in range(N_PROMPTS):
            a, b = softmax(theta[p]), softmax(REF_LOGITS[p])
            total += float(np.sum(a * np.log(a / b)))
        return total / N_PROMPTS


    def train(pairs, beta=BETA, steps=300, lr=2.0, record=False):
        """Plain gradient descent. DPO always starts the policy AT the reference."""
        theta = REF_LOGITS.copy()
        history = []
        for _ in range(steps):
            if record:
                history.append((dpo_loss(theta, pairs, beta),
                                float(margins(theta, pairs, beta).mean())))
            theta -= lr * dpo_grad(theta, pairs, beta)
        if record:
            history.append((dpo_loss(theta, pairs, beta),
                            float(margins(theta, pairs, beta).mean())))
        return theta, history


    # ==================== 6. the rejection-sampling baseline ==================
    def best_of_n_distribution(prompt_i, n):
        """Exact distribution of best-of-n sampling — no sampling required.

        Draw n responses from the reference and keep the annotator's favourite.
        Order the responses by score; the chance the winner is `y` is the chance
        all n draws land in {y or worse} minus the chance they all land strictly
        below y. Closed form, so the baseline is exact rather than noisy.
        """
        p_ref = softmax(REF_LOGITS[prompt_i])
        scores = TRUE_SCORES[prompt_i]
        probability = np.zeros(N_RESPONSES)
        for j in range(N_RESPONSES):
            at_or_below = p_ref[scores <= scores[j]].sum()
            strictly_below = p_ref[scores < scores[j]].sum()
            probability[j] = at_or_below ** n - strictly_below ** n
        return probability / probability.sum()


    def best_of_n_policy(n):
        """Return best-of-n as logits, so every metric above applies unchanged."""
        return np.log(np.array([best_of_n_distribution(p, n)
                                for p in range(N_PROMPTS)]))


    # =============================== driver ===================================
    print("=" * 70)
    print("1. the frozen reference, and what the annotator actually wants")
    print("=" * 70)
    print(f"{'prompt':<30}{'reference favourite':<26}{'annotator favourite':<26}")
    for p, prompt in enumerate(PROMPTS):
        ref_best = RESPONSES[p][int(np.argmax(REF_LOGITS[p]))]
        true_best = RESPONSES[p][int(np.argmax(TRUE_SCORES[p]))]
        print(f"{prompt:<30}{ref_best:<26}{true_best:<26}")
    ref_probs = np.array([softmax(REF_LOGITS[p]) for p in range(N_PROMPTS)])
    print(f"\nthe reference is length-biased by construction: correlation between "
          f"log P(response)\nand its word count is "
          f"{np.corrcoef(np.log(ref_probs).ravel(), WORDS.ravel())[0, 1]:+.3f}")
    print(f"reference mass on the annotator's favourite: "
          f"{np.mean([ref_probs[p, np.argmax(TRUE_SCORES[p])] for p in range(N_PROMPTS)]):.1%}")

    print("\n" + "=" * 70)
    print("2. preference pairs from a rule-based annotator")
    print("=" * 70)
    print(f"{len(TRAIN_PAIRS)} training pairs, {len(HELD_OUT_PAIRS)} held out "
          f"(close calls within 0.30 were dropped as noise)\n")
    print(f"{'prompt':<22}{'preferred':<26}{'over':<26}{'gap':>6}")
    for p, win, lose in TRAIN_PAIRS:
        gap = TRUE_SCORES[p, win] - TRUE_SCORES[p, lose]
        print(f"{PROMPTS[p][:20]:<22}{RESPONSES[p][win]:<26}"
              f"{RESPONSES[p][lose]:<26}{gap:>6.2f}")

    print("\n" + "=" * 70)
    print("3 + 4. the loss, and the gradient check that makes it trustworthy")
    print("=" * 70)
    theta0 = REF_LOGITS.copy()
    print(f"loss at the reference: {dpo_loss(theta0, TRAIN_PAIRS):.6f}"
          f"   (= -log 0.5 = {np.log(2):.6f}, because policy == reference means"
          f" every margin is 0)")
    analytic = dpo_grad(theta0, TRAIN_PAIRS)
    numeric = finite_difference_grad(theta0, TRAIN_PAIRS)
    print(f"analytic gradient, prompt 0: {np.round(analytic[0], 6)}")
    print(f"numeric  gradient, prompt 0: {np.round(numeric[0], 6)}")
    worst = float(np.abs(analytic - numeric).max())
    print(f"worst disagreement over all {theta0.size} parameters: {worst:.2e}")
    assert worst < 1e-6, "the analytic gradient is wrong"
    print("gradient check passed")

    print("\n" + "=" * 70)
    print("5. training")
    print("=" * 70)
    theta, history = train(TRAIN_PAIRS, record=True)
    losses = [loss for loss, _ in history]
    mean_margins = [margin for _, margin in history]
    print(f"{'step':>6}{'loss':>10}{'mean margin':>14}{'train ranking':>15}")
    for step in (0, 25, 50, 100, 200, 300):
        partial, _ = train(TRAIN_PAIRS, steps=step)
        correct = int((margins(partial, TRAIN_PAIRS) > 0).sum())
        print(f"{step:>6}{losses[step]:>10.4f}{mean_margins[step]:>14.4f}"
              f"{correct:>12}/{len(TRAIN_PAIRS)}")

    reward = implicit_reward(theta)
    print(f"\ntrain-set agreement    {agreement(reward, TRAIN_PAIRS):>7.1%}")
    print(f"held-out agreement     {agreement(reward, HELD_OUT_PAIRS):>7.1%}"
          f"   (the reference scores 50.0%: every implicit reward is 0)")
    print(f"KL from the reference  {kl_from_reference(theta):>7.3f} nats")
    missed = [(p, w, l) for p, w, l in HELD_OUT_PAIRS
              if reward[p, w] - reward[p, l] <= 1e-12]
    print(f"\nheld-out pairs it does not get right ({len(missed)} of "
          f"{len(HELD_OUT_PAIRS)}):")
    for p, win, lose in missed:
        tie = abs(reward[p, win] - reward[p, lose]) <= 1e-12
        print(f"   {PROMPTS[p][:20]:<22}{RESPONSES[p][win]:<26}"
              f"{'ties with' if tie else 'ranked below':<14}"
              f"{RESPONSES[p][lose]}")

    print("\nbefore and after, per prompt:")
    for p, prompt in enumerate(PROMPTS):
        before, after = softmax(REF_LOGITS[p]), softmax(theta[p])
        print(f"\n  {prompt!r}   (rank = the annotator's order)")
        print(f"   {'response':<28}{'rank':>5}{'reference':>11}{'policy':>9}"
              f"{'change':>9}{'implicit r':>12}")
        for j in np.argsort(-TRUE_SCORES[p]):
            rank = int(np.sum(TRUE_SCORES[p] > TRUE_SCORES[p, j])) + 1
            print(f"   {RESPONSES[p][j]:<28}{rank:>5}{before[j]:>11.3f}"
                  f"{after[j]:>9.3f}{after[j] - before[j]:>+9.3f}"
                  f"{reward[p, j]:>12.3f}")

    print("\n" + "=" * 70)
    print("6. what DPO buys you, against a rejection-sampling baseline")
    print("=" * 70)
    print(f"{'method':<24}{'P(top answer)':>15}{'KL from ref':>13}"
          f"{'held-out':>11}{'generations / query':>21}")
    rows = [("reference (untuned)", REF_LOGITS.copy(), 0),
            ("best-of-4 sampling", best_of_n_policy(4), 4),
            ("best-of-16 sampling", best_of_n_policy(16), 16),
            ("best-of-64 sampling", best_of_n_policy(64), 64),
            (f"DPO, {len(TRAIN_PAIRS)} pairs", theta, 1)]
    for label, logits, generations in rows:
        probability = np.array([softmax(logits[p])[np.argmax(TRUE_SCORES[p])]
                                for p in range(N_PROMPTS)])
        print(f"{label:<24}{probability.mean():>15.1%}"
              f"{kl_from_reference(logits):>13.3f}"
              f"{agreement(implicit_reward(logits), HELD_OUT_PAIRS):>11.1%}"
              f"{generations:>21}")
    print("\nbest-of-n needs the annotator at inference time, every single query,")
    print("and can never produce a response the reference would not have sampled.")
    print("DPO pays once, offline, from 12 comparisons and no scorer at run time.")

    print("\n" + "=" * 70)
    print("7. what beta does")
    print("=" * 70)
    BETAS = [0.02, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0]
    sweep = []
    print(f"{'beta':>6}{'final loss':>12}{'KL from ref':>13}{'train':>9}"
          f"{'held-out':>10}{'P(top answer)':>15}")
    for beta in BETAS:
        th, _ = train(TRAIN_PAIRS, beta=beta)
        r = implicit_reward(th, beta)
        top = np.mean([softmax(th[p])[np.argmax(TRUE_SCORES[p])]
                       for p in range(N_PROMPTS)])
        sweep.append((beta, kl_from_reference(th),
                      agreement(r, HELD_OUT_PAIRS), top))
        print(f"{beta:>6.2f}{dpo_loss(th, TRAIN_PAIRS, beta):>12.4f}"
              f"{kl_from_reference(th):>13.3f}"
              f"{agreement(r, TRAIN_PAIRS):>9.1%}"
              f"{agreement(r, HELD_OUT_PAIRS):>10.1%}{top:>15.1%}")

    fig, axes = plt.subplots(1, 3, figsize=(11.0, 3.2))
    axes[0].plot(losses, label="loss")
    axes[0].set_xlabel("gradient step")
    axes[0].set_ylabel("DPO loss")
    axes[0].set_title(f"training, beta = {BETA}")
    axes[1].plot(mean_margins, color="tab:orange")
    axes[1].set_xlabel("gradient step")
    axes[1].set_ylabel("mean implicit-reward margin")
    axes[1].set_title("margin")
    axes[2].semilogx([b for b, *_ in sweep], [kl for _, kl, *_ in sweep],
                     marker="o", label="KL from reference (nats)")
    axes[2].semilogx([b for b, *_ in sweep], [top for *_, top in sweep],
                     marker="s", label="P(annotator's favourite)")
    axes[2].set_xlabel("beta (log scale)")
    axes[2].set_ylabel("nats / probability")
    axes[2].set_title("300 steps at every beta")
    axes[2].legend(fontsize=8)
    fig.tight_layout()
    ```

    Four things in that output are worth more than the headline number.

    **The held-out failures are informative, not embarrassing.** Four of 22
    held-out pairs come out wrong, and three of them are *ties*: responses
    that appear in no training pair end up with identical implicit rewards,
    because the only thing that moved them was the softmax renormalising
    around the responses that did appear. DPO is offline — it knows about
    exactly the comparisons you gave it and nothing else. The fourth is a
    genuine inversion: `marketing pitch` was pushed down in two training
    pairs and `verbatim changelog` in only one, so the policy now ranks them
    the wrong way round on a comparison it never saw.

    **The loss stalls at 0.478 and that is healthy.** All twelve training
    pairs are ranked correctly by step 25, while the loss is still 0.6695.
    Ranking accuracy and loss answer different questions.

    **$\beta$ controls distance, not direction.** Held-out agreement is
    88.6% at every $\beta$ in the sweep — the *ordering* DPO learns from
    these twelve pairs is the same one every time. What $\beta$ changes is
    how far the policy travels to express it, and the probability mass on
    the best answer peaks at 96.5% for $\beta = 0.5$ and then *falls* to
    80.0% at $\beta = 2.0$, where the sigmoid saturates and training stops
    early.

    **Both likelihoods can fall.** Watch `just 'sorry'` under the apology
    prompt: the annotator ranks it second, and DPO drove it from 7.8% down
    to 0.7%. The objective only ever constrained *differences*, and mass has
    to go somewhere. Logging absolute log-probabilities, not just margins,
    is how you catch this on a real run.

## Going further

- **GRPO on the same setup.** Replace the pairs with the annotator used as
  a *verifier*: sample a group of $G = 8$ responses per prompt from the
  current policy, set
  $A_i = (r_i - \text{mean}(r)) / \text{std}(r)$, and apply the policy
  gradient with those advantages, exactly as
  [31.3](../../ch31-rl/03-dpo-grpo.md) does. Then count the zero-variance
  groups — the ones where every sampled response scored the same and the
  entire group produced no gradient at all. You will pay full generation
  cost for an empty update, and watching that number climb as the policy
  improves is the whole argument for difficulty curation.
- **A preference conflict, on purpose.** Add pairs from a second annotator
  who weights politeness at $3.0$ and ignores length. Some pairs will now
  contradict the first annotator's. Train on the union and measure
  agreement against *each* annotator separately: the policy lands somewhere
  between them and satisfies neither, and the loss gives no hint that
  anything is wrong. This is what a preference dataset built by two teams
  with different rubrics does to a model, and it is why
  [31.4](../../ch31-rl/04-reward-models.md) insists that inter-annotator
  agreement is a number you must measure before you train on anything.
- **Label noise.** Flip the label on 2 of the 12 pairs and retrain. DPO has
  no sampling step to contradict a bad label, so it fits the mistakes with
  total confidence — plot held-out agreement against the number of flipped
  labels and you have priced your annotation quality.
- **An SFT term to hold the winners up.** Add
  $\lambda \sum_{\text{pairs}} -\log \pi_\theta(y_w)$ to the loss and sweep
  $\lambda$. Track the chosen responses' absolute log-probabilities: this is
  the standard mitigation for the "both likelihoods fell" failure, and you
  can now show it working rather than quote it.
- **Length-controlled evaluation.** Your annotator's strongest signal is
  length. Re-run the held-out agreement using only pairs whose two responses
  are within ten words of each other, and see how much of the 88.6% was
  really "the model learned to prefer answers of about thirty words". The
  same control is what [33.3](../../ch33-eval/03-llm-as-judge.md) applies to
  an LLM judge, for exactly the same reason.
- **More prompts, fewer pairs per prompt.** Twelve pairs spread over four
  prompts is three per prompt. Try twelve prompts with one pair each and the
  same total budget. Which generalises better on held-out comparisons, and
  what does that tell you about how to spend a real annotation budget?
