# 34.2 Portfolio, open source, and research

Phase 4 of the learning path produces evidence, and this section is about what
counts as evidence. The short version: a project that **runs**, is **measured**,
and is **documented** beats any list of technologies, and it beats it by so much
that the comparison is not close. A repository whose README opens with "built
with LangChain, Pinecone, FastAPI, Docker" tells a reader which tutorials you
followed. A repository whose README opens with "answers questions over 40k
support tickets; 71% ± 6 exact-match on a 200-item held-out set, up from 48%
with naive chunking; p95 latency 1.9s; here is what still fails" tells them you
can do the job.

## Four portfolio archetypes

Four projects that reliably demonstrate the skills of Part V. Build **one**
properly rather than four halfway; a single finished, measured system is worth
more than a portfolio page of abandoned starts. Each archetype below comes with
the trap that eats most attempts at it.

### 1. A domain MCP server plus an agent

**Scope.** Pick a data source you genuinely know — a hobby's public API, your
own notes, a public dataset with awkward structure — and expose it as three to
five well-designed tools over MCP
([28.3](../ch28-tools-mcp/03-mcp-protocol.md),
[28.4](../ch28-tools-mcp/04-building-mcp-server.md)). Then write an agent
([30.1](../ch30-agents/01-agent-loop-react.md)) that answers questions requiring
several of those tools in sequence.

**Measure.** Task success rate on 30–50 questions you wrote in advance,
steps-to-success, tool-error rate, and cost per successful task — the metric set
from [33.2](../ch33-eval/02-eval-harness.md). Include the failures.

**The trap.** Wrapping a single API call in a tool and calling it an agent. The
value is in tool *design*: the argument schema that a model gets right first
time, the error message that tells the model how to recover, the narrow
`list_open_tickets` rather than the dangerous `run_sql`
([30.4](../ch30-agents/04-frameworks.md)). Show your before-and-after tool
schemas and the error rate for each — that comparison is the actual content.

### 2. An inference optimisation study

**Scope.** Take one model and one workload, and produce real latency and
throughput numbers across a deliberate set of changes: batch size, quantization
level, context length, KV-cache behaviour, one serving engine against another
([Chapter 27](../ch27-inference/index.md)).

**Measure.** Time to first token, inter-token latency, tokens per second at p50
and p95, memory footprint, and cost per thousand requests — reported as curves,
not single points, because the throughput/latency trade-off *is* the result
([27.3](../ch27-inference/03-latency-streaming.md)).

**The trap.** Reporting an average of ten runs on your laptop while a browser is
open, and drawing conclusions from a 5% difference. Pin what you can, report
variance, state your hardware, and say plainly which comparisons your setup
cannot resolve. A study that says "these two configurations were
indistinguishable at my sample size" reads as competence; one that claims a
precise 3% win reads as inexperience.

### 3. A synthetic-data and alignment experiment

**Scope.** Choose a narrow behaviour a small model does badly. Generate
candidate data ([32.1](../ch32-data/01-why-data.md)), filter it deliberately,
build a preference set, run one alignment method
([31.3](../ch31-rl/03-dpo-grpo.md)), and evaluate against a held-out set you
built **before** training ([Chapter 33](../ch33-eval/index.md)).

**Measure.** Before and after on the held-out set with confidence intervals, plus
at least one *regression* check on a capability you were not targeting — the
result everyone forgets to look for and the one that makes the write-up
credible.

**The trap.** Evaluating on data drawn from the same generator that produced the
training set. That is contamination by construction
([33.1](../ch33-eval/01-benchmarks.md)), and it produces spectacular numbers that
mean nothing. Build the eval set first, from a different source, and never look
at it while iterating.

### 4. A reproduction

**Scope.** Take one paper, pick the smallest experiment it reports, and
reproduce that number. Then write up honestly where your result differed and why.

**Measure.** Their number, your number, and a diagnosis of the gap: data version,
tokenizer, decoding settings, evaluation normalizer, hardware, hyperparameters
you had to guess because the paper did not say.

**The trap.** Treating a difference as failure and abandoning the write-up. The
gap analysis *is* the contribution — practitioners know reproduction is hard, and
a careful account of why a number moved is more informative than a matching
number. Say clearly when a difference is not explained; unexplained is an honest
finding, "must be a random seed" without evidence is not.

## The README that gets you hired

Someone will spend ninety seconds on your repository. Structure it so that the
ninety seconds land on the right things. This mirrors the self-review discipline
in [24.3](../ch24-practice/03-style-review.md) — the reader is a stranger with
no context and no patience, exactly like a code reviewer.

| Section | Length | Contents |
| --- | --- | --- |
| **Problem** | 2–3 sentences | what task, for whom, and why it is not trivial |
| **Approach** | 1 paragraph + a diagram | the design and the one interesting decision in it |
| **Results** | a table | the metric, the baseline, the number, the interval, the eval-set size |
| **Limitations** | a short list | what it does badly, what you did not test, what would break at scale |
| **How to run** | a code block | clone, install, one command that produces the results table |

Four rules that separate a README that works from one that does not.

**Lead with the number, and put an interval on it.** "71% ± 6 on 200 held-out
items, against a 48% baseline" is a sentence a reader can evaluate. "Achieves
high accuracy" is one they will skip.

**Name the baseline.** A number with nothing to compare it to is not a result.
The baseline can be humble — the naive implementation, the previous version, the
off-the-shelf default — but it must exist, and it must have been measured the
same way on the same items.

**Make "how to run" actually work, on a clean machine.** Pin your dependencies,
include a tiny sample dataset, and make the default command finish in under a
couple of minutes. A reader who hits an error in the first command stops being a
reader.

**Write the limitations section yourself.** It is the highest-signal paragraph in
the whole document. Anyone senior will find the weaknesses in five minutes; the
only question is whether you found them first. "Retrieval degrades badly on
queries with no lexical overlap; I did not test above 100k documents; the judge
was not validated against human labels" reads as judgement, not weakness.

## Open source is the highest-signal credential

A merged pull request to a project you did not create is worth more than a
personal repository of equivalent size, for reasons that have nothing to do with
prestige. It proves you can read unfamiliar code, work within someone else's
conventions, respond to review, and finish. Those are precisely the things a
personal project cannot demonstrate and precisely the things a team is hiring
for.

**Finding a first issue.** Pick a project you already use — that is not advice
about passion, it is about being able to tell whether a change is correct. Then,
in order of increasing effort: reproduce an open bug and post the exact steps and
environment (valuable on its own, and often the whole blocker); fix a
documentation error you personally hit; add a test for an untested branch; then
take a small labelled issue. Read `CONTRIBUTING.md` first, and read the last
twenty merged pull requests before opening one — they tell you the house style
faster than any document.

**First-PR etiquette.** Comment on the issue before you start, so two people do
not do the same work. Keep the change small and single-purpose; a 40-line PR gets
reviewed today and a 900-line PR gets reviewed eventually. Match the surrounding
style even where you disagree with it. Include a test that fails before your
change and passes after ([24.2](../ch24-practice/02-testing.md)). Write a
description with what, why, and how you verified it
([24.1](../ch24-practice/01-git-workflow.md)). When review comes, respond to
every comment, push fixes as new commits so the reviewer can see what changed,
and do not argue about style in your first contribution. Then be patient:
maintainers are volunteers and a two-week wait is normal, not rejection.

**Why documentation and test pull requests are underrated.** They are the two
kinds of contribution maintainers most reliably want and least reliably get.
They require you to understand the code as well as a feature PR would, they are
much easier to review, and they get merged. Three merged documentation fixes
tell a hiring manager that you can operate inside someone else's project; one
unmerged 900-line feature branch tells them nothing at all.

## Research output, honestly

Not everyone should write papers, and a portfolio does not need one. But the
publication ladder is worth understanding, because it calibrates how much a
given line on a résumé actually represents.

| Venue | What it typically requires | Realistic effort |
| --- | --- | --- |
| Preprint (arXiv and similar) | a clear write-up; no peer review | weeks; anyone can post, so it signals little on its own |
| Workshop paper | one focused idea, a small honest experiment, 4–8 pages | a few months; genuinely achievable alongside other work |
| Top conference | a novel contribution, strong baselines, ablations, statistical rigour, reproducibility | six to eighteen months, usually with an experienced co-author |

The **reproducibility bar** has risen sharply and is now the practical difference
between the rows: released code, released data or a precise description of it,
seeds, hyperparameters, hardware, and results reported over multiple runs with
variance. A workshop paper that meets that bar is more useful to the field —
and, frankly, more impressive to a knowledgeable reader — than a conference paper
that reports one lucky run.

If you have never published, the honest sequence is: reproduce someone else's
result, write it up publicly, then extend it by one question. That third step is
a workshop paper. And be aware of the failure mode specific to preprints: posting
something unreviewed that later turns out to be wrong is a permanent, searchable
part of your record, so apply Chapter 33's standards to yourself before you post.

## Interviewing

**System design for LLM roles** is a distinct format. The questions are open —
*design a RAG system for a company's internal documents*, *design a serving
stack for a chat product*, *design an evaluation pipeline for an agent* — and the
interviewer is watching for whether you ask about constraints before you draw
boxes, whether you can do capacity arithmetic out loud, and whether you know
which parts are hard.

Here is a worked outline for the first one.

> **Design a RAG system over 500k internal documents.**
>
> **1. Constraints first, before any design.** How many documents and how do
> they change? Who may see what — is there per-user access control on the
> corpus? What latency is acceptable? What is the budget? What does a *wrong*
> answer cost, and is a citation required? Access control is the question most
> candidates skip and the one that most constrains the design, because it means
> filtering at retrieval time rather than after.
>
> **2. Ingestion.** Parse, clean, chunk with overlap, embed, index. Store the
> source, offsets and permissions as metadata alongside every chunk so answers
> can cite and filters can apply ([29.2](../ch29-memory-rag/02-rag-pipeline.md)).
> Re-embedding 500k documents is a batch job you will run more than once, so
> make it resumable.
>
> **3. Retrieval.** Hybrid: lexical search catches identifiers and error codes
> that embeddings blur; dense retrieval catches paraphrase. Merge, then rerank
> the top candidates. Say plainly that retrieval quality, not model quality, is
> the usual bottleneck.
>
> **4. Generation.** Fit top-$k$ chunks into the context, require citations,
> and constrain the output format ([28.2](../ch28-tools-mcp/02-structured-output.md)).
>
> **5. Evaluation.** Two separate metrics — retrieval recall@k, and answer
> faithfulness to the retrieved context. A reference-based faithfulness judge is
> nearly free here because the context *is* the reference
> ([33.3](../ch33-eval/03-llm-as-judge.md)).
>
> **6. Numbers.** Then do the arithmetic out loud.

```python
"""Back-of-envelope sizing for the 'design a RAG system' whiteboard answer."""

DOCS = 500_000
TOKENS_PER_DOC = 1_200
CHUNK, OVERLAP = 400, 50
DIM, BYTES_PER_DIM = 768, 2          # fp16 vectors
TOP_K = 8
PROMPT_OVERHEAD, ANSWER_TOKENS = 500, 300
QUERIES_PER_MONTH = 200_000

# Illustrative prices per million tokens — plug in today's real numbers.
PRICE_EMBED, PRICE_IN, PRICE_OUT = 0.02, 0.60, 2.40

chunks_per_doc = max(1, -(-(TOKENS_PER_DOC - OVERLAP) // (CHUNK - OVERLAP)))
chunks = DOCS * chunks_per_doc
index_gb = chunks * DIM * BYTES_PER_DIM / 1e9
embed_tokens = DOCS * TOKENS_PER_DOC
in_tokens = TOP_K * CHUNK + PROMPT_OVERHEAD

print(f"{'chunks per document':<28}{chunks_per_doc:>12,}")
print(f"{'chunks total':<28}{chunks:>12,}")
print(f"{'vector index (fp16)':<28}{index_gb:>11.1f} GB")
print(f"{'one-time embedding cost':<28}"
      f"{'$' + format(embed_tokens / 1e6 * PRICE_EMBED, ',.0f'):>12}")
print()
print(f"{'input tokens per query':<28}{in_tokens:>12,}")
cost_q = (in_tokens * PRICE_IN + ANSWER_TOKENS * PRICE_OUT) / 1e6
print(f"{'cost per query':<28}{'$' + format(cost_q, '.5f'):>12}")
print(f"{'monthly generation cost':<28}"
      f"{'$' + format(cost_q * QUERIES_PER_MONTH, ',.0f'):>12}")
print()
print("what changes the answer most:")
for k in (2, 8, 20):
    c = ((k * CHUNK + PROMPT_OVERHEAD) * PRICE_IN
         + ANSWER_TOKENS * PRICE_OUT) / 1e6
    print(f"  top_k = {k:>2}: ${c * QUERIES_PER_MONTH:>7,.0f}/month "
          f"({c / cost_q:.2f}x)")
```

Two million chunks, a **3.1 GB** index that fits in memory on one machine, and
**$12** of one-time embedding. The headline for the interview is the last block:
moving `top_k` from 8 to 20 costs **1.98×** the monthly generation bill, and
dropping it to 2 halves it. That single sensitivity is worth more than a
beautiful architecture diagram, because it shows you know which knob is
expensive. Say out loud that the prices are placeholders and that you would
substitute current ones — an interviewer who knows the field will trust the
method and distrust confident stale numbers.

**The coding round is still a coding round.** For most LLM engineering roles it
is ordinary data-structures work: hash maps, graphs, two pointers, recursion with
memoisation, occasionally a heap. Parts III and VI are the preparation, and
[34.1](01-learning-path.md)'s drill schedule is how to keep it warm. Two pieces
of advice that generalise: state the complexity before you write the code, and
say what you are testing as you test it — interviewers are grading your process
at least as much as your solution ([16.1](../ch16-complexity/01-big-o.md)).
Expect at least one round to be practical instead: fix a bug in a small agent,
write a scorer, or design a prompt with an eval attached. Chapter 33 is
unusually good preparation for that round because almost nobody prepares for it.

## Staying current without drowning

The volume of output in this field is unmanageable and getting worse, and trying
to keep up with all of it is both impossible and unnecessary. Two things make it
tractable.

**A small, deliberate set of sources.** Three or four is enough: one place that
surfaces papers with discussion, one or two practitioner blogs from people who
actually ship, and the release notes of the two or three tools you depend on.
Release notes are the most underrated of these — they tell you what changed in
something you use, which is worth more than a survey of things you do not. Delete
anything that reliably produces excitement without information.

**A weekly habit rather than a daily scroll.** One hour, once a week: skim the
week's titles, pick one thing, give it pass 1 and — if it survives — pass 2
([34.1](01-learning-path.md)). Fifty papers a year at pass 2 is far more than
most working engineers manage, and it costs less attention than checking a feed
every morning.

The reason this is enough brings the chapter back to where Part V started. Most
of what looks new is a recombination of mechanisms you have already built by
hand. A new attention variant is a change to the numbers you computed in
[Chapter 26](../ch26-llm-internals/index.md); a new serving trick is arithmetic
you did in [Chapter 27](../ch27-inference/index.md); a new alignment method is a
different way to estimate the gradient in
[Chapter 31](../ch31-rl/index.md); and every claim about any of them is a
measurement that deserves the scrutiny of
[Chapter 33](../ch33-eval/index.md). Those foundations are what let you read a
launch announcement and work out in an afternoon whether it changes anything for
you. Tools age in months. That understanding does not.

!!! warning "Common mistakes"

    - **A portfolio of four half-finished projects.** One finished, measured,
      documented system outperforms all of them together.
    - **A results section with no baseline and no interval.** A number with
      nothing to compare it to is not a result, and on a 50-item eval set the
      95% half-width is about 12 points.
    - **Evaluating a fine-tune on data from the same generator that made the
      training set.** Contamination by construction; the numbers will be
      wonderful and meaningless.
    - **Hiding the limitations.** Any reviewer finds them in five minutes. The
      only question is whether you found them first.
    - **A first pull request that is 900 lines and changes three things.** Small
      and single-purpose gets merged; large and mixed gets postponed forever.
    - **Posting a preprint you have not tried to break.** It is permanent and
      searchable. Apply Chapter 33's standards to your own claims first.
    - **Treating the coding interview as beneath you.** It is still there, it is
      still Parts III and VI, and it is entirely maintainable with an hour a
      week.

## Check your understanding

1. Two candidates apply. One has six repositories using popular frameworks; the
   other has one repository with a results table, a limitations section, and
   three merged documentation PRs to a project they use. Why is the second
   stronger?

    ??? success "Answer"

        The second has demonstrated the things the job consists of: measuring
        whether a change helped, being honest about what does not work, and
        operating inside code they did not write under someone else's review.
        Six framework projects demonstrate that six tutorials were followed;
        nothing in them shows whether the person can tell a real improvement
        from noise, which is the skill Chapter 33 exists for and the one most
        often missing.

2. Your reproduction gets 63% where the paper reports 71%. What do you write?

    ??? success "Answer"

        Both numbers, then a diagnosis. Work through the differences you can
        identify — data version, tokenizer, prompt format and few-shot count,
        decoding settings, the evaluation normalizer, hardware and any
        hyperparameters the paper did not specify — quantify the ones you can by
        re-running with each changed, and state plainly which part of the gap
        remains unexplained. That write-up is more useful than a matching number
        would have been, because everyone in the field has hit the same wall.
        What you must not write is a shrug about random seeds without having
        measured seed variance.

3. In the RAG design question, why does the interviewer care more about the
   `top_k` sensitivity than about your architecture diagram?

    ??? success "Answer"

        Because the diagram is roughly the same in every candidate's answer, and
        the arithmetic is not. Moving `top_k` from 8 to 20 doubles the monthly
        generation bill while the index size and the embedding cost do not move
        at all — so knowing which knob is expensive tells the interviewer you
        have operated a system rather than drawn one. It also demonstrates the
        habit the whole of Part V teaches: write the formula, put realistic
        numbers in it, and let the arithmetic decide the design.

4. Why does this section recommend release notes as a source, over most other
   ways of keeping current?

    ??? success "Answer"

        Because they describe changes to something you actually depend on, so
        every item has a direct consequence for your work — a deprecation you
        must handle, a new capability you can use, a bug fix that explains
        something you saw last month. Most other channels report developments
        with no bearing on anything you are building, which feels like keeping
        up and is not. The general principle: prefer sources whose items you can
        act on, and let the foundations from Chapters 26, 27, 31 and 33 handle
        the rest by making new work fast to evaluate.
