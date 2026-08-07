# Appendix E · AI engineering glossary

The vocabulary of [Part V](../part5-overview.md), defined the way this
handbook uses it. Each entry links to the section that teaches the idea
properly — the definition is the reminder, the chapter is the lesson.

Where a word also has an ordinary programming meaning, the entry says so and
points at [Appendix C](C-glossary.md), the general glossary. That happens
more often than you would like: a *reference* model is not a reference, a
decoder *stack* is not a call stack, and an LLM *token* is not a lexical
token.

## A

**advantage**
:   How much better an action turned out than the baseline you expected —
    reward minus baseline. Subtracting a baseline leaves the direction of
    the update unchanged while shrinking its variance, which is why every
    modern policy-gradient method uses one. See
    [31.2](../ch31-rl/02-policy-gradient-ppo.md).

**agent**
:   A program in which a model repeatedly chooses an action, observes the
    result, and uses that observation to choose the next action, until it
    decides it is done or a budget runs out. The novelty is not the loop; it
    is that the *control flow* is data produced by the model at run time.
    See [30.1](../ch30-agents/01-agent-loop-react.md) and
    [Project 6](../projects/06-react-agent/README.md).

**agentic RL**
:   Reinforcement learning where an episode is a whole multi-step agent
    trajectory — tool calls, observations, and a final outcome — rather than
    a single response. The reward usually arrives only at the end, which
    makes credit assignment the hard part. See
    [31.4](../ch31-rl/04-reward-models.md) and
    [32.3](../ch32-data/03-trajectories.md).

**alignment**
:   Making a model's behaviour match what its developers and users actually
    want, rather than what raw next-token prediction produces. In practice
    it names the post-training stack: instruction tuning, then preference
    optimisation such as RLHF, DPO, or GRPO. See
    [Chapter 31](../ch31-rl/index.md).

**ANN index (approximate nearest neighbour)**
:   A data structure that finds *probably* the closest vectors to a query
    much faster than checking all of them, trading a little recall for a lot
    of speed. HNSW and IVF are the common families. See
    [29.1](../ch29-memory-rag/01-embeddings-vector-search.md).

**attention**
:   The operation that lets each position in a sequence read from every
    other position, weighted by a learned similarity: softmax of query·key
    scores, applied to values. It is the whole reason transformers replaced
    recurrent models. See
    [26.2](../ch26-llm-internals/02-attention.md).

**autoregressive**
:   Generating a sequence one element at a time, with each new element
    conditioned on everything produced so far. It is why generation cannot
    be parallelised across output tokens, and therefore why the KV cache and
    batching matter so much. See
    [27.1](../ch27-inference/01-kv-cache.md).

## B

**batching**
:   Running several requests through the model together so that one pass
    over the weights serves all of them. Since decoding is memory-bandwidth
    bound, batching buys throughput almost for free — up to the point where
    memory runs out. See [27.2](../ch27-inference/02-batching.md).

**beam search**
:   Keeping the $k$ best partial candidates at every step instead of
    committing to one. Classically a decoding strategy; the same idea
    reappears in agents as searching over *action* sequences rather than
    tokens. See [30.2](../ch30-agents/02-planning-reflection.md).

**benchmark**
:   A fixed, public dataset plus a scoring rule, used to compare systems on
    equal terms — MMLU, HumanEval, GSM8K, SWE-bench, GAIA. Necessary for
    comparability, insufficient for deciding whether *your* application
    works. See [33.1](../ch33-eval/01-benchmarks.md).

**BPE (byte-pair encoding)**
:   The tokenizer training algorithm that starts from bytes and repeatedly
    merges the most frequent adjacent pair into a new symbol. It is why
    common words are one token and rare ones fragment. See
    [26.1](../ch26-llm-internals/01-tokenization.md).

**Bradley-Terry model**
:   The statistical model behind preference learning: the probability that
    $y_w$ beats $y_l$ is $\sigma(r(y_w) - r(y_l))$, so only *differences* in
    reward are identifiable. It is what turns "A is better than B" labels
    into a trainable loss. See
    [31.4](../ch31-rl/04-reward-models.md).

## C

**chain-of-thought**
:   Having the model write out intermediate reasoning before its answer.
    It helps on multi-step problems because the intermediate text becomes
    part of the context the next tokens condition on. See
    [30.2](../ch30-agents/02-planning-reflection.md).

**chat template**
:   The exact string format — role markers and special tokens — that a
    particular instruction-tuned model was trained to expect. Using the
    wrong one silently degrades quality without raising any error. See
    [26.1](../ch26-llm-internals/01-tokenization.md).

**chunking**
:   Splitting documents into retrievable pieces before embedding them. The
    chunk boundary is a design decision with real consequences: too small
    and the answer is split across chunks, too large and the embedding
    averages away what made the passage relevant. See
    [29.1](../ch29-memory-rag/01-embeddings-vector-search.md).

**constrained decoding**
:   Restricting the sampler at each step to tokens that can still lead to a
    valid output — the mechanism that makes "always valid JSON" a guarantee
    rather than a hope. See
    [28.2](../ch28-tools-mcp/02-structured-output.md).

**contamination**
:   A benchmark's test items having appeared in a model's training data, so
    the score measures memorisation rather than ability. It inflates every
    affected number at once and leaves no visible trace in the report. See
    [33.1](../ch33-eval/01-benchmarks.md).

**context window**
:   The maximum number of tokens a model can attend to in one call —
    prompt plus generated output together. Every memory technique in
    [Chapter 29](../ch29-memory-rag/index.md) exists because this number is
    finite and you pay for it on every turn. See
    [26.1](../ch26-llm-internals/01-tokenization.md) and
    [29.3](../ch29-memory-rag/03-agent-memory.md).

**continuous batching**
:   Adding and removing requests from a running batch at token granularity,
    instead of waiting for every sequence in a batch to finish. It is the
    single biggest throughput win in modern serving. See
    [27.2](../ch27-inference/02-batching.md).

**cosine similarity**
:   The cosine of the angle between two vectors: the dot product divided by
    both lengths. It is the standard similarity for embeddings because it
    compares *direction* and ignores magnitude. See
    [29.1](../ch29-memory-rag/01-embeddings-vector-search.md).

**cross-encoder**
:   A model that reads the query and a candidate document *together* and
    scores the pair, rather than embedding each separately. Far more
    accurate and far too slow to run over a whole corpus, so it is used to
    rerank a shortlist. See
    [29.2](../ch29-memory-rag/02-rag-pipeline.md).

## D

**decoder-only**
:   The transformer architecture used by essentially every modern chat model:
    one stack of causally-masked blocks, no separate encoder. *Stack* here
    means a pile of identical layers — unrelated to the call stack or the
    stack ADT in [Appendix C](C-glossary.md). See
    [26.3](../ch26-llm-internals/03-decoder-stack.md).

**deduplication**
:   Removing near-identical examples from a training set. Duplicates waste
    compute, encourage memorisation, and quietly leak evaluation items into
    training. See [32.4](../ch32-data/04-filtering.md).

**distillation**
:   Training a small model on the outputs of a larger one, so the student
    inherits behaviour it could not have learned from raw data alone. The
    cheapest way to get most of a big model's quality at a small model's
    price. See [32.2](../ch32-data/02-synthetic-data.md).

**DPO (Direct Preference Optimization)**
:   Preference training with no reward model and no sampling: rearranging
    the RLHF optimum shows that any policy already *defines* a reward, so
    the objective collapses into a binary cross-entropy over preference
    pairs. See [31.3](../ch31-rl/03-dpo-grpo.md) and
    [Project 7](../projects/07-dpo-alignment/README.md).

## E

**embedding**
:   A fixed-length vector representing a piece of text, positioned so that
    similar meanings sit close together. Retrieval, clustering, and
    deduplication all reduce to arithmetic on these vectors. See
    [29.1](../ch29-memory-rag/01-embeddings-vector-search.md).

**environment**
:   In RL, everything outside the policy: it receives an action and returns
    an observation and a reward. For an LLM agent the environment is your
    tools, your filesystem, and the APIs it can reach. See
    [31.1](../ch31-rl/01-rl-basics.md) and
    [32.3](../ch32-data/03-trajectories.md).

**epsilon-greedy**
:   The simplest exploration rule: take the best-known action most of the
    time, and a uniformly random one with probability $\varepsilon$. It is
    the cheapest answer to the exploration-versus-exploitation problem, and
    often good enough. See [31.1](../ch31-rl/01-rl-basics.md).

**eval harness**
:   The program that turns a dataset, a model interface, and a scorer into a
    report: dataset → prompt → runner → scorer → aggregator → report. Build
    the small one before adopting a big one, or you cannot tell whether a
    printed number is real. See
    [33.2](../ch33-eval/02-eval-harness.md) and
    [Project 8](../projects/08-eval-harness/README.md).

**exact match**
:   Scoring an answer as correct only if it equals the reference string —
    after whatever normalisation you chose. That choice (case, punctuation,
    articles, whitespace) is not a detail; it is the metric. See
    [33.1](../ch33-eval/01-benchmarks.md).

## F

**few-shot**
:   Putting a handful of worked examples in the prompt so the model infers
    the task and the output format from them. Cheap, effective, and it costs
    context on every single call. See
    [33.1](../ch33-eval/01-benchmarks.md).

**FlashAttention**
:   An exact attention implementation that never materialises the full
    $n \times n$ score matrix, tiling the computation to keep it in fast
    on-chip memory. Same maths, dramatically less memory traffic. See
    [26.2](../ch26-llm-internals/02-attention.md).

**function calling**
:   The provider-level protocol where you send tool *schemas* with the
    prompt and the model replies with a structured, validated call instead
    of prose. Your program still executes it — the model only requests. See
    [28.1](../ch28-tools-mcp/01-function-calling.md).

## G

**GGUF, GPTQ, AWQ**
:   Concrete quantized-model formats and methods. GGUF is the file format
    used by llama.cpp and Ollama; GPTQ and AWQ are post-training
    quantization methods that pick weight scales to minimise the damage.
    See [27.4](../ch27-inference/04-quantization-deploy.md).

**GQA, MQA, MHA**
:   Three ways to share attention heads' keys and values. Multi-head (MHA)
    gives every head its own; multi-query (MQA) gives them all one; grouped
    query (GQA) is the compromise, and it cuts KV-cache memory by the group
    factor with little quality loss. See
    [27.1](../ch27-inference/01-kv-cache.md).

**GraphRAG**
:   Retrieval over an extracted entity-and-relation *graph* rather than over
    isolated chunks, so multi-hop and global questions become traversals.
    A graph here is the ordinary data structure from
    [Appendix C](C-glossary.md). See
    [29.4](../ch29-memory-rag/04-graphrag.md).

**greedy decoding**
:   Always taking the highest-probability next token. Deterministic and
    repetitive; it is the right choice for eval gates and the wrong one for
    anything creative. See
    [26.4](../ch26-llm-internals/04-sampling.md).

**GRPO (Group Relative Policy Optimization)**
:   A policy-gradient method that deletes the value network by sampling a
    *group* of responses per prompt and using the group's mean as the
    baseline, normalised by its standard deviation. A group where every
    response scores the same produces no gradient at all. See
    [31.3](../ch31-rl/03-dpo-grpo.md).

## H

**hallucination**
:   A fluent, confident output that is not supported by anything — no source,
    no tool result, no fact. It is not a bug to be patched but a consequence
    of a model trained to continue text plausibly. See
    [29.2](../ch29-memory-rag/02-rag-pipeline.md).

**HNSW (hierarchical navigable small world)**
:   The dominant ANN index: a layered proximity graph where search starts on
    a sparse top layer and descends, giving roughly logarithmic hops to a
    near neighbour. See
    [29.1](../ch29-memory-rag/01-embeddings-vector-search.md).

**human in the loop**
:   Requiring a person's confirmation before an irreversible action —
    sending, deleting, paying, deploying, merging. Do not rely on the host
    to add it; mark destructive tools and keep them apart from read-only
    ones. See
    [28.4](../ch28-tools-mcp/04-building-mcp-server.md).

**hybrid search**
:   Combining keyword scoring (BM25) with dense embedding similarity, then
    fusing the two ranked lists. Each covers the other's blind spot: exact
    identifiers for keyword search, paraphrases for embeddings. See
    [29.2](../ch29-memory-rag/02-rag-pipeline.md).

## I

**inference**
:   Running a trained model to produce output, as opposed to training it.
    Unrelated to *type* inference in a compiler. Almost all of the money in
    a deployed system is spent here. See
    [Chapter 27](../ch27-inference/index.md).

**instruction tuning**
:   Supervised fine-tuning on (instruction, response) pairs, which turns a
    raw next-token predictor into something that answers questions and
    follows formats. It is where a base model becomes a chat model. See
    [32.1](../ch32-data/01-why-data.md).

## J

**JSON Schema**
:   The vocabulary for describing the shape of a JSON value — types,
    required keys, enums, bounds. It is how a tool tells a model what
    arguments it accepts, and how your server rejects the ones it does not.
    See [28.1](../ch28-tools-mcp/01-function-calling.md).

**JSON-RPC 2.0**
:   The small, old, boring remote-procedure-call format MCP speaks: a
    request with `method`, `params` and an `id`; a response echoing that
    `id` with *either* `result` or `error`; and a notification, which is a
    request with no `id` and therefore no reply. See
    [28.3](../ch28-tools-mcp/03-mcp-protocol.md) and
    [Project 5](../projects/05-mcp-server/README.md).

## K

**KL divergence**
:   A measure of how far one probability distribution has moved from
    another. In RLHF it is the leash: penalising $\text{KL}(\pi \| \pi_{\text{ref}})$
    stops the policy from wandering somewhere the reward model scores highly
    and humans do not. See
    [31.2](../ch31-rl/02-policy-gradient-ppo.md).

**KV cache**
:   The stored keys and values for every token already processed, so each
    new token attends to them instead of recomputing them. It turns
    generation from quadratic to linear in work — and it is usually the
    thing that runs you out of GPU memory. See
    [27.1](../ch27-inference/01-kv-cache.md).

## L

**latency: TTFT and TPOT**
:   **Time to first token** is how long the user waits before anything
    appears; **time per output token** is how fast text then streams. They
    have different causes — prefill versus decode — and averaging them
    together hides both. Report p95, not the mean. See
    [27.3](../ch27-inference/03-latency-streaming.md).

**LLM-as-a-judge**
:   Using a model to grade outputs that have no checkable answer. It works,
    it is standard practice, and it will hand you wrong numbers unless you
    treat the judge as a component to be measured — position, verbosity,
    self-preference and formatting biases are all real and all measurable.
    See [33.3](../ch33-eval/03-llm-as-judge.md).

**logits**
:   The raw, unnormalised scores the model produces over the vocabulary
    before softmax. Temperature, top-k and top-p all operate on these
    numbers. See [26.4](../ch26-llm-internals/04-sampling.md).

**LoRA, QLoRA**
:   Fine-tuning by training a small pair of low-rank matrices alongside
    frozen weights, so you update a fraction of a percent of the parameters.
    QLoRA is the same idea on top of a 4-bit quantized base model. See
    [27.4](../ch27-inference/04-quantization-deploy.md).

**loop guard**
:   An agent guard that fingerprints each action as (tool, normalised
    arguments) and replaces the tool's output with a corrective message when
    a fingerprint repeats. A step budget stops a runaway agent; a loop guard
    makes it change its mind. See
    [30.1](../ch30-agents/01-agent-loop-react.md) and
    [Project 6](../projects/06-react-agent/README.md).

## M

**MCP (Model Context Protocol)**
:   An open standard for connecting AI applications to external context and
    capabilities, spoken over JSON-RPC, with three primitives — tools
    (model-controlled), resources (application-controlled), and prompts
    (user-controlled). It turns $M \times N$ bespoke integrations into
    $M + N$. A local server is an ordinary operating-system *process* (see
    [Appendix C](C-glossary.md)). See
    [28.3](../ch28-tools-mcp/03-mcp-protocol.md) and
    [Project 5](../projects/05-mcp-server/README.md).

**MinHash and LSH**
:   Locality-sensitive hashing for near-duplicate detection: hash documents
    so that *similar* ones collide on purpose, then compare only within a
    bucket. The opposite goal from an ordinary hash function, where a
    collision is an accident (see [Appendix C](C-glossary.md)). See
    [32.4](../ch32-data/04-filtering.md).

**mixture of experts (MoE)**
:   An architecture where each token is routed to a few of many parallel
    feed-forward "experts", so total parameters grow while per-token compute
    does not. This handbook builds the dense stack it replaces rather than
    the routing itself; see
    [26.3](../ch26-llm-internals/03-decoder-stack.md) for that stack.

**model collapse**
:   The degradation that follows from training generation after generation
    on the previous generation's synthetic output: diversity narrows, tails
    disappear, and the model converges on its own average. See
    [32.2](../ch32-data/02-synthetic-data.md).

**multi-agent**
:   Several agents with different roles or tools coordinating on one task.
    It buys specialisation and parallelism, and it costs you a communication
    protocol, a budget that no longer composes, and much harder debugging.
    See [30.3](../ch30-agents/03-multi-agent.md).

## N

**nucleus sampling (top-p)**
:   Sampling only from the smallest set of tokens whose probabilities sum to
    $p$. Unlike top-k it adapts: a confident step keeps one or two
    candidates, an uncertain one keeps many. See
    [26.4](../ch26-llm-internals/04-sampling.md).

## O

**observability: span and trace**
:   A **span** is one timed operation with a name and attributes; a
    **trace** is the tree of spans for one request. Agents fail in
    *sequences*, so the tree — including errors the agent caught and
    ignored — is usually the only place the bug is visible. See
    [30.4](../ch30-agents/04-frameworks.md) and
    [Project 6](../projects/06-react-agent/README.md).

## P

**PagedAttention**
:   Storing the KV cache in fixed-size blocks with an indirection table,
    exactly as an operating system pages memory, so that variable-length
    sequences stop fragmenting GPU memory. It is the idea vLLM was built
    around. See [27.2](../ch27-inference/02-batching.md).

**pass@k**
:   The probability that at least one of $k$ sampled attempts passes the
    tests. Reported honestly it uses the unbiased estimator over $n \gg k$
    samples, not "we generated $k$ and one worked". See
    [33.1](../ch33-eval/01-benchmarks.md).

**PEFT (parameter-efficient fine-tuning)**
:   The family of methods that adapt a model by training a small number of
    new or selected parameters while the rest stay frozen. LoRA and QLoRA
    are the members you will actually meet. See
    [27.4](../ch27-inference/04-quantization-deploy.md).

**perplexity**
:   The exponential of the average negative log-likelihood the model assigns
    to held-out text — roughly, how many equally likely options it feels it
    is choosing between. Useful for spotting quantization damage, useless as
    a measure of helpfulness. See
    [27.4](../ch27-inference/04-quantization-deploy.md).

**policy**
:   In RL, the thing that chooses actions: a distribution over actions given
    a state, written $\pi_\theta$. For a language model the policy *is* the
    model, and in an agent loop the same word is used for whatever function
    picks the next step. Nothing to do with a security policy. See
    [31.1](../ch31-rl/01-rl-basics.md).

**PPO (Proximal Policy Optimization)**
:   The workhorse RLHF algorithm: sample, score, and take a clipped policy
    gradient step so no single update moves the policy too far. Correct,
    stable, and expensive — four models resident, two of them training. See
    [31.2](../ch31-rl/02-policy-gradient-ppo.md).

**prefill and decode**
:   The two phases of a generation request. **Prefill** processes the whole
    prompt in parallel and is compute-bound; **decode** produces one token
    at a time and is memory-bandwidth-bound. Nearly every serving
    optimisation targets one phase or the other. See
    [27.2](../ch27-inference/02-batching.md).

**prefix caching**
:   Reusing the KV cache for a prompt prefix that has been seen before — a
    shared system prompt, a long document, the stable head of an agent
    transcript. Free latency, as long as the prefix stays byte-identical.
    See [27.1](../ch27-inference/01-kv-cache.md).

**prompt injection**
:   Text in retrieved or tool-returned content that the model treats as
    instructions. It is the security problem specific to agents, it cannot
    be fully solved at the prompt level, and the real defences are
    structural: least privilege, allowlisted tools, and confirmation on
    anything irreversible. See
    [30.4](../ch30-agents/04-frameworks.md).

**PRM and ORM**
:   An **outcome** reward model scores only the final answer; a **process**
    reward model scores each intermediate step. Process supervision gives
    far better credit assignment and costs far more to label. See
    [31.4](../ch31-rl/04-reward-models.md).

## Q

**quantization**
:   Storing weights (and sometimes activations) in fewer bits — 8, 4, or
    fewer — to cut memory and bandwidth. The arithmetic is simple and the
    engineering is not: which tensors, which granularity, and how much
    quality you are willing to lose. See
    [27.4](../ch27-inference/04-quantization-deploy.md).

## R

**RAG (retrieval-augmented generation)**
:   Retrieving relevant text at query time and putting it in the prompt, so
    the answer is grounded in a source you control rather than in weights
    you cannot inspect. Retrieval quality, not generation quality, is
    usually what a bad RAG system is short of. See
    [29.2](../ch29-memory-rag/02-rag-pipeline.md).

**ReAct**
:   The interleaved Thought / Action / Observation format for agent loops,
    from Yao et al. (ICLR 2023). The model writes the thought and the
    action; **your program** writes the observation. See
    [30.1](../ch30-agents/01-agent-loop-react.md) and
    [Project 6](../projects/06-react-agent/README.md).

**reference model**
:   The frozen copy of the starting policy that DPO, PPO and GRPO measure
    against — usually the SFT checkpoint. Nothing to do with a *reference*
    in the pointer sense (see [Appendix C](C-glossary.md)). Freeze it, or
    every log-ratio is zero and nothing trains. See
    [31.3](../ch31-rl/03-dpo-grpo.md).

**reflection**
:   Having the model criticise its own output against the goal and revise
    it. The returns fall off fast, so cap the number of passes — an
    uncapped critic is a second infinite loop. See
    [30.2](../ch30-agents/02-planning-reflection.md).

**reranking**
:   Re-scoring a retrieved shortlist with a slower, more accurate model —
    usually a cross-encoder — before anything reaches the prompt. Retrieve
    broadly, rerank narrowly. See
    [29.2](../ch29-memory-rag/02-rag-pipeline.md).

**reward hacking**
:   The policy finding behaviour that scores well under the reward model
    while being worse by the standard the reward model was meant to
    approximate — longer answers, more hedging, more markdown. Every learned
    reward has holes, and optimisation finds them. See
    [31.4](../ch31-rl/04-reward-models.md).

**reward model**
:   A model trained on human preference comparisons to predict a scalar
    score for a response. Its output is a *proxy* for human judgement, and
    the gap between the proxy and the thing is where most RLHF failures
    live. See [31.4](../ch31-rl/04-reward-models.md).

**RLHF and RLAIF**
:   Reinforcement learning from **human** feedback, and the same pipeline
    with the comparisons produced by a model instead of a person. RLAIF is
    dramatically cheaper and inherits whatever the labelling model gets
    wrong. See [31.4](../ch31-rl/04-reward-models.md).

**RLVR (reinforcement learning with verifiable rewards)**
:   RL where the reward comes from a checker rather than a learned model — a
    unit test, a math answer key, a compiler. Nothing to hack, because
    nothing was learned; the limit is that most useful tasks have no
    verifier. See [31.3](../ch31-rl/03-dpo-grpo.md).

**rollout**
:   One sampled trajectory generated by the current policy during training —
    the "generate" half of generate-score-update. Rollouts are why PPO and
    GRPO are expensive and DPO is not. See
    [31.2](../ch31-rl/02-policy-gradient-ppo.md).

**RoPE (rotary position embedding)**
:   Encoding position by rotating query and key vectors by an angle
    proportional to their index, so attention depends on *relative*
    distance. It is what most current models use, and what context-length
    extension tricks stretch. See
    [26.3](../ch26-llm-internals/03-decoder-stack.md).

## S

**sampling temperature**
:   The divisor applied to logits before softmax. Below 1 sharpens the
    distribution towards the argmax, above 1 flattens it, and 0 means greedy.
    It is the single most consequential generation knob. See
    [26.4](../ch26-llm-internals/04-sampling.md).

**sandbox**
:   An isolated execution environment — no credentials, no network, capped
    memory, capped wall clock — for running code a model wrote. Running
    generated code in your own process is not a feature; it is a remote code
    execution vulnerability. See
    [30.4](../ch30-agents/04-frameworks.md).

**self-consistency**
:   Sampling several independent reasoning paths at nonzero temperature and
    taking the majority answer. It costs $n$ times the tokens and buys
    accuracy on problems with one checkable answer. See
    [30.2](../ch30-agents/02-planning-reflection.md).

**Self-Instruct and Evol-Instruct**
:   Two recipes for generating instruction data with a model. Self-Instruct
    bootstraps new instructions from a small seed set; Evol-Instruct
    repeatedly rewrites existing instructions to be harder or more
    constrained. See
    [32.2](../ch32-data/02-synthetic-data.md).

**SFT (supervised fine-tuning)**
:   Ordinary next-token training on curated (prompt, response) pairs. It
    teaches format and style reliably and cannot teach the model to prefer
    one good answer over another — which is the gap preference optimisation
    fills. See [31.1](../ch31-rl/01-rl-basics.md).

**SSE (Server-Sent Events)**
:   The one-way text streaming format APIs use to send tokens as they are
    produced: lines of `data: {...}` separated by blank lines, ended by a
    sentinel. Simpler than WebSockets and sufficient, because only the
    server needs to push. See
    [27.3](../ch27-inference/03-latency-streaming.md).

**structured output**
:   Making a model return machine-readable data that always parses —
    through a schema the provider enforces, or through constrained decoding.
    "Please reply with JSON" plus a `try/except` is not structured output.
    See [28.2](../ch28-tools-mcp/02-structured-output.md).

**synthetic data**
:   Training data generated by a model rather than collected from people.
    It is now most of the post-training pipeline, and its quality is decided
    entirely by the filtering you apply afterwards. See
    [32.2](../ch32-data/02-synthetic-data.md).

**system prompt**
:   The instruction block placed before the conversation that sets the
    model's role, constraints and format. It occupies context on every call,
    which is exactly why keeping it byte-stable makes prefix caching pay.
    See [26.1](../ch26-llm-internals/01-tokenization.md).

## T

**throughput**
:   Total tokens served per second across all concurrent requests — the
    number that decides your cost per million tokens. It trades directly
    against per-user latency, and you cannot optimise both. See
    [27.2](../ch27-inference/02-batching.md).

**token**
:   The unit a language model actually reads and writes: a common word, a
    word fragment, or a few bytes. Not the lexical token a compiler
    produces (see [Appendix C](C-glossary.md)) — this one is learned from
    data, and it is why models are bad at counting letters. See
    [26.1](../ch26-llm-internals/01-tokenization.md).

**tokenizer**
:   The reversible mapping between text and token ids, trained alongside (or
    before) the model. Model and tokenizer are a matched pair: mixing them
    produces fluent nonsense, not an error. See
    [26.1](../ch26-llm-internals/01-tokenization.md).

**tool call**
:   One request from the model to run a named function with named
    arguments, plus the result your program feeds back. The model never
    executes anything; it only asks. See
    [28.1](../ch28-tools-mcp/01-function-calling.md).

**top-k sampling**
:   Sampling only from the $k$ highest-probability tokens. Simple and
    fixed-width, which is its weakness: the right $k$ differs between a
    confident step and an uncertain one. See
    [26.4](../ch26-llm-internals/04-sampling.md).

**trajectory**
:   The recorded sequence of states, actions, observations and rewards for
    one episode — for an agent, the whole run: every thought, tool call,
    result and error. It is both the training datum and the debugging
    artifact. See [32.3](../ch32-data/03-trajectories.md).

**transformer**
:   The architecture behind every model in Part V: stacked blocks of
    attention plus a feed-forward network, with residual connections and
    normalisation, from *Attention Is All You Need* (Vaswani et al., 2017).
    See [26.3](../ch26-llm-internals/03-decoder-stack.md).

## V

**value model (critic)**
:   The network PPO trains alongside the policy to predict "how good is this
    state on average", so its prediction can be subtracted as a baseline.
    Deleting it is exactly what GRPO does. See
    [31.2](../ch31-rl/02-policy-gradient-ppo.md).

**vector database**
:   A store for embeddings with an ANN index, metadata filtering, and the
    usual database concerns — persistence, updates, and deletes. FAISS,
    Chroma, Qdrant, pgvector and others differ mostly in how much of that
    list they take on. See
    [29.1](../ch29-memory-rag/01-embeddings-vector-search.md).

**vLLM**
:   An open-source, high-throughput serving engine built around
    PagedAttention and continuous batching, with an OpenAI-compatible HTTP
    interface. See [27.2](../ch27-inference/02-batching.md).

## W

**workflow**
:   An LLM program whose control flow you wrote — branches, retries, a fixed
    order of calls — as opposed to an agent, where the model decides what
    happens next at run time. Most production systems should be workflows.
    See [30.1](../ch30-agents/01-agent-loop-react.md).

## Z

**zero-shot**
:   Asking for a task with no examples in the prompt, relying on the
    instruction alone. Instruction tuning is what made this work; a base
    model generally needs few-shot examples instead. See
    [33.1](../ch33-eval/01-benchmarks.md).
