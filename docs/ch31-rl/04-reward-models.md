# 31.4 Reward models — PRM, RLHF, RLAIF

Every algorithm in this chapter maximises a number. Sections 31.2 and 31.3
taught you how to maximise it efficiently; this section is about where the
number comes from, and it is the part practitioners lose sleep over. An RL run
does not learn what you want — it learns what you *measured*, with a
thoroughness no human employee would ever apply. So the reward function is not
a configuration detail. It is the specification, and it is where almost all the
real failures live.

## Humans compare; they do not score

The obvious way to get a reward is to ask someone to rate a response out of ten.
It does not work. Ask five annotators to score the same answer and you get 6, 7,
7, 9, and 4 — and the same annotator will drift over a shift, anchor on whatever
they saw last, and use a different part of the scale on Friday than on Monday.
Absolute scores are **uncalibrated**: the number depends on the rater as much as
on the response.

Comparisons are far more robust. "Is A better than B?" removes the scale
entirely; there is nothing to calibrate. It is faster, it has higher
inter-annotator agreement, and — as [31.3](03-dpo-grpo.md) showed — it is
exactly the form that Bradley-Terry and DPO consume. That is why essentially all
preference data is pairwise. The cost is real: a comparison carries at most one
bit, and it tells you nothing about *how much* better A was.

Good annotation guidelines are the other half. They must state the priority
order when criteria conflict (is a correct-but-rude answer better than a
polite-but-wrong one?), define ties, and give worked examples of hard cases.
Without an explicit ordering, annotators silently apply their own, and your
reward model learns the average of several incompatible value systems.

Then you measure whether the annotators agree, and raw agreement is a trap.

```python
def cohens_kappa(a, b, labels=("A", "B")):
    """Agreement corrected for the agreement you would get by guessing."""
    n = len(a)
    p_observed = sum(x == y for x, y in zip(a, b)) / n
    p_chance = sum((a.count(l) / n) * (b.count(l) / n) for l in labels)
    return p_observed, p_chance, (p_observed - p_chance) / (1 - p_chance)

# 20 pairwise judgements. "A" means the first response won.
balanced_1 = list("ABABBAABBABAAABBABAB")
balanced_2 = list("ABABBABBBABAAABAABAB")

# Two tired annotators who almost always click "A".
lazy_1 = list("AAAAAAAAAAAAAAAAAABA")
lazy_2 = list("AAAAAAAAAAAAAAAAAAAB")

print(f"{'annotator pair':<22}{'raw agreement':>15}{'by chance':>12}{'kappa':>9}")
for name, x, y in [("balanced, thoughtful", balanced_1, balanced_2),
                   ("both always click A", lazy_1, lazy_2)]:
    po, pe, k = cohens_kappa(x, y)
    print(f"{name:<22}{po:>15.3f}{pe:>12.3f}{k:>9.3f}")
```

Both pairs agree on 18 of 20 items — identical raw agreement of 0.900. But the
second pair agrees because they both click the same button almost every time:
chance alone predicts 0.905 agreement, so their **Cohen's kappa** is $-0.053$,
meaning they are doing very slightly *worse* than coin-flipping annotators with
their marginal habits. The first pair's kappa is 0.800. Kappa above roughly 0.6
is usually considered acceptable for preference work, above 0.8 good; if you are
below 0.4 your guidelines are the problem, not your model.

## Training a reward model: Bradley-Terry

A **reward model** turns comparisons into a scalar function. The
**Bradley-Terry** model assumes a latent quality score $r$ per response and says
the probability that $y_w$ is preferred to $y_l$ is a sigmoid of the gap:

$$
P(y_w \succ y_l) = \sigma\big(r_\phi(x, y_w) - r_\phi(x, y_l)\big)
$$

Fitting by maximum likelihood gives the loss every RLHF pipeline uses:

$$
\mathcal{L}_{\text{RM}}(\phi) = -\,\mathbb{E}_{(x,\,y_w,\,y_l)}
\Big[\log \sigma\big(r_\phi(x, y_w) - r_\phi(x, y_l)\big)\Big]
$$

If that looks like the DPO loss with $\beta \log \frac{\pi_\theta}{\pi_{\text{ref}}}$
swapped for $r_\phi$, that is exactly what it is — DPO's whole trick was
substituting one for the other.

In a real pipeline $r_\phi$ is a transformer with a scalar head. Ours is a dot
product against four features, which keeps every number visible. The *loss* and
its gradient are the real ones.

```python
import numpy as np

NAMES = ["terse but correct", "correct + example", "correct, blunt",
         "wrong and short", "polite waffle", "padded correct",
         "rambling with example", "crisp + example", "wrong with example",
         "hedged non-answer", "wrong, exhaustive", "short and rude"]
FEATURES = ["correct", "example", "polite", "length"]
#                correct example polite length (units of 300 words)
X = np.array([[1, 0, 0, 0.3], [1, 1, 1, 0.6], [1, 1, 0, 0.5], [0, 0, 1, 0.2],
              [0, 0, 1, 2.6], [1, 0, 1, 1.8], [0, 1, 1, 2.9], [1, 1, 1, 0.4],
              [0, 1, 0, 0.9], [0, 0, 1, 1.2], [0, 0, 1, 3.0], [0, 0, 0, 0.2]],
             dtype=float)

W_TRUE = np.array([2.0, 1.0, 0.6, 0.0])   # what we actually want: length is irrelevant
W_ANNOTATOR = np.array([2.0, 1.0, 0.6, 1.0])   # what annotators do: longer looks better

true_quality = X @ W_TRUE
annotator_utility = X @ W_ANNOTATOR

rng = np.random.default_rng(0)
pairs = []
for _ in range(240):                       # collect noisy human comparisons
    i, j = rng.choice(len(X), 2, replace=False)
    p_i_wins = 1 / (1 + np.exp(-(annotator_utility[i] - annotator_utility[j])))
    pairs.append((i, j) if rng.random() < p_i_wins else (j, i))
train, held_out = pairs[:180], pairs[180:]

def rm_loss_and_grad(w, data):
    """Bradley-Terry loss and its exact gradient for a linear reward model."""
    loss, grad = 0.0, np.zeros(len(w))
    for win, lose in data:
        d = X[win] - X[lose]
        sigma = 1 / (1 + np.exp(-(w @ d)))
        loss += -np.log(sigma)
        grad += -(1 - sigma) * d           # d/dw of -log sigmoid(w . d)
    return loss / len(data), grad / len(data)

w = np.zeros(4)
losses = []
for _ in range(600):
    loss, grad = rm_loss_and_grad(w, train)
    losses.append(loss)
    w -= 1.0 * grad

def accuracy(w, data):
    return float(np.mean([w @ (X[a] - X[b]) > 0 for a, b in data]))

print(f"loss {losses[0]:.4f} -> {losses[-1]:.4f}")
print(f"train accuracy {accuracy(w, train):.1%}   "
      f"held-out accuracy {accuracy(w, held_out):.1%}")
print(f"\n{'feature':<10}{'what we want':>14}{'RM learned':>13}")
for name, wt, wl in zip(FEATURES, W_TRUE, w):
    print(f"{name:<10}{wt:>14.2f}{wl:>13.3f}")
```

The reward model works: 73.3% held-out accuracy on comparisons it has never
seen, against a 50% baseline, from 180 noisy pairs. Look at the last row
though. We wanted length to count for nothing, and the model learned a weight of
$+1.205$ for it — because that is genuinely what the annotators did. **The
reward model is not wrong. It is an accurate model of a biased labelling
process**, and no amount of held-out accuracy will tell you that, because the
held-out data has the same bias.

!!! note "What is toy, what is faithful"
    Toy: twelve responses described by four hand-written features, 180 pairs,
    and a linear model. Faithful: `rm_loss_and_grad` is the Bradley-Terry
    objective and its exact gradient, the train/held-out split is how reward
    models are actually validated, and 65–75% held-out agreement is a realistic
    figure — production reward models typically land in that range, because
    humans themselves only agree about that often.

## Reward hacking, made visible

Now hand that reward model to an optimiser and let it run. The policy is a
softmax over the twelve responses; we ascend expected reward and watch two
numbers — the proxy the optimiser can see, and the true quality it cannot.

```python
# continues
import matplotlib.pyplot as plt

def softmax(z):
    e = np.exp(z - z.max())
    return e / e.sum()

proxy_reward = X @ w                     # what the reward model says

def optimise(score, steps=150, lr=0.6):
    """Gradient ascent of a softmax policy on expected score."""
    theta = np.zeros(len(X))
    got_proxy, got_true, got_len = [], [], []
    for _ in range(steps):
        p = softmax(theta)
        got_proxy.append(float(p @ score))
        got_true.append(float(p @ true_quality))
        got_len.append(float(p @ X[:, 3]))
        theta += lr * p * (score - p @ score)      # d E[score] / d theta
    return np.array(got_proxy), np.array(got_true), np.array(got_len), softmax(theta)

pr, tr, ln, policy = optimise(proxy_reward)
print(f"proxy reward   {pr[0]:.3f} -> {pr[-1]:.3f}   (up {pr[-1] - pr[0]:+.3f})")
print(f"TRUE quality   {tr[0]:.3f} -> {tr[-1]:.3f}   (down {tr[-1] - tr[0]:+.3f}, "
      f"after peaking at {tr.max():.3f} on step {int(tr.argmax())})")
print(f"mean length    {ln[0]:.2f} -> {ln[-1]:.2f}")
print(f"\nthe policy converged on {NAMES[int(policy.argmax())]!r} "
      f"with probability {policy.max():.3f}")
print(f"   its RM score is {proxy_reward[policy.argmax()]:.2f} (the highest) "
      f"and its true quality is {true_quality[policy.argmax()]:.2f}")
print(f"   the genuinely best response scores "
      f"{true_quality.max():.2f} on truth and only "
      f"{proxy_reward[int(true_quality.argmax())]:.2f} on the RM")

fig, ax = plt.subplots(figsize=(7.2, 3.4))
ax.plot(pr, label="proxy reward (what we optimise)")
ax.plot(tr, label="true quality (what we wanted)")
ax.plot(ln, "--", label="mean response length")
ax.axvline(int(tr.argmax()), color="0.8", zorder=0)
ax.set_xlabel("optimisation step")
ax.set_ylabel("value")
ax.set_title("Goodhart's law, plotted")
ax.legend(fontsize=8)
fig.tight_layout()
```

There it is. The proxy climbs from 3.028 to 4.913 and never stops looking
healthy. True quality rises for the first thirteen steps — to 1.992, a real
improvement — and then *falls*, ending at 1.608, **below where it started**. The
optimiser found `rambling with example`: incorrect, but long and polite, which
the reward model was taught to love. Mean response length went from 1.22 to 2.88.

This is **Goodhart's law**:

> When a measure becomes a target, it ceases to be a good measure.

The vertical line at step 13 is the part that should worry you. If you had
stopped there you would have shipped a genuine improvement. The reward curve
gives you no signal at all about where that line is — it looks identical either
side. That is why the only trustworthy stopping signal is an *independent*
evaluation the optimiser cannot see: a held-out human eval, a different reward
model, a rule-based check.

!!! warning "Reward hacking is not a bug in the optimiser"
    The optimiser did exactly what it was told, perfectly. Every reward-hacking
    story reduces to a specification that was subtly wrong and an optimiser
    that was fully competent. Length is the most famous leak, because verbose
    answers look thorough to a tired annotator, but the same thing happens with
    formatting, hedging, flattery, and confident tone.

## Three mitigations

**KL anchoring** you already have: [31.2](02-policy-gradient-ppo.md) showed
that $\beta$ bounds how far the policy can travel from the reference, which
bounds how deep into the hole it can fall. It is a limit on the damage, not a
fix for the measurement.

**Reward ensembles**: train several reward models on different data splits or
seeds and take the minimum (pessimism) or the mean. Exploits tend to be specific
to one model's quirks, so a response that games all five is rarer than one that
games any one of them.

**Length normalisation** attacks the most common leak directly. The practical
recipe is to fit how much of the reward is explained by length, then subtract
that component — the same debiasing idea behind length-controlled evaluations.

```python
# continues
lengths = X[:, 3]
design = np.column_stack([np.ones(len(X)), lengths])
intercept, slope = np.linalg.lstsq(design, proxy_reward, rcond=None)[0]
debiased_reward = proxy_reward - slope * lengths      # remove the length component

print(f"least-squares slope of RM score on length: {slope:.3f} points per unit")
for label, order in [("top 4 by RM score", np.argsort(-proxy_reward)[:4]),
                     ("top 4 once debiased", np.argsort(-debiased_reward)[:4])]:
    print(f"\n{label}")
    print(f"   {'response':<24}{'RM score':>10}{'debiased':>10}{'true':>8}")
    for i in order:
        print(f"   {NAMES[i]:<24}{proxy_reward[i]:>10.2f}"
              f"{debiased_reward[i]:>10.2f}{true_quality[i]:>8.2f}")

pr2, tr2, ln2, policy2 = optimise(debiased_reward)
print(f"\noptimising the DEBIASED reward:")
print(f"   true quality {tr2[0]:.3f} -> {tr2[-1]:.3f}   (was {tr[-1]:.3f})")
print(f"   mean length  {ln2[0]:.2f} -> {ln2[-1]:.2f}   (was {ln[-1]:.2f})")
print(f"   converged on {NAMES[int(policy2.argmax())]!r}")
```

The fix works and it is worth being precise about how much. Optimising the raw
reward ended at true quality 1.608; optimising the length-debiased reward ends at
3.584, which is 99.6% of the best possible 3.6, and the mean response length
*falls* from 1.22 to 0.60 instead of climbing to 2.88. One least-squares fit and
a subtraction. It is not a general solution — it only removes the leak you
thought to look for — but "measure the correlation with the suspected confounder
and subtract it" is a technique you will use repeatedly.

## Outcome versus process supervision

An **outcome reward model** (ORM) scores the final answer. A **process reward
model** (PRM) scores each intermediate step. The difference matters most exactly
where RL is most useful: multi-step reasoning.

Consider: *14 boxes of 3 pens each, plus 8 loose pens, minus 5 defective ones.*
The answer is 45. Here are three worked solutions.

```python
PROBLEM_NUMBERS = {14, 3, 8, 5}
ANSWER = 45

TRACES = {
    "sound":   [(14, "*", 3, 42), (42, "+", 8, 50), (50, "-", 5, 45)],
    "lucky":   [(14, "*", 3, 40), (40, "+", 8, 48), (48, "-", 3, 45)],
    "slipped": [(14, "*", 3, 42), (42, "+", 8, 50), (50, "-", 5, 44)],
}

def apply_op(a, op, b):
    return a * b if op == "*" else (a + b if op == "+" else a - b)

def step_is_valid(step, previous):
    """A step is sound if its inputs are legitimate AND its arithmetic is right."""
    a, op, b, claimed = step
    inputs_ok = ((a in PROBLEM_NUMBERS or a == previous) and
                 (b in PROBLEM_NUMBERS or b == previous))
    return inputs_ok and apply_op(a, op, b) == claimed

def outcome_reward(trace):
    """ORM: one number for the whole trace."""
    return 1.0 if trace[-1][3] == ANSWER else 0.0

def process_rewards(trace):
    """PRM: one number per step."""
    out, previous = [], None
    for step in trace:
        out.append(1.0 if step_is_valid(step, previous) else 0.0)
        previous = step[3]
    return out

print(f"{'trace':<10}{'steps':>32}{'ORM':>6}{'PRM mean':>10}  per-step")
for name, trace in TRACES.items():
    shown = " ".join(f"{a}{op}{b}={c}" for a, op, b, c in trace)
    pr = process_rewards(trace)
    print(f"{name:<10}{shown:>32}{outcome_reward(trace):>6.1f}"
          f"{sum(pr) / len(pr):>10.2f}  {pr}")
```

Read the ORM column: `sound` and `lucky` are indistinguishable. Both get 1.0,
because both end at 45. But `lucky` computed $14 \times 3 = 40$ and then
subtracted 3 defective pens instead of 5 — two errors that happened to cancel.
Train on outcome reward and you have just reinforced "$14 \times 3 = 40$".

The PRM column separates them: 1.00 versus 0.67, and its per-step list points at
step 0 as the failure. It also rescues `slipped`, which the ORM gives a flat
zero despite two perfectly correct steps followed by one slip — under outcome
supervision, every good step in a failed attempt is punished identically to the
bad one. That is the credit-assignment problem in miniature, and it is why
process supervision helps most on long chains.

The costs are real. Step-level labels are far more expensive to collect than
final-answer labels, and a *learned* PRM is a reward model like any other, with
the same holes and the same hackability — a policy can learn to emit steps that
look sound to the PRM. Our `step_is_valid` is a hand-written checker, not a
learned model, and it is deliberately coarse: it accepts `48 - 3 = 45` because 3
is a number in the problem, even though 3 is the wrong number to subtract. A
real PRM would need to judge intent, which is exactly the part that is hard.

## The most reliable reward is not a model at all

When the task has a checkable answer, skip the learned reward entirely. A test
suite is a reward function: deterministic, un-hackable in the ways a neural
network is hackable, and free to evaluate. This is the reward that
[31.3](03-dpo-grpo.md)'s GRPO section called *verifiable*, and it is
[Chapter 24's testing discipline](../ch24-practice/02-testing.md) pointed at a
model instead of at a developer.

```python
def run_tests(candidate):
    """Reward = fraction of the test suite that passes. This IS the reward model."""
    cases = [((3, 1, 2), 2), ((5,), 5), ((1, 2, 3, 4), 2.5),
             ((7, 7, 7), 7), ((-1, 0, 1), 0)]
    passed = 0
    for args, expected in cases:
        try:
            result = candidate(list(args))
            passed += abs(result - expected) < 1e-9
        except Exception:              # a crash is simply a failed test
            pass
    return passed / len(cases)

def median_a(xs):                      # forgets to sort
    return xs[len(xs) // 2]

def median_b(xs):                      # sorts, but mishandles even lengths
    s = sorted(xs)
    return s[len(s) // 2]

def median_c(xs):                      # correct
    s = sorted(xs)
    mid = len(s) // 2
    return s[mid] if len(s) % 2 else (s[mid - 1] + s[mid]) / 2

for name, fn in [("median_a", median_a), ("median_b", median_b),
                 ("median_c", median_c)]:
    print(f"{name}: reward = {run_tests(fn):.2f}")
```

Three candidate solutions, three different rewards, no annotators and no
training. The signal is dense enough to rank near-misses (`median_b` gets 0.8,
not 0) and it cannot be flattered. The catch is coverage: a model optimised
against your tests will satisfy exactly your tests, so a weak suite produces a
weak model — `median_a` would score 1.0 if every case were already sorted with
an odd length. Reward hacking has not disappeared; it has turned into the very
old problem of writing tests that pin down the behaviour you meant.

## RLAIF and Constitutional AI

Human comparisons are the bottleneck: slow, expensive, and inconsistent.
**RLAIF** — reinforcement learning from AI feedback — replaces the annotator
with a model asked to make the same comparison against written criteria.
Anthropic's **Constitutional AI** work is the best-known instance: a written set
of principles (the "constitution") drives a *critique-and-revise* loop that
produces improved responses without human labels for the harm dimension, and the
resulting comparisons then train a preference model.

The loop is small enough to write out. Ours uses a deterministic rule-based
stand-in for the model, as everywhere in Part V — a real system would send each
prompt to an actual API.

```python
CONSTITUTION = [
    ("blames the user", "never blame the user for a service failure",
     lambda t: "your fault" in t or "you should have" in t),
    ("no apology", "acknowledge the impact before explaining",
     lambda t: "sorry" not in t.lower()),
    ("no next step", "always say what happens next",
     lambda t: "next" not in t.lower()),
]

def fake_llm_critique(text):
    """Stand-in for an LLM asked: 'which principles does this response break?'"""
    return [(name, rule) for name, rule, breaks in CONSTITUTION if breaks(text)]

def fake_llm_revise(text, violation):
    """Stand-in for an LLM asked: 'rewrite the response to fix this.'"""
    edits = {
        "blames the user": lambda t: (t.replace("Your fault", "Our error")
                                       .replace("your fault", "our error")
                                       .replace("You should have", "We should have")
                                       .replace("you should have", "we should have")),
        "no apology": lambda t: "Sorry for the disruption. " + t,
        "no next step": lambda t: t + " Next, we are adding a monitor to catch this.",
    }
    return edits[violation](text)

draft = "The outage was your fault for retrying so fast."
print(f"draft: {draft}")
for round_i in range(1, 5):
    problems = fake_llm_critique(draft)
    if not problems:
        print(f"round {round_i}: no violations — done")
        break
    name, rule = problems[0]
    print(f"round {round_i}: violates {name!r} ({rule})")
    draft = fake_llm_revise(draft, name)
    print(f"          -> {draft}")
print(f"\nfinal: {draft}")
print(f"violations remaining: {len(fake_llm_critique(draft))}")
```

Three rounds, three fixes, and the pair `(draft, final)` is now a training
example that no human wrote. Two honest caveats. The model doing the critiquing
must actually be able to tell — asking a model to judge a capability it does not
have produces confident noise. And the critic's blind spots become the policy's
blind spots systematically rather than randomly, which is a worse failure mode
than human inconsistency: humans at least disagree in different directions.

## Credit assignment over a trajectory

The last open problem. An agent from [Chapter 30](../ch30-agents/index.md) takes
twelve steps and succeeds. Which steps deserve the credit? The reward arrived
once, at the end, and the policy gradient needs a number per step.

```python
import numpy as np

STEPS = ["read the ticket", "search the wiki", "FOUND the error code",
         "open the dashboard", "scroll", "scroll", "filter by service",
         "SPOTTED the bad deploy", "open the runbook", "check permissions",
         "ROLLED BACK the deploy", "confirm recovery"]
DECISIVE = {2, 7, 10}                   # the three steps that actually mattered
T = len(STEPS)
final_reward = 1.0

uniform = np.full(T, final_reward / T)

gamma = 0.85
discounted = gamma ** np.arange(T - 1, -1, -1)
discounted = discounted / discounted.sum() * final_reward

step_level = np.array([1.0 if i in DECISIVE else 0.0 for i in range(T)])
step_level = step_level / step_level.sum() * final_reward

print(f"{'#':>3} {'step':<24}{'uniform':>9}{'discounted':>12}{'step-level':>12}")
for i, name in enumerate(STEPS):
    mark = "*" if i in DECISIVE else " "
    print(f"{i:>3}{mark}{name:<24}{uniform[i]:>9.3f}{discounted[i]:>12.3f}"
          f"{step_level[i]:>12.3f}")

for label, credit in [("uniform", uniform), ("discounted", discounted),
                      ("step-level", step_level)]:
    on_target = sum(credit[i] for i in DECISIVE)
    print(f"{label:>12}: {on_target:.1%} of the credit landed on the three "
          f"steps that mattered")
```

**Uniform** attribution — what plain REINFORCE with a single end-of-episode
reward does — sends 25% of the credit to the right places and 75% to `scroll`,
`scroll`, and `check permissions`. Those steps are now more likely next time.
**Discounting** barely helps — 28.0% against uniform's 25.0% — and it helps for
the wrong reason: step 10 happens to sit near the end, so it collects 14.9%,
while step 2 (the one that found the error code and made everything after it
possible) collects 4.1%, *less* than the uniform scheme gave it. Meanwhile
`confirm recovery`, which did nothing but observe, takes the single largest
share at 17.5%. Discounting encodes "later is more responsible", which is a
guess about causality, not a measurement of it.

**Step-level** attribution puts 100% where it belongs, and the catch is in the
name of the variable: `DECISIVE` was hand-written. Producing that set
automatically for a real trajectory is the open research problem. Current
approaches — Monte-Carlo rollouts from each intermediate state to estimate how
much that state was worth, learned PRMs, or asking a strong model to grade each
step — are all expensive, noisy, or both. This is one of the genuine frontiers
of agent training, and anyone who tells you it is solved is selling something.

!!! warning "Common mistakes"
    - **Reporting raw annotator agreement.** Two annotators who both always
      pick "A" agree 90% of the time and have learned nothing. Report kappa.
    - **Treating held-out reward-model accuracy as validation of the reward.**
      Our model scored 73.3% held out and had a large spurious length weight,
      because the held-out set carried the identical bias. Only an
      independently-collected evaluation catches that.
    - **Watching the reward curve to decide when to stop.** It rises smoothly
      straight through the point where true quality peaked and began falling.
      Stop on an eval the optimiser cannot see.
    - **Using outcome reward on multi-step reasoning and being surprised by
      confident wrong steps.** A right answer reached by two cancelling errors
      gets the same reward as a sound derivation, and you just trained on it.
    - **Assuming a rule-based verifier cannot be hacked.** It cannot be
      flattered, but it *can* be satisfied narrowly. A weak test suite is a
      weak specification, and the model will find the difference.
    - **Believing that AI feedback removes bias.** It replaces many humans
      disagreeing randomly with one model being wrong consistently, which is
      harder to detect.

## Check your understanding

1. Why is pairwise comparison preferred to a 1–10 rating, and what does it cost
   you?

    ??? success "Answer"

        Absolute scores are uncalibrated: they depend on the rater's mood,
        scale usage and recent anchors, so the same response gets different
        numbers from different people and from the same person on different
        days. A comparison has no scale to calibrate, so agreement is higher
        and annotation is faster. The cost is information: a comparison is at
        most one bit and says nothing about *how much* better the winner was,
        so a landslide and a coin-flip produce identical training data.

2. Your reward model has 78% held-out accuracy and your policy's reward is
   climbing steadily. Name two things that could still be badly wrong.

    ??? success "Answer"

        First, the reward model may faithfully reproduce a bias in the
        annotation process — our model reached 73.3% held out while carrying a
        large spurious weight on length, and the held-out split could not
        reveal it because it shared the bias. Second, a rising reward curve is
        consistent with reward hacking: in the plotted run the proxy rose
        monotonically while true quality peaked at step 13 and then fell below
        its starting value.

3. A trace computes $14 \times 3 = 40$, then $40 + 8 = 48$, then
   $48 - 3 = 45$, and 45 is the correct final answer. What does an ORM say?
   What does a PRM say? Which would you rather train on?

    ??? success "Answer"

        The ORM gives 1.0 — the answer is right, so as far as outcome
        supervision is concerned this trace is as good as a flawless one. The
        PRM gives 0.67 and flags step 0, where $14 \times 3$ was claimed to be
        40. Train on the ORM signal and you reinforce the wrong multiplication
        along with everything else; the PRM lets you reinforce only the steps
        that were actually sound.

4. You must ship in a week and can build exactly one reward source: human
   pairwise labels, an LLM judge, or a test suite. The task is "generate a
   Python function from a docstring". Which, and why?

    ??? success "Answer"

        The test suite. The task has a checkable answer, so the reward is
        deterministic, free to evaluate, available in unlimited quantity, and
        immune to the flattery and length biases that afflict both humans and
        LLM judges. Spend the week writing tests that pin down edge cases —
        because a weak suite is now a weak specification, and that is the only
        place this reward can fail.
