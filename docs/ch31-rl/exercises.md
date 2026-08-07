# Chapter 31 · Exercises

Eight problems on the whole post-training pipeline, easiest first. They build on
[31.1](01-rl-basics.md), [31.2](02-policy-gradient-ppo.md),
[31.3](03-dpo-grpo.md) and [31.4](04-reward-models.md), and every solution runs
in the browser on numpy alone. Exercise 31.3 asks you to **predict** the output
before running it — write your predictions down first, because the gap between
your list and the printed one is the whole lesson of the clipped objective.

Nothing here calls a model or touches the network. Every policy is a softmax
over a handful of logits and every reward is a function you can read.

---

### Exercise 31.1 — Tune epsilon and read the regret curve (●)

Take the three-armed bandit of [31.1](01-rl-basics.md) — true payout
probabilities `[0.30, 0.55, 0.50]` — and compare four exploration settings:
$\varepsilon = 0$, $\varepsilon = 0.05$, $\varepsilon = 0.30$, and a **decaying**
schedule $\varepsilon_t = 1/\sqrt{t+1}$.

Plot the cumulative regret of each and answer: which finishes with the least
regret, and *why* does the decaying schedule beat both fixed extremes?

??? success "Solution"

    ```python
    import numpy as np
    import matplotlib.pyplot as plt

    TRUE_MEANS = np.array([0.30, 0.55, 0.50])
    BEST = TRUE_MEANS.max()

    def run(eps_fn, n_steps=3000, seed=1):
        rng = np.random.default_rng(seed)
        Q, N = np.zeros(3), np.zeros(3)
        regret, running = np.zeros(n_steps), 0.0
        for t in range(n_steps):
            eps = eps_fn(t)
            a = int(rng.integers(3)) if rng.random() < eps else int(Q.argmax())
            reward = float(rng.random() < TRUE_MEANS[a])
            N[a] += 1
            Q[a] += (reward - Q[a]) / N[a]
            running += BEST - TRUE_MEANS[a]
            regret[t] = running
        return Q, N, regret

    schedules = {
        "eps = 0.00":     lambda t: 0.0,
        "eps = 0.05":     lambda t: 0.05,
        "eps = 0.30":     lambda t: 0.30,
        "eps = 1/sqrt(t)": lambda t: 1.0 / np.sqrt(t + 1),
    }

    fig, ax = plt.subplots(figsize=(7.0, 3.4))
    print(f"{'schedule':>16}{'final regret':>14}{'pulls of best arm':>20}")
    for name, fn in schedules.items():
        Q, N, regret = run(fn)
        ax.plot(regret, label=name)
        print(f"{name:>16}{regret[-1]:>14.1f}{int(N[1]):>15}/3000")
    ax.set_xlabel("pull number")
    ax.set_ylabel("cumulative regret")
    ax.set_title("Four exploration schedules")
    ax.legend()
    fig.tight_layout()
    ```

    The decaying schedule wins. Read the curves as slopes: $\varepsilon = 0$ is
    a straight line because a greedy agent starting from $Q = [0,0,0]$ locks
    onto arm 0 and never re-examines it. $\varepsilon = 0.30$ bends over
    quickly — it identifies the best arm fast — but then keeps a permanent
    straight-line component, because 30% of every future pull is still thrown
    away at random forever.

    $\varepsilon_t = 1/\sqrt{t+1}$ gets both halves right: it explores almost
    constantly at the start, when information is worth the most, and by pull
    2500 it is exploring about 2% of the time, so its curve is nearly flat at
    the end. Exploration is an investment; the correct schedule spends early
    and coasts later. Every serious bandit algorithm (UCB, Thompson sampling)
    is a more principled version of exactly this idea.

---

### Exercise 31.2 — Check an analytic gradient numerically (●)

Someone hands you this claim about the Bradley-Terry reward-model loss of
[31.4](04-reward-models.md). For a single preference pair with feature
difference $d = x_w - x_l$ and weights $w$:

$$
L(w) = -\log \sigma(w \cdot d)
\qquad\qquad
\nabla_w L = -\big(1 - \sigma(w \cdot d)\big)\, d
$$

Do not take it on trust. Write `finite_difference` and check the claim at three
different $w$ vectors. Then check a *deliberately wrong* version — one that
forgets the $(1 - \sigma)$ factor — and confirm your check catches it.

??? success "Solution"

    ```python
    import numpy as np

    d = np.array([1.0, -0.5, 2.0])          # x_winner - x_loser

    def sigmoid(z):
        return 1.0 / (1.0 + np.exp(-z))

    def loss(w):
        return float(-np.log(sigmoid(w @ d)))

    def analytic_grad(w):
        return -(1.0 - sigmoid(w @ d)) * d

    def wrong_grad(w):                       # forgot the (1 - sigma) factor
        return -d

    def finite_difference(f, w, h=1e-6):
        g = np.zeros_like(w)
        for k in range(len(w)):
            up, down = w.copy(), w.copy()
            up[k] += h
            down[k] -= h
            g[k] = (f(up) - f(down)) / (2 * h)
        return g

    print(f"{'w':>22}{'max |analytic - numeric|':>27}{'max |wrong - numeric|':>24}")
    for w in [np.zeros(3), np.array([0.5, 1.0, -0.3]), np.array([2.0, 0.0, 1.0])]:
        num = finite_difference(loss, w)
        ok = np.abs(analytic_grad(w) - num).max()
        bad = np.abs(wrong_grad(w) - num).max()
        print(f"{str(np.round(w, 2)):>22}{ok:>27.2e}{bad:>24.4f}")

    w = np.array([0.5, 1.0, -0.3])
    assert np.abs(analytic_grad(w) - finite_difference(loss, w)).max() < 1e-6
    print("\nanalytic gradient verified; the 'wrong' version is off by a factor "
          f"of {1 / (1 - sigmoid(w @ d)):.2f} at w = [0.5, 1.0, -0.3]")
    ```

    The analytic gradient agrees to about ten decimal places at every point;
    the broken one is off by a factor of $1/(1 - \sigma)$, which grows without
    bound as the model gets the pair more and more right. That is exactly the
    kind of bug that does not crash — it just trains too hard on examples the
    model already has correct. Two loops and twenty seconds of compute is a
    very cheap way never to ship it.

---

### Exercise 31.3 — Predict what clipping does (●●)

**Predict before you run.** For PPO with $\epsilon = 0.2$, work out for each row
below: (a) the unclipped objective $rA$, (b) the clipped objective, (c) which
one the `min` selects, and (d) whether the gradient is alive or zero.

| ratio $r$ | advantage $A$ |
| --- | --- |
| 1.00 | +3.0 |
| 1.35 | +3.0 |
| 0.60 | +3.0 |
| 1.35 | −3.0 |
| 0.60 | −3.0 |

Write your five answers down, then run the code.

??? success "Solution"

    ```python
    import numpy as np

    EPS = 0.2

    def ppo_terms(ratio, adv, eps=EPS):
        unclipped = ratio * adv
        clipped = float(np.clip(ratio, 1 - eps, 1 + eps)) * adv
        chosen = min(unclipped, clipped)
        # The clipped branch is constant in theta, so the gradient dies exactly
        # when the min picks it *and* the ratio is outside the trust region.
        frozen = (adv > 0 and ratio > 1 + eps) or (adv < 0 and ratio < 1 - eps)
        return unclipped, clipped, chosen, "zero" if frozen else "live"

    print(f"{'ratio':>7}{'A':>7}{'r*A':>9}{'clip*A':>9}{'min picks':>11}{'grad':>7}")
    for ratio, adv in [(1.00, 3.0), (1.35, 3.0), (0.60, 3.0),
                       (1.35, -3.0), (0.60, -3.0)]:
        u, c, chosen, grad = ppo_terms(ratio, adv)
        which = "unclipped" if chosen == u else "clipped"
        print(f"{ratio:>7.2f}{adv:>7.1f}{u:>9.2f}{c:>9.2f}{which:>11}{grad:>7}")
    ```

    Row by row:

    - **(1.00, +3)** — inside the region, both terms are 3.00, gradient live.
    - **(1.35, +3)** — 4.05 versus 3.60; the `min` takes 3.60, which no longer
      depends on $\theta$, so the gradient is **zero**. We have already pushed
      this good action far enough.
    - **(0.60, +3)** — 1.80 versus 2.40; the `min` takes the *unclipped* 1.80,
      gradient **live**. A good action whose probability has fallen still gets
      pulled back up. This is the asymmetry the `min` exists to create.
    - **(1.35, −3)** — −4.05 versus −3.60; the `min` takes −4.05, unclipped,
      gradient **live**. A bad action that became *more* likely is still
      penalised, with no ceiling.
    - **(0.60, −3)** — −1.80 versus −2.40; the `min` takes −2.40, constant,
      gradient **zero**. We have suppressed this bad action enough.

    The pattern: the clip removes the incentive only in the direction you were
    already overshooting. In both of the other directions the gradient is fully
    alive, which is what stops the policy from wandering off and staying there.

---

### Exercise 31.4 — Group-relative advantages by hand (●●)

A GRPO group of eight responses to one prompt is scored by a verifier:

```text
group A rewards:  1  0  1  1  0  0  0  1
group B rewards:  1  1  1  1  1  1  0  1
```

By hand, compute the mean, the (population) standard deviation, and the
advantage $A_i = (r_i - \bar r)/\text{std}(r)$ for a correct and an incorrect
response in **each** group. Then verify with code, and answer: why does being
right earn so much less in group B, and what does that tell you about which
prompts belong in a GRPO training set?

??? success "Solution"

    By hand for group A: $\bar r = 4/8 = 0.5$, variance
    $= 0.5 \times 0.5 = 0.25$, so std $= 0.5$. A correct response gets
    $(1 - 0.5)/0.5 = +1$ and an incorrect one $-1$.

    Group B: $\bar r = 7/8 = 0.875$, variance
    $= 0.875 \times 0.125 = 0.109375$, std $= 0.3307$. Correct gets
    $0.125 / 0.3307 = +0.378$; the single failure gets
    $-0.875 / 0.3307 = -2.646$.

    ```python
    import numpy as np

    groups = {"A": np.array([1., 0., 1., 1., 0., 0., 0., 1.]),
              "B": np.array([1., 1., 1., 1., 1., 1., 0., 1.]),
              "C (all correct)": np.ones(8)}

    print(f"{'group':>16}{'mean':>8}{'std':>9}{'A(correct)':>13}{'A(wrong)':>11}")
    for name, r in groups.items():
        mean, std = r.mean(), r.std()
        if std < 1e-8:
            print(f"{name:>16}{mean:>8.3f}{std:>9.3f}{'0 (dead)':>13}{'—':>11}")
            continue
        adv = (r - mean) / std
        right = float(adv[r == 1][0])
        wrong = float(adv[r == 0][0]) if (r == 0).any() else float("nan")
        print(f"{name:>16}{mean:>8.3f}{std:>9.3f}{right:>13.3f}{wrong:>11.3f}")
        assert abs(adv.mean()) < 1e-9 and abs(adv.std() - 1) < 1e-9
    print("\nevery group's advantages have mean 0 and std 1 — that is the point "
          "of dividing by the standard deviation")
    ```

    Being right in group B earns $+0.378$ instead of $+1$ because in group B it
    is *not surprising*: the policy already solves this prompt six times out of
    eight, so there is little left to learn. Nearly all of group B's gradient
    comes from the one failure, at $-2.646$.

    Group C is the limiting case: all eight correct, standard deviation zero,
    every advantage zero, **no gradient at all** — eight generations bought
    nothing. That is why GRPO pipelines curate the prompt set to problems the
    model solves *sometimes*. A prompt the model always gets right and a prompt
    it always gets wrong are equally worthless, and both cost full generation
    price.

---

### Exercise 31.5 — Which signal saw the mistake? (●●)

Here is a worked solution to *"A tank holds 6 crates of 9 bottles. 12 bottles
are removed for testing, and then 2 more break. How many are left?"* The
correct answer is 40.

```text
step 1:  6 * 9   = 54
step 2:  54 - 12 = 42
step 3:  42 - 2  = 40
```

And here is a second trace that also ends at 40:

```text
step 1:  6 * 9   = 44
step 2:  44 - 2  = 42
step 3:  42 - 2  = 40
```

Say what an outcome reward model and a process reward model each report for
both traces, then implement both and confirm. Which step does the PRM blame,
and what would training on the ORM signal alone teach the model?

??? success "Solution"

    ```python
    PROBLEM_NUMBERS = {6, 9, 12, 2}
    ANSWER = 40

    TRACES = {
        "sound": [(6, "*", 9, 54), (54, "-", 12, 42), (42, "-", 2, 40)],
        "lucky": [(6, "*", 9, 44), (44, "-", 2, 42), (42, "-", 2, 40)],
    }

    def apply_op(a, op, b):
        return {"*": a * b, "-": a - b}[op]

    def step_is_valid(step, previous):
        a, op, b, claimed = step
        inputs_ok = ((a in PROBLEM_NUMBERS or a == previous) and
                     (b in PROBLEM_NUMBERS or b == previous))
        return inputs_ok and apply_op(a, op, b) == claimed

    def orm(trace):
        return 1.0 if trace[-1][3] == ANSWER else 0.0

    def prm(trace):
        out, previous = [], None
        for step in trace:
            out.append(1.0 if step_is_valid(step, previous) else 0.0)
            previous = step[3]
        return out

    for name, trace in TRACES.items():
        per_step = prm(trace)
        blame = [i for i, s in enumerate(per_step) if s == 0.0]
        print(f"{name:<7} ORM = {orm(trace):.1f}   "
              f"PRM = {sum(per_step) / len(per_step):.2f}   per-step {per_step}"
              f"   blamed steps: {blame}")
    ```

    The ORM gives **1.0 to both** — it can only see the final 40, and both
    traces produce it. The PRM gives 1.00 and 0.67, and blames step 0 of the
    `lucky` trace, where $6 \times 9$ was claimed to be 44.

    Notice how the lucky trace got away with it. Its first step is 10 too low,
    and its second step subtracts 2 instead of 12 — an error of exactly $+10$
    that cancels the first. Both later steps are *internally* valid: 44 − 2
    really is 42, and 2 really is one of the problem's numbers, so even the
    provenance check passes. The trace is arithmetically self-consistent from
    step 1 onward and still wrong, which is precisely the shape a confident
    model error takes.

    Training on the ORM signal alone reinforces the whole trace, including
    "$6 \times 9 = 44$", with the same strength as the sound derivation — you
    would be teaching the model a false multiplication fact because the answer
    happened to come out right.

---

### Exercise 31.6 — Poison one preference pair (●●)

Take the DPO setup from [31.3](03-dpo-grpo.md) and flip a single label: change
the pair `worked example > wall of jargon` into `wall of jargon > worked
example`. Everything else stays identical.

Train both versions and report: what happens to `worked example`'s probability,
what happens to `wall of jargon`'s, and does the loss curve warn you?

??? success "Solution"

    ```python
    import numpy as np

    REF_LOGITS = np.array([0.5, 0.0, 1.0, -0.5, 0.0])      # one prompt, 5 responses
    RESPONSES = ["one-line definition", "worked example", "wall of jargon",
                 "flatly wrong", "off-topic ramble"]
    CLEAN     = [(1, 0), (1, 2), (0, 3), (1, 3)]           # (winner, loser)
    POISONED  = [(1, 0), (2, 1), (0, 3), (1, 3)]           # pair 2 flipped
    BETA = 0.1

    def softmax(z):
        e = np.exp(z - z.max())
        return e / e.sum()

    def log_softmax(z):
        m = z.max()
        return z - m - np.log(np.exp(z - m).sum())

    def loss_and_grad(theta, pairs):
        lp, lref = log_softmax(theta), log_softmax(REF_LOGITS)
        loss, grad = 0.0, np.zeros_like(theta)
        for w, l in pairs:
            s = BETA * ((lp[w] - lref[w]) - (lp[l] - lref[l]))
            sigma = 1.0 / (1.0 + np.exp(-s))
            loss += -np.log(sigma)
            coef = -(1.0 - sigma) * BETA
            grad[w] += coef
            grad[l] -= coef
        return loss / len(pairs), grad / len(pairs)

    results = {}
    for name, pairs in [("clean", CLEAN), ("poisoned", POISONED)]:
        theta, curve = REF_LOGITS.copy(), []
        for _ in range(150):
            loss, grad = loss_and_grad(theta, pairs)
            curve.append(loss)
            theta -= 1.0 * grad
        results[name] = (softmax(theta), curve)
        print(f"{name:>9}: loss {curve[0]:.4f} -> {curve[-1]:.4f}")

    print(f"\n{'response':<22}{'reference':>11}{'clean':>9}{'poisoned':>11}")
    ref = softmax(REF_LOGITS)
    for j, name in enumerate(RESPONSES):
        print(f"{name:<22}{ref[j]:>11.3f}{results['clean'][0][j]:>9.3f}"
              f"{results['poisoned'][0][j]:>11.3f}")
    ```

    One flipped label out of four inverts the result. With clean data `worked
    example` reaches 0.971 and `wall of jargon` is crushed to 0.005. With the
    single poisoned pair, `worked example` collapses to 0.193 and `wall of
    jargon` — the response the reference model was already over-producing —
    ends up the policy's *most likely* output at 0.705. One bad label out of
    four did not degrade the model slightly; it trained the opposite model.

    The damage also spreads beyond the flipped pair, because softmax is
    competitive: every unit of probability that stays with `wall of jargon` is
    a unit that never reaches anything else, so `one-line definition` ends
    higher too (0.061 against 0.015) purely as a side effect.

    And the loss curve gives you **no warning**. Both runs descend smoothly and
    monotonically from $\log 2$; the poisoned run simply settles a little
    higher (0.5787 against 0.4589), because contradictory pairs pull the policy
    in opposite directions and it lands somewhere that partially satisfies
    both. Without the clean run printed beside it you would call that a healthy
    curve. A falling loss means the model is fitting your labels; it says
    nothing about whether your labels are right — which is why annotation
    quality, and the kappa of [31.4](04-reward-models.md), are not optional.

---

### Exercise 31.7 — Design a reward, then break it (●●)

The task: *summarise a customer support ticket*. A colleague proposes this
reward, arguing that a good summary must mention the important things:

> reward = fraction of the ticket's key terms that appear in the summary

Implement it, then find a response that scores 1.0 and is useless as a summary.
State the general lesson in one sentence, and name one change that would help.

??? success "Solution"

    ```python
    KEY_TERMS = ["refund", "order 4471", "damaged", "shipping", "replacement"]

    def keyword_reward(summary):
        text = summary.lower()
        return sum(term in text for term in KEY_TERMS) / len(KEY_TERMS)

    CANDIDATES = {
        "a real summary":
            "Customer received order 4471 damaged in shipping and wants a "
            "refund or a replacement.",
        "misses two terms":
            "Customer is unhappy about order 4471 and would like a refund.",
        "THE HACK (keyword soup)":
            "refund order 4471 damaged shipping replacement",
        "THE HACK, worse":
            "refund refund order 4471 damaged shipping replacement refund "
            "order 4471 damaged shipping replacement",
    }

    print(f"{'candidate':<26}{'reward':>8}  {'words':>6}")
    for name, text in CANDIDATES.items():
        print(f"{name:<26}{keyword_reward(text):>8.2f}  {len(text.split()):>6}")
    ```

    The keyword soup scores a perfect 1.00 in six words, tying the genuine
    summary, and the repeated version ties it again. Nothing in the reward
    mentions grammar, ordering, causality, or whether the summary would be
    intelligible to a human — so an optimiser will discover that emitting the
    key-term list *is* the maximum, and it will get there long before it learns
    to write.

    The general lesson: **a reward that only measures presence will be
    satisfied by presence alone.** Anything the reward does not mention is
    free for the optimiser to destroy.

    Things that would genuinely help, roughly in order of effort: require the
    summary to parse as sentences and cover the terms *in context* rather than
    as a list; add a fluency term from a second model; pair the keyword score
    with a pairwise preference model so the reward has an opinion about writing
    as well as coverage; or — cheapest and most effective — hold out an
    evaluation the optimiser never sees, so the moment the soup appears you can
    see the true quality falling even while the reward rises, exactly as in
    [31.4](04-reward-models.md).

---

### Exercise 31.8 — Kill the length hack (●●●)

Here is a reward model whose scores have length baked in, and a catalogue of
nine candidate responses. Optimising it produces the classic failure: the policy
converges on a long, wrong, polite answer.

Your job: implement a **length-penalised** reward
$r_\lambda(y) = r(y) - \lambda \cdot \text{len}(y)$, sweep $\lambda$, and find
the range that makes the hack disappear. Report the best $\lambda$, what the
policy converges on there, and what happens when $\lambda$ is too large.

??? success "Solution"

    ```python
    import numpy as np
    import matplotlib.pyplot as plt

    NAMES = ["terse correct", "correct + example", "correct, blunt",
             "wrong, short", "polite waffle", "padded correct",
             "rambling wrong", "crisp + example", "wrong, exhaustive"]
    #              correct example polite  length
    X = np.array([[1, 0, 0, 0.3], [1, 1, 1, 0.6], [1, 1, 0, 0.5],
                  [0, 0, 1, 0.2], [0, 0, 1, 2.6], [1, 0, 1, 1.8],
                  [0, 1, 1, 2.9], [1, 1, 1, 0.4], [0, 0, 1, 3.0]], dtype=float)
    W_RM   = np.array([2.0, 1.0, 0.5, 1.2])    # the reward model, length leaked in
    W_TRUE = np.array([2.0, 1.0, 0.6, 0.0])    # what we actually wanted
    rm_score, true_quality, lengths = X @ W_RM, X @ W_TRUE, X[:, 3]

    def softmax(z):
        e = np.exp(z - z.max())
        return e / e.sum()

    def optimise(score, steps=200, lr=0.6):
        """Ascend expected score with a softmax policy; report the end state."""
        theta = np.zeros(len(X))
        for _ in range(steps):
            p = softmax(theta)
            theta += lr * p * (score - p @ score)
        p = softmax(theta)
        return float(p @ true_quality), int(p.argmax()), float(p @ lengths)

    print(f"{'lambda':>8}{'true quality':>15}{'mean length':>14}  converged on")
    best_lam, best_true = None, -np.inf
    for lam in [0.0, 0.8, 1.6, 4.0, 8.0, 16.0, 20.0]:
        true_end, winner, mean_len = optimise(rm_score - lam * lengths)
        if true_end > best_true:
            best_lam, best_true = lam, true_end
        print(f"{lam:>8.1f}{true_end:>15.3f}{mean_len:>14.2f}  {NAMES[winner]}")

    print(f"\nbest lambda tried = {best_lam} with true quality {best_true:.3f} "
          f"(the best any response can reach is {true_quality.max():.3f})")

    lams = np.linspace(0.0, 22.0, 45)
    trues = [optimise(rm_score - l * lengths)[0] for l in lams]
    fig, ax = plt.subplots(figsize=(7.0, 3.2))
    ax.plot(lams, trues)
    ax.axhline(true_quality.max(), ls="--", color="0.7", label="best possible")
    ax.set_xlabel("length penalty lambda")
    ax.set_ylabel("true quality of the optimised policy")
    ax.set_title("Too little penalty hacks; too much penalty starves")
    ax.legend()
    fig.tight_layout()
    ```

    At $\lambda = 0$ the policy converges on `rambling wrong` — 2.9 units of
    length at 1.2 points each beats being correct — and true quality ends at
    1.608 with a mean response length of 2.89. **Anything from about
    $\lambda = 0.8$ to $\lambda = 8$ fixes it completely**: the policy picks
    `correct + example` or `crisp + example`, true quality 3.59 against a
    maximum of 3.60, and the mean length falls to 0.4–0.6. That plateau is very
    wide, which is the practical good news — you do not have to tune this
    precisely, you only have to notice the leak exists.

    Push $\lambda$ far enough and the opposite failure appears. At
    $\lambda = 16$ true quality has slipped to 3.300, and by $\lambda = 20$ the
    penalty outweighs everything the reward model knows: the policy converges on
    `wrong, short` purely because it is 0.2 units long, and true quality
    collapses to 0.611. The curve is an arc with a long flat top and a cliff at
    each end, and *both* cliffs are reward hacking — one hacking length upward,
    the other downward.

    The general lesson: the fix for a leaky reward is not "penalise the leak as
    hard as possible". It is "remove the leak's *slope*" — which is exactly what
    the least-squares debiasing in [31.4](04-reward-models.md) does, and it needs
    no hyperparameter at all because it measures the slope from the data instead
    of guessing it.
