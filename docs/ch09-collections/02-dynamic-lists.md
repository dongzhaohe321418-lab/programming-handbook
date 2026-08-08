# 9.2 Dynamic lists — ArrayList and list

Chapter 7 introduced arrays the way Java teaches them: you declare a length,
and that length is final — need an eleventh slot in a ten-slot array and you
must build a bigger array and copy everything across. Real programs rarely
know their sizes in advance (how many tasks on a to-do list? how many lines
in a file?), which is why every language offers a *growable* sequence.

In Java that is `ArrayList`, the star of this module of your Java course. In
Python it is the `list` you have been using all along — Python simply never
made you suffer the fixed-size version first. This page lines the two up
method-by-method so you can translate fluently in both directions.

## Fixed arrays grow the hard way; dynamic lists grow themselves

A Java array's length is part of its identity: `new int[3]` is three slots,
forever. An `ArrayList` wraps an ordinary array and manages it for you — when
the hidden array fills up, the `ArrayList` allocates a bigger one and copies
the elements over, without you noticing. Python's `list` works the same way
under the hood: a hidden, over-allocated array that is quietly replaced as
the list grows.

=== "Python"

    ```python
    scores = []              # empty — length 0, no ceremony
    scores.append(71)
    scores.append(84)
    scores.append(93)
    scores.append(65)        # it just grows
    print(scores)            # [71, 84, 93, 65]
    print(len(scores))       # 4
    ```

=== "Java"

    ```java
    import java.util.ArrayList;

    int[] fixed = new int[3];              // stuck at 3 slots forever

    ArrayList<Integer> scores = new ArrayList<>();
    scores.add(71);
    scores.add(84);
    scores.add(93);
    scores.add(65);                        // grows automatically
    System.out.println(scores);            // [71, 84, 93, 65]
    System.out.println(scores.size());     // 4
    ```

!!! info "Java corner — autoboxing"
    Generic types like `ArrayList<...>` only accept *objects*, and Java's
    primitive `int` is not an object. So you write `ArrayList<Integer>`,
    using the wrapper class, and Java silently converts between `int` and
    `Integer` for you — that conversion is called **autoboxing**. It mostly
    just works, with one famous trap shown later on this page.

## The translation table

Everything your Java course does with an `ArrayList`, Python does with a
built-in method or operator. This table is the whole correspondence — worth
bookmarking:

| What you want                | Java `ArrayList<Integer> a`      | Python `list` `a`            |
| ---------------------------- | -------------------------------- | ---------------------------- |
| add `x` at the end           | `a.add(x)`                       | `a.append(x)`                |
| insert `x` at index `i`      | `a.add(i, x)`                    | `a.insert(i, x)`             |
| read the element at `i`      | `a.get(i)`                       | `a[i]`                       |
| overwrite the element at `i` | `a.set(i, x)`                    | `a[i] = x`                   |
| remove first occurrence of value `x` | `a.remove(Integer.valueOf(x))` | `a.remove(x)`          |
| remove (and get) element at index `i` | `a.remove(i)`           | `a.pop(i)`                   |
| number of elements           | `a.size()`                       | `len(a)`                     |
| is `x` in there?             | `a.contains(x)`                  | `x in a`                     |
| where is `x`?                | `a.indexOf(x)` — `-1` if absent  | `a.index(x)` — *error* if absent |
| is it empty?                 | `a.isEmpty()`                    | `len(a) == 0`                |
| remove everything            | `a.clear()`                      | `a.clear()`                  |

Two notes on reading that table:

- **Style.** Where Java uses a method call for everything, Python uses square
  brackets for reading and writing by index, and keywords (`in`, `len`) for
  the most common questions.
- **One honest behavioural difference.** A failed `indexOf` *returns* `-1`,
  while a failed `index()` *raises an error* — a `ValueError`, exactly the
  kind of event [Chapter 10](../ch10-exceptions/index.md) teaches you to
  handle.

Now let's run each row of the table.

## Reading, writing, and measuring

```python
languages = ["Python", "Java", "C"]

print(languages[0])        # Python          (Java: languages.get(0))
languages[2] = "Rust"      #                 (Java: languages.set(2, "Rust"))
print(languages)           # ['Python', 'Java', 'Rust']
print(len(languages))      # 3               (Java: languages.size())
```

Indexes still start at 0, and reading past the end is still an error — being
growable does not mean indexes appear out of nowhere. Only `append` and
`insert` create new slots.

## Removing: by value or by position

There are two different jobs here, and mixing them up is a classic bug.
`remove(x)` searches for the *value* `x` and deletes its first occurrence;
`pop(i)` deletes whatever sits at *index* `i` — and hands it back to you:

```python
queue = ["Ada", "Grace", "Alan", "Grace"]

queue.remove("Grace")      # by VALUE — deletes only the first "Grace"
print(queue)               # ['Ada', 'Alan', 'Grace']

first = queue.pop(0)       # by INDEX — removes slot 0 and returns it
print(first)               # Ada
print(queue)               # ['Alan', 'Grace']
```

!!! info "Java corner — the autoboxing trap"
    Java's `ArrayList` has both jobs on one name: `remove(int i)` removes
    by index and `remove(Object x)` removes by value. For a list of
    `Integer`, `list.remove(2)` calls the *index* version — it deletes
    whatever is at position 2, not the number 2! To remove the value you
    must box it yourself: `list.remove(Integer.valueOf(2))`. Python
    sidesteps the trap by giving the two jobs two names, `remove` and
    `pop`.

## Searching: membership and position

```python
tickets = [101, 205, 307]

print(205 in tickets)         # True     (Java: tickets.contains(205))
print(999 in tickets)         # False
print(tickets.index(307))     # 2        (Java: tickets.indexOf(307))
```

Asking `index()` about a missing value raises a `ValueError`, so the safe
idiom is *check first, then ask*:

```python
tickets = [101, 205, 307]
wanted = 999

if wanted in tickets:
    print("found at index", tickets.index(wanted))
else:
    print(wanted, "is not in the list")   # Java-style: indexOf gave -1
```

## Inserting in the middle — and what it costs

`insert(i, x)` puts `x` at index `i`. But a list is a contiguous run of
slots, so there is no gap at index `i` to drop into — every element from
`i` onward must first shift one place to the right:

```python
line = ["Ada", "Alan", "Grace"]
line.insert(1, "Edsger")        # everyone from index 1 onward shifts right
print(line)                     # ['Ada', 'Edsger', 'Alan', 'Grace']
print(line.index("Alan"))       # 2 — Alan used to be at 1
```

Shifting is invisible in a four-element list. It is very visible when the
list is long and you insert at the front over and over — each insert shifts
the *entire* list:

```python
import time

n = 5000

front = []
start = time.perf_counter()
for i in range(n):
    front.insert(0, i)          # every insert shifts everything already there
front_time = time.perf_counter() - start

back = []
start = time.perf_counter()
for i in range(n):
    back.append(i)              # append only touches the end
back_time = time.perf_counter() - start

print(f"{n} inserts at the front: {front_time:.4f} seconds")
print(f"{n} appends at the end:   {back_time:.4f} seconds")
```

The exact numbers depend on your machine, but the front-inserting loop is
reliably many times slower — it does roughly $n^2/2$ element shifts in
total, while appending does none. Keep the intuition: **appending to the
end of a dynamic list is cheap; inserting or removing near the front is
expensive.** When a program genuinely needs fast insertion at the front,
there are data structures built for exactly that — the linked lists of
[Chapter 18](../ch18-linked-lists/index.md).

## Worked example: a to-do-list manager

Time to put the whole API to work. A to-do manager needs four features, and
each one is a row of the translation table:

- **Add a task, refusing duplicates** — `in` to check, then `append`.
- **Jump the queue for something urgent** — `insert(0, task)`.
- **Mark a task done** — `remove` by value, wherever it has drifted to.
- **Report what is left** — `len` for the count, `todo[0]` for what is next.

```python
def add_task(todo, task):
    if task in todo:                  # contains
        print("  already listed:", task)
    else:
        todo.append(task)             # add at the end
        print("  added:", task)

def add_urgent(todo, task):
    todo.insert(0, task)              # insert at the front
    print("  URGENT, added first:", task)

def finish_task(todo, task):
    if task in todo:
        todo.remove(task)             # remove by value
        print("  done:", task)
    else:
        print("  not on the list:", task)

def next_task(todo):
    if len(todo) == 0:                # isEmpty
        return "nothing — all clear!"
    return todo[0]                    # get(0)

todo = []
add_task(todo, "buy milk")
add_task(todo, "write essay")
add_task(todo, "buy milk")            # duplicate — rejected
add_urgent(todo, "submit tax form")
finish_task(todo, "buy milk")
print("remaining:", todo)
print("count:", len(todo))
print("up next:", next_task(todo))
```

Read the output against the code: the duplicate is refused by the `in`
check, the urgent task cuts the line via `insert(0, ...)`, and `remove`
deletes by value no matter where the task has drifted to. Every function
*mutates the shared list* it receives — the reference model from
[Section 9.1](01-references.md) working for you, not against you.

## Lists of lists: dynamic in two dimensions

Chapter 8's grids had a fixed shape decided up front. Because a list can
hold references to other lists, you can grow a table one row at a time —
and grow each row independently:

```python
gradebook = []                          # one row per student, added on demand
gradebook.append(["Ada", 91, 84])
gradebook.append(["Alan", 78, 88])
gradebook.append(["Grace", 95, 90])

for row in gradebook:
    average = (row[1] + row[2]) / 2
    print(f"{row[0]:<6} average {average:.1f}")

gradebook[1].append(99)                 # Alan takes an extra quiz
print(gradebook[1])                     # ['Alan', 78, 88, 99]
```

Rows of different lengths make this a **ragged** table — impossible with a
rectangular Java 2-D array, routine with nested dynamic lists (Java gets
the same effect with `ArrayList<ArrayList<Integer>>`). The price of the
flexibility is that *you* must keep track of what each row contains; the
grid patterns from [Section 8.1](../ch08-grids/01-2d-arrays.md) still apply
whenever the shape is regular.

!!! warning "Common mistakes"

    - **Confusing `remove` and `pop`.** `remove("Ada")` searches for a
      *value*; `pop(0)` deletes by *index*. Calling `remove(2)` on a list
      of numbers deletes the first `2` it finds — not the element at
      index 2. (In Java the same call *does* use the index — see the
      autoboxing trap above.)
    - **Calling `index()` without checking membership first.** A missing
      value raises `ValueError` and stops your program. Guard with `in`,
      or handle the exception once you have read
      [Chapter 10](../ch10-exceptions/index.md).
    - **Removing items from a list while looping over it** — elements
      shift left under the loop and get skipped. Loop over a copy
      (`for task in todo[:]`) or build a new list of survivors instead.
    - **Java: writing `ArrayList<int>`.** Generics need objects:
      `ArrayList<Integer>`, and let autoboxing handle the conversions.

## Check your understanding

1. Translate to Python, then give the final printed list:
   `a.add("x"); a.add("y"); a.add(1, "z"); a.set(0, "w"); a.remove("y");`
   starting from an empty `ArrayList<String> a`.

    ??? success "Answer"
        `a = []`, `a.append("x")`, `a.append("y")`,
        `a.insert(1, "z")`, `a[0] = "w"`, `a.remove("y")`.
        Trace: `['x']` → `['x','y']` → `['x','z','y']` → `['w','z','y']`
        → `['w','z']`.

2. Both `queue.remove("Grace")` and `queue.pop(1)` can delete `"Grace"`
   from `["Ada", "Grace", "Alan"]`. When would the two calls stop being
   interchangeable?

    ??? success "Answer"
        As soon as the list changes shape or holds duplicates: `remove`
        always deletes the *first occurrence of the value*, wherever it
        is; `pop(1)` always deletes *whatever is at index 1*. They only
        coincide while `"Grace"` happens to sit at index 1. Also, `pop`
        returns the removed element; `remove` returns nothing.

3. Why is `insert(0, x)` on a list of a million elements slow, while
   `append(x)` is fast?

    ??? success "Answer"
        The list stores its elements contiguously. Inserting at index 0
        must shift all one million references one slot to the right to
        open a gap; appending writes into the spare capacity at the end
        and shifts nothing. That per-insert shifting cost is why
        front-heavy workloads call for a linked structure
        ([Chapter 18](../ch18-linked-lists/index.md)).
