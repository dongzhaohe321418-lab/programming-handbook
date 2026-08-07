# 33.3 LLM-as-a-judge

The harness in [33.2](02-eval-harness.md) can score anything with a checkable
answer: a string to match, a schema to satisfy, a test suite to pass. Most of
what a language model produces is not like that. "Summarise this ticket",
"explain this error to a non-engineer", "rewrite this politely" — there is no
reference string, there are many good answers, and a human reading a thousand
outputs costs more than the model that produced them. The obvious move is to ask
a model to grade. It works, it is now standard practice, and it will quietly
hand you wrong numbers unless you treat the judge as a component to be measured
rather than an oracle to be trusted.

This section makes the biases concrete by implementing a judge whose biases you
can read in the source, measuring each one, and fixing the ones that are
fixable.

## Write the judge prompt like a specification

A judge prompt is a spec. The most common failure is not that the model cannot
judge — it is that nobody told it what "good" means. Here is the prompt people
write first:

```text
You are an impartial judge. Rate the following response from 1 to 10
for quality.

Question: {question}
Response: {response}

Score:
```

Every problem with LLM judging is visible in those four lines. "Quality" is
undefined, so the model supplies its own definition and it will not be yours.
The 1–10 scale has no anchors, so the scores pile up on 7 and 8 and stop
discriminating. There is nothing to reason about before committing, so the score
is a first-token guess. The output format is unconstrained, so half the replies
begin "Sure! Here's my assessment:" and your parser drops them. And the criteria
are fused into a single number, so a factually wrong but beautifully written
answer and a correct but terse one both land on 6.

The repaired version:

```text
You are grading a customer-support reply against a rubric. Judge ONLY the
criterion named below. Ignore length, formatting, and writing style.

CRITERION: factual grounding
  3 = every factual claim is supported by the provided ticket context
  2 = all claims supported except one minor detail
  1 = contains a claim that the context does not support
  0 = contains a claim the context contradicts

TICKET CONTEXT:
{context}

CUSTOMER QUESTION:
{question}

REPLY TO GRADE:
{reply}

First write one sentence quoting the specific claim that determined your
score. Then output the score.

Respond with JSON only: {"evidence": "<one sentence>", "score": <0-3>}
```

Six changes, each doing a specific job:

| Change | Why it works |
| --- | --- |
| One named criterion | Fused criteria produce an average of incomparable things; grade factuality and tone in separate passes |
| Anchored integer levels | "3 = every claim supported" is checkable; "8/10" is a vibe |
| A short 0–3 scale | Judges do not use ten levels; they use three or four, badly disguised |
| Explicit exclusions | Naming the biases ("ignore length, formatting, style") measurably reduces them, though it never removes them |
| Evidence before the score | Forces the decision to be conditioned on a quoted fact rather than emitted as a first token |
| Constrained JSON output | Makes the result parseable — the same argument as [28.2](../ch28-tools-mcp/02-structured-output.md), and worth a schema-constrained decode if you have one |

Keep the justification **short**. A judge asked for a paragraph of reasoning
writes a persuasive essay and then agrees with itself; one sentence quoting the
deciding fact is enough to change the decision without inventing a narrative.

## Pairwise beats absolute, for the same reason it did in Chapter 31

[31.4](../ch31-rl/04-reward-models.md) opened with the observation that humans
cannot produce calibrated absolute scores. Neither can judges, and for a related
reason: an absolute score requires an internal, stable notion of what a 7 is,
whereas a comparison only requires noticing a difference. In practice, asking
"is A better than B?" gives higher agreement with humans, is more robust across
prompt rewordings, and — decisively — does not drift when you re-run it next
month against a new candidate.

| | Absolute scoring | Pairwise comparison |
| --- | --- | --- |
| What it asks | "how good is this, 0–3" | "which of these two is better" |
| Calibration | must be maintained by the judge | none needed |
| Stability across runs | drifts with prompt and model version | drifts less; the baseline is re-graded each time |
| Cost | one call per item | one call per pair, and *two* if you swap orders |
| Gives you | a number you can average and trend | a win rate against a fixed baseline |
| Main failure | scores bunch at the top of the scale | position bias, and no sense of *how much* better |

Use pairwise against a **frozen baseline** — the previous release, or a strong
reference answer — and report a win rate. Use absolute scoring when you need to
trend a single system over time and cannot keep re-running a baseline, and then
accept that the absolute level means less than its changes.

## The bias catalogue, measured

Now the substance. Below is a judge whose four biases are written as
coefficients. Two hundred pairs, from two systems of **equal true quality** —
ours is merely longer and prettier. Everything the table reports is a bias,
because the true win rate is 52.5% and nothing about the systems changes between
rows.

```python
"""Four judge biases, implemented on purpose so they can be measured."""
import numpy as np

rng = np.random.default_rng(0)
N = 200

# Two systems of EQUAL true quality. Ours is simply more verbose and prettier.
q_ours = rng.normal(0.0, 1.0, N)
q_theirs = rng.normal(0.0, 1.0, N)
len_ours = rng.integers(120, 400, N)          # words
len_theirs = rng.integers(80, 260, N)
TRUE_WIN = float((q_ours > q_theirs).mean())


class BiasedJudge:
    """A FakeLLM judge. A real one has these tendencies too; the difference
    is that here you can read the coefficients."""

    POSITION = 0.45      # bonus for whichever answer is shown first
    VERBOSITY = 0.005    # bonus per word
    SELF = 0.55          # bonus for text it believes it wrote
    STYLE = 0.60         # bonus for bullet-point formatting

    def utility(self, ans, first):
        return (ans["quality"]
                + self.VERBOSITY * ans["words"]
                + self.SELF * ans["is_self"]
                + self.STYLE * ans["bullets"]
                + self.POSITION * first)

    def compare(self, x, y):
        """Returns 'first' or 'second' — the judge only sees an order."""
        return "first" if self.utility(x, 1) > self.utility(y, 0) else "second"


JUDGE = BiasedJudge()


def make(i, mine, *, is_self=False, bullets=False):
    q = q_ours[i] if mine else q_theirs[i]
    w = len_ours[i] if mine else len_theirs[i]
    return {"quality": q, "words": int(w), "is_self": is_self,
            "bullets": bullets}


def win_rate(is_self=False, bullets=False, order="both", equal_length=False):
    """Fraction of the N pairs the judge awards to OUR system."""
    wins = np.zeros(N)
    for i in range(N):
        ours = make(i, True, is_self=is_self, bullets=bullets)
        theirs = make(i, False)
        if equal_length:                       # hand both the same word count
            ours["words"] = theirs["words"] = 200
        if order == "ours-first":
            wins[i] = JUDGE.compare(ours, theirs) == "first"
        elif order == "ours-second":
            wins[i] = JUDGE.compare(theirs, ours) == "second"
        else:                                  # average of both orders
            wins[i] = 0.5 * ((JUDGE.compare(ours, theirs) == "first")
                             + (JUDGE.compare(theirs, ours) == "second"))
    return wins


print(f"true win rate for our system: {TRUE_WIN:.1%}   ({N} pairs)\n")
print(f"{'bias':<14}{'protocol':<34}{'win rate':>9}")
rows = [
    ("position", "ours shown first", win_rate(order="ours-first")),
    ("", "ours shown second", win_rate(order="ours-second")),
    ("", "averaged over both orders", win_rate(order="both")),
    ("verbosity", "as generated (ours is longer)", win_rate()),
    ("", "length-matched", win_rate(equal_length=True)),
    ("self-pref", "ours labelled as the judge's own", win_rate(is_self=True)),
    ("", "ours labelled as a competitor", win_rate(is_self=False)),
    ("formatting", "ours reformatted as bullets", win_rate(bullets=True)),
    ("", "both in plain prose", win_rate(bullets=False)),
]
for bias, protocol, w in rows:
    print(f"{bias:<14}{protocol:<34}{w.mean():>9.1%}")

flips = win_rate(order="both")
print(f"\norder-flip rate: {(flips == 0.5).mean():.1%} of pairs get a "
      f"different winner when swapped")

# --- the fix that does not need a matched subset: regress out length ----
delta = (len_ours - len_theirs).astype(float)
design = np.column_stack([np.ones(N), delta])
intercept, slope = np.linalg.lstsq(design, flips, rcond=None)[0]
print(f"length-controlled win rate (fit at equal length): {intercept:.1%}")
print(f"  each extra 100 words is worth {slope * 100:+.1%} of win rate")
```

Read the table one bias at a time. Everything except the first two rows already
averages both orders, so each pair of rows isolates a single effect.

**Position bias: 75.5% versus 50.5%.** The identical comparison, decided by
which answer was pasted in first, moves the reported win rate by 25 points — and
**25.0% of individual pairs get a different winner when swapped**. This is the
most dangerous bias because it is invisible: nothing in the output looks wrong,
and if you always build the prompt the same way (your system first, baseline
second, because that is how the loop was written) it is a constant thumb on the
scale. The fix is complete and costs one extra call: **judge every pair in both
orders and average**, which lands at 63.0%. Pairs that disagree between orders
are genuine ties, and treating them as half a win is the right accounting.

**Verbosity bias: 63.0% versus 53.5%.** Once position is handled, our system
still "wins" 63% of comparisons it should win 52.5% of. The whole remaining gap
is length. Hand both answers the same word count and it collapses to 53.5% — a
point off the truth. When you cannot match lengths (usually), the regression fix
from [31.4](../ch31-rl/04-reward-models.md) applies unchanged: fit win rate
against the length difference and read off the value at zero. That gives
**55.5%**, and prices the bias explicitly: **every extra 100 words buys +8.1
points of win rate**. If your "improvement" was a prompt change that made
answers longer, that number is your improvement.

**Self-preference: 76.0% versus 63.0%.** Telling the judge that an answer came
from its own model family is worth 13 points. This is why using the model you
are shipping as the judge of your own release is not an evaluation, and why the
comparison rows above never change anything except a label. Judge with a
different model family than the one you are grading, or at minimum verify the
gap by running the comparison with the labels removed and with them swapped.

**Formatting bias: 76.5% versus 63.0%.** Reformatting the *same content* into
bullet points is worth 13.5 points. Headings, bold text, and numbered structure
all read as effort. If your product needs prose, a judge that rewards markdown
is measuring the wrong thing entirely.

!!! warning "You cannot prompt these away"
    "Ignore length and formatting" in the judge prompt reduces these effects and
    does not remove them — the same structural point [30.4](../ch30-agents/04-frameworks.md)
    made about prompt-level defences against injection. The reliable
    countermeasures are *protocol* changes: swap orders and average, control for
    length, hide authorship, and normalise formatting before judging.

## Validation: agreement with humans is the only ground truth

A judge is a measuring instrument, and an uncalibrated instrument is decoration.
Before you let one gate a release, label 100–200 items by hand and measure how
often the judge agrees — and, as [31.4](../ch31-rl/04-reward-models.md) insisted
for annotators, correct that agreement for chance.

```python
"""Validating a judge: agreement with humans, corrected for chance."""

LABELS = ("A", "B", "T")          # A wins, B wins, tie

HUMAN = "ABTAABBATBAABABTABBAATABABTAAB"
JUDGE_1 = "AAAAABAAAAAABABAABBAAAAAABAAAB"    # dislikes ties, prefers A
JUDGE_2 = "ABTAABBATBAABBBTABBAATABAATAAB"    # occasionally slips


def agreement(x, y):
    return sum(a == b for a, b in zip(x, y)) / len(x)


def cohens_kappa(x, y):
    """Agreement above what these two label habits would produce by chance."""
    n = len(x)
    p_o = agreement(x, y)
    p_e = sum((x.count(l) / n) * (y.count(l) / n) for l in LABELS)
    return p_o, p_e, (p_o - p_e) / (1 - p_e)


print(f"{len(HUMAN)} items labelled A / B / tie\n")
print(f"{'labeller':<10}" + "".join(f"{l:>6}" for l in LABELS))
for name, seq in (("human", HUMAN), ("judge 1", JUDGE_1), ("judge 2", JUDGE_2)):
    print(f"{name:<10}" + "".join(f"{seq.count(l):>6}" for l in LABELS))

print(f"\n{'judge':<10}{'raw agreement':>15}{'by chance':>11}{'kappa':>8}")
for name, seq in (("judge 1", JUDGE_1), ("judge 2", JUDGE_2)):
    p_o, p_e, k = cohens_kappa(HUMAN, seq)
    print(f"{name:<10}{p_o:>15.1%}{p_e:>11.1%}{k:>8.2f}")
```

Judge 1 agrees with the human **70.0%** of the time, which sounds usable, and
has a **kappa of 0.46**, which is not. The label counts explain why: the human
used A 14 times, B 11 and tie 5; judge 1 said A 23 times and never once called a
tie. It agrees mostly by guessing the majority class. Judge 2 reproduces the
human's label distribution and reaches 93.3% agreement with **kappa 0.89**.

The rule, and it is not negotiable: **validate the judge before you trust it.**
Using the bands from 31.4, kappa above roughly 0.6 is workable for preference
work and above 0.8 is good; below 0.4 the problem is your rubric, not the model.
Re-validate whenever you change the judge model, the judge prompt, or the task
distribution — all three are silent changes to your measuring instrument.

!!! note "Ties are a real category, and judges hate them"
    Judge 1's refusal to use "tie" is the single most common calibration
    failure. Forced to choose, a judge invents a distinction, and your win rate
    picks up noise that looks like signal. Allow an explicit tie, tell the
    rubric when to use it ("both satisfy every criterion" or "the difference is
    stylistic"), and *report the tie rate* — a suspiciously low one means the
    judge is fabricating preferences. Order-swap disagreements, as above, are
    also ties, and counting them as such costs nothing.

## Panels, and when they stop helping

If one judge is noisy, use three and take the majority. This works — up to a
point that is worth knowing precisely.

```python
"""A panel of judges: when majority voting helps, and when it does nothing."""
import numpy as np

N = 4000
JUDGE_ACCURACY = 0.70
rng = np.random.default_rng(0)
truth = rng.integers(0, 2, N)


def panel(k, shared_error, seed):
    """k judges, each 70% accurate. `shared_error` of the error rate comes
    from items every judge finds hard; the rest is independent."""
    g = np.random.default_rng(seed)
    hard = g.random(N) < shared_error                    # everyone fails these
    independent_rate = (1 - JUDGE_ACCURACY - shared_error) / (1 - shared_error)
    votes = np.empty((k, N), dtype=int)
    for j in range(k):
        wrong = hard | (g.random(N) < independent_rate)
        votes[j] = np.where(wrong, 1 - truth, truth)
    single = float((votes[0] == truth).mean())
    majority = np.where(votes.sum(axis=0) * 2 > k, 1, 0)
    return single, float((majority == truth).mean())


print(f"{N} items, each judge {JUDGE_ACCURACY:.0%} accurate on its own\n")
print(f"{'shared error':>13}{'judges':>8}{'one judge':>12}{'majority':>10}"
      f"{'gain':>8}{'cost':>7}")
for shared in (0.00, 0.15, 0.30):
    for k in (3, 5):
        one, maj = panel(k, shared, seed=k * 10 + int(shared * 100))
        label = f"{shared:.0%}" if k == 3 else ""
        print(f"{label:>13}{k:>8}{one:>12.1%}{maj:>10.1%}"
              f"{maj - one:>+8.1%}{'x' + str(k):>7}")
```

With **independent** errors, three judges take 71.2% to 79.6% and five take
70.6% to 84.2%. That is the textbook result, and it is why panels are popular.
Now read the bottom block: when *all* of the error is shared — the judges fail
on the same hard items, which is exactly what happens when they are three
prompts against the same model, or three models trained on overlapping data —
the majority is **69.0%**, identical to a single judge, at three times the cost.

Voting removes independent noise. It cannot remove a bias the panel shares, and
the biases in the previous section are shared by essentially every judge you can
buy. **A panel is a variance reduction technique, not a bias correction.** Buy
diversity deliberately — different model families, different rubric phrasings,
different presentation orders — or do not buy the panel.

## Reference-based versus reference-free

A **reference-free** judge sees the question and the answer and decides. A
**reference-based** judge also sees a known-good answer — a human-written gold
response, a documentation quote, the retrieved context the answer had to stay
faithful to.

Reference-based judging is dramatically more reliable wherever you can afford
it, because it converts an open-ended aesthetic question into a comparison
against something fixed. "Is this a good summary?" is hard; "does this summary
contain each of these four facts, and does it add any not in the source?" is
nearly mechanical, and a weaker, cheaper judge can do it well. For RAG systems
([Chapter 29](../ch29-memory-rag/index.md)) the retrieved context is a reference
you already have, which makes faithfulness — every claim traceable to the
context — the single highest-value judge to build first.

Use reference-free judging when no reference can exist (open-ended creative
work, tone, helpfulness) and treat its numbers with correspondingly more
suspicion.

## Controlling the cost

Judging is inference, and inference is a bill. A frontier judge on every output
of every release is a line item somebody will eventually question.

```python
"""Judging costs money. Sampling costs precision. Price both."""
from math import sqrt

POPULATION = 5000          # outputs produced per release
STRONG = 0.010             # dollars per judged item
CHEAP = 0.001
P = 0.80                   # roughly the pass rate we expect


def half_width(n, p=P, N=POPULATION):
    """95% half-width for a proportion, with the finite-population fix."""
    se = sqrt(p * (1 - p) / n) * sqrt((N - n) / (N - 1)) if n < N else 0.0
    return 1.96 * se


print(f"{POPULATION} outputs, strong judge at ${STRONG:.3f}/item\n")
print(f"{'sampled':>8}{'cost':>9}{'95% half-width':>17}")
for n in (50, 200, 500, 1000, POPULATION):
    print(f"{n:>8}{'$' + format(n * STRONG, '.2f'):>9}"
          f"{half_width(n):>16.1%}")

# --- two-tier: cheap judge everywhere, strong judge where it matters -----
ESCALATE = 0.15            # fraction the cheap judge is unsure about
tiered = POPULATION * CHEAP + POPULATION * ESCALATE * STRONG
print(f"\ncheap judge on all {POPULATION}, strong judge on the "
      f"{ESCALATE:.0%} it flags:")
print(f"  ${tiered:.2f} per release versus ${POPULATION * STRONG:.2f} "
      f"({POPULATION * STRONG / tiered:.1f}x cheaper), full coverage")
print(f"  but it is only valid if the cheap judge's agreement with the "
      f"strong one\n  has been measured on a sample — that sample is not "
      f"optional.")
```

Sampling 200 of 5000 outputs costs **$2.00** instead of $50.00 and gives you an
answer good to **±5.4 points**. That is plenty for "did the release get
dramatically worse" and useless for "did we gain 2 points", and the table lets
you pick deliberately instead of by accident. Note the shape you have now seen
three times: 500 items halve the interval of 200, and 1000 barely halve it
again. Precision is bought at $1/\sqrt{n}$, forever.

The two-tier arrangement — a cheap judge on everything, escalating the cases it
is unsure about to the strong judge — costs $12.50 against $50.00 for full
coverage, and it is the arrangement most production systems converge on. It has
one prerequisite, and skipping it is the standard way this goes wrong: you must
measure the cheap judge's agreement with the strong one *on a sample*, exactly
as you measured the strong judge against humans. A cheap judge trusted on faith
is a cost saving on a number that no longer means anything.

## The shipping checklist

Before an LLM judge is allowed to gate anything:

1. **One criterion per judge call**, with anchored integer levels and an
   explicit definition of a tie.
2. **A short justification before the score**, and constrained output so it
   parses.
3. **Both orders, averaged**, for every pairwise comparison. Non-negotiable —
   it cost 25 points above.
4. **Length reported alongside every win rate**, and a length-controlled number
   whenever the systems differ in verbosity.
5. **A judge from a different model family** than the system under test, or an
   explicit measurement of the self-preference gap.
6. **Human agreement measured on 100–200 items**, reported as kappa, above 0.6
   before the judge is used for decisions.
7. **Confidence intervals on every judged win rate** — a judged number is still
   a sample ([33.2](02-eval-harness.md)).
8. **The judge prompt version-controlled and pinned**, with a re-validation run
   whenever it, or the judge model, changes.
9. **A small human spot-check every release**, forever. Twenty items read by a
   person catches drift that no metric will.
10. **Never optimise directly against the judge.** Tuning prompts until the
    judge is happy is [31.4's reward hacking](../ch31-rl/04-reward-models.md)
    with a language model as the reward model — and it is the reason your final
    decision should always rest partly on something the optimiser cannot see.

!!! warning "Common mistakes"

    - **Judging in one order.** 25.0% of our pairs changed winner when swapped,
      and the reported win rate moved 25 points. Always swap and average.
    - **Comparing systems of different verbosity.** Length was worth +8.1 points
      of win rate per 100 words. Report length, or control for it.
    - **Using your own model as its own judge.** The self-preference label alone
      was worth 13 points here.
    - **Trusting raw agreement.** Judge 1 agreed with humans 70% of the time
      with a kappa of 0.46, achieved by almost always saying "A".
    - **Assuming a panel fixes bias.** With fully shared errors, three judges
      scored exactly what one judge scored, at three times the price.
    - **Asking for a 1–10 score.** You will get 7s and 8s. Use three or four
      anchored levels.
    - **Letting the judge write a long rationale.** It talks itself into a
      position. One sentence, quoting the deciding fact.

## Check your understanding

1. Your new prompt wins 68% of judged comparisons against the previous release.
   What three things do you check before believing it?

    ??? success "Answer"

        Order: was every pair judged in both orders and averaged? Swapping alone
        moved our win rate from 75.5% to 50.5%. Length: are the new answers
        longer? Each 100 extra words bought +8.1 points, and a length-matched
        or length-controlled figure is the one to quote. Authorship and
        formatting: does the judge know which system is which, and did the new
        prompt add markdown structure? Those were worth 13 and 13.5 points.
        After all three, put a confidence interval on the remainder.

2. A judge agrees with your human labels 82% of the time. Is that good?

    ??? success "Answer"

        Unknowable from that number alone. Compute kappa. If the task is
        heavily skewed — most items pass — a judge that always says "pass"
        scores high raw agreement while carrying no information; ours managed
        70% agreement with kappa 0.46 by mostly saying "A". Also compare the
        label distributions: a judge that never uses the tie label is
        fabricating distinctions, whatever its agreement rate.

3. Why does a panel of three judges built from three prompts against the same
   model often fail to beat one judge?

    ??? success "Answer"

        Because majority voting removes *independent* noise and their errors are
        not independent. In the simulation, three judges with fully shared error
        scored 69.0% — exactly what one scored — at three times the cost, while
        three judges with independent errors went from 71.2% to 79.6%. Three
        prompts against one model share its training data, its biases, and the
        items it finds hard. If you want a panel, buy genuine diversity:
        different model families, different rubric phrasings, different
        presentation orders.

4. When is a reference-based judge worth the extra work of producing references?

    ??? success "Answer"

        Whenever a reference can exist, which is more often than people assume.
        It converts an aesthetic judgement into a checkable comparison — "does
        this contain these four facts and add nothing else" instead of "is this
        good" — which raises agreement, lowers variance, and lets a cheaper
        judge do the job. RAG is the clearest case: the retrieved context is
        already a reference, so a faithfulness judge is nearly free and catches
        the failure mode users care most about. Reserve reference-free judging
        for genuinely open-ended qualities like tone and helpfulness, and treat
        its numbers with more suspicion.
