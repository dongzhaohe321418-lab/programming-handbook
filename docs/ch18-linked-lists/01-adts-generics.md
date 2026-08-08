# 18.1 Abstract data types and generics

When you call `my_list.append(x)`, do you know — or care — whether the items
live in one contiguous block of memory or in a chain of separate nodes? You
should not have to care while *using* the list; you absolutely must care
when *choosing or building* one. Keeping those two concerns apart is one of
the great organizing ideas of computer science, and it finally gets its
formal name here: the split between an **abstract data type** and a **data
structure**. This section pins down the vocabulary, shows why one contract
can have rival implementations with opposite costs, and explains the tool —
**generics** — that lets a single implementation serve every element type.

## WHAT versus HOW

An **abstract data type (ADT)** is a specification: the set of operations a
collection supports, and the contract each operation honours — what it
requires, what it returns, what state it leaves behind. It says nothing
about memory. A **data structure** is a concrete arrangement of data in
memory, plus algorithms, that *implements* an ADT.

You have met this WHAT/HOW split before: an interface in
[Chapter 15](../ch15-inheritance/03-interfaces.md) declares method
signatures without bodies, and any class that fills the bodies in can stand
behind the interface. An ADT is exactly that idea applied to collections —
in fact Java literally spells the List ADT as `interface List<E>`, which
`ArrayList` and `LinkedList` both implement.

Here is the **List ADT** — the contract behind both Python's `list` and
Java's `List` — reduced to its essential operations:

| Operation | Contract (the WHAT) |
| --- | --- |
| `get(i)` | return the item at position `i`; positions run `0 … size-1` |
| `set(i, x)` | replace the item at position `i` with `x` |
| `insert(i, x)` | make `x` the new position-`i` item; later items shift up one position |
| `remove(i)` | delete the position-`i` item; later items shift down one position |
| `size()` | return how many items are stored |

Nothing in that table mentions arrays, nodes, or memory addresses. That is
the point: any code written against the contract works with *any* correct
implementation.

## One contract, two rival implementations

The contract can be honoured two structurally different ways:

- **Array-based** (Python's `list`, Java's `ArrayList`): items sit side by
  side in one block, so position `i` is pure address arithmetic — but
  inserting at the front means shifting everything over.
- **Linked nodes** (this chapter; Java's `LinkedList`): each item lives in
  its own node holding a reference to the next, so splicing a node in at the
  front is two assignments — but reaching position `i` means walking `i`
  links.

| Operation | Array-based | Linked nodes |
| --- | --- | --- |
| `get(i)` / `set(i, x)` | $O(1)$ | $O(n)$ |
| `insert(0, x)` / `remove(0)` (front) | $O(n)$ | $O(1)$ |
| append at back | $O(1)$ amortized | $O(1)$ with a tail reference, else $O(n)$ |
| `insert` / `remove` in the middle, once you are standing there | $O(n)$ (shifting) | $O(1)$ (relinking) |
| find a value | $O(n)$ | $O(n)$ |
| memory layout | one compact block | one small object per item + references |

Read the first two rows together — they are mirror images. Neither
implementation wins; each is the champion of the operations the other is
worst at. This single table is the reason the next two sections (and half of
Part III) exist: to earn the right-hand column, you have to build it.

You can *feel* the left column's front-insertion cost from Chapter 16's
timing method without any new machinery:

```python
import time

def time_front_inserts(n):
    items = []
    start = time.perf_counter()
    for k in range(n):
        items.insert(0, k)        # front insertion: shifts every item over
    return (time.perf_counter() - start) * 1000

for n in [2000, 4000, 8000]:
    print(f"n = {n:5d}: {time_front_inserts(n):7.2f} ms")
```

Doubling `n` roughly quadruples the time — the signature of an $O(n^2)$
total, i.e. $O(n)$ *per insertion*. Hold that thought; in the next section a
linked list does the same job in $O(1)$ per insertion, and we will race
them.

## Generics: one implementation, many element types

Whichever implementation you pick, one thing would be absurd: writing
`IntList`, `StringList`, `DogList` … one collection class per element type.
The machinery that avoids this is called **generics** — the collection is
written once with a placeholder for the element type, and the placeholder is
filled in where the collection is used. Java and Python realize this idea
very differently, and the difference is worth seeing side by side.

=== "Python"

    ```python
    names: list[str] = []        # a type HINT: "list of strings"
    names.append("Ada")
    names.append("Grace")
    print(names[0].upper())      # tools know names[0] is a str
    ```

=== "Java"

    ```java
    List<String> names = new ArrayList<>();
    names.add("Ada");
    names.add("Grace");
    String first = names.get(0);   // no cast needed: compiler KNOWS
    ```

### Java: checked by the compiler

In Java, `List<String>` is enforced by the **compiler**: the parameter
`<String>` becomes part of the type, and code that violates it does not
compile — the error below is caught before the program ever runs:

```text
names.add(42);
      ^^^^^^^
error: incompatible types: int cannot be converted to String
```

### Python: checked by your tools, if you run them

Python's `list[str]` looks similar but is honestly weaker: it is a **type
hint**, checked by *tools* (editors, and checkers such as `mypy`) — not by
the running interpreter. Python itself will happily execute type-violating
code:

```python
def shout(words: list[str]) -> str:
    return " ".join(w.upper() for w in words)

print(shout(["type", "hints", "are", "labels"]))
print(shout("oops"))     # wrong type — but Python runs it anyway!
```

The second call passes a plain string where a list of strings was promised.
No error: iterating a string yields its characters, so you get `O O P S` —
silently wrong-shaped output instead of a compile-time stop. A type checker
flags `shout("oops")` immediately; the interpreter never will.

So the two languages differ in *who* checks and *when*:

| | Java `List<String>` | Python `list[str]` |
| --- | --- | --- |
| Who checks | the compiler | a separate tool (editor, `mypy`) |
| When | before the program runs | whenever you choose to run the checker |
| Is it optional? | no — the code will not compile | yes — the interpreter ignores hints |
| Violation results in | a compile error | a wrong-looking result, or nothing at all |

That is the honest deal with Python typing: hints are machine-checkable
*documentation*, valuable precisely because tools and teammates read them —
but the runtime safety net of Java generics is not there.

## A typed Bag, and a glimpse of Stack[T]

Let us practise writing the hints ourselves. A **Bag** is one of the
simplest ADTs: add items, count occurrences, report the size — no positions,
no ordering promises. Here it is, typed by convention throughout:

```python
class Bag:
    """Bag ADT: an unordered collection that counts duplicates."""

    def __init__(self) -> None:
        self._items: list[str] = []      # the HOW, hidden behind an underscore

    def add(self, item: str) -> None:
        self._items.append(item)

    def count(self, item: str) -> int:
        return self._items.count(item)

    def size(self) -> int:
        return len(self._items)

votes = Bag()
for choice in ["tea", "coffee", "tea", "water", "tea"]:
    votes.add(choice)
print("total votes:", votes.size())
print("tea:", votes.count("tea"), "| coffee:", votes.count("coffee"))
```

The public methods *are* the ADT; the private `_items` list is the data
structure, swappable without any caller noticing. But this `Bag` is welded
to `str`. To write it once for *any* element type — Python's counterpart to
Java's `<E>` — declare a **type variable**:

```python
from typing import TypeVar, Generic

T = TypeVar("T")                 # "some element type, fixed per stack"

class Stack(Generic[T]):
    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> T:
        return self._items.pop()

numbers: Stack[int] = Stack()
numbers.push(7)
numbers.push(11)
print(numbers.pop() + 1)         # a checker knows this is an int

words: Stack[str] = Stack()
words.push("hi")
print(words.pop().upper())       # ...and this is a str
```

One class, two differently-typed stacks — a checker will flag
`numbers.push("oops")` while the same `push` accepts `"hi"` on `words`.
(Python 3.12 adds the tidier spelling `class Stack[T]:`; same meaning.) The
full Stack ADT gets its own treatment in
[Chapter 19](../ch19-stacks-queues/02-stacks.md) — here it is only our
excuse to write `T`.

!!! info "Java corner"
    Java generics stop at the compiler by design ("type erasure"): at
    runtime a `List<String>` and a `List<Integer>` are the same class. So
    Java's story is *compile-time yes, runtime no*, while Python's is
    *tool-time yes, runtime no* — the difference is that Java's check is
    mandatory and Python's is opt-in.

!!! warning "Common mistakes"
    - **Believing hints are enforced.** `def f(x: int)` does not stop
      `f("hello")` at runtime. If you need a hard guarantee, check
      explicitly (`isinstance`) or run a type checker in CI.
    - **Confusing the ADT with its habitual implementation.** "List" names a
      contract; Python's `list` is one implementation of it. Saying "lists
      are $O(1)$ at the front" is a claim about a *structure*, not the ADT.
    - **Choosing a structure before listing the operations.** The table
      above is only usable once you know which operations your program
      actually performs most. Count first, choose second.
    - **Writing one collection class per element type.** If you find
      yourself designing `IntStack` and `StrStack`, you want a type
      variable, not a copy-paste.

## Check your understanding

1. In one sentence each: what does an ADT specify, and what does a data
   structure add to that?

    ??? success "Answer"
        An ADT specifies *what* operations exist and what each promises (the
        contract); a data structure supplies *how* — a concrete memory
        arrangement and algorithms that honour the contract, with particular
        costs.

2. Your program does millions of `get(i)` calls at random positions and
   almost never inserts. Array or linked nodes? What if it instead does
   millions of insertions at the front?

    ??? success "Answer"
        Random `get(i)`: array-based — $O(1)$ indexing versus $O(n)$ walking.
        Millions of front insertions: linked nodes — $O(1)$ relinking versus
        $O(n)$ shifting per insertion.

3. Why does `shout("oops")` run without error in Python, and what would
   Java do with the equivalent mistake?

    ??? success "Answer"
        Python hints are not enforced at runtime; a string is iterable, so
        the function happily iterates its characters and returns `O O P S`.
        Java would reject the program at compile time — the argument type
        would not match the declared parameter type.

4. What problem do generics solve that inheritance alone does not?

    ??? success "Answer"
        They let *one* implementation work for many element types while
        keeping type safety per instance: `Stack[int]` and `Stack[str]`
        share all their code, yet a checker (or the Java compiler) still
        rejects pushing a string onto the int stack.
