# Chapter 27 · Serving Models — Inference Infrastructure

[Chapter 26](../ch26-llm-internals/index.md) built a language model: tokens in,
attention, a stack of decoder blocks, a sampled token out. It answered *what a
model computes*. This chapter answers a different question, and it is the one
that decides whether your application is usable: **what does it cost to run
that computation thousands of times per second, for hundreds of users at
once?** The answer has almost nothing to do with machine learning and almost
everything to do with the material of Parts I–IV — memory layout, Big-O,
caching, queues, and scheduling. When people say "vLLM is fast", they are not
saying it found a better model. They are saying it manages memory and
schedules work better.

The central fact of this chapter is that generating text is done **one token
at a time**, and each token requires reading the model's entire weight matrix
out of memory. That single sentence generates the whole field. It means a
naive implementation redoes almost all of its work every step (fixed by the
**KV cache**, Section 27.1). It means a single request leaves the hardware
almost completely idle (fixed by **batching**, Section 27.2). It means there
are two different latencies users feel, and optimizing one hurts the other
(Section 27.3). And it means memory is the binding constraint, so shrinking
the numbers themselves buys you capacity (**quantization**, Section 27.4).

Everything here is arithmetic you can run. We cannot import `vllm` — the
Run buttons on this site execute Python in your browser with no GPU and no
network — but we do not need to. Every claim in this chapter is either a
counting argument, a formula with a calculator attached, or a simulation you
can edit. Where a real command is the honest answer (`vllm serve`,
`ollama run`), it appears in a plain text box with no Run button, described
accurately and without pinning a version. Where numbers describe hardware,
they are clearly labelled as the illustrative constants they are — change
them to match your machine and rerun.

**After this chapter you can …**

- explain why generating token $n$ without a cache re-computes work for all
  $n-1$ earlier tokens, and count exactly how much;
- say precisely what a KV cache stores (K and V, per layer, per KV head, per
  token) and compute its size in GB for a real model configuration;
- predict when a GPU will run out of memory from context length and batch
  size alone, and explain why GQA and MQA help;
- distinguish the **prefill** phase (compute-bound) from the **decode** phase
  (memory-bandwidth-bound) and show the arithmetic that makes each true;
- explain head-of-line blocking in static batching and why **continuous
  batching** fixes it, with a simulation you can rerun;
- describe **PagedAttention** as virtual memory for the KV cache, and quantify
  the fragmentation it removes;
- define TTFT and TPOT precisely, compute end-to-end latency from them, and
  explain the throughput-versus-latency tradeoff as a curve, not a slogan;
- read and parse the Server-Sent Events wire format that carries a token
  stream to a browser;
- quantize a weight array to int8 and int4 by hand, measure the reconstruction
  error, and state honestly what quality it costs;
- choose between GGUF, GPTQ, AWQ, and NF4 for a given deployment, and size a
  model against a given amount of memory.

**Prerequisites:** [Chapter 26](../ch26-llm-internals/index.md) (tokens,
attention, the decoder stack, sampling) is required — we reuse its numpy
attention directly, and Section 26.3's GQA and KV-memory arithmetic is the
starting point for Section 27.1. From Part IV you need
[Section 16.1](../ch16-complexity/01-big-o.md) (Big-O, and the habit of
counting operations before reaching for a stopwatch) and
[Section 23.2](../ch23-os/02-memory-layout.md) (a process's address space and
how memory gets laid out — PagedAttention extends that story with the OS
notion of paging, introduced here in Section 27.2).
[Section 21.2](../ch21-heaps/02-priority-queues.md) returns in the hardest
exercise, and [Section 5.1](../ch05-under-the-hood/01-numeric-pitfalls.md)
plus [Section 0.2](../ch00-machine/02-binary.md) (floating point and bits)
underpin Section 27.4.

**Sections**

- [27.1 The KV cache](01-kv-cache.md) — the single most important
  optimization in LLM serving: what is redundant, what gets cached, how big
  the cache grows, and why long contexts blow up your GPU.
- [27.2 Batching, PagedAttention, chunked prefill](02-batching.md) — why one
  request wastes a GPU, how static batching stalls, how continuous batching
  and paged KV memory fix it, and what a real server startup looks like.
- [27.3 Latency, throughput, and streaming](03-latency-streaming.md) — TTFT
  and TPOT defined properly, the throughput/latency curve, and the wire
  format that delivers tokens to a browser one at a time.
- [27.4 Quantization and deployment](04-quantization-deploy.md) — fewer bits
  per number, measured honestly: a working quantizer, a sizing table, the
  format landscape, and a decision flowchart.
- [Exercises](exercises.md) — KV arithmetic, scheduling predictions, timeline
  reading, an SSE parse, a quantizer, and a priority-queue scheduler.
