# Chapter 32 · Exercises

## The chapter in brief

What you now know, in the order the chapter taught it.

- **At a fixed compute budget the corpus sets the ceiling** — a model cannot
  learn a behaviour nothing demonstrates, it copies the corpus's errors as
  faithfully as its truths, and every token spent on one domain is spent
  nowhere else ([32.1](01-why-data.md)).
- **Training data arrives as four record types** — pretraining text, SFT pairs,
  preference pairs, trajectories — the loss lands on a different part of each,
  and a schema validator run *before* training is what keeps a broken one out.
- **Mixture weights are the cheapest lever you have**, and the epochs column
  tells you which small domain is about to be memorised instead of generalised.
- **Decontamination and PII scrubbing are floors, not guarantees**: n-gram
  overlap catches copying but never paraphrase, and a phone-number regex both
  misses obfuscated formats and shreds innocent order numbers.
- **Synthetic data moves the human from author to inspector**, which is a real
  saving — but the audit, not the generation, is most of the remaining bill
  ([32.2](02-synthetic-data.md)).
- **Self-Instruct's similarity filter is the method rather than an
  optimisation**, and near-duplicate rejection grows from irrelevant to dominant
  as the pool saturates.
- **Evol-Instruct buys difficulty, and its four elimination checks are what stop
  it buying unanswerable garbage** — two of our four eliminations were triggered
  by the length of the parent, not by the operator.
- **Volume is not quality**: measure distinct-$n$ at matched length, and know
  that refitting on your own outputs shrinks spread predictably and kills rare
  categories abruptly and permanently.
- **A trajectory is one attempt at one task plus a verdict the *environment*
  computed**, which is why the environment has to be deterministic, resettable,
  verifiable and graded by difficulty ([32.3](03-trajectories.md)).
- **One trajectory corpus yields three products** — SFT on the successes,
  preference pairs across the same `task_id`, and step-level PRM labels
  estimated by Monte-Carlo rollouts from a prefix.
- **Filters run cheapest-first, and every family has a blind spot the next one
  covers**: exact dedup misses one changed word, MinHash misses a paraphrase, a
  lexical quality model is a topic model in disguise, and only a verifier
  catches a confident, well-formatted, wrong answer ([32.4](04-filtering.md)).
- **Stage removals are not additive**, so the artefacts you ship with a corpus
  are a per-stage funnel report and a dataset card carrying the config hash, the
  seed, and an honest list of what is wrong with it.

### Key terms

| Term | One-clause reminder |
| --- | --- |
| **[synthetic data](../appendix/E-ai-glossary.md#s)** | records written by a model rather than a person, and audited by one |
| **[Self-Instruct and Evol-Instruct](../appendix/E-ai-glossary.md#s)** | bootstrap breadth from a seed pool; rewrite for difficulty |
| **[model collapse](../appendix/E-ai-glossary.md#m)** | what happens when each generation trains only on the last one's output |
| **[trajectory](../appendix/E-ai-glossary.md#t)** | one episode: thought, action, observation, repeated, plus the outcome |
| **[environment](../appendix/E-ai-glossary.md#e)** | the seeded, resettable world an agent acts in and is graded by |
| **[deduplication](../appendix/E-ai-glossary.md#d)** | removing exact and near-identical records before they get memorised |
| **[MinHash and LSH](../appendix/E-ai-glossary.md#m)** | signature-based near-duplicate search that avoids the $O(n^2)$ scan |
| **[contamination](../appendix/E-ai-glossary.md#c)** | eval items that leaked into training, so the benchmark measures recall |
| **funnel report** | the per-stage table of how many records each filter removed ([32.4](04-filtering.md)) |
| **dataset card** | what the data is, how it was built, and what is known to be wrong with it ([32.4](04-filtering.md)) |

Now put all of it to work.

Eight problems on the data pipeline, easiest first. They build on
[32.1](01-why-data.md), [32.2](02-synthetic-data.md), [32.3](03-trajectories.md)
and [32.4](04-filtering.md), and every solution runs in the browser on the
standard library plus numpy. Exercise 32.6 asks you to **predict** the funnel
numbers before running anything — write your four numbers down first, because
the one you get wrong is the lesson.

Nothing here downloads a dataset or calls a model. Every corpus is generated
from a seed you can see, and every verifier is a function you can read.

---

### Exercise 32.1 — Spot the bad records (●)

Here are eight JSONL records from a supplier. Exactly one is usable as-is; each
of the other seven has exactly one problem. Read them, and for each one name the
problem and say which pipeline stage should have caught it.

```text
{"id": "e01", "instruction": "Explain what a stack is.", "output": "A stack removes the most recently added item, which is why it matches the call stack.", "license": "CC-BY-4.0"}
{"id": "e02", "instruction": "Explain what a stack is.", "output": "A stack removes the most recently added item, which is why it matches the call stack.", "license": "CC-BY-4.0"}
{"id": "e03", "instruction": "Summarise the passage.", "output": "", "license": "CC-BY-4.0"}
{"id": "e04", "instruction": "What is 17 * 4?", "output": "17 * 4 = 68.", "license": "unknown"}
{"id": "e05", "instruction": "Contact details?", "output": "Write to ada@example.org or call (608) 555-0142.", "license": "CC-BY-4.0"}
{"id": "e06", "instruction": "What is the average time complexity of a hash table lookup?", "output": "Constant on average.", "license": "CC-BY-4.0"}
{"id": "e07", "instruction": "hi", "output": "Hello! What would you like to know about data structures today?", "license": "CC-BY-4.0"}
{"id": "e08", "instruction": "What is 12 + 5?", "output": "12 + 5 = 18.", "license": "CC-BY-4.0"}
```

Assume the evaluation set you plan to report contains the question *"What is the
average time complexity of a hash table lookup?"*.

??? success "Solution"

    ```python
    import json
    import re

    RAW = """{"id": "e01", "instruction": "Explain what a stack is.", "output": "A stack removes the most recently added item, which is why it matches the call stack.", "license": "CC-BY-4.0"}
    {"id": "e02", "instruction": "Explain what a stack is.", "output": "A stack removes the most recently added item, which is why it matches the call stack.", "license": "CC-BY-4.0"}
    {"id": "e03", "instruction": "Summarise the passage.", "output": "", "license": "CC-BY-4.0"}
    {"id": "e04", "instruction": "What is 17 * 4?", "output": "17 * 4 = 68.", "license": "unknown"}
    {"id": "e05", "instruction": "Contact details?", "output": "Write to ada@example.org or call (608) 555-0142.", "license": "CC-BY-4.0"}
    {"id": "e06", "instruction": "What is the average time complexity of a hash table lookup?", "output": "Constant on average.", "license": "CC-BY-4.0"}
    {"id": "e07", "instruction": "hi", "output": "Hello! What would you like to know about data structures today?", "license": "CC-BY-4.0"}
    {"id": "e08", "instruction": "What is 12 + 5?", "output": "12 + 5 = 18.", "license": "CC-BY-4.0"}"""

    EVAL_SET = ["What is the average time complexity of a hash table lookup?"]
    records = [json.loads(line) for line in RAW.splitlines()]

    def audit(recs):
        seen, problems = {}, {r["id"]: [] for r in recs}
        for r in recs:
            key = (r["instruction"].strip().lower(), r["output"].strip().lower())
            if key in seen:
                problems[r["id"]].append(f"exact duplicate of {seen[key]}")
            seen.setdefault(key, r["id"])
            if not r["output"].strip():
                problems[r["id"]].append("empty output")
            if r["license"] == "unknown":
                problems[r["id"]].append("unknown licence")
            if len(r["instruction"].strip()) < 8:
                problems[r["id"]].append("stub instruction")
            if r["instruction"] in EVAL_SET:
                problems[r["id"]].append("verbatim eval question (contamination)")
            if (re.search(r"[\w.+-]+@[\w-]+\.\w{2,}", r["output"])
                    or re.search(r"\(?\d{3}\)?[-. ]\d{3}[-. ]\d{4}", r["output"])):
                problems[r["id"]].append("contains PII")
            m = re.fullmatch(r"What is (\d+) ([-+*]) (\d+)\?", r["instruction"])
            if m:
                truth = {"+": int(m[1]) + int(m[3]), "*": int(m[1]) * int(m[3]),
                         "-": int(m[1]) - int(m[3])}[m[2]]
                claimed = int(re.findall(r"\d+", r["output"])[-1])
                if claimed != truth:
                    problems[r["id"]].append(f"wrong answer ({claimed} != {truth})")
        return problems

    problems = audit(records)
    for rid, ps in problems.items():
        print(f"{rid}: {'OK' if not ps else '; '.join(ps)}")
    print(f"\nusable: {sum(1 for ps in problems.values() if not ps)} "
          f"of {len(records)}")
    ```

    ```text
    e01: OK
    e02: exact duplicate of e01
    e03: empty output
    e04: unknown licence
    e05: contains PII
    e06: verbatim eval question (contamination)
    e07: stub instruction
    e08: wrong answer (18 != 17)

    usable: 1 of 8
    ```

    Seven records, seven different stages: exact dedup (e02), schema validation
    (e03), the licence check in the schema (e04), the PII scrubber (e05),
    decontamination (e06), heuristics (e07) and verification (e08). That spread
    is the argument for having all of them — no single stage catches more than
    one of these, and the last one, e08, is well-formed, well-licensed, unique
    and simply wrong.

---

### Exercise 32.2 — A filter for a stated failure (●)

Your generator has developed a specific habit: some of its answers **restate the
question instead of answering it**. Write a heuristic filter that catches this,
using nothing but the instruction and the output. Then check it on the eight
labelled examples below and choose a threshold.

The filter must not fire on genuine answers that happen to reuse a couple of
words from the question.

??? success "Solution"

    Measure the fraction of the *answer's* tokens that also appear in the
    question. An answer that restates the question is almost entirely built from
    the question's own words; a real answer introduces new ones.

    ```python
    import re

    def toks(t):
        return re.findall(r"[a-z0-9]+", t.lower())

    def echo_ratio(rec):
        """Fraction of the output's words that already appear in the instruction."""
        q, a = set(toks(rec["instruction"])), toks(rec["output"])
        if not a:
            return 1.0
        return sum(1 for word in a if word in q) / len(a)

    LABELLED = [
     ({"instruction": "Explain why quicksort is fast on average.",
       "output": "Explain why quicksort is fast on average. That is the question."}, True),
     ({"instruction": "Explain why quicksort is fast on average.",
       "output": "Quicksort partitions around a pivot and recurses on both halves, "
                 "so it does about n log n comparisons when the pivots split evenly."}, False),
     ({"instruction": "What is a binary search tree?",
       "output": "A binary search tree is a tree. It is a binary search tree."}, True),
     ({"instruction": "What is a binary search tree?",
       "output": "It keeps smaller keys left and larger keys right, giving log n "
                 "lookup when balanced."}, False),
     ({"instruction": "Describe the queue data structure.",
       "output": "The queue data structure is a data structure, namely a queue."}, True),
     ({"instruction": "Describe the queue data structure.",
       "output": "Items leave in arrival order, so the oldest waiting job is served "
                 "first."}, False),
     ({"instruction": "List two uses of a hash table.",
       "output": "Two uses of a hash table: a hash table is used, and a hash table "
                 "is used."}, True),
     ({"instruction": "List two uses of a hash table.",
       "output": "Counting word frequencies, and testing membership without "
                 "scanning a list."}, False),
    ]

    print(f"{'echo':>6}  {'label':<9} output")
    for rec, is_echo in LABELLED:
        print(f"{echo_ratio(rec):>6.2f}  {'ECHO' if is_echo else 'genuine':<9} "
              f"{rec['output'][:52]!r}")

    print()
    for thr in (0.3, 0.4, 0.5, 0.6, 0.7):
        flagged = [(r, e) for r, e in LABELLED if echo_ratio(r) >= thr]
        tp = sum(1 for _, e in flagged if e)
        fp = len(flagged) - tp
        fn = sum(1 for _, e in LABELLED if e) - tp
        print(f"threshold {thr:.1f}: flagged {len(flagged)}  "
              f"tp={tp} fp={fp} fn={fn}")
    ```

    ```text
      echo  label     output
      0.73  ECHO      'Explain why quicksort is fast on average. That is th'
      0.09  genuine   'Quicksort partitions around a pivot and recurses on '
      0.92  ECHO      'A binary search tree is a tree. It is a binary searc'
      0.00  genuine   'It keeps smaller keys left and larger keys right, gi'
      0.64  ECHO      'The queue data structure is a data structure, namely'
      0.08  genuine   'Items leave in arrival order, so the oldest waiting '
      0.71  ECHO      'Two uses of a hash table: a hash table is used, and '
      0.20  genuine   'Counting word frequencies, and testing membership wi'

    threshold 0.3: flagged 4  tp=4 fp=0 fn=0
    threshold 0.4: flagged 4  tp=4 fp=0 fn=0
    threshold 0.5: flagged 4  tp=4 fp=0 fn=0
    threshold 0.6: flagged 4  tp=4 fp=0 fn=0
    threshold 0.7: flagged 3  tp=3 fp=0 fn=1
    ```

    The two classes separate cleanly: echoes score 0.64–0.92, genuine answers
    0.00–0.20, and any threshold from 0.3 to 0.6 is perfect on this set. Pick
    the middle of the gap — around 0.45 — rather than an edge, so a slightly
    different batch does not immediately break it. Note that the correct answer
    at 0.20 does reuse "hash table" from the question; a threshold of 0.15 would
    have destroyed it, which is exactly the false positive the exercise warned
    about.

---

### Exercise 32.3 — Jaccard by hand, then MinHash (●●)

Take these two sentences:

```text
S1 = "the cat sat on the warm mat"
S2 = "the cat sat on the mat"
```

Using **2-word shingles**, write out both shingle sets by hand and compute the
Jaccard index as an exact fraction. Then verify it with MinHash, and find out
how many hash functions you need before the estimate is trustworthy.

??? success "Solution"

    By hand, the 2-shingles are

    - $A$ = {the cat, cat sat, sat on, on the, the warm, warm mat}, 6 shingles
    - $B$ = {the cat, cat sat, sat on, on the, the mat}, 5 shingles

    They share 4, and the union has 7 distinct shingles, so
    $J = 4/7 \approx 0.5714$.

    ```python
    import re
    import zlib
    import numpy as np

    S1 = "the cat sat on the warm mat"
    S2 = "the cat sat on the mat"

    def shingles(text, k=2):
        w = re.findall(r"[a-z0-9]+", text.lower())
        return {" ".join(w[i:i + k]) for i in range(len(w) - k + 1)}

    A, B = shingles(S1), shingles(S2)
    print("A =", sorted(A))
    print("B =", sorted(B))
    exact = len(A & B) / len(A | B)
    print(f"|A and B| = {len(A & B)}, |A or B| = {len(A | B)}, "
          f"J = {len(A & B)}/{len(A | B)} = {exact:.4f}")

    PRIME = (1 << 31) - 1
    print(f"\n{'hashes':>7}{'estimate':>10}{'error':>9}{'1/sqrt(N)':>11}")
    for N in (16, 64, 256, 1024):
        rng = np.random.default_rng(7)
        a = rng.integers(1, PRIME, N)
        b = rng.integers(0, PRIME, N)

        def signature(s):
            ids = np.array([zlib.crc32(x.encode()) for x in s], dtype=np.int64)
            return ((np.outer(a, ids) + b[:, None]) % PRIME).min(axis=1)

        est = float((signature(A) == signature(B)).mean())
        print(f"{N:>7}{est:>10.4f}{abs(est - exact):>9.4f}{1 / np.sqrt(N):>11.4f}")
    ```

    ```text
    A = ['cat sat', 'on the', 'sat on', 'the cat', 'the warm', 'warm mat']
    B = ['cat sat', 'on the', 'sat on', 'the cat', 'the mat']
    |A and B| = 4, |A or B| = 7, J = 4/7 = 0.5714

     hashes  estimate    error  1/sqrt(N)
         16    0.3750   0.1964     0.2500
         64    0.5781   0.0067     0.1250
        256    0.5391   0.0324     0.0625
       1024    0.5723   0.0008     0.0312
    ```

    The estimator is unbiased but noisy, and the noise shrinks like
    $1/\sqrt{N}$: every observed error sits inside its row's $1/\sqrt{N}$
    column — which is a generous yardstick, since the true standard error is
    $\sqrt{J(1-J)/N}$, at most half of it — and 16 hashes is genuinely useless (0.375 against a true 0.571). The
    errors do not fall monotonically — 256 hashes did worse than 64 here — which
    is what "unbiased with variance" means in practice. You are choosing a
    *distribution* of errors, not a guarantee, so pick $N$ from the error you can
    tolerate: at $N = 126$ (the setting used in [32.4](04-filtering.md)) and
    $J$ near a half, an error around 0.04 is typical, which is fine for a 0.7 drop threshold and
    hopeless for distinguishing 0.68 from 0.72.

---

### Exercise 32.4 — One trajectory, three training formats (●●)

Below are two attempts at the same task: one succeeds, one fails. Produce all
three training artefacts from them — an SFT record, a preference pair, and
step-level labels for a PRM — and say which step in the failing attempt is to
blame.

```text
Goal: What is the total price of two widgets and one gizmo?

tr-a (success)                       tr-b (failure)
  price widget  -> widget: 7           price widget  -> widget: 7
  price gizmo   -> gizmo: 11           calc 3 * 7    -> 21
  calc 2*7+11   -> 25                  final_answer 21
  final_answer 25
```

??? success "Solution"

    ```python
    TASK = "task-042"
    GOAL = "What is the total price of two widgets and one gizmo?"
    SUCCESS = {
        "traj_id": "tr-a", "task_id": TASK, "goal": GOAL, "success": True,
        "steps": [
            ("I need the unit prices first.", "price", "widget", "widget: 7"),
            ("Now the gizmo price.", "price", "gizmo", "gizmo: 11"),
            ("Two widgets and one gizmo: 2*7 + 11.", "calc", "2 * 7 + 11", "25"),
            ("That is the total.", "final_answer", "25", "(episode ends)"),
        ]}
    FAILURE = {
        "traj_id": "tr-b", "task_id": TASK, "goal": GOAL, "success": False,
        "steps": [
            ("I need the unit prices first.", "price", "widget", "widget: 7"),
            ("I will assume the gizmo costs the same.", "calc", "3 * 7", "21"),
            ("That is the total.", "final_answer", "21", "(episode ends)"),
        ]}

    def render(traj, upto=None):
        out = []
        for thought, action, arg, obs in traj["steps"][:upto]:
            out.append(f"Thought: {thought}")
            if action == "final_answer":
                out.append(f"Final Answer: {arg}")
            else:
                out.append(f"Action: {action}\nAction Input: {arg}")
                out.append(f"Observation: {obs}")
        return "\n".join(out)

    SYSTEM = "You are a pricing assistant. Use price and calc, then Final Answer."

    # 1. SFT: the successful trajectory as one assistant turn.
    sft = {"task_id": TASK, "messages": [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": GOAL},
        {"role": "assistant", "content": render(SUCCESS)}]}

    # 2. Preference pair: SAME task, success chosen over failure.
    pref = {"task_id": TASK, "prompt": GOAL,
            "chosen": render(SUCCESS), "rejected": render(FAILURE),
            "source": "outcome-verified", "margin": 1.0}

    # 3. Step labels: is the prefix still consistent with the right answer?
    def prefix_ok(traj, k):
        facts, need = {}, {"widget": 2, "gizmo": 1}
        for thought, action, arg, obs in traj["steps"][:k]:
            if action == "price":
                facts[arg] = int(obs.split(": ")[1])
            if action == "calc":
                if any(item not in facts for item in need):
                    return 0.0                # calculated before looking up
                if int(obs) != sum(facts[i] * n for i, n in need.items()):
                    return 0.0
            if action == "final_answer":
                return 1.0 if arg == "25" else 0.0
        return 1.0

    prm = [{"task_id": TASK, "traj_id": t["traj_id"], "step": k,
            "prefix": render(t, upto=k + 1), "label": prefix_ok(t, k + 1),
            "action": t["steps"][k][1]}
           for t in (SUCCESS, FAILURE) for k in range(len(t["steps"]))]

    print("1) SFT record")
    print(f"   roles  : {[m['role'] for m in sft['messages']]}")
    print(f"   assistant turn: "
          f"{len(sft['messages'][2]['content'].splitlines())} lines")
    print("\n2) preference pair")
    print(f"   keys         : {sorted(pref)}")
    print(f"   chosen ends  : {pref['chosen'].splitlines()[-1]}")
    print(f"   rejected ends: {pref['rejected'].splitlines()[-1]}")
    print("\n3) PRM step records")
    print(f"{'traj':<6}{'step':>5}{'action':>15}{'label':>7}")
    for r in prm:
        print(f"{r['traj_id']:<6}{r['step']:>5}{r['action']:>15}{r['label']:>7.1f}")
    print(f"\nfirst bad step in tr-b: "
          f"{min(r['step'] for r in prm if r['traj_id'] == 'tr-b' and not r['label'])}")
    ```

    ```text
    1) SFT record
       roles  : ['system', 'user', 'assistant']
       assistant turn: 14 lines

    2) preference pair
       keys         : ['chosen', 'margin', 'prompt', 'rejected', 'source', 'task_id']
       chosen ends  : Final Answer: 25
       rejected ends: Final Answer: 21

    3) PRM step records
    traj   step         action  label
    tr-a      0          price    1.0
    tr-a      1          price    1.0
    tr-a      2           calc    1.0
    tr-a      3   final_answer    1.0
    tr-b      0          price    1.0
    tr-b      1           calc    0.0
    tr-b      2   final_answer    0.0

    first bad step in tr-b: 1
    ```

    Step 1 is to blame — the model calculated before it had the gizmo price,
    and everything after inherits the error. This is the whole difference
    between outcome and process supervision
    ([31.4](../ch31-rl/04-reward-models.md)): the outcome label says "tr-b is
    bad", which penalises its correct first step along with everything else,
    while the step labels say *step 0 was fine, step 1 was the mistake*. Also
    notice that the SFT record uses only tr-a while the preference pair needs
    both: failures are not waste, they are the `rejected` side.

---

### Exercise 32.5 — Design a verifiable environment (●●)

Build an environment for the task *"insert exactly N cents into a vending
machine that accepts at most three coins"*. It must have `reset`, `step`,
`is_done` and a `success()` that the environment computes itself, plus a
difficulty knob. Then run a greedy policy across difficulties and read the
success table.

??? success "Solution"

    ```python
    import random

    class VendingEnv:
        """Insert exactly `target` cents, using at most MAX_COINS coins.

        difficulty = how many distinct coin denominations go into the target,
        so higher difficulty needs more coins and strains the three-coin limit.
        """
        COINS = (1, 5, 10, 25)
        MAX_COINS = 3
        MAX_STEPS = 12

        def __init__(self, seed, difficulty):
            self.seed, self.difficulty = seed, difficulty
            self.reset()

        def reset(self):
            rng = random.Random(100 * self.difficulty + self.seed)
            kinds = rng.sample(self.COINS, self.difficulty)
            self.target = sum(c * rng.randint(1, 3) for c in kinds)
            self.inserted, self.n_steps, self.bought = [], 0, False
            return self.goal()

        def goal(self):
            return (f"Insert exactly {self.target} cents using coins "
                    f"{self.COINS}, at most {self.MAX_COINS} of them.")

        def step(self, action, arg=""):
            self.n_steps += 1
            if action == "insert":
                coin = int(arg)
                if coin not in self.COINS:
                    return f"ERROR: no {coin}c coin"
                if len(self.inserted) >= self.MAX_COINS:
                    return f"ERROR: the machine holds only {self.MAX_COINS} coins"
                self.inserted.append(coin)
                return f"inserted {coin}c, total now {sum(self.inserted)}c"
            if action == "buy":
                self.bought = True
                return (f"machine reports {sum(self.inserted)}c "
                        f"against {self.target}c")
            return f"ERROR: unknown action {action!r}"

        def is_done(self):
            return self.bought or self.n_steps >= self.MAX_STEPS

        def success(self):
            """Verifiable: the environment knows the target and counts the coins."""
            return (self.bought
                    and sum(self.inserted) == self.target
                    and len(self.inserted) <= self.MAX_COINS)

    def greedy(env):
        """Insert the largest coin that still fits, then buy."""
        env.reset()
        trace = []
        while not env.is_done():
            remaining = env.target - sum(env.inserted)
            if remaining <= 0 or len(env.inserted) >= env.MAX_COINS:
                trace.append(("buy", "", env.step("buy")))
                break
            coin = max(c for c in env.COINS if c <= remaining)
            trace.append(("insert", str(coin), env.step("insert", str(coin))))
        return trace

    env = VendingEnv(3, 3)
    print(env.goal())
    for action, arg, obs in greedy(env):
        print(f"   {action} {arg:<3} -> {obs}")
    print(f"is_done={env.is_done()}  success={env.success()}")
    print(f"same seed rebuilds the same task: {VendingEnv(3, 3).target == env.target}")

    print(f"\n{'difficulty':>11}{'n':>5}{'success':>10}{'mean coins':>12}")
    for d in (1, 2, 3, 4):
        runs = [VendingEnv(s, d) for s in range(30)]
        for e in runs:
            greedy(e)
        print(f"{d:>11}{len(runs):>5}"
              f"{sum(e.success() for e in runs) / len(runs):>10.0%}"
              f"{sum(len(e.inserted) for e in runs) / len(runs):>12.1f}")
    ```

    ```text
    Insert exactly 106 cents using coins (1, 5, 10, 25), at most 3 of them.
       insert 25  -> inserted 25c, total now 25c
       insert 25  -> inserted 25c, total now 50c
       insert 25  -> inserted 25c, total now 75c
       buy     -> machine reports 75c against 106c
    is_done=True  success=False
    same seed rebuilds the same task: True

     difficulty    n   success  mean coins
              1   30      100%         1.7
              2   30       53%         2.7
              3   30       30%         3.0
              4   30        0%         3.0
    ```

    All four required properties are present: seeded and deterministic
    (`VendingEnv(3, 3)` twice gives the same target), resettable, verified by
    the environment against a number it computed, and graded by a knob that
    changes the amount of work required rather than just a label. The success
    column falls 100% → 53% → 30% → 0%, which is a usable difficulty ladder: the
    two middle rows are where collection is worth doing, because difficulty 1 is
    solved every time and teaches nothing about what to do differently, while
    difficulty 4 produces no successes to learn from at all. The greedy policy
    is genuinely bad here — grabbing the largest coin first burns the three-coin
    budget, which is why the 106c example runs out of coins at 75c — and that is
    exactly the kind of failure you want a corpus of.

---

### Exercise 32.6 — Predict the funnel (●●)

A corpus of **60** records is assembled like this:

- 40 unique, correct arithmetic records;
- 6 unique records with a **wrong** answer;
- 8 records whose output is fewer than five words (of these 8, four form two
  identical pairs);
- 6 records that are exact copies of records already in the 40.

The pipeline runs three stages in this order: heuristics (drop outputs under
five words), exact deduplication, verification (recompute the arithmetic).

**Predict the four numbers** — input, after heuristics, after dedup, after
verification — and write them down before running the block.

??? success "Solution"

    The trap is the interaction. Four of the short records are duplicates of
    each other, and it is tempting to count them twice: once in the heuristic
    stage and once in the dedup stage. They are gone after the first stage, so
    dedup only ever sees the 6 copies of good records. The answer is
    **60 → 52 → 46 → 40**.

    ```python
    import hashlib
    import re

    PAIRS = [(3, 4), (5, 6), (7, 8), (9, 10), (11, 12), (13, 14), (15, 16),
             (17, 18), (19, 20), (21, 22), (23, 24), (25, 26), (27, 28),
             (29, 30), (31, 32), (33, 34), (35, 36), (37, 38), (39, 40),
             (41, 42), (43, 44), (45, 46), (47, 48), (49, 50), (51, 52),
             (53, 54), (55, 56), (57, 58), (59, 60), (61, 62), (63, 64),
             (65, 66), (67, 68), (69, 70), (71, 72), (73, 74), (75, 76),
             (77, 78), (79, 80), (81, 82)]
    GOOD = [{"id": f"g{i:02d}", "instruction": f"What is {a} + {b}?",
             "output": f"Adding {a} and {b} step by step gives {a + b} in total."}
            for i, (a, b) in enumerate(PAIRS)]
    WRONG = [{"id": f"w{i:02d}", "instruction": f"What is {a} + {b}?",
              "output": f"Adding {a} and {b} step by step gives {a + b + 1} in total."}
             for i, (a, b) in enumerate([(2, 2), (4, 4), (6, 6), (8, 8),
                                         (10, 10), (12, 12)])]
    SHORT = [{"id": f"s{i:02d}", "instruction": "What is 1 + 1?", "output": o}
             for i, o in enumerate(["", "2", "Two.", "It is 2.", "2.", "Yes.",
                                    "2", "Two."])]
    DUPES = [{**GOOD[i], "id": f"d{i:02d}"} for i in range(6)]
    CORPUS = GOOD + WRONG + SHORT + DUPES

    def too_short(r):
        return len(r["output"].split()) < 5

    def fingerprint(r):
        text = re.sub(r"\s+", " ",
                      (r["instruction"] + "|" + r["output"]).lower()).strip()
        return hashlib.blake2b(text.encode(), digest_size=8).hexdigest()

    def verified(r):
        m = re.fullmatch(r"What is (\d+) \+ (\d+)\?", r["instruction"])
        nums = re.findall(r"\d+", r["output"])
        return bool(m and nums) and int(nums[-1]) == int(m[1]) + int(m[2])

    s1 = [r for r in CORPUS if not too_short(r)]
    seen, s2 = set(), []
    for r in s1:
        if fingerprint(r) in seen:
            continue
        seen.add(fingerprint(r))
        s2.append(r)
    s3 = [r for r in s2 if verified(r)]

    print(f"{'stage':<22}{'kept':>6}{'removed':>9}")
    prev = None
    for name, stage in [("input", CORPUS), ("after heuristics", s1),
                        ("after exact dedup", s2), ("after verification", s3)]:
        removed = "" if prev is None else f"{prev - len(stage):>9}"
        print(f"{name:<22}{len(stage):>6}{removed}")
        prev = len(stage)

    dup_shorts = sum(1 for r in SHORT
                     if sum(1 for x in SHORT
                            if fingerprint(x) == fingerprint(r)) > 1)
    print(f"\nshort records that were ALSO duplicates: {dup_shorts}")
    print("they were removed once, by the first stage that saw them")
    ```

    ```text
    stage                   kept  removed
    input                     60
    after heuristics          52        8
    after exact dedup         46        6
    after verification        40        6

    short records that were ALSO duplicates: 4
    they were removed once, by the first stage that saw them
    ```

    If you predicted 44 after dedup you double-counted the four short
    duplicates. This is why a funnel report is per-stage rather than a list of
    defect counts: **stage removals are not additive**, because each stage only
    ever sees what survived the last one. It is also why the order matters. Put
    dedup first and it removes 8 (6 good copies plus 2 short duplicates), the
    heuristics then remove 6, and the final count is identical — the same 40 —
    but the intermediate numbers, and therefore your diagnosis of what is wrong
    with the corpus, would be different.

---

### Exercise 32.7 — Catch the contaminated record (●●)

Your evaluation set contains one classic puzzle. Five candidate training records
are below. Run n-gram overlap decontamination at $n = 8$ and again at $n = 5$,
and say which records are caught at each setting — and which one leaks and is
never caught at all.

```text
eval: "A ball and a bat cost one dollar and ten cents in total.
       The bat costs one dollar more than the ball. How much is the ball?"
```

??? success "Solution"

    ```python
    import re

    def ngrams(text, n):
        w = re.findall(r"[a-z0-9]+", text.lower())
        return {tuple(w[i:i + n]) for i in range(len(w) - n + 1)}

    EVAL = ["A ball and a bat cost one dollar and ten cents in total. "
            "The bat costs one dollar more than the ball. How much is the ball?"]

    TRAIN = {
     "verbatim":
        "A ball and a bat cost one dollar and ten cents in total. The bat "
        "costs one dollar more than the ball. How much is the ball?",
     "one sentence copied":
        "A ball and a bat cost one dollar and ten cents in total. Work out "
        "both prices.",
     "reworded":
        "Together a bat and a ball come to 1.10. The bat is a dollar dearer "
        "than the ball. Price the ball.",
     "numbers changed":
        "A ball and a bat cost two dollars and twenty cents in total. The bat "
        "costs two dollars more than the ball. How much is the ball?",
     "unrelated":
        "Two trains leave stations 300 km apart travelling towards each other "
        "at 60 and 90 km/h.",
    }

    for n in (8, 5):
        grams = set().union(*(ngrams(q, n) for q in EVAL))
        print(f"n = {n}  ({len(grams)} eval n-grams)")
        for name, text in TRAIN.items():
            hit = len(ngrams(text, n) & grams)
            print(f"   {name:<22}{hit:>4} shared   "
                  f"{'FLAG' if hit else 'pass'}")
        print()
    ```

    ```text
    n = 8  (20 eval n-grams)
       verbatim                20 shared   FLAG
       one sentence copied      6 shared   FLAG
       reworded                 0 shared   pass
       numbers changed          2 shared   FLAG
       unrelated                0 shared   pass

    n = 5  (23 eval n-grams)
       verbatim                23 shared   FLAG
       one sentence copied      9 shared   FLAG
       reworded                 0 shared   pass
       numbers changed          9 shared   FLAG
       unrelated                0 shared   pass
    ```

    The record that leaks and is never caught is **"reworded"**. It is the same
    puzzle with the same answer and shares zero $n$-grams at either setting,
    because every content word was replaced. Training on it teaches the model
    the answer to an eval question, and n-gram overlap cannot see it — the
    limitation [32.1](01-why-data.md) warned about and
    [32.4](04-filtering.md) could only partly fix with MinHash, which also works
    on word overlap.

    Two subtler points. Lowering $n$ from 8 to 5 raised every hit count but
    changed no verdict here, and on a large corpus it would start flagging
    innocent records that share a common five-word phrase — strictness costs
    recall of good data. And "numbers changed" is flagged at both settings,
    which is arguably *correct* rather than a false positive: it is the same
    problem with different constants, and a model that memorises the solution
    method still gains an unfair advantage. Decide deliberately which of those
    two you consider contamination, and write the decision in the dataset card.

---

### Exercise 32.8 — Invent an Evol-Instruct operator, and defend it (●●●)

Write a **new** in-depth evolving operator for Evol-Instruct — one not in
[32.2](02-synthetic-data.md) — apply it to a seed set, run it through the
elimination checks, and then defend it with measurements. "It looks harder" is
not a defence. Show what the operator changed about the *instructions* and what
it changed about the *responses*.

??? success "Solution"

    The operator below is **add-counterexample**: it demands not just a solution
    but an input on which a naive solution fails. That is a genuine step up in
    difficulty, because producing it requires the model to reason about the
    space of wrong answers rather than just the right one.

    ```python
    import re

    SEEDS = [
        "Write a Python function that reverses a string.",
        "Write a Python function that sums a list of numbers.",
        "Write a Python function that checks whether a word is a palindrome.",
        "Write a Python function that removes duplicates from a list.",
        "Explain what a hash table is.",
        "Say hello.",
    ]

    def add_counterexample(instr):
        """NEW OPERATOR: demand an input on which a naive solution fails.

        It refuses to apply where there is no implementation to break, and
        returns the input unchanged so `eliminate` discards the attempt.
        """
        if not instr.rstrip().endswith(".") or "function" not in instr.lower():
            return instr
        return (instr.rstrip(".") +
                ", and give one input on which a naive one-line solution "
                "returns the wrong answer.")

    def respond(instr):
        """Deterministic stand-in for the responder model."""
        low = instr.lower()
        if "wrong answer" in low:
            if "reverses a string" in low:
                return ("def solve(s): return s[::-1]. A naive sorted(s) "
                        "fails on 'abc'.")
            if "sums a list" in low:
                return ("def solve(xs): return sum(xs). A naive max(xs) "
                        "fails on [1, 2, 3].")
            if "palindrome" in low:
                return ("def solve(w): return w == w[::-1]. A naive "
                        "len(w) % 2 check fails on 'abba'.")
            if "removes duplicates" in low:
                return ("def solve(xs): return sorted(set(xs)). A naive "
                        "xs.remove call fails on [2, 2, 2].")
            return "Sorry, I cannot construct a counterexample for that."
        return "Here is a straightforward answer."

    def eliminate(parent, child, answer):
        if child.strip() == parent.strip():
            return "no information gain over the parent"
        if "sorry" in answer.lower() or "cannot" in answer.lower():
            return "the model could not answer it"
        if len(re.findall(r"[a-z0-9]+", answer.lower())) <= 3:
            return "answer is empty or stop words only"
        return None

    def constraints(instr):
        """Difficulty proxy: how many separate requirements are stated."""
        return instr.count(",") + instr.lower().count(" and ")

    kept, killed = [], []
    print(f"{'seed':<68}fate")
    for seed in SEEDS:
        child = add_counterexample(seed)
        answer = respond(child)
        why = eliminate(seed, child, answer)
        print(f"{seed:<68}{'ELIMINATED: ' + why if why else 'kept'}")
        (killed if why else kept).append((seed, child, answer))

    print(f"\nkept {len(kept)} of {len(SEEDS)}")
    print(f"mean constraints per instruction : "
          f"seed {sum(constraints(s) for s in SEEDS) / len(SEEDS):.2f}"
          f"  ->  evolved {sum(constraints(c) for _, c, _ in kept) / len(kept):.2f}")
    print(f"mean words per response         : "
          f"seed {sum(len(respond(s).split()) for s in SEEDS) / len(SEEDS):.1f}"
          f"  ->  evolved {sum(len(a.split()) for _, _, a in kept) / len(kept):.1f}")
    print(f"responses naming a failing input: "
          f"{sum('fails on' in a for _, _, a in kept)}/{len(kept)}")
    print(f"\nexample evolved instruction:\n   {kept[0][1]}")
    print(f"example evolved response:\n   {kept[0][2]}")
    ```

    ```text
    seed                                                                fate
    Write a Python function that reverses a string.                     kept
    Write a Python function that sums a list of numbers.                kept
    Write a Python function that checks whether a word is a palindrome. kept
    Write a Python function that removes duplicates from a list.        kept
    Explain what a hash table is.                                       ELIMINATED: no information gain over the parent
    Say hello.                                                          ELIMINATED: no information gain over the parent

    kept 4 of 6
    mean constraints per instruction : seed 0.00  ->  evolved 2.00
    mean words per response         : seed 5.0  ->  evolved 12.5
    responses naming a failing input: 4/4

    example evolved instruction:
       Write a Python function that reverses a string, and give one input on which a naive one-line solution returns the wrong answer.
    example evolved response:
       def solve(s): return s[::-1]. A naive sorted(s) fails on 'abc'.
    ```

    **The defence, in three measurements.**

    *The instructions really are more demanding.* Constraints per instruction
    went from 0.00 to 2.00 — every evolved instruction now states two separate
    requirements where the seed stated one. That is a structural change, not a
    rewording.

    *The responses carry more information.* Mean response length went from 5.0
    words to 12.5, and — the part that matters more than length — 4 of 4
    responses name a specific failing input. A model trained on these sees
    worked *contrasts* between a correct and an incorrect approach, which the
    seed corpus never contained.

    *The operator knows when not to fire.* It declined on "Explain what a hash
    table is" and "Say hello" because neither asks for an implementation, and
    the elimination check turned those non-applications into discards rather
    than into duplicate records with new ids. An operator that silently returns
    its input is how a corpus fills with near-duplicates
    ([32.4](04-filtering.md) would then have to delete them), so refusing
    loudly is a feature.

    **What would falsify the defence.** Two checks this block does not run:
    whether the counterexamples are *correct* (a plausible-looking but wrong
    counterexample is worse than none, and needs a verifier — run the naive
    solution on the claimed input and confirm it really fails), and whether
    student models trained on the evolved set actually do better on held-out
    tasks. Difficulty is a proxy for value, never a substitute for measuring it.
