# 33.1 Benchmarks and what they measure

Everything else in this handbook has a referee. A syntax error stops the
interpreter, a failing `assert` turns red, a segfault crashes the process — the
machine tells you that you are wrong, immediately and without being asked. A
language model has no such referee. It answers every question fluently,
including the ones it is wrong about, and the only way to find out whether your
system got better is to *measure* it. That measurement is the hardest
engineering problem in Part V, and this section is about the part of it other
people have already built for you: public benchmarks, what each one really
tests, and the ways a number produced by one can be flatly untrue.

!!! abstract "In plain words"

    - **What it is.** Judging whether a model is any good, when nothing
      automatically tells you an answer is wrong.
    - **Picture it.** Grading a stack of essays instead of a maths quiz. The quiz
      has an answer key; the essays force you first to decide what "good" even
      means, then measure every paper against it — and reasonable graders will
      disagree.
    - **Why it matters.** Every other chapter had a referee: a crash, a failing
      test, a red error. A language model answers everything fluently, including
      what it is wrong about, so measuring it well is the hardest engineering
      problem in Part V.

## The shape of the problem

A benchmark is four things bolted together:

1. a **dataset** of inputs;
2. a **reference** for each input;
3. a **metric** that compares an output to the reference;
4. a **protocol** — the prompt format, the decoding settings, the number of
   examples shown.

Change any one of the four and the number changes. Most disputes about "model A
beats model B" are really disputes about the third and fourth, which is why this
section spends more time on metrics and protocols than on datasets.

!!! abstract "In plain words"

    - **What it is.** A benchmark is a standardised exam for models — a fixed set
      of questions plus a way to mark the answers — so two models can be compared
      on the same terms.
    - **Picture it.** Standardised school tests, each measuring something
      different: MMLU is a broad written exam, HumanEval a coding test graded by
      running the code, SWE-bench a real-repair job on an actual codebase, GAIA a
      practical assistant task that needs tools.
    - **Why it matters.** Each exam tests one slice of ability and is blind to the
      rest, so a single leaderboard number never means "better" outright — it
      means "better at this particular test, marked this particular way."

Here is the landscape, described by what each benchmark actually asks a model
to do. Treat the *descriptions* as durable and any leaderboard position you see
elsewhere as a snapshot with a short shelf life.

| Benchmark | Task format | Metric | Good for | What it misses |
| --- | --- | --- | --- | --- |
| **MMLU** | ~16k four-way multiple-choice questions across 57 subjects, exam-style | accuracy | cheap, broad, comparable coverage of academic knowledge | picking a letter is not generating an answer; heavily discussed online, so leakage is likely; strong models are bunched near the top |
| **HumanEval** | 164 hand-written Python function stubs with a docstring, graded by hidden unit tests | pass@k | does the model write a short, correct, self-contained function | function-level only — no repo, no imports you did not expect, no multi-file change; 164 items is small enough that a few flips move the score |
| **MBPP** | ~1,000 short crowd-sourced Python problems, each with three `assert` tests | pass@k | breadth of everyday programming | same function-level ceiling; some prompts are ambiguous enough that a correct program fails the asserts |
| **SWE-bench** | a real GitHub issue plus the repository at that commit; the model must produce a patch, graded by running the project's own test suite | % of issues resolved | execution-verified, agentic, genuinely multi-file work | expensive to run; Python open-source repos only; a patch can pass a weak test suite without fixing the issue; scores depend on the scaffold as much as the model |
| **GAIA** | 466 assistant-style questions in three difficulty levels, each with one unambiguous short answer, requiring multi-step work and tools | exact match | end-to-end assistant ability: planning, tool use, following a chain to a checkable answer | measures your *tool stack* as much as your model; small, so per-level error bars are wide |
| **Long-context** probes | retrieve or reason over documents from thousands to a million tokens; "needle in a haystack" style retrieval and long-document QA | accuracy by position and length | whether a context window is *usable* or merely advertised | finding a planted sentence is far easier than reasoning over the whole document |
| **Tool-use / function-calling** suites | given tool schemas, emit the right call with the right arguments | schema-valid call rate, argument accuracy, task success | the behaviour [Chapter 28](../ch28-tools-mcp/index.md) built | their tool inventory is not yours; a model tuned to their schemas may not transfer |
| **Safety / refusal** suites | harmful, borderline, and benign-but-scary prompts | refusal rate *and* over-refusal rate | both failure directions at once | narrow coverage; culturally specific; trivially gamed by refusing more |

Two structural distinctions cut across that table and matter more than the
names.

- **Execution-verified versus reference-compared.** SWE-bench, HumanEval and
  MBPP run code, so the grader is a program and cannot be sweet-talked. MMLU and
  GAIA compare strings, so the grader is only as good as its normalization rules.
- **Single-turn versus agentic.** An MMLU item is one forward pass. A SWE-bench
  instance is a whole episode with a budget, a scaffold, and dozens of tool
  calls — which means SWE-bench measures your agent, not just your model.

!!! abstract "In plain words"

    - **What it is.** The simplest possible grader — does the output string equal
      the reference string? — and the surprising number of hidden choices buried
      inside that word "equal".
    - **Picture it.** Marking `"3.14"` against `"3.140"`, or `"Paris."` against
      `"Paris"`. The same answer to a human; different bytes to a computer. Someone
      has to decide which differences to forgive.
    - **Why it matters.** Those forgiveness rules — lowercasing, trimming
      punctuation, dropping "the" — swing the very same model's score by tens of
      points, and they hand out undeserved credit as silently as deserved credit.

## Exact match is not one metric — it is a family

Start with the simplest metric imaginable: does the output string equal the
reference string? It sounds like it has no free parameters. It has at least
five, and they are worth a 75-point swing.

```python
"""Exact match is not one metric — it is a family, and the family disagrees."""
import re
import string

# Twelve (prediction, gold) pairs from a short-answer QA set. The MODEL is
# fixed. Only the scorer changes below.
PAIRS = [
    ("Paris", "Paris"),
    ("paris", "Paris"),
    ("Paris.", "Paris"),
    ("  Paris  ", "Paris"),
    ("The answer is Paris", "Paris"),
    ("the Eiffel Tower", "The Eiffel Tower"),
    ("an apple", "apple"),
    ("1969", "1969"),
    ("July 20, 1969", "July 20 1969"),
    ("Yes.", "Yes"),
    ("3.14", "314"),          # WRONG, but punctuation-stripping will accept it
    ("Lyon", "Paris"),        # simply wrong
]

ARTICLES = re.compile(r"\b(a|an|the)\b")
PREFIX = re.compile(r"^(the answer is|answer:)\s*", re.IGNORECASE)


def normalize(text, strip=False, lower=False, punct=False,
              articles=False, prefix=False):
    if strip:
        text = text.strip()
    if lower:
        text = text.lower()
    if prefix:
        text = PREFIX.sub("", text)
    if punct:
        text = text.translate(str.maketrans("", "", string.punctuation))
    if articles:
        text = ARTICLES.sub(" ", text)
    return " ".join(text.split()) if (strip or punct or articles) else text


LEVELS = [
    ("raw string equality", {}),
    ("+ strip whitespace", dict(strip=True)),
    ("+ lowercase", dict(strip=True, lower=True)),
    ("+ drop punctuation", dict(strip=True, lower=True, punct=True)),
    ("+ drop articles", dict(strip=True, lower=True, punct=True, articles=True)),
    ("+ strip 'the answer is'", dict(strip=True, lower=True, punct=True,
                                     articles=True, prefix=True)),
]

print(f"{'scorer':<26}{'score':>8}   items it newly accepts")
previous = None
for name, opts in LEVELS:
    hits = [normalize(p, **opts) == normalize(g, **opts) for p, g in PAIRS]
    new = [PAIRS[i][0] for i in range(len(PAIRS))
           if hits[i] and (previous is None or not previous[i])]
    print(f"{name:<26}{sum(hits) / len(hits):>7.1%}   {new}")
    previous = hits
```

The same model scores **16.7%** under raw equality and **91.7%** once you apply
the normalization chain that essentially every QA benchmark uses. Nothing about
the model changed. If a paper reports 91.7% and you reproduce 16.7%, the
disagreement is entirely in code that nobody wrote about.

Now read the `+ drop punctuation` row of the output more carefully. The model actually
answered ten of the twelve correctly, so its honest score is 83.3%. The
punctuation step accepted `"3.14"` against a gold of `"314"` — normalization
does not only recover deserved credit, it also hands out undeserved credit, and
it does so silently. **Log every prediction your normalizer flips**, and read a
sample of them. That five-minute habit catches this class of bug permanently.

!!! tip "The normalizer is part of the benchmark"
    When you publish a score, publish the normalizer with it. When you consume
    a score, find the normalizer before you believe it. This is exactly why the
    real harnesses in [33.2](02-eval-harness.md) ship the scoring code rather
    than describing it in a README.

!!! abstract "In plain words"

    - **What it is.** If the model gets $k$ tries at a problem, pass@k is how often
      at least one of those tries works.
    - **Picture it.** Basketball free throws. A 40%-per-shot player almost never
      sinks the first attempt, but given ten attempts will usually make at least
      one — so "one shot" and "best of ten" measure genuinely different things.
    - **Why it matters.** More tries can only raise the number, so pass@1 and
      pass@10 can rank two models in opposite orders. If your product samples once,
      a headline pass@10 is measuring a product you are not shipping.

## pass@k, and the estimator that makes it honest

Code benchmarks do not compare strings; they run the program. But a model
sampling at nonzero temperature is a *distribution* over programs, so "did it
solve the problem" is not a yes/no question. The standard answer is **pass@k**:
the probability that at least one of $k$ independently drawn samples passes the
tests.

The naive way to estimate that is to draw exactly $k$ samples and check. It
works, and it is extremely noisy. The estimator introduced with HumanEval draws
$n > k$ samples, counts how many pass, and computes the probability that a
random $k$-subset of those $n$ misses every correct one:

$$
\text{pass@}k \;=\; \mathbb{E}_{\text{tasks}}
\left[\, 1 - \frac{\dbinom{n - c}{k}}{\dbinom{n}{k}} \,\right]
$$

where $c$ is the number of the $n$ samples that passed. The fraction is exactly
"choose $k$ from the failures" over "choose $k$ from everything", which is the
chance of drawing an all-failing subset.

Computing a benchmark's pass@k is four steps:

1. **Sample $n$ completions per task**, with $n$ comfortably larger than $k$.
2. **Run the tests** on each, and count how many passed. That count is $c$.
3. **Apply the formula above** once per task, giving a per-task probability.
4. **Average across tasks.** That average is the reported pass@k.

```python
"""pass@k: the unbiased estimator, the tempting shortcut, and the truth."""
from math import comb
import numpy as np

# Eight tasks with different true per-sample success rates. In a real eval you
# never see these numbers; here we do, so the estimators can be checked.
P_TRUE = np.array([0.95, 0.70, 0.55, 0.40, 0.25, 0.10, 0.05, 0.00])
N = 20                                    # samples drawn per task


def pass_at_k(n, c, k):
    """Unbiased pass@k for ONE task: n samples drawn, c of them correct."""
    if n - c < k:                         # every k-subset contains a correct one
        return 1.0
    return 1.0 - comb(n - c, k) / comb(n, k)


def plug_in(n, c, k):
    """The tempting shortcut: treat c/n as p and assume independence."""
    return 1.0 - (1.0 - c / n) ** k


rng = np.random.default_rng(0)
counts = rng.binomial(N, P_TRUE)          # c for each task, one eval run

print(f"per-task, n = {N}")
print(f"{'p_true':>7}{'c':>4}{'pass@1':>9}{'pass@5':>9}{'pass@10':>9}")
for p, c in zip(P_TRUE, counts):
    print(f"{p:>7.2f}{c:>4}" + "".join(f"{pass_at_k(N, c, k):>9.3f}"
                                       for k in (1, 5, 10)))

print(f"\nbenchmark score = the mean of that column")
print(f"{'k':>3}{'unbiased':>11}{'plug-in':>10}{'truth':>9}")
for k in (1, 5, 10):
    unb = np.mean([pass_at_k(N, c, k) for c in counts])
    plg = np.mean([plug_in(N, c, k) for c in counts])
    tru = np.mean(1 - (1 - P_TRUE) ** k)
    print(f"{k:>3}{unb:>11.3f}{plg:>10.3f}{tru:>9.3f}")

# --- why n must exceed k -------------------------------------------------
truth5 = float(np.mean(1 - (1 - P_TRUE) ** 5))
print(f"\nre-running the whole eval 200 times, estimating pass@5 "
      f"(truth {truth5:.3f})")
print(f"{'n':>5}{'unbiased mean':>15}{'std':>7}{'plug-in mean':>14}{'std':>7}")
for n in (5, 10, 20, 100):
    r = np.random.default_rng(1)
    unb, plg = [], []
    for _ in range(200):
        cs = r.binomial(n, P_TRUE)
        unb.append(np.mean([pass_at_k(n, int(c), 5) for c in cs]))
        plg.append(np.mean([plug_in(n, int(c), 5) for c in cs]))
    print(f"{n:>5}{np.mean(unb):>15.3f}{np.std(unb):>7.3f}"
          f"{np.mean(plg):>14.3f}{np.std(plg):>7.3f}")
```

Three things to take from the output.

**The shortcut is biased, not just noisy.** At $n = 5$ the plug-in estimator
reports 0.599 against a truth of 0.662 — a six-point systematic
under-estimate that *does not shrink as you add tasks*. Only more samples per
task fix it: by $n = 100$ it has drifted up to 0.658. The unbiased estimator's
mean is 0.667, 0.661, 0.663, 0.661 at $n = 5, 10, 20, 100$ — right at every
sample size, which is what "unbiased" means.

**$n > k$ buys precision, not correctness.** The unbiased estimator's standard
deviation falls from 0.108 at $n = 5$ to 0.019 at $n = 100$. At $n = k = 5$ the
formula collapses to "did any of the five pass", so every task contributes a
single coin flip; the average is still right, but one run of your eval can land
five points from another for no reason at all. This is the single most common
way people fool themselves with pass@k.

**pass@1 and pass@10 rank models differently.** Look at the per-task table: the
task with $p = 0.10$ scores 0.200 at $k = 1$ and 0.957 at $k = 10$. A model that
is usually-nearly-right wins at high $k$; a model that is occasionally-perfect
wins at $k = 1$. If your product samples once, pass@10 is measuring a product
you are not shipping.

## Multiple choice: two completely different questions

"Which of A, B, C, D is correct?" can be scored two ways, and they are not
variants of one measurement — they ask different things. **Log-likelihood
scoring** appends each option to the prompt and compares the model's total
log-probability for the continuation; nothing is generated and no parsing is
needed. **Generation scoring** lets the model write an answer and then parses a
letter out of it, which is what a user would actually experience.

Six scorers appear below — three of each kind:

| Scorer | What it ranks options by | Known bias | Reach for it when |
| --- | --- | --- | --- |
| `acc` (summed log-prob) | total log-probability of the option text | prefers short options | you want the cheapest possible signal |
| `acc_norm` (per byte) | log-probability per byte | prefers long, fluent options | the options differ a lot in length |
| `pmi` (minus the prior) | how much the *question* raised the option | costs a second scoring pass per option | some options are simply common English |
| generate + strict parse | a bare letter, nothing else | scores a fully-correct chatty model near zero | you constrain the output format |
| generate + lenient parse | any letter appearing in the reply | can pick up an incidental letter | the model usually names a letter |
| generate + text fallback | letter first, then option text | most forgiving, so most likely to over-credit | the reply may answer in words only |

The log-probabilities below are scripted, standing in for what a real model
would return — the arithmetic on them is exactly what a real harness does. The
`cond` numbers are $\log P(\text{option} \mid \text{question})$ per token, and
`uncond` is $\log P(\text{option})$ with no question, which the PMI scorer uses
to cancel out options that are simply common English.

```python
"""One model, four questions, six scorers, four different scores."""
import re

QUESTIONS = [
    {"q": "Which gas do plants absorb during photosynthesis?", "gold": "B",
     "opts": {"A": "Oxygen", "B": "Carbon dioxide",
              "C": "Nitrogen", "D": "Hydrogen"},
     "cond": {"A": [-1.4], "B": [-1.2, -0.3], "C": [-3.0], "D": [-4.0]},
     "uncond": {"A": [-2.0], "B": [-2.4, -0.5], "C": [-2.6], "D": [-3.2]},
     "generated": "B"},
    {"q": "Which metal is the main component of steel?", "gold": "A",
     "opts": {"A": "Iron", "B": "a mixture of common household solvents",
              "C": "Copper", "D": "Zinc"},
     "cond": {"A": [-0.6], "B": [-0.5] * 6, "C": [-2.8], "D": [-3.4]},
     "uncond": {"A": [-1.0], "B": [-0.45] * 6, "C": [-2.0], "D": [-2.6]},
     "generated": "The answer is (A)."},
    {"q": "Why does Earth have seasons?", "gold": "D",
     "opts": {"A": "Because the Sun's output varies", "B": "Ocean currents",
              "C": "Solar flares", "D": "Because Earth's axis is tilted"},
     "cond": {"A": [-0.5] * 6, "B": [-0.6] * 2, "C": [-1.1] * 2,
              "D": [-0.3] * 5},
     "uncond": {"A": [-0.6] * 6, "B": [-0.8] * 2, "C": [-1.2] * 2,
                "D": [-0.48] * 5},
     "generated": "Because Earth's axis is tilted."},
    {"q": "In which year was the first artificial satellite launched?",
     "gold": "C",
     "opts": {"A": "1969", "B": "1961", "C": "1957", "D": "1972"},
     "cond": {"A": [-2.0], "B": [-1.8], "C": [-1.0], "D": [-2.6]},
     "uncond": {"A": [-1.5], "B": [-1.7], "C": [-2.2], "D": [-1.9]},
     "generated": "I'd say C, though B is close."},
]


def score_acc(item, letter):                      # harness-style `acc`
    return sum(item["cond"][letter])


def score_acc_norm(item, letter):                 # `acc_norm`: per byte
    return sum(item["cond"][letter]) / len(item["opts"][letter].encode())


def score_pmi(item, letter):                      # subtract the option's prior
    return sum(item["cond"][letter]) - sum(item["uncond"][letter])


def pick(item, scorer):
    return max(item["opts"], key=lambda L: scorer(item, L))


def parse_strict(text, item):
    return text if text in item["opts"] else None


def parse_lenient(text, item):
    m = re.search(r"\b([A-D])\b", text)
    return m.group(1) if m else None


def parse_with_text(text, item):
    letter = parse_lenient(text, item)
    if letter:
        return letter
    low = text.lower().rstrip(".")
    for L, option in item["opts"].items():        # fall back to the option text
        if option.lower().rstrip(".") in low:
            return L
    return None


LIKELIHOOD = [("acc (sum log-prob)", score_acc),
              ("acc_norm (per byte)", score_acc_norm),
              ("pmi (minus prior)", score_pmi)]
GENERATION = [("generate + strict parse", parse_strict),
              ("generate + lenient parse", parse_lenient),
              ("generate + text fallback", parse_with_text)]

print(f"{'Q':>2}{'gold':>6}{'acc':>6}{'norm':>6}{'pmi':>6}   what it generated")
for i, item in enumerate(QUESTIONS, 1):
    picks = "".join(f"{pick(item, s):>6}" for _, s in LIKELIHOOD)
    print(f"{i:>2}{item['gold']:>6}{picks}   {item['generated']!r}")

print(f"\n{'scorer':<26}{'score':>7}")
for name, scorer in LIKELIHOOD:
    hits = sum(pick(q, scorer) == q["gold"] for q in QUESTIONS)
    print(f"{name:<26}{hits / len(QUESTIONS):>7.0%}")
for name, parser in GENERATION:
    hits = sum(parser(q["generated"], q) == q["gold"] for q in QUESTIONS)
    print(f"{name:<26}{hits / len(QUESTIONS):>7.0%}")
```

One model, one set of questions, scores of **25%, 50%, 75%, 75%, 100%, 100%**.
Every one of those numbers is defensible and none of them is a lie.

Raw summed log-probability (`acc`) systematically prefers *short* options,
because every extra token adds another negative number — it picks the one-token
`"Oxygen"` over the correct two-token `"Carbon dioxide"`. Dividing by the
option's byte length (`acc_norm`) fixes that and immediately over-corrects on
question 2, where a long fluent wrong option wins on average quality. Subtracting
the option's unconditional log-probability (PMI-style scoring) fixes both,
because it asks "how much did the *question* raise this option's probability"
rather than "how probable is this text". Real harnesses report several of these
side by side for exactly this reason.

The generation column is worse, and more important, because it is what your
users will experience. The strict parser — accept only a bare `"A"` — scores
25% on a model that got everything right, because the model is chatty. The
lenient parser recovers two of those. Question 3, where the model answered
correctly *in words* and never emitted a letter, needs a fallback that matches
the option text. **A large fraction of reported "model failures" are parsing
failures**, and the fix belongs in the harness, not in a bigger model. This is
the same lesson as [28.2 Structured output](../ch28-tools-mcp/02-structured-output.md):
if you need a parseable answer, constrain the format rather than hoping.

!!! note "Which one should you use?"
    Whichever matches your product. If your system shows the user generated
    prose, score generation — the parsing difficulty is a real cost you are
    paying. Log-likelihood scoring is for comparing *base* models cheaply and
    without prompt-format confounds; it measures knowledge the model has but may
    not be able to express. Reporting one and shipping the other is how a launch
    surprises you.

## Contamination: the failure that inflates every number at once

Public benchmarks live on the public web. Training corpora are scraped from the
public web. The conclusion writes itself, and it is the single largest threat to
the validity of any published score: the model may have *seen the test set*.
The standard detector is n-gram overlap between each test item and the training
corpus — cheap, effective, and full of holes.

```python
"""Contamination detection by n-gram overlap — and the leaks it cannot see."""

# A slice of a pretraining corpus. Documents 2 and 4 are scraped quiz pages;
# document 5 states a test answer in its own words.
CORPUS = [
    "photosynthesis converts light energy into chemical energy stored in sugars",
    "practice quiz question in which year was the first artificial satellite "
    "launched the answer is 1957 the satellite was sputnik 1",
    "steel is an alloy whose main component is iron with a little carbon added",
    "quiz bank which planet has the shortest year the answer is mercury at "
    "eighty eight days",
    "neptune is currently known to have fourteen confirmed natural satellites",
]

TEST_SET = [
    ("In which year was the first artificial satellite launched?", "1957"),
    ("Which planet has the shortest year?", "Mercury"),
    ("How many moons does Neptune have?", "14"),
    ("Which gas do plants absorb during photosynthesis?", "Carbon dioxide"),
    ("What is the main component of steel?", "Iron"),
    ("Which ocean is the deepest?", "Pacific"),
]

# What the model answers: the three leaked answers plus two it genuinely knows.
ANSWERS = {"1957", "Mercury", "14", "Carbon dioxide", "Iron"}


def ngrams(text, n):
    words = "".join(c if c.isalnum() else " " for c in text.lower()).split()
    return {tuple(words[i:i + n]) for i in range(len(words) - n + 1)}


def overlap(question, corpus_grams, n):
    """Fraction of the question's n-grams that already appear in the corpus."""
    grams = ngrams(question, n)
    return len(grams & corpus_grams) / len(grams) if grams else 0.0


print(f"{'n=8':>6}{'n=5':>6}  question")
flags = {}
for n in (8, 5):
    corpus_grams = set().union(*(ngrams(doc, n) for doc in CORPUS))
    flags[n] = {q for q, _ in TEST_SET if overlap(q, corpus_grams, n) > 0.5}
for question, _ in TEST_SET:
    marks = "".join(f"{'HIT' if question in flags[n] else '-':>6}"
                    for n in (8, 5))
    print(f"{marks}  {question}")


def score(items):
    return sum(gold in ANSWERS for _, gold in items) / len(items)


TRULY_LEAKED = {q for q, _ in TEST_SET[:3]}         # we happen to know this
print()
for label, removed in [("reported score", set()),
                       ("decontaminated, n=8", flags[8]),
                       ("decontaminated, n=5", flags[5]),
                       ("every real leak removed", TRULY_LEAKED)]:
    kept = [(q, g) for q, g in TEST_SET if q not in removed]
    print(f"{label:<24}{score(kept):>6.1%}  "
          f"({len(kept)} items, {len(removed)} removed)")
```

The model reports **83.3%**. Its real ability on unseen questions is **66.7%**,
and the reported score plus the two n-gram policies land at 83.3%, 80.0% and
75.0% — every one of them an over-estimate. Follow the failures:

- At $n = 8$, the question *"Which planet has the shortest year?"* is only six
  words long, so it has no 8-grams at all and cannot be flagged. Short items are
  invisible to long-n detectors.
- Dropping to $n = 5$ catches it, at the cost of flagging any test item that
  shares a common five-word phrase with anything. Lower $n$ trades false
  negatives for false positives, and there is no setting that is right.
- The Neptune item is never caught at any $n$, because the corpus states the
  answer *in different words*. Verbatim overlap cannot detect a paraphrase, and
  paraphrase is how most contamination actually arrives.

This is the [Chapter 32](../ch32-data/01-why-data.md) problem viewed from the
other end: everything you put in the training set determines what your test set
can still tell you. The countermeasures used in practice are all imperfect and
all worth doing — canary strings embedded in benchmark files so a corpus can be
searched for them, held-out test splits that are never published, benchmarks
built *after* a model's training cutoff, and private variants of public sets.
The strongest of them is the last one, and it is the point of the whole section.

## Saturation, ceilings, and Goodhart

Even with no contamination at all, a benchmark wears out. Two mechanisms.

**Label noise puts a hard ceiling below 100%.** Every hand-built dataset
contains items whose reference answer is wrong or ambiguous. A model that is
*perfect* still loses those points, and — worse — the noise compresses the gaps
between good models.

```python
"""What a benchmark can still tell you once everyone is near the top."""

LABEL_ERROR = 0.04        # 4% of the gold answers are simply wrong
OPTIONS = 4               # multiple choice


def measured(ability):
    """Score the benchmark reports for a model of the given true ability.

    Marked correct = gold is right AND the model is right, OR gold is wrong
    AND the model happens to have produced that same wrong option.
    """
    coincide = 1 / (OPTIONS - 1)
    return ((1 - LABEL_ERROR) * ability
            + LABEL_ERROR * (1 - ability) * coincide)


print(f"label error {LABEL_ERROR:.0%}, {OPTIONS} options\n")
print(f"{'true ability':>13}{'reported':>10}{'headroom left':>15}")
for ability in (0.60, 0.80, 0.86, 0.90, 0.95, 1.00):
    m = measured(ability)
    print(f"{ability:>13.0%}{m:>10.1%}{measured(1.0) - m:>15.1%}")

gap_true = 0.04
lo, hi = 0.86, 0.86 + gap_true
print(f"\na genuine {gap_true:.0%}-point gain from {lo:.0%} to {hi:.0%} "
      f"shows up as {measured(hi) - measured(lo):.2%}")
print(f"the benchmark's maximum possible score is {measured(1.0):.0%}, "
      f"not 100%")
```

With 4% label error the ceiling is **96%**, and a genuine four-point improvement
in ability registers as **3.79 points** of reported score. Once the field is at
90% true ability — 86.5% reported, 9.5 points of headroom left — most of the
remaining gap is noise,
not capability, and the benchmark has stopped being able to rank the models you
care about. That is **saturation**, and it is why benchmarks are retired and
replaced rather than improved.

**Optimisation destroys the measurement.** This is [31.4's reward
hacking](../ch31-rl/04-reward-models.md) with a longer feedback loop and human
beings inside it. When a benchmark becomes the number everyone reports, people
tune prompts against it, select checkpoints on it, add its training split to the
mixture, and — occasionally — train on data that is "similar in spirit". None of
those steps is fraud, every one of them raises the score without raising the
underlying ability, and together they are Goodhart's law operating on a
community timescale:

> When a measure becomes a target, it ceases to be a good measure.

The reward-hacking plot in 31.4 rose smoothly while true quality fell. A
benchmark leaderboard looks exactly the same from the outside.

## Necessary, insufficient, and the eval you must build yourself

None of this means public benchmarks are worthless. They are the only
*comparable* numbers in existence: they let you rank candidate base models
before you commit, sanity-check that a quantization or a serving change did not
break anything ([27.4](../ch27-inference/04-quantization-deploy.md)), and detect
catastrophic regressions after fine-tuning. Skipping them is not sophistication.

But they cannot tell you whether *your* system works, for three reasons that no
amount of benchmark quality fixes: your inputs are not their inputs, your
definition of "correct" is not their reference answer, and your failures are
specific to your domain. A model at the top of every public leaderboard can be
useless on your support tickets.

So build a **private eval set out of your own failures**. The recipe is
unglamorous and it works:

1. Every time your system produces a bad output, save the input, the output, and
   one sentence on what was wrong. A file is enough to start.
2. Once a week, turn those into eval items with a checkable expected result:
   an exact answer, a required substring, a schema, a test that must pass.
3. Group them by failure *category* — retrieval missed, tool arguments wrong,
   format broken, hallucinated fact, refused a benign request.
4. Never fix a bug without adding its case to the set first. This is the
   [regression test](../ch24-practice/02-testing.md) discipline you already
   know, pointed at a probabilistic component.
5. Keep it private and never train on it. The moment it leaks into a prompt
   library or a fine-tuning set, it stops measuring anything.

Fifty items collected this way will tell you more about your next release than
any public leaderboard, because every one of them is a mistake your system
actually made. [33.2](02-eval-harness.md) builds the machinery to run them.

!!! warning "Common mistakes"

    - **Comparing scores produced by different harnesses.** Prompt format,
      few-shot count, normalizer and scoring mode each move the number by more
      than most model upgrades do. Re-run both models yourself, or compare
      nothing.
    - **Reporting pass@k from k samples.** The estimator is unbiased at
      $n = k$ but maximally noisy — our $n = 5$ run had a standard deviation of
      0.108 across repeats. Sample $n$ well above $k$.
    - **Blaming the model for a parsing failure.** The strict parser scored a
      fully-correct model at 25%. Look at raw outputs before you conclude
      anything about capability.
    - **Trusting an n-gram decontamination report.** It cannot see paraphrases
      and it cannot see items shorter than $n$ words. It is evidence of
      cleanliness, not proof.
    - **Chasing the last few points of a saturated benchmark.** Below the label
      noise floor you are fitting the errors in the dataset.
    - **Having no private eval.** If the only numbers you can quote are public
      ones, you cannot tell whether last Tuesday's prompt change helped.

## Check your understanding

1. A colleague reports 71% on a QA set; you reproduce 44% with the same model
   and the same data. Name the three most likely causes, in order.

    ??? success "Answer"

        First, the normalizer: raw equality versus a full lowercase,
        punctuation- and article-stripping chain moved our toy set from 16.7%
        to 91.7%. Second, the answer-extraction step — whether a chatty answer
        is parsed for the reference span or compared whole (25% versus 100% in
        the multiple-choice block). Third, the prompt protocol: few-shot count,
        instruction wording, and whether the answer format was demonstrated.
        Only after ruling those out is it worth suspecting the model or a
        decoding setting.

2. You draw $n = 5$ samples per task and report pass@5. What is wrong, and what
   is *not* wrong?

    ??? success "Answer"

        Nothing is wrong with the expected value: at $n = k$ the estimator
        reduces to "did any of the five pass", which is still unbiased — our
        200-repeat run averaged 0.667 against a truth of 0.662. What is wrong
        is the precision. Each task contributes a single coin flip, giving a
        standard deviation of 0.108 across repeats, so two runs of the same
        eval on the same model can differ by ten points. At $n = 100$ the
        standard deviation is 0.019.

3. Your model scores 83% on a benchmark. An 8-gram contamination check flags
   nothing. Can you conclude the score is clean?

    ??? success "Answer"

        No. In the contamination block the 8-gram check missed a leaked
        question that was shorter than eight words, and missed entirely a test
        item whose answer appeared in the corpus in different words. The
        reported 83.3% was really 66.7%. A clean n-gram report raises your
        confidence; it does not establish anything, and paraphrase leakage is
        both the most common form and the completely undetectable one.

4. Why is a private eval set built from your own failures more useful than a
   public benchmark, and what is the one rule that keeps it useful?

    ??? success "Answer"

        Because it is drawn from your input distribution, uses your definition
        of correct, and consists of mistakes your system actually made — so a
        gain on it is a gain your users will feel. Public benchmarks measure
        general ability on someone else's distribution and are increasingly
        contaminated and saturated. The rule: never train on it, never publish
        it, and never let it into a prompt library. A private eval that leaks
        into training becomes a memorisation test, which is exactly the failure
        this section spent five hundred words describing.
