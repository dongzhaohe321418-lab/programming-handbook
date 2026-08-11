# 23.5.1 · What makes a computer fast

Ask "which computer is faster?" and almost everyone reaches for one number:
the clock speed in gigahertz. It is the number on the box, the number in the
ad — and on its own it is close to meaningless. This section replaces that
single number with the handful of quantities that *actually* decide speed,
each one small enough to compute in a few lines of Python. By the end you will
be able to look at two chip designs and say, with arithmetic instead of a hunch,
which one finishes the job first. This is Chapter 1 of Patterson & Hennessy's
*Computer Organization and Design* (COD), rebuilt so every claim is runnable.

## The trap of "fast"

!!! abstract "In plain words"

    - **What it is.** "Fast" is not one thing. **Response time** is how long
      one task takes; **throughput** is how many tasks finish per second. A
      change can improve one and hurt the other.
    - **Picture it.** One sports car versus a city bus network. The car has the
      best *response time* (you, personally, arrive soonest). The buses have the
      best *throughput* (far more people moved per hour). Neither is simply
      "faster."
    - **Why it matters.** Clock speed measures neither directly. A higher clock
      can be dragged down by an instruction set that needs more, slower steps —
      so the box number and the finish line disagree.

Two honest ways to say "faster," and they are not the same question:

- **Response time (latency)** — elapsed time for *one* task, start to finish.
  What you feel when a page loads or a build runs. Lower is better.
- **Throughput (bandwidth)** — tasks completed per unit time across the whole
  workload. What a datacenter is billed on. Higher is better.

Clock speed — the **clock rate**, in cycles per second — is tempting because it
is a single big number. But a cycle is just a tick; what matters is how many
ticks a job needs and how long each tick lasts. A 4 GHz chip that needs three
ticks per useful step can easily lose to a 3 GHz chip that needs one. To compare
honestly we need to open up "time per task." That is the next idea, and it is
the most important equation in the chapter.

## The CPU performance equation

!!! abstract "In plain words"

    - **What it is.** The time a program takes on the CPU is exactly three
      things multiplied together: how many instructions it runs, how many clock
      cycles each instruction costs on average, and how long a cycle lasts.
    - **Picture it.** Driving somewhere: total time = (number of blocks) ×
      (seconds spent per block) — and seconds-per-block itself splits into how
      many stop-lights per block and how long each light is.
    - **Why it matters.** It is the whole game. Every trick in computer
      architecture — a smarter compiler, a leaner instruction set, a faster
      clock, a pipeline — is an attempt to shrink one of these three factors
      without inflating the others.

Here is COD's central formula:

$$\text{CPU time} = \text{Instructions} \times \text{CPI} \times \text{Clock cycle time}$$

Read aloud: *the time on the CPU is the number of instructions executed, times
the average cycles each one takes, times the length of one cycle.* The three
factors, and what moves each:

| Symbol | Name | Plain meaning | Set mostly by |
| --- | --- | --- | --- |
| Instructions | instruction count | how many machine instructions actually run | the program, compiler, and instruction set |
| CPI | cycles per instruction | average clock cycles one instruction costs | the CPU design (pipeline, caches) and instruction mix |
| Clock cycle time | seconds per cycle | how long one tick lasts (= 1 / clock rate) | the silicon and clock rate |

The trap the clock-speed number falls into is now obvious: it is only
*one over the third factor*. A design can win on clock rate and still lose the
race by inflating the other two. The classic COD trade-off is a design that
uses **fewer instructions but a higher CPI** against one that uses **more
instructions but a lower CPI**. Let's settle it with numbers instead of loyalty:

```python
# Compare two CPU designs on the SAME program with the CPU performance equation:
#   CPU time = Instructions x CPI x Clock cycle time
# Design A ("complex"): fewer instructions, but each costs more cycles.
# Design B ("simple"):  more instructions, but each costs fewer cycles.
# Both run at the same 2 GHz clock, so we isolate the count-vs-CPI trade.

clock_hz = 2e9                 # 2 GHz
cycle_time = 1 / clock_hz      # seconds per cycle = 0.5 ns

def cpu_time(instructions, cpi):
    return instructions * cpi * cycle_time

designs = {
    "A (fewer instrs, high CPI)": dict(instructions=2.0e9, cpi=2.0),
    "B (more instrs,  low CPI)":  dict(instructions=2.5e9, cpi=1.2),
}

for name, d in designs.items():
    t = cpu_time(d["instructions"], d["cpi"])
    print(f"{name:<28}  {d['instructions']/1e9:.1f}B instrs x "
          f"CPI {d['cpi']:.1f}  ->  {t:.2f} s")

t_a = cpu_time(2.0e9, 2.0)
t_b = cpu_time(2.5e9, 1.2)
winner = "B" if t_b < t_a else "A"
print(f"\nDesign {winner} wins: it is {t_a / t_b:.2f}x faster "
      f"despite running 25% MORE instructions.")
```

Design A runs **2.00 s** and Design B runs **1.50 s**: B finishes first and is
about **1.33× faster** — even though it executes 25% *more* instructions. The
lower CPI more than paid for the extra instructions, at the same clock. This is
the lesson COD drills first: **you cannot judge speed from any single factor.**
Instruction count, CPI, and cycle time only mean something multiplied together.
(This is also why the RISC philosophy from
[0.4](../ch00-machine/04-machine-instructions.md) — simpler instructions, more
of them — can beat a "richer" instruction set: it trades count for a lower CPI
and a faster clock.)

## CPI and instruction mix

!!! abstract "In plain words"

    - **What it is.** A program is a *mix* of instruction kinds — loads, stores,
      arithmetic, branches — and each kind costs a different number of cycles.
      The program's CPI is the **weighted average** of those costs.
    - **Picture it.** A shopping bill: some items are cheap, some dear. The
      average cost per item is not the middle price — it is weighted by how many
      of each you actually bought.
    - **Why it matters.** It tells you *where the cycles go*. If loads are 20% of
      your instructions but eat 45% of the cycles, speeding up loads is where the
      win is — the seed of Amdahl's law, next.

CPI in the equation above is not a fixed property of the chip; it depends on
*what the program does*. Give each instruction class its own cycle cost and its
frequency in the program, and the overall CPI is the frequency-weighted average
— exactly a dot product:

```python
import numpy as np

# An instruction mix: fraction of all instructions, and cycles each kind costs.
# (Order-of-magnitude teaching numbers in the spirit of COD, not one chip.)
kinds  = ["ALU",  "Load", "Store", "Branch"]
freq   = np.array([0.50,  0.20,   0.10,    0.20])   # must sum to 1.0
cpi_of = np.array([1.0,   5.0,    3.0,     2.0])     # cycles per instruction

assert np.isclose(freq.sum(), 1.0)                   # frequencies are a mix

avg_cpi = float(freq @ cpi_of)                        # weighted average = dot product
print("instruction mix and per-class cost:")
for k, f, c in zip(kinds, freq, cpi_of):
    print(f"  {k:<7} freq {f:>4.0%}   CPI {c:>3.0f}   contributes {f*c:.2f} cycles")
print(f"\noverall CPI = {avg_cpi:.2f} cycles/instruction")

# Where do the cycles actually go? Loads are the story.
load_share = (freq[1] * cpi_of[1]) / avg_cpi
print(f"loads are {freq[1]:.0%} of instructions but "
      f"{load_share:.0%} of all cycles")
```

The weighted CPI comes out to **2.20 cycles per instruction**. The striking line
is the last one: loads are only **20%** of the instructions but consume
**45%** of the cycles, because each load costs five cycles while an ALU op costs
one. That imbalance is a signpost. If you wanted this program to run faster, you
would not shave the cheap, common ALU ops — you would attack the expensive
loads, because that is where the time hides. Which is precisely the law we turn
to now.

## Amdahl's law

!!! abstract "In plain words"

    - **What it is.** If you speed up only *part* of a program, the overall
      speed-up is capped by the part you *didn't* touch — no matter how much
      you accelerate the rest.
    - **Picture it.** A commute that is 1 hour of driving plus a fixed 20-minute
      walk from the car park. Buy a car that teleports (driving → 0) and the
      trip still takes 20 minutes. The walk you didn't fix sets the floor.
    - **Why it matters.** It is the mathematics of "make the common case fast"
      — and the honest brake on every optimization, from a hot loop to buying
      more CPU cores (which we do in [23.5.6](06-parallelism.md)).

Amdahl's law puts a number on that ceiling. Let $p$ be the fraction of the work
you can speed up, and $s$ the factor you speed *that part* up by:

$$\text{speedup} = \frac{1}{(1 - p) + \dfrac{p}{s}}$$

Read aloud: *the un-accelerated fraction $(1-p)$ stays exactly as slow as
before; only the fraction $p$ shrinks, to $p/s$. The total time is the sum, and
speed-up is one over it.* The trap is the $(1-p)$ term — it never shrinks, so as
$s \to \infty$ the best you can ever reach is $1/(1-p)$. Let's watch the
diminishing returns:

```python
import numpy as np
import matplotlib.pyplot as plt

def amdahl(p, s):
    """Overall speedup when a fraction p is accelerated by factor s."""
    return 1.0 / ((1 - p) + p / s)

# Say 95% of a program can be accelerated; 5% is stuck (I/O, setup, serial glue).
p = 0.95
print(f"accelerating the {p:.0%} that we can, by factor s:")
for s in [2, 4, 10, 100]:
    print(f"  s = {s:>3}x   ->   overall speedup = {amdahl(p, s):5.2f}x")
cap = 1 / (1 - p)
print(f"  s -> infinity ->   overall speedup ->  {cap:.2f}x   (the hard ceiling)")

# The curve: speedup vs how hard we accelerate the fast part, for several p.
s_axis = np.linspace(1, 100, 400)
plt.figure(figsize=(7, 4.5))
for p_val in [0.50, 0.90, 0.95, 0.99]:
    plt.plot(s_axis, amdahl(p_val, s_axis), label=f"p = {p_val:.2f}")
    plt.axhline(1 / (1 - p_val), color="gray", ls=":", lw=0.8)
plt.xlabel("speed-up of the accelerated part (s)")
plt.ylabel("overall program speed-up")
plt.title("Amdahl's law: the un-accelerated part sets the ceiling")
plt.legend(title="fraction sped up")
plt.grid(True, alpha=0.3)
```

The printed table is the whole moral. With **95%** of the program accelerable,
a **2×** boost on the hot part yields **1.90×** overall; a **10×** boost yields
**6.90×**; a **100×** boost yields only **16.81×** — and no matter how large $s$
grows, you can never beat **20.00×**, the $1/(1-0.95)$ ceiling. The curves flatten
into their dotted asymptotes: past a point, pouring effort into the fast part
buys almost nothing, because the untouched 5% now dominates. The punchline COD
repeats everywhere: **make the common case fast** — and know that the part you
*didn't* speed up quietly caps the whole thing.

## Benchmarks: why one number lies

!!! abstract "In plain words"

    - **What it is.** A **benchmark** is a fixed set of programs run on each
      machine so their times can be compared apples-to-apples. Suites like SPEC
      CPU bundle many real workloads and report a summary.
    - **Picture it.** Judging chefs by a whole tasting menu, not a single dish —
      one great dessert shouldn't crown a chef who burns everything else.
    - **Why it matters.** Any *single* score hides the shape of performance. The
      same chip can be a champion on one workload and mediocre on another.

Cautions, all of them things COD stresses and none requiring a made-up number:

- **A workload is not *your* workload.** A chip tuned for the benchmark mix may
  lag on your actual program, whose instruction mix and locality differ.
- **Summaries hide variance.** A single "SPEC score" is an average over many
  programs; averaging can bury a workload where the chip is terrible.
- **How you average matters.** Ratios of speeds should be summarized with a
  **geometric mean**, not an arithmetic one — the wrong mean can flip the
  ranking of two machines.
- **Clock rate and core count are not scores.** They are inputs to the
  performance equation, not the finish time. Only measured time on a real
  workload settles it.
- **Beware numbers with no workload attached.** "3× faster" is meaningless
  until you know *at what*, *versus what*, and *measured how*.

We deliberately quote **no** benchmark scores here: real ones are specific to a
chip, a compiler, and a date, and stating them as timeless facts is exactly the
mistake this section warns against. The tool you *can* trust is the one from
[16.2](../ch16-complexity/02-timing.md) — measure your own code on your own
inputs.

## The power wall → why one core became many

!!! abstract "In plain words"

    - **What it is.** For decades, clock speed climbed every year. Around 2004
      it stopped — not because faster transistors were impossible, but because
      the *heat* became unmanageable. That ceiling is the **power wall**.
    - **Picture it.** Revving an engine: a little faster is fine, but past a
      point the extra speed produces far more heat than motion, and it melts.
    - **Why it matters.** Unable to make one core much faster, the industry made
      *many* cores instead. Every "quad-core" and "GPU" is a direct consequence
      — and the reason [23.5.6](06-parallelism.md) exists.

The physics in one line — the **dynamic power** a chip burns while switching:

$$P \approx C \times V^2 \times f$$

Read aloud: *power grows with the capacitance being switched ($C$), the square
of the voltage ($V$), and the clock frequency ($f$).* For years, **Dennard
scaling** meant that as transistors shrank, voltage $V$ dropped too — so
frequency $f$ could rise while power stayed flat. Around 2004 that broke:
voltage could no longer fall (leakage set a floor), so cranking $f$ now drove
power straight up. Worse, switching faster needs a higher voltage, so in the
clock-chasing regime voltage rises *with* frequency — and $V^2 f$ turns roughly
into $f^3$. Let's see how brutal that is, and why more cores beat a faster core:

```python
# Dynamic power ~ C * V^2 * f. Once Dennard scaling ended, pushing the clock up
# also needs more voltage (roughly V grows with f), so power ~ f^3 in the
# clock-chasing regime. Compare two ways to double throughput.
def rel_power_one_core(f):
    # normalized so f = 1 -> power 1; V grows ~ with f, so V^2 * f ~ f^3
    return f ** 3

print("Making ONE core faster (voltage must rise with clock):")
for f in [1.0, 1.5, 2.0]:
    print(f"  clock {f:.1f}x  ->  throughput {f:.1f}x   power {rel_power_one_core(f):.2f}x")

# Doubling throughput two ways:
one_fast = rel_power_one_core(2.0)     # one core at 2x clock
two_cores = 2 * rel_power_one_core(1.0)  # two cores at 1x clock (ideal parallel)
print(f"\nsame 2x throughput, two ways:")
print(f"  one core at 2x clock : power {one_fast:.0f}x")
print(f"  two cores at 1x clock: power {two_cores:.0f}x")
print(f"  -> multicore delivers 2x work at {one_fast/two_cores:.0f}x LESS power")
```

The numbers are stark: doubling a single core's clock costs about **8×** the
power (the $f^3$ blow-up), while two cores at the original clock deliver the same
**2×** throughput for only **2×** the power — **4× more efficient**. That is the
causal chain, start to finish:

1. Transistors kept shrinking, but **Dennard scaling ended** (~2004): voltage
   stopped dropping.
2. So raising the clock now **raised power steeply** ($\sim f^3$) → heat you
   cannot remove → the **power wall**.
3. One core could not get much faster, but chips could hold **more cores**.
4. So performance growth moved from "faster core" to "**more cores**" — and the
   burden shifted onto *software* to use them.

That last shift is the whole subject of [23.5.6](06-parallelism.md): the free
lunch of a rising clock is over, and speed now comes from doing many things at
once — which, as Amdahl warned above, is far harder than it sounds.

!!! warning "Common mistakes"

    - **Judging a CPU by gigahertz alone.** Clock rate is only *one over the
      cycle time* — one of three factors. A higher-clocked chip loses whenever
      its instruction count or CPI is worse. Compare *time on a real workload*.
    - **Treating CPI as a fixed chip spec.** CPI is a weighted average over the
      program's instruction mix; the *same* chip has different CPI on different
      code. Change the mix (or the cache behaviour) and CPI moves.
    - **Optimizing the rare case.** Amdahl's law says effort spent on code that
      is a small fraction of the runtime is nearly wasted. Profile first; speed
      up the part that actually dominates.
    - **Believing a benchmark score is "the speed."** It is a summary of one
      workload under one compiler on one day. Your program may stress the chip
      completely differently.

## Check your understanding

1. Chip X runs at 4 GHz; chip Y runs at 3 GHz. On the same program, X executes
   3.0 billion instructions at CPI 2.0, and Y executes 2.0 billion at CPI 1.0.
   Which finishes first?

    ??? success "Answer"
        Use $\text{CPU time} = \text{Instructions} \times \text{CPI} \times
        \text{cycle time}$, with cycle time = 1 / clock.

        ```python
        def cpu_time(instrs, cpi, clock_hz):
            return instrs * cpi * (1 / clock_hz)
        x = cpu_time(3.0e9, 2.0, 4e9)   # higher clock...
        y = cpu_time(2.0e9, 1.0, 3e9)
        print(f"X: {x:.3f} s,  Y: {y:.3f} s  -> Y is {x/y:.2f}x faster")
        ```

        X takes 1.5 s, Y takes ~0.667 s: **Y wins, ~2.25× faster**, despite its
        lower clock rate. Fewer instructions and a lower CPI beat the faster
        clock — the whole point of the performance equation.

2. A program spends 80% of its time in a function you can make 5× faster. What
   is the overall speed-up, and what is the best you could *ever* get by
   optimizing only that function?

    ??? success "Answer"
        Amdahl's law with $p = 0.80$, $s = 5$: speedup $= 1/((1-0.8) + 0.8/5)
        = 1/(0.2 + 0.16) = 1/0.36 \approx 2.78×$. The ceiling as $s \to \infty$
        is $1/(1-0.8) = 5×$ — the untouched 20% caps you at 5× no matter how
        fast the function becomes.

3. Loads are 15% of a program's instructions but each costs 6 cycles, while
   the other 85% cost 1 cycle each. What is the overall CPI, and what share of
   cycles do loads consume?

    ??? success "Answer"
        CPI $= 0.15 \times 6 + 0.85 \times 1 = 0.90 + 0.85 = 1.75$. Loads
        contribute $0.90$ of those $1.75$ cycles — about **51%** — while being
        only 15% of the instructions. That imbalance is exactly why loads (and
        the [memory hierarchy](../ch23-os/04-memory-hierarchy.md) behind them)
        are worth optimizing.

4. Why did CPUs stop getting much faster per core around 2004, and what did the
   industry do instead?

    ??? success "Answer"
        Dynamic power is roughly $C V^2 f$. **Dennard scaling** — which let
        voltage fall as transistors shrank — ended, so raising the clock $f$
        (and the voltage it needs) made power climb steeply and generate more
        heat than could be removed: the **power wall**. Unable to speed up one
        core much further, designers put *more cores* on the chip, pushing the
        job of using them onto software — the subject of
        [23.5.6](06-parallelism.md).

!!! info "Where to go deeper — Patterson & Hennessy"

    Every idea here is Chapter 1 of **Patterson & Hennessy, *Computer
    Organization and Design* (RISC-V edition)**: the CPU performance equation,
    CPI and instruction mix, Amdahl's law, the SPEC benchmark methodology (and
    why the geometric mean), and the power wall that ended clock scaling. COD
    develops each with full derivations and real measured data; this section is
    its runnable on-ramp. Next: [the instruction set up close](02-instruction-set.md).
