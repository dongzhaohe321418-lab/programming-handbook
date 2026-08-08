# 25.5.1 · The neuron and the layer

Everything in a neural network — every transformer, every chatbot — is built
from one tiny piece repeated millions of times. That piece is the **neuron**,
and it is far simpler than the biological word suggests: it takes a few
numbers, decides how much to trust each one, adds them up, and reports a
score. This section builds one in numpy, then stacks a row of them into a
**layer** with a single matrix multiply. No learning yet — just the forward
arithmetic, so you can see exactly what a network is made of.

!!! abstract "In plain words"

    - **What it is.** A neuron takes several input numbers, multiplies each by
      a **weight** that says how much it trusts that input, adds a fixed
      **bias**, and outputs one number — a score.
    - **Picture it.** A loan officer deciding on an application. They weigh
      your income heavily and positively, your existing debt heavily and
      *negatively*, your credit history moderately, then start from a baseline
      mood (the bias) and add it all up into one "approve-ness" score.
    - **Why it matters.** This weigh-and-sum is the *only* computation a
      network does. Master this one number and the billion-parameter version
      is just more of the same.

## One neuron is a weighted sum

Suppose an applicant is summarised by three numbers, each scaled to a
convenient range: income `0.6`, debt `0.3`, credit history `0.8`. The neuron
holds one **weight** per input — how much it trusts each — plus one **bias**, a
constant it always adds. Its output is

$$
\text{score} = w_1 x_1 + w_2 x_2 + w_3 x_3 + b = \mathbf{w}\cdot\mathbf{x} + b
$$

Read aloud: *multiply each input by its weight, add them all up, then add the
bias.* The middle sum $w_1x_1 + w_2x_2 + w_3x_3$ is exactly the **dot product**
$\mathbf{w}\cdot\mathbf{x}$ from the [math primer](../part5-math-primer.md) —
matching slots multiplied, then totalled. A neuron *is* a dot product plus a
bias.

```python
import numpy as np

x = np.array([0.6, 0.3, 0.8])     # income, debt, credit history (all scaled)
w = np.array([1.5, -2.0, 1.0])    # trust: income +, debt -, history +
b = -0.5                          # baseline: start slightly sceptical

score = w @ x + b                 # `@` is numpy's dot product
print("dot product w·x :", round(float(w @ x), 3))
print("neuron score    :", round(float(score), 3))
print("decision        :", "approve" if score > 0 else "reject")
```

The dot product is $1.5(0.6) + (-2.0)(0.3) + 1.0(0.8) = 0.9 - 0.6 + 0.8 =
1.1$; subtract the bias `0.5` and the **score is `0.6`** — positive, so this
neuron approves. Notice how the signs of the weights encode the neuron's
"opinion": debt has a negative weight, so more debt pushes the score *down*.
Nobody chose `1.5`, `-2.0`, `1.0` by hand in a real network — those are the
**knobs we will tune** in [Section 25.5.4](04-learning.md). For now we set them
by hand so the arithmetic is visible.

!!! info "Why the bias?"
    Without a bias, an all-zero input forces an all-zero score, and every
    neuron is nailed to pass through the origin. The bias is a free constant
    that shifts the whole decision up or down — the loan officer's baseline
    mood before they read a single number. It is a weight on an imaginary
    input that is always `1`.

## A layer is many neurons at once

One neuron gives one score. Real networks want *many* scores from the same
inputs — one neuron watching creditworthiness, another watching debt, a third
weighing history first — so we run a whole **row** of neurons side by side.
Each has its own weight vector and its own bias. That is a **layer**.

Stacking the neurons' weight vectors as the rows of a matrix $W$ turns the
whole layer into a single matrix–vector multiply:

$$
\mathbf{y} = W\mathbf{x} + \mathbf{b}
$$

Read aloud: *row $i$ of $W$ is neuron $i$'s weights, so entry $i$ of the output
is neuron $i$'s weighted sum plus its bias.* One line of numpy computes every
neuron at once.

```python
import numpy as np

x = np.array([0.6, 0.3, 0.8])

W = np.array([
    [ 1.5, -2.0,  1.0],    # neuron 0 — "creditworthiness"
    [ 0.0,  1.0,  0.0],    # neuron 1 — "debt watcher"
    [-1.0, -1.0,  2.0],    # neuron 2 — "history first"
])
b = np.array([-0.5, 0.0, 0.2])

y = W @ x + b              # three neurons, one multiply
print("W shape:", W.shape, " x shape:", x.shape, " y shape:", y.shape)
print("layer output:", np.round(y, 3))
```

The output is **`[0.6, 0.3, 0.9]`** — three numbers, one per neuron. Neuron 0
is the same one from before (still `0.6`); neuron 1 simply reports the debt
input; neuron 2 combines the three its own way. Watch the **shapes**: a
`(3, 3)` weight matrix times a length-`3` input gives a length-`3` output. The
first dimension of $W$ is *how many neurons the layer has* (its output width);
the second is *how many inputs each expects*. Getting these to line up is 90%
of the work in real network code.

### Many inputs at once — a batch

In practice you push many examples through the layer together — a **batch** —
because one big matrix multiply is far faster than a loop. Stack the examples
as rows of a matrix $X$ and the layer becomes $Y = XW^{\top} + \mathbf{b}$:

```python
import numpy as np

W = np.array([[ 1.5, -2.0,  1.0],
              [ 0.0,  1.0,  0.0],
              [-1.0, -1.0,  2.0]])
b = np.array([-0.5, 0.0, 0.2])

X = np.array([[0.6, 0.3, 0.8],     # applicant 0
              [0.2, 0.9, 0.1],     # applicant 1
              [0.9, 0.1, 0.9],     # applicant 2
              [0.5, 0.5, 0.5]])    # applicant 3

Y = X @ W.T + b                    # (4,3) @ (3,3) -> (4,3)
print("batch input shape :", X.shape)
print("batch output shape:", Y.shape)
print("applicant 0 output:", np.round(Y[0], 3))
```

Four applicants in, a `(4, 3)` block of scores out — one row per applicant,
one column per neuron. Applicant 0's row is still **`[0.6, 0.3, 0.9]`**,
identical to the single-example version: batching changes *nothing* about the
arithmetic, it just does four applicants' worth at once. This `X @ W.T + b`
shape is the beating heart of every layer you will ever write, and it is
exactly the shape [Chapter 26](../ch26-llm-internals/02-attention.md) uses to
project token embeddings.

!!! warning "Common mistakes"

    - **Mismatched shapes.** `W @ x` needs `W`'s second dimension to equal
      `x`'s length. Numpy raises a `ValueError` the moment they disagree; read
      the two numbers in the message and line them up. This is the single most
      common neural-network bug.
    - **Forgetting the bias.** `W @ x` without `+ b` is a different (and
      weaker) function — every neuron is forced through zero. The bias is not
      optional decoration.
    - **Confusing the two dimensions of `W`.** Rows are neurons (output width),
      columns are inputs. Swapping them transposes the layer and produces
      confident, wrong numbers with no error.
    - **Thinking a neuron "decides".** It only outputs a number. The *network*
      turns numbers into decisions later, through activations and a final
      threshold.

## Check your understanding

1. A neuron has weights `[2.0, -1.0]` and bias `0.5`. What score does it output
   for the input `[1.0, 3.0]`?

    ??? success "Answer"

        $2.0(1.0) + (-1.0)(3.0) + 0.5 = 2.0 - 3.0 + 0.5 = -0.5$. Negative —
        the second input's large value, hit by the negative weight, dragged the
        score below zero. In code: `np.array([2.0,-1.0]) @ np.array([1.0,3.0])
        + 0.5` gives `-0.5`.

2. A layer takes inputs of length 5 and has 8 neurons. What is the shape of its
   weight matrix $W$, and of its output for a single input?

    ??? success "Answer"

        $W$ is `(8, 5)` — 8 rows (one weight vector per neuron), 5 columns (one
        weight per input). The output is length `8`, one score per neuron.
        Rows = output width, columns = input width, always.

3. Why can a whole layer of neurons be computed with one matrix multiply
   instead of a Python loop over neurons?

    ??? success "Answer"

        Because each neuron's output is a dot product of its weight row with
        the input, and stacking those dot products *is* the definition of a
        matrix–vector product. One `W @ x` computes all of them at once — and
        numpy runs it as a single fast operation instead of a slow Python loop,
        which is why real networks are written this way.
