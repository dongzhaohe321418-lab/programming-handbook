# Project 4 · Sorting Visualizer

Big-O tells you *that* quicksort beats selection sort; this project makes
you watch it happen. You will instrument four sorting algorithms so every
comparison and move is counted, then photograph a sort mid-flight as a
gallery of bar charts.

## What you'll build

Two artifacts. First, a hard-numbers table — the same 500 values sorted
by four algorithms on three kinds of input:

```text
n = 500 — comparisons / moves per algorithm and input

algorithm             random            sorted          reversed
----------------------------------------------------------------
selection    124750/984        124750/0          124750/500
insertion     60756/60765         499/499        124750/125249
merge          3844/4488         2216/4488         2272/4488
quick          5858/2376         4008/510          4014/1008
```

Second, a six-panel figure showing selection sort's sorted prefix growing
across one run — algorithm progress as pictures, not prose.

## What it exercises

- [22.1 Elementary sorts](../../ch22-sorting/01-elementary-sorts.md) and
  [22.2 Merge sort and quicksort](../../ch22-sorting/02-merge-quick.md) —
  the four algorithms being instrumented.
- [16.1 Big-O notation](../../ch16-complexity/01-big-o.md) and
  [16.2 Measuring running time](../../ch16-complexity/02-timing.md) —
  counting operations is measurement without a stopwatch's noise.
- [Chapter 12 · Writing Your Own Classes](../../ch12-classes/index.md) —
  the `Tally` counter object threaded through every sort.
- [8.3 First algorithms](../../ch08-grids/03-first-algorithms.md) — where
  you first met selection sort; now you weigh it.

## Milestones

### Milestone 1 — the Tally class and one instrumented sort

**Goal:** write `Tally` with `comparisons` and `moves` counters and a
`less(a, b)` method that counts, then route *every* comparison in
selection sort through it (and count 2 moves per swap).

**Done when...** sorting any 500-element input reports exactly
$n(n-1)/2 = 124750$ comparisons — selection sort's signature — and the
output equals Python's `sorted()` on the same data.

??? tip "Hint"

    The discipline that makes counts trustworthy: the sort never writes
    `a < b` directly, only `tally.less(a, b)`. One counter object, passed
    in, mutated as it goes:

    ```python
    class Tally:
        def __init__(self):
            self.comparisons = 0

        def less(self, a, b):
            self.comparisons += 1
            return a < b

    t = Tally()
    print(t.less(3, 5), t.less(5, 3), "->", t.comparisons, "comparisons")
    ```

    Sort a *copy* (`a = list(data)`) so every algorithm gets identical,
    untouched input.

### Milestone 2 — instrument all four algorithms

**Goal:** add insertion sort (count each shift as a move), merge sort
(count each element placed into a merged list), and quicksort with a
**middle-element pivot**, all using the same `Tally` interface.

**Done when...** all four return exactly `sorted(data)` for random,
sorted, *and* reversed inputs — verified by an `assert` — and quicksort
on already-sorted input stays in the thousands of comparisons instead of
exploding to 124,750.

??? tip "Hint"

    The pivot choice is the whole ballgame: `a[lo]` as pivot degrades to
    $O(n^2)$ — and blows the recursion limit — on *sorted* input, the very
    case users feed you most. `a[(lo + hi) // 2]` sidesteps it. Test the
    ugly inputs first; random input forgives bugs that sorted and
    reversed input expose, like a merge that drops leftovers or an
    insertion shift that goes one slot too far.

### Milestone 3 — the comparison table

**Goal:** generate seeded random / sorted / reversed inputs at `n = 500`,
run every algorithm on every input, and print an aligned
`comparisons/moves` table plus a short "reading the table" summary.

**Done when...** your table matches the one at the top of this page
(same seed, same numbers): selection is identical down all three columns,
insertion collapses to `499/499` on sorted input, and merge/quick stay
within a small factor of $n \log_2 n \approx 4483$ in every column.

??? tip "Hint"

    Build each row as formatted cells, and keep the input kinds in one
    dictionary so the header and the cells can't drift apart:

    ```python
    inputs = {"random": [3, 1, 2], "sorted": [1, 2, 3]}
    header = f"{'algorithm':<10}" + "".join(f"{k:>12}" for k in inputs)
    print(header)
    print(f"{'demo':<10}" + "".join(f"{'9/9':>12}" for k in inputs))
    ```

    Seed once (`random.seed(20)`) *before* generating the shuffled input,
    and derive sorted/reversed from that same list — three personalities,
    identical values.

### Milestone 4 — record snapshots of a sort in progress

**Goal:** write `selection_sort_with_snapshots(data)` that appends a
`(passes_completed, copy_of_list)` pair to a history list after every
pass, then pick 6 evenly spaced snapshots including the start and the
finish.

**Done when...** for `n = 60` the history holds 60 entries (start plus 59
passes), the last snapshot is fully sorted, and your six chosen indices
are `[0, 12, 24, 35, 47, 59]`.

??? tip "Hint"

    Store `list(a)` — a *copy* — not `a` itself, or every snapshot will
    point at the same finished list (the aliasing trap from
    [9.1 Values vs references](../../ch09-collections/01-references.md)).
    Even spacing over any history length is one formula:

    ```python
    length = 60
    picks = [round(k * (length - 1) / 5) for k in range(6)]
    print(picks)
    ```

### Milestone 5 — the six-panel figure

**Goal:** draw the six snapshots as bar charts in a $2 \times 3$ grid, coloring
the settled prefix differently from the unsorted rest, with a title per
panel saying how many passes have run.

**Done when...** the figure reads left-to-right, top-to-bottom as a story:
noise in panel one, a growing teal staircase, a complete staircase in
panel six — and axes are labeled.

??? tip "Hint"

    One subplot grid, one loop; `axes.flat` walks the $2 \times 3$ grid in
    reading order, and `bar` accepts one color per bar:

    ```python
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(2, 3, figsize=(11, 6), sharey=True)
    for panel, ax in enumerate(axes.flat):
        heights = [1, 3, 2, 5, 4]
        colors = ["#00897b" if i <= panel else "#b0bec5"
                  for i in range(len(heights))]
        ax.bar(range(len(heights)), heights, color=colors, width=1.0)
        ax.set_title(f"panel {panel}")
        ax.set_xlabel("index")
    fig.tight_layout()
    ```

    After `passes` passes of selection sort, the first `passes` slots are
    final — and after the last pass, the final slot is automatically in
    place too.

!!! note "Why snapshots instead of animation?"

    Locally, matplotlib's `FuncAnimation` plays a sort as a movie — but the
    in-browser runner captures **one finished figure**, so an animation
    would collapse into its last frame. Snapshots tell the same story in
    print. On your own machine, the animated version is a small change:

    ```text
    # Local-only variant (desktop Python, not this page):
    import matplotlib.animation as animation

    fig, ax = plt.subplots()
    bars = ax.bar(range(n), history[0][1], color="#b0bec5", width=1.0)

    def update(frame):
        passes, snapshot = history[frame]
        for bar, height in zip(bars, snapshot):
            bar.set_height(height)
        ax.set_title(f"after pass {passes}")
        return bars

    anim = animation.FuncAnimation(fig, update,
                                   frames=len(history), interval=50)
    plt.show()
    ```

## Reference implementation

Two runnable blocks: the counting laboratory, then the snapshot gallery.
Each stands alone.

??? success "Full reference implementation"

    **Part 1 — instrumented sorts and the counting table.**

    ```python
    """Instrumented sorting: count exactly what each algorithm does."""
    import math
    import random


    class Tally:
        """Counts comparisons and element moves for one sorting run."""

        def __init__(self):
            self.comparisons = 0
            self.moves = 0

        def less(self, a, b):
            """Every 'is a < b?' question in a sort goes through here."""
            self.comparisons += 1
            return a < b


    def selection_sort(data, tally):
        """Repeatedly select the smallest remaining value; O(n^2) compares."""
        a = list(data)
        n = len(a)
        for i in range(n - 1):
            smallest = i
            for j in range(i + 1, n):
                if tally.less(a[j], a[smallest]):
                    smallest = j
            if smallest != i:
                a[i], a[smallest] = a[smallest], a[i]
                tally.moves += 2
        return a


    def insertion_sort(data, tally):
        """Slide each value left to its place; fast on nearly-sorted input."""
        a = list(data)
        for i in range(1, len(a)):
            value = a[i]
            j = i
            while j > 0 and tally.less(value, a[j - 1]):
                a[j] = a[j - 1]           # shift the bigger value right
                tally.moves += 1
                j -= 1
            a[j] = value
            tally.moves += 1
        return a


    def merge_sort(data, tally):
        """Split in half, sort halves, merge; O(n log n) always."""
        a = list(data)
        if len(a) <= 1:
            return a
        mid = len(a) // 2
        left = merge_sort(a[:mid], tally)
        right = merge_sort(a[mid:], tally)
        merged = []
        i = j = 0
        while i < len(left) and j < len(right):
            if tally.less(right[j], left[i]):
                merged.append(right[j])
                j += 1
            else:
                merged.append(left[i])
                i += 1
            tally.moves += 1
        for leftover in (left[i:], right[j:]):
            merged.extend(leftover)
            tally.moves += len(leftover)
        return merged


    def quick_sort(data, tally):
        """Partition around a middle pivot; O(n log n) on average."""
        a = list(data)
        _quick(a, 0, len(a) - 1, tally)
        return a


    def _quick(a, lo, hi, tally):
        if lo >= hi:
            return
        pivot = a[(lo + hi) // 2]         # middle pivot: safe on sorted input
        i, j = lo, hi
        while i <= j:
            while tally.less(a[i], pivot):
                i += 1
            while tally.less(pivot, a[j]):
                j -= 1
            if i <= j:
                a[i], a[j] = a[j], a[i]
                tally.moves += 2
                i += 1
                j -= 1
        _quick(a, lo, j, tally)
        _quick(a, i, hi, tally)


    ALGORITHMS = [
        ("selection", selection_sort),
        ("insertion", insertion_sort),
        ("merge", merge_sort),
        ("quick", quick_sort),
    ]


    def make_inputs(n):
        """Three personalities of input, same values in each."""
        random.seed(20)
        shuffled = random.sample(range(n), n)
        return {"random": shuffled, "sorted": sorted(shuffled),
                "reversed": sorted(shuffled, reverse=True)}


    def main():
        n = 500
        inputs = make_inputs(n)
        expected = sorted(inputs["random"])

        print(f"n = {n} — comparisons / moves per algorithm and input\n")
        header = f"{'algorithm':<10}" + "".join(f"{kind:>18}" for kind in inputs)
        print(header)
        print("-" * len(header))
        for name, sort in ALGORITHMS:
            cells = []
            for kind, data in inputs.items():
                tally = Tally()
                result = sort(data, tally)
                assert result == expected, f"{name} failed to sort {kind}!"
                cells.append(f"{tally.comparisons:>9}/{tally.moves:<8}")
            print(f"{name:<10}" + "".join(f"{c:>18}" for c in cells))

        n_squared = n * (n - 1) // 2
        n_log_n = round(n * math.log2(n))
        print("\nReading the table:")
        print(f" * selection never notices the input: always n(n-1)/2 = "
              f"{n_squared} comparisons")
        print(f" * insertion drops to n-1 = {n - 1} comparisons on sorted input,"
              " worst on reversed")
        print(f" * merge and quick stay within a small factor of n*log2(n) ~="
              f" {n_log_n} everywhere — never {n_squared}")


    main()
    ```

    **Part 2 — the snapshot gallery** (self-contained; re-run it after
    changing the seed or `n`).

    ```python
    """Watch selection sort work: six snapshots of one list being sorted."""
    import random
    import matplotlib.pyplot as plt


    def selection_sort_with_snapshots(data):
        """Sort a copy of `data`, recording the list after every pass."""
        a = list(data)
        history = [(0, list(a))]          # (passes completed, list state)
        n = len(a)
        for i in range(n - 1):
            smallest = i
            for j in range(i + 1, n):
                if a[j] < a[smallest]:
                    smallest = j
            a[i], a[smallest] = a[smallest], a[i]
            history.append((i + 1, list(a)))
        return history


    random.seed(11)
    n = 60
    values = random.sample(range(1, n + 1), n)
    history = selection_sort_with_snapshots(values)

    # Six evenly spaced snapshots, always including start and finish.
    picks = [round(k * (len(history) - 1) / 5) for k in range(6)]

    fig, axes = plt.subplots(2, 3, figsize=(11, 6), sharey=True)
    for ax, index in zip(axes.flat, picks):
        passes, snapshot = history[index]
        # After `passes` passes the first `passes` slots are final — and
        # after the last pass (n - 1) the final slot is in place too.
        done = passes == n - 1
        settled = n if done else passes
        colors = ["#00897b" if pos < settled else "#b0bec5"
                  for pos in range(n)]
        ax.bar(range(n), snapshot, color=colors, width=1.0)
        ax.set_title(f"after pass {passes}" + (" — sorted" if done else ""))
        ax.set_xlabel("index")
    for row in axes:
        row[0].set_ylabel("value")
    fig.suptitle("Selection sort: the sorted prefix (teal) grows from the left")
    fig.tight_layout()
    ```

## Going further

- **Add heapsort.** Bring in the sift-down heapsort from
  [21.2 Priority queues and heapsort](../../ch21-heaps/02-priority-queues.md),
  route its comparisons through `Tally`, and add a fifth row to the table.
  Prediction before you run it: closer to merge's counts, or quick's?
- **Race chart with log-log slopes.** Run each algorithm at
  $n = 125, 250, 500, 1000, 2000$ (random input only), then
  `plt.loglog(ns, comparisons, marker="o")` per algorithm. On log-log
  axes, $O(n^2)$ algorithms plot as lines of slope 2 and
  $O(n \log n)$ ones as slope just above 1 — you can *see* the exponent.
- **Snapshot other sorts.** Insertion sort photographs beautifully (a
  sorted region with one value sliding home). Merge sort needs care:
  snapshot the working array once per merge instead of per pass.
- **Count real work.** Add a `swaps` vs `shifts` distinction, or tally
  slice copying in merge sort — then argue about whether merge's hidden
  memory traffic is fairly represented by `moves`.
- **Nearly-sorted inputs.** Add a fourth input personality: sorted except
  for 10 random swaps. Watch insertion sort become the best algorithm in
  the table — and know why libraries build hybrids like Timsort on
  exactly that observation.
