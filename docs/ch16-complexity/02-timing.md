# 16.2 Measuring running time

Big-O predicts how cost *grows*; it deliberately says nothing about whether
your code takes a millisecond or a minute at the sizes you actually run.
For that you must measure — and measuring is surprisingly easy to do wrong.
This section gives you a small, trustworthy protocol for timing Python
code, then a lovely trick — the *doubling experiment* — that lets you
discover an algorithm's growth family purely from a stopwatch, no source
code reading required.

## The timing protocol: repeat, take the minimum

Python's honest stopwatch is `time.perf_counter()` — a high-resolution
timer designed for exactly this job. Read it before and after the work; the
difference is elapsed seconds.

But a single measurement is polluted by whatever else your machine was doing
in that instant. So the protocol has three steps:

1. **Time it** — read `perf_counter()`, do the work, read it again.
2. **Repeat** the exact same work several times.
3. **Keep the minimum** of the timings you collected.

```python
import time

def sum_of_squares(n):
    total = 0
    for i in range(n):
        total += i * i
    return total

timings = []
for _ in range(5):                        # repeat...
    start = time.perf_counter()
    sum_of_squares(100_000)               # ...the exact same work...
    timings.append(time.perf_counter() - start)

print("all 5 runs (ms):", "  ".join(f"{t * 1000:6.2f}" for t in timings))
print(f"best run   (ms): {min(timings) * 1000:6.2f}")
```

Run it a few times: the individual numbers wobble, the minimum is far
steadier.

Why the minimum and not the average? Because noise on a computer is strictly
*additive* — a background process, a garbage collection, a cache miss can
only make a run slower, never faster. The fastest run you observed is
therefore the closest to the code's true cost, and averaging would smear the
noise back in.

## The doubling experiment

Here is the payoff idea of this section. Suppose an algorithm's cost
follows a power law, $T(n) \approx c \cdot n^k$. Then

$$ \frac{T(2n)}{T(n)} \approx \frac{c\,(2n)^k}{c\,n^k} = 2^k, $$

and the messy constant $c$ — the laptop, the Python version, the units —
**cancels out completely**. Time the function at $n$ and at $2n$, divide, and
the ratio names the family:

| Measured $T(2n)/T(n)$ | Exponent $k$ | Family |
| --- | --- | --- |
| near $2 = 2^1$ | $1$ | linear, $O(n)$ |
| near $4 = 2^2$ | $2$ | quadratic, $O(n^2)$ |
| near $8 = 2^3$ | $3$ | cubic, $O(n^3)$ |

So you can identify an algorithm's growth family without reading a line of
its source. (A ratio barely above $1$ means the cost hardly responds to $n$
at all — constant or logarithmic; those two the stopwatch cannot easily tell
apart.)

Two candidates: summing a range (touch each value once — linear), and
finding the closest pair of values by brute force (compare every pair —
quadratic, like Pattern 3 of [section 16.1](01-big-o.md)):

```python
import time

def time_best_of(func, n, repeats=3):
    best = float("inf")
    for _ in range(repeats):
        start = time.perf_counter()
        func(n)
        best = min(best, time.perf_counter() - start)
    return best

def list_sum(n):                          # linear suspect
    total = 0
    for x in range(n):
        total += x
    return total

def closest_gap(n):                       # quadratic suspect
    values = [(i * 37) % n for i in range(n)]
    best = None
    for i in range(n):
        for j in range(i + 1, n):
            gap = abs(values[i] - values[j])
            if best is None or gap < best:
                best = gap
    return best

n = 20_000
ratio = time_best_of(list_sum, 2 * n) / time_best_of(list_sum, n)
print(f"list_sum   : T(2n)/T(n) = {ratio:4.1f}   (near 2 -> linear)")

n = 400
ratio = time_best_of(closest_gap, 2 * n) / time_best_of(closest_gap, n)
print(f"closest_gap: T(2n)/T(n) = {ratio:4.1f}   (near 4 -> quadratic)")
```

Your exact decimals will differ run to run — that is measurement, not
mathematics — but the first ratio lands near 2 and the second near 4.
Notice the input sizes: 20,000 for the linear function but only 400 for
the quadratic one. Quadratic cost at $n = 800$ already means ~320,000 pair
comparisons; doubling experiments on slow-growing budgets keep everything
under a couple of seconds.

## The log-log plot: slope = exponent

The doubling experiment uses two sizes; a plot can use many. The trick is
to draw both axes on a logarithmic scale. Taking logs of
$T(n) = c \cdot n^k$ gives

$$ \log T = k \log n + \log c, $$

which is a *straight line* whose slope is $k$ — the exponent appears as
pure geometry. Measure at several sizes, plot on log-log axes, and read
the family off the tilt of the line:

```python
import time
import numpy as np
import matplotlib.pyplot as plt

def time_best_of(func, n, repeats=3):
    best = float("inf")
    for _ in range(repeats):
        start = time.perf_counter()
        func(n)
        best = min(best, time.perf_counter() - start)
    return best

def list_sum(n):
    total = 0
    for x in range(n):
        total += x
    return total

def closest_gap(n):
    values = [(i * 37) % n for i in range(n)]
    best = None
    for i in range(n):
        for j in range(i + 1, n):
            gap = abs(values[i] - values[j])
            if best is None or gap < best:
                best = gap
    return best

linear_sizes = [2_000, 4_000, 8_000, 16_000, 32_000]
quad_sizes = [100, 200, 400, 800]

linear_times = [time_best_of(list_sum, n) for n in linear_sizes]
quad_times = [time_best_of(closest_gap, n) for n in quad_sizes]

slope_lin = np.polyfit(np.log(linear_sizes), np.log(linear_times), 1)[0]
slope_quad = np.polyfit(np.log(quad_sizes), np.log(quad_times), 1)[0]
print(f"fitted slope, list_sum   : {slope_lin:.2f}  (theory: 1)")
print(f"fitted slope, closest_gap: {slope_quad:.2f}  (theory: 2)")

plt.loglog(linear_sizes, linear_times, "o-",
           label=f"list_sum (slope $\\approx$ {slope_lin:.2f})")
plt.loglog(quad_sizes, quad_times, "s-",
           label=f"closest_gap (slope $\\approx$ {slope_quad:.2f})")
plt.xlabel("input size n (log scale)")
plt.ylabel("best-of-3 time in seconds (log scale)")
plt.title("On log-log axes, the slope is the exponent")
plt.legend()
plt.grid(True, which="both", alpha=0.3)
```

Expect the fitted slopes near 1 and 2 (small inputs are noisy — see the
pitfalls below — so 0.9 or 2.1 is a perfectly good day). This one picture
is the empirical twin of everything section 16.1 derived by counting.

## Timing pitfalls

Timing code looks trivial and is full of traps. The big four:

1. **No warm-up.** The very first execution often pays one-off costs —
   imports finishing, files and caches filling, and (in the browser) the
   Python runtime itself settling in. Watch the first run stand out:

    ```python
    import time

    def work(n):
        return sum(i * i for i in range(n))

    for run in range(1, 6):
        start = time.perf_counter()
        work(200_000)
        elapsed = time.perf_counter() - start
        print(f"run {run}: {elapsed * 1000:6.2f} ms")
    ```

    The first run is typically the slowest — sometimes by a lot. The
    protocol's *repeat and take the minimum* absorbs this automatically;
    timing something exactly once does not.

2. **Inputs too tiny.** Below a few thousand operations, the thing you are
   timing is smaller than the cost of the timing machinery, loop setup,
   and general overhead around it. A doubling experiment at $n = 10$
   versus $n = 20$ measures mostly fog. Grow $n$ until times reach at
   least a few milliseconds before trusting any ratio.

3. **Timing `print()`.** Writing to the screen is I/O — thousands of times
   more expensive than arithmetic, with a cost set by the console, not
   your algorithm. If the code under test prints inside its loop, you are
   benchmarking the terminal. Compute first; print after the clock stops.

4. **Changing two things at once.** Compare algorithm A at size $n$ with
   algorithm B at size $n$ — same data, same machine, same session. A
   timing taken yesterday is not a control group.

## When measurement beats theory

If Big-O were the whole story, this section would not exist. Big-O hides
constants, and **at real sizes the constants can win.** Two everyday
examples:

- **Small $n$ makes everything equal.** A linear scan of a five-element list
  beats every fancier structure, because five of anything is nothing.
- **The same family can hide a large constant factor.** Python's built-in
  `sort` is an $O(n \log n)$ algorithm with superbly tuned constants, written
  in C; it demolishes any $O(n \log n)$ sort you write in Python.

Theory tells you how the race ends *as $n$ grows without bound*; only
measurement tells you who is ahead at the $n$ your program actually sees.

The professional habit is to use both: Big-O to choose candidates that won't
collapse at scale, and the stopwatch — protocol, doubling, log-log — to pick
among them at your sizes.

!!! warning "Common mistakes"

    - **Averaging instead of taking the minimum.** Noise only ever adds
      time, so the mean drags in every background hiccup; the minimum of
      several runs is the cleanest estimate of true cost.
    - **Trusting one run.** A single measurement can be off by a large
      factor thanks to warm-up or a background task. Always repeat.
    - **Doubling from a tiny base.** If $T(n)$ is microseconds, overhead
      drowns the signal and the ratio is meaningless. Scale $n$ up until
      times are comfortably measurable, then double.
    - **Leaving `print` inside the timed region.** I/O costs swamp
      computation; move all output outside the start/stop pair.

## Check your understanding

1. Why is the *minimum* of repeated timings a better estimate than the
   *mean*?

    ??? success "Answer"

        Interference (other processes, garbage collection, cache misses)
        can only slow a run down, never speed it up. The distribution of
        timings is true-cost-plus-nonnegative-noise, so its minimum is the
        observation with the least noise; the mean includes all of it.

2. You time a mystery function: $T(5000) = 0.02$ s and
   $T(10000) = 0.16$ s. What growth family do you suspect, and why?

    ??? success "Answer"

        The ratio is $0.16 / 0.02 = 8 = 2^3$ — doubling the input cost
        eight times the time, suggesting cubic, $O(n^3)$. (One pair of
        measurements is a hint, not a verdict: repeat at more sizes, or
        fit a log-log slope, before betting on it.)

3. On a log-log plot, one algorithm's line has slope 1 and another's has
   slope 2, but the slope-2 line sits *lower* for all plotted sizes. What
   is going on, and which algorithm should you pick?

    ??? success "Answer"

        The quadratic algorithm has much smaller constants, so it is
        genuinely faster at every size you measured. Straight lines with
        different slopes must eventually cross: beyond the crossover the
        slope-1 algorithm wins. Pick based on the sizes you expect — and
        if they may grow, prefer the flatter slope.

4. A classmate benchmarks two sorts by timing each once, on different
   lists, with a `print` inside one of them. Name the three protocol
   violations.

    ??? success "Answer"

        (1) No repetition — single runs are noise-dominated (and the first
        run pays warm-up). (2) Different inputs — the comparison changes
        two variables at once. (3) I/O inside the timed region — the
        `print` benchmarks the console, not the sort.
