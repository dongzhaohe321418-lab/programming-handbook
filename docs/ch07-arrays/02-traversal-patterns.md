# 7.2 Traversal patterns and parallel arrays

Once your data lives in a list, nearly everything you do with it is a
**traversal**: a loop that visits the elements one by one. The good news
is that after fifty years of programming, traversals boil down to a
handful of patterns that appear over and over — visit, accumulate, search
for the best, transform.

Learn these four as named recipes and most list problems become "which
pattern is this?" rather than a blank page. We finish with *parallel arrays*,
the classic technique of linking two lists by index.

## Pattern 1 — visit every element

The simplest traversal just touches each element in order. Python gives
you two ways to write it.

The **for-each loop** hands you each *value* directly:

```python
pets = ["cat", "dog", "fox"]
for pet in pets:
    print(pet)
```

```text
cat
dog
fox
```

The **indexed loop** counts through the *positions* and looks each one
up:

```python
pets = ["cat", "dog", "fox"]
for i in range(len(pets)):
    print(i, pets[i])
```

```text
0 cat
1 dog
2 fox
```

Which one should you use?

| Loop form | Reach for it when | Because |
| --- | --- | --- |
| **for-each** | you only need the values | it is shorter, and an off-by-one error is impossible |
| **indexed** | the *position* matters | numbered output, changing elements in place (`pets[i] = ...`), or reading two lists at once |

=== "Python"

    ```python
    scores = [83, 91, 78]

    for score in scores:          # for-each
        print(score)

    for i in range(len(scores)):  # indexed
        print(i, scores[i])
    ```

=== "Java"

    ```java
    int[] scores = {83, 91, 78};

    for (int score : scores) {              // "enhanced for"
        System.out.println(score);
    }

    for (int i = 0; i < scores.length; i++) {  // indexed
        System.out.println(i + " " + scores[i]);
    }
    ```

Java makes the same distinction: the *enhanced for* loop (`for (int
score : scores)`) is Java's for-each. Note the indexed condition
`i < scores.length` — using `<=` is the classic way to run one index too
far.

## Pattern 2 — accumulate

An **accumulator** is a variable that starts at a neutral value (usually
0) and is updated once per element. Totals, counts, and averages are all
accumulations. Here is the pattern by hand:

```python
scores = [83, 91, 78, 95, 88]

total = 0
count = 0
for score in scores:
    total += score
    count += 1

print("total  :", total)
print("count  :", count)
print("average:", total / count)
```

```text
total  : 435
count  : 5
average: 87.0
```

The shape to memorise has three steps:

1. **Initialise** the accumulator *before* the loop.
2. **Update** it *inside* the loop, once per element.
3. **Use** it *after* the loop has finished.

Putting `total = 0` inside the loop is the classic bug — it wipes the running
total on every pass.

For plain sums and counts, Python has built-ins that run the same loop
for you:

```python
scores = [83, 91, 78, 95, 88]
print(sum(scores) / len(scores))
```

This prints `87.0` again. Use the built-ins when they fit — but the
hand-written pattern is what you adapt when the built-ins *don't* fit,
such as counting only elements that pass a test:

```python
scores = [83, 91, 78, 95, 88]

honor_roll = 0
for score in scores:
    if score >= 90:
        honor_roll += 1

print(honor_roll, "scores of 90 or above")
```

This prints `2 scores of 90 or above` (the 91 and the 95). The
accumulator update is guarded by an `if` — same pattern, one extra line.

## Pattern 3 — search for the best

To find the largest (or smallest) element, run a competition: crown the
first element the **running champion**, then let every later element
challenge it.

```python
scores = [83, 91, 78, 95, 88]

best = scores[0]              # the first element starts as champion
for score in scores[1:]:      # every later element challenges
    if score > best:
        best = score

print("highest score:", best)
```

This prints `highest score: 95`. Trace the championship by hand:

| challenger | is it `> best`? | `best` afterwards |
|---|---|---|
| — (start) | — | 83 |
| 91 | yes | 91 |
| 78 | no | 91 |
| 95 | yes | 95 |
| 88 | no | 95 |

Two details deserve attention:

- **The champion starts as `scores[0]`, not 0.** Initialising to 0 silently
  fails on a list of negative numbers — nothing ever beats the champion.
- **The pattern assumes a non-empty list.** `scores[0]` on an empty list is
  an `IndexError`.

Often you need *where* the best lives, not just what it is. Track the
champion's **index** instead:

```python
scores = [83, 91, 78, 95, 88]

best_i = 0
for i in range(1, len(scores)):
    if scores[i] > scores[best_i]:
        best_i = i

print("highest score is", scores[best_i], "at index", best_i)
```

This prints `highest score is 95 at index 3`. Python's built-ins `max()`
and `min()` cover the plain cases — `max(scores)` is `95` — but the
index-tracking version is yours to adapt, and it is the heart of
selection sort in [Chapter 8](../ch08-grids/03-first-algorithms.md).

## Pattern 4 — transform into a new list

To apply the same change to every element, build a **new** list: start
empty, append one transformed value per element.

```python
prices = [4.00, 2.50, 10.00]

discounted = []
for price in prices:
    discounted.append(round(price * 0.9, 2))

print(discounted)
print(prices)          # the original is untouched
```

```text
[3.6, 2.25, 9.0]
[4.0, 2.5, 10.0]
```

The original `prices` survives unchanged — transformation into a new list
is the polite, low-surprise default. (Changing a list *in place* is
sometimes right too; Chapter 8 discusses
[when and how](../ch08-grids/02-arrays-functions.md).)

Python offers a one-line shorthand for exactly this pattern, the **list
comprehension**:

```python
prices = [4.00, 2.50, 10.00]
discounted = [round(price * 0.9, 2) for price in prices]
print(discounted)
```

Same output: `[3.6, 2.25, 9.0]`. Read it inside-out: "for each `price`
in `prices`, keep `round(price * 0.9, 2)`". Use it when the transform
fits comfortably on one line; use the loop form when it doesn't.

## Comparing two lists

Are two lists equal — same length, same values, same order? The manual
pattern walks both lists in step with one index:

```python
expected = [1, 2, 3, 4]
actual   = [1, 2, 7, 4]

if len(expected) != len(actual):
    print("different lengths")
else:
    all_match = True
    for i in range(len(expected)):
        if expected[i] != actual[i]:
            print(f"first difference at index {i}: "
                  f"{expected[i]} vs {actual[i]}")
            all_match = False
            break
    if all_match:
        print("lists are equal")
```

This prints `first difference at index 2: 3 vs 7`. The pattern is worth
knowing because it can *report* the difference — invaluable when testing
(Chapter 8.4). But when you only need yes-or-no, Python's `==` runs the
whole comparison for you:

```python
a = [1, 2, 3]
b = [1, 2, 3]
c = [1, 2, 4]
print(a == b)
print(a == c)
```

This prints `True` then `False` — `==` on lists compares element by
element, exactly like the loop above.

!!! info "Java corner"
    This is a genuine Python/Java difference. In Java, `a == b` on two
    arrays compares the **references** — it asks "are these the *same*
    array object?", not "do they hold equal values?" — so two separate
    arrays with identical contents give `false`. To compare contents you
    must call `java.util.Arrays.equals(a, b)`. Python's reference
    comparison is spelled `is`
    (see [equality vs identity](../ch04-branching/03-equality-identity.md)).

## Parallel arrays: two lists linked by index

Suppose a gradebook needs each student's *name* and *score*. One classic
technique is two lists kept **parallel**: index $i$ in `names` and index
$i$ in `scores` describe the same student.

```python
names  = ["Ava", "Ben", "Chloe", "Dev"]
scores = [88, 94, 79, 91]

# print the gradebook: the indexed loop reads BOTH lists at position i
for i in range(len(names)):
    print(f"{names[i]:<6} {scores[i]:>3}")

# who topped the class? find the best INDEX, then use it in both lists
best_i = 0
for i in range(1, len(scores)):
    if scores[i] > scores[best_i]:
        best_i = i

print(f"top of the class: {names[best_i]} with {scores[best_i]}")
```

```text
Ava     88
Ben     94
Chloe   79
Dev     91
top of the class: Ben with 94
```

Notice how the patterns combine: the search-for-best recipe finds
`best_i` in `scores`, and because the lists are parallel, the *same*
index retrieves the matching name. This is precisely why the
index-tracking version of pattern 3 earns its keep.

Parallel arrays work, and you will see them in real code — but they are
fragile. Nothing in the program *enforces* the link:

- **Sort `scores` without rearranging `names`** and every pairing is silently
  wrong.
- **Append to one list and forget the other** and the two drift out of step.

The robust fix is to bundle each name-score pair into a single object — a
`Student` with `.name` and `.score` — which is exactly what classes give
you in [Chapter 12](../ch12-classes/index.md). Until then, treat
parallel lists as one structure: every change happens to both, at the
same index.

!!! warning "Common mistakes"
    - **Off-by-one in indexed loops.** `range(len(xs))` is right;
      `range(len(xs) + 1)` (or Java's `i <= xs.length`) walks off the end
      and raises `IndexError`.
    - **Initialising `best = 0` instead of `best = xs[0]`.** On the list
      `[-8, -3, -5]` the champion 0 never loses, and the "maximum"
      reported is a value that isn't even in the list.
    - **Resetting the accumulator inside the loop.** `total = 0` placed
      inside the loop body makes every pass start over; the final total
      is just the last element.
    - **Updating one parallel list but not the other.** After
      `scores.sort()`, `names[i]` no longer belongs to `scores[i]`. Sort,
      append, and delete in *both* lists together — or use a class.

## Check your understanding

1. You need to print a numbered menu: `1. tea`, `2. coffee`, … Which loop
   form do you need, and why?

    ??? success "Answer"
        The indexed form — the printed number is the position, which the
        for-each loop never sees. `for i in range(len(menu)):` then print
        `f"{i + 1}. {menu[i]}"` (adding 1 for human-friendly counting).

2. Without running it, what does this print?

    ```text
    values = [4, -2, 9, 1]
    total = 0
    for v in values:
        if v > 0:
            total += v
    print(total)
    ```

    ??? success "Answer"
        `14`. The guarded accumulator adds only positive values:
        $4 + 9 + 1 = 14$; the $-2$ is skipped.

3. In Java, when does `a == b` on two arrays print `true`?

    ??? success "Answer"
        Only when `a` and `b` refer to the *same array object*. Equal
        contents in two different arrays give `false`; content comparison
        needs `Arrays.equals(a, b)`. Python's `==` compares contents, and
        `is` is the "same object" test.

4. A program stores products in `names` and their prices in a parallel
   list `prices`, then calls `prices.sort()`. What breaks?

    ??? success "Answer"
        The index link. Prices are rearranged but names are not, so
        `names[i]` and `prices[i]` no longer describe the same product —
        with no error message to warn you. Either sort both lists
        together or bundle name and price into one object (Chapter 12).
