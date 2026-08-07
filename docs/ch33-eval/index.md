# Chapter 33 · Evaluation

Every chapter of Part V so far has taught you to build something: a sampler, a
serving stack, a tool protocol, a retrieval pipeline, an agent loop, a training
update, a dataset. This chapter asks the question that decides whether any of it
was worth building. Did the change help? By how much? Would you bet a release on
it? For every other kind of program you have written, the machine answers that
question for you — the tests pass or they do not, the program crashes or it
does not. A language model always answers, always fluently, and is sometimes
confidently wrong in ways nothing in your toolchain notices. Evaluation is the
discipline that replaces the missing compiler, and it is the skill that most
reliably separates people who ship working AI systems from people who ship
demos.

It is also where the field is weakest, which makes it unusually valuable to be
good at. Public benchmarks are contaminated, saturated, and measured with
undocumented normalizers; run-to-run variance routinely exceeds the improvements
people announce; and the fashionable shortcut — asking a model to grade another
model — carries biases large enough to reverse a conclusion. None of that means
evaluation is hopeless. It means the numbers require the same engineering care
as the systems they describe: error bars, isolation, version control, regression
gates, and a healthy suspicion of any measurement you did not produce yourself.

This chapter builds that care from the ground up. You will implement the metrics
rather than import them, watch a single unchanged model score anywhere from 25%
to 100% depending only on the scorer, build a complete harness with error
isolation and a report that tells you what to fix, put confidence intervals on
everything, and then construct an LLM judge whose biases are written in the
source so you can measure each one and remove the ones that are removable. The
running theme is the one [31.4](../ch31-rl/04-reward-models.md) introduced for
reward models and that applies with equal force here: **the measurement is a
component of your system, and an unvalidated component is a liability.**

**After this chapter you can …**

- explain why evaluation, not modelling, is the hardest part of AI engineering,
  and what replaces the compiler's feedback;
- describe MMLU, HumanEval, MBPP, SWE-bench and GAIA accurately — task format,
  metric, what each is good for and what each misses — and place long-context,
  tool-use and safety suites in the same taxonomy;
- implement exact match with a normalization chain, and demonstrate a 75-point
  score swing plus the false positives normalization creates;
- write the unbiased pass@k estimator from its formula, compare it with the
  plug-in shortcut, and explain why $n > k$ sampling matters;
- score multiple choice by log-likelihood, byte-normalized log-likelihood and
  PMI, contrast all three with generation plus parsing, and pick the mode that
  matches your product;
- detect contamination by n-gram overlap, and state exactly which leaks that
  method cannot see;
- reason about benchmark saturation, label-noise ceilings and Goodhart's law,
  and argue for a private eval set built from your own failures;
- build a complete eval harness — task dataclass, pluggable model interface,
  four scorers including an execution scorer, a runner with per-task error
  isolation, and a report with per-category accuracy and failure buckets;
- compute bootstrap confidence intervals, run paired comparisons, and decide
  whether a gap is real;
- ship a regression gate that fails the build on a per-task regression even when
  the aggregate is unchanged;
- evaluate agents with success rate, steps-to-success, cost per success,
  tool-error rate and trajectory-level scoring over recorded trajectories;
- name the real harnesses — lm-evaluation-harness, HELM, the BigCode harness,
  the SWE-bench harness, promptfoo and Inspect — and say what each is for;
- write a judge prompt with anchored levels, one criterion, evidence before the
  score and constrained output;
- measure position, verbosity, self-preference and formatting bias, and remove
  the ones that protocol changes can remove;
- validate a judge against human labels with Cohen's kappa, run a panel, and
  price a judged eval against its sampling error.

**Prerequisites.** [Chapter 24](../ch24-practice/index.md) is the direct
ancestor of this chapter: [24.2 Testing](../ch24-practice/02-testing.md) is where
regression discipline was introduced, and a golden-set gate is that idea pointed
at a probabilistic component. From Part V you need
[26.4 Sampling](../ch26-llm-internals/04-sampling.md) (temperature is why the
same eval gives different answers twice),
[28.2 Structured output](../ch28-tools-mcp/02-structured-output.md) (a large
share of apparent model failures are parsing failures),
[Chapter 30](../ch30-agents/index.md) (agent evaluation scores trajectories, not
answers), and [31.4 Reward models](../ch31-rl/04-reward-models.md) — the
Goodhart's-law argument there is the same argument as benchmark saturation here,
on a different timescale. [32.1](../ch32-data/01-why-data.md) supplies the
training-data view of contamination. From Parts I–IV you need dictionaries and
classes ([Chapter 12](../ch12-classes/index.md)), exceptions
([Chapter 10](../ch10-exceptions/index.md) — error isolation is the whole
runner), and comfort with reading a table of numbers.

**Sections**

- [33.1 Benchmarks and what they measure](01-benchmarks.md) — the four parts of
  a benchmark, an honest taxonomy of MMLU, HumanEval, MBPP, SWE-bench, GAIA and
  the long-context, tool-use and safety families; exact match as a family of
  metrics with a 75-point swing; pass@k with the unbiased estimator against the
  plug-in shortcut; log-likelihood versus generation scoring; contamination
  detection and the leaks it misses; label-noise ceilings, saturation, Goodhart,
  and the case for a private eval set.
- [33.2 Building an eval harness](02-eval-harness.md) — the pipeline as a
  diagram, then the whole thing runnable: tasks, a pluggable model interface,
  four scorers, a runner with error isolation, and a report with failure
  buckets; bootstrap confidence intervals, paired comparison and how many tasks
  you need; a regression gate that catches a break the aggregate hides; agent
  metrics over recorded trajectories; cost and latency as first-class axes; and
  the real harness landscape with commands.
- [33.3 LLM-as-a-judge](03-llm-as-judge.md) — a bad judge prompt beside a good
  one; pairwise versus absolute scoring; the bias catalogue measured on a judge
  whose coefficients you can read — position, verbosity, self-preference,
  formatting — with the fixes that work; validation against humans with Cohen's
  kappa; ties and calibration; panels and when they stop helping;
  reference-based judging; cost control by sampling and tiering; and a shipping
  checklist.
- [Exercises](exercises.md) — predict a normalizer's score, compute pass@k, write
  a rubric, decide whether a gap is real, detect contamination, remove position
  bias, design metrics for a triage agent, and extend the harness with a schema
  scorer and a gate.

!!! note "What is real and what is simulated here"
    Nothing on these pages calls a model or touches the network. Every "model"
    is a deterministic `FakeLLM` or a list of recorded results, and the judge in
    33.3 has its biases written as numeric coefficients precisely so you can
    measure them — which is the one thing you can never do with a real judge.
    What is **faithful** is everything else: the pass@k estimator is the one the
    HumanEval paper defines, the bootstrap is the standard percentile bootstrap,
    Cohen's kappa is the real statistic, and the harness architecture is the
    architecture every real framework implements. The scale is toy; the
    machinery is not.
