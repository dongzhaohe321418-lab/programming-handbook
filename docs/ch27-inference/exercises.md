# Chapter 27 · Exercises

## The chapter in brief

- Generating without a **KV cache** re-projects every earlier token at every
  step, which is $\Theta(n^2)$ work where $\Theta(n)$ would do
  ([27.1](01-kv-cache.md)).
- The cache stores **K and V only** — per token, per layer, per KV head — and
  it changes the output by nothing at all.
- The KV cache removes *redundant* work; it does **not** make attention
  linear, because the score total is $\Theta(n^2)$ even with a perfect cache.
- Cache size is one multiplication you can do from a `config.json`, and
  $H_{kv}$ is the term architects cut with **GQA** and **MQA**.
- **Prefill is compute-bound and decode is memory-bandwidth-bound**, which is
  why one unbatched user leaves the GPU's multipliers idle ~99% of the time.
- **Prefix caching** reuses the K and V of a shared prompt across requests,
  so stable text belongs at the *top* of a prompt and volatile text at the
  bottom.
- **Batching** is free up to the compute-bound crossover, and costly past it —
  the same lever raises throughput and lowers per-user speed
  ([27.2](02-batching.md)).
- **Continuous batching** refills a slot the moment a sequence finishes,
  which converts static batching's head-of-line blocking into useful work.
- **PagedAttention** is OS paging applied to the KV cache: fixed-size blocks
  kill fragmentation and let identical prefixes share physical memory.
- **Chunked prefill** stops one long prompt from freezing everyone else's
  token stream, for a few percent of extra TTFT.
- **TTFT, ITL, TPOT, and throughput are different numbers** that move in
  different directions; streaming shortens the *perceived* wait without
  changing E2E latency at all ([27.3](03-latency-streaming.md)).
- **Quantization** trades precision for memory, and grouping is what makes
  4 bits survive outliers — measure the quality cost on your own task
  ([27.4](04-quantization-deploy.md)).

### Key terms

| Term | One-clause reminder |
| --- | --- |
| [KV cache](../appendix/E-ai-glossary.md) | Stored keys and values so old tokens are never re-projected |
| [Prefill](../appendix/E-ai-glossary.md) | Processing the whole prompt at once; compute-bound |
| [Decode](../appendix/E-ai-glossary.md) | Producing one token per step; memory-bandwidth-bound |
| [Prefix caching](../appendix/E-ai-glossary.md) | Reusing the cached blocks of a prompt prefix shared across requests |
| [GQA / MQA](../appendix/E-ai-glossary.md) | Fewer KV heads than query heads, so the cache shrinks proportionally |
| [Continuous batching](../appendix/E-ai-glossary.md) | Scheduling per iteration instead of per batch |
| Head-of-line blocking | A short request held hostage by the longest member of its batch |
| [PagedAttention](../appendix/E-ai-glossary.md) | Fixed-size KV blocks plus a block table — virtual memory for the cache |
| Chunked prefill | Splitting a long prompt across steps so decoders never stall |
| [TTFT](../appendix/E-ai-glossary.md) | Time to first token: queueing plus prefill |
| [TPOT](../appendix/E-ai-glossary.md) | Time per output token: the mean gap between tokens |
| [Throughput](../appendix/E-ai-glossary.md) | Output tokens per second across all users, set mostly by batch size |
| [SSE](../appendix/E-ai-glossary.md) | Server-Sent Events, the plain-HTTP wire format that carries a token stream |
| [Quantization](../appendix/E-ai-glossary.md) | Storing weights in fewer bits, with a scale per group |
| [GGUF / GPTQ / AWQ / NF4](../appendix/E-ai-glossary.md) | The four quantized-model ecosystems you will actually download |

The [concept index](../concept-index.md) links each of these to the section
that derives it.

Now the problems.

Eight problems on the arithmetic and the scheduling of LLM inference. They
build on [27.1](01-kv-cache.md), [27.2](02-batching.md),
[27.3](03-latency-streaming.md), and [27.4](04-quantization-deploy.md), and
every solution runs in the browser. Exercise 27.2 asks you to *predict* the
output before running it — do that honestly; the gap between your prediction
and the printed answer is the part that teaches.

Nothing here needs a GPU, a network, or a real model. Where numbers stand in
for hardware they are labelled illustrative, and you are meant to change them.

---

### Exercise 27.1 — KV cache arithmetic (●)

Three model shapes are on the table for a product that needs an 8192-token
context and must serve 16 concurrent users:

| Model | Layers | KV heads | $d_{head}$ |
| --- | --- | --- | --- |
| A — 7B, multi-head attention | 32 | 32 | 128 |
| B — 8B, grouped-query (8 KV heads) | 32 | 8 | 128 |
| C — 70B, grouped-query (8 KV heads) | 80 | 8 | 128 |

Write `kv_gb(layers, kv_heads, d_head, tokens, batch)` for fp16 and print, for
each model: bytes per token, GB for one 8192-token request, and GB for 16 of
them. Which of the three fit their KV cache in a 40 GB budget at that
concurrency? Then compute, for each, the largest batch that does fit.

??? success "Solution"

    ```python
    BYTES_PER = 2                      # fp16
    GB = 1e9

    def kv_gb(layers, kv_heads, d_head, tokens, batch=1):
        """2 (K and V) x layers x KV heads x head dim x tokens x batch x bytes."""
        return 2 * layers * kv_heads * d_head * tokens * batch * BYTES_PER / GB

    MODELS = [("A  7B MHA", 32, 32, 128),
              ("B  8B GQA-8", 32, 8, 128),
              ("C  70B GQA-8", 80, 8, 128)]
    CTX, USERS, BUDGET_GB = 8192, 16, 40.0

    hdr = (f"{'model':<14}{'B/token':>9}{'1 user GB':>11}{'16 users GB':>13}"
           f"{'fits 40GB?':>12}{'max batch':>11}")
    print(hdr)
    print("-" * len(hdr))
    for name, L, H, dh in MODELS:
        per_token = kv_gb(L, H, dh, 1) * GB
        one = kv_gb(L, H, dh, CTX)
        many = kv_gb(L, H, dh, CTX, USERS)
        print(f"{name:<14}{per_token:>9,.0f}{one:>11.2f}{many:>13.2f}"
              f"{('yes' if many <= BUDGET_GB else 'NO'):>12}"
              f"{int(BUDGET_GB / one):>11}")

    print(f"\nA vs B: {kv_gb(32, 32, 128, CTX) / kv_gb(32, 8, 128, CTX):.0f}x "
          f"more cache for the same layer count — only H_kv changed.")
    ```

    Only model B fits 16 users in 40 GB. Model A needs 68.72 GB for the same
    job because its 32 KV heads cost exactly 4× model B's 8, and model C needs
    42.95 GB because 80 layers cost 2.5× model B's 32. The formula is linear in
    every one of its terms, which makes this kind of sizing pure multiplication
    — and it is the calculation to do *before* choosing a model, not after.

---

### Exercise 27.2 — Predict the redundant work (●)

A request has a 100-token prompt and generates 50 tokens. Read this code and
write down three numbers **before you run it**: how many token-vectors get
pushed through the projection matrices without a cache, how many with a
cache, and the ratio.

```text
def projections(prompt, new):
    no_cache = sum(prompt + s for s in range(new))
    cached = new
    return no_cache, cached, no_cache / cached

a, b, r = projections(100, 50)
print(f"no cache: {a}   cached: {b}   ratio: {r}")
```

Then: does the ratio go up or down if the prompt is 2000 tokens instead
of 100, and why?

??? success "Solution"

    ```python
    def projections(prompt, new):
        """Token-vectors pushed through the weight matrices while generating."""
        no_cache = sum(prompt + s for s in range(new))   # whole prefix, every step
        cached = new                                     # one new token per step
        return no_cache, cached, no_cache / cached

    a, b, r = projections(100, 50)
    print(f"no cache: {a}   cached: {b}   ratio: {r}")

    print(f"\n{'prompt':>8}{'no cache':>12}{'cached':>9}{'ratio':>9}")
    for prompt in [100, 500, 2000, 8000]:
        a, b, r = projections(prompt, 50)
        print(f"{prompt:>8}{a:>12,}{b:>9}{r:>9.1f}x")
    print("\nclosed form: no_cache = new*prompt + new*(new-1)/2")
    print("check for (100, 50):", 50 * 100 + 50 * 49 // 2)
    ```

    **6225, 50, and 124.5.** The no-cache count is $50 \times 100$ for the
    prompt re-processed fifty times, plus $1+2+\dots+49 = 1225$ for the tokens
    generated along the way. Longer prompts make the ratio *worse*, because
    the term that grows is the one multiplied by the prompt length: at a
    2000-token prompt the ratio is 2024.5×. That is why the KV cache matters
    most in exactly the settings people care about — long system prompts, long
    documents, long conversations.

---

### Exercise 27.3 — Which scheduler wins? (●●)

A service handles a mix of two long generations and six short ones:
output lengths `[200, 8, 12, 6, 250, 10, 9, 7]`, batch capacity 4, all
arriving at once. Before coding, predict which scheduling strategy has the
bigger advantage here compared with the eight-request example in Section
27.2, and why.

Then implement both `static_batching` and `continuous_batching` and print
makespan, slot utilisation, and mean latency for each.

??? success "Solution"

    ```python
    LENS, CAPACITY, STEP_MS = [200, 8, 12, 6, 250, 10, 9, 7], 4, 25.0

    def static_batching(lens, capacity):
        done, t = [0] * len(lens), 0
        for b in range(0, len(lens), capacity):
            group = list(range(b, min(b + capacity, len(lens))))
            t += max(lens[i] for i in group)    # the batch ends with its longest
            for i in group:
                done[i] = t                     # the whole batch returns together
        return done, t

    def continuous_batching(lens, capacity):
        waiting, active, done, t = list(range(len(lens))), {}, [0] * len(lens), 0
        while waiting or active:
            while waiting and len(active) < capacity:
                i = waiting.pop(0)
                active[i] = lens[i]
            t += 1
            for i in list(active):
                active[i] -= 1
                if active[i] == 0:
                    done[i] = t
                    del active[i]
        return done, t

    print(f"{'strategy':<14}{'makespan':>10}{'utilisation':>13}{'mean latency':>14}")
    for name, (done, mk) in [("static", static_batching(LENS, CAPACITY)),
                             ("continuous", continuous_batching(LENS, CAPACITY))]:
        util = 100 * sum(LENS) / (CAPACITY * mk)
        mean = STEP_MS * sum(done) / len(done)
        print(f"{name:<14}{mk:>10}{util:>12.1f}%{mean:>12.0f}ms")

    d_s, _ = static_batching(LENS, CAPACITY)
    d_c, _ = continuous_batching(LENS, CAPACITY)
    print(f"\nthe 6-token request finishes at step {d_s[3]} (static) "
          f"vs {d_c[3]} (continuous)")
    ```

    Continuous batching wins by far more here than in Section 27.2's example,
    because the *variance* in output length is far larger: a 6-token request
    sharing a static batch with a 200-token one waits 200 steps for an answer
    it had after 6. Variance in output length is the entire source of
    continuous batching's advantage — which is also why a benchmark that gives
    every request the same `max_tokens` will show almost no difference, and
    should not be trusted.

---

### Exercise 27.4 — Read TTFT and TPOT off a timeline (●●)

A server logged the wall-clock millisecond at which each token of one
response reached the client. The request was submitted at $t = 0$:

```text
token  1 at   842 ms        token  6 at   902 ms
token  2 at   854 ms        token  7 at   914 ms
token  3 at   866 ms        token  8 at   926 ms
token  4 at   878 ms        token  9 at   938 ms
token  5 at   890 ms        token 10 at  1490 ms
```

Compute TTFT, every inter-token latency, TPOT (the mean ITL), and E2E
latency. One ITL is wildly out of line — what would cause that in a real
server, and which metric would hide it?

??? success "Solution"

    ```python
    import numpy as np

    arrivals = [842, 854, 866, 878, 890, 902, 914, 926, 938, 1490]  # ms since submit

    ttft = arrivals[0]
    itls = [b - a for a, b in zip(arrivals, arrivals[1:])]
    tpot = sum(itls) / len(itls)
    e2e = arrivals[-1]

    print(f"TTFT           : {ttft} ms")
    print(f"ITLs           : {itls}")
    print(f"TPOT (mean ITL): {tpot:.1f} ms")
    print(f"median ITL     : {np.median(itls):.1f} ms")
    print(f"p90 ITL        : {np.percentile(itls, 90):.1f} ms")
    print(f"E2E            : {e2e} ms")
    print(f"check: TTFT + TPOT x (N-1) = "
          f"{ttft + tpot * (len(arrivals) - 1):.0f} ms")
    print(f"\nnormalised time per output token (E2E / N): "
          f"{e2e / len(arrivals):.1f} ms — a different convention!")
    ```

    TTFT is 842 ms, the steady ITL is 12 ms, and one gap is 552 ms. The mean
    (TPOT = 72 ms) is dragged six-fold by that single stall while the median
    stays at 12 ms — so reporting only TPOT hides *when* the problem happens,
    and reporting only the median hides *that* it happened. A 552 ms stall in
    a real server is the signature of another request's long prefill running
    as one indivisible step, which is exactly what chunked prefill
    ([Section 27.2](02-batching.md)) exists to prevent. Track p90/p99 ITL, not
    just the mean.

---

### Exercise 27.5 — Parse a messy SSE stream (●●)

Here is a raw Server-Sent Events stream with everything a real one throws at
you: heartbeat comments, an `id:` field you should ignore, an event whose
`data:` is split across two lines, an `event: error` that is not a content
delta, and the `[DONE]` sentinel.

Write a parser that returns the concatenated assistant text and, separately,
any error events. It must not crash on the error event and must not treat
`[DONE]` as JSON.

??? success "Solution"

    ```python
    import json

    RAW = (
        ": ping\n\n"
        "id: 1\n"
        "data: {\"delta\": {\"content\": \"Continuous\"}}\n\n"
        "id: 2\n"
        "data: {\"delta\": {\"content\": \" batching\"}}\n\n"
        ": ping\n\n"
        "data: {\"delta\": {\"content\":\n"
        "data:  \" refills a slot\"}}\n\n"
        "event: error\n"
        "data: {\"message\": \"upstream timeout\", \"retryable\": true}\n\n"
        "data: {\"delta\": {\"content\": \" every step.\"}}\n\n"
        "data: [DONE]\n\n"
    )

    def parse_sse(raw):
        """Yield (event_name, joined_data) for each dispatched SSE event."""
        name, data = "message", []
        for line in raw.replace("\r\n", "\n").split("\n"):
            if line == "":
                if data:
                    yield name, "\n".join(data)
                name, data = "message", []
            elif line.startswith(":"):
                continue                                  # heartbeat comment
            else:
                field, _, value = line.partition(":")
                value = value[1:] if value.startswith(" ") else value
                if field == "data":
                    data.append(value)
                elif field == "event":
                    name = value
                # 'id' and 'retry' are ignored by this client

    text, errors = [], []
    for name, payload in parse_sse(RAW):
        if payload == "[DONE]":
            break
        obj = json.loads(payload)
        if name == "error":
            errors.append(obj)
        else:
            text.append(obj["delta"]["content"])

    print("events parsed :", len(text) + len(errors))
    print("assistant text:", repr("".join(text)))
    print("errors        :", errors)
    ```

    The two details that break naive parsers are both here. The split payload
    is only valid JSON *after* the two `data:` lines are joined with a newline
    — JSON treats that newline as ordinary whitespace. And `[DONE]` is not
    JSON at all, so it must be checked before `json.loads`. Note also that
    dispatch happens on the blank line, not on the `data:` line, which is what
    makes multi-line payloads possible in the first place.

---

### Exercise 27.6 — Quantize and measure (●●)

Take a seeded array of 2048 weights drawn from $\mathcal{N}(0, 0.02)$ with
four planted outliers. Quantize it to int8 with one scale for the whole
tensor, and to int4 with group sizes 256, 64, and 16. For each, print the
relative error, the effective bits per weight (remember the fp16 scales), and
the compression versus fp32. Then find the smallest number of effective bits
per weight that keeps the relative error under 15%.

??? success "Solution"

    ```python
    import numpy as np

    def quantize(w, bits, group):
        q_max = 2 ** (bits - 1) - 1
        g = w.reshape(-1, group)
        scales = np.abs(g).max(axis=1, keepdims=True) / q_max
        scales = np.where(scales == 0.0, 1e-12, scales)
        return np.clip(np.round(g / scales), -q_max, q_max), scales

    def round_trip(w, bits, group):
        q, s = quantize(w, bits, group)
        approx = (q * s).reshape(w.shape).astype(np.float32)
        rel = 100 * float(np.linalg.norm(w - approx) / np.linalg.norm(w))
        return rel, bits + 16 / group

    rng = np.random.default_rng(11)
    W = rng.normal(0, 0.02, size=2048).astype(np.float32)
    W[[5, 300, 1200, 2000]] = [0.4, -0.45, 0.38, -0.41]      # planted outliers

    print(f"{'scheme':<20}{'rel. error':>12}{'bits/weight':>13}{'vs fp32':>9}")
    rows = [("int8, one scale", 8, 2048), ("int4, group 256", 4, 256),
            ("int4, group  64", 4, 64), ("int4, group  32", 4, 32),
            ("int4, group  16", 4, 16)]
    for label, bits, group in rows:
        rel, eff = round_trip(W, bits, group)
        print(f"{label:<20}{rel:>11.2f}%{eff:>13.2f}{32 / eff:>8.1f}x")

    print("\nsmallest budget that stays under 15% relative error:")
    best = None
    for bits in (4, 8):
        for group in (2048, 512, 256, 128, 64, 32, 16):
            rel, eff = round_trip(W, bits, group)
            if rel < 15.0 and (best is None or eff < best[0]):
                best = (eff, bits, group, rel)
    print(f"  int{best[1]}, group {best[2]}: {best[0]:.2f} bits/weight, "
          f"{best[3]:.2f}% error")
    ```

    The answer is **int4 with groups of 16, at 5.00 effective bits per
    weight** and 12.09% error; group 32 (4.50 bits) just misses the target at
    15.82%. Two things are worth noticing. Group size matters more than bit
    width over part of this range — int4 at group 256 (40.80% error, 4.06
    bits) is far worse than int4 at group 16 for less than a bit of savings,
    because four outliers in 2048 weights ruin any block big enough to contain
    one. And int8 with a single scale reaches 3.76% error but spends 8.01
    bits, so the 15% budget lets you keep three bits per weight. Bits alone
    never tell you the quality of a quantization scheme; the blocking scheme
    does at least as much work.

---

### Exercise 27.7 — Will it fit? (●●)

Write `fits(gpu_gb, params, bits_per_weight, layers, kv_heads, d_head,
context, batch)` that returns the total memory needed (weights + KV cache +
1.5 GB of overhead) and whether it fits. Use it to answer: on a single 24 GB
GPU, running a 13B model (40 layers, 40 KV heads, $d_{head}=128$) at 4.5
effective bits per weight, what is the largest context length you can offer
at a batch size of 8? And what happens to that answer at fp16?

??? success "Solution"

    ```python
    GB, OVERHEAD_GB = 1e9, 1.5

    def needed_gb(params, bits, layers, kv_heads, d_head, context, batch):
        weights = params * bits / 8 / GB
        kv = 2 * layers * kv_heads * d_head * context * batch * 2 / GB   # fp16 KV
        return weights + kv + OVERHEAD_GB

    def max_context(gpu_gb, params, bits, layers, kv_heads, d_head, batch):
        """Largest power-of-two-ish context that still fits."""
        for ctx in [131072, 65536, 32768, 16384, 8192, 4096, 2048, 1024, 512]:
            if needed_gb(params, bits, layers, kv_heads, d_head, ctx, batch) <= gpu_gb:
                return ctx
        return 0

    GPU, PARAMS, L, H, DH, BATCH = 24.0, 13e9, 40, 40, 128, 8
    print(f"{'precision':<12}{'weights GB':>12}{'max ctx @ batch 8':>20}{'total GB':>11}")
    for label, bits in [("fp16", 16.0), ("int8", 8.125), ("int4", 4.5)]:
        ctx = max_context(GPU, PARAMS, bits, L, H, DH, BATCH)
        w = PARAMS * bits / 8 / GB
        if ctx == 0:
            print(f"{label:<12}{w:>12.1f}{'does not fit':>20}{'—':>11}")
        else:
            total = needed_gb(PARAMS, bits, L, H, DH, ctx, BATCH)
            print(f"{label:<12}{w:>12.1f}{ctx:>20}{total:>11.1f}")

    print(f"\nKV cost for this model: "
          f"{2 * L * H * DH * 2 / 1e6:.3f} MB per token per sequence")
    print(f"at batch 8 that is {8 * 2 * L * H * DH * 2 / 1e6:.2f} MB per token")
    ```

    At 4.5 bits the weights take 7.3 GB, leaving about 15.2 GB for cache —
    enough for a **2048-token context at batch 8**, since this model burns
    0.819 MB of KV per token per sequence and therefore 6.55 MB per token
    across the batch (2048 tokens × 6.55 MB = 13.4 GB). At int8 the weights
    are 13.2 GB and the answer drops to 1024 tokens; at fp16 the weights alone
    are 26 GB, so nothing fits on a 24 GB card at any context length. Notice
    how quickly the KV term takes over:
    quantizing the weights bought room that the cache then spends, which is
    why context length, batch size, and precision have to be chosen together.

---

### Exercise 27.8 — A priority-aware scheduler (●●●)

The continuous-batching simulator of Section 27.2 admits waiting requests in
arrival order. Real servers often need classes of service: an interactive
chat request should not sit behind a queue of long batch jobs.

Replace the FIFO waiting list with a **priority queue** built on `heapq`
([Section 21.2](../ch21-heaps/02-priority-queues.md)), keyed on
`(priority_class, arrival_time, request_id)` so that ties break
deterministically. Requests arrive over time, so the scheduler must also
release newly arrived requests into the queue at the right step. Run the same
workload under both policies and report mean latency for each class.

Does priority scheduling improve *total* throughput? Explain the result.

??? success "Solution"

    ```python
    import heapq

    CAPACITY, STEP_MS = 4, 25.0
    # (id, arrival step, class: 0 = interactive / 1 = batch, output tokens)
    REQUESTS = [(0, 0, 1, 120), (1, 0, 1, 90), (2, 0, 1, 150), (3, 0, 1, 110),
                (4, 0, 1, 130), (5, 0, 1, 95), (6, 0, 1, 140), (7, 0, 1, 105),
                (8, 5, 0, 8), (9, 10, 0, 6), (10, 15, 0, 10), (11, 20, 0, 7)]

    def simulate(requests, capacity, use_priority):
        pending = sorted(requests, key=lambda r: r[1])      # by arrival
        queue, active, done, t, i = [], {}, {}, 0, 0
        while i < len(pending) or queue or active:
            while i < len(pending) and pending[i][1] <= t:  # arrivals become eligible
                rid, arr, cls, out = pending[i]
                key = (cls, arr, rid) if use_priority else (arr, rid)
                heapq.heappush(queue, (key, rid, out))
                i += 1
            while queue and len(active) < capacity:         # admit best-first
                _, rid, out = heapq.heappop(queue)
                active[rid] = out
            t += 1
            for rid in list(active):
                active[rid] -= 1
                if active[rid] == 0:
                    done[rid] = t
                    del active[rid]
        return done, t

    print(f"{'policy':<12}{'interactive':>14}{'batch':>10}{'makespan':>11}"
          f"{'throughput':>13}")
    for label, prio in [("FIFO", False), ("priority", True)]:
        done, mk = simulate(REQUESTS, CAPACITY, prio)
        lat = {c: [] for c in (0, 1)}
        for rid, arr, cls, _ in REQUESTS:
            lat[cls].append(STEP_MS * (done[rid] - arr))
        tput = sum(r[3] for r in REQUESTS) / (mk * STEP_MS / 1000)
        print(f"{label:<12}{sum(lat[0]) / len(lat[0]):>12.0f}ms"
              f"{sum(lat[1]) / len(lat[1]):>8.0f}ms{mk:>11}{tput:>10.0f} t/s")
    ```

    Priority scheduling cuts mean interactive latency from 5238 ms to
    2394 ms — a 2.2× improvement, because those four short requests jump the
    queue instead of waiting behind four long batch jobs — while mean batch
    latency rises only from 4406 ms to 4503 ms, since a short request occupies
    a slot for a handful of steps. But **total throughput (149 tokens/s) and
    makespan (260 steps) are identical**: the same tokens are generated and
    the batch is just as full either way. Priority reallocates *who waits*; it
    does not create capacity. That is the honest summary of most scheduling
    work, and the reason a scheduler change should always be evaluated on
    per-class latency rather than aggregate tokens per second.

    Two extensions worth trying. First, add **starvation protection** by
    ageing the key — subtract a small amount from the priority class for every
    step a request has waited — so a flood of interactive traffic cannot
    freeze the batch queue forever. Second, add **preemption**: allow the
    scheduler to evict a running batch job (dropping or swapping out its KV
    cache) to make room immediately, and measure how much interactive latency
    that buys and how much recomputation it costs.
