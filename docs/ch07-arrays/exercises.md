# Exercises

Work through these in order — they start with reading indexes and end
with a genuinely tricky one-pass search. Try each one before opening the
solution, and for Exercise 7.1 commit to your prediction *in writing*
before you press Run.

### Exercise 7.1 — Predict the print (●)

Without running it, write down exactly what this program prints — four
lines. Then run it and check.

```python
pets = ["cat", "dog", "fox", "owl"]
print(pets[1])
print(pets[-1])
print(len(pets))
print(pets[len(pets) - 2])
```

??? success "Solution"

    ```python
    pets = ["cat", "dog", "fox", "owl"]
    print(pets[1])               # dog  (index 1 = SECOND element)
    print(pets[-1])              # owl  (last)
    print(len(pets))             # 4
    print(pets[len(pets) - 2])   # fox  (index 4 - 2 = 2)
    ```

    The output is `dog`, `owl`, `4`, `fox`. The two classic stumbles:
    index 1 is the second element, not the first, and `len(pets) - 2`
    evaluates to the plain index 2.

### Exercise 7.2 — First, last, and middle (●)

Given any non-empty list, print its first element, its last element (two
different ways), and its length. Test with `[10, 20, 30, 40, 50]`.

??? success "Solution"

    ```python
    values = [10, 20, 30, 40, 50]
    print("first :", values[0])
    print("last  :", values[len(values) - 1])   # the universal way
    print("last  :", values[-1])                # the Python shortcut
    print("length:", len(values))
    ```

    Both "last" lines print `50`: `values[-k]` is exactly
    `values[len(values) - k]`. Only the `values[0]` / `len - 1` forms
    translate to Java.

### Exercise 7.3 — Above average (●)

Compute the average of `[70, 85, 90, 65, 100]`, then count how many
scores are strictly above it. Print both.

??? success "Solution"

    ```python
    scores = [70, 85, 90, 65, 100]

    average = sum(scores) / len(scores)

    above = 0
    for score in scores:
        if score > average:
            above += 1

    print("average:", average)
    print("above  :", above)
    ```

    This prints `average: 82.0` and `above: 3` (85, 90, and 100). Two
    passes are required: you cannot know the average until one full
    traversal has finished, so the counting loop must come second.

### Exercise 7.4 — Every index of a value (●●)

Find *all* the indexes where a target appears. For
`values = [4, 7, 4, 9, 4]` and target `4`, build and print the list
`[0, 2, 4]`. What does your code produce when the target is absent?

??? success "Solution"

    ```python
    values = [4, 7, 4, 9, 4]
    target = 4

    hits = []
    for i in range(len(values)):
        if values[i] == target:
            hits.append(i)

    print(hits)   # [0, 2, 4]
    ```

    This combines the indexed visit (we need positions, so for-each
    won't do) with the transform pattern (build a new list). An absent
    target yields `[]` — an empty list is a perfectly good answer for
    "no hits", and nicer to work with than a special value like `-1`.

### Exercise 7.5 — Range in one pass (●●)

The *range* of a data set is `max - min`. Compute it for
`[7, 3, 9, 2, 8]` **without** calling `max()` or `min()`, and using only
**one** loop that tracks both champions at once.

??? success "Solution"

    ```python
    data = [7, 3, 9, 2, 8]

    biggest = data[0]
    smallest = data[0]
    for value in data[1:]:
        if value > biggest:
            biggest = value
        if value < smallest:
            smallest = value

    print("max  :", biggest)
    print("min  :", smallest)
    print("range:", biggest - smallest)
    ```

    Output: `max: 9`, `min: 2`, `range: 7`. Two running champions ride
    the same loop; note both are initialised to `data[0]`, never to 0 —
    a min initialised to 0 would "win" against any all-positive list.

### Exercise 7.6 — Cheapest item (●●)

Parallel lists: `items = ["tea", "coffee", "juice"]` and
`prices = [1.20, 2.50, 1.80]`. Print the *name* of the cheapest item and
its price formatted to two decimals, like `tea costs $1.20`.

??? success "Solution"

    ```python
    items  = ["tea", "coffee", "juice"]
    prices = [1.20, 2.50, 1.80]

    cheap_i = 0
    for i in range(1, len(prices)):
        if prices[i] < prices[cheap_i]:
            cheap_i = i

    print(f"{items[cheap_i]} costs ${prices[cheap_i]:.2f}")
    ```

    This prints `tea costs $1.20`. The search happens entirely in
    `prices`, but because the lists are parallel, the winning *index*
    unlocks the matching name in `items`. Searching for the best value
    directly (pattern 3 without the index) would leave you unable to
    name the item.

### Exercise 7.7 — Reversed copy, by hand (●●)

Build a **new** list containing the elements of `[1, 2, 3, 4]` in
reverse order, without using `reversed()`, slicing, or `.reverse()`.
Print both lists to show the original is untouched.

??? success "Solution"

    ```python
    data = [1, 2, 3, 4]

    backwards = []
    for i in range(len(data) - 1, -1, -1):   # last index down to 0
        backwards.append(data[i])

    print("reversed:", backwards)
    print("original:", data)
    ```

    Output: `reversed: [4, 3, 2, 1]` and `original: [1, 2, 3, 4]`.
    `range(len(data) - 1, -1, -1)` reads: start at the last index,
    stop *before* $-1$ (i.e. include 0), step backwards by 1. Off-by-one
    errors love this exercise — check that both endpoints appear.

### Exercise 7.8 — Second largest, one pass (●●●)

Find the second-largest value in `[31, 7, 42, 18, 40]` using a single
loop and no sorting. Hint: keep *two* champions, and think carefully
about what happens when a new value dethrones the leader.

??? success "Solution"

    ```python
    data = [31, 7, 42, 18, 40]

    if data[0] > data[1]:
        best, second = data[0], data[1]
    else:
        best, second = data[1], data[0]

    for value in data[2:]:
        if value > best:
            second = best      # the old champion is demoted...
            best = value       # ...and the newcomer takes the crown
        elif value > second:
            second = value     # beats second place only

    print("largest       :", best)
    print("second largest:", second)
    ```

    Output: `largest: 42`, `second largest: 40`. The subtle line is
    `second = best` *before* `best = value`: when a new maximum arrives,
    the dethroned champion is exactly the new runner-up. Writing the two
    assignments in the other order loses it. Trace it on the list to
    convince yourself: after 42 arrives, `second` is 31; then 40 beats
    31 without beating 42.
