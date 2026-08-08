# Exercises

## The chapter in brief

- A variable is a **name bound to an object** on the heap, not a box holding
  a value ([9.1](01-references.md)).
- `b = a` copies the *reference*, so both names are aliases of one object and
  a mutation through either is visible through both.
- `==` asks whether contents are equal; `is` asks whether there is only one
  object — and `is` on numbers or strings reports caching, not logic.
- A slice, `list(...)`, or `.copy()` makes a **shallow** copy: a new outer
  list whose elements are still shared, which is why nested data needs
  `copy.deepcopy`.
- Python has no primitives; integers merely *feel* like values because they
  are immutable, so the sharing can never be observed.
- Argument passing is assignment, so a function can mutate the caller's list,
  while rebinding the parameter name changes nothing outside.
- A dynamic list — Python's `list`, Java's `ArrayList` — grows itself by
  quietly replacing a hidden over-allocated array ([9.2](02-dynamic-lists.md)).
- Every `ArrayList` method has a Python equivalent, with one honest
  difference: a missing value makes `indexOf` return `-1` but makes `index()`
  raise `ValueError`.
- `remove(x)` deletes by *value* and `pop(i)` by *index* — two jobs that Java
  packs into one overloaded name.
- Appending is cheap, while inserting near the front shifts every later
  element, which is why front-heavy work eventually wants a linked structure.
- Stack frames hold names and the heap holds objects, so several frames can
  point at one object at once ([9.3](03-objects-in-memory.md)).
- Every object has an **external view** (the method menu you may rely on) and
  an **internal view** (the state and code its author may rewrite freely).

### Key terms

| Term | Reminder |
| --- | --- |
| [reference](../concept-index.md) | the tie from a name to an object living on the heap |
| [aliasing](../concept-index.md) | two or more names bound to one object |
| [identity](../concept-index.md) | what `is` compares — same object, not merely equal contents |
| [copy, shallow vs deep](../concept-index.md) | shallow duplicates the outer container only; deep duplicates every level |
| immutability | no operation changes the object in place, which is what hides an `int`'s sharing |
| [primitive vs reference type](../concept-index.md) | Java's two-world split; Python has references only |
| [`ArrayList`](../concept-index.md) | Java's growable list, method-for-method Python's `list` |
| [stack frame](../concept-index.md) | one call's names — frames hold names, the heap holds objects |
| external vs internal view | the promises a user relies on, versus the mechanism its author may rewrite |

Now put the model to the test.

Aliasing predictions are the heart of this chapter: for every "predict"
exercise, write down the exact output *before* running anything — the gap
between your prediction and reality is where the reference model gets
installed. Difficulty: ● warm-up, ●● standard, ●●● challenge.

### Exercise 9.1 — Predict the alias ●

Two names, one list. Predict the three printed lines exactly, then run.

```python
a = [1, 2, 3]
b = a
b.append(4)
a[0] = 99
print(a)
print(b)
print(a is b)
```

??? success "Solution"

    ```python
    a = [1, 2, 3]
    b = a
    b.append(4)
    a[0] = 99
    print(a)        # [99, 2, 3, 4]
    print(b)        # [99, 2, 3, 4]
    print(a is b)   # True
    ```

    `b = a` copied a reference, so both mutations — the append through `b`
    and the index assignment through `a` — landed on the single shared
    list, and both names show both changes.

### Exercise 9.2 — `==` or `is`? ●

Predict all four boolean values, then run.

```python
p = [7, 8]
q = [7, 8]
r = q
print(p == q, p is q)
print(q == r, q is r)
```

??? success "Solution"

    ```python
    p = [7, 8]
    q = [7, 8]
    r = q
    print(p == q, p is q)   # True False
    print(q == r, q is r)   # True True
    ```

    `p` and `q` were built by two separate list displays — equal contents,
    different objects. `r = q` created an alias, so `q is r` is `True`
    (and identity always implies equality).

### Exercise 9.3 — The photocopy that wasn't ●●

A program "backs up" a nested list before changing it. Predict what
`print(backup)` shows, explain why the backup failed, then fix the code so
the backup really is untouched.

```python
teams = [["Ada", "Alan"], ["Grace"]]
backup = teams.copy()
teams[1].append("Edsger")
teams.append(["Linus"])
print(backup)
```

??? success "Solution"

    It prints `[['Ada', 'Alan'], ['Grace', 'Edsger']]` — the appended
    *row* leaked into the backup (shared inner list), while the appended
    *team* did not (the outer lists are separate). `copy()` is shallow.
    The fix is a deep copy:

    ```python
    import copy

    teams = [["Ada", "Alan"], ["Grace"]]
    backup = copy.deepcopy(teams)
    teams[1].append("Edsger")
    teams.append(["Linus"])
    print(backup)   # [['Ada', 'Alan'], ['Grace']] — a true snapshot
    print(teams)    # [['Ada', 'Alan'], ['Grace', 'Edsger'], ['Linus']]
    ```

    `deepcopy` duplicates the outer list *and* every inner list, so no
    later mutation can reach the backup.

### Exercise 9.4 — ArrayList → list translation ●●

Translate this Java fragment into Python line by line, predict the four
printed values, then run your translation.

```java
ArrayList<String> stack = new ArrayList<>();
stack.add("red");
stack.add("green");
stack.add(1, "blue");
stack.set(0, "pink");
stack.remove("green");
System.out.println(stack.size());
System.out.println(stack);
System.out.println(stack.indexOf("blue"));
System.out.println(stack.contains("red"));
```

??? success "Solution"

    ```python
    stack = []
    stack.append("red")            # ['red']
    stack.append("green")          # ['red', 'green']
    stack.insert(1, "blue")        # ['red', 'blue', 'green']
    stack[0] = "pink"              # ['pink', 'blue', 'green']
    stack.remove("green")          # ['pink', 'blue']
    print(len(stack))              # 2
    print(stack)                   # ['pink', 'blue']
    print(stack.index("blue"))     # 1
    print("red" in stack)          # False
    ```

    Method map used: `add`→`append`, `add(i, x)`→`insert`,
    `set`→`stack[i] = x`, `remove(value)`→`remove`, `size`→`len`,
    `indexOf`→`index`, `contains`→`in`. Note `"red"` was overwritten by
    `set(0, "pink")`, so the membership test is `False`.

### Exercise 9.5 — Mutate or rebind? ●●

One of these functions changes the caller's list; the other only thinks it
does. Predict the final print, then run and explain the difference in one
sentence.

```python
def grow(items):
    items.append("!")

def shrink(items):
    items = items[:-1]

words = ["a", "b", "c"]
grow(words)
shrink(words)
print(words)
```

??? success "Solution"

    ```python
    def grow(items):
        items.append("!")        # mutates the shared list object

    def shrink(items):
        items = items[:-1]       # builds a NEW list, rebinds the local name

    words = ["a", "b", "c"]
    grow(words)
    shrink(words)
    print(words)                 # ['a', 'b', 'c', '!']
    ```

    `append` mutates the object both names share, so it sticks; the slice
    in `shrink` creates a new list and binds it to the *local* name
    `items`, leaving the caller's list untouched.

### Exercise 9.6 — To-do manager, extended ●●

Extend the to-do manager from
[Section 9.2](02-dynamic-lists.md) with two features:
`rename_task(todo, old, new)` replaces a task's text *in place* (keep its
position!), and `postpone(todo, task)` moves a task to the end of the list.
Both should print a friendly message when the task is missing.

??? success "Solution"

    ```python
    def rename_task(todo, old, new):
        if old in todo:
            todo[todo.index(old)] = new     # overwrite at the same index
            print("  renamed:", old, "->", new)
        else:
            print("  not on the list:", old)

    def postpone(todo, task):
        if task in todo:
            todo.remove(task)               # take it out ...
            todo.append(task)               # ... and re-add at the end
            print("  postponed:", task)
        else:
            print("  not on the list:", task)

    todo = ["buy milk", "write essay", "call plumber"]
    rename_task(todo, "buy milk", "buy oat milk")
    postpone(todo, "buy oat milk")
    rename_task(todo, "walk dog", "walk cat")
    print(todo)   # ['write essay', 'call plumber', 'buy oat milk']
    ```

    Renaming keeps position by writing through `index()`; postponing is a
    remove-by-value followed by an append, and both functions guard with
    `in` so a missing task never raises `ValueError`.

### Exercise 9.7 — Write your own deep copy ●●●

Without importing the `copy` module, write `copy_grid(grid)` that returns a
fully independent copy of a list of lists (two levels deep). Prove it works:
mutate the original's outer list *and* one inner list, and show the copy is
unchanged.

??? success "Solution"

    ```python
    def copy_grid(grid):
        new_grid = []
        for row in grid:
            new_grid.append(row[:])    # a fresh copy of each inner list
        return new_grid                # inside a fresh outer list

    grid = [[1, 2], [3, 4]]
    snapshot = copy_grid(grid)

    grid[0].append(99)                 # mutate an inner list
    grid.append([5, 6])                # mutate the outer list

    print(grid)       # [[1, 2, 99], [3, 4], [5, 6]]
    print(snapshot)   # [[1, 2], [3, 4]] — fully independent
    ```

    A deep copy is just a shallow copy applied at every level: a new outer
    list whose elements are new inner lists. (`copy.deepcopy` does the same
    idea for arbitrarily nested data.)

### Exercise 9.8 — One dict, two rosters ●●●

Alan is enrolled in two classes, and both class lists refer to the same
record. Predict the printed score, explain the mechanism with the words
*heap*, *reference*, and *alias*, then change the code so each class holds
an independent record (hint: `dict(alan)` copies a dict shallowly).

```python
alan = {"name": "Alan", "score": 78}
class_a = [alan]
class_b = [alan]
class_b[0]["score"] = 100
print(class_a[0]["score"])
```

??? success "Solution"

    It prints `100`. There is one dict object on the heap; `alan`,
    `class_a[0]`, and `class_b[0]` are three aliases holding references to
    it, so a mutation through any alias is visible through all of them.
    Independent records require copies:

    ```python
    alan = {"name": "Alan", "score": 78}
    class_a = [dict(alan)]              # a copy for class A
    class_b = [dict(alan)]              # a separate copy for class B
    class_b[0]["score"] = 100
    print(class_a[0]["score"])          # 78 — unaffected
    print(class_a[0] is class_b[0])     # False
    ```

    Whether sharing or copying is *correct* depends on the program: one
    student with one official record probably *should* be shared — that
    is aliasing used deliberately.
