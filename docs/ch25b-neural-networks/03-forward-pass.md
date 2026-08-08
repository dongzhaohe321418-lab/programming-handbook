# 25.5.3 · The forward pass — a network as a function

We have a layer ([25.5.1](01-neuron-and-layer.md)) and a reason to bend it
([25.5.2](02-activations.md)). Assembling them is now almost anticlimactic: a
neural network is just those two operations, alternated, wrapped in a function.
Numbers go in one end, numbers come out the other. Running that function is
called the **forward pass**, and this section builds a complete one on a real
little dataset — then shows it confidently predicting nonsense, because we have
not yet tuned a single weight.

!!! abstract "In plain words"

    - **What it is.** The forward pass is running the network's function on an
      input: multiply by a matrix, bend with an activation, multiply by the
      next matrix, and so on until an answer falls out the end.
    - **Picture it.** An assembly line of identical stations. Each station does
      the same two moves — combine the parts in front of it (matrix multiply),
      then reshape the result (activation) — and hands its output to the next.
    - **Why it matters.** This function *is* the model. Training will change the
      numbers inside it, but the forward pass — the thing that turns an input
      into a prediction — never changes. Get it right once and you reuse it
      forever.

## A dataset the network will learn

We need a task a straight line cannot solve, so the network's power is actually
required. Here is one: points scattered on a plane, labelled `1` if they fall
**inside a circle** and `0` if outside. The boundary is round, so no single
line separates the classes — exactly the situation [Section
25.5.2](02-activations.md) built the machinery for.

```python
import numpy as np
import matplotlib.pyplot as plt

rng = np.random.default_rng(0)
N = 200
X = rng.uniform(-2, 2, size=(N, 2))                 # 200 random points
y = ((X ** 2).sum(axis=1) < 1.4 ** 2).astype(float).reshape(N, 1)  # inside?

print("points :", N)
print("inside :", int(y.sum()), " outside:", int(N - y.sum()))

inside = y[:, 0] == 1
plt.figure(figsize=(4.2, 4.2))
plt.scatter(X[inside, 0], X[inside, 1], c="tab:orange", s=16, label="inside (1)")
plt.scatter(X[~inside, 0], X[~inside, 1], c="tab:blue", s=16, label="outside (0)")
plt.gca().set_aspect("equal")
plt.xlabel("x1"); plt.ylabel("x2"); plt.legend(loc="upper right")
plt.title("The task: is the point inside the circle?")
```

There are **72 points inside** and 128 outside — a round orange island in a
blue sea. A ruler laid anywhere on this picture will always cut off some orange
with the blue. We need a curve, and the network will have to bend one.

## Assembling the network

The network is a stack of two layers with a ReLU bend between them, ending in a
sigmoid so the output reads as a probability of "inside":

$$
\mathbf{x} \;\xrightarrow{W_1,\,\mathbf{b}_1}\; \operatorname{ReLU}
\;\xrightarrow{W_2,\,\mathbf{b}_2}\; \sigma \;\to\; \hat{y}
$$

Read aloud: *take the 2-number point, expand it to 16 hidden numbers and bend
them with ReLU, then collapse those to one number and squash it to a
probability with sigmoid.* This shape — an input layer, one **hidden** layer,
an output — is the classic **multi-layer perceptron (MLP)**, the simplest true
neural network. In code the whole model is four arrays and one `forward`
function:

```python
# continues
def relu(z):    return np.maximum(0.0, z)
def sigmoid(z): return 1.0 / (1.0 + np.exp(-z))

init = np.random.default_rng(1)
H = 16                                       # hidden layer width
W1 = init.normal(0, 0.5, size=(2, H)); b1 = np.zeros((1, H))   # 2 -> 16
W2 = init.normal(0, 0.5, size=(H, 1)); b2 = np.zeros((1, 1))   # 16 -> 1

def forward(X):
    a1 = relu(X @ W1 + b1)                    # hidden layer + bend
    p  = sigmoid(a1 @ W2 + b2)                # output layer -> probability
    return a1, p

a1, p = forward(X)
print("hidden activations shape:", a1.shape, "(one 16-vector per point)")
print("prediction shape        :", p.shape, "(one probability per point)")
print("point 0 is at", np.round(X[0], 2),
      "true label", int(y[0, 0]),
      "-> network says", round(float(p[0, 0]), 3))
```

The forward pass is those two lines inside `forward`. Every point flows through
the same arithmetic, and out comes a probability. But look at point 0: its true
label is `1` (inside), yet the network reports **`0.221`** — it is fairly sure
the point is *outside*. It is wrong, and it is wrong because nobody has tuned
the weights: `W1` and `W2` are still the random numbers we sprinkled in.

## Random weights predict nonsense

How wrong is the whole network? Turn each probability into a hard yes/no at the
`0.5` mark and compare with the truth:

```python
# continues
pred = (p > 0.5).astype(float)
accuracy = float((pred == y).mean())
print("accuracy with random weights:", round(accuracy, 3))
```

**`0.465`** — the network is right on 46.5% of the points, which is *worse than
flipping a coin*. That is exactly what we should expect: random weights encode
no knowledge of circles. Plotting the region the network currently calls
"inside" shows the damage — a jagged, meaningless split with nothing round
about it:

```python
# continues
gx, gy = np.meshgrid(np.linspace(-2, 2, 120), np.linspace(-2, 2, 120))
grid = np.column_stack([gx.ravel(), gy.ravel()])
_, gp = forward(grid)
zone = gp.reshape(gx.shape)

inside = y[:, 0] == 1
plt.figure(figsize=(4.4, 4.2))
plt.contourf(gx, gy, zone, levels=[0, 0.5, 1], colors=["#cfe3f5", "#f7d7b0"])
plt.scatter(X[inside, 0], X[inside, 1], c="tab:orange", s=14)
plt.scatter(X[~inside, 0], X[~inside, 1], c="tab:blue", s=14)
plt.gca().set_aspect("equal")
plt.xlabel("x1"); plt.ylabel("x2")
plt.title("Decision boundary — random, untrained weights")
```

The shaded regions are where the network guesses "inside" (orange) versus
"outside" (blue), and they have no relationship to the actual circle. The
*machine* is fully built — the forward pass runs, the shapes line up, a
probability comes out for every point. What is missing is not more code. It is
the right *numbers* in `W1`, `b1`, `W2`, `b2`.

That is the whole job of the next section: **tune the knobs** until the shaded
boundary curls up to hug the orange island. The forward pass you just wrote will
not change one character — we will only change the numbers it multiplies by.

!!! warning "Common mistakes"

    - **Expecting an untrained network to work.** With random weights the
      output is random. A near-50% accuracy on a two-class problem is a
      *correct* forward pass on an *untrained* model, not a bug.
    - **Wrong output activation.** Sigmoid is right here because the target is a
      0/1 label. For predicting an unbounded number, the last layer would have
      *no* activation; for choosing among many classes, it would be softmax.
    - **Bias shape mismatches.** We used `b1` of shape `(1, H)` so it *broadcasts*
      across every row of a batch. A shape of `(H,)` also works by broadcasting;
      `(H, 1)` would not. When in doubt, print the shapes.
    - **Reading the probability as certainty.** `0.221` does not mean "22.1%
      of the point is inside". It is the model's current, uninformed *guess* at
      the probability, and right now that guess is worthless.

## Check your understanding

1. The hidden layer has width 16. What are the shapes of `W1` and `W2`, and why
   is `W2` shaped the way it is?

    ??? success "Answer"

        `W1` is `(2, 16)`: it turns each 2-number point into 16 hidden numbers.
        `W2` is `(16, 1)`: it collapses those 16 hidden numbers into a single
        output. The hidden width 16 is the second dimension of `W1` and the
        first of `W2` — they must match for the multiply to line up.

2. If you deleted the `relu` and used `a1 = X @ W1 + b1` directly, what kind of
   boundary could the network draw, no matter how you set the weights?

    ??? success "Answer"

        Only a straight line. Without the bend the two layers collapse into one
        (Section 25.5.2), and a single linear layer through a sigmoid can only
        produce a straight decision boundary — hopeless for a circle. The ReLU
        is what makes a curved boundary even *possible*.

3. The forward pass is the same function before and after training. So what,
   precisely, does training change?

    ??? success "Answer"

        Only the numbers in `W1`, `b1`, `W2`, `b2`. The *structure* — two
        matrix multiplies with a ReLU and a sigmoid — is fixed. Training
        searches for values of those four arrays that make `forward` map inputs
        to the right labels. That search is [Section 25.5.4](04-learning.md).
