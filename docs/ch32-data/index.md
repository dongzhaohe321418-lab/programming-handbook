# Chapter 32 · Data-Centric AI

Chapters 26 to 31 built the machinery: attention and sampling, the KV cache,
tool calls, retrieval, agent loops, and the post-training methods that turn a
next-token predictor into an assistant. Every one of those is now, in broad
outline, public. The architecture of a modern open-weights model is a handful of
well-known choices; the training recipes are in papers; the frameworks are on
GitHub. What is *not* public, for any frontier system, is the corpus. This
chapter is about the part of the work that is still nobody's commodity.

The claim it argues is specific: **at a fixed compute budget, the data pipeline
is where the remaining quality lives.** Not because "garbage in, garbage out" is
a catchy phrase, but for three mechanical reasons:

- **A model cannot learn a behaviour the corpus never demonstrates.** There is
  no architectural substitute for an example.
- **It learns the corpus's errors with exactly the same enthusiasm as its
  truths.** The loss function has no opinion about which tokens are correct.
- **Every token spent on one domain is a token not spent on another.** The
  mixture decides what the model ends up good at.

None of those is fixable by a better attention variant. All of them are fixable
by better data.

So this chapter is a working pipeline rather than a survey. You will:

- write a JSONL schema validator, a mixture sampler, an n-gram contamination
  detector, and a PII scrubber with an honest account of what it misses;
- implement Self-Instruct and Evol-Instruct end to end with a deterministic
  `FakeLLM`;
- make model collapse happen on purpose, and watch the rare words go extinct;
- record agent trajectories from an instrumented ReAct loop, design an
  environment worth collecting from, and convert the results into SFT records,
  preference pairs and process-reward labels;
- build the filter stack — heuristics, exact dedup, MinHash and LSH, a quality
  classifier with a swept threshold, verifiers — and print the funnel report
  that says how many records each stage removed.

**After this chapter you can …**

- state the data-centric thesis with mechanisms rather than slogans, and say
  what is settled about it and what is current practice;
- name the four record types (pretraining text, SFT pairs, preference pairs,
  trajectories), write each as JSON, and say what the loss is computed on;
- stream JSONL, validate records against a declared schema before training, and
  render instruction records into a chat template without a template mismatch;
- compute what a mixture weight does to the effective distribution, including
  how many epochs each domain gets;
- detect benchmark contamination with n-gram overlap, and say precisely what
  that method cannot see;
- scrub PII with regexes, measure the false positives and false negatives, and
  write an honest claim about it in a dataset card;
- price synthetic data against human annotation, and explain why the audit, not
  the generation, is the expensive part;
- implement Self-Instruct — seed pool, generation, ROUGE-L similarity filter,
  instance generation, filtering — and read the growth and rejection curves;
- implement Evol-Instruct's depth and breadth operators together with the
  elimination check that discards failed evolutions, and explain why the check
  is the method rather than an optimisation;
- synthesise preference pairs UltraFeedback-style with per-criterion scores, in
  the format Chapter 31's DPO trainer consumes;
- measure diversity with distinct-$n$, vocabulary size and pairwise Jaccard,
  and explain why distinct-$n$ must be compared at matched length;
- simulate model collapse, match the variance decay to its closed form, and
  show that rare categories die abruptly and permanently;
- specify a trajectory schema field by field and serialise it to JSONL with a
  verified round trip;
- instrument a ReAct agent with a recorder, and design an environment that is
  deterministic, resettable, verifiably scored and graded by difficulty;
- run a rollout driver over many seeds and read a success-rate table as a
  diagnosis rather than a score;
- convert trajectories into SFT data, preference pairs on the same task, and
  step-level PRM labels estimated by Monte-Carlo rollouts from a prefix;
- clean trajectories — truncate loops, strip detours, redact secrets, cap
  length — and check that the survivors still support their own conclusions;
- build a heuristic filter bank that reports a rejection-reason histogram;
- deduplicate exactly with a stable cryptographic fingerprint, and
  near-duplicate with shingles, MinHash and LSH banding written in numpy;
- state what MinHash cannot detect, and why that limit needs to appear in the
  dataset card;
- train a small quality classifier, sweep its threshold, and read the trade-off
  curve instead of guessing a number;
- use verifiers — executed tests and recomputed answers — as the strongest
  filter available, and recognise a verifier that has silently stopped running;
- sample a training set stratified by difficulty and domain, and detect
  under-filled cells;
- decontaminate against every eval you intend to report;
- produce a funnel report and a dataset card that make the build reproducible
  from a recorded seed and a config hash.

**Prerequisites.** [Chapter 11](../ch11-files/index.md) is the direct ancestor of
everything here — a corpus is a file you stream, and
[Section 11.2](../ch11-files/02-read-write.md) is the read/write pattern used on
every page. Beyond that:

- **From Part II** — dictionaries and sets
  ([Chapter 9](../ch09-collections/index.md)).
- **From Part III** — [Section 16.1](../ch16-complexity/01-big-o.md), because the
  whole argument for LSH is that $O(n^2)$ is not available.
- **From Part IV** — [Section 24.2](../ch24-practice/02-testing.md), the ancestor
  of verifier-based filtering: a passing test suite is a ground-truth label.
- **From Part V** — [Chapter 30](../ch30-agents/index.md) is required for 32.3,
  because trajectories are recordings of that loop, and
  [Chapter 31](../ch31-rl/index.md) for the formats: 32.2 and 32.3 both produce
  the preference pairs [31.3](../ch31-rl/03-dpo-grpo.md) consumes and the step
  labels [31.4](../ch31-rl/04-reward-models.md) describes.
- **From Part VI, useful but not required** —
  [Section 36.1](../ch36-hashing-tries/01-hash-tables.md) explains the hash table
  under exact dedup, and [Section 41.1](../ch41-regex/01-fundamentals.md) the
  pattern syntax used for scrubbing.

**Sections**

- [32.1 Why data decides everything](01-why-data.md) — the thesis argued with
  three mechanisms, the data lifecycle, the four record types as JSON, JSONL and
  a schema validator, chat templates and the template-mismatch bug, mixture
  weights with an epoch calculation and a plot, n-gram decontamination, and a
  PII scrubber together with the two ways it fails.
- [32.2 Synthetic data generation](02-synthetic-data.md) — the cost arithmetic,
  distillation and the licensing question it raises, Self-Instruct as a running
  pipeline with a ROUGE-L filter, Evol-Instruct's five operators and four
  elimination checks, UltraFeedback-style multi-criteria preference synthesis,
  diversity metrics at matched length, model collapse matched to its closed
  form, and the quality-control loop with a seeded human audit.
- [32.3 Agent trajectory data](03-trajectories.md) — the trajectory schema field
  by field, a dataclass with a verified JSONL round trip, a recorder bolted onto
  a ReAct loop, an environment with `reset`/`step`/`is_done` and verifiable
  success, a rollout driver with a success-rate table, conversion into all three
  training formats including Monte-Carlo PRM labels, and a four-stage cleaner
  with before/after counts.
- [32.4 Filtering, dedup, and verification](04-filtering.md) — a filter bank with
  a rejection histogram, exact dedup by stable fingerprint, shingles → MinHash →
  LSH banding in numpy with estimated versus exact Jaccard, a quality classifier
  with a swept threshold, executed verifiers, stratified sampling,
  decontamination, the end-to-end funnel report, and dataset cards.
- [Exercises](exercises.md) — spot the bad records, write a filter for a stated
  failure, compute a Jaccard by hand and check it with MinHash, convert a
  trajectory into three formats, design a verifiable environment, predict the
  funnel numbers, catch a contaminated record, and build your own Evol-Instruct
  operator and defend it.

!!! note "What is real and what is simulated here"

    Nothing on these pages calls a model, downloads a dataset, or touches the
    network — the Run buttons execute Python and numpy in your browser. Where a
    language model is needed it is a deterministic `FakeLLM`, and every corpus is
    generated on the spot from a recorded seed. What is **faithful** is the
    engineering: the JSONL schema, the ROUGE-L threshold from the Self-Instruct
    paper, Evol-Instruct's elimination rules, the MinHash estimator and the LSH
    S-curve formula, the Monte-Carlo value estimate behind process-reward labels,
    and the funnel discipline itself. A MinHash signature over 126 hashes is a
    *correct* MinHash signature. Each page says plainly which parts are toy
    scale, and — more importantly — where the method stops working at all.
