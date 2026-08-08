# Chapter 26 · How Language Models Work

You have almost certainly used a large language model. You type a sentence,
and text comes back — fluent, often useful, occasionally confidently wrong,
and reliably unable to count the letters in "strawberry". From the outside
it is a black box, and the internet is full of confident explanations of it
that are either hand-waving metaphors ("it's like a brain!") or dense
research papers. This chapter takes the third route, the one this handbook
has taken since Chapter 0: we open the box and build the thing. By the end
you will have written, and run, a tokenizer, an embedding lookup, an
attention head, a multi-layer transformer forward pass, and a full sampling
loop — every one of them in plain Python and numpy, every one of them small
enough to print every number it produces.

!!! abstract "In plain words"

    - **What it is.** A language model is one function: hand it a list of
      numbers standing for the text so far, and it returns a score for every
      word that could come next.
    - **Picture it.** A phone's autocomplete that has read most of the
      internet. It only ever guesses the next piece — but it guesses so well
      that, by feeding each guess back in and asking again, you get whole
      essays.
    - **Why it matters.** Answering, coding, refusing, "reasoning" — all of it
      is that one guess-the-next-token step, repeated. Nothing in this chapter
      is more mysterious than that, and every later chapter is built on it.

The honest headline is this: **a language model is a function that takes a
list of integers and returns a list of scores, one score per possible next
token.** That is the entire interface. Everything the model appears to do —
answer questions, write code, hold a conversation, refuse a request — is
that one function applied over and over, with the output of each call
appended to the input of the next. There is no memory beyond the input list,
no plan beyond the current score row, and no step that is not arithmetic you
could in principle do by hand. Chapters 27 onward build agents, training,
and serving infrastructure on top of this; none of it makes sense until this
function does.

The numbers here are tiny — vocabularies of a dozen tokens, vectors of
length four, models with two layers — and that is deliberate. A real model
differs from what you will build in exactly three ways: it has bigger
arrays, it has trained rather than random weights, and it runs on a GPU. It
does not have a secret extra mechanism. When you finish Section 26.3 you
will have run a transformer, and the sentence "I know what happens inside an
LLM" will be literally true rather than aspirational.

## After this chapter you can

- Explain why a model sees tokens instead of characters, and train a real
  byte-pair-encoding tokenizer from scratch on your own text.
- Predict which inputs will tokenize badly, and explain letter-counting and
  arithmetic failures in terms of tokenization rather than "intelligence".
- Describe what an embedding is, and measure whether two token vectors are
  related using a dot product and cosine similarity.
- Compute attention by hand in numpy — queries, keys, values, scaled scores,
  softmax, weighted sum — and read an attention heatmap.
- Say precisely why the $\sqrt{d_k}$ scaling and the causal mask are there,
  and what breaks without each.
- Assemble residual connections, layer normalization, and a feed-forward
  network into a transformer block, stack it, and run a complete forward
  pass from token IDs to a next-token distribution.
- Explain how position information is added, and why RoPE's relative
  encoding extrapolates better than a learned position table.
- Calculate a model's parameter count and its KV-cache memory, and explain
  what GQA and FlashAttention each buy.
- Implement greedy decoding, temperature, top-k, top-p, and a repetition
  penalty, and choose sensible settings for a given task.

## Prerequisites

Parts I–IV of this handbook. Concretely, you should be comfortable with
Python functions, classes, and dictionaries ([Chapter 3](../ch03-functions/index.md),
[Chapter 9](../ch09-collections/index.md), [Chapter 12](../ch12-classes/index.md)),
loops over lists ([Chapter 6](../ch06-loops/index.md)), the idea of a
two-dimensional grid ([Chapter 8](../ch08-grids/index.md)), and Big-O
notation ([Chapter 16](../ch16-complexity/index.md)) — attention's $O(n^2)$
cost is the single most consequential complexity fact in the field.

You need **no** machine learning, no calculus, and no linear algebra. Every
mathematical object used here — vector, matrix product, dot product, softmax
— is introduced from scratch, with a runnable implementation, at the point
where it first matters. If you have met numpy before, you have a small head
start; if not, the arrays in this chapter are small enough to read entry by
entry.

!!! tip "Two gentler on-ramps first"

    A language model is a kind of **neural network**, so this chapter reads
    far more easily if you meet the network first. Two short pages open
    Part V for exactly that:

    - [The math you'll actually need](../part5-math-primer.md) — vectors, dot
      products, softmax, and (later, for training) gradients, each with a
      one-line analogy and a runnable example. No calculus.
    - [Chapter 25.5 · Neural Networks from Scratch](../ch25b-neural-networks/index.md)
      — build a neuron, a layer, and a working network by hand before you
      meet attention. Its last section shows attention *is* a graph neural
      network in disguise.

## Sections

| Section | What it builds |
| --- | --- |
| [26.1 From text to tokens](01-tokenization.md) | A working BPE tokenizer, trained on a paragraph, and why tokenization explains the famous failures |
| [26.2 Embeddings and attention](02-attention.md) | Token IDs to vectors, then $\operatorname{softmax}(QK^\top/\sqrt{d_k})V$ computed step by step and plotted |
| [26.3 The decoder-only stack](03-decoder-stack.md) | Residuals, LayerNorm, feed-forward, positions, a full two-layer forward pass, and the memory arithmetic |
| [26.4 Sampling — how text is chosen](04-sampling.md) | Logits to text: greedy, temperature, top-k, top-p, penalties, and a complete `generate()` loop |
| [Exercises](exercises.md) | Eight problems with full solutions, from BPE by hand to adding a second attention head |

!!! tip "How to read this chapter"
    Run every block, and *change* the numbers. Set $T$ to 5, delete the
    `/ np.sqrt(d_k)`, remove the causal mask, shrink `d_model` to 2. The
    arrays are small on purpose: you can break this model in a hundred ways
    and see exactly what each break does, which is a luxury nobody has when
    the model has 70 billion parameters and costs a fortune to run.
