# Chapter 25.5 · Neural Networks from Scratch

Part V is about large language models — and a language model is a **neural
network**. Chapter 26 opens the transformer and starts computing attention on
the very first page, quietly assuming you already know what a neural network
*is*: what a neuron computes, why layers stack, what "training" actually
changes. This chapter fills that gap. It is the missing first step, and it is
built the way the rest of this handbook is built: no black boxes, every idea
small enough to run in numpy and print, one honest analogy per hard part.

Here is the whole subject in three sentences. **A neural network is a
function: numbers go in, numbers come out.** It is built by alternating two
operations — multiply by a grid of numbers (a "layer"), then bend the result
through a simple curve (an "activation") — and the grids of numbers are called
**weights**. *Training* is nothing more than nudging those weights, over and
over, until the function's outputs match the answers you wanted.

That is the entire idea. Everything else — transformers, attention, the models
behind every chatbot you have used — is that idea repeated at enormous scale.
By the end of this chapter you will have trained a real neural network by hand,
watched its error shrink epoch by epoch, and then taken one more step that ties
the whole book together: you will run a neural network on a **graph** (the
structure from [Chapter 37](../ch37-graphs/index.md)) and discover that
attention itself is a graph neural network in disguise.

## After this chapter you can

- Say in plain words what a single **neuron** computes, and why it is `w·x + b`.
- Build a **layer** as one matrix multiply, and read the shapes of the arrays
  flowing through it.
- Explain why a network needs **activation functions** — and show, by running
  it, that without them a deep network collapses into a single layer.
- Recognise **ReLU**, **sigmoid**, and **tanh** on sight and say what each is
  for.
- Assemble a small multi-layer network as a runnable `forward(x)` function and
  see why random weights predict nonsense.
- Explain **loss**, **gradient descent**, and **backpropagation** as three
  plain ideas, and use them to **train** a network until its error drops to
  near zero.
- Describe **message passing** on a graph, build a first **graph neural
  network**, and explain why a convolution and an attention layer are both
  special cases of it.

## Prerequisites

- **Parts I–IV of this handbook.** You should be comfortable with Python
  functions ([Chapter 3](../ch03-functions/index.md)), loops
  ([Chapter 6](../ch06-loops/index.md)), and the idea of a two-dimensional grid
  of numbers ([Chapter 8](../ch08-grids/index.md)).
- **The [Part V math primer](../part5-math-primer.md).** That page introduces
  everything mathematical this chapter leans on: vectors, the dot product,
  softmax, and the picture of a **gradient as "which way is downhill"**. If a
  symbol here looks unfamiliar, it is defined there.
- **No calculus, and no prior machine learning.** Every array in this chapter
  is small enough to print and read entry by entry. If you have never seen
  numpy, that is fine — the [Chapter 26 tokenizer page](../ch26-llm-internals/01-tokenization.md)
  and the primer introduce it gently, and we use only a handful of operations.

## Sections

| Section | What it builds |
| --- | --- |
| [25.5.1 The neuron and the layer](01-neuron-and-layer.md) | One neuron as `w·x + b`, then a whole layer as a single matrix multiply |
| [25.5.2 Activation functions](02-activations.md) | Why stacked linear layers collapse, and the ReLU / sigmoid / tanh curves that fix it |
| [25.5.3 The forward pass](03-forward-pass.md) | A multi-layer network as one `forward(x)` function, predicting (badly) with random weights |
| [25.5.4 How a network learns](04-learning.md) | Loss, gradient descent, backpropagation — and training the network until it works |
| [25.5.5 A first GNN](05-gnn.md) | Message passing on a graph, node classification, and attention seen as a graph network |
| [Exercises](exercises.md) | Eight problems with full solutions, from one neuron by hand to a baby attention layer |

!!! tip "How to read this chapter"
    Run every block, then *change a number* and run it again. Make a weight
    negative, delete the activation, train for ten times as long, add a third
    round of message passing. The arrays are tiny on purpose — you can break
    this network a hundred ways and watch exactly what each break does, which
    is a luxury nobody has once the network has billions of weights.
