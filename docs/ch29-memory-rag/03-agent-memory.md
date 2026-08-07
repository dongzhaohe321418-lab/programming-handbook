# 29.3 Agent memory and context management

Retrieval gets you facts. Memory gets you *continuity* — the difference
between a search engine that answers each question from scratch and an
assistant that knows you prefer zsh, that you are in UTC+1, and that you spent
yesterday chasing an ingestion bug. The awkward truth underneath is that a
language model has no memory at all: every call is stateless, and everything
it "remembers" is text your program chose to put in the prompt. So agent
memory is not a model feature. It is a *data structures* problem — what to
store, how to rank it, and how to fit the winners into a fixed budget — which
is why you already have every tool you need for it.

## Four memories, one context window

Human memory research gives us a vocabulary that maps unreasonably well onto
agent design. The mapping is an analogy, not a claim about cognition, but it
tells you exactly which store a given fact belongs in.

| Kind | In a person | In an agent | Lives where | Example |
| --- | --- | --- | --- | --- |
| **Working** | what you are holding in mind right now | the current conversation's turns | *in the context window*, verbatim | "Found it, it says 200. Can I just edit that?" |
| **Episodic** | remembering a specific event | summaries of past sessions and past stretches of this one | a store, retrieved on demand | "Session 1: debugged an Atlas failure caused by batch size 200." |
| **Semantic** | knowing a fact, without recalling when you learned it | distilled facts and preferences | a keyed store, usually small | `user.timezone = "UTC+1"` |
| **Procedural** | knowing *how* — riding a bike | learned skills: tool definitions, few-shot examples, checklists the agent has refined | the system prompt, or a skill library | "When ingestion fails, check batch size, then the dead-letter queue." |

Only the first kind lives in the context window for free. The other three live
in stores you build, and reach the model only when your code retrieves them
and writes them into the prompt. That is the entire subject of this section:
**everything is a decision about what to put in a fixed-size box.**

## The context window is a budget, and you pay it every turn

Context is not free memory. It costs money per token, it costs latency because
every prompt token must be prefilled
([Section 27.1](../ch27-inference/01-kv-cache.md)), and it costs GPU memory
because every token needs a KV cache entry. Worse, an agent resends its whole
context on *every* call, so an unmanaged conversation's total input tokens grow
quadratically with the number of turns.

```python
PRICE_IN, PRICE_OUT = 3.0, 15.0   # illustrative USD per MILLION tokens
TURNS, OUT_PER_TURN = 20, 250     # a 20-turn session; model writes 250 tokens
SYSTEM_AND_TOOLS = 1200           # stable prefix, resent on every call
PER_TURN = 400                    # tokens each user exchange adds to history

def kv_bytes(layers, kv_heads, head_dim, n_tokens, bytes_per_elt=2):
    """The Section 27.1 formula: 2 (K and V) x layers x KV heads x dim x tokens."""
    return 2 * layers * kv_heads * head_dim * n_tokens * bytes_per_elt

def session(cap=None):
    """Run a whole session; return (input tokens, output tokens, cost, peak context)."""
    total_in = total_out = history = peak = 0
    for _ in range(TURNS):
        context = SYSTEM_AND_TOOLS + history
        if cap is not None:
            context = min(context, cap)         # the whole job of a memory manager
        peak = max(peak, context)
        total_in += context                     # you pay for the WHOLE context, every call
        total_out += OUT_PER_TURN
        history += PER_TURN + OUT_PER_TURN
    cost = total_in / 1e6 * PRICE_IN + total_out / 1e6 * PRICE_OUT
    return total_in, total_out, cost, peak

head = (f"{'strategy':<18} {'input tok':>10} {'cost/session':>13} "
        f"{'1k sessions':>12} {'peak ctx':>9} {'peak KV':>9}")
print(head)
print("-" * len(head))
for label, cap in [("keep everything", None), ("cap at 8000", 8000),
                   ("cap at 4000", 4000), ("cap at 2000", 2000)]:
    total_in, _, cost, peak = session(cap)
    kv = kv_bytes(32, 8, 128, peak) / 1e9      # 8B-class model, GQA-8, fp16
    print(f"{label:<18} {total_in:>10,} {'$' + format(cost, '.4f'):>13} "
          f"{'$' + format(1000 * cost, ',.0f'):>12} {peak:>9,} {kv:>8.3f}G")

print()
PARAMS, COMPUTE = 8e9, 150e12      # illustrative: 8B model, achieved FLOP/s
for ctx in (1200, 4000, 32000, 128000):
    print(f"prefilling {ctx:>7,} tokens ~ {1e3 * 2 * PARAMS * ctx / COMPUTE:>7.1f} ms"
          f"   KV cache {kv_bytes(32, 8, 128, ctx) / 1e9:>6.3f} GB")
```

The prices and FLOP rate are illustrative stand-ins — substitute your
provider's numbers and rerun. What generalizes is the shape:

- An unmanaged 20-turn session sends **147,500 input tokens** and costs
  **$0.5175**. Capping the context at 4000 tokens sends 72,500 and costs
  $0.2925 — a **2.0×** saving on input tokens, which at a thousand sessions a
  day is $518 versus $293.
- Peak context also sets **latency**: prefilling 32,000 tokens costs about
  3413 ms of compute against 128 ms for 1200. Every one of those milliseconds
  happens *before the first output token appears*.
- And it sets **memory**: 4.194 GB of KV cache at 32k tokens, 16.777 GB at
  128k — per concurrent request.

!!! tip "The other half of the saving is free"

    Notice that `SYSTEM_AND_TOOLS` is identical on every call. With prefix
    caching ([Section 27.1](../ch27-inference/01-kv-cache.md)) the server
    skips prefilling it entirely after the first time — *provided you keep it
    at the front and byte-identical*. We come back to this at the end of the
    section, because it is the single most commonly wasted optimization in
    agent code.

## A twenty-turn conversation, and four ways to shrink it

Every strategy below runs against the same fake conversation. The token
counter is the rule of thumb from
[Section 26.1](../ch26-llm-internals/01-tokenization.md) — about four
characters per token for English — implemented as a real function so the
numbers are reproducible.

```python
CONVERSATION = [
    ("user", "Hi! I'm Rosa, I work on the Atlas ingestion service and I'm in UTC+1."),
    ("assistant", "Nice to meet you, Rosa. What can I help with on Atlas today?"),
    ("user", "Ingestion is failing on big uploads. Where do I start?"),
    ("assistant", "Check the batch size first: Atlas rejects batches over 64 "
                  "documents with a 413."),
    ("user", "How do I see the current setting?"),
    ("assistant", "It lives in atlas.yaml under ingest.batch_size."),
    ("user", "Found it, it says 200. Can I just edit that?"),
    ("assistant", "Yes, but the new value only takes effect after a restart of "
                  "the service."),
    ("user", "Okay. Please always give me commands for zsh, not bash."),
    ("assistant", "Noted, I'll use zsh syntax from now on."),
    ("user", "What happens to the batches that already failed?"),
    ("assistant", "Each batch retries three times with backoff, then goes to the "
                  "dead-letter queue."),
    ("user", "Can I replay the dead-letter queue?"),
    ("assistant", "Yes, the replay tool re-enqueues messages in arrival order."),
    ("user", "Does any of this touch Beacon?"),
    ("assistant", "No. Beacon is the search API; it shares the Postgres cluster "
                  "but not the pipeline."),
    ("user", "Good. Unrelated: my teammate Ivan owns the billing job."),
    ("assistant", "Understood, Ivan owns Cinder, the nightly billing job at 02:00 UTC."),
    ("user", "Right. Now, what time will the restart finish in my timezone?"),
    ("assistant", "A restart takes about two minutes, so start it whenever suits you."),
]

def tok(text):
    """Stand-in tokenizer: one token per 4 characters (Section 26.1's rule)."""
    return [text[i:i + 4] for i in range(0, len(text), 4)]

def n_tokens(text):
    return len(tok(text))

def sliding_window(turns, budget):
    """Strategy 1: keep the most recent turns that fit. Forget the rest."""
    kept, used = [], 0
    for role, text in reversed(turns):
        cost = n_tokens(text)
        if used + cost > budget:
            break
        kept.append((role, text))
        used += cost
    return list(reversed(kept)), used

FACTS = {"user's name": "Rosa", "timezone": "UTC+1", "shell preference": "zsh"}

def facts_kept(turns):
    blob = " ".join(t for _, t in turns).lower()
    return [name for name, value in FACTS.items() if value.lower() in blob]

total = sum(n_tokens(t) for _, t in CONVERSATION)
print(f"{len(CONVERSATION)} turns, {total} tokens\n")
for budget in (60, 120, 240):
    kept, used = sliding_window(CONVERSATION, budget)
    print(f"budget {budget:>3}: {len(kept):>2} turns, {used:>3} tokens, "
          f"still knows {facts_kept(kept)}")
print(f"\nthe last question is: {CONVERSATION[-2][1]!r}")
```

The whole conversation is 290 tokens. A **sliding window** is the simplest
possible policy — keep the newest turns, drop the oldest — and it takes four
lines. Look at what it costs. At a 240-token budget the window keeps 16 of 20
turns and has already forgotten Rosa's name and her timezone; at 120 tokens it
knows none of the three facts. And the very last user question is *"what time
will the restart finish in my timezone?"*, whose answer requires the timezone
stated in **turn 0**. The sliding window's failure is not a rounding error. It
is structural: recency and importance are different things, and a window can
only see one of them.

### Strategy 2: summarize the old turns

Instead of deleting old turns, compress them. Ask the model to distil the
early part of the conversation into a handful of durable facts, then keep the
summary plus the recent turns verbatim.

```python
# continues
import re

class FakeSummarizer:
    """Scripted stand-in for 'ask the model to summarise these turns'.

    A real summariser is one API call with a prompt like "extract the durable
    facts". Ours is a table of patterns so the output is identical every run —
    but it does the same *job*: turn many conversational sentences into a few
    facts worth carrying forward.
    """
    RULES = [
        (r"I'm (\w+),", "the user is called {0}"),
        (r"UTC\+(\d+)", "the user's timezone is UTC+{0}"),
        (r"commands for (\w+), not", "the user wants {0} commands, not bash"),
        (r"over (\d+) documents with a (\d+)",
         "Atlas rejects batches over {0} documents ({1})"),
        (r"in (\S+\.yaml) under (\S+)\.", "batch size lives in {0} at {1}"),
        (r"after a restart", "batch-size changes need a restart"),
        (r"then goes to the dead-letter queue",
         "failed batches end in the dead-letter queue"),
        (r"(\w+) owns (\w+), the nightly billing job", "{1} is owned by {0}"),
    ]

    def __call__(self, turns):
        facts = []
        for _, text in turns:
            for pattern, template in self.RULES:
                m = re.search(pattern, text)
                if m:
                    facts.append("- " + template.format(*m.groups()))
        return "Earlier in this conversation:\n" + "\n".join(dict.fromkeys(facts))

summarize = FakeSummarizer()
old, recent = CONVERSATION[:14], CONVERSATION[14:]
summary = summarize(old)
print(summary)

before, after = sum(n_tokens(t) for _, t in old), n_tokens(summary)
kept_live = sum(n_tokens(t) for _, t in recent)
print(f"\n{before} tokens of history -> {after} tokens of summary "
      f"({before / after:.1f}x compression)")
print(f"context: {after} + {kept_live} = {after + kept_live} tokens "
      f"(was {sum(n_tokens(t) for _, t in CONVERSATION)})")
print("facts surviving:", facts_kept([("summary", summary)] + recent))
```

The 14 oldest turns collapse from 197 tokens to 78 — **2.5× compression** — and
crucially all three durable facts survive, because a summarizer keeps facts
while a window keeps *recency*. The total context drops from 290 to 171 tokens
while getting *more* useful.

Summarization has a cost the window does not: it needs an extra model call, it
adds latency at the moment it triggers, and it is lossy in a way you cannot
predict. Anything the summarizer failed to consider important is gone forever —
so real systems summarize *and* keep the raw turns in a store they can retrieve
from, which is exactly what the `AgentMemory` class at the end of this section
does.

### Strategy 3: score-based selection

A window ranks by recency. A summarizer ranks by whatever the model thought
mattered. A **scoring function** lets you say what you mean, by combining three
signals that pull in different directions:

$$
\text{score}(m) \;=\; w_r \cdot \underbrace{0.5^{\,\text{age}/h}}_{\text{recency}}
\;+\; w_v \cdot \underbrace{\frac{|Q \cap M|}{|Q|}}_{\text{relevance}}
\;+\; w_i \cdot \underbrace{\text{importance}}_{\text{assigned when stored}}
$$

Recency decays with a half-life $h$ measured in turns. Relevance is overlap
with the current query — the retrieval machinery of
[Section 29.1](01-embeddings-vector-search.md), simplified here to term
overlap. Importance is a number you attach when the memory is written: an
identity fact scores high forever, a passing remark does not.

```python
# continues
STOP = set("the a an of in to is are and or it its for with at on by that this "
           "i my me you your what how do does can be when not so will".split())

def terms(text):
    return {w for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in STOP}

MEMORIES = [                       # (text, importance, turns ago)
    ("the user is called Rosa", 0.9, 19),
    ("the user's timezone is UTC+1", 0.9, 19),
    ("the user wants zsh commands, not bash", 0.8, 11),
    ("Atlas rejects batches over 64 documents with a 413", 0.6, 16),
    ("batch-size changes need a restart", 0.6, 12),
    ("failed batches end in the dead-letter queue", 0.4, 8),
    ("Beacon is the search API and shares the Postgres cluster", 0.2, 4),
    ("Cinder is owned by Ivan and runs nightly at 02:00 UTC", 0.3, 2),
]

def score(text, importance, age, query, half_life=8.0):
    recency = 0.5 ** (age / half_life)
    q, m = terms(query), terms(text)
    relevance = len(q & m) / len(q) if q else 0.0
    return 0.25 * recency + 0.55 * relevance + 0.20 * importance, recency, relevance

QUERY = "what time will the restart finish in my timezone?"
rows = sorted(((score(*m, QUERY), m) for m in MEMORIES), key=lambda r: -r[0][0])
print(f"{'total':>6} {'recency':>8} {'relevance':>10} {'importance':>11}  memory")
for (total, recency, relevance), (text, importance, _) in rows:
    print(f"{total:>6.3f} {recency:>8.2f} {relevance:>10.2f} {importance:>11.2f}"
          f"  {text[:52]}")

print("\nby recency alone (what a sliding window would keep):")
for text, _, age in sorted(MEMORIES, key=lambda m: m[2])[:3]:
    print(f"   {age:>2} turns ago  {text[:52]}")
```

The scored ranking puts *"the user's timezone is UTC+1"* first, at 0.366 —
nineteen turns old and decayed to 0.19 on recency, but rescued by relevance
(0.25) and importance (0.90). A sliding window, ranking by recency alone, would
instead have kept the three newest memories, none of which mention a timezone.
That is the entire argument for scoring in one comparison.

The weights are a policy, not a discovery. Raise $w_i$ and the agent becomes
conservative and repetitive; raise $w_r$ and it becomes forgetful; raise $w_v$
and it becomes topic-obsessed and loses the thread. Tune them against a set of
scripted conversations with known "must not forget" facts, exactly as you tuned
$k$ in [Section 29.2](02-rag-pipeline.md).

### Strategy 4: hierarchical summary trees

A single summary is one level of detail for everything. A **summary tree**
keeps several: raw turns at the leaves, a short summary of every few turns
above them, a summary of the summaries above that. The agent loads the top
level always, and descends into a branch only when a query points at it — the
same "look at the index, then open the chapter" move as the IVF index in
[Section 29.1](01-embeddings-vector-search.md).

```python
# continues
def importance_of(fact):
    """A crude durability score: identity and configuration outlive incidents."""
    for keyword, weight in [("user", 0.9), ("Atlas", 0.6), ("restart", 0.6),
                            ("dead-letter", 0.4)]:
        if keyword in fact:
            return weight
    return 0.2

GROUP = 4
leaves = [CONVERSATION[i:i + GROUP] for i in range(0, len(CONVERSATION), GROUP)]
level1 = [summarize(g) for g in leaves]

all_facts = []
for s in level1:
    all_facts += [f for f in s.splitlines() if f.startswith("- ")]
level2 = "Overall:\n" + "\n".join(
    sorted(dict.fromkeys(all_facts), key=importance_of, reverse=True)[:3])

print("level 2 (always loaded):")
print(level2)
print(f"\n{'level':<9} {'nodes':>6} {'tokens':>7}")
print(f"{'leaves':<9} {len(CONVERSATION):>6} {sum(n_tokens(t) for _, t in CONVERSATION):>7}")
print(f"{'level 1':<9} {len(level1):>6} {sum(n_tokens(s) for s in level1):>7}")
print(f"{'level 2':<9} {1:>6} {n_tokens(level2):>7}")

query = "how do I replay failed batches?"
best = max(range(len(level1)), key=lambda i: len(terms(query) & terms(level1[i])))
zoom = n_tokens(level2) + sum(n_tokens(t) for _, t in leaves[best])
print(f"\nquery {query!r} -> descend into group {best}")
print(f"  root + that group only: {zoom} tokens, versus "
      f"{sum(n_tokens(t) for _, t in CONVERSATION)} for the whole transcript")
```

The tree costs 290 tokens at the leaves, 115 at level 1, and 27 at level 2. The
top level alone is not enough to answer a detailed question — it is a table of
contents — but combined with *one* descended branch it answers the dead-letter
question in 83 tokens instead of 290. Scale that up: a hierarchy over a year of
sessions lets an agent hold the gist of everything and the detail of exactly
what it needs. Note the honest cost, visible in the numbers: level 2 kept 3
facts out of the 8 the tree knows. **Every level up throws information away.**
The tree works because you keep the lower levels and can descend, not because
the summary is lossless.

## Keeping the prefix stable: the optimization nobody mentions

Now for a practical point that costs nothing and is almost never taught. A
server's prefix cache reuses KV entries for an *exact* token prefix
([Section 27.1](../ch27-inference/01-kv-cache.md)). So the order in which you
assemble a prompt determines how much of it has to be recomputed on every
single call. Put the stable material first — system prompt, tool definitions,
long documents — and the volatile material last — timestamps, the new user
turn. Put them the other way round and you invalidate everything.

```python
def tok(text):
    return [text[i:i + 4] for i in range(0, len(text), 4)]

def n_tokens(text):
    return len(tok(text))

SYSTEM = ("You are an on-call assistant for the Atlas, Beacon and Cinder "
          "services. Answer from the provided context. Cite chunk numbers. "
          "Never invent configuration values. Prefer zsh syntax. ") * 6
TOOLS = ("TOOL read_config(path) -> str | TOOL restart(service) -> status | "
         "TOOL search_logs(query, since) -> list[str] ") * 4
HISTORY = ["User: ingestion is failing.\nAssistant: check the batch size.\n",
           "User: where is it set?\nAssistant: atlas.yaml, ingest.batch_size.\n",
           "User: do I need a restart?\nAssistant: yes, after editing.\n"]
CLOCK = ["Current time: 09:41:02", "Current time: 09:41:57", "Current time: 09:42:31"]
NEW = ["User: how long does a restart take?",
       "User: can I replay the dead-letter queue?",
       "User: does this affect Beacon?"]

def stable_first(i):
    return SYSTEM + TOOLS + "".join(HISTORY[:i]) + CLOCK[i] + "\n" + NEW[i]

def volatile_first(i):
    return CLOCK[i] + "\n" + NEW[i] + "\n" + SYSTEM + TOOLS + "".join(HISTORY[:i])

def cached_tokens(previous, current):
    """How many leading tokens are byte-identical — exactly what a prefix cache reuses."""
    hits = 0
    for a, b in zip(tok(previous), tok(current)):
        if a != b:
            break
        hits += 1
    return hits

head = f"{'request':>8} {'tokens':>7} {'cached: stable first':>21} {'volatile first':>15}"
print(head)
print("-" * len(head))
paid_good = paid_bad = 0
for i in (1, 2):
    total = n_tokens(stable_first(i))
    good = cached_tokens(stable_first(i - 1), stable_first(i))
    bad = cached_tokens(volatile_first(i - 1), volatile_first(i))
    paid_good += total - good
    paid_bad += n_tokens(volatile_first(i)) - bad
    print(f"{i:>8} {total:>7} {good:>21} {bad:>15}")

print(f"\nprefill tokens actually paid for: stable-first {paid_good}, "
      f"volatile-first {paid_bad} ({paid_bad / paid_good:.1f}x more)")
```

Same content, same information, same answer — and the volatile-first layout
recomputes **13.4×** more prompt tokens, because one timestamp at the top makes
every following token a cache miss. Request 1 reuses 380 of its 412 tokens in
the good layout and 5 of them in the bad one.

The rule that falls out is simple and worth writing on the wall of your prompt
builder:

1. system prompt (never changes),
2. tool definitions (change on deploy),
3. retrieved documents and long-lived memories (change per session),
4. conversation history (append-only),
5. the new user turn and anything time-varying (changes every call).

Anything that violates that order — a timestamp in the system prompt, a tool
list you sort by a dictionary's iteration order, a memory block you rebuild
from scratch each turn — silently costs you the cache.

## Writing memories: what to store, and what to do when it changes

Reading memory is the easy half. Writing it well requires three decisions.

**What to store.** Store *durable* things: identity, preferences, stable
configuration, decisions and their reasons, corrections the user made. Do not
store the whole transcript as "memories" — you will drown the scorer in noise.
A useful test: would this still be true and useful next month?

**Dedup.** The same fact restated should refresh recency, not add a row.
Otherwise a preference the user mentions five times outvotes everything else.

**Conflict.** When a new value contradicts an old one, the default rule is
**newer overrides older**, keeping the old value as history rather than
deleting it — you will want it when someone asks why the agent changed its
mind.

```python
def write_memory(store, key, value, turn, importance=0.5):
    """Insert (key, value). Identical writes refresh; different values supersede."""
    old = store.get(key)
    if old is None:
        store[key] = {"value": value, "turn": turn,
                      "importance": importance, "history": []}
        return f"NEW       {key} = {value!r}"
    if old["value"] == value:
        old["turn"] = turn                        # refresh recency, store nothing new
        return f"DUPLICATE {key} (refreshed to turn {turn})"
    history = old["history"] + [(old["turn"], old["value"])]
    store[key] = {"value": value, "turn": turn,
                  "importance": importance, "history": history}
    return f"UPDATED   {key}: {old['value']!r} -> {value!r} (old value kept)"

store = {}
WRITES = [("user.name", "Rosa", 1, 0.9), ("user.timezone", "UTC+1", 1, 0.9),
          ("user.shell", "bash", 3, 0.8), ("user.name", "Rosa", 6, 0.9),
          ("user.shell", "zsh", 9, 0.8), ("atlas.batch_limit", "64", 4, 0.5),
          ("user.timezone", "UTC+2", 18, 0.9)]
for key, value, turn, importance in WRITES:
    print(" ", write_memory(store, key, value, turn, importance))

print("\nfinal store:")
for key, rec in sorted(store.items()):
    was = (f"   (was {rec['history'][-1][1]!r} at turn {rec['history'][-1][0]})"
           if rec["history"] else "")
    print(f"  {key:<18} = {rec['value']!r:<8} turn {rec['turn']:>2}{was}")

THRESHOLD = 0.4

def retention(rec, now, half_life=10.0):
    """Forgetting must respect importance, or you lose the user's name first."""
    decay = 0.5 ** ((now - rec["turn"]) / half_life)
    return 0.4 * decay + 0.6 * rec["importance"], decay

print(f"\nat turn 30, half-life 10 turns, forget below {THRESHOLD}:")
for key, rec in sorted(store.items(), key=lambda kv: -retention(kv[1], 30)[0]):
    weighted, decay = retention(rec, 30)
    verdict = lambda x: "keep" if x >= THRESHOLD else "FORGET"
    print(f"  {key:<18} decay only {decay:.3f} -> {verdict(decay):<6} | "
          f"importance-weighted {weighted:.3f} -> {verdict(weighted)}")
```

Read the last block carefully, because it contains a trap that real systems
fall into. **Decay by recency alone forgets the wrong things.** At turn 30 the
user's name has decayed to 0.189, and a threshold of 0.4 on recency alone
deletes it — along with their shell preference — while keeping a timezone
merely because it was restated recently. Weighting the decay by importance —
here $0.4 \times \text{decay} + 0.6 \times \text{importance}$ — keeps all three
identity facts (0.616, 0.573, 0.714) and drops only `atlas.batch_limit` at
0.366, which is exactly the outcome you wanted. Forgetting is a feature;
forgetting by age alone is a bug.

## Putting it together: the `AgentMemory` class

Here is the centrepiece: one class holding all three stores, with three
methods. `remember()` writes, with dedup and newer-overrides-older.
`recall(query)` ranks across stores with the scoring function. And
`build_context(budget_tokens)` assembles a prompt that **provably fits** the
budget, laid out in the cache-friendly order.

```python
import re

def tok(text):
    return [text[i:i + 4] for i in range(0, len(text), 4)]

def n_tokens(text):
    return len(tok(text))

STOP = set("the a an of in to is are and or it its for with at on by that this "
           "i my me you your what how do does can be when not so will".split())

def terms(text):
    return {w for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in STOP}

class AgentMemory:
    """Working + episodic + semantic memory behind three methods."""

    def __init__(self, system_prompt, half_life=10.0):
        self.system_prompt = system_prompt
        self.half_life = half_life
        self.clock = 0
        self.working = []      # recent verbatim turns, in order
        self.episodic = []     # summaries of past stretches or sessions
        self.semantic = {}     # key -> one durable fact; newer wins

    # ---------------- writing ----------------
    def remember(self, text, kind="working", importance=0.5, key=None):
        self.clock += 1
        item = {"text": text, "turn": self.clock, "importance": importance}
        if kind == "working":
            self.working.append(item)
            return "stored"
        if kind == "episodic":
            self.episodic.append(item)
            return "stored"
        if kind == "semantic":
            key = key or text
            old = self.semantic.get(key)
            if old and old["text"] == text:
                old["turn"] = self.clock                 # duplicate: refresh only
                return "duplicate"
            item["superseded"] = old["text"] if old else None
            self.semantic[key] = item
            return "updated" if old else "new"
        raise ValueError(f"unknown memory kind: {kind!r}")

    # ---------------- scoring ----------------
    def _score(self, item, query):
        recency = 0.5 ** ((self.clock - item["turn"]) / self.half_life)
        q, m = terms(query), terms(item["text"])
        relevance = len(q & m) / len(q) if q else 0.0
        return 0.25 * recency + 0.55 * relevance + 0.20 * item["importance"]

    def recall(self, query, k=3):
        pool = list(self.semantic.values()) + self.episodic
        ranked = sorted(pool, key=lambda i: -self._score(i, query))
        return [(i["text"], round(self._score(i, query), 3)) for i in ranked[:k]]

    # ---------------- reading ----------------
    def build_context(self, query, budget_tokens, memory_share=0.5, verbose=True):
        """Assemble a prompt guaranteed to fit in budget_tokens.

        Layout: system prompt, then memories, then live turns, then the
        question — the cache-friendly order from Section 27.1.
        """
        question, header = f"User: {query}", "What you remember:"
        fixed = sum(n_tokens(t) for t in (self.system_prompt, question, header))
        if fixed >= budget_tokens:
            raise ValueError("budget cannot hold the system prompt and the question")
        spare = budget_tokens - fixed
        memory_budget = int(spare * memory_share)

        chosen, dropped, left = [], [], memory_budget
        for text, _ in self.recall(query, k=len(self.semantic) + len(self.episodic)):
            line = f"- {text}"
            if n_tokens(line) <= left:
                chosen.append(line)
                left -= n_tokens(line)
            else:
                dropped.append(line)

        window, left = [], spare - memory_budget + left      # unspent memory budget
        for item in reversed(self.working):                  # newest first while it fits
            if n_tokens(item["text"]) > left:
                dropped.append(item["text"])
                break
            window.append(item["text"])
            left -= n_tokens(item["text"])
        window.reverse()

        def assemble():
            return "\n".join([self.system_prompt, "", header, *chosen, "",
                              *window, question])

        while window and n_tokens(assemble()) > budget_tokens:   # newlines cost too
            dropped.append(window.pop(0))
        context = assemble()
        if verbose:
            print(f"budget {budget_tokens} -> used {n_tokens(context)} tokens; "
                  f"{len(chosen)} memories, {len(window)} live turns, "
                  f"{len(dropped)} dropped")
            for line in context.splitlines():
                if line:
                    print(f"   {n_tokens(line):>3}t  {line[:66]}")
        return context

mem = AgentMemory("You are an on-call assistant. Cite sources. Use zsh.")
mem.remember("the user is called Rosa", "semantic", 0.9, key="user.name")
mem.remember("the user's timezone is UTC+1", "semantic", 0.9, key="user.timezone")
mem.remember("the user wants zsh commands, not bash", "semantic", 0.8, key="user.shell")
mem.remember("Atlas rejects batches over 64 documents with a 413", "semantic", 0.6,
             key="atlas.batch_limit")
mem.remember("Session 1: debugged an Atlas failure caused by batch size 200.",
             "episodic", 0.5)
mem.remember("Session 2: walked through replaying the dead-letter queue.",
             "episodic", 0.4)
for line in ["User: does any of this touch Beacon?",
             "Assistant: no, Beacon is the search API and shares only Postgres.",
             "User: my teammate Ivan owns the billing job.",
             "Assistant: understood, Ivan owns Cinder, nightly at 02:00 UTC."]:
    mem.remember(line, "working")

QUERY = "what time will the restart finish in my timezone?"
print("recall:")
for text, s in mem.recall(QUERY):
    print(f"   {s:.3f}  {text}")

print()
mem.build_context(QUERY, 120)
print()
mem.build_context(QUERY, 70)

print("\nwriting the same fact again  ->",
      mem.remember("the user is called Rosa", "semantic", 0.9, key="user.name"))
print("writing a contradicting fact ->",
      mem.remember("the user's timezone is UTC+2", "semantic", 0.9, key="user.timezone"))
print("the superseded value is kept:", mem.semantic["user.timezone"]["superseded"])
```

Read the 70-token run against the sliding window from earlier in this section.
The window at *240* tokens had already lost the timezone. `AgentMemory` at
**70** tokens still has it — first line of the memory block — because it ranked
by relevance and importance rather than by position in a list. That is the
whole chapter's argument, reduced to two printouts: retrieval is what lets a
small context behave like a large one.

Three properties worth noticing in the implementation:

- **The budget is a guarantee, not a hope.** The final `while` loop drops the
  oldest live turn until the assembled string genuinely fits, because newlines
  and headers cost tokens too. Estimating a budget and then blowing it is the
  most common bug in context builders.
- **`memory_share` is the one real design knob.** At 0.5 the memory block and
  the live conversation each get half of the spare budget. Push it to 0.9 and
  the agent recites facts at you; push it to 0.1 and it forgets who you are.
- **Semantic memory is keyed, the others are appended.** That is what makes
  dedup and newer-overrides-older possible at all: `user.timezone` names a
  *slot*, and a slot can be updated. An append-only log cannot contradict
  itself, which sounds nice until you need the current answer.

!!! warning "Common mistakes"

    - **Trusting a sliding window.** It is four lines and it will lose the
      user's name, their language, and the constraint they gave you in turn 2.
      Any agent that must remember anything needs a store outside the window.
    - **Storing every turn as a "memory".** Retrieval quality collapses when
      the store is 95% conversational filler. Store distilled facts; keep raw
      turns separately if you need them.
    - **Forgetting by age alone.** Recency decay deletes identity facts before
      it deletes yesterday's noise. Weight retention by importance, or exempt
      semantic memory from decay entirely.
    - **Rebuilding the prompt prefix every turn.** Reordered tool lists,
      regenerated timestamps, and freshly formatted memory blocks all break
      prefix caching for the entire rest of the prompt — a 13× prefill bill in
      the demo above, for no benefit.
    - **Estimating tokens and never checking.** "About four characters per
      token" is a planning rule, not a measurement. Before you ship, count
      with the real tokenizer and leave headroom for the model's reply.

## Check your understanding

1. An agent keeps the last 3000 tokens of conversation and nothing else. A
   user says in turn 2 "never suggest force-pushing", and in turn 40 the agent
   suggests force-pushing. Which memory type was missing, and what should have
   been stored?

    ??? success "Answer"
        Semantic memory — a durable, keyed fact such as
        `user.constraints.no_force_push = True`, written with high importance
        the moment the user said it. Working memory (the window) is the wrong
        home for a standing constraint: it is ranked by recency, so the
        constraint aged out while remaining just as true. The general rule is
        that anything still true next month belongs outside the window.

2. Your prompt is: retrieved documents, then the system prompt, then tool
   definitions, then the conversation, then a timestamp, then the user's new
   message. What is wrong with this order?

    ??? success "Answer"
        The two most stable blocks — system prompt and tool definitions — are
        not at the front, so they cannot be reused from a prefix cache once
        the retrieved documents change (which they do every query). Move them
        first, then long-lived memory, then history, then the new turn. The
        timestamp is fine where it is, right before the volatile user message;
        putting it at the top, as many systems do "for context", would cost
        you every cache hit for the whole prompt.

3. Why does the score-based selector rank "the user's timezone is UTC+1" above
   memories from two turns ago?

    ??? success "Answer"
        Because recency is only one of three terms. That memory's recency has
        decayed to 0.19 after nineteen turns, but it scores 0.25 on relevance
        (the query shares the word "timezone") and 0.90 on importance
        (identity facts are marked durable when written), so the weighted sum
        $0.25 \times 0.19 + 0.55 \times 0.25 + 0.20 \times 0.90 = 0.366$ beats a
        recent but irrelevant, unimportant memory. A sliding window has no way to
        express any of that.

4. `build_context` ends with a `while` loop that pops turns until the string
   fits. Why is that loop necessary when every piece was already measured?

    ??? success "Answer"
        Because the pieces are measured individually but assembled with
        separators — newlines, the blank lines, and the `What you remember:`
        header — and joining changes where the 4-character token boundaries
        fall. Summing the parts is an estimate of the whole; the only way to
        guarantee the budget is to measure the assembled string and trim until
        it fits. The same applies with a real tokenizer, for the same reason:
        tokenization is not additive across concatenation.
