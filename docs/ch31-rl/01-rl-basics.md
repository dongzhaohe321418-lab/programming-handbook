# 31.1 RL from first principles

Every model you have met so far in Part V was trained by being shown the right
answer. Reinforcement learning is what you do when nobody has the right answer
but somebody can tell you how good yours was — and that turns out to describe
almost everything we want from a chat model. This section builds the whole
vocabulary from zero: what a policy is, what a reward is, what a *gradient* is
(we will measure one with a ruler before we ever write a derivative), and a
baseline algorithm so simple that it is genuinely the right answer surprisingly
often.

## Two kinds of learning signal

Pretraining and supervised fine-tuning both work the same way: you have a
correct output, the model produces a different output, and you nudge the
weights so that next time its output is closer to the correct one. Call this
**supervised learning** — *here is the right answer*.

Now consider a prompt like "write a condolence message to a colleague whose
project was cancelled". There is no right answer. There are thousands of good
ones and millions of bad ones, and no human being is going to write out the
target text for every prompt a chat model will ever see. But a human can read
two candidate messages and say which one is better in about four seconds. That
is **reinforcement learning** — *here is how good your answer was*.

The gap between those two is the entire reason RL matters for language models:

!!! note "The asymmetry that makes RL worth it"
    **Judging is easier than producing.** You can tell that a proof is wrong
    without being able to write the correct proof. You can tell that code is
    buggy by running its tests without being able to write the code. You can
    rank two summaries without being able to write a better one. RL lets you
    convert that cheap judgement into training signal — which means a model
    can be pushed towards behaviour that *nobody demonstrated*, because the
    only thing anyone had to supply was a score.

Two consequences follow immediately, and they shape everything in this chapter.
First, the signal is much thinner: one number for a whole 500-token response,
instead of a correct token at every position. Second, the model has to *produce
its own training data* — you cannot score a response that was never generated.
That is why RL training loops sample, then score, then update, forever.

| | Supervised fine-tuning | Reinforcement learning |
| --- | --- | --- |
| What you need | (prompt, ideal response) pairs | a way to score responses |
| Signal per example | one target token per position | one number per response |
| Who writes the data | humans, or a stronger model | the model being trained |
| Can it exceed its data? | no — it imitates | yes — it can find responses nobody wrote |
| Cost per example | high (writing) | low (judging) |
| Failure mode | copies style without substance | games the scorer |

## The vocabulary, defined twice

RL has seven words you must have. Every one of them is easier to see in a grid
than in a language model, so here is each defined against both.

| Term | Grid world | Language model |
| --- | --- | --- |
| **state** $s$ | which square you stand on | the prompt plus every token generated so far |
| **action** $a$ | move up / down / left / right | emit one token from the vocabulary |
| **policy** $\pi(a \mid s)$ | your rule for choosing a move | the model itself — a distribution over the next token |
| **reward** $r$ | $-1$ per step, $+10$ on the goal | usually $0$ per token, one score at the end |
| **trajectory** $\tau$ | the path you actually walked | the complete generated response |
| **return** $G$ | total reward collected on that path | the response's score |
| **discount** $\gamma$ | how much you care about later reward | usually $1.0$ for a single response |

Notice what the LLM column implies. The model you have been calling a "next
token predictor" *is a policy* — no modification required. Sampling from it
(Chapter 26.4's [sampler](../ch26-llm-internals/04-sampling.md)) *is* running a
policy for one episode. Generating a response *is* rolling out a trajectory.
RL for LLMs is not bolting a new machine onto the model; it is noticing that the
model was already an RL agent and we had simply never scored it.

Here is a trajectory in the grid, with its return computed both undiscounted
and discounted.

```python
import numpy as np

# A 4x4 grid. Start at (0, 0), goal at (3, 3). Each step costs -1;
# arriving at the goal pays +10. This is the whole "environment".
GOAL = (3, 3)
MOVES = {"right": (0, 1), "down": (1, 0), "left": (0, -1), "up": (-1, 0)}

def step(state, action):
    """Environment: given a state and an action, return (next_state, reward)."""
    dr, dc = MOVES[action]
    r, c = state[0] + dr, state[1] + dc
    r, c = min(max(r, 0), 3), min(max(c, 0), 3)      # walls: you just stay put
    nxt = (r, c)
    return nxt, (10.0 if nxt == GOAL else -1.0)

# A trajectory is what happens when a policy meets the environment.
plan = ["right", "right", "down", "down", "right", "down"]
state, trajectory = (0, 0), []
for action in plan:
    nxt, reward = step(state, action)
    trajectory.append((state, action, reward, nxt))
    state = nxt

print(f"{'t':>2} {'state':>8} {'action':>7} {'reward':>7} {'next':>8}")
for t, (s, a, r, n) in enumerate(trajectory):
    print(f"{t:>2} {str(s):>8} {a:>7} {r:>7.1f} {str(n):>8}")

rewards = np.array([r for _, _, r, _ in trajectory])
for gamma in [1.0, 0.9, 0.5]:
    weights = gamma ** np.arange(len(rewards))
    print(f"gamma = {gamma:<4} -> return G = {float(rewards @ weights):.3f}")
```

The **return** is just the sum of the rewards, optionally with later ones shrunk
by $\gamma$ per step:

$$
G = \sum_{t=0}^{T-1} \gamma^{t} r_t
$$

Read the three lines of output together. At $\gamma = 1.0$ every reward counts
fully. At $\gamma = 0.5$ the $+10$ at the end has been multiplied by
$0.5^5 = 0.03125$, so it barely registers and the return goes *negative* — a
$\gamma$ that small describes an agent too impatient to walk to the goal at all.
For LLM training we almost always use $\gamma = 1$: a response is short, it ends,
and we do not want the model to prefer earlier tokens over later ones.

## The simplest RL problem: three slot machines

Strip away states and sequences and you get the **multi-armed bandit**: $k$
levers, each paying out from an unknown distribution, and you want to maximise
total payout. There is only one state, so a policy is just "which lever". Every
hard idea in RL is already visible here.

The tension is **exploration versus exploitation**. Pull the lever that looks
best so far and you might be stuck on a mediocre one you got lucky with. Pull
random levers and you knowingly waste money. **Epsilon-greedy** splits the
difference: with probability $\varepsilon$ pull a random lever, otherwise pull
the best-looking one. The estimate $Q(a)$ of a lever's value is just the running
average of what it has paid.

```python
import numpy as np
import matplotlib.pyplot as plt

TRUE_MEANS = np.array([0.30, 0.55, 0.50])   # arm 1 is best; arm 2 is a near-miss
BEST = TRUE_MEANS.max()

def run_bandit(epsilon, n_steps=2000, seed=0):
    """Epsilon-greedy over 3 Bernoulli arms. Returns estimates, pulls, regret."""
    rng = np.random.default_rng(seed)
    Q = np.zeros(3)          # value estimate for each arm (starts at zero)
    N = np.zeros(3)          # how many times each arm was pulled
    regret, running = np.zeros(n_steps), 0.0
    for t in range(n_steps):
        if rng.random() < epsilon:
            a = int(rng.integers(3))          # explore: pick uniformly
        else:
            a = int(Q.argmax())               # exploit: pick the current best
        reward = float(rng.random() < TRUE_MEANS[a])   # pays 1 or 0
        N[a] += 1
        Q[a] += (reward - Q[a]) / N[a]        # running mean, no list needed
        running += BEST - TRUE_MEANS[a]       # what this pull cost us
        regret[t] = running
    return Q, N, regret

print(f"true means: {TRUE_MEANS}   (arm 1 is optimal)\n")
print(f"{'eps':>5}{'Q0':>7}{'Q1':>7}{'Q2':>7}{'pulls of arm 1':>16}{'regret':>9}")
curves = {}
for eps in [0.0, 0.02, 0.10, 0.50]:
    Q, N, regret = run_bandit(eps)
    curves[eps] = regret
    print(f"{eps:>5.2f}{Q[0]:>7.3f}{Q[1]:>7.3f}{Q[2]:>7.3f}"
          f"{int(N[1]):>12}/2000{regret[-1]:>9.1f}")

fig, ax = plt.subplots(figsize=(7.0, 3.6))
for eps, regret in curves.items():
    ax.plot(regret, label=f"epsilon = {eps}")
ax.set_xlabel("pull number")
ax.set_ylabel("cumulative regret")
ax.set_title("Exploration is an investment: it costs early and pays later")
ax.legend()
fig.tight_layout()
```

**Regret** is the gap between what you earned and what a perfect player would
have earned. Read the curves as slopes, not heights: a flat curve means you are
currently playing optimally, and a straight line means you are losing at a
constant rate and learning nothing.

The $\varepsilon = 0$ curve is the lesson. It is a perfectly straight line
ending at 500 regret, because a purely greedy agent that starts with
$Q = [0, 0, 0]$ picks arm 0 (the first maximum), and — since arm 0's estimate
can only stay at or below zero while the others remain exactly zero — never has
a reason to try anything else. Look at the printed estimates: `Q1` and `Q2` are
still exactly `0.000`, because those arms were never pulled at all. The agent
locked onto the worst arm and paid for it 2000 times. **A policy that never
explores can only ever confirm what it already believes.**

$\varepsilon = 0.02$ shows the subtler failure. It escapes arm 0 — but it
settles on arm 2, whose true mean of 0.50 is barely below arm 1's 0.55. With
only 19 pulls of arm 1 in 2000 it never gathers enough evidence to tell the two
apart, so its curve keeps climbing at a shallow constant slope, ending near 292.
Too little exploration does not merely slow you down; it leaves you confidently
committed to a near-miss.

$\varepsilon = 0.10$ is the one that works: 1682 of 2000 pulls on the best arm
and a curve that bends over almost flat, final regret about 32. And
$\varepsilon = 0.50$ shows the opposite excess — its $Q$ estimates are the most
accurate of the four (0.308 / 0.559 / 0.518, close to the true means, because
every arm gets pulled hundreds of times) and yet it accumulates four times the
regret of $\varepsilon = 0.10$, because it spends half of every session throwing
away what it knows. Knowing the right answer earns nothing if you do not use it.

This trade-off never goes away. In an LLM run, temperature and top-p are your
$\varepsilon$: too low and the model only ever regenerates what it already does,
so RL has nothing new to score; too high and you are scoring nonsense.

## What a gradient is, measured with a ruler

Everything from here on "takes a gradient step". You do not need a calculus
course to know exactly what that means. You need one idea: **a gradient is a
slope, and you can measure a slope by wiggling.**

Take a **loss** — any function of your parameters that you want to be small.
Here is a deliberately tiny one with a single parameter $w$:

$$
L(w) = (w - 3)^2 + 2
$$

To find its slope at some $w$, nudge $w$ by a tiny amount $h$ in each direction
and see how much $L$ changed. Rise over run. That is a **finite difference**, and
it is arithmetic — no symbols, no rules to memorise.

```python
def loss(w):
    return (w - 3.0) ** 2 + 2.0

def numeric_slope(f, w, h=1e-5):
    """Rise over run: how much does f change per unit of w, right here?"""
    return (f(w + h) - f(w - h)) / (2 * h)

print(f"{'w':>6}{'L(w)':>10}{'slope':>10}   what the slope tells you")
for w in [0.0, 2.0, 3.0, 5.0]:
    s = numeric_slope(loss, w)
    direction = "go right" if s < 0 else ("go left" if s > 0 else "you are at the bottom")
    print(f"{w:>6.1f}{loss(w):>10.4f}{s:>10.4f}   {direction}")
```

The sign is the whole message. A **positive** slope means "moving right
increases the loss", so to *decrease* the loss you move left. A **negative**
slope means the opposite. In both cases the rule is the same, and it is the rule
every optimiser in this chapter uses:

$$
w \leftarrow w - \eta \cdot \frac{dL}{dw}
$$

Subtract the slope, scaled by a **learning rate** $\eta$. That is **gradient
descent** — "the gradient points uphill, so walk the other way". Let us walk.

```python
# continues
import matplotlib.pyplot as plt
import numpy as np

w, eta, history = 0.0, 0.2, []
for step_i in range(25):
    g = numeric_slope(loss, w)
    history.append((w, loss(w), g))
    w = w - eta * g                        # the one line that does the learning

print(f"{'step':>5}{'w':>9}{'L(w)':>10}{'slope':>10}")
for i in [0, 1, 2, 5, 10, 24]:
    wi, li, gi = history[i]
    print(f"{i:>5}{wi:>9.5f}{li:>10.5f}{gi:>10.5f}")
print(f"\nminimum found at w = {w:.6f} (the true minimum is w = 3)")

grid = np.linspace(-1.0, 7.0, 200)
fig, axes = plt.subplots(1, 2, figsize=(9.0, 3.4))
axes[0].plot(grid, [loss(x) for x in grid], color="0.7")
axes[0].plot([h[0] for h in history], [h[1] for h in history], "o-", ms=4)
axes[0].set_xlabel("w"); axes[0].set_ylabel("L(w)")
axes[0].set_title("walking downhill")
axes[1].plot([h[1] for h in history], "o-", ms=4)
axes[1].set_xlabel("step"); axes[1].set_ylabel("L(w)")
axes[1].set_title("the loss curve")
fig.tight_layout()
```

The steps are large where the hill is steep and shrink automatically as it
flattens, because the step size *is* the slope. That self-braking behaviour is
why the same learning rate works far from and near the optimum.

Now the analytic form. For $L(w) = (w-3)^2 + 2$ the derivative is

$$
\frac{dL}{dw} = 2(w - 3)
$$

You can take that on faith — but you should never take it on faith in your own
code, and researchers do not. The **gradient check** is a real, everyday
practice: compute the gradient your formula claims, compute it again by finite
differences, and assert they agree. If your hand-derived gradient has a sign
error or a missing factor, this catches it in one second instead of after a
six-hour training run that silently learns nothing.

```python
# continues
def analytic_slope(w):
    return 2.0 * (w - 3.0)

print(f"{'w':>7}{'analytic':>12}{'numeric':>12}{'abs diff':>12}")
worst = 0.0
for w in [-2.0, 0.0, 1.5, 3.0, 4.7, 9.0]:
    a, n = analytic_slope(w), numeric_slope(loss, w)
    worst = max(worst, abs(a - n))
    print(f"{w:>7.1f}{a:>12.6f}{n:>12.6f}{abs(a - n):>12.2e}")
assert worst < 1e-4, "gradient check FAILED"
print(f"\nworst disagreement {worst:.2e} — gradient check passed")
```

They agree to nine or ten decimal places, and the leftover difference is
floating-point noise in the subtraction, not an error in the formula. The
`assert` is the point: this is a *test*, in exactly the sense of
[Section 24.2](../ch24-practice/02-testing.md), and it belongs in your suite.
Every
analytic gradient in this chapter — REINFORCE, DPO, the reward model — will be
checked against finite differences exactly like this before we trust it.

!!! tip "Why not just use finite differences for everything?"
    Because it costs two full evaluations *per parameter*. For our one
    parameter that is 2 forward passes; for a 7-billion-parameter model it is
    14 billion, per step. The analytic gradient gets all of them from a single
    backward pass. Finite differences are the ruler you check the machine
    with — never the machine.

## Softmax policies and log-probabilities

For a policy over a handful of actions, the standard parameterisation is the one
you already know from [26.4](../ch26-llm-internals/04-sampling.md): keep one real
number ("logit", or "preference") per action and push them through a softmax.

$$
\pi_\theta(a) = \frac{e^{\theta_a}}{\sum_{a'} e^{\theta_{a'}}}
$$

RL formulas are written in terms of $\log \pi_\theta(a)$, the **log-probability**
of the action actually taken, for three reasons: probabilities of long sequences
underflow to zero while their logs add up harmlessly; a product of per-token
probabilities becomes a sum of per-token log-probs; and the gradient of the log
is unusually clean, which is what makes the next section work.

```python
import numpy as np

ACTIONS = ["apologise", "explain", "joke"]
theta = np.array([0.0, 1.0, -0.5])          # the policy's parameters

def softmax(z):
    e = np.exp(z - z.max())
    return e / e.sum()

probs = softmax(theta)
logps = np.log(probs)
print(f"{'action':<11}{'theta':>8}{'pi(a)':>9}{'log pi(a)':>12}")
for a, th, p, lp in zip(ACTIONS, theta, probs, logps):
    print(f"{a:<11}{th:>8.2f}{p:>9.4f}{lp:>12.4f}")

# A whole response is a sequence of actions: log-probs add.
response = ["explain", "explain", "joke"]
total_logp = sum(logps[ACTIONS.index(a)] for a in response)
print(f"\nlog pi(response) = {total_logp:.4f}"
      f"   ->  pi(response) = {np.exp(total_logp):.6f}")

# Raising one logit by 1.0 does not raise its probability by 1.0.
bumped = softmax(theta + np.array([0.0, 1.0, 0.0]))
print(f"after theta[explain] += 1: pi = {np.round(bumped, 4)}"
      f"  (the other two shrank without being touched)")
```

That last line is the property to carry forward. Softmax is **competitive**:
pushing one action up automatically pushes every other one down, because the
probabilities must sum to one. Every RL update in this chapter exploits that —
you never have to say "and make the bad action less likely"; raising the good one
does it for free.

## The baseline everyone should try first

Before any gradient, there is a technique so simple it barely deserves a name:
**sample several responses, keep the best one**. It is called **best-of-$n$** at
inference time and **rejection sampling fine-tuning** when you then train on the
winners. It needs no new algorithm, no new model in memory, and no stability
tricks — and on many tasks it captures a large share of what full RL delivers.

```python
import numpy as np

rng = np.random.default_rng(7)

def fake_llm(prompt, n, rng):
    """Stand-in for a real model: returns n candidate responses.

    A real call would be client.messages.create(...); here each candidate is
    just a quality score drawn from the model's (fixed) response distribution.
    """
    return rng.normal(loc=0.0, scale=1.0, size=n)

def reward(response):
    """Stand-in for a verifier or a reward model: scores one response."""
    return response

print(f"{'n':>5}{'mean score of best-of-n':>26}{'gain':>9}{'KL cost (nats)':>17}")
base = None
for n in [1, 2, 4, 16, 64]:
    trials = [max(reward(r) for r in fake_llm("prompt", n, rng))
              for _ in range(4000)]
    score = float(np.mean(trials))
    base = score if base is None else base
    kl = np.log(n) - (n - 1) / n                # cost of best-of-n, in nats
    print(f"{n:>5}{score:>26.4f}{score - base:>9.4f}{kl:>17.4f}")
```

Two things to take from the table. Best-of-$n$ *works*: going from 1 sample to
64 moves the average score by about 2.36 — over two standard deviations of the
model's own output distribution — with no training whatsoever. And it has
**diminishing returns**: the first doubling buys $0.58$, the jump from 16 to 64
buys $0.58$ as well while costing four times as much compute. The gain grows
roughly like $\sqrt{\log n}$, so every doubling is worth less than the last.

The right-hand column prices that gain in the same currency the rest of this
chapter uses. Best-of-$n$ shifts the output distribution away from the model's
own by about $\log n - \frac{n-1}{n}$ nats of **KL divergence** — a measure of
how far one distribution has moved from another, which we will meet again in
[31.2](02-policy-gradient-ppo.md) as an explicit penalty term. Every method in
this chapter is buying reward with KL; best-of-$n$ just makes the exchange rate
unusually easy to see.

Turning this into *training* is one more step: generate $n$ responses per prompt,
keep the best, and fine-tune on those pairs with ordinary supervised learning.
That is rejection sampling fine-tuning (sometimes "RAFT" or "best-of-$n$
distillation"), it is one of the two or three most-used post-training recipes in
practice, and it is a completely reasonable thing to ship. Everything after this
section exists because it has two limits: it can only ever select from what the
model already produces, and it throws away every rejected sample instead of
learning from the fact that it *was* rejected.

!!! warning "Common mistakes"
    - **Confusing reward with loss.** Reward goes *up*, loss goes *down*. Every
      RL objective in this chapter is written as a loss (the negative of
      something you want to maximise) so that the same "subtract the gradient"
      rule applies. Get the sign wrong and your model reliably learns to be
      terrible, which is at least easy to spot.
    - **Setting $\varepsilon$ (or temperature) to zero and calling it
      training.** With no exploration the model regenerates what it already
      does, every sample scores about the same, and there is nothing to learn
      from. RL runs need sampling turned on.
    - **Trusting a hand-derived gradient.** Always finite-difference-check it.
      A wrong gradient does not crash; it quietly trains the wrong thing.
    - **Reaching for PPO before trying best-of-$n$.** If sampling 8 responses
      and picking the best solves your problem, you have saved yourself three
      extra models in GPU memory and a week of tuning.
    - **Assuming a discount $\gamma < 1$ is always safer.** In the grid world
      $\gamma = 0.5$ made reaching the goal not worth walking to. For
      single-response LLM training, $\gamma = 1$ is the normal choice.

## Check your understanding

1. Why can reinforcement learning produce behaviour that supervised fine-tuning
   on the same budget cannot?

    ??? success "Answer"

        Supervised fine-tuning can only imitate the responses in its dataset,
        so it is bounded by whoever wrote them. RL only needs a *scorer*, and
        the responses being scored are generated by the model itself — so it
        can discover a response nobody demonstrated, as long as the scorer
        recognises it as good. The catch is that it is also bounded, by the
        scorer: it will find whatever the scorer rewards, including mistakes
        in the scorer.

2. Your greedy ($\varepsilon = 0$) bandit agent has a perfectly straight regret
   curve. What has happened, and what is the minimal fix?

    ??? success "Answer"

        A straight line means constant regret per pull — the agent is playing
        the same suboptimal arm every time and learning nothing. It committed
        to whichever arm looked best after almost no data and now has no
        mechanism to revisit that. The minimal fix is any exploration at all:
        a small $\varepsilon$, or optimistic initial values (set $Q$ high so
        every arm must be tried before it can be ruled out).

3. `numeric_slope(loss, 5.0)` returns $+4$. Which way do you move $w$, and by
   how much if $\eta = 0.1$?

    ??? success "Answer"

        A positive slope means the loss increases as $w$ increases, so you move
        *left*: $w \leftarrow 5.0 - 0.1 \times 4 = 4.6$. Check it against the
        function — $L(5) = 6$ and $L(4.6) = 4.56$, so the loss went down.

4. Best-of-64 scores much better than a single sample. Why is that not the end
   of the chapter?

    ??? success "Answer"

        Because it costs 64 forward passes *at every request, forever* — the
        model itself never improved. It can also only pick from what the model
        already generates, so it cannot reach behaviour outside that
        distribution, and it discards the information in the 63 rejected
        samples. Training methods pay the cost once and change the policy, and
        they learn from losers as well as winners.
