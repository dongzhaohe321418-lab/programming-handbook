# Chapter 33 · Exercises

Eight problems on measuring systems that have no compiler to tell you they are
wrong, easiest first. They build on [33.1](01-benchmarks.md),
[33.2](02-eval-harness.md) and [33.3](03-llm-as-judge.md), and every solution
runs in the browser on the standard library and numpy alone.

Exercise 33.1 asks you to **predict** three numbers before running anything.
Write them down first — the gap between your list and the printed one is the
whole lesson about normalization.

Nothing here calls a model or touches the network. Every "model" is a scripted
`FakeLLM` or a list of recorded results.

---

### Exercise 33.1 — Predict the score, then normalize (●)

Here are eight (prediction, gold) pairs from a short-answer eval:

```text
("Berlin", "Berlin")                 ("42", "42")
("berlin.", "Berlin")                ("42.", "42")
("  BERLIN ", "Berlin")              ("4.2", "42")
("The capital is Berlin", "Berlin")  ("Munich", "Berlin")
```

Six of the eight predictions are genuinely correct. **Before running anything**,
predict the score under three scorers: `strict` (raw string equality),
`trimmed` (strip and lowercase), and `aggressive` (strip, lowercase, and remove
all punctuation). Then run the solution and check.

??? success "Solution"

    ```python
    import string

    PAIRS = [
        ("Berlin", "Berlin"),
        ("berlin.", "Berlin"),
        ("  BERLIN ", "Berlin"),
        ("The capital is Berlin", "Berlin"),
        ("42", "42"),
        ("42.", "42"),
        ("4.2", "42"),          # wrong: 4.2 is not 42
        ("Munich", "Berlin"),   # wrong
    ]


    def strict(p, g):
        return p == g


    def trimmed(p, g):
        return p.strip().lower() == g.strip().lower()


    def aggressive(p, g):
        def norm(t):
            t = t.strip().lower()
            t = t.translate(str.maketrans("", "", string.punctuation))
            return " ".join(t.split())
        return norm(p) == norm(g)


    TRULY_CORRECT = [True, True, True, True, True, True, False, False]

    print(f"{'scorer':<12}{'score':>7}   accepted")
    for name, fn in (("strict", strict), ("trimmed", trimmed),
                     ("aggressive", aggressive)):
        hits = [fn(p, g) for p, g in PAIRS]
        accepted = [PAIRS[i][0] for i in range(len(PAIRS)) if hits[i]]
        print(f"{name:<12}{sum(hits) / len(hits):>7.1%}   {accepted}")

    wrongly = [PAIRS[i][0] for i in range(len(PAIRS))
               if aggressive(*PAIRS[i]) and not TRULY_CORRECT[i]]
    print(f"\ntrue accuracy: {sum(TRULY_CORRECT) / len(PAIRS):.1%}")
    print(f"aggressive scorer wrongly accepts: {wrongly}")
    ```

    The scores are 25.0%, 37.5% and 75.0% — a 50-point range for one unchanged
    model. The important line is the last one. The `aggressive` scorer reports
    exactly the true accuracy of 75.0%, and it is right by accident: it wrongly
    accepts `"4.2"` against a gold of `"42"` and wrongly rejects
    `"The capital is Berlin"`, and the two errors cancel. A score that happens
    to be correct is not a correct score — always print which items your
    normalizer flipped.

---

### Exercise 33.2 — pass@k on real sample counts (●)

Two code models were sampled $n = 10$ times on the same five problems. The
number of samples that passed the tests:

```text
model X:  [9, 8, 7, 0, 0]
model Y:  [4, 4, 4, 3, 3]
```

Compute the unbiased pass@1, pass@5 and pass@10 for each. Your product samples
**once** per request and shows the result. Which model do you ship, and what
would change your mind?

??? success "Solution"

    ```python
    from math import comb

    N = 10                       # samples drawn per task
    RESULTS = {"model X": [9, 8, 7, 0, 0], "model Y": [4, 4, 4, 3, 3]}


    def pass_at_k(n, c, k):
        if n - c < k:            # every k-subset contains a passing sample
            return 1.0
        return 1.0 - comb(n - c, k) / comb(n, k)


    print(f"{'model':<9}{'pass@1':>9}{'pass@5':>9}{'pass@10':>9}")
    for name, counts in RESULTS.items():
        row = [sum(pass_at_k(N, c, k) for c in counts) / len(counts)
               for k in (1, 5, 10)]
        print(f"{name:<9}" + "".join(f"{v:>9.3f}" for v in row))

    print("\nplug-in estimate 1-(1-c/n)^k, for comparison:")
    for name, counts in RESULTS.items():
        row = [sum(1 - (1 - c / N) ** k for c in counts) / len(counts)
               for k in (1, 5, 10)]
        print(f"{name:<9}" + "".join(f"{v:>9.3f}" for v in row))
    ```

    Ship **model X**: at pass@1 it scores 0.480 against Y's 0.360, and pass@1
    is the metric that matches a product which samples once. The ranking
    reverses completely by pass@10 — 0.600 for X against 1.000 for Y — because
    X is hopeless on two problems while Y eventually solves everything. What
    would change your mind: adding retries, best-of-$n$ selection, or a test
    suite the model can iterate against, all of which turn your product into a
    higher-$k$ system. Notice too that the plug-in estimator puts Y's pass@10 at
    0.985 rather than 1.000 — biased low, exactly as [33.1](01-benchmarks.md)
    showed.

---

### Exercise 33.3 — Write a rubric that a judge can actually apply (●)

Your support agent answers customer questions from a ticket context. Write a
judge rubric for the criterion **factual grounding**, with four anchored levels,
an explicit tie rule, and a constrained output format. Then implement a scripted
judge that applies it to four replies and prints the score plus the deciding
evidence.

??? success "Solution"

    ```python
    """A rubric, and a scripted judge that applies it."""

    RUBRIC = """CRITERION: factual grounding (judge this and nothing else —
    ignore tone, length and formatting)

      3 = every factual claim in the reply is supported by the ticket context
      2 = every claim is supported except one MINOR detail (a rounding, a
          wording difference) that would not change the customer's action
      1 = the reply contains a claim the context does not support
      0 = the reply contains a claim the context CONTRADICTS

    Tie rule: if two replies earn the same level, they are tied. Do not
    break ties on style.

    Output JSON only: {"evidence": "<the deciding claim, quoted>", "score": n}
    """

    CONTEXT = {"order shipped on 3 May", "carrier is Ravenpost",
               "tracking number RP-88123", "estimated delivery 9 May"}
    CONTRADICTS = {"order has not shipped", "estimated delivery 4 May"}

    # Each reply is (label, [(claim, is_minor), ...]).
    REPLIES = [
        ("A", [("order shipped on 3 May", False),
               ("tracking number RP-88123", False)]),
        ("B", [("order shipped on 3 May", False),
               ("estimated delivery 9 or 10 May", True)]),
        ("C", [("carrier is Ravenpost", False),
               ("a refund is available if it is late", False)]),
        ("D", [("order has not shipped", False)]),
    ]


    def judge(claims):
        """Applies the rubric mechanically. A real judge is an LLM prompted
        with the RUBRIC text above; this stand-in keeps the block runnable."""
        if any(c in CONTRADICTS for c, _ in claims):
            bad = next(c for c, _ in claims if c in CONTRADICTS)
            return 0, f"contradicted: {bad!r}"
        unsupported = [(c, minor) for c, minor in claims if c not in CONTEXT]
        if not unsupported:
            return 3, "every claim supported"
        if len(unsupported) == 1 and unsupported[0][1]:
            return 2, f"one minor detail: {unsupported[0][0]!r}"
        return 1, f"unsupported: {unsupported[0][0]!r}"


    print(RUBRIC)
    print(f"{'reply':<7}{'score':>6}   evidence")
    for label, claims in REPLIES:
        score, evidence = judge(claims)
        print(f"{label:<7}{score:>6}   {evidence}")
    ```

    The four replies score 3, 2, 1 and 0, and each score comes with the claim
    that decided it. That last property is what makes a rubric auditable: when
    a human disagrees with the judge, they argue about a quoted claim rather
    than about a vibe. Note that reply C is fluent, polite and helpful and still
    scores 1 — it invented a refund policy. A rubric that had asked for "overall
    quality" would have rewarded it.

---

### Exercise 33.4 — Is the gap real? (●●)

Two prompt versions were run on the same 40 tasks, scored 1 or 0. Version 2 is
version 1 with five previously-failing tasks now passing. Compute a bootstrap
95% confidence interval for each version's accuracy, then for the **paired**
per-task difference, and decide whether to ship.

??? success "Solution"

    ```python
    import numpy as np

    # 40 tasks, scored 1 or 0, same tasks for both prompt versions.
    V1 = np.array([1,1,0,1,1,1,0,1,1,1,0,1,1,0,1,1,1,0,1,1,
                   0,1,1,1,0,1,1,0,1,1,1,0,1,1,0,1,1,1,0,1], dtype=float)
    V2 = V1.copy()
    V2[[2, 10, 13, 17, 20]] = 1.0          # v2 fixes five of v1's failures


    def boot_ci(x, reps=5000, seed=0):
        g = np.random.default_rng(seed)
        idx = g.integers(0, len(x), size=(reps, len(x)))
        return np.percentile(x[idx].mean(axis=1), [2.5, 97.5])


    for name, x in (("prompt v1", V1), ("prompt v2", V2)):
        lo, hi = boot_ci(x)
        print(f"{name}: {x.mean():.1%}   95% CI [{lo:.1%}, {hi:.1%}]")

    d = V2 - V1
    lo, hi = boot_ci(d)
    w, l = int((d > 0).sum()), int((d < 0).sum())
    print(f"\npaired difference: {d.mean():+.1%}   95% CI [{lo:+.1%}, {hi:+.1%}]")
    print(f"v2 wins on {w} tasks, loses on {l}, ties on {len(d) - w - l}")
    print("verdict:", "real" if lo > 0 else "cannot distinguish from noise")
    ```

    Ship it. The unpaired intervals — [57.5%, 85.0%] and [72.5%, 95.0%] —
    overlap heavily, and stopping there would have you shrugging at a 12.5-point
    gain. The paired difference is +12.5% with a CI of [+2.5%, +22.5%], which
    excludes zero. The reason pairing is so much sharper here is that the two
    versions agree on 35 of 40 tasks, and all five disagreements go the same
    way; the shared difficulty of the tasks cancels out of the difference. The
    interval is still 20 points wide, so "we gained somewhere between 2 and 22
    points" is the honest claim, not "we gained 12.5".

---

### Exercise 33.5 — Detect contamination, and find the leak you cannot detect (●●)

Given the four-document corpus and six-item test set below, flag every test
question with more than 50% 6-gram overlap with the corpus, and report the score
before and after decontamination. Then read the corpus and find the leaked item
your detector missed.

??? success "Solution"

    ```python
    CORPUS = [
        "welcome to the trivia archive todays question what is the boiling "
        "point of water at sea level in celsius the answer is 100 degrees",
        "the human skeleton of an adult contains two hundred and six bones in "
        "total which is fewer than a newborn has",
        "study set flashcard which element has the chemical symbol au the "
        "answer is gold used in jewellery and electronics",
        "rivers of the world vary greatly in length and discharge volume "
        "across every continent",
    ]

    TEST_SET = [
        ("What is the boiling point of water at sea level in Celsius?", "100"),
        ("Which element has the chemical symbol Au?", "Gold"),
        ("How many bones are in the adult human skeleton?", "206"),
        ("What is the longest river in Africa?", "Nile"),
        ("What is the chemical symbol for potassium?", "K"),
        ("Which planet is closest to the Sun?", "Mercury"),
    ]

    MODEL_ANSWERS = {"100", "Gold", "206", "Mercury"}      # 4 of 6 correct
    N = 6


    def ngrams(text, n):
        words = "".join(c if c.isalnum() else " " for c in text.lower()).split()
        return {tuple(words[i:i + n]) for i in range(len(words) - n + 1)}


    corpus_grams = set().union(*(ngrams(d, N) for d in CORPUS))


    def overlap(text):
        grams = ngrams(text, N)
        return len(grams & corpus_grams) / len(grams) if grams else 0.0


    print(f"{N}-gram overlap\n{'overlap':>8}  question")
    flagged = []
    for q, _ in TEST_SET:
        o = overlap(q)
        if o > 0.5:
            flagged.append(q)
        print(f"{o:>8.0%}  {q}")

    kept = [(q, a) for q, a in TEST_SET if q not in flagged]
    score = lambda items: sum(a in MODEL_ANSWERS for _, a in items) / len(items)
    print(f"\nreported       {score(TEST_SET):>6.1%}  ({len(TEST_SET)} items)")
    print(f"decontaminated {score(kept):>6.1%}  ({len(kept)} items, "
          f"{len(flagged)} removed)")

    # The skeleton answer is in the corpus too — spelled out in words, so no
    # n-gram at any length matches the question.
    paraphrased = TEST_SET[2][0]
    clean = [(q, a) for q, a in kept if q != paraphrased]
    print(f"paraphrase too {score(clean):>6.1%}  ({len(clean)} items)")
    ```

    The detector flags two items and the score falls from 66.7% to 50.0%. The
    third leak is document 2: it states that an adult skeleton has *two hundred
    and six* bones, so the model can answer "206" from memory while sharing no
    n-gram at any length with the question. Removing it too leaves 33.3% — half
    the reported figure. This is the general shape of contamination work: your
    detector gives you a lower bound on the leakage and never an upper one.

---

### Exercise 33.6 — Measure position bias, then remove it (●●)

The judge below adds a fixed bonus to whichever answer it reads first. Two
hundred pairs compare a new prompt against the old one; the new prompt is
genuinely a little better. Measure the win rate with the new answer shown first,
shown second, and averaged over both orders. Report the fraction of pairs whose
winner flips, and say how much of the single-order win rate was position rather
than quality.

??? success "Solution"

    ```python
    import numpy as np

    rng = np.random.default_rng(4)
    N = 200
    q_new = rng.normal(0.40, 1.0, N)        # the new prompt is genuinely better
    q_old = rng.normal(0.00, 1.0, N)
    TRUTH = float((q_new > q_old).mean())


    class PairJudge:
        """Scripted judge: quality, plus a bonus for whatever it reads first."""
        POSITION = 0.5

        def __call__(self, first, second):
            return "first" if first + self.POSITION > second else "second"


    judge = PairJudge()
    new_first = np.array([judge(q_new[i], q_old[i]) == "first"
                          for i in range(N)], dtype=float)
    new_second = np.array([judge(q_old[i], q_new[i]) == "second"
                           for i in range(N)], dtype=float)
    averaged = 0.5 * (new_first + new_second)

    print(f"true win rate for the new prompt   {TRUTH:>8.1%}")
    print(f"judged with new shown first        {new_first.mean():>8.1%}")
    print(f"judged with new shown second       {new_second.mean():>8.1%}")
    print(f"averaged over both orders          {averaged.mean():>8.1%}")
    print(f"\npairs that flip when swapped       {(averaged == 0.5).mean():>8.1%}")
    print(f"single-order overstatement         "
          f"{new_first.mean() - averaged.mean():>+8.1%}")
    ```

    The true win rate is 62.0%. Judged with the new answer first it reads 77.5%;
    judged second, 44.5% — the same comparison, opposite conclusions. Averaging
    the two orders gives 61.0%, within a point of the truth, and **33.0% of
    individual pairs change winner when swapped**. So 16.5 of the 77.5 points
    were position, not quality. One extra call per pair removes essentially all
    of it, which makes this the highest return-on-effort fix in the whole
    chapter. Watch out for the numpy trap in this exercise: adding two boolean
    arrays performs a logical *or*, so cast to `float` before averaging.

---

### Exercise 33.7 — Metrics for an inbox-triage agent (●●)

You are shipping an agent that reads each incoming email and either **files** it,
**drafts** a reply for a human to send, or **escalates** it to a person. Design
the metric set — you may not use "accuracy" alone — and compute it over the ten
recorded episodes below. State which single metric you would gate the deploy on
and why.

??? success "Solution"

    ```python
    """Metrics for an inbox-triage agent: file, draft, or escalate."""
    from statistics import median

    # Each episode: what the agent did, what a human said it should have done,
    # whether it sent anything without approval, plus steps and tokens.
    EPISODES = [
        # id     did          should       sent  steps tokens
        ("m01", "filed",     "filed",      False,  2,  1200),
        ("m02", "drafted",   "drafted",    False,  5,  4100),
        ("m03", "escalated", "drafted",    False,  3,  2200),
        ("m04", "filed",     "escalated",  False,  2,  1100),
        ("m05", "drafted",   "drafted",    True,   6,  4800),
        ("m06", "escalated", "escalated",  False,  4,  2600),
        ("m07", "drafted",   "filed",      False,  9,  7300),
        ("m08", "filed",     "filed",      False,  2,  1150),
        ("m09", "escalated", "escalated",  False,  3,  2050),
        ("m10", "drafted",   "drafted",    False,  4,  3300),
    ]
    PRICE_PER_1K = 0.003

    correct = [e for e in EPISODES if e[1] == e[2]]
    escalated = [e for e in EPISODES if e[1] == "escalated"]
    should_escalate = [e for e in EPISODES if e[2] == "escalated"]
    unapproved = [e for e in EPISODES if e[3]]
    cost = sum(e[5] for e in EPISODES) / 1000 * PRICE_PER_1K

    precision = sum(e[2] == "escalated" for e in escalated) / len(escalated)
    recall = sum(e[1] == "escalated" for e in should_escalate) / len(
        should_escalate)

    print(f"routing accuracy        {len(correct) / len(EPISODES):>7.1%}")
    print(f"escalation precision    {precision:>7.1%}"
          f"   (escalations that were warranted)")
    print(f"escalation recall       {recall:>7.1%}"
          f"   (warranted escalations caught)")
    print(f"unapproved send rate    {len(unapproved) / len(EPISODES):>7.1%}"
          f"   <-- gate on this one")
    print(f"median steps            {median(e[4] for e in EPISODES):>7.1f}")
    print(f"p90 steps               "
          f"{sorted(e[4] for e in EPISODES)[int(0.9 * len(EPISODES))]:>7.1f}")
    print(f"cost per email          ${cost / len(EPISODES):>6.4f}")
    print(f"cost per CORRECT email  ${cost / len(correct):>6.4f}")
    ```

    Routing accuracy is 70.0%, but the number that decides the deploy is the
    **unapproved send rate of 10.0%**. The three routing outcomes are not
    equally bad: filing something that should have been escalated is a missed
    ticket, escalating something that could have been drafted is wasted human
    time, and sending an email without approval is an irreversible action taken
    on a customer — the class of failure
    [30.4](../ch30-agents/04-frameworks.md) says must be behind a human
    approval. Gate on it at zero. Everything else is a quality dial: escalation
    precision and recall both sit at 66.7%, the p90 step count of 9 against a
    median of 3.5 shows a long tail worth investigating, and cost per *correct*
    email ($0.0128) is 1.4× cost per email because mistakes are paid for twice.

---

### Exercise 33.8 — Extend the harness with a schema scorer and a gate (●●●)

Add a fifth scorer to the [33.2](02-eval-harness.md) harness: `json_schema`,
which parses the model's output as JSON and awards partial credit for the
fraction of required fields that are present *and* of the right type. Then wire
it to a regression gate that compares two model versions per task and fails when
any task goes backwards — even if the aggregate improves.

??? success "Solution"

    ```python
    """A JSON-schema scorer plus a regression gate, on the 33.2 harness."""
    import json
    from dataclasses import dataclass


    @dataclass(frozen=True)
    class Task:
        id: str
        prompt: str
        schema: tuple            # (field, type) pairs


    SCHEMA = (("name", str), ("priority", int), ("tags", list))
    TASKS = [Task("j01", "reset password ticket", SCHEMA),
             Task("j02", "billing error ticket", SCHEMA),
             Task("j03", "vpn down ticket", SCHEMA)]

    V1 = {"j01": '{"name": "reset password", "priority": 2, "tags": ["auth"]}',
          "j02": '{"name": "billing error", "priority": "high", "tags": ["bill"]}',
          "j03": 'Sure! {"name": "vpn down", "priority": 1, "tags": ["net"]}'}
    V2 = {"j01": '{"name": "reset password", "priority": 2}',
          "j02": '{"name": "billing error", "priority": "high", "tags": ["bill"]}',
          "j03": '{"name": "vpn down", "priority": 1, "tags": ["net"]}'}


    def score_json_schema(output, task):
        """Partial credit: the fraction of schema fields present and well typed."""
        try:
            obj = json.loads(output)
        except json.JSONDecodeError:
            return 0.0                               # not JSON at all
        if not isinstance(obj, dict):
            return 0.0
        ok = sum(field in obj and isinstance(obj[field], kind)
                 and not isinstance(obj[field], bool)
                 for field, kind in task.schema)
        return ok / len(task.schema)


    def run(outputs):
        scored = {}
        for task in TASKS:
            try:
                scored[task.id] = score_json_schema(outputs[task.id], task)
            except Exception:                        # isolation, as always
                scored[task.id] = 0.0
        return scored


    base, new = run(V1), run(V2)
    TOLERANCE = 0.0

    print(f"{'task':<6}{'v1':>7}{'v2':>7}   verdict")
    regressions = []
    for task in TASKS:
        delta = new[task.id] - base[task.id]
        verdict = ("REGRESSED" if delta < -TOLERANCE else
                   "improved" if delta > 0 else "unchanged")
        if delta < -TOLERANCE:
            regressions.append(task.id)
        print(f"{task.id:<6}{base[task.id]:>7.2f}{new[task.id]:>7.2f}   {verdict}")

    b = sum(base.values()) / len(base)
    n = sum(new.values()) / len(new)
    print(f"\naggregate {b:.1%} -> {n:.1%}   ({n - b:+.1%})")
    print("GATE FAILED:" if regressions else "GATE PASSED:",
          f"{len(regressions)} per-task regression(s) {regressions}")
    ```

    The aggregate goes from 55.6% to 77.8% — a 22-point improvement — and the
    gate fails anyway, because `j01` dropped from 1.00 to 0.67 when v2 stopped
    emitting the `tags` field. That is the correct behaviour: the aggregate
    gain came from v2 finally producing parseable JSON on `j03`, which has
    nothing to do with the field it silently dropped. A human now decides
    whether the trade is acceptable and, if so, re-records the baseline in a
    visible commit.

    Three details worth stealing. Partial credit over schema fields turns "the
    JSON was wrong" into "one of three fields was wrong", which is actionable.
    The `not isinstance(obj[field], bool)` guard exists because `bool` is a
    subclass of `int` in Python, so `True` would otherwise pass an `int` field.
    And the scorer never raises: unparseable output scores 0.0 rather than
    taking the suite down, which is the error-isolation rule from
    [33.2](02-eval-harness.md) applied inside the scorer as well as around it.
