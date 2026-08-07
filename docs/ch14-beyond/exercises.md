# Exercises

These exercises cement the chapter's two habits: reaching for the right
collection without hesitation, and settling speed questions with
measurements instead of opinions. Predict before you run — starting with
Exercise 14.1, where that is the whole task.

### Exercise 14.1 — Predict the set output ●

Without running the code, write down exactly what the four `print`
lines produce. Then run it and compare.

```text
a = {1, 2, 3, 3, 2}
b = {3, 4}
print(len(a))
print(sorted(a | b))
print(sorted(a & b))
print(a - b == {1, 2})
```

??? success "Solution"

    ```python
    a = {1, 2, 3, 3, 2}
    b = {3, 4}
    print(len(a))
    print(sorted(a | b))
    print(sorted(a & b))
    print(a - b == {1, 2})
    ```

    It prints `3`, `[1, 2, 3, 4]`, `[3]`, `True`. The duplicates in the
    literal `{1, 2, 3, 3, 2}` collapse immediately, so `a` has three
    elements; union collects both sets, intersection keeps the shared
    `3`, and removing `b`'s elements from `a` leaves exactly `{1, 2}`.

### Exercise 14.2 — A phone book ●

Build a dictionary phone book with two entries. Then: add a third
person, look up one existing and one missing name using `get` with the
default `"not found"`, delete an entry with `del`, and finally print
the remaining entries in alphabetical order, one per line as
`name: number`.

??? success "Solution"

    ```python
    phone_book = {"Maya": "555-0142", "Leo": "555-0198"}
    phone_book["Iris"] = "555-0177"          # add

    print(phone_book.get("Leo", "not found"))
    print(phone_book.get("Zed", "not found"))

    del phone_book["Leo"]                    # remove

    for name in sorted(phone_book):          # loops over the keys
        print(f"{name}: {phone_book[name]}")
    ```

    Output: `555-0198`, `not found`, then `Iris: 555-0177` and
    `Maya: 555-0142`. Using `get` for the lookups means a missing name
    is an ordinary answer, not a `KeyError` crash.

### Exercise 14.3 — Enrollment puzzles ●●

Given these two course rosters, use set operations (no loops!) to
print, in sorted order: (a) students taking both courses, (b) students
taking at least one course, (c) students taking Python but not Java,
and (d) students taking exactly one of the two.

```python
python_course = {"ada", "ben", "chloe", "dev", "elena"}
java_course = {"ben", "dev", "farid"}
print("rosters loaded:", len(python_course), "and", len(java_course))
```

??? success "Solution"

    ```python
    python_course = {"ada", "ben", "chloe", "dev", "elena"}
    java_course = {"ben", "dev", "farid"}

    print(sorted(python_course & java_course))    # both
    print(sorted(python_course | java_course))    # at least one
    print(sorted(python_course - java_course))    # Python only
    print(sorted(python_course ^ java_course))    # exactly one
    ```

    Output: `['ben', 'dev']`, then all six names, then
    `['ada', 'chloe', 'elena']`, then
    `['ada', 'chloe', 'elena', 'farid']`. The `^` (symmetric
    difference) operator is union minus intersection. One thing sets
    *cannot* tell you: who takes neither course — the rosters only know
    who is in them, not who exists.

### Exercise 14.4 — Refactor to a set and prove the speedup ●●

The code below checks 1,000 ID badges against a list of 20,000 issued
IDs — with the list. Refactor it to use a set for the membership test,
time both versions with `time.perf_counter`, and print the ratio.

```python
issued = [f"ID-{i:05d}" for i in range(20_000)]
badges = [f"ID-{i:05d}" for i in range(0, 20_000, 20)]
valid = sum(1 for b in badges if b in issued)
print(valid, "valid badges")
```

??? success "Solution"

    ```python
    import time

    issued = [f"ID-{i:05d}" for i in range(20_000)]
    badges = [f"ID-{i:05d}" for i in range(0, 20_000, 20)]

    t0 = time.perf_counter()
    valid_list = sum(1 for b in badges if b in issued)
    list_time = time.perf_counter() - t0

    issued_set = set(issued)                 # one-time conversion
    t0 = time.perf_counter()
    valid_set = sum(1 for b in badges if b in issued_set)
    set_time = time.perf_counter() - t0

    print(valid_list, valid_set)             # same answer both ways
    print(f"list {list_time*1000:.1f} ms, set {set_time*1000:.2f} ms")
    print(f"roughly {list_time / set_time:.0f}x faster")
    ```

    Both counts are `1000`, and the set version wins by a factor in the
    hundreds. The refactor is one changed line plus one conversion —
    the cheapest large speedup you will ever buy.

### Exercise 14.5 — Top five words ●●

Count the words in the text below with a dictionary, then print the
five most frequent as `word: count`, most frequent first, breaking ties
alphabetically. (Hint: sort the items by `(-count, word)`.)

```python
text = ("the cat saw the dog and the dog saw the fish "
        "so the fish hid and the cat ran")
print(len(text.split()), "words")
```

??? success "Solution"

    ```python
    text = ("the cat saw the dog and the dog saw the fish "
            "so the fish hid and the cat ran")

    counts = {}
    for word in text.split():
        counts[word] = counts.get(word, 0) + 1

    ranked = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    for word, n in ranked[:5]:
        print(f"{word}: {n}")
    ```

    Output:

    ```text
    the: 6
    and: 2
    cat: 2
    dog: 2
    fish: 2
    ```

    Sorting by `(-count, word)` puts big counts first (negating flips
    the order) and alphabetical order second, so the six words tied at
    2 resolve deterministically — `saw` is the unlucky sixth.

### Exercise 14.6 — Tuple-keyed gradebook ●●

Store the scores below in one dictionary keyed by `(student, subject)`
tuples. Then compute and print each student's average, in alphabetical
order, without hard-coding the student names.

```text
Ana:  math 91, history 84
Ben:  math 77, history 88
```

??? success "Solution"

    ```python
    scores = {
        ("Ana", "math"): 91,
        ("Ana", "history"): 84,
        ("Ben", "math"): 77,
        ("Ben", "history"): 88,
    }

    totals = {}
    for (student, subject), score in scores.items():   # unpack the key!
        totals.setdefault(student, []).append(score)

    for student in sorted(totals):
        marks = totals[student]
        print(f"{student}: {sum(marks) / len(marks):.1f}")
    ```

    Output: `Ana: 87.5` and `Ben: 82.5`. The pattern to remember is the
    loop header: `for (student, subject), score in scores.items()`
    unpacks the tuple key and the value in one motion.

### Exercise 14.7 — Build your own Counter ●●●

Using only a plain dict, tally the letters of `"encyclopedia"`. Verify
your tally equals `Counter("encyclopedia")` with `==`, then produce the
top three letters yourself (count descending, ties alphabetical) —
without calling `most_common`.

??? success "Solution"

    ```python
    from collections import Counter

    word = "encyclopedia"
    tally = {}
    for letter in word:
        tally[letter] = tally.get(letter, 0) + 1

    print(tally == Counter(word))        # a Counter is a dict subclass

    top3 = sorted(tally.items(), key=lambda kv: (-kv[1], kv[0]))[:3]
    print(top3)
    ```

    Output: `True`, then `[('c', 2), ('e', 2), ('a', 1)]`. Note the
    tie-break: our rule ranks `c` before `e` alphabetically, whereas
    `Counter.most_common` breaks ties by first-seen order and would put
    `e` first — a reminder that "top three" is ambiguous until you
    state the tie rule.

### Exercise 14.8 — A miniature event dispatcher ●●●

Recreate the heart of a GUI framework from
[14.3](03-guis-and-beyond.md), one step further: allow *multiple*
handlers per event. Write `register(event, func)` and
`dispatch(event)` backed by a dictionary mapping each event name to a
*list* of callbacks. Dispatching an event calls every registered
handler in registration order; dispatching an unknown event prints
`(nothing registered for '<event>')`. Demonstrate with two handlers on
`"save"`, one on `"open"`, and a dispatch of `"close"`.

??? success "Solution"

    ```python
    handlers = {}

    def register(event, func):
        handlers.setdefault(event, []).append(func)

    def dispatch(event):
        funcs = handlers.get(event, [])
        if not funcs:
            print(f"(nothing registered for '{event}')")
        for func in funcs:                 # registration order
            func()

    def ding():
        print("ding!")

    def write_log():
        print("saved to log")

    register("save", ding)
    register("save", write_log)
    register("open", ding)

    dispatch("save")
    dispatch("open")
    dispatch("close")
    ```

    Output:

    ```text
    ding!
    saved to log
    ding!
    (nothing registered for 'close')
    ```

    `setdefault` creates the empty list the first time an event is
    registered; after that, handlers append in order. Swap the `print`
    calls for window redraws and you have the skeleton of every GUI
    toolkit ever shipped.
