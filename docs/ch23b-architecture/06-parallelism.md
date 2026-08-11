# 23.5.6 · Parallelism and modern hardware

Every earlier section in this chapter made *one* instruction stream faster:
fewer instructions, lower CPI, a shorter cycle, a deeper pipeline. This one
changes the question. When a single core stopped getting much faster, the only
way left to go faster was to do **many things at once**. That single pivot
explains the shape of all modern hardware — multicore CPUs, GPUs, and the
tensor engines that run the models you built in Part V. This is Chapter 6 of
Patterson & Hennessy's *Computer Organization and Design* (COD), kept runnable
and tied back to the rest of the book.

## Why parallelism at all

!!! abstract "In plain words"

    - **What it is.** Speed used to arrive for free: each year the clock ticked
      faster and yesterday's code ran quicker with no effort. That stopped.
      Now speed comes from splitting work across many units running at once.
    - **Picture it.** One checkout lane that can't scan faster versus opening
      twenty lanes. The scanner's speed is capped, so you add lanes — and now
      *how you split the shoppers* decides whether it helps.
    - **Why it matters.** The burden moved from hardware to *you*. A faster
      clock sped up any program automatically; more cores only help code
      *written* to use them. Parallelism is a software problem now.

The cause is the **power wall** from [23.5.1](01-performance.md#the-power-wall-why-one-core-became-many):
dynamic power is roughly $C V^2 f$, Dennard scaling ended, and pushing the clock
$f$ up drove power (and heat) up faster than performance. So chips stopped
selling more gigahertz and started selling more **cores**. The rest of this
section is the catalogue of ways hardware does many things at once — and the
stubborn arithmetic (Amdahl again) that limits how much it helps.

## The kinds of parallelism

!!! abstract "In plain words"

    - **What it is.** "Parallelism" is really four different ideas at four
      different scales — from overlapping steps *inside* one instruction stream
      up to spreading millions of requests across a datacenter.
    - **Picture it.** A kitchen: one cook overlapping prep-and-cook steps
      (instruction-level), one motion that chops many carrots at once
      (data-level), several cooks at several stations (thread-level), and a
      chain of restaurants serving different cities (request-level).
    - **Why it matters.** They stack. A real machine uses all four at once, and
      knowing which is which tells you *why* a given speed-up did or didn't show
      up.

| Kind | Scale | What runs at once | Hardware that does it | Everyday example |
| --- | --- | --- | --- | --- |
| **Instruction-level (ILP)** | within one core | steps of *different* instructions overlap | pipelining, superscalar issue → [23.5.5](05-pipelining.md) | an assembly line: fetch the next order while cooking this one |
| **Data-level (DLP)** | within one core | one operation over *many* data items | SIMD / vector units, GPUs | chop every carrot with one press |
| **Thread-level (TLP)** | across cores | independent instruction streams | multicore CPUs, hardware threads | several cooks at several stations |
| **Request-level (RLP)** | across machines | independent user requests | datacenters, load balancers | a restaurant chain serving many cities |

The four are not competitors; a phone doing video calls uses **all four at
once**. The rest of the section takes the middle two — data-level and
thread-level — because those are the ones your code most directly controls, then
climbs to GPUs and specialized chips.

## SIMD: one instruction, many data lanes

!!! abstract "In plain words"

    - **What it is.** **SIMD** — Single Instruction, Multiple Data — applies one
      operation to a whole row of values in a single step, instead of looping
      over them one at a time.
    - **Picture it.** A stamp that prints eight cells of a spreadsheet at once
      versus filling them cell by cell. Same operation, applied in parallel
      across the row.
    - **Why it matters.** It is free parallelism *inside one core*: the hardware
      already has wide lanes, and using them turns one loop iteration into eight
      (or sixteen) useful results per instruction.

You have already used SIMD without naming it. Every time you replace a Python
`for` loop with a numpy array operation, numpy hands the work to code that runs
the same instruction across many data lanes at once. We can *time* the
difference on the exact same computation:

```python
import numpy as np
import time

# Same math two ways: y = a*a + b, over a million elements.
n = 1_000_000
rng = np.random.default_rng(0)
a = rng.random(n)
b = rng.random(n)

# 1) Scalar: a plain Python loop, one element per iteration (no SIMD).
a_list, b_list = a.tolist(), b.tolist()
start = time.perf_counter()
y_scalar = [a_list[i] * a_list[i] + b_list[i] for i in range(n)]
t_scalar = time.perf_counter() - start

# 2) Vectorized: one numpy expression -> SIMD-style data parallelism under it.
start = time.perf_counter()
y_vec = a * a + b
t_vec = time.perf_counter() - start

print(f"scalar Python loop : {t_scalar*1000:8.1f} ms")
print(f"numpy vectorized   : {t_vec*1000:8.1f} ms")
print(f"vectorized is about {t_scalar / t_vec:.0f}x faster")
print("same answer?", np.allclose(y_scalar, y_vec))
```

The two results are identical (`same answer? True`), but the numpy version is
**dramatically faster** — typically tens of times, often 50–100× on this page's
runner (your exact ratio will vary with the machine). Two things are happening
at once, and both matter:

- **No interpreter per element.** The Python loop pays interpreter overhead a
  million times; numpy pays it once and does the million multiplies in compiled
  code — the same lesson as [16.2](../ch16-complexity/02-timing.md).
- **Data-level parallelism underneath.** That compiled code uses the CPU's SIMD
  units, applying the multiply-add across many lanes per instruction. This is
  DLP from the table above: **numpy's vectorization *is* SIMD**, one instruction
  over many data.

The habit "push the loop into numpy" that you learned for readability is, at the
hardware level, the habit "let the SIMD lanes do the work."

## Multicore — and Amdahl comes back to collect

!!! abstract "In plain words"

    - **What it is.** A **multicore** chip has several complete CPUs (cores) on
      one piece of silicon. Split a program across them and, in the best case,
      $n$ cores finish in $1/n$ the time.
    - **Picture it.** Painting a fence with 8 painters. If the fence divides
      cleanly, it's 8× faster — but the one gate only one painter can reach, and
      the minute spent handing out brushes, don't get any faster.
    - **Why it matters.** Real programs always have a serial part, and Amdahl's
      law says that part sets a hard ceiling — which is why 8 cores almost never
      give 8×.

Thread-level parallelism is where the extra cores from the power wall are
supposed to pay off. But Amdahl's law from
[23.5.1](01-performance.md#amdahls-law) applies exactly, now with $s = n$ cores
speeding up the parallel fraction $p$:

```python
import numpy as np
import matplotlib.pyplot as plt

def multicore_speedup(p, n):
    """Amdahl's law: fraction p runs in parallel on n cores; (1-p) stays serial."""
    return 1.0 / ((1 - p) + p / n)

# A program that is 90% parallelizable, run on more and more cores.
p = 0.90
print(f"a {p:.0%}-parallel program on n cores:")
for n in [2, 4, 8, 16]:
    sp = multicore_speedup(p, n)
    print(f"  {n:>2} cores -> {sp:5.2f}x speedup   "
          f"({sp/n:4.0%} efficiency)")
print(f"  infinite cores -> {1/(1-p):.1f}x   (the serial 10% caps it)")

cores = np.arange(1, 33)
plt.figure(figsize=(7, 4.5))
for p_val in [0.50, 0.75, 0.90, 0.95]:
    plt.plot(cores, [multicore_speedup(p_val, n) for n in cores],
             marker=".", label=f"p = {p_val:.2f}")
plt.plot(cores, cores, "k--", lw=0.8, label="ideal (n cores = nx)")
plt.xlabel("number of cores (n)")
plt.ylabel("speed-up")
plt.title("Multicore speed-up: Amdahl's law vs the ideal line")
plt.legend()
plt.grid(True, alpha=0.3)
```

The table tells the sobering story: a 90%-parallel program on **8 cores** reaches
only **4.71×**, not 8× — **59% efficiency** — and even infinite cores cap out at
**10×**, because the serial 10% never speeds up. The plot shows every curve
peeling away from the dashed "ideal" line: the more cores you add, the more the
un-parallelizable remainder dominates. Adding cores has sharply diminishing
returns, and the fix is never "more cores" — it is **shrinking the serial
fraction**.

!!! note "Why Python makes this worse: the GIL"

    In CPython, the **Global Interpreter Lock** means only one thread runs
    Python bytecode at a time, so pure-Python threads do *not* give you
    thread-level parallelism on multiple cores — the serial fraction is
    effectively 100%. That is why Python reaches for multiple *processes*
    (or numpy/C extensions that release the lock) to use many cores; see
    [23.1](../ch23-os/01-os-processes.md#threads-sharing-the-apartment).

## GPUs: thousands of simple lanes

!!! abstract "In plain words"

    - **What it is.** A **GPU** trades a few fast, clever cores for *thousands*
      of small, simple ones. Each lane is slower on its own, but there are so
      many that fully parallel work flies.
    - **Picture it.** A CPU is a handful of master chefs; a GPU is a stadium of
      line cooks each doing one simple step. For one elaborate dish the chefs
      win; for a million identical burgers, the stadium wins overwhelmingly.
    - **Why it matters.** Matrix math — the core of deep learning — is exactly
      "the same simple operation over enormous grids of numbers," which is what
      those thousands of lanes were built for.

A GPU is data-level parallelism taken to the extreme. A toy accounting of *why*
it wins on parallel work, and *loses* on serial work:

```python
# A toy model: total throughput = (number of lanes) x (per-lane rate).
# CPU: few fast lanes.  GPU: thousands of slower lanes.
cpu_lanes, cpu_ghz = 8, 3.0
gpu_lanes, gpu_ghz = 4096, 1.5

cpu_throughput = cpu_lanes * cpu_ghz     # arbitrary "ops/sec" units
gpu_throughput = gpu_lanes * gpu_ghz
print(f"CPU: {cpu_lanes:>4} lanes x {cpu_ghz} GHz = {cpu_throughput:>7.0f} units")
print(f"GPU: {gpu_lanes:>4} lanes x {gpu_ghz} GHz = {gpu_throughput:>7.0f} units")
print(f"on fully parallel work, GPU throughput is "
      f"{gpu_throughput / cpu_throughput:.0f}x the CPU")

# But each GPU lane is slower, so a single SERIAL task is worse on the GPU:
print(f"on one serial task, a GPU lane is "
      f"{cpu_ghz / gpu_ghz:.0f}x slower per step than a CPU core")
```

On fully parallel work the GPU's throughput is about **256×** the CPU's — but on
a single serial task, each GPU lane is **2×** slower per step. That is the whole
trade in two numbers: **a GPU is not a faster computer, it is a wider one.** It
shines only when the work is thousands of independent, identical operations —
which is precisely a matrix multiply. That is why the neural networks you trained
by hand in [Chapter 25.5](../ch25b-neural-networks/index.md) and the models you
served in [Chapter 27](../ch27-inference/index.md) run on GPUs: a forward pass is
a stack of big matrix multiplies, the most data-parallel workload there is.
(This toy ignores memory bandwidth, which the last section fixes.)

## Domain-specific architectures: the TPU

!!! abstract "In plain words"

    - **What it is.** When general-purpose chips stopped getting faster,
      designers built chips that do *one kind of work* extremely well. A
      **TPU** (Tensor Processing Unit) is built almost entirely to multiply
      matrices.
    - **Picture it.** A general chef's knife versus a purpose-built machine on a
      production line that does only one cut, but perfectly and endlessly. Give
      up flexibility, win enormously on the one job.
    - **Why it matters.** The end of Dennard scaling made specialization the
      last big lever. A TPU's **systolic array** wrings far more compute out of
      each byte fetched from memory than a general CPU can.

The TPU's heart is a **systolic array**: a grid of tiny multiply-accumulate cells
through which the matrix values *flow*, so each value loaded from memory feeds
many multiplications instead of being re-fetched. The payoff is **data reuse**:

```python
# Why a systolic array is efficient: each loaded value is reused many times.
# Multiply two N x N matrices. Total work is fixed; memory traffic is not.
N = 8

macs = N ** 3                 # multiply-accumulate operations: N^3
distinct_inputs = 2 * N * N   # each matrix has N^2 numbers; load each once
input_uses = 2 * macs         # every MAC consumes one value from each matrix
reuse = input_uses / distinct_inputs

print(f"{N}x{N} @ {N}x{N} matrix multiply:")
print(f"  multiply-accumulates (compute) : {macs}")
print(f"  distinct inputs (memory loads) : {distinct_inputs}")
print(f"  each loaded value is reused     : {reuse:.0f}x   (= N)")
print(f"\ncompute grows as N^3 but memory as N^2, so a systolic array is")
print(f"compute-bound: it keeps {macs} multipliers busy from just "
      f"{distinct_inputs} loads.")
```

For an 8×8 matmul there are **512** multiply-accumulates but only **128**
distinct inputs to load, so each value is reused **8×** (exactly $N$). Because
compute grows as $N^3$ while the data to fetch grows only as $N^2$, a systolic
array can keep a huge grid of multipliers fed from a trickle of memory traffic —
that reuse is why a TPU does matrix math so much more efficiently per watt than a
general CPU. The cost of every one of these matmuls, added up across a model, is
the inference arithmetic of [Chapter 27](../ch27-inference/index.md).

## The memory wall: parallel compute still waits

!!! abstract "In plain words"

    - **What it is.** Compute got parallel and fast, but memory bandwidth did
      not keep up. Past a point, adding compute lanes does nothing — the lanes
      sit idle waiting for data. That gap is the **memory wall**.
    - **Picture it.** Twenty chefs (compute) fed by one narrow doorway to the
      pantry (memory). Hire more chefs and they just queue at the door; the
      doorway, not the chefs, sets the pace.
    - **Why it matters.** It decides whether a workload is *compute-bound*
      (helped by more lanes) or *memory-bound* (helped only by more bandwidth or
      better locality) — the whole reason the memory hierarchy exists.

Whether more lanes help depends on **arithmetic intensity**: how many
computations you do per byte of memory you move. Below a machine's *ridge point*,
you are memory-bound and extra compute is wasted:

```python
# A machine can do 'peak' compute/sec and move 'bw' bytes/sec.
# A kernel with arithmetic intensity I (flops per byte) achieves:
#     min(peak, I * bw)
peak = 1000.0   # GFLOP/s of compute available
bw   = 100.0    # GB/s of memory bandwidth

ridge = peak / bw   # ridge point: intensity where memory stops being the limit
print(f"ridge point = {ridge:.0f} flops/byte "
      f"(above this: compute-bound; below: memory-bound)\n")

for intensity in [2, 10, 20]:
    achieved = min(peak, intensity * bw)
    bound = "compute-bound" if intensity * bw >= peak else "MEMORY-bound"
    print(f"  intensity {intensity:>2} flops/byte -> {achieved:>6.0f} GFLOP/s "
          f"({achieved/peak:4.0%} of peak, {bound})")
```

The ridge point is **10 flops/byte**. A kernel that does only **2** flops per
byte reaches just **200 GFLOP/s — 20% of peak** — and is memory-bound: giving it
more compute lanes changes nothing, because they starve. A kernel at **20**
flops/byte saturates the full **1000 GFLOP/s**. This is why all the parallelism
above eventually circles back to the
[memory hierarchy](../ch23-os/04-memory-hierarchy.md): caches, locality, and
bandwidth decide whether your thousands of lanes are working or waiting. Fast
compute and slow memory are the two halves of every performance story — the
compute half is this chapter, the memory half is [23.4](../ch23-os/04-memory-hierarchy.md).

!!! warning "Common mistakes"

    - **Expecting $n$ cores to give $n×$.** Amdahl's law caps you at
      $1/(1-p)$; the serial fraction, not the core count, sets the ceiling. Cut
      the serial part before buying cores.
    - **Thinking Python threads use many cores.** The GIL serializes CPython
      bytecode, so CPU-bound pure-Python threads do not scale across cores. Use
      processes, or numpy/C extensions that release the lock.
    - **Assuming a GPU is just a faster CPU.** It is *wider*, not faster per
      lane. It wins only on massively data-parallel work; a serial task can run
      slower on a GPU than on a CPU.
    - **Ignoring the memory wall.** More compute lanes help only a
      compute-bound kernel. A memory-bound kernel needs better locality or more
      bandwidth — throwing lanes at it just adds idle lanes.

## Check your understanding

1. A workload is 95% parallelizable. What speed-up do 20 cores give, and what
   is the absolute ceiling no number of cores can beat?

    ??? success "Answer"
        Amdahl with $p = 0.95$, $n = 20$: $1/((1-0.95) + 0.95/20)
        = 1/(0.05 + 0.0475) = 1/0.0975 \approx 10.3×$. The ceiling is
        $1/(1-0.95) = 20×$ — even infinite cores can't beat it, because the
        serial 5% never speeds up.

        ```python
        def speedup(p, n): return 1 / ((1 - p) + p / n)
        print(f"20 cores: {speedup(0.95, 20):.1f}x,  ceiling: {1/(1-0.95):.0f}x")
        ```

2. Replacing a Python `for` loop with a numpy expression made your code 60×
   faster. Name the *two* distinct effects, and which one is "parallelism."

    ??? success "Answer"
        (1) **Interpreter overhead removed** — the million per-element Python
        dispatches collapse into one compiled call (the
        [16.2](../ch16-complexity/02-timing.md) effect). (2) **Data-level
        parallelism** — the compiled code uses the CPU's SIMD lanes to apply one
        instruction across many values at once. The *second* is the parallelism;
        the first is just avoiding interpreter tax. Both contribute to the 60×.

3. Why are GPUs so well suited to deep learning specifically?

    ??? success "Answer"
        A forward (or backward) pass through a neural network is dominated by
        large **matrix multiplies** — the same multiply-accumulate applied over
        enormous grids of numbers, with no dependencies between them. That is
        the maximally data-parallel workload, and a GPU's thousands of lanes are
        built for exactly it. The models in
        [Chapter 25.5](../ch25b-neural-networks/index.md) and
        [Chapter 27](../ch27-inference/index.md) run on this hardware for that
        reason.

4. You add more compute lanes to a kernel and its performance doesn't budge.
   What is the likely cause, and what actually helps?

    ??? success "Answer"
        The kernel is **memory-bound** — below the ridge point, so its speed is
        set by memory bandwidth, not compute. Extra lanes just wait for data.
        What helps is raising arithmetic intensity (better locality/data reuse,
        as a systolic array does) or more memory bandwidth — the domain of the
        [memory hierarchy](../ch23-os/04-memory-hierarchy.md), not more cores.

!!! info "Where to go deeper — Patterson & Hennessy"

    This section follows Chapter 6 of **Patterson & Hennessy, *Computer
    Organization and Design* (RISC-V edition)**: Flynn's taxonomy and the kinds
    of parallelism, SIMD/vector units, multicore and the Amdahl limits on
    scaling, GPUs as data-parallel processors, domain-specific architectures
    like the TPU's systolic array, and the roofline model of the memory wall.
    COD develops each with real hardware and measured roofline plots; this
    section is its runnable on-ramp — and the bridge from architecture to the
    AI infrastructure of [Part V](../ch27-inference/index.md).
