# 25.5.2 · Activation functions

We can now stack layers — so let us stack two and see what we get. The
surprising answer is: *nothing new*. Two layers of pure matrix multiplication
are mathematically identical to one layer, no matter how many you pile up. A
network built that way could be a mile deep and still only draw straight lines.
The one small ingredient that rescues the whole enterprise is the **activation
function** — a simple bend applied between layers — and this section shows,
by running it, both the collapse and the cure.

!!! abstract "In plain words"

    - **What it is.** An activation function is a simple curve applied to every
      number coming out of a layer, before it flows into the next layer.
    - **Picture it.** A chain of currency exchanges with *no fees*: dollars →
      euros → yen is just one combined rate, so the two hops give you nothing a
      single hop wouldn't. Add a fee at each desk — a bend that isn't a
      straight line — and the trip genuinely differs from any single exchange.
    - **Why it matters.** Without the bend, stacking layers is pointless: the
      whole network collapses to one layer and can only separate data a
      straight line could. The bend is what lets depth buy you power.

## Two linear layers are secretly one

Take an input, push it through one weight matrix, then through a second. Pure
linear algebra says $W_2(W_1\mathbf{x}) = (W_2 W_1)\mathbf{x}$ — the two
matrices can be multiplied together *once*, ahead of time, into a single matrix
$W_c = W_2 W_1$ that does the identical job. Here it is, run on real numbers:

```python
import numpy as np

rng = np.random.default_rng(7)
W1 = rng.normal(size=(4, 2))     # layer 1: 2 inputs -> 4 outputs
W2 = rng.normal(size=(3, 4))     # layer 2: 4 inputs -> 3 outputs
x = np.array([1.5, -0.7])

two_layers = W2 @ (W1 @ x)       # push through both
W_c = W2 @ W1                    # collapse them into ONE matrix first
one_layer = W_c @ x              # then push through the single matrix

print("through two layers:", np.round(two_layers, 3))
print("through one matrix:", np.round(one_layer, 3))
print("identical?        :", np.allclose(two_layers, one_layer))
print("collapsed shape   :", W_c.shape, "(3 outputs from 2 inputs — one layer)")
```

Both paths print **`[-0.326, -0.809, 1.252]`** — exactly equal. The two-layer
network was never more expressive than the single `(3, 2)` matrix `W_c`; the
extra layer bought precisely nothing. Add a third linear layer, a fourth, a
hundredth: they all fold into one matrix, and one matrix can only compute a
straight-line (linear) function of its inputs. A deep *linear* network is a
very expensive way to draw a single flat plane.

## The fix: bend the signal

The escape is to apply a **nonlinear** function to each number *between* the
layers — a curve that a single matrix cannot undo. Now $W_2 f(W_1\mathbf{x})$
genuinely cannot be flattened into $W_c\mathbf{x}$, because $f$ breaks the
algebra that let the matrices merge. Three activation functions do almost all
the work in practice.

- **ReLU** — $\operatorname{ReLU}(z) = \max(0, z)$. *Pass positive signals
  through unchanged; block negative ones at zero.* It is the default hidden-layer
  activation in modern networks because it is trivially cheap and trains well.
- **Sigmoid** — $\sigma(z) = 1/(1+e^{-z})$. *Squash any number into the range
  $(0, 1)$*, so the output reads as a probability. This is the two-outcome
  cousin of the **softmax** from the [math primer](../part5-math-primer.md).
- **tanh** — $\tanh(z)$. *Squash into $(-1, 1)$*, an S-curve centred on zero,
  useful when you want signed outputs.

```python
import numpy as np

def relu(z):    return np.maximum(0.0, z)
def sigmoid(z): return 1.0 / (1.0 + np.exp(-z))

z = np.array([-2.0, -0.5, 0.0, 0.5, 2.0])
print("input  :", z)
print("relu   :", np.round(relu(z), 3))
print("sigmoid:", np.round(sigmoid(z), 3))
print("tanh   :", np.round(np.tanh(z), 3))
```

Read the ReLU row: the two negative inputs became `0.0` (blocked), the zero
stayed `0.0`, and the positives `0.5` and `2.0` passed straight through. The
sigmoid row maps the same five numbers into $(0, 1)$, with `0.0` landing
exactly at `0.5` — the midpoint. tanh does the same but centred on zero, so
`0.0` maps to `0.0` and the sign is preserved. A picture makes the shapes
obvious:

```python
import numpy as np
import matplotlib.pyplot as plt

def relu(z):    return np.maximum(0.0, z)
def sigmoid(z): return 1.0 / (1.0 + np.exp(-z))

z = np.linspace(-5, 5, 200)
fig, axes = plt.subplots(1, 3, figsize=(9, 3))
for ax, (name, f) in zip(axes, [("ReLU", relu),
                                 ("sigmoid", sigmoid),
                                 ("tanh", np.tanh)]):
    ax.plot(z, f(z), linewidth=2)
    ax.axhline(0, color="gray", linewidth=0.5)
    ax.axvline(0, color="gray", linewidth=0.5)
    ax.set_title(name)
    ax.set_xlabel("input z")
    ax.set_ylabel("output")
fig.tight_layout()
```

Three bends. ReLU is a hinge — flat then rising. Sigmoid and tanh are
S-curves that flatten out at the extremes. Each is dirt cheap to compute, and
each is enough to break the collapse.

## Now the network can bend a boundary

Here is the payoff, made concrete with the smallest example that needs it: the
**XOR** problem. Four points, labelled by whether their two coordinates
*differ*: `(0,0)→0`, `(0,1)→1`, `(1,0)→1`, `(1,1)→0`. No straight line can
separate the two 1s from the two 0s — the classes sit on opposite diagonals.
We can *prove* a linear model is helpless, then watch a network with one ReLU
hidden layer nail it exactly.

First the impossibility. Any linear (affine) function $f(x_1,x_2)=ax_1+bx_2+c$
obeys an identity: the two diagonal sums are always equal.

```python
import numpy as np

rng = np.random.default_rng(0)
a, b, c = rng.normal(size=3)                 # ANY linear function you like
f = lambda p: a * p[0] + b * p[1] + c

diag_00_11 = f((0, 0)) + f((1, 1))
diag_01_10 = f((0, 1)) + f((1, 0))
print("f(0,0) + f(1,1) =", round(diag_00_11, 3))
print("f(0,1) + f(1,0) =", round(diag_01_10, 3))
print("always equal?   :", np.isclose(diag_00_11, diag_01_10))
print("but XOR wants   : f(0,0)+f(1,1) = 0, f(0,1)+f(1,0) = 2  -> impossible")
```

The two sums come out equal (both about `0.999` here) for *any* choice of
`a, b, c` — that is an algebraic fact, not luck. But XOR demands the first sum
be `0+0 = 0` and the second be `1+1 = 2`. A linear model literally cannot
satisfy both, so no single layer can ever learn XOR. Now add one ReLU hidden
layer of two neurons, with weights chosen by hand, and the wall falls:

```python
import numpy as np

def relu(z): return np.maximum(0.0, z)

X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]], dtype=float)
target = np.array([0, 1, 1, 0])

# Hidden layer: two ReLU neurons that carve the plane into pieces.
W1 = np.array([[1.0, 1.0],       # neuron A: fires on "at least one input"
               [1.0, 1.0]])
b1 = np.array([0.0, -1.0])       # neuron B: fires only on "both inputs"
# Output layer: combine the pieces.
W2 = np.array([1.0, -2.0])
b2 = 0.0

hidden = relu(X @ W1.T + b1)     # (4,2) hidden activations
out = hidden @ W2 + b2           # (4,) network output
print("network output:", out.tolist())
print("target (XOR)  :", target.tolist())
print("solved exactly:", np.allclose(out, target))
```

The output is **`[0.0, 1.0, 1.0, 0.0]`** — exactly XOR. The single ReLU between
the two layers let the network bend its decision surface into two pieces
instead of one flat cut. That bend is the entire reason activations exist, and
it scales: with enough hidden neurons and the right (learned) weights, a
network with one nonlinear hidden layer can approximate essentially any
function — a fact grand enough to have a name, the *universal approximation*
result. We will not prove it, but you just watched its smallest instance.

!!! warning "Common mistakes"

    - **Leaving out the activation.** A network of `Linear → Linear → Linear`
      with no bends between them is, provably, a single linear layer. It runs
      fine and learns almost nothing. This is a silent, common bug.
    - **Putting an activation on the final regression output.** A ReLU on the
      last layer clamps every prediction to be non-negative; a sigmoid clamps
      it to $(0,1)$. Those are right for probabilities and wrong for predicting,
      say, a temperature. Match the final activation to the task.
    - **Using sigmoid everywhere in deep hidden layers.** Its curve is nearly
      flat at both ends, so its slope there is almost zero — and [Section
      25.5.4](04-learning.md) will show why a near-zero slope stalls learning
      ("vanishing gradients"). ReLU's constant slope for positive inputs is a
      big reason it displaced sigmoid in hidden layers.
    - **Thinking more layers alone means more power.** Depth only helps *with*
      nonlinearities. Ten linear layers = one linear layer.

## Check your understanding

1. What does `relu(np.array([-3.0, 0.0, 4.0]))` return, and why?

    ??? success "Answer"

        `[0.0, 0.0, 4.0]`. ReLU is $\max(0, z)$: it replaces every negative
        value with zero and leaves non-negatives alone. `-3.0` is blocked,
        `0.0` stays, `4.0` passes through.

2. You stack five layers with no activation between them. How many *distinct*
   linear layers is your network equivalent to, and what kinds of data can it
   separate?

    ??? success "Answer"

        Exactly one — the five weight matrices multiply into a single matrix
        $W_c = W_5W_4W_3W_2W_1$. It can only separate data that a single
        straight line (or flat plane) could. The four extra layers add cost and
        zero expressive power.

3. Sigmoid maps every input into $(0, 1)$. Why is that the natural activation
   for the *final* neuron of a yes/no classifier, but a poor choice for the
   *hidden* layers of a deep network?

    ??? success "Answer"

        A yes/no classifier wants its final output to read as a probability,
        and $(0, 1)$ is exactly the probability range — so sigmoid is perfect
        at the end. But in hidden layers its curve is almost flat for large
        positive or negative inputs, so its slope there is nearly zero; stack
        many and the learning signal shrinks toward nothing as it passes back
        through them. ReLU keeps a healthy slope, which is why hidden layers
        use it.
