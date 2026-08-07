# 31.2 Policy gradients and PPO

Section 31.1 left us with a policy, a reward, and one tool: gradient descent.
This section connects them. The connection has a name — the **policy gradient**
— and once you have it, PPO is not a new algorithm so much as four patches
applied to it, each one fixing a specific way the naive version breaks. We will
apply them in order, and you will implement every patch. By the end you will
have a working PPO loop in about forty lines of numpy, and a memory calculation
that explains why half the field went looking for something cheaper.

## The idea in one sentence

> **Raise the log-probability of actions that led to high reward; lower it for
> actions that led to low reward.**

That is the whole of policy gradient methods. Everything else — baselines,
advantages, clipping, KL penalties — is about making that sentence work when
the reward is noisy, the samples are expensive, and the model has seven billion
parameters.

## REINFORCE, symbol by symbol

The formal statement is one line. We write it as a **loss** (something to
minimise) so the descent rule of 31.1 applies unchanged:

$$
\mathcal{L}(\theta) = -\,\mathbb{E}_{\tau \sim \pi_\theta}
\left[ \sum_{t} \log \pi_\theta(a_t \mid s_t)\; G_t \right]
$$

$$
\nabla_\theta \mathcal{L}(\theta) = -\,\mathbb{E}
\left[ \sum_{t} G_t \, \nabla_\theta \log \pi_\theta(a_t \mid s_t) \right]
$$

| Symbol | Read it as |
| --- | --- |
| $\theta$ | the policy's parameters — for an LLM, the weights |
| $\pi_\theta(a_t \mid s_t)$ | probability the policy assigns to the action it took |
| $\tau \sim \pi_\theta$ | "trajectories sampled *from the current policy*" — the data is generated, not fixed |
| $G_t$ | the return that followed this action (for LLMs, usually the response's score) |
| $\nabla_\theta \log \pi_\theta$ | the direction in parameter space that makes this action more likely |
| $\mathbb{E}[\cdot]$ | average over many sampled trajectories |
| the minus sign | we minimise loss, so maximising reward means minimising its negative |

Read the gradient as a recipe: for each action taken, find the direction that
makes it more likely, scale that direction by how good the outcome was, and add
it up. Actions followed by $G_t = 0$ contribute nothing. Actions followed by
negative return get pushed *down*, because scaling an "uphill" direction by a
negative number points downhill. This is **REINFORCE** (Williams, 1992), and it
is the ancestor of every method in this chapter.

For a softmax policy the gradient has a form you can write by hand. With one
logit $\theta_j$ per action,

$$
\frac{\partial \log \pi_\theta(a)}{\partial \theta_j} = \mathbb{1}[j = a] - \pi_\theta(j)
$$

which reads: *push the chosen action's logit up by one unit, and pull every
logit down in proportion to its current probability*. Softmax's competitive
nature (31.1) does the rest.

## REINFORCE, running

Here is the whole algorithm on a **contextual bandit**: a customer message
arrives in one of two moods, the policy picks one of three replies, and a
reward comes back. Six parameters — two contexts times three actions — and you
can watch every one of them move.

```python
import numpy as np
import matplotlib.pyplot as plt

CONTEXTS = ["angry", "confused"]
ACTIONS = ["apologise", "explain", "joke"]
REWARD = np.array([[1.0, 0.3, -1.0],      # what an angry customer wants
                   [0.1, 1.0, -0.5]])     # what a confused customer wants

def softmax(z):
    e = np.exp(z - z.max())
    return e / e.sum()

def reinforce(n_steps=600, lr=0.2, seed=0):
    rng = np.random.default_rng(seed)
    theta = np.zeros((2, 3))              # 6 parameters, all starting equal
    rewards, snapshots = [], {}
    for t in range(n_steps):
        if t in (0, 50, 200, n_steps - 1):
            snapshots[t] = np.array([softmax(theta[0]), softmax(theta[1])])
        c = int(rng.integers(2))                       # the environment picks a context
        p = softmax(theta[c])                          # the policy's distribution
        a = int(rng.choice(3, p=p))                    # sample an action (explore!)
        r = REWARD[c, a] + 0.3 * rng.normal()          # noisy reward from the world

        onehot = np.zeros(3)
        onehot[a] = 1.0
        grad_logp = onehot - p                         # d log pi(a) / d theta
        theta[c] += lr * r * grad_logp                 # REINFORCE: ascend r * grad

        rewards.append(r)
    return theta, np.array(rewards), snapshots

theta, rewards, snapshots = reinforce()
print(f"{'step':>6}  " + "  ".join(f"{c}: {'/'.join(ACTIONS)}" for c in CONTEXTS))
for t, snap in snapshots.items():
    left = " ".join(f"{v:.2f}" for v in snap[0])
    right = " ".join(f"{v:.2f}" for v in snap[1])
    print(f"{t:>6}  angry: [{left}]   confused: [{right}]")
print(f"\nmean reward, first 100 steps: {rewards[:100].mean():.3f}")
print(f"mean reward, last  100 steps: {rewards[-100:].mean():.3f}")

smooth = np.convolve(rewards, np.ones(40) / 40, mode="valid")
fig, ax = plt.subplots(figsize=(7.0, 3.2))
ax.plot(smooth)
ax.set_xlabel("step")
ax.set_ylabel("reward (40-step moving average)")
ax.set_title("REINFORCE on a two-context, three-action bandit")
fig.tight_layout()
```

The policy starts uniform — every reply equally likely in every mood — and ends
essentially deterministic and *context-dependent*: `apologise` to the angry
customer, `explain` to the confused one. Nobody ever told it which reply was
correct. It tried all three, the world scored them, and the log-probabilities
moved. That is the complete loop, and swapping the six-parameter softmax for a
7-billion-parameter transformer changes the code but not the algorithm.

!!! note "What is toy, what is faithful"
    Toy: six parameters, three actions, two contexts, a reward table instead of
    a human. Faithful: the update `theta += lr * r * (onehot - p)` is exactly
    the REINFORCE gradient for a softmax policy, and the sampling-then-scoring
    structure is exactly what an LLM RL run does — it just samples a
    500-token trajectory instead of a single action.

## The variance problem, and the fix that is one subtraction

REINFORCE is *unbiased* — average enough samples and you get the true gradient
— but it is extremely noisy, and there is a specific reason. Suppose every
reward in your problem is positive. Then every sampled action gets pushed *up*,
including the bad ones; the only thing distinguishing good from bad is that good
ones get pushed harder. The learning signal is buried under a large common
offset.

The fix is to subtract a **baseline** $b$ — any number that does not depend on
the action:

$$
\nabla_\theta \mathcal{L} = -\,\mathbb{E}\left[(G_t - b)\, \nabla_\theta \log \pi_\theta(a_t \mid s_t)\right]
$$

Subtracting $b$ leaves the gradient's *average* unchanged (this is a real
theorem, not a hack: $\mathbb{E}[b \nabla \log \pi] = b \nabla \sum_a \pi(a) = b \nabla 1 = 0$)
while potentially shrinking its variance enormously. Let us measure both claims.

```python
import numpy as np

REWARD = np.array([1.0, 0.3, -1.0])       # one context, three actions

def softmax(z):
    e = np.exp(z - z.max())
    return e / e.sum()

def gradient_samples(offset, use_baseline, n=8000, seed=1):
    """Draw n single-sample REINFORCE gradient estimates at a uniform policy."""
    rng = np.random.default_rng(seed)
    p = softmax(np.zeros(3))
    rewards = REWARD + offset                       # shift ALL rewards equally
    b = float(rewards @ p) if use_baseline else 0.0   # baseline = expected reward
    g = np.zeros((n, 3))
    for i in range(n):
        a = int(rng.choice(3, p=p))
        r = rewards[a] + 0.3 * rng.normal()
        onehot = np.zeros(3)
        onehot[a] = 1.0
        g[i] = (r - b) * (onehot - p)
    return g.mean(axis=0), g.var(axis=0).sum()

print(f"{'offset':>7}{'variance, no baseline':>24}{'with baseline':>16}{'ratio':>10}")
for offset in [0.0, 2.0, 10.0]:
    m_no, v_no = gradient_samples(offset, False)
    m_yes, v_yes = gradient_samples(offset, True)
    print(f"{offset:>7.1f}{v_no:>24.4f}{v_yes:>16.4f}{v_no / v_yes:>9.1f}x")
    print(f"        mean estimate no baseline {np.round(m_no, 3)}"
          f"   with baseline {np.round(m_yes, 3)}")
```

Adding a constant to every reward cannot change which action is best — but
without a baseline it multiplies the gradient's variance by 239. With a
baseline the variance is *identical* at every offset (0.2854 in all three
rows), and the two mean estimates agree to within sampling noise, confirming
the unbiasedness claim: the baseline removed variance, not signal.

This is not an academic point. Reward-model scores routinely live in a range
like $[2, 8]$ with no natural zero, and the difference between a good and a
great response might be 0.3. Watch what that does to actual learning:

```python
# continues
def reinforce(offset, use_baseline, n_steps=600, lr=0.2, seed=0):
    rng = np.random.default_rng(seed)
    theta, b, hist = np.zeros((2, 3)), 0.0, []
    table = np.array([[1.0, 0.3, -1.0], [0.1, 1.0, -0.5]])
    for t in range(n_steps):
        c = int(rng.integers(2))
        p = softmax(theta[c])
        a = int(rng.choice(3, p=p))
        r = table[c, a] + offset + 0.3 * rng.normal()
        advantage = r - b if use_baseline else r
        onehot = np.zeros(3)
        onehot[a] = 1.0
        theta[c] += lr * advantage * (onehot - p)
        b += 0.05 * (r - b)                  # running average of reward
        hist.append(r - offset)              # log the un-shifted reward
    return theta, np.array(hist)

for use_baseline in [False, True]:
    theta, hist = reinforce(10.0, use_baseline)
    tag = "with baseline" if use_baseline else "no baseline  "
    print(f"{tag} | final reward {hist[-100:].mean():>6.3f} | "
          f"angry {np.round(softmax(theta[0]), 3)} "
          f"confused {np.round(softmax(theta[1]), 3)}")
```

Without a baseline, a reward offset of $+10$ destroys the run. Every action
looks good, so whichever action happened to be sampled first gets reinforced
hardest, the policy collapses onto `apologise` in *both* contexts, and it can
never recover because it no longer samples anything else. Final reward 0.552.
With a baseline — the same code, one subtraction — the policy learns both
contexts correctly and scores 0.995. **A baseline is not an optimisation; it is
usually the difference between learning and not learning.**

## Advantage and value functions

The best baseline is not a single running average but one that depends on the
state: how good is this *situation*, before we consider which action we chose?
That function is the **value function** $V(s)$, and the difference

$$
A(s, a) = G - V(s)
$$

is the **advantage**: how much better than expected this action turned out.
Positive advantage, push up; negative, push down; average action, no update.

A policy-gradient method that learns $V$ alongside $\pi$ is called
**actor-critic**: the *actor* is the policy that acts, the *critic* is the value
model that judges how good the state was. The critic is trained by ordinary
supervised regression — predict the return, minimise squared error — and PPO for
LLMs uses exactly this arrangement. Remember that the critic is a whole extra
neural network; that fact returns with a vengeance at the end of this section,
and it is precisely what GRPO in [31.3](03-dpo-grpo.md) deletes.

## PPO as four fixes

**Proximal Policy Optimization** (Schulman et al., 2017) is REINFORCE plus
answers to four practical problems. Take them one at a time.

### Fix 1 — reuse samples with an importance ratio

REINFORCE is *on-policy*: the expectation is over trajectories from the
**current** policy, so the instant you take one gradient step your data is
stale and must be thrown away. For an LLM, that data cost you a full generation
run over a batch of prompts — by far the most expensive part of the loop. We
would very much like to take several steps per batch.

**Importance sampling** makes that legal. If you have samples from an old
policy $\pi_{\theta_{\text{old}}}$ but want the gradient for the new one,
reweight each sample by the **ratio**

$$
r_t(\theta) = \frac{\pi_\theta(a_t \mid s_t)}{\pi_{\theta_{\text{old}}}(a_t \mid s_t)}
$$

A ratio of 1 means the new policy would have made the same choice just as
often. A ratio of 3 means the new policy is now three times as likely to do
this — and that the sample is being counted three times.

### Fix 2 — stop the ratio running away: clipping

And there is the danger. If a sample has a large positive advantage, the update
raises its probability, which raises the ratio, which makes the next update on
that same sample larger still. The estimate degrades exactly where it is being
trusted most, and one unlucky batch can flatten the policy into a
near-deterministic answer that it can never sample its way out of.

PPO's answer is blunt and effective: refuse to let the objective reward a ratio
that has moved too far.

$$
\mathcal{L}^{\text{CLIP}}(\theta) = -\,\mathbb{E}\Big[
\min\big(r_t(\theta) A_t,\;
\text{clip}(r_t(\theta), 1-\epsilon, 1+\epsilon)\, A_t\big)\Big]
$$

with $\epsilon$ typically $0.1$–$0.2$. The `min` is the clever part, and it is
worth drawing rather than arguing about.

```python
import numpy as np
import matplotlib.pyplot as plt

EPS = 0.2

def clipped_objective(ratio, advantage, eps=EPS):
    unclipped = ratio * advantage
    clipped = np.clip(ratio, 1 - eps, 1 + eps) * advantage
    return np.minimum(unclipped, clipped)      # min, for both signs of A

ratios = np.linspace(0.0, 2.0, 400)
fig, axes = plt.subplots(1, 2, figsize=(9.0, 3.4), sharey=True)
for ax, A in zip(axes, [+1.0, -1.0]):
    ax.plot(ratios, ratios * A, "--", color="0.7", label="unclipped  r*A")
    ax.plot(ratios, clipped_objective(ratios, A), lw=2, label="PPO objective")
    ax.axvline(1 - EPS, color="0.85", zorder=0)
    ax.axvline(1 + EPS, color="0.85", zorder=0)
    ax.set_xlabel("probability ratio  r")
    ax.set_title(f"advantage A = {A:+.0f}")
    ax.legend(fontsize=8)
axes[0].set_ylabel("objective (higher is better)")
fig.tight_layout()

def has_gradient(ratio, advantage, eps=EPS):
    """The min picks the constant branch exactly when the ratio overshoots."""
    frozen = (advantage > 0 and ratio > 1 + eps) or (advantage < 0 and ratio < 1 - eps)
    return "zero" if frozen else "live"

print(f"{'ratio':>7}{'A=+1 obj':>11}{'grad':>7}{'A=-1 obj':>11}{'grad':>7}")
for r in [0.5, 0.79, 1.0, 1.21, 1.5]:
    print(f"{r:>7.2f}{clipped_objective(r, 1.0):>11.3f}{has_gradient(r, 1.0):>7}"
          f"{clipped_objective(r, -1.0):>11.3f}{has_gradient(r, -1.0):>7}")
```

Read the left panel ($A > 0$, a good action). The objective rises with the
ratio until $1 + \epsilon$, then goes flat: making a good action *even more*
likely stops paying, so the gradient becomes zero and the update stops. Now the
right panel ($A < 0$, a bad action). The objective rises as the ratio *falls*,
but stops at $1 - \epsilon$ — you get credit for making a bad action less
likely, up to a point.

The asymmetry is deliberate and it is what the `min` buys. On the left panel
the objective still *falls* below $1 - \epsilon$: if the ratio has gone the
wrong way on a good action, the gradient is alive and pulls it back. The clip
only ever removes the incentive to keep pushing in the direction you were
already going too far in. It never removes the incentive to come back.

### Fix 3 — several epochs per batch

With the ratio and the clip in place, you can safely take several gradient
steps on one expensive batch of generations. Typical LLM runs do 1–4 epochs.
More than that and most samples clip out anyway, so you are spending compute to
produce zero gradient.

### Fix 4 — a KL penalty to the reference model

The last fix is specific to language models, and it is the one with the most
character. A reward model is not the truth; it is a model, trained on finite
data, with holes in it. A policy optimised hard enough against it will find the
holes — strings that score wonderfully and read like nothing a person would
write. The literature calls it **reward hacking** and
[31.4](04-reward-models.md) is largely about it.

The standard defence: keep a frozen copy of the model as it was before RL — the
**reference policy** $\pi_{\text{ref}}$, usually the SFT checkpoint — and charge
the policy for every step it takes away from it.

$$
r_{\text{total}} = r_{\text{RM}}(\tau) - \beta \, \mathrm{KL}\!\left(\pi_\theta \,\|\, \pi_{\text{ref}}\right)
$$

This regularised objective has a beautiful property: its exact optimum can be
written down in closed form.

$$
\pi^{*}(a) \;\propto\; \pi_{\text{ref}}(a)\, \exp\!\left(\frac{r(a)}{\beta}\right)
$$

*Start from the reference distribution, and re-weight it by the exponential of
the reward.* You do not need to trust that — you can compute it on five
candidate responses, one of which is a reward-model exploit.

```python
import numpy as np

RESPONSES = ["terse", "rambling", "good", "great", "GAMED"]
pi_ref = np.array([0.40, 0.30, 0.20, 0.08, 0.02])   # what the SFT model produces
r_rm   = np.array([0.10, 0.20, 0.85, 1.10, 1.60])   # what the reward model says
r_true = np.array([0.10, 0.15, 0.85, 1.00, -1.00])  # what a human would say

print(f"{'beta':>6}" + "".join(f"{name:>10}" for name in RESPONSES)
      + f"{'true quality':>15}")
print(f"{'ref':>6}" + "".join(f"{p:>10.3f}" for p in pi_ref)
      + f"{float(pi_ref @ r_true):>15.3f}")
for beta in [10.0, 3.0, 1.0, 0.3, 0.1]:
    w = pi_ref * np.exp(r_rm / beta)
    star = w / w.sum()                       # the exact KL-regularised optimum
    print(f"{beta:>6.1f}" + "".join(f"{p:>10.3f}" for p in star)
          + f"{float(star @ r_true):>15.3f}")
```

Read the `true quality` column down the page — it is an arc, and that arc is the
whole of RLHF in one table. The reference policy scores 0.315. At $\beta = 10$
the KL penalty dominates and the optimum is barely distinguishable from the
reference: safe, and almost useless (0.324). At $\beta = 1$ true quality peaks
at 0.395 — the policy has shifted real mass onto `good` and `great` and away
from `terse`, which is exactly the improvement we wanted. Push further and it
inverts: by $\beta = 0.3$ the exploit is already the single most likely response
and true quality has fallen to 0.171, below where we started; by $\beta = 0.1$
the policy puts 97% of its mass on the exploit, its reward-model score is superb,
and its true quality is $-0.938$.

$\beta$ is the dial between "did not learn anything" and "learned to cheat",
there is a genuine optimum in between, and it is not marked. Finding it — by
measuring true quality on held-out data, not by watching the reward go up — is a
real part of the job.

Remember this formula. In [31.3](03-dpo-grpo.md), solving it for $r$ instead of
for $\pi$ is the entire idea behind DPO.

## A toy PPO loop

Now all four fixes at once, on the same contextual bandit. The rewards here are
deliberately hard: `apologise` (1.0) barely beats `explain` (0.8) for the angry
customer, the noise is large, and the batch is only eight samples — so batches
frequently *disagree with the truth*, which is exactly the regime where an
unclipped update does damage.

```python
import numpy as np

REWARD = np.array([[1.0, 0.8, -1.0],
                   [0.2, 1.0, -0.5]])
NOISE, CLIP_EPS = 1.5, 0.2

def softmax(z):
    e = np.exp(z - z.max())
    return e / e.sum()

def ppo(use_clip, seed, n_iters=60, epochs=8, lr=1.0, batch=8):
    rng = np.random.default_rng(seed)
    theta, value = np.zeros((2, 3)), np.zeros(2)    # actor and (tiny) critic
    clip_counts, kls = [], []
    for _ in range(n_iters):
        # --- rollout: generate a batch with the CURRENT policy, then freeze it
        ctx = rng.integers(2, size=batch)
        act = np.empty(batch, dtype=int)
        logp_old, rew = np.empty(batch), np.empty(batch)
        for i, c in enumerate(ctx):
            p = softmax(theta[c])
            a = int(rng.choice(3, p=p))
            act[i], logp_old[i] = a, np.log(p[a])
            rew[i] = REWARD[c, a] + NOISE * rng.normal()
        before = np.array([softmax(theta[c]) for c in (0, 1)])

        # --- advantages: reward minus the critic's estimate, then standardised
        adv = rew - value[ctx]
        for c in (0, 1):
            m = ctx == c
            if m.any():
                value[c] += 0.3 * (rew[m].mean() - value[c])   # critic update
        adv = (adv - adv.mean()) / (adv.std() + 1e-8)

        # --- several epochs on the SAME batch, thanks to the ratio
        clipped = 0
        for _ in range(epochs):
            grad = np.zeros_like(theta)
            for i in range(batch):
                c, a, A = ctx[i], act[i], adv[i]
                p = softmax(theta[c])
                ratio = np.exp(np.log(p[a]) - logp_old[i])
                binding = use_clip and ((A > 0 and ratio > 1 + CLIP_EPS) or
                                        (A < 0 and ratio < 1 - CLIP_EPS))
                if binding:
                    clipped += 1          # objective is flat here: no gradient
                    continue
                onehot = np.zeros(3)
                onehot[a] = 1.0
                grad[c] += A * ratio * (onehot - p)
            theta += lr * grad / batch
        after = np.array([softmax(theta[c]) for c in (0, 1)])
        kls.append(float(np.sum(before * np.log(before / after))))
        clip_counts.append(clipped / (epochs * batch))
    true_reward = float(np.mean([REWARD[c] @ softmax(theta[c]) for c in (0, 1)]))
    return true_reward, float(np.mean(clip_counts)), float(np.max(kls))

print(f"{'run':>10}{'mean true reward':>19}{'worst seed':>13}"
      f"{'clip fired':>13}{'max KL/iter':>14}")
for use_clip in [True, False]:
    runs = [ppo(use_clip, seed) for seed in range(12)]
    scores = [r[0] for r in runs]
    print(f"{'clipped' if use_clip else 'unclipped':>10}"
          f"{np.mean(scores):>19.3f}{min(scores):>13.3f}"
          f"{np.mean([r[1] for r in runs]):>12.1%}{max(r[2] for r in runs):>14.3f}")
```

Twelve seeds each. The clipped runs average 0.957 true reward with a worst seed
of 0.892, and the clip fires on about 12% of sample-epochs — proof that it is
actually binding rather than decorative. The unclipped runs average 0.907 with a
worst seed of **0.250**: one of the twelve collapsed onto the wrong action and
never came back.

That is the honest shape of the result, and it is worth stating plainly. Without
clipping, most runs are fine and slightly *sharper* than the clipped ones — the
last column tells you why they are not safe: the largest single-iteration KL is
0.169 with clipping and 11.9 without. Unclipped PPO occasionally takes a step
seventy times larger than it should, and on a language model such a step does
not produce a slightly worse policy; it produces one that emits the same token
forever. **Clipping trades a little final performance for the guarantee that no
single batch can destroy the run** — and when a run costs thousands of GPU-hours,
that is a trade you take every time.

## The bill: four models in memory

Everything above is the algorithm. Here is why PPO for LLMs is an
infrastructure project. Count the models you must hold:

1. the **policy** — being trained, so weights *and* gradients *and* optimiser
   state;
2. the **reference** — frozen, inference only, for the KL penalty;
3. the **reward model** — frozen, inference only, to score responses;
4. the **value model** (critic) — also being trained, so also a full optimiser
   state.

Mixed-precision Adam costs about 16 bytes per trainable parameter (bf16 weights
2, bf16 gradients 2, fp32 master copy 4, and Adam's two moment buffers at 4
each). A frozen model costs 2. And on top of all that, generation needs a KV
cache — the structure from
[Section 27.1](../ch27-inference/01-kv-cache.md) — because every RL step begins
by generating fresh responses.

```python
GB = 1024 ** 3

def training_gb(n_params):
    """bf16 weights + bf16 grads + fp32 master + Adam m + Adam v = 16 bytes."""
    return n_params * 16 / GB

def frozen_gb(n_params):
    """Inference only: bf16 weights."""
    return n_params * 2 / GB

def kv_cache_gb(n_layers, hidden, n_tokens, bytes_per=2):
    """2 (K and V) x layers x hidden x bytes, per token — see Section 27.1."""
    return 2 * n_layers * hidden * bytes_per * n_tokens / GB

P7B, LAYERS, HIDDEN = 7e9, 32, 4096
kv = kv_cache_gb(LAYERS, HIDDEN, n_tokens=32 * 1024)     # 32 seqs x 1024 tokens

recipes = {
    "PPO":  [("policy", "train"), ("reference", "frozen"),
             ("reward model", "frozen"), ("value model", "train")],
    "DPO":  [("policy", "train"), ("reference", "frozen")],
    "GRPO (rule reward)": [("policy", "train"), ("reference", "frozen")],
}
print(f"{'recipe':>20}{'models':>8}{'weights+opt (GB)':>19}{'+KV cache':>12}"
      f"{'80GB GPUs':>11}")
for name, parts in recipes.items():
    total = sum(training_gb(P7B) if kind == "train" else frozen_gb(P7B)
                for _, kind in parts)
    print(f"{name:>20}{len(parts):>8}{total:>19.1f}{total + kv:>12.1f}"
          f"{-(-(total + kv) // 80):>11.0f}")
print(f"\nKV cache for 32 sequences x 1024 tokens at 7B: {kv:.1f} GB")
print(f"one trainable 7B model: {training_gb(P7B):.1f} GB   "
      f"one frozen 7B model: {frozen_gb(P7B):.1f} GB")
```

Look at the two single-model figures at the bottom first, because they carry the
whole argument: a *trainable* 7B model costs 104 GB, while a *frozen* one costs
13 GB. Optimiser state, not weights, is what fills a GPU — the weights are 12%
of the trainable figure.

So a 7B PPO setup needs about 235 GB of weights and optimiser state, 251 GB
once a modest KV cache for the rollouts is added, and that is before
activations: four 80 GB GPUs at an absolute minimum, in practice more. All four
models must be resident *simultaneously*, because every step touches every one
of them. Scale to 70B and multiply by ten. The two-model recipes need 117 GB,
133 GB with the cache — half the hardware — and one of their two models never
needs an optimiser state at all.

That number is the reason the rest of this chapter exists. Two of the four
models — the value model and the reward model — are pure overhead in the sense
that neither is the thing you are shipping. Delete the reward model and you get
DPO. Delete the value model and you get GRPO. Both are in
[31.3](03-dpo-grpo.md).

!!! warning "Common mistakes"
    - **Forgetting the baseline.** Without one, a constant offset in your
      reward — which reward models have, since their scores are only defined
      up to a shift — can multiply gradient variance by hundreds and break the
      run entirely.
    - **Reading the clip as "clip the gradient".** It is not gradient
      clipping. It clips the *objective*, which removes the gradient in one
      direction only; the pull back towards the trust region stays alive.
    - **Cranking the epoch count.** Once most samples have clipped out you are
      burning compute for zero gradient, and the samples that have *not*
      clipped are the outliers you least want to over-fit.
    - **Setting $\beta$ to zero because the KL term "slows learning down".**
      It does slow learning down. It is also the only thing standing between
      your policy and a reward-model exploit, as the $\beta = 0.1$ row showed.
    - **Budgeting memory for one model.** PPO needs four, two of them with
      optimiser state, plus a KV cache large enough to generate a whole batch.

## Check your understanding

1. In REINFORCE, why does an action with return $0$ produce no update at all,
   even though it was sampled?

    ??? success "Answer"

        The gradient contribution is $G_t \nabla_\theta \log \pi_\theta(a_t)$
        and $G_t = 0$ scales the whole direction to nothing. This is also why
        baselines matter so much: with a baseline the multiplier becomes
        $G_t - b$, so "exactly average" actions produce no update, and only
        genuine surprises move the policy.

2. A sample has advantage $A = +2$ and its ratio has reached $1.4$ with
   $\epsilon = 0.2$. What does the PPO objective contribute, and what does its
   gradient contribute?

    ??? success "Answer"

        The unclipped term is $1.4 \times 2 = 2.8$; the clipped term is
        $1.2 \times 2 = 2.4$; the `min` takes $2.4$. That value does not depend
        on $\theta$ any more, so the gradient is **zero** — the update stops
        pushing this sample. Had the advantage been negative, the same ratio of
        $1.4$ would still be live, because the clip only removes the incentive
        in the direction that is already overshooting.

3. Your reward model outputs scores between 5 and 9, and your policy stops
   improving. Give the most likely cause and the one-line fix.

    ??? success "Answer"

        Every reward is strongly positive, so every sampled action is
        reinforced and the gradient is dominated by a constant offset. Subtract
        a baseline — a running mean, a learned value function, or the mean over
        the batch. The offset demo above showed this exact failure: with a
        $+10$ shift and no baseline the policy collapsed onto one action in
        both contexts.

4. Someone proposes dropping the reference model to halve memory. What
   specifically are you now unprotected against?

    ??? success "Answer"

        Unbounded drift from the SFT distribution — reward hacking. Without the
        KL term the objective is "maximise the reward model", and the reward
        model has holes; the closed-form optimum at $\beta \to 0$ puts all its
        mass on whatever scores highest, which in the demo was the exploit with
        *negative* true quality. Note the reference model is also the cheapest
        of the four (frozen, 14 GB at 7B), so it is the worst possible place to
        save memory.
