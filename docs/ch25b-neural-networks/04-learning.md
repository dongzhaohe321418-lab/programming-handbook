# 25.5.4 · How a network learns

This is the page everything has been building toward. We have a network that
runs but predicts nonsense, because its weights are random. Learning is the
process of *changing those weights* until the predictions come true — and it
rests on three plain ideas: a **loss** that scores how wrong the network is, a
rule (**gradient descent**) for which way to nudge each weight to make the loss
smaller, and a piece of bookkeeping (**backpropagation**) that works out each
weight's share of the blame. Put them in a loop and the network teaches itself.
By the end of this page the circle from [Section 25.5.3](03-forward-pass.md)
will be perfectly separated — and *you* will have trained the network that does
it.

## Loss: one number for "how wrong"

!!! abstract "In plain words"

    - **What it is.** The loss is a single number measuring how far the
      network's current predictions are from the true answers — small is good,
      zero is perfect.
    - **Picture it.** Your score in golf. It is not the goal itself (the goal
      is to sink the ball), but it summarises the whole round in one number,
      and *lower is always better*, so you can tell if a change helped.
    - **Why it matters.** You cannot improve what you cannot measure. The loss
      turns the vague wish "predict better" into one number to push downward,
      which is the only thing the rest of the machinery needs.

For yes/no problems the standard loss is **binary cross-entropy**: it rewards
confident-correct predictions and punishes confident-wrong ones harshly.

$$
L = -\frac{1}{N}\sum_{i} \Big[\, y_i \log \hat{y}_i + (1-y_i)\log(1-\hat{y}_i)\,\Big]
$$

Read aloud: *for each point, if the true label is 1 we want $\hat{y}$ near 1 so
$\log\hat{y}$ is near 0; if the label is 0 we want $\hat{y}$ near 0. Any
confident mistake makes a $\log$ blow up, and we average over all points.* Here
is the network from Section 25.5.3, rebuilt, with its starting loss measured:

```python
import numpy as np

# --- the circle dataset, exactly as in Section 25.5.3 ---
rng = np.random.default_rng(0)
N = 200
X = rng.uniform(-2, 2, size=(N, 2))
y = ((X ** 2).sum(axis=1) < 1.4 ** 2).astype(float).reshape(N, 1)

def relu(z):    return np.maximum(0.0, z)
def sigmoid(z): return 1.0 / (1.0 + np.exp(-z))

# --- the network, same random start as before ---
init = np.random.default_rng(1)
H = 16
W1 = init.normal(0, 0.5, size=(2, H)); b1 = np.zeros((1, H))
W2 = init.normal(0, 0.5, size=(H, 1)); b2 = np.zeros((1, 1))

def forward(X):
    z1 = X @ W1 + b1
    a1 = relu(z1)
    z2 = a1 @ W2 + b2
    a2 = sigmoid(z2)
    return z1, a1, a2                 # keep z1: backprop will need it

def bce(pred, y):
    pred = np.clip(pred, 1e-7, 1 - 1e-7)     # avoid log(0)
    return float(-np.mean(y * np.log(pred) + (1 - y) * np.log(1 - pred)))

# snapshot the untrained decision boundary for a before/after picture later
gx, gy = np.meshgrid(np.linspace(-2, 2, 120), np.linspace(-2, 2, 120))
grid = np.column_stack([gx.ravel(), gy.ravel()])
zone_before = forward(grid)[2].reshape(gx.shape)

_, _, a2 = forward(X)
print("starting loss    :", round(bce(a2, y), 4))
print("starting accuracy:", round(float(((a2 > 0.5) == (y > 0.5)).mean()), 3))
```

The starting loss is **`0.6652`** and the accuracy `0.465` — the coin-flip
network from last section, now with a number attached to its wrongness. Our
whole job is to drive that `0.6652` down toward zero.

## Gradient descent: which way is downhill

!!! abstract "In plain words"

    - **What it is.** A rule for improving every weight at once: figure out
      which direction each weight would have to move to make the loss *rise*,
      then move it the opposite way, by a small step.
    - **Picture it.** You are on a foggy hillside and want the valley. You
      cannot see it, but you can feel the slope under your feet, so you step
      downhill a little, feel again, step again. The **gradient** is that
      felt slope — which way is up, and how steep (see the
      [math primer](../part5-math-primer.md)).
    - **Why it matters.** A network has thousands to billions of weights; you
      cannot try combinations by hand. Gradient descent gives every weight its
      own marching order from one measurement of the slope.

The rule for a single weight $w$ is one line of maths:

$$
w \leftarrow w - \eta\,\frac{\partial L}{\partial w}
$$

Read aloud: *the new weight is the old weight minus a small step $\eta$ times
the loss's slope with respect to that weight.* The slope $\partial L/\partial
w$ says "increase $w$ and the loss changes *this* fast, in *this* direction";
the minus sign turns "uphill" into "downhill". The step size $\eta$ (the
**learning rate**) controls how big a stride we take — too small and learning
crawls, too big and we overshoot the valley and bounce.

The only remaining question is where those slopes come from. That is
backpropagation.

## Backpropagation: passing the blame backward

!!! abstract "In plain words"

    - **What it is.** A way to compute, for every weight, how much it
      contributed to the loss — by starting at the output error and pushing it
      backward through the network layer by layer.
    - **Picture it.** A project runs late, and the blame flows backward down the
      chain: the final team measures how far off it was, then tells the team
      that fed it "here is how much of this is your fault", which passes its own
      share further back, and so on to the start.
    - **Why it matters.** A weight in an early layer affects the loss only
      *through* all the layers after it. Backprop is the accountancy — the
      chain rule from calculus, used as bookkeeping — that correctly splits the
      final error across every weight, in one backward sweep.

We will not derive the formulas; we will *use* them. For our two-layer network
the backward pass is six lines, and each line has a plain meaning. The one
piece of magic worth knowing: because we paired a sigmoid output with
cross-entropy loss, the error signal at the output collapses to something
beautifully simple — **prediction minus truth**.

```python
# continues
def train_step(lr):
    """One forward pass, then one backward pass, then one downhill step."""
    z1, a1, a2 = forward(X)

    # --- backward pass: blame flows from the output back to the input ---
    dz2 = (a2 - y) / N            # output error: prediction minus truth
    dW2 = a1.T @ dz2             # blame on W2: which hidden units fired wrong?
    db2 = dz2.sum(axis=0, keepdims=True)

    da1 = dz2 @ W2.T            # push the blame back into the hidden layer
    dz1 = da1 * (z1 > 0)         # ReLU gate: blocked units get no blame
    dW1 = X.T @ dz1             # blame on W1: which inputs drove the error?
    db1 = dz1.sum(axis=0, keepdims=True)

    # --- gradient-descent step: nudge every weight downhill ---
    return dW1, db1, dW2, db2

dW1, db1, dW2, db2 = train_step(0.5)
print("gradient shapes match weight shapes:",
      dW1.shape == W1.shape, db1.shape == b1.shape,
      dW2.shape == W2.shape, db2.shape == b2.shape)
```

Every gradient array has the *same shape* as the weight it corrects — that is
the invariant to check when you write backprop by hand. Read the middle of the
backward pass as a sentence: the output error `dz2` is multiplied back through
`W2` to reach the hidden layer (`da1`), then the ReLU **gate** `(z1 > 0)` zeroes
out the blame for any hidden unit that was switched off — a blocked unit had no
effect, so it deserves no blame. That single `(z1 > 0)` is the entire reason we
kept `z1` around.

## The training loop

Now put it in a loop: forward, measure loss, backward, step downhill, repeat.
Each pass over the data is one **epoch**. Watch the loss fall.

```python
# continues
lr = 0.5
losses = []
for epoch in range(1, 1501):
    z1, a1, a2 = forward(X)
    losses.append(bce(a2, y))

    # backward pass (same six lines as above, inlined for the loop)
    dz2 = (a2 - y) / N
    dW2 = a1.T @ dz2;  db2 = dz2.sum(axis=0, keepdims=True)
    dz1 = (dz2 @ W2.T) * (z1 > 0)
    dW1 = X.T @ dz1;   db1 = dz1.sum(axis=0, keepdims=True)

    # downhill step
    W1 -= lr * dW1;  b1 -= lr * db1
    W2 -= lr * dW2;  b2 -= lr * db2

    if epoch in (300, 600, 900, 1200, 1500):
        acc = float(((a2 > 0.5) == (y > 0.5)).mean())
        print(f"epoch {epoch:4d}   loss {losses[-1]:.4f}   accuracy {acc:.3f}")
```

The loss marches down and the accuracy climbs:

```text
epoch  300   loss 0.0816   accuracy 0.995
epoch  600   loss 0.0406   accuracy 1.000
epoch  900   loss 0.0246   accuracy 1.000
epoch 1200   loss 0.0172   accuracy 1.000
epoch 1500   loss 0.0129   accuracy 1.000
```

From a loss of `0.6652` to **`0.0129`**, and from 46.5% accuracy to **100%** —
by around epoch 600 the network already separates every point correctly, and
the remaining epochs just sharpen its confidence. Nothing changed but the
numbers in four arrays, nudged fifteen hundred times. That is training, in
full, with no library doing it for you.

The loss curve tells the story at a glance:

```python
# continues
import matplotlib.pyplot as plt

plt.figure(figsize=(5, 3.2))
plt.plot(losses, linewidth=2)
plt.xlabel("epoch"); plt.ylabel("loss (binary cross-entropy)")
plt.title("Loss falls as the network learns")
plt.ylim(0, losses[0] * 1.05)
```

A steep drop early — the network finds the circle fast — then a long, flat
polish. And the decision boundary, before versus after, is the whole chapter in
one image:

```python
# continues
zone_after = forward(grid)[2].reshape(gx.shape)
inside = y[:, 0] == 1

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 4))
for ax, zone, title in [(ax1, zone_before, "Before: random weights"),
                        (ax2, zone_after,  "After: trained")]:
    ax.contourf(gx, gy, zone, levels=[0, 0.5, 1], colors=["#cfe3f5", "#f7d7b0"])
    ax.scatter(X[inside, 0], X[inside, 1], c="tab:orange", s=12)
    ax.scatter(X[~inside, 0], X[~inside, 1], c="tab:blue", s=12)
    ax.set_aspect("equal"); ax.set_xlabel("x1"); ax.set_ylabel("x2")
    ax.set_title(title)
fig.tight_layout()
```

On the left, the jagged nonsense we started with. On the right, a clean round
island: the network *bent a straight boundary into a circle*, exactly the power
[Section 25.5.2](02-activations.md) promised the ReLU would unlock. You built
it, and you trained it.

## What the real frameworks automate

You just did, by hand, everything PyTorch and JAX do — which means you now know
what they actually are. Two things separate your loop from an industrial one:

- **Automatic differentiation (autodiff).** We *derived* the six backward lines
  ourselves. PyTorch and JAX compute them for you: you write only the forward
  pass, and the library records every operation and replays it backward to
  produce the gradients automatically. For a two-layer net that is a
  convenience; for a transformer with hundreds of operations it is the
  difference between possible and not.
- **GPUs and scale.** Our arrays are `200 × 16`. A real model's are millions by
  thousands, and the same `X @ W` runs on a GPU across thousands of cores at
  once. The *arithmetic is identical* — matrix multiply, activation, matrix
  multiply — just vastly larger and faster.

That is the honest headline of this chapter: a frontier model differs from what
you just trained in *scale and engineering*, not in kind. It is this loop —
forward, loss, backward, step — repeated over more weights and more data than
you can picture. [Chapter 26](../ch26-llm-internals/index.md) now takes the
forward pass and grows it into a transformer.

!!! warning "Common mistakes"

    - **Learning rate too big.** A large $\eta$ overshoots the valley; the loss
      jumps around or explodes to `nan`. Too small and it barely moves.
      Exercise 25.5.4 has you watch both failures directly.
    - **Forgetting to divide the gradient by `N`.** Our `dz2 = (a2 - y) / N`
      averages the blame over the batch. Drop the `/ N` and the effective step
      size is 200× bigger — instant divergence.
    - **A wrong-shaped gradient.** Every gradient must match its weight's shape.
      If `dW1.shape != W1.shape`, the `-=` either crashes or silently
      broadcasts garbage. Assert the shapes while learning.
    - **Reading one low loss as success.** A loss that is low *on the training
      data* can still be memorising rather than generalising. Measuring on
      held-out data is the subject of [evaluation](../ch26-llm-internals/index.md)
      later in Part V; here, with a tidy circle, memorising and generalising
      happen to coincide.

## Check your understanding

1. In the update $w \leftarrow w - \eta\,\partial L/\partial w$, why is the sign
   a minus?

    ??? success "Answer"

        The gradient $\partial L/\partial w$ points in the direction that makes
        the loss *increase*. We want it to decrease, so we step the opposite
        way — hence minus. Flip it to a plus and you would climb the hill,
        driving the loss *up*.

2. The output error came out as `dz2 = (a2 - y) / N`, just "prediction minus
   truth". What does that quantity say about a point the network already
   predicts perfectly?

    ??? success "Answer"

        If `a2` equals `y` for that point, its contribution to `dz2` is zero —
        it generates no blame and no weight change. Learning concentrates
        entirely on the points the network still gets wrong, which is exactly
        what you want. (This clean form is a special gift of pairing sigmoid
        output with cross-entropy loss.)

3. The accuracy hit 100% around epoch 600, but the loss kept dropping to epoch
   1500. What was happening in those later epochs?

    ??? success "Answer"

        Accuracy only asks whether each prediction lands on the right side of
        `0.5`. Once every point does, accuracy is pinned at 100%. But the loss
        also rewards *confidence*: pushing a correct `0.7` up toward `0.99`
        still lowers cross-entropy. The later epochs sharpened the network's
        certainty without changing any decision.
