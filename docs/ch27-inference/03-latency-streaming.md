# 27.3 Latency, throughput, and streaming

"Is it fast?" is not a question about an LLM service; it is at least three
questions, and they have different answers that often point in opposite
directions. The person waiting for a chatbot to start typing cares about one
number. The person paying the GPU bill cares about a different one. The
engineer choosing a batch size is trading one against the other, whether they
know it or not. This section defines the metrics precisely, computes them
from the machinery of Sections 27.1 and 27.2, plots the tradeoff that every
serving decision lives on, and then builds the actual wire protocol that
carries tokens to a browser one at a time.

## Three numbers, defined precisely

!!! abstract "In plain words"

    - **What it is.** "Fast" splits into two clocks: **TTFT**, how long until
      the first token appears, and **TPOT**, how long between each token after
      that.
    - **Picture it.** Ordering at a café. TTFT is the wait from ordering until
      the barista sets down your first item; TPOT is the pace at which the rest
      of the order keeps arriving. A quick first cup with slow refills feels
      completely different from a long initial wait followed by a flood.
    - **Why it matters.** The two respond to different things — TTFT to prompt
      length and queueing, TPOT to model size and memory bandwidth — and they
      often move in opposite directions. A single "latency" number hides which
      one your users are actually feeling.

Loose talk about "latency" causes most confusion in this area, so here are
the definitions serving teams actually use:

| Metric | Definition | Set mostly by |
| --- | --- | --- |
| **TTFT** (time to first token) | request submitted → first token reaches the client | queueing + prefill: prompt length, batch pressure |
| **ITL** (inter-token latency) | gap between two consecutive tokens | one decode step: model size, memory bandwidth, batch size |
| **TPOT** (time per output token) | the *mean* ITL over a response | the same, averaged |
| **E2E latency** | request submitted → last token | all of the above plus output length |
| **Throughput** | output tokens per second across *all* users | batch size |

TTFT and TPOT come from the two phases of Section 27.1: TTFT is dominated by
**prefill**, which is compute-bound and grows with prompt length; TPOT is a
**decode** step, which is memory-bandwidth-bound and barely depends on prompt
length at all. Because the first token arrives at TTFT and each of the
remaining $N-1$ tokens costs one TPOT:

$$
\text{E2E} \;=\; \text{TTFT} \;+\; \text{TPOT} \times (N_{\text{out}} - 1)
$$

Read aloud: the end-to-end time is the wait for the first token, plus one
per-token time for each of the remaining tokens after it.

!!! note "The $N-1$ matters less than the convention"
    Some tools report a *normalised* time per output token,
    $\text{E2E} / N_{\text{out}}$, which folds TTFT into the average. Both are
    defensible; they differ by a lot on short responses and by nothing on long
    ones. When you compare two systems, check which one each tool means — a
    "faster TPOT" that is really a normalised figure on a 10-token response is
    measuring TTFT in disguise.

## A latency calculator for real workloads

The two phases have different formulas, so build both and let the workload
choose. Prefill processes $P$ prompt tokens in one shot (or a few chunks);
decode processes one token per step per sequence.

```python
PARAMS, W_BYTES = 7e9, 2               # 7B model, fp16
BANDWIDTH, COMPUTE = 2.0e12, 150e12    # bytes/s, FLOP/s — illustrative constants
QUEUE_MS = 15.0                        # illustrative scheduler + network overhead

weights = PARAMS * W_BYTES
t_mem = 1e3 * weights / BANDWIDTH      # ms to stream the weights once

def prefill_ms(prompt_tokens, batch=1):
    """Compute-bound: 2 FLOPs per parameter per token, weights read once."""
    return max(t_mem, 1e3 * 2 * PARAMS * prompt_tokens * batch / COMPUTE)

def decode_ms(batch=1):
    """Memory-bound until the batch grows past the crossover."""
    return max(t_mem, 1e3 * 2 * PARAMS * batch / COMPUTE)

def e2e(prompt, out, batch=1):
    ttft = QUEUE_MS + prefill_ms(prompt, batch)
    tpot = decode_ms(batch)
    return ttft, tpot, ttft + tpot * (out - 1)

WORKLOADS = [                      # (name, prompt tokens, output tokens)
    ("code completion", 512, 24),
    ("chat turn", 700, 250),
    ("RAG answer", 4000, 200),
    ("document summary", 16000, 500),
]
hdr = (f"{'workload':<18}{'prompt':>8}{'out':>6}{'TTFT ms':>9}{'TPOT ms':>9}"
       f"{'E2E s':>8}{'TTFT share':>12}")
print(hdr)
print("-" * len(hdr))
for name, p, o in WORKLOADS:
    ttft, tpot, total = e2e(p, o)
    print(f"{name:<18}{p:>8,}{o:>6}{ttft:>9.0f}{tpot:>9.1f}{total / 1000:>8.2f}"
          f"{100 * ttft / total:>11.0f}%")
```

The `TTFT share` column is the design lesson, and it says something different
for each row:

- **Chat turn — 4% TTFT.** Almost pure decode, so TPOT is the number to
  optimise, and batching hurts it.
- **Document summary — 30% TTFT.** A full 1.5 seconds of a five-second request
  producing nothing at all: precisely the dead air users complain about.
  Prefix caching and chunked prefill target exactly this row.
- **Code completion — 28% TTFT.** The whole request is only 224 ms, so the
  63 ms before the first token is the difference between an editor that feels
  instant and one that feels laggy.

Same model, three different problems.

Notice also how differently the two phases scale with prompt length. Going
from a 512-token prompt to a 16,000-token one takes TTFT from 63 ms to
1508 ms — the prefill term is exactly linear in prompt length, 31× — while
TPOT does not move at all, because decode reads the same weights regardless.
(A real system's TPOT does creep up with context, since attention must read a
longer KV cache each step; this model leaves that out.)

## Throughput versus latency: the curve, not the slogan

!!! abstract "In plain words"

    - **What it is.** Throughput is total tokens per second across *everyone*;
      per-user latency is the speed *one* person sees. Pushing one up past a
      point drags the other down.
    - **Picture it.** A restaurant kitchen. Seating more diners at once gets
      more meals out the door per hour (throughput), but past the point where
      the cooks are already flat out, every single diner waits longer for their
      plate (latency). No table count is best for both at once.
    - **Why it matters.** Batch size is that dial. This is why serving targets
      are written as "keep first-token time under 500 ms *and* per-token time
      under 50 ms, at the most throughput that still meets both" — not "make it
      fast".

Section 27.2 showed batching buying throughput for free up to the
compute-bound crossover. Plot both metrics against batch size and you get the
picture that every capacity-planning conversation is really about.

```python
import numpy as np
import matplotlib.pyplot as plt

PARAMS, BANDWIDTH, COMPUTE = 7e9, 2.0e12, 150e12     # illustrative
t_mem = 1e3 * PARAMS * 2 / BANDWIDTH

batches = np.array([1, 2, 4, 8, 16, 32, 64, 96, 128, 192, 256, 384, 512])
step = np.maximum(t_mem, 1e3 * 2 * PARAMS * batches / COMPUTE)   # ms per step
throughput = 1000 * batches / step                               # tokens/s total
per_user = 1000 / step                                           # tokens/s each

print(f"{'batch':>6}{'step ms':>9}{'total tok/s':>13}{'per user tok/s':>16}")
for b, s, tp, pu in zip(batches, step, throughput, per_user):
    print(f"{b:>6}{s:>9.2f}{tp:>13,.0f}{pu:>16.1f}")

knee = int(batches[np.argmax(throughput > 0.95 * throughput.max())])
print(f"\nthroughput reaches 95% of its ceiling at batch {knee}; "
      f"per-user speed there is {1000 / np.maximum(t_mem, 1e3 * 2 * PARAMS * knee / COMPUTE):.0f} tok/s")

fig, ax1 = plt.subplots(figsize=(7, 4))
ax1.plot(batches, throughput, marker="o", color="tab:blue", label="total tok/s")
ax1.set_xscale("log", base=2)
ax1.set_xlabel("batch size (log scale)")
ax1.set_ylabel("throughput: total output tokens/s", color="tab:blue")
ax1.tick_params(axis="y", labelcolor="tab:blue")

ax2 = ax1.twinx()
ax2.plot(batches, per_user, marker="s", color="tab:red", label="per-user tok/s")
ax2.set_ylabel("latency: tokens/s seen by one user", color="tab:red")
ax2.tick_params(axis="y", labelcolor="tab:red")
ax1.set_title("Throughput and per-user speed pull in opposite directions")
fig.tight_layout()
```

The two curves cross, which is the entire story in one image:

- **Total throughput (blue)** climbs steeply, then bends over and saturates
  once the step becomes compute-bound.
- **Per-user speed (red)** is a flat plateau while the step time is pinned to
  the memory floor, then falls away as $1/\text{batch}$.

**There is no batch size that maximises both.** What you *can* find is the
knee:

- **Batch 64** delivers 9,143 tok/s — 85% of the ceiling — while every user
  still gets the full 142.9 tok/s.
- **Batch 96** is where throughput first reaches 95% of its ceiling, and a
  user is down to 112 tok/s.
- **Batch 128** buys 17% more throughput than 64 and costs each user 41% of
  their speed.

Whether that last trade is a good one is a product decision, not a technical
one, which is the point.

This is why serving configurations are stated as service-level objectives,
not as "make it fast": *"p95 TTFT under 500 ms and TPOT under 50 ms, at the
highest throughput that satisfies both"* is a question the curve can answer.
"Make it fast" is not.

## Streaming: latency you feel versus latency you measure

Now the part that changes user experience without changing a single number
above. A response that takes 5 seconds can feel like a 5-second wait or like
a 0.7-second wait, depending entirely on whether the tokens are delivered as
they are produced. People read at roughly 4–5 words per second; a model
emitting 143 tokens per second produces text faster than anyone can read it.
So after the first token arrives, the user is never waiting again — they are
reading, and the model stays ahead of them.

```python
TTFT_MS, TPOT_MS = 700.0, 7.0        # from the calculator above
N_OUT = 500                          # tokens in the answer
TOKENS_PER_WORD = 1.3                # English averages ~1.3 tokens per word
READ_WPS = 4.5                       # words per second a person reads

e2e_ms = TTFT_MS + TPOT_MS * (N_OUT - 1)
words = N_OUT / TOKENS_PER_WORD
read_ms = 1000 * words / READ_WPS

print(f"generation finishes at {e2e_ms / 1000:.2f} s "
      f"({words:.0f} words, {N_OUT} tokens)")
print(f"reading {words:.0f} words takes about {read_ms / 1000:.1f} s\n")

print(f"{'':<14}{'first text on screen':>22}{'user finishes reading':>24}")
print(f"{'buffered':<14}{e2e_ms / 1000:>21.2f}s"
      f"{(e2e_ms + read_ms) / 1000:>23.1f}s")
print(f"{'streamed':<14}{TTFT_MS / 1000:>21.2f}s"
      f"{max(e2e_ms, TTFT_MS + read_ms) / 1000:>23.1f}s")

print(f"\nperceived wait: {e2e_ms / TTFT_MS:.1f}x shorter when streamed")
gen_rate = 1000 / TPOT_MS / TOKENS_PER_WORD
print(f"model writes {gen_rate:.0f} words/s, reader consumes {READ_WPS} words/s "
      f"-> generation stays {gen_rate / READ_WPS:.0f}x ahead")
```

Nothing was made faster: E2E latency is identical in both rows, because it is
the same computation. But the streamed reader starts at 0.70 s instead of
4.19 s — a **6.0× shorter perceived wait** — and finishes the whole
interaction sooner too, because reading overlaps generation instead of
following it.

Note that this block computes a timeline; it never actually sleeps. Simulating
time is how you reason about latency without wasting any.

The catch is worth stating: streaming means committing to tokens as they are
produced. You cannot post-process, re-rank, or retract text you have already
sent, which is why moderation and structured-output validation are harder in
a streaming pipeline than a buffered one.

## Server-Sent Events: the wire format

Tokens reach the browser over **Server-Sent Events** (SSE), a small,
old, plain-text HTTP protocol: the server responds with
`Content-Type: text/event-stream` and then keeps the connection open,
writing events as they occur. Every major LLM API's streaming mode is SSE.
The format is deliberately trivial — lines of `field: value`, and a **blank
line dispatches the event**:

```text
HTTP/1.1 200 OK
Content-Type: text/event-stream
Cache-Control: no-cache

: this is a comment, used as a keep-alive heartbeat

data: {"choices":[{"delta":{"role":"assistant"}}]}

data: {"choices":[{"delta":{"content":"Paged"}}]}

data: {"choices":[{"delta":{"content":" attention"}}]}

data: [DONE]
```

Four rules cover almost everything:

1. **A line beginning with `:` is a comment.** Servers send these periodically
   so proxies do not time the connection out.
2. **A single leading space after the colon is stripped** — exactly one.
3. **Multiple `data:` lines in one event are joined with a newline.**
4. **A blank line ends the event** and dispatches it.

The `[DONE]` sentinel is not part of SSE. It is a convention popularised by the
OpenAI API and copied widely, including by vLLM's compatible endpoint.

Why SSE rather than something more modern? Because the traffic is one-way
and the protocol is ordinary HTTP:

| | SSE | WebSocket | Polling |
| --- | --- | --- | --- |
| Direction | server → client only | full duplex | client asks, repeatedly |
| Protocol | plain HTTP/1.1 or /2 | HTTP upgrade to `ws://` | plain HTTP |
| Proxies, CDNs, auth headers | work unchanged | often need configuration | work unchanged |
| Auto-reconnect | built into the browser API | you write it | trivial but wasteful |
| Payload | UTF-8 text only | text or binary | anything |
| Right for | token streams, progress, logs | chat rooms, collaboration, games | slow-changing status |

Token generation is strictly one-directional after the request is sent, so
the extra machinery of WebSockets buys nothing.

## Writing the parser

A parser for this is real, useful, and about twenty lines. Here it is,
running against a hard-coded stream — no network involved, so the Run button
works exactly like a production client would:

```python
import json

RAW_STREAM = (
    ": keep-alive\n"
    "\n"
    "event: message\n"
    "data: {\"choices\": [{\"delta\": {\"role\": \"assistant\"}}]}\n"
    "\n"
    "data: {\"choices\": [{\"delta\": {\"content\": \"Paged\"}}]}\n"
    "\n"
    "data: {\"choices\": [{\"delta\": {\"content\": \"Attention\"}}]}\n"
    "\n"
    "data: {\"choices\": [{\"delta\": {\"content\": \" is\"}}]}\n"
    "\n"
    "data: {\"choices\": [{\"delta\": {\"content\": \" paging\"}}]}\n"
    "\n"
    ": keep-alive\n"
    "\n"
    "data: {\"choices\": [{\"delta\": {\"content\": \".\"}},\n"
    "data:   {\"finish_reason\": \"stop\"}]}\n"
    "\n"
    "data: [DONE]\n"
    "\n"
)

def parse_sse(raw):
    """Yield (event_name, data) pairs from a Server-Sent Events stream."""
    event, data_lines = "message", []
    for line in raw.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        if line == "":                             # blank line: dispatch
            if data_lines:
                yield event, "\n".join(data_lines)
            event, data_lines = "message", []
            continue
        if line.startswith(":"):                   # comment / heartbeat
            continue
        field, _, value = line.partition(":")
        if value.startswith(" "):                  # strip ONE leading space
            value = value[1:]
        if field == "data":
            data_lines.append(value)
        elif field == "event":
            event = value
        # 'id' and 'retry' fields exist too; ignored here

pieces = []
for name, payload in parse_sse(RAW_STREAM):
    if payload == "[DONE]":
        print(f"[{name}] stream closed by the server")
        break
    obj = json.loads(payload)
    delta = obj["choices"][0].get("delta", {})
    text = delta.get("content", "")
    pieces.append(text)
    print(f"[{name}] {str(delta):<45} -> {text!r}")

print("\nreassembled:", repr("".join(pieces)))
print("chunks received:", len(pieces))
```

Three things in that stream are there on purpose:

- **The keep-alive comments** are skipped without producing an event.
- **The first event carries a `role` and no `content`**, so it contributes an
  empty string. Clients must tolerate deltas with no text.
- **The final content event is split across two `data:` lines.** Joining them
  with a newline yields valid JSON, because JSON ignores whitespace between
  tokens.

Handle those three cases and you have a correct client.

## Backpressure and cancellation

Two operational realities live at this boundary, and they are mirror images of
each other.

**Backpressure** is what happens when the model produces tokens faster than
the client can accept them — a mobile connection, a slow browser tab, a
downstream service. The kernel's socket buffer fills and writes start
blocking. A server that does not handle that either stalls a GPU worker on a
network write or grows an unbounded in-memory queue until it runs out of RAM.
Production servers therefore bound the per-connection queue and treat a
persistently blocked client as a disconnection.

**Cancellation** is the other direction. When a user closes the tab or hits
stop, the HTTP connection drops, and the server must notice and evict that
sequence from the running batch. This matters more than it sounds: an
abandoned generation that runs to `max_tokens` occupies a batch slot and its
whole KV cache for nothing, which is pure lost throughput in the exact
currency Section 27.2 was counting. Every serious client library exposes
cancellation — an `AbortController` in the browser, a cancelled task in
Python — and every serious server acts on it.

## The browser side

For completeness, here is a browser consuming the stream. TypeScript, not
Python, because this code runs in a page — it is illustrative and does not
have a Run button:

```typescript
const controller = new AbortController();   // lets the user hit "stop"

const response = await fetch("/v1/chat/completions", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ model: "local", messages, stream: true }),
  signal: controller.signal,
});

const reader = response.body!.getReader();
const decoder = new TextDecoder();
let buffer = "";

while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  buffer += decoder.decode(value, { stream: true });

  // Events are separated by a blank line; keep any partial tail in the buffer.
  const events = buffer.split("\n\n");
  buffer = events.pop() ?? "";

  for (const event of events) {
    for (const line of event.split("\n")) {
      if (!line.startsWith("data:")) continue;      // skip ": heartbeat"
      const payload = line.slice(5).trimStart();
      if (payload === "[DONE]") return;
      const delta = JSON.parse(payload).choices[0].delta;
      if (delta.content) appendToScreen(delta.content);
    }
  }
}
```

The `buffer` logic is the part people get wrong: a network chunk has nothing
to do with an SSE event boundary, so a `read()` can hand you half an event.
Splitting on `\n\n` and keeping the last fragment for next time is the fix —
the same "incremental parse over a stream of unknown chunking" pattern you
met reading files line by line in
[Chapter 11](../ch11-files/02-read-write.md).

!!! warning "Common mistakes"

    - **Reporting one "latency" number.** TTFT and TPOT respond to different
      changes and often move in opposite directions; a single average hides
      the regression your users actually feel.
    - **Benchmarking at batch 1.** It measures the best latency your hardware
      can give and the worst throughput, so it predicts neither production
      cost nor production speed. Always report the batch size and the
      concurrency alongside the numbers.
    - **Assuming one SSE chunk equals one token.** Servers may coalesce
      deltas, and a network read may split an event in half. Parse the
      protocol; do not count `read()` calls.
    - **Forgetting `[DONE]` is a convention, not a standard.** Some endpoints
      signal completion with `finish_reason` and simply close the connection.
      Handle both, and treat a closed connection as the end.
    - **Ignoring cancellation.** An abandoned request that keeps generating
      holds a batch slot and its KV cache to the token limit — throughput you
      paid for and threw away.

## Check your understanding

1. A request has TTFT = 900 ms, TPOT = 20 ms, and produces 40 tokens. What is
   the E2E latency, and what fraction is TTFT? Would you optimise prefill or
   decode?

    ??? success "Answer"
        $900 + 20 \times 39 = 1680$ ms, of which TTFT is $900/1680 = 54\%$.
        More than half of the wall-clock time happens before the first token,
        so prefill and queueing are the target — a shorter prompt, prefix
        caching, or less queue pressure. Halving TPOT would save only 390 ms;
        halving TTFT saves 450 ms and improves the *perceived* responsiveness
        far more, because it is the wait the user actually experiences.

2. Your throughput doubles when you raise the batch size from 64 to 256, and
   users start complaining. What did the second curve do?

    ??? success "Answer"
        Per-user speed fell. Above the compute-bound crossover the step time
        grows linearly with batch size, so each user's tokens arrive
        proportionally slower — in the plotted numbers, from 143 tok/s at
        batch 64 to 42 tok/s at batch 256. Throughput and per-user latency are
        the two ends of one lever; the right batch size is the largest one
        that still satisfies your TPOT objective.

3. In the SSE stream, why does the parser skip lines beginning with `:`, and
   why does it join multiple `data:` lines with a newline rather than
   concatenating them directly?

    ??? success "Answer"
        A line starting with `:` is a comment — servers send them as
        heartbeats so intermediaries do not close an idle connection — and by
        the spec it produces no event. Multiple `data:` lines are the format's
        way of carrying multi-line payloads, and the spec says they are joined
        with `\n`; direct concatenation would silently corrupt any payload
        that genuinely contained line breaks.

4. Streaming does not reduce E2E latency at all. Why is it nevertheless the
   single biggest perceived-speed improvement available to a chat product?

    ??? success "Answer"
        Because the user's wait ends at the *first* token, not the last. In
        the block above that is 0.70 s instead of 4.19 s, a 6× shorter
        perceived wait, and since the model generates about 110 words per
        second while a person reads about 4.5, generation stays permanently
        ahead of the reader — so after the first token there is no waiting
        left to feel.
