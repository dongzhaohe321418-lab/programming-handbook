# Chapter 25.5 · Exercises

## The chapter in brief

- A **neuron** is a weighted sum plus a bias, `w·x + b` — a dot product that
  weighs each input by how much it is trusted ([25.5.1](01-neuron-and-layer.md)).
- A **layer** is a row of neurons run at once as a single matrix multiply
  `W·x + b`; rows of `W` are neurons, columns are inputs.
- Two linear layers with nothing between them **collapse into one** matrix, so
  a network of pure matrix multiplies can only draw straight lines
  ([25.5.2](02-activations.md)).
- **Activation functions** — ReLU, sigmoid, tanh — put a bend between layers;
  that bend is what lets depth buy power, enough to solve XOR and bend a
  decision boundary into a circle.
- A network is a **function**: the **forward pass** alternates "multiply by a
  matrix" and "squash", turning an input into a prediction
  ([25.5.3](03-forward-pass.md)).
- With random weights the forward pass predicts nonsense — the structure is
  right, the *numbers* are wrong.
- The **loss** scores how wrong the network is in one number; **gradient
  descent** nudges every weight downhill; **backpropagation** works out each
  weight's share of the blame ([25.5.4](04-learning.md)).
- Training is a loop — forward, loss, backward, step — repeated over **epochs**
  until the loss falls; frameworks like PyTorch automate the backward step
  (autodiff) and run it on GPUs.
- A **graph neural network** runs on graphs by **message passing**: each node
  mixes in a summary of its neighbours, repeated a few rounds so information
  spreads ([25.5.5](05-gnn.md)).
- More message-passing rounds widen each node's **receptive field**; a few
  labelled nodes can classify a whole graph.
- A **convolution** is message passing on a grid, and **attention** is message
  passing on a fully-connected graph with learned edge weights — the insight
  that unites Parts V and VI.

### Key terms

| Term | What it means |
| --- | --- |
| [neuron](01-neuron-and-layer.md) | a weighted sum of inputs plus a bias — one score |
| [weight](01-neuron-and-layer.md) | how much a neuron trusts one input; the tuned knob |
| [bias](01-neuron-and-layer.md) | a neuron's constant offset — its baseline before any input |
| [layer](01-neuron-and-layer.md) | many neurons at once, computed as `W·x + b` |
| [activation function](02-activations.md) | the nonlinear bend applied between layers |
| [ReLU](02-activations.md) | $\max(0, z)$ — pass positives, block negatives |
| [sigmoid / softmax](../part5-math-primer.md) | squash to $(0,1)$ / to a probability distribution |
| [forward pass](03-forward-pass.md) | running the network's function, input to prediction |
| [MLP](03-forward-pass.md) | multi-layer perceptron — input, hidden layer(s), output |
| [loss](04-learning.md) | one number for how wrong the network is; lower is better |
| [gradient descent](../concept-index.md#g) | nudge each weight opposite its slope to lower the loss |
| [backpropagation](04-learning.md) | pass the output error backward to blame each weight |
| [epoch](04-learning.md) | one full pass over the training data |
| [message passing](05-gnn.md) | a node updates from a summary of its neighbours |
| [GNN](05-gnn.md) | a neural network that learns on graph-shaped data |
| [node features](05-gnn.md) | the vector attached to each node, updated each round |

Work these easiest-first. Sketch the arithmetic on paper where you can, *predict*
the printed output before you run the solution (Exercise 25.5.5 is built for
that), then run it and check. Every solution is a self-contained runnable block.

### Exercise 25.5.1 — One neuron by hand ●

A neuron has weights `[0.5, -1.0, 2.0]` and bias `0.1`. Compute its output for
the input `[2.0, 1.0, 0.5]` on paper, then verify with numpy.

??? success "Solution"

    On paper: $0.5(2.0) + (-1.0)(1.0) + 2.0(0.5) + 0.1 = 1.0 - 1.0 + 1.0 + 0.1
    = 1.1$.

    ```python
    import numpy as np

    w = np.array([0.5, -1.0, 2.0])
    x = np.array([2.0, 1.0, 0.5])
    b = 0.1
    print("neuron output:", round(float(w @ x + b), 3))
    ```

    The output is `1.1`. A neuron is a dot product plus a bias — nothing more.

### Exercise 25.5.2 — Predict the activations ●

Before running, write down what each of `relu`, `sigmoid`, and `tanh` returns
for the input vector `[-1.0, 0.0, 2.0]`. Then check.

??? success "Solution"

    ReLU blocks the negative and passes the rest: `[0, 0, 2]`. Sigmoid and tanh
    both send `0.0` to their midpoints (`0.5` and `0.0`) and squash the others.

    ```python
    import numpy as np

    z = np.array([-1.0, 0.0, 2.0])
    print("relu   :", np.round(np.maximum(0.0, z), 3).tolist())
    print("sigmoid:", np.round(1 / (1 + np.exp(-z)), 3).tolist())
    print("tanh   :", np.round(np.tanh(z), 3).tolist())
    ```

    ReLU gives `[0.0, 0.0, 2.0]`, sigmoid `[0.269, 0.5, 0.881]`, tanh
    `[-0.762, 0.0, 0.964]`. Sigmoid stays inside $(0,1)$; tanh inside $(-1,1)$.

### Exercise 25.5.3 — Two linear layers collapse ●

Show that pushing a vector through two weight matrices `W1` then `W2` gives the
same result as pushing it through the single matrix `W2 @ W1`.

??? success "Solution"

    ```python
    import numpy as np

    W1 = np.array([[1., -1.], [2., 0.], [0., 3.]])   # 2 inputs -> 3
    W2 = np.array([[1., 0., 1.], [0., 2., -1.]])      # 3 -> 2 outputs
    x = np.array([2., 1.])

    two_layers = W2 @ (W1 @ x)
    W_c = W2 @ W1
    print("through two layers:", two_layers.tolist())
    print("through W2 @ W1    :", (W_c @ x).tolist())
    print("collapsed matrix   :", W_c.tolist())
    print("identical?         :", np.allclose(two_layers, W_c @ x))
    ```

    Both give `[4.0, 5.0]`, and the two layers were secretly the one matrix
    `[[1, 2], [4, -3]]`. This is why a network needs a nonlinearity between
    layers — without one, extra layers add nothing.

### Exercise 25.5.4 — A deeper network ●●

Add a **second hidden layer** to the MLP from [Section 25.5.3](03-forward-pass.md),
so the shape is `2 → 16 → 16 → 1`. Write its `forward` function and confirm it
produces one probability per point.

??? success "Solution"

    A second hidden layer is one more `W`, `b`, and ReLU in the chain.

    ```python
    import numpy as np

    rng = np.random.default_rng(0)
    X = rng.uniform(-2, 2, size=(200, 2))

    def relu(z):    return np.maximum(0.0, z)
    def sigmoid(z): return 1.0 / (1.0 + np.exp(-z))

    init = np.random.default_rng(1)
    W1 = init.normal(0, 0.5, (2, 16));  b1 = np.zeros((1, 16))
    W2 = init.normal(0, 0.5, (16, 16)); b2 = np.zeros((1, 16))   # NEW layer
    W3 = init.normal(0, 0.5, (16, 1));  b3 = np.zeros((1, 1))

    def forward(X):
        a1 = relu(X @ W1 + b1)
        a2 = relu(a1 @ W2 + b2)        # the extra hidden layer
        return sigmoid(a2 @ W3 + b3)

    print("prediction shape:", forward(X).shape)
    ```

    The output is `(200, 1)` — one probability per point, as before. Training it
    would need one more line in the backward pass (blame flows through three
    layers now instead of two), but the forward pass grows by exactly one
    `relu(a @ W + b)`. Depth is just repetition.

### Exercise 25.5.5 — Predict a message-passing round ●●

A 4-node path graph `0 — 1 — 2 — 3` starts with a signal `[1, 0, 0, 0]` (only
node 0 is lit). Using **mean aggregation over self + neighbours**, predict each
node's value after one round *before* running the code.

??? success "Solution"

    Node 0 averages itself and node 1: $(1+0)/2 = 0.5$. Node 1 averages nodes 0,
    1, 2: $(1+0+0)/3 \approx 0.333$. Nodes 2 and 3 are too far to have heard the
    signal yet, so they stay `0`.

    ```python
    import numpy as np

    graph = {0: [1], 1: [0, 2], 2: [1, 3], 3: [2]}
    n = len(graph)
    A = np.zeros((n, n))
    for u in graph:
        A[u, u] = 1.0
        for v in graph[u]:
            A[u, v] = 1.0
    Ahat = A / A.sum(axis=1, keepdims=True)

    signal = np.array([1.0, 0.0, 0.0, 0.0]).reshape(-1, 1)
    after = Ahat @ signal
    print("after one round:", np.round(after[:, 0], 3).tolist())
    ```

    The result is `[0.5, 0.333, 0.0, 0.0]` — the signal has reached node 1 and
    no further. One round = one hop.

### Exercise 25.5.6 — Too big, too small, just right ●●

Train the circle MLP three times with learning rates `0.01`, `0.5`, and `20.0`,
recording the loss each epoch. Plot the three curves and explain what each
learning rate does.

??? success "Solution"

    ```python
    import numpy as np
    import matplotlib.pyplot as plt

    rng = np.random.default_rng(0)
    N = 200
    X = rng.uniform(-2, 2, size=(N, 2))
    y = ((X ** 2).sum(axis=1) < 1.4 ** 2).astype(float).reshape(N, 1)

    def relu(z):    return np.maximum(0.0, z)
    def sigmoid(z): return 1.0 / (1.0 + np.exp(-z))
    def bce(p, y):
        p = np.clip(p, 1e-7, 1 - 1e-7)
        return float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))

    def train(lr, epochs=300):
        init = np.random.default_rng(1)          # same start every time
        W1 = init.normal(0, 0.5, (2, 16)); b1 = np.zeros((1, 16))
        W2 = init.normal(0, 0.5, (16, 1)); b2 = np.zeros((1, 1))
        losses = []
        for _ in range(epochs):
            z1 = X @ W1 + b1; a1 = relu(z1); a2 = sigmoid(a1 @ W2 + b2)
            losses.append(bce(a2, y))
            dz2 = (a2 - y) / N
            dW2 = a1.T @ dz2; db2 = dz2.sum(0, keepdims=True)
            dz1 = (dz2 @ W2.T) * (z1 > 0)
            dW1 = X.T @ dz1;  db1 = dz1.sum(0, keepdims=True)
            W1 -= lr * dW1; b1 -= lr * db1; W2 -= lr * dW2; b2 -= lr * db2
        return losses

    plt.figure(figsize=(5.5, 3.4))
    for lr in (0.01, 0.5, 20.0):
        losses = train(lr)
        plt.plot(losses, label=f"lr = {lr}  (final {losses[-1]:.3f})")
    plt.xlabel("epoch"); plt.ylabel("loss"); plt.ylim(0, 1.4)
    plt.title("Learning rate: too small, just right, too big")
    plt.legend()
    ```

    - **`lr = 0.01` (too small)** barely moves — it ends near `0.526`, hardly
      down from the starting `0.665`. Correct direction, hopelessly slow.
    - **`lr = 0.5` (just right)** drops smoothly to about `0.082`.
    - **`lr = 20.0` (too big)** overshoots the valley every step: the loss
      *bounces* and ends around `0.724` — actually **worse than where it
      started**. A step size too large repeatedly leaps past the minimum.

### Exercise 25.5.7 — Two rounds versus three ●●

On the 8-node two-community graph from [Section 25.5.5](05-gnn.md), how many
nodes does node 3's representation draw on after 2 message-passing rounds versus
3? Explain the difference in terms of the receptive field.

??? success "Solution"

    ```python
    import numpy as np

    graph = {0: [1, 2], 1: [0, 2, 3], 2: [0, 1, 3], 3: [1, 2, 4],
             4: [3, 5, 6], 5: [4, 6, 7], 6: [4, 5, 7], 7: [5, 6]}
    n = len(graph)
    A = np.zeros((n, n))
    for u in graph:
        A[u, u] = 1.0
        for v in graph[u]:
            A[u, v] = 1.0
    Ahat = A / A.sum(axis=1, keepdims=True)

    H = np.eye(n)
    for rounds in (2, 3):
        Hk = np.linalg.matrix_power(Ahat, rounds) @ np.eye(n)
        reached = [i for i in range(n) if Hk[3, i] > 1e-9]
        print(f"{rounds} rounds: node 3 draws on {len(reached)} nodes {reached}")
    ```

    After 2 rounds node 3 reaches 7 nodes (everything except node 7); after 3
    rounds it reaches all 8. Each extra round adds one hop to the **receptive
    field**, so it takes 3 rounds for a signal to cross from node 3 all the way
    to node 7 on the far side of the bridge. More rounds do not add nodes to the
    graph — they let each node *see* further across it.

### Exercise 25.5.8 — Baby attention on the graph ●●●

Plain message passing averages all neighbours equally. Add **neighbour
weighting** — a baby version of attention — so that node 3 (the bridge) trusts
neighbours whose features resemble its own more than dissimilar ones. Show it
changes which neighbours dominate. Give community A nodes a feature of `+1` and
community B nodes `-1`; node 3 is in community A.

??? success "Solution"

    Score each neighbour by the product of features (a dot product for
    1-D features), softmax the scores into weights, then take the weighted
    average — exactly [Chapter 26's attention](../ch26-llm-internals/02-attention.md)
    in miniature.

    ```python
    import numpy as np

    def softmax(v):
        e = np.exp(v - v.max())
        return e / e.sum()

    # features: community A = +1 (nodes 0-3), community B = -1 (nodes 4-7)
    feat = np.array([1., 1., 1., 1., -1., -1., -1., -1.])
    neighbours = [3, 1, 2, 4]          # node 3 with self, plus 1, 2 (A) and 4 (B)

    vals = feat[neighbours]
    uniform = vals.mean()
    scores = feat[3] * vals            # similarity of each neighbour to node 3
    weights = softmax(scores)
    attention = float(weights @ vals)

    print("neighbours          :", neighbours)
    print("attention weights   :", np.round(weights, 3).tolist())
    print("uniform average     :", round(float(uniform), 3))
    print("attention-weighted  :", round(attention, 3))
    ```

    The uniform average is `0.5` — dragged down because the lone community-B
    neighbour (node 4) counts as much as the three community-A nodes. Attention
    gives the three similar neighbours weight `0.319` each and the dissimilar
    one only `0.043`, so the weighted result is `0.914` — much closer to node
    3's true community-A signal. Learning *which* neighbours to trust, instead
    of averaging them all, is the entire step from a plain GNN to attention.
