# 31.3 DPO and GRPO

Section 31.2 ended with a bill: four models in memory, two of them carrying
optimiser state, roughly 235 GB for a 7-billion-parameter run before you have
generated a single token.

The two methods in this section each delete one of those models:

- **DPO** removes the reward model *and* the sampling loop, by noticing that the
  RLHF objective can be solved on paper.
- **GRPO** removes the value model, by replacing it with something you already
  have: the other responses to the same prompt.

Both are simple enough to implement from scratch in numpy, and you are about to
implement both.

## DPO's insight: the answer was already written down

!!! abstract "In plain words"

    - **What it is.** DPO trains a model straight from "answer A is better than
      answer B" pairs — no separate reward model, no sampling loop.
    - **Picture it.** PPO builds a judge (the reward model) and then has the
      student chase the judge's scores. DPO notices that the student *already
      contains a judge*: how much more probable it makes one answer than another
      already says which it prefers. So cut out the middleman and teach that
      built-in preference directly, from the human-labelled pairs.
    - **Why it matters.** Deleting the reward model and the generation loop turns
      alignment back into ordinary supervised training — the exact setup every
      fine-tuning team already runs. That convenience is why DPO spread so fast.

    The algebra below is just the careful version of "the model already contains
    a judge." We take the equation for the *ideal* policy and, instead of chasing
    it, solve it for the reward — which turns out to be written in the policy's
    own probabilities. Read the derivation for that one payoff.

Recall the closed-form optimum from the end of [31.2](02-policy-gradient-ppo.md).
For the KL-regularised RLHF objective, the best possible policy is

$$
\pi^{*}(y \mid x) = \frac{1}{Z(x)}\, \pi_{\text{ref}}(y \mid x)\,
\exp\!\left(\frac{r(x, y)}{\beta}\right)
$$

Read aloud: *the ideal policy is the reference model, re-weighted to favour
high-reward answers.* The factor $\exp(r/\beta)$ tilts probability towards good
responses, and $Z(x)$ is just the divisor that makes the result sum to one.

Everyone had been treating this as a *goal*: train a reward model $r$, then run
PPO for a long time hoping to approach $\pi^{*}$. Rafailov et al. (2023) asked
the algebra question instead — what if we rearrange it to isolate $r$?

$$
r(x, y) = \beta \log \frac{\pi^{*}(y \mid x)}{\pi_{\text{ref}}(y \mid x)}
+ \beta \log Z(x)
$$

Read aloud: *a response's reward is $\beta$ times how much more likely the
trained policy makes it than the reference does, plus a term ($\beta \log Z(x)$)
that is identical for every response to the same prompt.* That second term is the
nuisance we are about to make vanish.

Read that carefully, because it is the whole paper.

!!! note "The one idea behind DPO"

    **Any policy implicitly defines a reward function** — namely $\beta$ times
    its log-ratio against the reference. There is no separate reward network
    anywhere in that expression. The policy *is* the reward model, viewed
    sideways.

### Why the intractable term disappears

The remaining nuisance is $Z(x)$, the normalising constant. It is a sum over
every possible response, and completely intractable. It disappears for free, in
two steps:

1. **Preference data contains no absolute scores** — only *comparisons* between
   two responses **to the same prompt**.
2. **Under the Bradley-Terry model** (see [31.4](04-reward-models.md)) the
   probability that $y_w$ beats $y_l$ depends only on the *difference*
   $r(x, y_w) - r(x, y_l)$.

Both terms carry the same $\beta \log Z(x)$, so it cancels exactly.

## The DPO loss

Substituting the implicit reward into Bradley-Terry and maximising the
likelihood of the observed preferences gives:

$$
\mathcal{L}_{\text{DPO}}(\theta) = -\,\mathbb{E}_{(x,\,y_w,\,y_l)}
\left[\log \sigma\!\left(
\beta \log \frac{\pi_\theta(y_w \mid x)}{\pi_{\text{ref}}(y_w \mid x)}
- \beta \log \frac{\pi_\theta(y_l \mid x)}{\pi_{\text{ref}}(y_l \mid x)}
\right)\right]
$$

Read aloud: *for every labelled pair, make the policy prefer the winner over the
loser by a comfortable margin.* The two log-ratios are the policy's own implicit
scores for the two answers, and $-\log\sigma$ of the gap between them is nothing
more than the ordinary "get this comparison right" classification loss.

| Term | What it is |
| --- | --- |
| $x,\ y_w,\ y_l$ | a prompt, the **w**inning (preferred) response, the **l**osing one |
| $\pi_\theta$ | the policy being trained |
| $\pi_{\text{ref}}$ | a frozen copy of the starting model (usually the SFT checkpoint) |
| $\beta \log \frac{\pi_\theta(y)}{\pi_{\text{ref}}(y)}$ | the **implicit reward** $\hat r(y)$ — no reward model computes this |
| $\hat r(y_w) - \hat r(y_l)$ | the **margin**: how much more the policy prefers the winner than the reference did |
| $\sigma(\cdot)$ | the logistic sigmoid, turning a margin into a probability |
| $-\log \sigma(\cdot)$ | ordinary binary cross-entropy — this is a *classification* loss |
| $\beta$ | how many nats of implicit reward one unit of log-ratio buys |

Look at the shape of what is left — a fixed dataset, two forward passes per
example, a sigmoid, a cross-entropy.

**There is no sampling, no reward model, no value model, and no rollout.** DPO
is a supervised training loop that happens to optimise an RL objective. That is
why it took over: it fits in the fine-tuning infrastructure teams already had.

### Reading the gradient

The gradient has an interpretable form too:

$$
\nabla_\theta \mathcal{L}_{\text{DPO}} = -\beta\,\mathbb{E}\Big[
\underbrace{\sigma\big(\hat r(y_l) - \hat r(y_w)\big)}_{\text{how wrong we currently are}}
\big(\nabla_\theta \log \pi_\theta(y_w) - \nabla_\theta \log \pi_\theta(y_l)\big)\Big]
$$

In words: *push the winner up, push the loser down, weighted by how badly the
current policy has the pair backwards.* Pairs the model already gets right
contribute almost nothing.

## A complete DPO trainer

Here is the real thing at a scale you can read:

- **Two prompts**, five candidate responses each — so the policy is ten logits.
- **A frozen reference**, which deliberately favours the two responses a
  badly-tuned SFT model would favour: jargon and corporate boilerplate.
- **Eight hand-written preference pairs.**

```python
import numpy as np

PROMPTS = ["explain recursion", "apologise for the outage"]
RESPONSES = [
    ["one-line definition", "worked example", "wall of jargon",
     "flatly wrong", "off-topic ramble"],
    ["just 'sorry'", "sorry + cause + fix", "blames the user",
     "corporate word salad", "off-topic ramble"],
]
# The frozen reference: what our SFT model does before any preference training.
REF_LOGITS = np.array([[0.5, 0.0, 1.0, -0.5, 0.0],
                       [0.3, 0.2, -0.5, 1.0, 0.0]])
# Eight hand-made preferences: (prompt, winner index, loser index).
PAIRS = [(0, 1, 0), (0, 1, 2), (0, 0, 3), (0, 1, 3),
         (1, 1, 0), (1, 1, 2), (1, 0, 3), (1, 1, 3)]
BETA = 0.1

def softmax(z):
    e = np.exp(z - z.max())
    return e / e.sum()

def log_softmax(z):
    m = z.max()
    return z - m - np.log(np.exp(z - m).sum())

def margins(theta, beta=BETA):
    """The implicit-reward margin beta*(r_hat(y_w) - r_hat(y_l)) for each pair."""
    out = []
    for p, w, l in PAIRS:
        lp, lref = log_softmax(theta[p]), log_softmax(REF_LOGITS[p])
        out.append(beta * ((lp[w] - lref[w]) - (lp[l] - lref[l])))
    return np.array(out)

def dpo_loss(theta, beta=BETA):
    s = margins(theta, beta)
    return float(np.mean(-np.log(1.0 / (1.0 + np.exp(-s)))))   # -log sigmoid(s)

def dpo_grad(theta, beta=BETA):
    """Analytic gradient: -(1 - sigma(margin)) * beta * (push winner, pull loser)."""
    g = np.zeros_like(theta)
    for (p, w, l), s in zip(PAIRS, margins(theta, beta)):
        sigma = 1.0 / (1.0 + np.exp(-s))
        coef = -(1.0 - sigma) * beta
        g[p, w] += coef          # raise the winner's log-probability
        g[p, l] -= coef          # lower the loser's
    return g / len(PAIRS)

theta = REF_LOGITS.copy()        # DPO always starts the policy at the reference
print(f"starting loss: {dpo_loss(theta):.6f}   (-log 0.5 = {np.log(2):.6f}, "
      f"because policy == reference means every margin is exactly 0)")
```

Before trusting one line of that, check the gradient — the practice from
[31.1](01-rl-basics.md). Ten parameters, twenty extra loss evaluations, one
second of your life, and it catches every sign error you will ever make.

```python
# continues
def finite_difference_grad(theta, h=1e-6):
    g = np.zeros_like(theta)
    for i in range(theta.shape[0]):
        for j in range(theta.shape[1]):
            up, down = theta.copy(), theta.copy()
            up[i, j] += h
            down[i, j] -= h
            g[i, j] = (dpo_loss(up) - dpo_loss(down)) / (2 * h)
    return g

analytic = dpo_grad(theta)
numeric = finite_difference_grad(theta)
print("analytic gradient (prompt 0):", np.round(analytic[0], 6))
print("numeric  gradient (prompt 0):", np.round(numeric[0], 6))
print(f"worst disagreement: {np.abs(analytic - numeric).max():.2e}")
assert np.abs(analytic - numeric).max() < 1e-6
print("gradient check passed")
```

Read the numbers as well as the check:

- **`worked example` (index 1)** has the most negative gradient, $-0.01875$,
  because it wins three of prompt 0's four pairs — and descent *subtracts* the
  gradient, so it will be raised hardest.
- **`flatly wrong` (index 3)** loses two pairs and gets $+0.0125$, twice the
  $+0.00625$ of `wall of jargon`, which loses one.
- **The two zeros have different causes.** `off-topic ramble` (index 4) appears
  in no pair at all, so DPO has nothing to say about it. `one-line definition`
  (index 0) wins one pair and loses one, and its two contributions cancel
  exactly.

Now train.

```python
# continues
import matplotlib.pyplot as plt

theta = REF_LOGITS.copy()
losses, mean_margin = [], []
for step in range(150):
    losses.append(dpo_loss(theta))
    mean_margin.append(float(margins(theta).mean()))
    theta -= 1.0 * dpo_grad(theta)          # plain gradient descent, lr = 1.0
losses.append(dpo_loss(theta))

correct = sum(1 for m in margins(theta) if m > 0)
print(f"loss   {losses[0]:.4f} -> {losses[-1]:.4f}")
print(f"margin {mean_margin[0]:.4f} -> {float(margins(theta).mean()):.4f}")
print(f"pairs ranked correctly: {correct}/{len(PAIRS)}")

fig, axes = plt.subplots(1, 2, figsize=(9.0, 3.2))
axes[0].plot(losses)
axes[0].set_xlabel("step"); axes[0].set_ylabel("DPO loss")
axes[0].set_title("loss")
axes[1].plot(mean_margin)
axes[1].set_xlabel("step"); axes[1].set_ylabel("mean implicit-reward margin")
axes[1].set_title("margin")
fig.tight_layout()
```

The loss falls from $0.6931$ to $0.5553$ — and if you were expecting it to
approach zero, this is the most useful surprise on the page.

With $\beta = 0.1$ the loss is $-\log \sigma(0.1 \times \text{log-ratio gap})$,
so reaching a loss of $0.2$ would require a log-ratio gap of about 15 — which
means moving the policy astronomically far from the reference.

!!! tip "A DPO loss that stalls around 0.5 is normal and often healthy"

    Judge the run by the **margin** and by the **ranking accuracy** — here all
    eight pairs correct — not by the loss reaching zero. A loss that *does*
    crash to zero usually means $\beta$ is too large or the pairs are trivially
    separable.

Now the before-and-after, which is what you actually wanted to know:

```python
# continues
for p, prompt in enumerate(PROMPTS):
    before, after = softmax(REF_LOGITS[p]), softmax(theta[p])
    implicit = BETA * (np.log(after) - np.log(before))
    print(f"\n{prompt!r}")
    print(f"   {'response':<22}{'reference':>11}{'policy':>9}{'change':>10}"
          f"{'implicit r':>13}")
    for j, name in enumerate(RESPONSES[p]):
        print(f"   {name:<22}{before[j]:>11.3f}{after[j]:>9.3f}"
              f"{after[j] - before[j]:>+10.3f}{implicit[j]:>13.3f}")
```

Two prompts, four numbers each:

- **`explain recursion`** — `worked example` went from 14.3% to 76.8%, and
  `wall of jargon`, the reference model's favourite at 39.0%, fell to 6.8%.
- **`apologise for the outage`** — `corporate word salad` collapsed from 39.4%
  to 2.5%, while `sorry + cause + fix` rose from 17.7% to 83.6%.

The `implicit r` column is **the reward function DPO learned without ever
building one**: $\beta$ times the log-ratio, positive for responses the policy
now prefers over the reference and negative for the rest.

!!! note "What is toy, what is faithful"
    Toy: five candidate responses instead of a vocabulary raised to the power of
    the sequence length, ten parameters instead of seven billion, eight pairs
    instead of a hundred thousand, and a "log-probability of a response" that is
    one softmax entry rather than a sum of per-token log-probabilities. Faithful:
    `dpo_loss` and `dpo_grad` are the DPO objective and its exact gradient,
    initialising the policy at the reference is what every implementation does,
    and the shape of the result — mass moving from reference-favoured responses
    to preferred ones — is what a real run produces.

## What $\beta$ does

!!! abstract "In plain words"

    - **What it is.** $\beta$ is a single dial: how tightly to hold the model near
      its starting point versus how freely to let it chase the preference data.
    - **Picture it.** The tension in the KL rubber band. Large $\beta$ is a stiff
      band — the model barely moves and learns little; small $\beta$ is a slack
      band — the model lunges after the preferences and can end up far from where
      it should be. The sweet spot is in between.
    - **Why it matters.** It is the main knob you tune on a DPO run, and the two
      extremes fail in opposite, recognisable ways — which the numbers below make
      concrete.

$\beta$ converts log-ratio into reward. To express an implicit-reward margin of
one nat, the policy's log-probability gap must be $1/\beta$ — and a log gap of
$1/\beta$ is a *probability* ratio of $e^{1/\beta}$. That number gets out of
hand quickly, which is the entire argument for not setting $\beta$ small.

```python
# continues
print(f"{'beta':>6}{'log gap needed for 1 nat':>27}{'= probability ratio':>22}")
for beta in [2.0, 0.5, 0.1, 0.02]:
    print(f"{beta:>6.2f}{1.0 / beta:>27.1f}{np.exp(1.0 / beta):>22.3g}")

def kl_from_reference(th):
    total = 0.0
    for p in range(len(PROMPTS)):
        a, b = softmax(th[p]), softmax(REF_LOGITS[p])
        total += float(np.sum(a * np.log(a / b)))
    return total / len(PROMPTS)

print(f"\n150 steps at lr = 1.0, same data, different beta:")
print(f"{'beta':>6}{'final loss':>13}{'KL from ref':>14}{'P(worked example)':>20}")
for beta in [0.02, 0.1, 0.5, 2.0]:
    th = REF_LOGITS.copy()
    for _ in range(150):
        th -= 1.0 * dpo_grad(th, beta)
    print(f"{beta:>6.2f}{dpo_loss(th, beta):>13.4f}{kl_from_reference(th):>14.3f}"
          f"{softmax(th[0])[1]:>20.3f}")
```

**$\beta = 0.02$ — too small.** The gradient is proportional to $\beta$, so
after 150 steps the loss has barely moved from $0.6931$ to $0.6866$ and the
target response has crawled from 14.3% to 24.8%. It would get there eventually,
and "eventually" is the problem: by then the policy would sit an enormous
distance from the reference, which is what the first table prices.

**$\beta = 2.0$ — too large, in the opposite way.** The loss hits $0.0063$
almost immediately, and once $\sigma(\text{margin}) \approx 1$ the gradient
factor $(1 - \sigma)$ is essentially zero, so training simply stops. The policy
freezes wherever the first few steps put it — 71.8% — having learned nothing
from the last 140 steps.

**$\beta = 0.5$ — commits hardest.** It moves furthest from the reference (KL
1.63), on the strength of eight examples.

**$\beta = 0.1$ — the default.** Most implementations use it, and the middle of
that spread is why.

## DPO's failure modes, honestly

DPO is not strictly better than PPO, and pretending otherwise will cost you a
training run. Three failure modes, in the order you are likely to hit them.

### It can push the preferred responses down too

The objective only constrains the *difference* between the two log-ratios.
Nothing in it says the winner's probability must rise. In practice both
frequently fall, with the freed-up mass going to responses that appear in no
pair at all. It happens in our ten-parameter model as well:

```python
# continues
print(f"{'pair':<40}{'d log pi(win)':>15}{'d log pi(lose)':>16}")
for p, w, l in PAIRS:
    b, a = log_softmax(REF_LOGITS[p]), log_softmax(theta[p])
    label = f"{RESPONSES[p][w][:16]} > {RESPONSES[p][l][:16]}"
    print(f"{label:<40}{a[w] - b[w]:>+15.3f}{a[l] - b[l]:>+16.3f}")
```

Look at the third and seventh rows. The *preferred* response in
`one-line definition > flatly wrong` had its log-probability driven **down** by
0.870 nats — because that same response is the loser in
`worked example > one-line definition`, and the losing pull was the stronger of
the two.

DPO satisfied the comparison correctly (the rejected response fell further, by
2.621) and reduced the winner's likelihood while doing so. Both sides of that
pair are now less likely than they were before training.

On a real model this is how DPO runs drift towards shorter, blander, or
off-distribution text: **mass has to go somewhere, and the loss never said
where.**

### It is sensitive to the reference

The implicit reward is defined *relative* to $\pi_{\text{ref}}$. If your
preference data was written for a different model than the one you froze — a
common accident when reusing a public preference dataset — the log-ratios are
measuring drift from the wrong starting point, and the resulting reward function
is not the one you meant.

### It needs pairs, and it inherits their flaws

Being offline is DPO's strength and its ceiling:

- **It can only learn from responses somebody already generated and compared.**
  It never scores its own new attempts, so it cannot discover behaviour outside
  the pair distribution.
- **A mislabelled pair is trained on with total confidence.** No sampling step
  exists to contradict it.
- **It does not know how *much* better the winner was.** A landslide and a
  coin-flip preference produce identical labels.

## GRPO: the group is the baseline

!!! abstract "In plain words"

    - **What it is.** Instead of training a whole separate network to guess "how
      good is this situation," GRPO samples several answers to the same question
      and grades each one against the group's average.
    - **Picture it.** A pop quiz marked on a curve. You do not need a *prediction*
      of the class average — you have the class. An answer that beats the other
      attempts at the same question gets pushed up; one that trails them gets
      pushed down.
    - **Why it matters.** It deletes the value network — its optimiser state and
      its ~104 GB with it — and it suits tasks where you can *check* an answer
      (maths, code), because there the group can be graded by a rule, with
      nothing to hack.

The other expensive model in PPO is the **value network**, whose only job is to
predict "how good is this state, on average" so we can subtract it as a
baseline.

GRPO — **Group Relative Policy Optimization**, introduced with DeepSeekMath
(Shao et al., 2024) — makes an observation that is obvious in hindsight: for a
language model we can simply *generate several responses to the same prompt* and
use their mean score as the baseline. **The other responses in the group are the
value estimate.**

The procedure, per prompt:

1. **Sample** a group of $G$ responses $y_1 \dots y_G$.
2. **Score** each one.
3. **Standardise** the scores into advantages:

$$
A_i = \frac{r_i - \text{mean}(r_1, \dots, r_G)}{\text{std}(r_1, \dots, r_G)}
$$

4. **Update** with the same clipped policy-gradient step as PPO, plus a KL term
   to the reference.

Read the formula as: *how far above or below its own group did this response
score, measured in group standard deviations?* Above the average gives a
positive advantage; below it, negative.

The division by the standard deviation is doing real work: it puts every prompt
on the same scale, so an easy prompt where all scores are near 1.0 does not
drown out a hard one.

**No value network, no optimiser state for it, no extra 104 GB.**

Here it is on three arithmetic prompts, each with four candidate answers and a
reward that is *verifiable*: 1 if the answer is right, 0 if it is wrong. The
starting policy prefers wrong answers, exactly as an untuned model would.

```python
import numpy as np
import matplotlib.pyplot as plt

PROMPTS = ["12 * 7 = ?", "sum 1..10 = ?", "17 - 9 = ?"]
CANDIDATES = [["84", "78", "96", "84 (with working)"],
              ["55", "45", "50", "55 (with working)"],
              ["8", "7", "9", "8 (with working)"]]
CORRECT = [{0, 3}, {0, 3}, {0, 3}]          # a rule, not a neural network
INIT = np.array([[0.0, 1.0, 0.5, -0.5],     # the policy starts out mostly wrong
                 [0.0, 0.8, 0.6, -0.4],
                 [0.0, 1.2, 0.3, -0.6]])

def softmax(z):
    e = np.exp(z - z.max())
    return e / e.sum()

def verify(prompt_i, answer_i):
    """The reward function: a checker, not a model. Cannot be hacked."""
    return 1.0 if answer_i in CORRECT[prompt_i] else 0.0

def grpo(n_iters=40, group=8, lr=0.5, seed=0, show_first=False):
    rng = np.random.default_rng(seed)
    theta = INIT.copy()
    accuracy, dead_groups = [], []
    for it in range(n_iters):
        grad, dead = np.zeros_like(theta), 0
        for p in range(len(PROMPTS)):
            probs = softmax(theta[p])
            sampled = rng.choice(4, size=group, p=probs)       # the rollout
            r = np.array([verify(p, int(j)) for j in sampled])
            if r.std() < 1e-8:
                dead += 1          # every response scored the same: no signal
                continue
            adv = (r - r.mean()) / (r.std() + 1e-8)            # group-relative
            g = np.zeros(4)
            for a, A in zip(sampled, adv):
                onehot = np.zeros(4)
                onehot[a] = 1.0
                g += A * (onehot - probs)                      # policy gradient
            grad[p] += g / group
            if show_first and it == 0:
                print(f"\n{PROMPTS[p]}   group mean r = {r.mean():.3f}, "
                      f"std = {r.std():.3f}")
                for a, ri, Ai in zip(sampled, r, adv):
                    arrow = "PUSH UP  " if Ai > 0 else "push down"
                    print(f"   {CANDIDATES[p][a]:<20}r={ri:.0f}  "
                          f"A={Ai:+.3f}  {arrow}")
        theta += lr * grad
        accuracy.append(float(np.mean(
            [sum(softmax(theta[p])[j] for j in CORRECT[p])
             for p in range(len(PROMPTS))])))
        dead_groups.append(dead)
    return theta, np.array(accuracy), np.array(dead_groups)

theta, accuracy, dead = grpo(show_first=True)
print(f"\nP(correct answer): {accuracy[0]:.3f} -> {accuracy[-1]:.3f}")
print(f"zero-variance groups: {dead.sum()} of {len(dead) * 3}"
      f"   (first 5 iters {dead[:5].tolist()}, last 5 {dead[-5:].tolist()})")

fig, ax = plt.subplots(figsize=(7.0, 3.2))
ax.plot(accuracy)
ax.set_xlabel("GRPO iteration")
ax.set_ylabel("probability of a correct answer")
ax.set_title("GRPO on three verifiable prompts, group size 8")
fig.tight_layout()
```

The first-iteration trace is the algorithm in one screen.

For `12 * 7 = ?`, three of the eight sampled responses were right. The group
mean is 0.375 and the standard deviation 0.484, so each correct response gets
$A = +1.291$ and each wrong one $A = -0.775$.

Now note what the *same* reward of 1 earns on a different prompt. For
`17 - 9 = ?` only two of eight were right, so being right there was more
surprising and earned $+1.732$. **That re-scaling is what "group relative"
means, and it is free.**

Across 40 iterations the probability of a correct answer climbs from 0.324 to
0.978. Nothing supervised the model; a four-line `verify` function did all the
work.

!!! note "What is toy, what is faithful"
    Faithful: the group-relative advantage exactly as written above, the
    generate–score–update cycle, and the zero-variance failure below.
    Simplified: this update is plain policy gradient with the group baseline —
    the PPO-style ratio clipping and the KL term to the reference are left out,
    because with one gradient step per rollout no sample is ever stale enough
    for a clip to matter and a rule-based verifier cannot be hacked. A
    production GRPO step keeps both.

### The dead-group problem

The `zero-variance groups` line is the algorithm's real cost, and it is worth
sitting with.

When all $G$ responses to a prompt receive the same score, the standard
deviation is zero, every advantage is zero, and the entire group produces **no
gradient at all**. You generated eight responses for nothing.

In our run that happened 57 times out of 120, and the trend is the interesting
part: 0 dead groups in the first iterations, 3 out of 3 in the last — because
the policy has learned the prompts and now answers them all correctly.

Real GRPO pipelines fight this by filtering the prompt set to problems the model
solves *sometimes*: neither never nor always. **Difficulty curation stops being
a nicety and becomes a throughput requirement.**

## Why GRPO suits verifiable rewards

Notice what `verify` is: four lines, deterministic, and impossible to fool. A
math answer either matches or it does not. A unit test either passes or it does
not.

There is no learned reward model, so **there is nothing to hack** — the failure
mode that dominates [31.4](04-reward-models.md) simply cannot occur, and the KL
penalty is no longer load-bearing.

That is why GRPO and **verifiable rewards** (often written RLVR) fit together so
naturally, and why the pairing became the standard recipe for training reasoning
models on mathematics and competitive programming. DeepSeek's R1 work is the
best-known public example, and several open-source stacks — TRL, verl, OpenRLHF
— ship GRPO implementations.

The honest version of the claim, in two halves:

- **What it does.** On tasks with a checkable answer, group-relative advantages
  plus a rule-based verifier remove two whole models from the loop and work at
  least as well as PPO.
- **What it does not.** There is no `verify` for "write a good condolence
  message". For open-ended generation you are back to a learned reward model
  with all its holes.

!!! warning "Current practice, not settled science"

    The details are moving quickly — group size, whether to normalise by the
    standard deviation at all, how to weight tokens within a response — and
    papers proposing adjustments appear constantly. The *idea* — **use a group
    of samples as the baseline instead of a learned critic** — is the part worth
    memorising.

## Choosing between them

| | Rejection sampling | PPO | DPO | GRPO |
| --- | --- | --- | --- | --- |
| **Data needed** | a scorer | prompts + reward model | fixed preference pairs | prompts + a verifier or reward model |
| **Models in memory** | 1 (+ scorer) | 4 | 2 | 2 |
| **Trainable models** | 1 | 2 (policy, value) | 1 | 1 |
| **7B memory (from 31.2)** | ~117 GB | ~235 GB | ~117 GB | ~117 GB |
| **Generates during training?** | yes, once | yes, every step | **no** | yes, $G$ per prompt |
| **Compute** | low | very high | low | high |
| **Stability** | trivially stable | fiddly; needs clipping, KL, tuning | stable, but silently over-fits | moderate; sensitive to group size |
| **Learns from its own new samples?** | only by selection | yes | no | yes |
| **Main risk** | ceiling: only what the model already produces | reward hacking + cost | over-fitting pairs; both likelihoods can fall | wasted zero-variance groups |
| **Reach for it when** | you want 80% of the gain this afternoon | you have a good reward model and a cluster | you have preference pairs and one GPU budget | the task has a checkable answer |

The honest summary is that **these are not ranked**. Many production pipelines
run several: SFT, then DPO on preference pairs, then GRPO on the verifiable
subset, with rejection sampling used throughout to build the data for the next
stage.

And "which algorithm" is usually a smaller question than "what is the reward,
and is it measuring what you meant" — which is
[31.4](04-reward-models.md).

!!! warning "Common mistakes"
    - **Expecting the DPO loss to reach zero.** With $\beta = 0.1$ a loss near
      $0.5$ can already correspond to perfect ranking accuracy. Track the
      margin and the win rate; a loss that *does* crash to zero usually means
      $\beta$ is too large or the pairs are trivially separable.
    - **Forgetting to freeze the reference.** If $\pi_{\text{ref}}$ updates
      along with $\pi_\theta$, every log-ratio is zero, every margin is zero,
      and the loss sits at $\log 2$ forever while nothing happens.
    - **Initialising the policy somewhere other than the reference.** DPO
      assumes $\pi_\theta$ starts at $\pi_{\text{ref}}$; starting elsewhere
      means the implicit rewards are measured from a point you did not choose.
    - **Assuming DPO raises the chosen responses' likelihood.** It very often
      does not — the objective only constrains the difference. Log the absolute
      log-probabilities, not just the margin.
    - **Running GRPO on prompts the model always gets right (or always wrong).**
      Zero variance in the group means zero advantage means zero gradient.
      You will pay full generation cost for an empty update.
    - **Calling GRPO "PPO without the critic" and stopping there.** The group
      baseline also *normalises* across prompts of different difficulty, which
      a single learned value function does not do for free.

## Check your understanding

1. DPO trains without a reward model. Where did the reward model go?

    ??? success "Answer"

        It was substituted away. Rearranging the closed-form RLHF optimum gives
        $r(x,y) = \beta \log \frac{\pi(y \mid x)}{\pi_{\text{ref}}(y \mid x)} + \beta \log Z(x)$,
        so any policy already defines a reward. The intractable $\log Z(x)$
        cancels because preference data compares two responses to the *same*
        prompt. The policy is the reward model.

2. Your DPO run shows the margin growing steadily while the chosen responses'
   log-probabilities fall. Is it broken?

    ??? success "Answer"

        Not broken — but it is doing something you should watch. The loss only
        constrains the difference of log-ratios, so it is satisfied by pushing
        the rejected response down harder than the chosen one. The mass has to
        go somewhere, and it goes to responses in no pair. Mitigations in
        practice: fewer epochs, a larger $\beta$, or adding an SFT term on the
        chosen responses to hold their likelihood up.

3. A GRPO group of 8 responses all score 1.0. What is the gradient, and what
   should you change?

    ??? success "Answer"

        Every advantage is $(1 - 1)/\text{std} = 0$, so the gradient is exactly
        zero and the eight generations were wasted. The prompt is too easy for
        the current policy. Filter the prompt set to items the model solves
        sometimes but not always, or raise the sampling temperature so the group
        contains genuine variation.

4. You have 50,000 preference pairs, one 80 GB GPU, and a week. Which method,
   and why not the others?

    ??? success "Answer"

        DPO. It is the only one of the four that needs no generation during
        training, and it holds two models with only one optimiser state — around
        117 GB at 7B, which still means sharding or a smaller model, but it is
        half of PPO's 235 GB and the *training* loop is ordinary supervised
        fine-tuning. PPO needs a reward model you do not have and four resident
        models. GRPO needs a verifier, and preference pairs are not one.
        Rejection sampling needs a scorer at generation time and would not use
        your pairs at all.
