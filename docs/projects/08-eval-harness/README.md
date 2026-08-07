# Project 8 · An Evaluation Harness

[33.2](../../ch33-eval/02-eval-harness.md) said it plainly: a harness is
four hundred lines of plumbing wrapped around five decisions, and if you
adopt someone else's plumbing before you have made those decisions yourself,
you cannot tell whether a number it prints is real. This project is the four
hundred lines — a dataset on disk, a model interface you can swap, four
scorers including a judge whose bias you *measure* rather than hope about, a
runner that survives a provider outage, bootstrap confidence intervals, a
paired comparison that decides whether a gap is real, and a regression gate
that fails a build.

Build it once and you own the instrument. Every claim you make about a model
afterwards — yours or somebody else's — gets read through it.

## What you'll build

A report you would be happy to put in a pull request, and a gate that stops
one:

```text
=== strong-1 ================================================
task  category   scorer      score   tok   secs  note
t01   knowledge  exact        1.00    15   0.21
t04   format     regex        1.00    12   0.21
t06   code       execution    1.00    42   0.35
t08   support    judge        0.50    39   0.33  partial
t09   support    judge        0.00    23   0.25  wrong

accuracy  85.0%   strict pass rate  80.0%   (10 tasks)
by category  code 100%   format 100%   knowledge 100%   math 100%   support 25%
failures     partial x1   wrong x1
cost         $0.00047 total, $0.00005/task, $0.00006/success

weak-1      37.5%   95% CI [15.0%, 62.6%]   width  48%
strong-1    85.0%   95% CI [60.0%, 100.0%]   width  40%

paired difference (strong-1 - weak-1): +47.5%
95% CI on the difference: [+22.5%, +70.1%]  -> significant
per task: 7 win / 0 loss / 3 tie

5. the regression gate
baseline strong-1: 85.0%   now: 85.0%   floor: 85.0%
  REGRESSED t04  1.00 -> 0.00   format: '14/03/2021'
  improved   t09  0.00 -> 1.00   support: 'A database failover caused a 40 minute outage, and it is now resolved.'

GATE FAILED: 1 task(s) went backwards.
In CI this is a non-zero exit code and the deploy stops.
```

Read the last block twice. **Aggregate accuracy is 85.0% before the change
and 85.0% after.** A gate that only checked the average would have shipped a
broken date format, because one gain cancelled one regression exactly.

## What it exercises

- [33.2 Building an eval harness](../../ch33-eval/02-eval-harness.md) — the
  five decisions, per-task error isolation, bootstrap intervals, and gating
  on per-task regressions rather than the mean.
- [33.3 LLM-as-a-judge](../../ch33-eval/03-llm-as-judge.md) — pairwise
  against a frozen reference, judged in both orders, with the biases
  measured before the judge is trusted.
- [33.1 Benchmarks and metrics](../../ch33-eval/01-benchmarks.md) — why
  exact match is a *family* of metrics and normalisation is a design choice.
- [Chapter 11 · Files](../../ch11-files/index.md) — the dataset and the
  baseline both live on disk, written then read back, because an eval you
  cannot check into a repository is not an eval.
- [24.2 Testing](../../ch24-practice/02-testing.md) — a regression gate is
  regression-test discipline applied to a component with no compiler.
- [Chapter 12 · Writing Your Own Classes](../../ch12-classes/index.md) and
  [15.3 Interfaces](../../ch15-inheritance/03-interfaces.md) — one model
  interface, many providers; one scorer signature, many scorers.

## Milestones

### Milestone 1 — a task dataclass, and a dataset on disk

**Goal:** a frozen `Task` dataclass (`id`, `prompt`, `scorer`, `expected`,
`tests`, `reference`, `rubric`, `category`), a `write_dataset` that emits one
JSON object per line, and a `read_dataset` that reads it back into `Task`
objects.

**Done when...** ten tasks survive a write-then-read round trip with
`tasks == TASKS` printing `True` — which means you have handled the fact
that JSON has no tuples, so `tests` and `rubric` come back as lists and must
be restored.

??? tip "Hint"

    JSONL, not JSON: one object per line means the file is greppable,
    appendable, and produces a readable diff when somebody adds a task in a
    pull request.

    ```python
    import json
    import tempfile
    from dataclasses import asdict, dataclass
    from pathlib import Path

    @dataclass(frozen=True)
    class Task:
        id: str
        tests: tuple = ()

    path = Path(tempfile.mkdtemp()) / "tasks.jsonl"
    path.write_text(json.dumps(asdict(Task("t01", (("f(1)", 2),)))) + "\n")

    record = json.loads(path.read_text().splitlines()[0])
    print("straight from JSON:", Task(**record))
    record["tests"] = tuple(tuple(t) for t in record["tests"])
    print("tuples restored   :", Task(**record))
    print("round trip equal? ", Task(**record) == Task("t01", (("f(1)", 2),)))
    ```

    Frozen matters too: a task that a scorer can mutate mid-run is a task
    whose meaning changed halfway through your suite.

### Milestone 2 — one model interface, two models

**Goal:** a `complete(prompt)` returning a `Completion` with the text, the
prompt and completion token counts, and a latency — plus two `FakeLLM`
instances of visibly different quality, one of which raises on a particular
prompt to stand in for a provider outage.

**Done when...** both models answer through the identical interface; the
weak one raises `RuntimeError` on exactly one task; and two runs produce
byte-identical numbers, because latency is *computed* from the reply length
rather than measured with a clock.

??? tip "Hint"

    Resist the urge to call `time.perf_counter()` here. A real adapter
    records a wall clock, and that is exactly what would make this project
    untestable and its output different on every machine:

    ```python
    from dataclasses import dataclass

    @dataclass
    class Completion:
        text: str
        completion_tokens: int
        latency_s: float

    def complete(text, ms_per_token=6.0, overhead_s=0.20):
        tokens = max(1, len(text) // 4)
        return Completion(text, tokens,
                          round(overhead_s + ms_per_token / 1000 * tokens, 3))

    print(complete("Paris"))
    print(complete("The capital of France is the city of Paris."))
    ```

    Keep the *shape* honest — tokens in, tokens out, seconds — and swapping
    in a real provider is one method body, with every column of your report
    already wired up.

### Milestone 3 — three scorers with checkable answers

**Goal:** `score_exact` with normalisation (lower-case, strip punctuation,
drop articles, collapse whitespace), `score_regex`, and `score_execution`
which `exec`s the generated code and returns the *fraction* of its tests
that pass.

**Done when...** `"  paris.  "` scores 1.0 against `"Paris"`;
`"The capital of France is Paris."` scores 0.0 and you can say why that is
the right answer for a task whose prompt says "the name only"; and a
`second_largest` that forgets duplicates scores 0.50 rather than 0.

??? tip "Hint"

    Partial credit is what tells you *which* wrong answer was closer:

    ```python
    def score_execution(code, tests):
        namespace = {}
        try:
            exec(code, namespace)
        except Exception:
            return 0.0
        passed = 0
        for call, expected in tests:
            try:
                passed += eval(call, namespace) == expected
            except Exception:
                pass
        return passed / len(tests)

    TESTS = [("second_largest([1, 5, 3])", 3), ("second_largest([9, 9, 4])", 4),
             ("second_largest([2, 1])", 1), ("second_largest([4, 4, 4])", None)]
    good = ("def second_largest(xs):\n"
            "    d = sorted(set(xs), reverse=True)\n"
            "    return d[1] if len(d) > 1 else None")
    buggy = "def second_largest(xs):\n    return sorted(xs)[-2]"
    print("good :", score_execution(good, TESTS))
    print("buggy:", score_execution(buggy, TESTS))
    ```

    Note what the buggy version does on `[4, 4, 4]`: it returns `4` instead
    of `None`, and on a two-element list it happens to be right. Only a test
    suite with the awkward cases in it can tell those apart from a correct
    answer.

!!! warning "The execution scorer runs model-written code"
    Ours uses `exec` because every string here is one we wrote and the block
    must run in your browser. In production, generated code executes in a
    sandbox — a container with no credentials, no network, a memory cap and
    a wall-clock limit. `exec` on model output inside your own process is
    not an eval harness; it is a remote code execution vulnerability with a
    progress bar.

### Milestone 4 — a judge, and the correction it needs

**Goal:** a `FakeJudge` whose position and verbosity biases are literal
coefficients, a `score_judge` that compares the candidate against a frozen
reference answer **in both orders and averages**, and a
`judge_calibration()` that measures the biases on pairs of *equal* true
quality.

**Done when...** calibration on equal-quality pairs shows a win rate near
100% when the candidate is always shown first, falls to 66.2% when both
orders are averaged, and reaches 50.0% only when lengths are matched as
well — and you can point at a real task in your suite whose score drops from
1.00 to 0.50 once the correction is applied.

??? tip "Hint"

    A pair that changes its winner when you swap the order is not a win for
    anybody; it is a tie, and half a win is the correct accounting:

    ```python
    def compare(a, b, position_bonus=0.35):
        """The judge only ever sees an order, never a label."""
        return "first" if a + position_bonus > b else "second"

    candidate, reference = 3.0, 3.0            # equal quality
    first = compare(candidate, reference) == "first"
    second = compare(reference, candidate) == "second"
    print("candidate shown first :", first)
    print("candidate shown second:", second)
    print("score with correction :", 0.5 * (first + second))
    ```

    You cannot prompt these biases away. "Ignore length and formatting"
    reduces them and never removes them; the reliable countermeasures are
    *protocol* changes — swap the order and average, control for length,
    hide authorship — as [33.3](../../ch33-eval/03-llm-as-judge.md) shows by
    measuring each one.

### Milestone 5 — the runner and the report

**Goal:** `run_eval(model, tasks, judge)` that catches **everything**
per task and records what it caught, plus a report printing a per-task table
and then accuracy, strict pass rate, per-category scores, failure buckets,
cost, and latency percentiles.

**Done when...** the weak model's simulated 503 shows up as a scored row
with an `error` note instead of a traceback that kills the run; accuracy and
strict pass rate are reported separately (37.5% and 20.0% for the weak
model); and the failure buckets name four different remedies rather than one
number.

??? tip "Hint"

    The rule is: the runner catches everything, records it as a scored
    result, and keeps going. A harness that dies on item 340 of 500 is a
    harness you will stop running — and re-running "just the rest" silently
    changes your sample.

    ```python
    def run(tasks, call):
        results = []
        for task in tasks:
            try:
                results.append((task, call(task), ""))
            except Exception as exc:              # isolation lives HERE
                results.append((task, 0.0, f"{type(exc).__name__}: {exc}"))
        return results

    def flaky(task):
        if task == "t03":
            raise RuntimeError("503 from upstream provider")
        return 1.0

    for task, score, error in run(["t01", "t02", "t03", "t04"], flaky):
        print(f"{task}  {score:.2f}  {error or 'ok'}")
    ```

    Silently *dropping* the failed item is the version to avoid: it inflates
    every score computed afterwards, and nothing in the report says so.

### Milestone 6 — confidence intervals and a paired comparison

**Goal:** a percentile bootstrap — resample the tasks with replacement,
re-average, take the 2.5th and 97.5th percentiles — reported for each model,
and then the same interval applied to the *per-task difference*.

**Done when...** each model's own interval is tens of points wide on ten
tasks; the paired interval on the difference is narrower than either; and
your comparison prints an explicit verdict, `significant` or
`inside the noise`, alongside a win/loss/tie count.

??? tip "Hint"

    Pairing is free precision, which is why both models must see identical
    tasks in identical order:

    ```python
    import numpy as np

    def boot_ci(values, reps=4000, seed=1):
        x = np.asarray(values, dtype=float)
        rng = np.random.default_rng(seed)
        index = rng.integers(0, len(x), size=(reps, len(x)))
        means = x[index].mean(axis=1)
        return np.percentile(means, [2.5, 97.5])

    a = np.array([1.0] * 28 + [0.0] * 12)                # 70% on 40 tasks
    b = a.copy()
    b[np.flatnonzero(a == 0)[:8]] = 1.0                  # B = A plus 8 fixes
    print("A     95% CI:", np.round(boot_ci(a), 3))
    print("B     95% CI:", np.round(boot_ci(b), 3))
    print("B - A 95% CI:", np.round(boot_ci(b - a), 3))
    ```

    The two separate intervals — `[0.55, 0.825]` and `[0.80, 0.975]` — still
    overlap, so read on their own they say "possibly better, cannot tell".
    The paired interval on the difference is `[0.075, 0.325]`: half as wide
    and nowhere near zero, because the shared difficulty of the tasks
    cancels out. Same +20 points either way; only one of the three intervals
    answers the question you asked.

### Milestone 7 — the regression gate

**Goal:** save a baseline to a JSON file (model name, aggregate accuracy,
per-task scores), then compare a new run against it and fail on **either** a
per-task regression **or** an accuracy drop below a floor.

**Done when...** a change that fixes one task and breaks another leaves the
aggregate at exactly 85.0% and the gate still fails, naming the task, the
category, and the offending output; and the message says what CI would do
about it.

??? tip "Hint"

    Three rules make a gate survivable, and skipping any one of them ends
    with the gate switched off:

    - Gate on per-task regressions, not only the aggregate. Improvements and
      regressions cancel in a mean, which is exactly what happens here.
    - Set the tolerance from *measured* variance, not a round number. If
      five reruns of an unchanged system span 8 points, a 2% tolerance
      produces a build that fails at random.
    - Allow deliberate updates, loudly. When the new behaviour is correct,
      re-record the baseline in its own commit with the diff visible in
      review — never lower the threshold.

    ```python
    baseline = {"t01": 1.0, "t04": 1.0, "t09": 0.0}
    now = {"t01": 1.0, "t04": 0.0, "t09": 1.0}
    before = sum(baseline.values()) / len(baseline)
    after = sum(now.values()) / len(now)
    regressions = [t for t in baseline if now[t] < baseline[t]]
    print(f"aggregate {before:.1%} -> {after:.1%}   regressions: {regressions}")
    print("a mean-only gate would have PASSED this change")
    ```

## Reference implementation

Seven labelled regions, matching the seven milestones. The whole thing runs
in under a second and writes two real files, so you can open the dataset and
the baseline and see what a checked-in eval actually looks like.

??? success "Full reference implementation"

    ```python
    """A reusable eval harness: dataset, models, scorers, runner, stats, gate."""
    import json
    import re
    import tempfile
    from dataclasses import asdict, dataclass
    from pathlib import Path

    import numpy as np

    WORKDIR = Path(tempfile.mkdtemp())        # an in-memory scratch directory
    DATASET = WORKDIR / "tasks.jsonl"
    BASELINE_FILE = WORKDIR / "baseline.json"

    # ============================== 1. dataset ================================


    @dataclass(frozen=True)
    class Task:
        """One eval item. `expected` means whatever `scorer` says it means."""
        id: str
        prompt: str
        scorer: str
        expected: str = ""
        tests: tuple = ()          # ((call, expected), ...) for the code scorer
        reference: str = ""        # the frozen answer a judge compares against
        rubric: tuple = ()         # what the judge is told to look for
        category: str = "general"


    TASKS = [
        Task("t01", "What is the capital of France? Answer with the name only.",
             "exact", "Paris", category="knowledge"),
        Task("t02", "What is 2 + 2? Answer with the number only.",
             "exact", "4", category="math"),
        Task("t03", "What is the chemical symbol for gold? Symbol only.",
             "exact", "Au", category="knowledge"),
        Task("t04", "Give the date 14 March 2021 as an ISO date.",
             "regex", r"^\d{4}-\d{2}-\d{2}$", category="format"),
        Task("t05", "Write count_vowels(s) returning the number of vowels.",
             "execution", tests=(("count_vowels('hello')", 2),
                                 ("count_vowels('AEIOU')", 5),
                                 ("count_vowels('')", 0),
                                 ("count_vowels('rhythm')", 0)),
             category="code"),
        Task("t06", "Write second_largest(xs): the second largest DISTINCT "
                    "value, or None.",
             "execution", tests=(("second_largest([1, 5, 3])", 3),
                                 ("second_largest([9, 9, 4])", 4),
                                 ("second_largest([2, 1])", 1),
                                 ("second_largest([4, 4, 4])", None)),
             category="code"),
        Task("t07", "Write chunk(xs, n) splitting a list into lists of length n, "
                    "last one shorter.",
             "execution", tests=(("chunk([1, 2, 3, 4], 2)", [[1, 2], [3, 4]]),
                                 ("chunk([1, 2, 3], 2)", [[1, 2], [3]]),
                                 ("chunk([], 3)", []),
                                 ("chunk([1], 5)", [[1]])),
             category="code"),
        Task("t08", "A customer asks why their refund is delayed. Reply in two "
                    "sentences.",
             "judge",
             reference="Sorry about the wait - your refund is approved and will "
                       "land within 5 business days.",
             rubric=("sorry", "refund", "business days"), category="support"),
        Task("t09", "Summarise the outage in one sentence for the status page.",
             "judge",
             reference="There was an outage and it is now resolved.",
             rubric=("database", "outage", "resolved"), category="support"),
        Task("t10", "Which is the deepest ocean? Answer with the name only.",
             "exact", "Pacific", category="knowledge"),
    ]


    def write_dataset(tasks, path):
        """One JSON object per line: greppable, appendable, diffable in review."""
        with path.open("w", encoding="utf-8") as handle:
            for task in tasks:
                handle.write(json.dumps(asdict(task)) + "\n")
        return path


    def read_dataset(path):
        """Read it back. Tuples come back as lists, so restore them explicitly."""
        tasks = []
        with path.open(encoding="utf-8") as handle:
            for line in handle:
                record = json.loads(line)
                record["tests"] = tuple(tuple(t) for t in record["tests"])
                record["rubric"] = tuple(record["rubric"])
                tasks.append(Task(**record))
        return tasks


    # =============================== 2. models ================================
    @dataclass
    class Completion:
        """What a model call returns, including what it cost you."""
        text: str
        prompt_tokens: int
        completion_tokens: int
        latency_s: float


    class FakeLLM:
        """Deterministic stand-in for a model API: scripted, offline, priced.

        `replies` maps a substring of the prompt to the reply; `outages` lists
        substrings that make the call raise, standing in for a provider error.
        Latency is *computed* from the reply length rather than measured, so the
        numbers are identical on every machine — a real adapter would record a
        wall clock here, which is precisely what would make this untestable.
        """

        def __init__(self, name, replies, outages=(), fallback="I don't know.",
                     usd_per_1k_tokens=0.002, ms_per_token=6.0, overhead_s=0.20):
            self.name, self.replies = name, replies
            self.outages, self.fallback = outages, fallback
            self.usd_per_1k_tokens = usd_per_1k_tokens
            self.ms_per_token, self.overhead_s = ms_per_token, overhead_s

        def complete(self, prompt):
            for marker in self.outages:
                if marker in prompt:
                    raise RuntimeError("503 from upstream provider")
            text = self.fallback
            for marker, reply in self.replies.items():
                if marker in prompt:
                    text = reply
                    break
            completion_tokens = max(1, len(text) // 4)
            return Completion(
                text=text,
                prompt_tokens=max(1, len(prompt) // 4),
                completion_tokens=completion_tokens,
                latency_s=round(self.overhead_s
                                + self.ms_per_token / 1000 * completion_tokens, 3))

        def cost(self, completion):
            tokens = completion.prompt_tokens + completion.completion_tokens
            return tokens / 1000 * self.usd_per_1k_tokens


    STRONG = FakeLLM("strong-1", {
        "capital of France": "Paris",
        "2 + 2": "4",
        "chemical symbol for gold": "Au",
        "ISO date": "2021-03-14",
        "count_vowels": "def count_vowels(s):\n"
                        "    return sum(c in 'aeiouAEIOU' for c in s)",
        "second_largest": "def second_largest(xs):\n"
                          "    d = sorted(set(xs), reverse=True)\n"
                          "    return d[1] if len(d) > 1 else None",
        "chunk(xs, n)": "def chunk(xs, n):\n"
                        "    return [xs[i:i + n] for i in range(0, len(xs), n)]",
        "refund is delayed": "We are sorry for the delay. Your refund is "
                             "approved and will arrive within 5 business days.",
        "outage in one sentence": "The site had an outage earlier today.",
        "deepest ocean": "Pacific",
    })

    WEAK = FakeLLM("weak-1", {
        "capital of France": "  paris.  ",
        "2 + 2": "4",
        "chemical symbol for gold": "Gold's symbol is Au.",
        "ISO date": "March 14, 2021",
        "count_vowels": "def count_vowels(s):\n"
                        "    return sum(c in 'aeiou' for c in s)",
        "second_largest": "def second_largest(xs):\n"
                          "    return sorted(xs)[-2]",
        "chunk(xs, n)": "def chunk(xs, n):\n"
                        "    return [xs[i:i + n] for i in range(len(xs))]",
        "refund is delayed": "Refunds take a while.",
        "outage in one sentence": "The site was down for a bit.",
    }, outages=("deepest ocean",), ms_per_token=11.0)


    # ============================== 3. scorers ================================
    ARTICLES = {"a", "an", "the"}


    def normalise(text):
        """Lower-case, drop punctuation and articles, collapse whitespace.

        The standard short-answer normalisation. It is the difference between
        'Paris' and '  paris.  ' being the same answer — and it deliberately
        does NOT rescue 'The capital of France is Paris.', because a task that
        says "the name only" is also testing instruction following.
        """
        words = re.sub(r"[^\w\s]", " ", text.lower()).split()
        return " ".join(w for w in words if w not in ARTICLES)


    def score_exact(output, task, judge=None):
        return float(normalise(output) == normalise(task.expected))


    def score_regex(output, task, judge=None):
        return float(re.search(task.expected, output.strip()) is not None)


    def score_execution(output, task, judge=None):
        """Run the generated code, then its tests. Partial credit is the point."""
        namespace = {}
        try:
            exec(output, namespace)                  # the model wrote this
        except Exception:
            return 0.0                               # did not even define it
        passed = 0
        for call, expected in task.tests:
            try:
                passed += eval(call, namespace) == expected
            except Exception:                        # a crash is a failed test
                pass
        return passed / len(task.tests)


    class FakeJudge:
        """A stand-in LLM judge whose biases are written down as coefficients.

        A real judge has these same tendencies; the only difference is that here
        you can read them, so every correction below can be measured rather than
        hoped for.
        """
        POSITION = 0.35        # bonus for whichever answer is shown first
        VERBOSITY = 0.004      # bonus per word, regardless of content

        def rubric_hits(self, text, rubric):
            return sum(1.0 for item in rubric if item in text.lower())

        def utility(self, text, rubric, shown_first):
            return (self.rubric_hits(text, rubric)
                    + self.VERBOSITY * len(text.split())
                    + self.POSITION * shown_first)

        def compare(self, first, second, rubric):
            """The judge sees an order, never a label. Returns 'first'/'second'."""
            return ("first" if self.utility(first, rubric, 1)
                    > self.utility(second, rubric, 0) else "second")


    def score_judge(output, task, judge):
        """Pairwise against a frozen reference, judged in BOTH orders.

        Position bias is the most dangerous judge bias because nothing in the
        output looks wrong. Judging each pair twice with the order swapped and
        averaging removes it exactly, and costs one extra call. A pair whose
        winner changes when swapped is a genuine tie, and half a win is the
        right accounting for it.
        """
        wins_when_first = judge.compare(output, task.reference, task.rubric)
        wins_when_second = judge.compare(task.reference, output, task.rubric)
        return 0.5 * ((wins_when_first == "first")
                      + (wins_when_second == "second"))


    def score_judge_single_order(output, task, judge):
        """The version everybody writes first: one call, candidate shown first."""
        return float(judge.compare(output, task.reference, task.rubric) == "first")


    SCORERS = {"exact": score_exact, "regex": score_regex,
               "execution": score_execution, "judge": score_judge}


    # =============================== 4. runner ================================
    @dataclass
    class Result:
        task: Task
        output: str
        score: float
        tokens: int = 0
        latency_s: float = 0.0
        usd: float = 0.0
        error: str = ""

        @property
        def failure(self):
            if self.error:
                return "model error"
            if self.score == 1.0:
                return ""
            if self.score > 0:
                return "partial"
            return "format" if self.task.scorer == "regex" else "wrong"


    def run_eval(model, tasks, judge):
        """One task must never take the suite down with it."""
        results = []
        for task in tasks:
            try:
                completion = model.complete(task.prompt)
                score = SCORERS[task.scorer](completion.text, task, judge)
                results.append(Result(
                    task, completion.text, score,
                    tokens=completion.prompt_tokens + completion.completion_tokens,
                    latency_s=completion.latency_s,
                    usd=model.cost(completion)))
            except Exception as exc:                 # isolation lives here
                results.append(Result(task, "", 0.0,
                                      error=f"{type(exc).__name__}: {exc}"))
        return results


    # =============================== 5. report ================================
    def report(model, results):
        print(f"=== {model.name} " + "=" * (56 - len(model.name)))
        print(f"{'task':<6}{'category':<11}{'scorer':<11}{'score':>6}"
              f"{'tok':>6}{'secs':>7}  note")
        for r in results:
            print(f"{r.task.id:<6}{r.task.category:<11}{r.task.scorer:<11}"
                  f"{r.score:>6.2f}{r.tokens:>6}{r.latency_s:>7.2f}  "
                  f"{r.error or r.failure}")

        n = len(results)
        scores = [r.score for r in results]
        print(f"\naccuracy {sum(scores) / n:>6.1%}   "
              f"strict pass rate {sum(s == 1 for s in scores) / n:>6.1%}   "
              f"({n} tasks)")

        by_category = {}
        for r in results:
            by_category.setdefault(r.task.category, []).append(r.score)
        print("by category  " + "   ".join(
            f"{c} {sum(v) / len(v):.0%}" for c, v in sorted(by_category.items())))

        buckets = {}
        for r in results:
            if r.failure:
                buckets[r.failure] = buckets.get(r.failure, 0) + 1
        print("failures     " + ("   ".join(f"{k} x{v}" for k, v in
                                            sorted(buckets.items())) or "none"))

        wins = [r for r in results if r.score == 1.0]
        total_usd = sum(r.usd for r in results)
        latencies = sorted(r.latency_s for r in results)
        per_success = f"${total_usd / len(wins):.5f}" if wins else "n/a"
        print(f"cost         ${total_usd:.5f} total, "
              f"${total_usd / n:.5f}/task, {per_success}/success")
        print(f"latency      p50 {latencies[len(latencies) // 2]:.2f}s   "
              f"p90 {latencies[int(0.9 * (n - 1))]:.2f}s   "
              f"max {latencies[-1]:.2f}s\n")


    # ========================== 6. statistical honesty ========================
    def boot_ci(values, reps=4000, seed=1, alpha=0.05):
        """Percentile bootstrap: resample TASKS with replacement, re-average."""
        x = np.asarray(values, dtype=float)
        rng = np.random.default_rng(seed)
        index = rng.integers(0, len(x), size=(reps, len(x)))
        means = x[index].mean(axis=1)
        return tuple(np.percentile(means, [100 * alpha / 2,
                                           100 * (1 - alpha / 2)]))


    def compare(name_a, results_a, name_b, results_b):
        """A PAIRED comparison on identical tasks, which is free precision."""
        a = np.array([r.score for r in results_a])
        b = np.array([r.score for r in results_b])
        for name, x in ((name_a, a), (name_b, b)):
            low, high = boot_ci(x)
            print(f"{name:<10} {x.mean():>6.1%}   95% CI [{low:>5.1%},"
                  f" {high:>5.1%}]   width {high - low:>4.0%}")
        difference = b - a
        low, high = boot_ci(difference)
        wins = int((difference > 0).sum())
        losses = int((difference < 0).sum())
        verdict = ("significant" if low > 0 or high < 0
                   else "inside the noise")
        print(f"\npaired difference ({name_b} - {name_a}): "
              f"{difference.mean():+.1%}")
        print(f"95% CI on the difference: [{low:+.1%}, {high:+.1%}]  -> {verdict}")
        print(f"per task: {wins} win / {losses} loss / "
              f"{len(difference) - wins - losses} tie")
        return low > 0 or high < 0


    def judge_calibration(judge, n=120, seed=0):
        """Measure the judge on pairs of EQUAL true quality.

        Both answers in every pair satisfy the rubric equally, so the true win
        rate is exactly 50%. Anything else the judge reports is a bias, and the
        rows below price each one.
        """
        rng = np.random.default_rng(seed)
        rubric = ("alpha", "beta")

        def answer(hits, words):
            return " ".join(list(rubric)[:hits] + ["filler"] * words)

        pairs = []
        for _ in range(n):
            hits = int(rng.integers(0, 3))       # identical rubric coverage
            pairs.append((answer(hits, int(rng.integers(20, 200))),   # candidate
                          answer(hits, int(rng.integers(20, 100))),   # reference
                          answer(hits, 60), answer(hits, 60)))        # matched
        first_only = np.mean([judge.compare(a, b, rubric) == "first"
                              for a, b, _, _ in pairs])
        both = np.array([0.5 * ((judge.compare(a, b, rubric) == "first")
                                + (judge.compare(b, a, rubric) == "second"))
                         for a, b, _, _ in pairs])
        matched = np.mean([0.5 * ((judge.compare(c, d, rubric) == "first")
                                  + (judge.compare(d, c, rubric) == "second"))
                           for _, _, c, d in pairs])
        print(f"   true win rate (equal quality) : {0.5:>6.1%}")
        print(f"   candidate always shown first  : {first_only:>6.1%}"
              f"   <- position bias, 1 call")
        print(f"   both orders, averaged         : {both.mean():>6.1%}"
              f"   <- position removed, 2 calls")
        print(f"   both orders + length-matched  : {matched:>6.1%}"
              f"   <- verbosity removed too")
        print(f"   pairs whose winner flips      : {(both == 0.5).mean():>6.1%}"
              f"   (each one is a genuine tie)")


    # ============================ 7. regression gate ==========================
    def save_baseline(results, path, model_name):
        payload = {"model": model_name,
                   "accuracy": sum(r.score for r in results) / len(results),
                   "per_task": {r.task.id: r.score for r in results}}
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return path


    def gate(baseline_path, results, tolerance=0.0):
        """Fail the build on a per-task regression OR an accuracy drop.

        Gating on the aggregate alone is how a silent breakage ships: one gain
        cancels one regression and the mean never moves.
        """
        baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
        now = {r.task.id: r for r in results}
        accuracy = sum(r.score for r in results) / len(results)
        floor = baseline["accuracy"] - tolerance

        print(f"baseline {baseline['model']}: {baseline['accuracy']:.1%}   "
              f"now: {accuracy:.1%}   floor: {floor:.1%}")
        regressions, gains = [], []
        for task_id, was in baseline["per_task"].items():
            is_now = now[task_id].score
            if is_now < was:
                regressions.append((task_id, was, is_now))
            elif is_now > was:
                gains.append((task_id, was, is_now))
        for label, rows in (("REGRESSED", regressions), ("improved  ", gains)):
            for task_id, was, is_now in rows:
                print(f"  {label} {task_id}  {was:.2f} -> {is_now:.2f}   "
                      f"{now[task_id].task.category}: {now[task_id].output!r}")
        failed = bool(regressions) or accuracy < floor
        if failed:
            reasons = []
            if regressions:
                reasons.append(f"{len(regressions)} task(s) went backwards")
            if accuracy < floor:
                reasons.append(f"accuracy below the {floor:.1%} floor")
            print(f"\nGATE FAILED: {'; '.join(reasons)}.")
            print("In CI this is a non-zero exit code and the deploy stops.")
        else:
            print("\nGATE PASSED")
        return not failed


    # =============================== driver ===================================
    print("1. dataset: write JSONL, then read it back")
    write_dataset(TASKS, DATASET)
    tasks = read_dataset(DATASET)
    print(f"   wrote {DATASET.name} ({DATASET.stat().st_size} bytes), "
          f"read back {len(tasks)} tasks")
    print(f"   round trip is faithful: {tasks == TASKS}")
    print(f"   first line: {DATASET.read_text(encoding='utf-8').splitlines()[0][:88]}...")

    judge = FakeJudge()
    print("\n2. the judge, calibrated before it is trusted")
    judge_calibration(judge)
    print("\n   the same correction on the real judge tasks:")
    print(f"   {'task':<6}{'model':<10}{'single order':>14}{'both orders':>13}")
    for model in (STRONG, WEAK):
        for task in [t for t in tasks if t.scorer == "judge"]:
            text = model.complete(task.prompt).text
            print(f"   {task.id:<6}{model.name:<10}"
                  f"{score_judge_single_order(text, task, judge):>14.2f}"
                  f"{score_judge(text, task, judge):>13.2f}")

    print("\n3. two models, one suite")
    results = {}
    for model in (STRONG, WEAK):
        results[model.name] = run_eval(model, tasks, judge)
        report(model, results[model.name])

    print("4. is the gap real?")
    compare("weak-1", results["weak-1"], "strong-1", results["strong-1"])

    print("\n5. the regression gate")
    save_baseline(results["strong-1"], BASELINE_FILE, "strong-1")
    # A prompt change ships. It teaches the model to name the database in
    # outage summaries — and, unnoticed, changes the date format.
    STRONG_V2 = FakeLLM("strong-2", {**STRONG.replies,
                                     "ISO date": "14/03/2021",
                                     "outage in one sentence":
                                         "A database failover caused a 40 minute "
                                         "outage, and it is now resolved."})
    gate(BASELINE_FILE, run_eval(STRONG_V2, tasks, judge))
    ```

    Four readings that the headline accuracy does not give you.

    **The judge's correction changes a real score.** On `t08` the strong
    model's answer and the frozen reference are of genuinely equal quality;
    judged candidate-first it "wins" 1.00, and judged in both orders it
    lands on 0.50 — a tie, which is the truth. Across 120 equal-quality
    pairs the single-order protocol reports a **100.0%** win rate against a
    true 50.0%; averaging both orders brings it to 66.2%, and matching
    lengths as well brings it to 50.0%. Two of those three numbers would be
    published as an improvement by somebody.

    **Cost per success is the number that decides deployments.** The weak
    model is *cheaper per task* ($0.00004 against $0.00005) and more than
    three times as expensive **per success** ($0.00019 against $0.00006),
    because failures cost money too. Budget by cost-per-success, never by
    cost-per-call.

    **Categories are the cheapest analysis you will ever add.** The strong
    model scores 100% on code, format, knowledge and math, and **25% on
    support** — the open-ended category the judge grades. Ten extra lines,
    and now a regression in one area cannot hide behind a gain in another.

    **One failure bucket is not a model problem.** `weak-1`'s line reads
    `format x1   model error x1   partial x3   wrong x3`, and those four
    buckets have four different remedies: constrain the output format, add a
    retry, improve the model, and check whether the reference is even right.
    `t03` is the interesting one — `"Gold's symbol is Au."` is *correct* and
    scores zero, because the prompt said "symbol only". That is an
    instruction-following failure, and only reading the output tells you so.

## Going further

- **Agent-trajectory metrics.** Score the *shape* of an episode, not just
  its final answer: success rate, median steps to success, tool-error rate,
  and a clean-trajectory rate that only counts runs with no repeated failing
  call and no unauthorised tool. Feed it the JSONL your
  [Project 6 agent](../06-react-agent/README.md) writes, in the schema from
  [32.3](../../ch32-data/03-trajectories.md). A run that succeeds by
  flailing is not the same product as one that succeeds cleanly, and
  [33.2](../../ch33-eval/02-eval-harness.md) shows a suite scoring 66.7%
  success against a 50.0% clean-trajectory rate.
- **A results chart.** Plot per-category accuracy for both models as grouped
  bars, with the bootstrap interval as an error bar on the overall column.
  `matplotlib` is available in these blocks — remember to label the axes and
  not to call `plt.show()`.
- **Full cost and latency columns.** You already record tokens and seconds
  per task. Add p50/p95 columns per *category*, a dollars-per-success column
  per model, and a rule that fails the gate when p95 latency rises more than
  20% — a change that adds two accuracy points and triples the tail latency
  is usually a regression, and only a harness that measures both can say so.
- **Retries with backoff.** The 503 currently scores zero. Retry it three
  times with exponential backoff (simulate the wait — do not actually
  sleep), record the retry count per task, and report a `retries` column.
  Then argue about whether a task that needed three attempts should count as
  a pass.
- **A contamination check.** Add a `sources` field to `Task` and a check
  that fails when a task's exact prompt appears in a training-data file you
  point it at. [33.1](../../ch33-eval/01-benchmarks.md) explains why this
  matters more than almost anything else in the report: a contaminated
  benchmark inflates every number at once, invisibly.
- **Five runs, not one.** Give `FakeLLM` a temperature-like knob that varies
  its reply among a few scripted alternatives, run the whole suite five
  times, and report the mean and the *spread*. Then set your gate tolerance
  from the spread you measured rather than from a round number, which is the
  single change that keeps a gate switched on.
- **Adopt a real harness.** Once you can write these four hundred lines,
  spend a morning with **lm-evaluation-harness** (EleutherAI), **Inspect**
  (UK AI Safety Institute), or **promptfoo**, and port two of your tasks
  into it. You will read their source much faster having built yours, and
  when a number looks wrong you will know where to look.
