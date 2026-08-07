# 32.4 Filtering, dedup, and verification

Everything so far has produced records. This section throws most of them away.
That is not a failure of the earlier stages — it is the job. A filtering
pipeline is a sequence of stages, each cheaper than the next is expensive, each
one measurable, and the artefact you ship at the end is not just the data but a
**funnel report** saying how many records each stage removed and why. Build it
in that order and you can answer the only question that matters when quality
drops: *which stage changed?* This section builds the whole thing on one corpus,
end to end, and prints the funnel.

## One corpus, with the defects put in on purpose

Everything below runs on the same 1,200-record synthetic instruction corpus.
It is generated with defects injected at known rates — duplicates, junk,
padding, wrong answers, benchmark leakage — so that every filter can be scored
against ground truth instead of admired. Three domains, because the strength of
your verifier depends entirely on the domain: `math` and `code` can be checked
mechanically, `prose` cannot.

```python
import random
import re
from collections import Counter

MATH_OPS = [("+", lambda a, b: a + b), ("*", lambda a, b: a * b),
            ("-", lambda a, b: a - b)]

CODE_FAMILIES = [                    # parameterised, so k gives real variety
    ("multiplies its argument by {k}",
     "def solve(x):\n    return x * {k}",
     "def solve(x):\n    return x + {k}",
     "# The argument is scaled, so the result grows linearly with the input.",
     "assert solve(3) == 3 * {k}"),
    ("reports whether its argument is divisible by {k}",
     "def solve(x):\n    return x % {k} == 0",
     "def solve(x):\n    return x % {k}",
     "# The remainder is compared with zero and a boolean comes back.",
     "assert solve({k}) is True and solve({k} + 1) is False"),
    ("adds {k} to every item of a list",
     "def solve(xs):\n    return [x + {k} for x in xs]",
     "def solve(xs):\n    return [x * {k} for x in xs]",
     "# A list comprehension builds a new list without touching the old one.",
     "assert solve([1, 2]) == [1 + {k}, 2 + {k}]"),
    ("repeats a string {k} times",
     "def solve(s):\n    return s * {k}",
     "def solve(s):\n    return s + str({k})",
     "# Multiplying a string concatenates that many copies of it.",
     "assert solve('ab') == 'ab' * {k}"),
]
CODE_ASKS = ["Write a Python function solve that {t}.",
             "Implement a function solve that {t}.",
             "In Python, define solve so that it {t}."]

PROSE = [
    ("a hash table", "maps keys to array slots through a hash function",
     "so an average lookup touches one slot instead of scanning"),
    ("a linked list", "chains nodes together by reference",
     "so inserting at the front costs constant time"),
    ("a binary search tree", "keeps smaller keys left and larger keys right",
     "so a balanced tree finds any key in about log n comparisons"),
    ("a queue", "removes items in the order they arrived",
     "so waiting jobs are served fairly"),
    ("a stack", "removes the item that was added most recently",
     "so it matches the call stack a program already uses"),
    ("a heap", "keeps the smallest key at the root of a complete tree",
     "so the minimum is available in constant time"),
    ("a set", "stores each value at most once and tests membership by hashing",
     "so duplicate checking costs constant time on average"),
    ("a trie", "stores strings character by character down a shared path",
     "so a prefix search only walks the prefix"),
]
ASKS = ["Explain what {t} is.", "In your own words, what is {t}?",
        "Describe {t} for someone new to programming."]
CLOSERS = ["That is the whole idea in one sentence.",
           "The cost only changes when the structure degenerates.",
           "It is worth drawing once on paper.",
           "Everything else follows from that one property.",
           "Compare it with an array before you decide."]

JUNK = [                                   # one per heuristic we will write
    "It is.",                                                  # too short
    "Sorting arranges items in order. " * 46,                  # too long
    "E = 1/2*m*v^2 ;; %%% [[ref]] <<<>>> $$$ @@@ ### %%%",      # symbol soup
    "Step 1: open it.\nStep 1: open it.\nStep 1: open it.\n"
    "Step 1: open it.\nThat is all there is to say here.",       # repeated line
    "answer answer answer answer answer answer answer answer "
    "answer answer answer answer.",                            # word soup
    "As an AI language model I cannot help with that, but click here.",
    "Binary search halves the interval each step, so it needs about "
    "log2(n) comparisons provided the input is",               # truncated
]
THIN = ["This is an important topic in computer science and many people ask "
        "about it. It is useful to know.",
        "That is a very good question and the answer is quite interesting to "
        "think about in general.",
        "There are many things you could say here, and they are all worth "
        "knowing about if you want to.",
        "It really depends on what you want, so there is no one answer that "
        "will be right for everybody."]
EVAL_SET = [
    "What is the average time complexity of a hash table lookup?",
    "Explain why quicksort degrades to quadratic time on sorted input.",
    "What does the modulo operator return for negative operands in Python?",
]

CONFIG = {"n": 1200, "seed": 11, "p_exact_dup": 0.05, "p_junk": 0.06,
          "p_thin": 0.07, "p_wrong": 0.15, "p_rephrase": 0.15,
          "p_contaminated": 0.04, "p_stub_instruction": 0.02}

def make_corpus(cfg=CONFIG):
    """A synthetic instruction corpus with defects injected on purpose."""
    rng = random.Random(cfg["seed"])
    recs, pool = [], []
    for i in range(cfg["n"]):
        rid = f"c{i:04d}"
        if rng.random() < cfg["p_exact_dup"] and pool:      # byte-for-byte copy
            src = rng.choice(pool)
            recs.append({**src, "id": rid, "source": f"dup-of-{src['id']}"})
            continue
        domain = rng.choice(["math", "code", "prose"])
        difficulty = rng.choice([1, 2, 3])
        test = ""
        if domain == "math":
            a, b = rng.randint(2, 60), rng.randint(2, 60)
            op, fn = MATH_OPS[rng.randrange(3)]
            instr = f"Compute the value of {a} {op} {b} and show your working."
            ans = fn(a, b)
            if rng.random() < cfg["p_wrong"]:
                ans += rng.choice([-2, -1, 1, 2])
            out = (f"Working it through step by step, {a} {op} {b} = {ans}, "
                   f"so the result is {ans}.")
        elif domain == "code":
            task, good, bad, note, check = CODE_FAMILIES[rng.randrange(4)]
            k = rng.randint(2, 12)
            instr = CODE_ASKS[rng.randrange(3)].format(t=task.format(k=k))
            body = bad if rng.random() < cfg["p_wrong"] else good
            out = f"{body.format(k=k)}\n{note}"
            test = check.format(k=k)          # shipped with the record
        else:
            topic, verb, why = PROSE[rng.randrange(len(PROSE))]
            instr = ASKS[rng.randrange(len(ASKS))].format(t=topic)
            out = (f"{topic.capitalize()} {verb}, {why}. "
                   f"{CLOSERS[rng.randrange(len(CLOSERS))]}")
            if rng.random() < cfg["p_rephrase"]:            # near-duplicate
                out = out.replace(", so ", ". That means ").replace(" the ", " a ")
        low = False
        if rng.random() < cfg["p_junk"]:
            out, low = rng.choice(JUNK), True
        elif rng.random() < cfg["p_thin"]:
            out, low = rng.choice(THIN), True
        if rng.random() < cfg["p_stub_instruction"]:
            instr, low = rng.choice(["Hi", "?", "explain"]), True
        if rng.random() < cfg["p_contaminated"]:
            instr = rng.choice(EVAL_SET)                    # benchmark leakage
        recs.append({"id": rid, "instruction": instr, "output": out,
                     "domain": domain, "difficulty": difficulty,
                     "source": "synth-v1", "low_quality": low, "test": test})
        pool.append(recs[-1])
    return recs

CORPUS = make_corpus()
print(f"corpus: {len(CORPUS)} records")
print(f"  by domain     : {dict(Counter(r['domain'] for r in CORPUS))}")
print(f"  by difficulty : {dict(Counter(r['difficulty'] for r in CORPUS))}")
print(f"  exact copies  : {sum(1 for r in CORPUS if r['source'].startswith('dup-'))}")
print(f"  low quality   : {sum(r['low_quality'] for r in CORPUS)}")
print(f"  eval leakage  : {sum(1 for r in CORPUS if r['instruction'] in EVAL_SET)}")
```

```text
corpus: 1200 records
  by domain     : {'prose': 402, 'math': 401, 'code': 397}
  by difficulty : {2: 399, 1: 412, 3: 389}
  exact copies  : 66
  low quality   : 188
  eval leakage  : 43
```

Note the `test` field on code records. Verifiable datasets ship their checks
alongside the data — HumanEval pairs every prompt with unit tests, and that is
the whole reason it can be scored automatically. Building that in from the start
is much cheaper than retrofitting it.

## Heuristic filters: cheap, blunt, and first

Heuristics run in microseconds per record and remove the obviously broken. They
go first for that reason alone: everything downstream is more expensive, so
every record a heuristic kills is money saved. The design rule is that each
filter is **one named predicate** returning True when the record is bad, so the
rejection reason is recorded rather than inferred.

```python
# continues
FILTERS = {}

def rule(name):
    """Register a predicate under a human-readable rejection reason."""
    def wrap(fn):
        FILTERS[name] = fn
        return fn
    return wrap

@rule("too short")
def _(r): return len(r["output"].split()) < 8

@rule("too long")
def _(r): return len(r["output"].split()) > 150

@rule("stub instruction")
def _(r): return len(r["instruction"].strip()) < 12

@rule("low alpha ratio")
def _(r):
    t = r["output"]
    return sum(c.isalpha() or c.isspace() for c in t) / max(len(t), 1) < 0.60

@rule("repeated line")
def _(r):
    lines = [x.strip() for x in r["output"].splitlines() if x.strip()]
    return len(lines) > 2 and len(set(lines)) / len(lines) < 0.5

@rule("word soup")
def _(r):
    w = r["output"].lower().split()
    return len(w) > 10 and len(set(w)) / len(w) < 0.35

@rule("boilerplate")
def _(r):
    return any(p in r["output"].lower() for p in
               ("as an ai language model", "click here", "lorem ipsum", "n/a"))

@rule("no terminal punctuation")
def _(r):
    return not r["output"].rstrip().endswith((".", "!", "?", '"', ")", ":", "`"))

def screen(rec):
    """Return the FIRST reason this record fails, or None if it is clean."""
    for name, fn in FILTERS.items():
        if fn(rec):
            return name
    return None

hist = Counter(screen(r) or "KEPT" for r in CORPUS)
after_heuristics = [r for r in CORPUS if screen(r) is None]

print(f"{'reason':<24}{'count':>6}  histogram")
for name in FILTERS:
    print(f"{name:<24}{hist[name]:>6}  {'#' * round(hist[name] / 2)}")
print(f"{'KEPT':<24}{hist['KEPT']:>6}")

caught = sum(1 for r in CORPUS if r["low_quality"] and screen(r))
falsepos = sum(1 for r in CORPUS if not r["low_quality"] and screen(r))
print(f"\nkept {len(after_heuristics)}/{len(CORPUS)} "
      f"({len(after_heuristics) / len(CORPUS):.0%})")
print(f"low-quality records caught: {caught} of "
      f"{sum(r['low_quality'] for r in CORPUS)}; false positives: {falsepos}")
```

```text
reason                   count  histogram
too short                   17  ########
too long                    15  ########
stub instruction            12  ######
low alpha ratio              8  ####
repeated line               15  ########
word soup                   16  ########
boilerplate                 10  #####
no terminal punctuation     15  ########
KEPT                      1092

kept 1092/1200 (91%)
low-quality records caught: 108 of 188; false positives: 0
```

The histogram is the point of the whole design. It is a **live specification of
what your corpus is doing wrong**, and it is how you notice that a supplier
changed something: a rejection reason that jumps from 15 to 900 overnight tells
you exactly where to look. Log it per batch, forever.

Read the last line carefully, because it says two different things. Zero false
positives — no genuinely good record was killed — which means these thresholds
are safely conservative. But only 108 of the 188 low-quality records were
caught. The other 80 are the *thin* ones: grammatical, correctly punctuated,
long enough, and empty of content. No cheap predicate catches those, which is
precisely why the quality-model stage exists further down.

!!! warning "Tune every threshold on your own data, and look at what dies"

    `< 8 words` is wrong for a corpus of one-line SQL answers and wrong again
    for a corpus of essays. Before shipping a filter, print twenty records it
    rejects and read them. A filter you have not read the output of is a filter
    you do not know the behaviour of.

## Exact duplicates: hashing, and what "exact" means

Exact deduplication is a hash-set membership test — the structure of
[Section 36.1](../ch36-hashing-tries/01-hash-tables.md) doing the job it is best
at. The only real decision is what you hash. Raw bytes miss a copy that differs
by a trailing newline; so the pipeline **canonicalises** first (lowercase,
collapse whitespace) and hashes that.

We use `blake2b` rather than Python's built-in `hash()` for one important
reason: `hash()` on strings is randomised per process, so the same corpus
deduplicated on two machines would give different results. A cryptographic
digest is stable across machines, runs and Python versions.

```python
# continues
import hashlib

def canonical(rec):
    """The comparison form: case-folded, whitespace-collapsed."""
    text = rec["instruction"] + " ||| " + rec["output"]
    return re.sub(r"\s+", " ", text.lower()).strip()

def fingerprint(rec):
    return hashlib.blake2b(canonical(rec).encode("utf-8"),
                           digest_size=16).hexdigest()

seen, after_exact, groups = {}, [], Counter()
for r in after_heuristics:
    fp = fingerprint(r)
    groups[fp] += 1
    if fp in seen:
        continue                       # already have this exact text
    seen[fp] = r["id"]
    after_exact.append(r)

print(f"in {len(after_heuristics)} -> out {len(after_exact)} "
      f"(removed {len(after_heuristics) - len(after_exact)})")
print("largest duplicate clusters:")
for fp, c in groups.most_common(3):
    print(f"  {c:>3} copies  fp={fp[:12]}  first id={seen[fp]}")
print(f"records appearing more than once: "
      f"{sum(1 for c in groups.values() if c > 1)} distinct texts")
```

```text
in 1092 -> out 715 (removed 377)
largest duplicate clusters:
    7 copies  fp=4eee89db5d25  first id=c0051
    7 copies  fp=fdc33cc73188  first id=c0089
    6 copies  fp=77be1467f3ce  first id=c0004
records appearing more than once: 197 distinct texts
```

Thirty-five percent of the surviving corpus was a byte-for-byte repeat, and only
5% of it was injected as a deliberate copy. The rest is **template collision** —
eight prose topics crossed with three question phrasings and five closing
sentences give 120 possible prose records, so 400 draws produce collisions by
the pigeonhole principle. This is the effect [32.2](02-synthetic-data.md)
predicted from the diversity metrics, now measured in records deleted.

Hashing costs $O(1)$ per record and one pass, so there is no reason ever to skip
this stage. What it cannot do is notice that two records differ by one word.

## Near-duplicates: shingles, MinHash, and LSH

Comparing every pair of $n$ documents is $O(n^2)$ — at a million documents that
is $5 \times 10^{11}$ comparisons, which is not a tuning problem but an
impossibility. The standard answer is three ideas stacked, and it is worth
understanding each separately.

**Shingles.** Represent a document as the *set* of its overlapping word
$k$-grams. Two documents that share most of their shingles say nearly the same
thing in nearly the same order. Similarity is the **Jaccard index**

$$
J(A, B) = \frac{|A \cap B|}{|A \cup B|}
$$

**MinHash.** Storing every shingle set is expensive and intersecting them is
slow. Instead, apply $N$ different hash functions to a set and keep only the
minimum value under each. The magic fact: for a random hash function, the
probability that two sets have the *same* minimum is exactly their Jaccard
index. So the fraction of matching positions in two $N$-length signatures is an
unbiased estimate of $J$, with standard error about $1/\sqrt{N}$.

**LSH banding.** Split each signature into $b$ bands of $r$ rows and hash each
band. Two documents become *candidates* if any band hashes identically. The
probability of that is

$$
P(\text{candidate}) = 1 - \left(1 - s^{r}\right)^{b}
$$

which is an S-curve with its steep part near $s \approx (1/b)^{1/r}$. Choosing
$b$ and $r$ *is* choosing the similarity threshold.

Here is all three on six documents chosen to sit at different distances from the
original.

```python
import hashlib
import re
import zlib
import numpy as np

A = ("A hash table stores key value pairs in an array of slots. A hash "
     "function maps each key to a slot index. When two keys land in the same "
     "slot the table resolves the collision by chaining. Average lookup cost "
     "is constant time.")
DOCS = {
    "A original": A,
    "B exact copy": A,
    "C whitespace/case": "  A HASH TABLE stores key value pairs in an array "
        "of slots.\tA hash function maps each key to a slot index. When two "
        "keys land in the same slot the table resolves the collision by "
        "chaining.  Average lookup cost is constant time.  ",
    "D near-duplicate": "A hash map stores key value pairs in an array of "
        "buckets. A hash function maps each key to a bucket index. Average "
        "lookup cost is constant time. When two keys land in the same bucket "
        "the table resolves the collision by chaining.",
    "E full rewrite": "Dictionaries keep entries in a flat block of memory. "
        "Where an entry lives is decided by running its identifier through a "
        "scrambling routine. Two identifiers may be sent to one place, and "
        "the structure copes by keeping a small list there. Retrieval "
        "normally takes the same time no matter how many entries exist.",
    "F unrelated": "Photosynthesis converts light energy into chemical energy "
        "stored in glucose inside the chloroplasts of green plants.",
}

NUM_HASHES, PRIME, BANDS, ROWS = 126, (1 << 31) - 1, 42, 3
_rng = np.random.default_rng(0)
COEF_A = _rng.integers(1, PRIME, NUM_HASHES)
COEF_B = _rng.integers(0, PRIME, NUM_HASHES)

def shingles(text, k=3):
    """The set of overlapping word k-grams, after normalisation."""
    w = re.findall(r"[a-z0-9]+", text.lower())
    return {" ".join(w[i:i + k]) for i in range(max(len(w) - k + 1, 1))}

def jaccard(s, t):
    return len(s & t) / len(s | t) if (s | t) else 0.0

def signature(sh):
    """MinHash: NUM_HASHES independent hashes, keep the minimum of each."""
    ids = np.array([zlib.crc32(s.encode()) for s in sh], dtype=np.int64)
    return ((np.outer(COEF_A, ids) + COEF_B[:, None]) % PRIME).min(axis=1)

def band_keys(sig):
    return [zlib.crc32(sig[b * ROWS:(b + 1) * ROWS].tobytes())
            for b in range(BANDS)]

sh = {n: shingles(t) for n, t in DOCS.items()}
sig = {n: signature(s) for n, s in sh.items()}
keys = {n: band_keys(s) for n, s in sig.items()}
digest = {n: hashlib.blake2b(re.sub(r"\s+", " ", t.lower().strip()).encode(),
                             digest_size=8).hexdigest()
          for n, t in DOCS.items()}

print(f"{'document':<20}{'exact J':>9}{'minhash':>9}{'err':>7}"
      f"{'bands':>7}{'LSH?':>6}{'same digest?':>14}")
for n in DOCS:
    ex = jaccard(sh["A original"], sh[n])
    est = float((sig["A original"] == sig[n]).mean())
    matched = sum(1 for x, y in zip(keys["A original"], keys[n]) if x == y)
    print(f"{n:<20}{ex:>9.3f}{est:>9.3f}{abs(ex - est):>7.3f}"
          f"{matched:>4}/{BANDS}{str(matched > 0):>6}"
          f"{str(digest[n] == digest['A original']):>14}")

print(f"\nLSH S-curve for b={BANDS}, r={ROWS} "
      f"(threshold approx {(1 / BANDS) ** (1 / ROWS):.2f}):")
for s in (0.1, 0.2, 0.3, 0.4, 0.5, 0.7, 0.9):
    print(f"   J={s:.1f}  P(candidate) = {1 - (1 - s ** ROWS) ** BANDS:.3f}")
```

```text
document              exact J  minhash    err  bands  LSH?  same digest?
A original              1.000    1.000  0.000  42/42  True          True
B exact copy            1.000    1.000  0.000  42/42  True          True
C whitespace/case       1.000    1.000  0.000  42/42  True          True
D near-duplicate        0.464    0.444  0.020   5/42  True         False
E full rewrite          0.000    0.000  0.000   0/42 False         False
F unrelated             0.000    0.000  0.000   0/42 False         False

LSH S-curve for b=42, r=3 (threshold approx 0.29):
   J=0.1  P(candidate) = 0.041
   J=0.2  P(candidate) = 0.286
   J=0.3  P(candidate) = 0.683
   J=0.4  P(candidate) = 0.938
   J=0.5  P(candidate) = 0.996
   J=0.7  P(candidate) = 1.000
   J=0.9  P(candidate) = 1.000
```

Three things to take from that table.

**The estimator works.** MinHash reports 0.444 where the true Jaccard is 0.464 —
an error of 0.020, comfortably inside the $1/\sqrt{126} \approx 0.089$ standard
error you should expect from 126 hashes. And it got there by comparing 126
integers instead of intersecting two shingle sets.

**Document D is the whole reason this stage exists.** It is the same explanation
with "map" for "table", "buckets" for "slots", and one sentence moved. Its
canonical digest differs from A's, so exact dedup lets it straight through;
MinHash puts it at 0.46 and LSH surfaces it as a candidate in 5 of the 42 bands.
Multiply that by a corpus scraped from mirrored sites and lightly-rewritten
content farms and you have the single largest category of duplicate in real
data.

**Document E is the honest limit.** It says exactly the same thing in entirely
different words, and MinHash scores it **0.000** — no shared 3-gram at all. Word
overlap cannot detect paraphrase. Catching E requires embeddings (the vector
machinery of [Chapter 29](../ch29-memory-rag/index.md)) and a nearest-neighbour
index, which costs a forward pass per document instead of a few hashes. Most
pipelines run MinHash on everything and semantic dedup only on the survivors, or
not at all — and their dataset cards should say which.

Now run it over the corpus. The candidate-pair count is the payoff.

```python
# continues
def near_dedup(recs, threshold=0.7):
    """Drop the later member of any pair whose estimated Jaccard >= threshold."""
    sigs = [signature(shingles(r["instruction"] + " " + r["output"]))
            for r in recs]
    buckets = {}
    for i, s in enumerate(sigs):
        for b in range(BANDS):
            key = (b, zlib.crc32(s[b * ROWS:(b + 1) * ROWS].tobytes()))
            buckets.setdefault(key, []).append(i)

    candidates = set()                    # distinct pairs sharing any band
    for members in buckets.values():
        for x in range(len(members)):
            for y in range(x + 1, len(members)):
                candidates.add((members[x], members[y]))

    dropped = set()
    for i, j in sorted(candidates):
        if i in dropped or j in dropped:
            continue
        if float((sigs[i] == sigs[j]).mean()) >= threshold:
            dropped.add(j)
    return ([r for k, r in enumerate(recs) if k not in dropped],
            len(dropped), len(candidates))

after_near, n_dropped, n_pairs = near_dedup(after_exact)
all_pairs = len(after_exact) * (len(after_exact) - 1) // 2
print(f"in {len(after_exact)} -> out {len(after_near)} (removed {n_dropped})")
print(f"pairs actually compared : {n_pairs}")
print(f"pairs in a full O(n^2) scan: {all_pairs}")
print(f"work avoided: {1 - n_pairs / all_pairs:.0%}")
```

```text
in 715 -> out 548 (removed 167)
pairs actually compared : 52053
pairs in a full O(n^2) scan: 255255
work avoided: 80%
```

167 more records gone that exact hashing could not see. The banding compared
52,053 pairs instead of 255,255 — an 80% saving on a corpus of 715, and the
saving grows with $n$ because the number of *genuinely similar* pairs grows far
more slowly than $n^2$. That is the entire argument for LSH: it turns a
quadratic problem into one that scales with the number of near-duplicates you
actually have.

## Model-based quality scoring

Heuristics catch garbage. They do not catch *mediocrity* — the 80 thin records
still in our corpus are well-formed and say nothing. The standard tool is a
small **quality classifier**: train a cheap model to distinguish a set of
reference documents you consider good from a set you consider bad, then score
everything with it. Real pipelines use fastText or a small transformer; the
mechanism is identical, and here it is a logistic regression over six features
so every number is visible.

The critical discipline is the **threshold sweep**. A quality score is not a
verdict, it is a knob, and picking a threshold without plotting what each one
costs is guessing.

```python
# continues
import matplotlib.pyplot as plt

STOP = set("a an the is are was were be been being this that these those it its "
           "of in on at to for with and or but if then so as by from very many "
           "people ask about know useful important topic thing things you your "
           "we they i not no yes do does did can could would should will there "
           "here what which who when where how why more most some any all one "
           "two three also just really quite often always never".split())
TECH = set("""hash table array slot bucket key value function index list node
reference pointer tree root leaf balanced comparison queue stack heap set trie
prefix string character constant linear logarithmic complexity lookup insert
delete sort search membership collision chaining recursion loop iterate memory
python return def assert sum max min sorted split reversed""".split())

def features(text):
    w = re.findall(r"[a-z0-9']+", text.lower())
    n = max(len(w), 1)
    return np.array([
        min(np.log1p(len(w)) / 4.0, 1.5),                # length
        len(set(w)) / n,                                  # type-token ratio
        sum(x not in STOP for x in w) / n,                # content density
        min(10.0 * sum(x in TECH for x in w) / n, 1.5),   # technical vocabulary
        1.0 if text.rstrip().endswith((".", "!", "?", ")", "`")) else 0.0,
        1.0,                                              # bias
    ])

GOOD_SEEDS = [
 "A hash table maps keys to array slots through a hash function, so an average lookup touches one slot.",
 "A linked list chains nodes by reference, so inserting at the front costs constant time.",
 "def solve(xs):\n    return sorted(set(xs))\n# A set drops repeats and sorted puts the survivors back in order.",
 "Working it through step by step, 14 * 3 = 42, so the result is 42.",
 "A binary search tree keeps smaller keys left and larger keys right, so lookup costs about log n.",
 "Quicksort partitions the list around a pivot and recurses on both halves.",
 "def solve(w):\n    return w == w[::-1]\n# The word is compared against its own reversal.",
 "A queue removes items in the order they arrived, so waiting jobs are served fairly.",
 "A trie stores strings character by character down a shared path, so a prefix search walks the prefix.",
 "Membership testing in a set costs constant time on average because the value is hashed to a bucket.",
]
BAD_SEEDS = [
 "This is an important topic in computer science and many people ask about it.",
 "It is.",
 "That is a very good question and the answer is quite interesting in general.",
 "N/A see above.",
 "answer answer answer answer answer answer answer answer answer answer.",
 "There are many things you could say here, and they are all worth knowing.",
 "Yes, that is correct, and it is something that comes up often when you do this.",
 "See above for the answer to this.",
 "Some people do it one way and some people do it another way, so it depends.",
 "It really depends on what you want, so there is no one answer to give here.",
]

X = np.array([features(t) for t in GOOD_SEEDS + BAD_SEEDS])
y = np.array([1.0] * len(GOOD_SEEDS) + [0.0] * len(BAD_SEEDS))
w_q = np.zeros(X.shape[1])
for _ in range(4000):                       # plain gradient descent, L2 = 0.01
    p = 1 / (1 + np.exp(-X @ w_q))
    w_q -= 0.5 * (X.T @ (p - y) / len(y) + 0.01 * w_q)

def quality(text):
    return float(1 / (1 + np.exp(-features(text) @ w_q)))

names = ["length", "type-token", "content", "technical", "punct", "bias"]
print("learned weights: " + "  ".join(f"{n}={v:+.2f}"
                                      for n, v in zip(names, w_q)))
print(f"training accuracy: {float((((X @ w_q) > 0) == (y > 0.5)).mean()):.0%}")

scores = np.array([quality(r["output"]) for r in after_near])
bad = np.array([r["low_quality"] for r in after_near])
print(f"\nscoring {len(after_near)} records; {int(bad.sum())} are known "
      f"low quality")
print(f"{'threshold':>10}{'kept':>8}{'kept %':>9}{'bad kept':>10}"
      f"{'good lost':>11}{'precision':>11}")

SHOWN = (0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50, 0.70, 0.90)
rows = []
for thr in np.round(np.arange(0.01, 1.0, 0.01), 2):
    keep = scores >= thr
    bad_kept = int((keep & bad).sum())
    good_lost = int((~keep & ~bad).sum())
    prec = float((keep & ~bad).sum() / max(keep.sum(), 1))
    rows.append((thr, keep.mean(), prec, 1 - bad_kept / max(bad.sum(), 1)))
    if thr in SHOWN:
        print(f"{thr:>10.2f}{int(keep.sum()):>8}{keep.mean():>9.0%}"
              f"{bad_kept:>10}{good_lost:>11}{prec:>11.1%}")

thrs = [r[0] for r in rows]
plt.figure(figsize=(7, 3.4))
plt.plot(thrs, [r[1] for r in rows], label="fraction of corpus kept")
plt.plot(thrs, [r[2] for r in rows], label="precision of the kept set")
plt.plot(thrs, [r[3] for r in rows], label="recall of junk removal")
plt.axvline(0.20, color="grey", linestyle="--", linewidth=1)
plt.xlabel("quality threshold")
plt.ylabel("fraction")
plt.title("Threshold sweep: every filter is a trade")
plt.legend(fontsize=8)
plt.grid(alpha=0.3)
plt.tight_layout()

QUALITY_THRESHOLD = 0.20
after_quality = [r for r in after_near
                 if quality(r["output"]) >= QUALITY_THRESHOLD]
print(f"\nat threshold {QUALITY_THRESHOLD}: {len(after_near)} -> "
      f"{len(after_quality)}")
```

```text
learned weights: length=+0.06  type-token=+0.03  content=+1.07  technical=+3.26  punct=-1.04  bias=-1.04
training accuracy: 95%

scoring 548 records; 43 are known low quality
 threshold    kept   kept %  bad kept  good lost  precision
      0.05     548     100%        43          0      92.2%
      0.10     548     100%        43          0      92.2%
      0.15     535      98%        30          0      94.4%
      0.20     505      92%         0          0     100.0%
      0.25     178      32%         0        327     100.0%
      0.30     178      32%         0        327     100.0%
      0.40     178      32%         0        327     100.0%
      0.50     174      32%         0        331     100.0%
      0.70     160      29%         0        345     100.0%
      0.90     136      25%         0        369     100.0%

at threshold 0.2: 548 -> 505
```

Look at the sweep before the weights. Between 0.20 and 0.25 the corpus falls off
a cliff: 92% kept becomes 32% kept, and 327 records that were **not** low
quality are destroyed to remove zero additional junk. Every one of those 327 is
a correct, verified math or code record. A threshold of 0.5 — the number you
would have picked without looking, because 0.5 feels like the middle — throws
away two thirds of a good corpus.

Now the weights, because they explain the cliff. `technical=+3.26` dominates
everything else, so the classifier has learned "contains data-structure
vocabulary". That is exactly the failure mode to be paranoid about: **a lexical
quality classifier is a topic classifier wearing a disguise.** Ours was trained
on ten computer-science paragraphs, so it rates a flawless poem, a medical note
or a French sentence as garbage. Real pipelines have shipped this bug at scale;
it is one mechanism by which quality filtering narrows a corpus to whatever the
reference set happened to contain.

The defence is not a better feature list, it is a habit: sweep the threshold,
read the records at each end, and check the *composition* of what survives
against the composition of what you started with.

## Verifiers: the gold standard

Every filter so far is a proxy. A **verifier** is not: it executes the claim.
For code, run the tests ([Section 24.2](../ch24-practice/02-testing.md) — a
passing test suite is a ground-truth label). For arithmetic, recompute. For
anything with a checkable answer, check it. This is the same argument
[31.4](../ch31-rl/04-reward-models.md) makes for verifiable rewards, applied one
stage earlier: a checker you wrote cannot be talked into agreeing with you.

Two verifier styles appear below, and the difference is worth naming. The math
verifier is **independent** — it re-derives the answer from the instruction and
never looks at what the record claims. The code verifier runs the **shipped
test** that came with the record, HumanEval style. Independent verifiers are
stronger; shipped tests are the only option when the answer is not
re-derivable.

```python
# continues
def verify(rec):
    """True = passed, False = failed, None = no verifier for this record."""
    if rec["domain"] == "math":
        # Independent verifier: recompute the answer from the instruction.
        m = re.search(r"value of (\d+) ([-+*]) (\d+)", rec["instruction"])
        if not m:
            return None
        a, op, b = int(m[1]), m[2], int(m[3])
        truth = {"+": a + b, "*": a * b, "-": a - b}[op]
        nums = re.findall(r"-?\d+", rec["output"])
        return bool(nums) and int(nums[-1]) == truth
    if rec["domain"] == "code" and rec["test"]:
        # Shipped-test verifier: run the record's own assert.
        ns = {}
        try:
            exec(rec["output"], ns)
            exec(rec["test"], ns)
            return True
        except Exception:               # AssertionError, TypeError, anything
            return False
    return None                          # prose: nothing to check

verdicts = [verify(r) for r in after_quality]
after_verify = [r for r, v in zip(after_quality, verdicts) if v is not False]
tally = Counter("pass" if v else "FAIL" if v is False else "no verifier"
                for v in verdicts)

print(f"{'domain':<10}{'checked':>9}{'passed':>8}{'failed':>8}{'pass rate':>11}")
for dom in ("math", "code", "prose"):
    checked = [v for r, v in zip(after_quality, verdicts)
               if r["domain"] == dom and v is not None]
    rate = f"{sum(checked) / len(checked):.0%}" if checked else "n/a"
    print(f"{dom:<10}{len(checked):>9}{sum(1 for v in checked if v):>8}"
          f"{sum(1 for v in checked if not v):>8}{rate:>11}")
print(f"\noverall: {dict(tally)}")
print(f"{len(after_quality)} -> {len(after_verify)}")
```

```text
domain      checked  passed  failed  pass rate
math            318     272      46        86%
code             68      56      12        82%
prose             0       0       0        n/a

overall: {'no verifier': 119, 'pass': 328, 'FAIL': 58}
505 -> 447
```

58 records with confident, well-formatted, *wrong* answers survived every
previous stage. Not one heuristic, hash or quality score could have caught them,
because there is nothing wrong with them except the content. That is what a
verifier buys, and it is why the field keeps returning to verifiable domains:
mathematics, code, unit conversion, structured extraction, anything with a
checkable answer.

And then the number that constrains everything: **119 records had no verifier at
all.** The prose is unverifiable, and it leaves this pipeline carrying nothing
stronger than a quality score. Be explicit about that split in your dataset
card. "Verified" and "not obviously bad" are different claims, and mixing them
under one label is how a corpus gets trusted more than it deserves.

!!! tip "A verifier that never fails is broken"

    An 86% pass rate is informative. A 100% pass rate almost always means the
    verifier is not running — a swallowed exception, a regex that stopped
    matching after a format change, a test file that no longer imports. Add a
    known-bad record to every batch and assert that the verifier rejects it.
    The check costs one record and catches a silent failure that would
    otherwise last for months.

## Decontamination against the eval sets

The [32.1](01-why-data.md) contamination detector becomes a pipeline stage here.
The rule is unchanged: build the $n$-grams of every evaluation item, and drop
any training record that shares one. Shorter $n$ is stricter — $n = 6$ below
rather than 8, because these evaluation questions are short and an 8-gram window
barely fits inside them.

```python
# continues
def ngrams(text, n=8):
    w = re.findall(r"[a-z0-9]+", text.lower())
    return {tuple(w[i:i + n]) for i in range(len(w) - n + 1)}

EVAL_GRAMS = set().union(*(ngrams(q, 6) for q in EVAL_SET))

def contaminated(rec, n=6):
    return bool(ngrams(rec["instruction"] + " " + rec["output"], n) & EVAL_GRAMS)

after_decon = [r for r in after_verify if not contaminated(r)]
print(f"eval set: {len(EVAL_SET)} questions, {len(EVAL_GRAMS)} distinct 6-grams")
print(f"{len(after_verify)} -> {len(after_decon)} "
      f"(removed {len(after_verify) - len(after_decon)})")
print(f"leaked records still present: "
      f"{sum(1 for r in after_decon if r['instruction'] in EVAL_SET)}")
```

```text
eval set: 3 questions, 17 distinct 6-grams
447 -> 421 (removed 26)
leaked records still present: 0
```

Seventeen 6-grams removed 26 records, and the check confirms none survived.
Three practical rules go with this stage. Decontaminate against **every** eval
you intend to report, not just the headline one. Run it **last**, so that a
record added by a later stage cannot slip past. And record in the dataset card
which eval sets were used and at what $n$ — a decontamination claim without
those two numbers is not checkable.

## The funnel report

Now all of it in one table. This is the artefact to save with every build.

```python
# continues
stages = [("input", CORPUS),
          ("after heuristics", after_heuristics),
          ("after exact dedup", after_exact),
          ("after near dedup", after_near),
          ("after quality >= 0.20", after_quality),
          ("after verification", after_verify),
          ("after decontamination", after_decon)]

print(f"{'stage':<24}{'kept':>7}{'removed':>9}{'% of input':>12}")
prev = None
for name, recs in stages:
    removed = "" if prev is None else f"{prev - len(recs):>9}"
    print(f"{name:<24}{len(recs):>7}{removed}{len(recs) / len(CORPUS):>12.1%}")
    prev = len(recs)

print(f"\nfinal composition")
print(f"  by domain     : {dict(Counter(r['domain'] for r in after_decon))}")
print(f"  by difficulty : {dict(Counter(r['difficulty'] for r in after_decon))}")
print(f"  yield         : {len(after_decon) / len(CORPUS):.1%}")
```

```text
stage                      kept  removed  % of input
input                      1200      100.0%
after heuristics           1092      108       91.0%
after exact dedup           715      377       59.6%
after near dedup            548      167       45.7%
after quality >= 0.20       505       43       42.1%
after verification          447       58       37.2%
after decontamination       421       26       35.1%

final composition
  by domain     : {'prose': 103, 'math': 272, 'code': 46}
  by difficulty : {2: 142, 1: 144, 3: 135}
```

**A 35% yield is normal, and the shape of the funnel is the diagnosis.**
Deduplication removed 544 records against the heuristics' 108, which says the
generator's problem was repetition, not brokenness — go back and diversify the
seeds rather than tighten the filters. Verification removed 58 that four earlier
stages had all approved, which is the argument for keeping it even though it is
the most expensive stage.

Look at the composition too, because the funnel changed it. The corpus went in
at roughly one third each and comes out 65% math, because math records carry
unique numbers and survive dedup while the templated prose collapses. Nobody
chose that mixture; it is a side effect of the filters. Always compare the
composition before and after, and if you do not like the answer, fix it
deliberately — which is what the next section does.

## Balancing difficulty and diversity

The funnel's output is not the training set. It is the *pool* you sample the
training set from, and sampling is where you fix the composition drift you just
measured. A **stratified sampler** takes a fixed quota from every
(domain, difficulty) cell, so the mixture is a decision rather than an accident.

```python
# continues
def stratified(recs, per_cell, seed=0):
    """Take up to per_cell records from every (domain, difficulty) cell."""
    rng = random.Random(seed)
    cells = {}
    for r in recs:
        cells.setdefault((r["domain"], r["difficulty"]), []).append(r)
    out, short = [], []
    for cell, members in sorted(cells.items()):
        take = min(per_cell, len(members))
        if take < per_cell:
            short.append((cell, len(members)))
        out.extend(rng.sample(members, take))
    return out, short

before = Counter((r["domain"], r["difficulty"]) for r in after_decon)
sample, short = stratified(after_decon, per_cell=12, seed=0)
after = Counter((r["domain"], r["difficulty"]) for r in sample)

print(f"{'cell':<20}{'available':>10}{'sampled':>9}")
for cell in sorted(before):
    print(f"{str(cell):<20}{before[cell]:>10}{after[cell]:>9}")
print(f"\nunder-filled cells: {short}")
print(f"stratified sample: {len(sample)} records "
      f"(from a pool of {len(after_decon)})")
```

```text
cell                 available  sampled
('code', 1)                 13       12
('code', 2)                 10       10
('code', 3)                 23       12
('math', 1)                 96       12
('math', 2)                 97       12
('math', 3)                 79       12
('prose', 1)                35       12
('prose', 2)                35       12
('prose', 3)                33       12

under-filled cells: [(('code', 2), 10)]
stratified sample: 106 records (from a pool of 421)
```

The `under-filled cells` line is the reason to write the sampler this way rather
than shuffling and slicing. `('code', 2)` could only supply 10 of the 12
requested, and the sampler *said so* instead of silently returning an unbalanced
set. That single line is the difference between "our corpus is balanced" and
"our corpus is balanced except where it isn't, and we know exactly where".

Two more things this stage should own. Diversity: within a cell, prefer records
that are far apart under the MinHash signatures you already computed, rather
than 12 near-neighbours. And difficulty: if the model already solves every
difficulty-1 item, a balanced sample is wasting a third of the budget — the same
"filter to problems the model solves *sometimes*" rule that
[31.3](../ch31-rl/03-dpo-grpo.md) applies to GRPO's prompt set.

## Dataset cards, provenance, and reproducible seeds

The last artefact is documentation, and it is not optional: a dataset nobody can
regenerate is a dataset nobody can fix. A **dataset card** records what the data
is, how it was made, what was removed, and — the section people skip — what is
known to be wrong with it.

The two mechanical requirements are that every random choice comes from a
recorded seed, and that the config is hashed so two builds can be compared by
one string.

```python
# continues
import json

PIPELINE = {"heuristics": sorted(FILTERS), "exact_dedup": "blake2b-128",
            "near_dedup": {"shingle_k": 3, "hashes": NUM_HASHES,
                           "bands": BANDS, "rows": ROWS, "threshold": 0.7},
            "quality_threshold": QUALITY_THRESHOLD,
            "verifiers": ["math:recompute", "code:shipped-assert"],
            "decontamination_ngram": 6, "sampler_seed": 0}

card = {
    "name": "ledger-instruct-v1",
    "config_sha256_12": hashlib.sha256(
        json.dumps({"generator": CONFIG, "pipeline": PIPELINE},
                   sort_keys=True).encode()).hexdigest()[:12],
    "generator_config": CONFIG,
    "pipeline_config": PIPELINE,
    "funnel": {name: len(recs) for name, recs in stages},
    "final_by_domain": dict(Counter(r["domain"] for r in after_decon)),
    "final_by_difficulty": dict(Counter(r["difficulty"] for r in after_decon)),
    "licence": "CC-BY-4.0 (synthetic; generated by this page)",
    "known_limitations": [
        "prose records are unverifiable and survive on the quality score alone",
        "the quality classifier is lexical and biased towards its seed topics",
        "decontamination used 6-grams against 3 eval questions only",
    ],
}

print(f"# {card['name']}   (config {card['config_sha256_12']})")
print(f"licence: {card['licence']}")
print("\nfunnel:")
for k, v in card["funnel"].items():
    print(f"   {k:<24}{v:>6}")
print(f"\nfinal composition: {card['final_by_domain']} / "
      f"{card['final_by_difficulty']}")
print(f"\ngenerator config : {card['generator_config']}")
print(f"near-dedup       : {card['pipeline_config']['near_dedup']}")
print(f"quality threshold: {card['pipeline_config']['quality_threshold']}")
print(f"verifiers        : {card['pipeline_config']['verifiers']}")
print("\nknown limitations:")
for line in card["known_limitations"]:
    print(f"   - {line}")

rebuilt = make_corpus(card["generator_config"])
print(f"\nregenerating from the recorded config reproduces the corpus: "
      f"{[r['output'] for r in rebuilt] == [r['output'] for r in CORPUS]}")
```

```text
# ledger-instruct-v1   (config 0bd84a4e3854)
licence: CC-BY-4.0 (synthetic; generated by this page)

funnel:
   input                     1200
   after heuristics          1092
   after exact dedup          715
   after near dedup           548
   after quality >= 0.20      505
   after verification         447
   after decontamination      421

final composition: {'prose': 103, 'math': 272, 'code': 46} / {2: 142, 1: 144, 3: 135}

generator config : {'n': 1200, 'seed': 11, 'p_exact_dup': 0.05, 'p_junk': 0.06, 'p_thin': 0.07, 'p_wrong': 0.15, 'p_rephrase': 0.15, 'p_contaminated': 0.04, 'p_stub_instruction': 0.02}
near-dedup       : {'shingle_k': 3, 'hashes': 126, 'bands': 42, 'rows': 3, 'threshold': 0.7}
quality threshold: 0.2
verifiers        : ['math:recompute', 'code:shipped-assert']

known limitations:
   - prose records are unverifiable and survive on the quality score alone
   - the quality classifier is lexical and biased towards its seed topics
   - decontamination used 6-grams against 3 eval questions only
```

The last line of that block is the whole point of writing seeds down: the
recorded config regenerates the identical corpus, so `0bd84a4e3854` is a name
for a specific dataset rather than a hopeful label. When an eval regresses three
months from now, that string is how you find out whether the data changed.

And write the limitations section honestly. Every corpus has one; the difference
between a good dataset card and a bad one is whether the author found the
limitations before the users did.

!!! warning "Common mistakes"

    - **Running the expensive stages first.** Verification on 1,200 records
      costs far more than heuristics on 1,200 records, and 780 of them were
      going to be deleted anyway. Order the pipeline cheapest-first.
    - **Picking a quality threshold without sweeping it.** Our 0.5 — the
      "obvious" middle — would have destroyed 331 good records to remove zero
      extra junk. Print the trade before you choose the point on it.
    - **Trusting exact dedup to catch duplicates.** One changed word defeats it
      completely. MinHash plus LSH is a hundred lines and catches the entire
      near-duplicate family.
    - **Believing MinHash catches paraphrase.** It scored a full rewrite at
      0.000. Word-overlap methods cannot see meaning; say so in the card rather
      than implying semantic dedup happened.
    - **Reporting a quality filter without checking what it deleted.** Ours
      learned "contains technical vocabulary" and would delete every well-written
      document about anything else. Compare the composition before and after.
    - **A dataset card with no limitations section.** If you cannot name three
      things wrong with your corpus, you have not looked at it.

## Check your understanding

??? success "Exact dedup removed 377 records but only about 5% of the corpus was injected as a deliberate copy. Where did the rest come from?"
    From template collision. The prose generator has 8 topics, 3 question
    phrasings and 5 closing sentences, which is 120 distinct prose records at
    most — and roughly 400 prose records were drawn. By the pigeonhole
    principle most of them had to repeat. This is exactly the effect
    [32.2](02-synthetic-data.md) measured with distinct-$n$ and mean pairwise
    Jaccard: a template-generated corpus has an *effective* size set by the
    number of template combinations, not by how many times you ran the
    generator. The fix is more seed diversity, not a better deduplicator.

??? success "The LSH stage compared 52,053 pairs instead of 255,255. Why does that saving grow rather than shrink as the corpus gets bigger?"
    The full comparison count is $\binom{n}{2}$, which grows quadratically. The
    candidate count grows roughly with the number of pairs that are *actually*
    similar plus a small false-positive rate from the S-curve — and in real
    corpora the number of genuinely near-duplicate pairs grows far more slowly
    than $n^2$. So the ratio candidates/all-pairs falls as $n$ rises. At 715
    documents it saved 80%; at a million it is the difference between a job
    that finishes and one that does not.

??? success "Predict: if you raised the near-dedup threshold from 0.7 to 0.9, would more or fewer records survive, and what new risk appears?"
    More records survive: a higher threshold means two documents must be more
    similar before one is dropped, so borderline pairs (like document D at 0.46
    — already below both thresholds) and moderate near-duplicates are kept.
    The risk is that near-duplicates that differ by a sentence or two now stay
    in the corpus, and they are the ones that get memorised: repeated text is
    memorised faster than it is generalised. Note also that the LSH banding is
    tuned to a threshold near 0.29; raising the *decision* threshold to 0.9
    without re-tuning $b$ and $r$ leaves you generating far more candidate pairs
    than you need, which costs time but not correctness.

??? success "The verifier found 58 wrong answers that four earlier stages approved. Why could no amount of heuristic or quality-model tuning have caught them?"
    Because nothing about those records is malformed. "Working it through step
    by step, 23 * 7 = 163, so the result is 163" has the right length, the right
    punctuation, the right vocabulary, a plausible structure, and a unique
    fingerprint. Every filter before the verifier is a proxy for correctness
    based on *surface form*, and the surface form is perfect. Only executing the
    claim — recomputing the product — distinguishes it from the correct version.
    This is the same reason [31.4](../ch31-rl/04-reward-models.md) prefers a
    passing test suite to a very good reward model.
