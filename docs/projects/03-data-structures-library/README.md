# Project 3 · Data-Structures Library

Every serious programmer builds these once. You will implement a dynamic
array, a linked list, a stack, a queue, and a min-heap from scratch — each
one backed by a batch of assert-style tests, so by the end you own a small,
*verified* library and know exactly what `list.append` and `heapq` are doing
on your behalf.

## What you'll build

Five data structures plus a tiny test harness that reports on each one:

```text
Testing the library:
  DynamicArray        10 checks
  SinglyLinkedList     9 checks
  Stack + Queue        6 checks
  MinHeap              6 checks
  protocols           10 checks

41/41 checks passed — library is healthy!
```

Quiet output is the point: a healthy library prints one line per structure,
and any failure prints a loud `FAIL:` line naming the broken check.

## What it exercises

- [8.4 Unit testing](../../ch08-grids/04-unit-testing.md) — the
  write-a-check-first habit, distilled into a 10-line harness.
- [16.1 Big-O notation](../../ch16-complexity/01-big-o.md) — every operation
  you write has a cost you can now *see*.
- [Chapter 18 · ADTs and Linked Lists](../../ch18-linked-lists/index.md) —
  nodes, references, and the head/tail bookkeeping.
- [Chapter 19 · Iterators, Stacks, and Queues](../../ch19-stacks-queues/index.md)
  — LIFO, FIFO, and making your own types work with `for`.
- [Chapter 21 · Heaps and Priority Queues](../../ch21-heaps/index.md) — the
  array-backed binary heap and its index arithmetic.

## Milestones

### Milestone 1 — a test harness you can trust

**Goal:** write `check(name, condition)` — count passes, print a `FAIL`
line with the name when a condition is false — and
`run_suite(title, suite)` which runs one structure's test function and
reports how many checks it added.

**Done when...** `check("math works", 1 + 1 == 2)` passes silently,
`check("broken", 1 + 1 == 3)` prints `FAIL: broken`, and a final summary
can report `passed/total`. Everything after this milestone gets tested
through this harness.

??? tip "Hint"

    A dictionary is the simplest shared scoreboard — mutating it inside a
    function needs no `global` declaration:

    ```python
    results = {"pass": 0, "fail": 0}

    def check(name, condition):
        if condition:
            results["pass"] += 1
        else:
            results["fail"] += 1
            print("FAIL:", name)

    check("math works", 1 + 1 == 2)
    check("broken on purpose", 1 + 1 == 3)
    print(results)
    ```

### Milestone 2 — DynamicArray (feel the doubling)

**Goal:** build a growable array on top of a *fixed-capacity* block:
`[None] * capacity`, a `_size` counter, `append` that doubles capacity when
full, index get/set with bounds checks, `pop_back`, and a public `resizes`
counter so you can watch the growth happen.

**Done when...** ten appends onto a capacity-4 array leave
`capacity() == 16` and `resizes == 2`; out-of-range indexing raises
`IndexError`; and appending 1000 items onto a capacity-1 array performs
exactly `1023` element copies in total — roughly `n`, which is *why* append
is O(1) amortized.

??? tip "Hint"

    Python lists hide their capacity, so simulate the fixed block
    yourself: a plain list of `None` that you index into but never
    `append` to. Growth is "allocate bigger, copy across, swap":

    ```python
    items, size = [None] * 4, 4          # full!
    bigger = [None] * (2 * len(items))
    for i in range(size):
        bigger[i] = items[i]             # this loop is the O(n) cost
    items = bigger
    print(len(items), items)
    ```

    The copies for 1000 appends from capacity 1 total
    $1 + 2 + 4 + \dots + 512 = 1023$ — a geometric series that stays
    proportional to $n$ no matter how large $n$ grows. Doubling is the
    whole trick.

### Milestone 3 — SinglyLinkedList

**Goal:** a `_Node` with `value` and `next`, then `push_front`,
`push_back`, `pop_front`, and `remove(value)` — with head *and* tail
references so both pushes are O(1).

**Done when...** pushes at both ends produce the right order, `pop_front`
on an empty list raises `IndexError`, removing the tail leaves the list
reusable (push after emptying still works — the classic dangling-tail
bug), and `remove` returns `True`/`False` for found/not found.

??? tip "Hint"

    `remove` needs *two* fingers walking the chain — the node you are
    looking at and the one before it, because unlinking happens at the
    predecessor:

    ```text
    previous, current = None, head
    while current is not None:
        if current.value == target:
            ... unlink: previous.next = current.next ...
        previous, current = current, current.next
    ```

    Three cases to test separately: removing the head (`previous` is
    `None`), a middle node, and the tail (must update the tail
    reference!).

### Milestone 4 — Stack and Queue by composition

**Goal:** `Stack` (`push`, `pop`, `peek`) built *on top of your
DynamicArray*, and `Queue` (`enqueue`, `dequeue`) built on your
SinglyLinkedList — no new storage logic, just thin adapters that expose
the right ends.

**Done when...** `push a, b, c` pops `c, b, a`; `enqueue a, b, c` dequeues
`a, b, c`; both raise `IndexError` when empty; and neither class touches
a private attribute of the structure it wraps.

??? tip "Hint"

    This milestone is a design lesson wearing a data-structure costume:
    pick the backing structure whose *cheap* ends match. Stack wants one
    fast end — the array's back. Queue wants two — the linked list's
    tail (in) and head (out). A queue on a plain array would shift every
    element on each dequeue: O(n) for what should cost O(1), as
    [19.3 Queues](../../ch19-stacks-queues/03-queues.md) explains.

### Milestone 5 — MinHeap

**Goal:** an array-backed binary min-heap: `push` (append, then sift up)
and `pop_min` (promote the last item to the root, then sift down), plus
`peek`.

**Done when...** after pushing 20 shuffled values, `peek()` is the
minimum, and 20 `pop_min()` calls come out exactly sorted — the
"accidental heapsort" test that catches almost every sifting bug.

??? tip "Hint"

    No node objects — the tree lives inside a flat list through pure
    index arithmetic:

    ```python
    i = 5
    print("parent of", i, "is", (i - 1) // 2)
    print("children of", i, "are", 2 * i + 1, "and", 2 * i + 2)
    ```

    Sift-down must pick the *smaller* child to swap with (compare both!),
    and stop when neither child is smaller. Off-by-one in the child
    bounds check (`left < n`, `right < n`) is the usual culprit when the
    drain test comes out unsorted.

### Milestone 6 — speak fluent Python: `__len__`, `__contains__`, `__iter__`

**Goal:** add the three protocol methods to DynamicArray,
SinglyLinkedList, and MinHeap, so `len(x)`, `value in x`, and
`for item in x` work on all of them.

**Done when...** the protocols suite passes: `len` and `in` work on all
three structures, a `for` loop yields array and list elements in order,
iterating the heap yields values *smallest-first without draining it*
(iterate a clone, not the real storage), and the heap still has its items
afterwards.

??? tip "Hint"

    Write `__iter__` as a generator and the other two almost fall out —
    `__contains__` can be one line over `self`:

    ```python
    class Bag:
        def __init__(self, *values):
            self._values = list(values)

        def __len__(self):
            return len(self._values)

        def __iter__(self):
            yield from self._values

        def __contains__(self, value):
            return any(item == value for item in self)

    bag = Bag(3, 1, 2)
    print(len(bag), 2 in bag, [x for x in bag])
    ```

    This is the payoff of [19.1 Iterators](../../ch19-stacks-queues/01-iterators.md):
    your types now plug into the same syntax as the built-ins.

## Reference implementation

Build yours milestone by milestone — the reference is for comparing test
ideas as much as code.

??? success "Full reference implementation"

    ```python
    """A small data-structures library, tested structure by structure."""
    import random

    # =========================== test harness ==============================
    results = {"pass": 0, "fail": 0}


    def check(name, condition):
        """Record one test result; print a line only when something fails."""
        if condition:
            results["pass"] += 1
        else:
            results["fail"] += 1
            print(f"     FAIL: {name}")


    def run_suite(title, suite):
        """Run one structure's tests and report how many checks it added."""
        before = results["pass"] + results["fail"]
        suite()
        ran = results["pass"] + results["fail"] - before
        print(f"  {title:<18} {ran:>3} checks")


    # =========================== DynamicArray ==============================
    class DynamicArray:
        """A growable array on a fixed-capacity block, like Java's ArrayList.

        Python lists do this internally; building it by hand shows *why*
        append is fast on average: doubling makes total copying O(n).
        """

        def __init__(self, capacity=4):
            self._items = [None] * capacity
            self._size = 0
            self.resizes = 0          # public: watch the doubling happen

        def append(self, value):
            if self._size == len(self._items):
                self._grow()
            self._items[self._size] = value
            self._size += 1

        def _grow(self):
            """Double the capacity and copy every element across."""
            self.resizes += 1
            bigger = [None] * (2 * len(self._items))
            for i in range(self._size):
                bigger[i] = self._items[i]
            self._items = bigger

        def pop_back(self):
            """Remove and return the last element; O(1)."""
            if self._size == 0:
                raise IndexError("pop_back from an empty array")
            self._size -= 1
            value = self._items[self._size]
            self._items[self._size] = None    # drop the hidden reference
            return value

        def capacity(self):
            return len(self._items)

        def _index_ok(self, index):
            if not 0 <= index < self._size:
                raise IndexError(
                    f"index {index} out of range for size {self._size}")

        def __getitem__(self, index):
            self._index_ok(index)
            return self._items[index]

        def __setitem__(self, index, value):
            self._index_ok(index)
            self._items[index] = value

        def __len__(self):
            return self._size

        def __iter__(self):
            for i in range(self._size):
                yield self._items[i]

        def __contains__(self, value):
            return any(item == value for item in self)


    def test_dynamic_array():
        arr = DynamicArray(capacity=4)
        check("new array is empty", len(arr) == 0)
        for n in range(10):
            arr.append(n * n)
        check("append grows size", len(arr) == 10)
        check("values in order", list(arr) == [n * n for n in range(10)])
        check("get by index", arr[3] == 9)
        arr[3] = -1
        check("set by index", arr[3] == -1)
        check("membership works", 81 in arr and 999 not in arr)
        check("doubled 4->8->16", arr.capacity() == 16 and arr.resizes == 2)
        check("pop_back returns last", arr.pop_back() == 81 and len(arr) == 9)
        try:
            arr[10]
            check("bounds check", False)
        except IndexError:
            check("bounds check", True)

        # Amortized growth: appending n items copies about n elements total.
        big = DynamicArray(capacity=1)
        for n in range(1000):
            big.append(n)
        total_copied = sum(2 ** k for k in range(big.resizes))  # 1+2+...+512
        check("about n copies for n appends", total_copied == 1023)


    # =========================== SinglyLinkedList ==========================
    class SinglyLinkedList:
        """Nodes chained by `next` references; no shifting, no capacity."""

        class _Node:
            __slots__ = ("value", "next")

            def __init__(self, value, next=None):
                self.value = value
                self.next = next

        def __init__(self):
            self._head = None
            self._tail = None
            self._size = 0

        def push_front(self, value):
            """O(1): the new node points at the old head."""
            self._head = self._Node(value, self._head)
            if self._tail is None:
                self._tail = self._head
            self._size += 1

        def push_back(self, value):
            """O(1) because we keep a tail reference."""
            node = self._Node(value)
            if self._tail is None:
                self._head = self._tail = node
            else:
                self._tail.next = node
                self._tail = node
            self._size += 1

        def pop_front(self):
            """Remove and return the first value; O(1)."""
            if self._head is None:
                raise IndexError("pop_front from an empty list")
            node = self._head
            self._head = node.next
            if self._head is None:
                self._tail = None
            self._size -= 1
            return node.value

        def remove(self, value):
            """Unlink the first node holding `value`; return True if found."""
            previous, current = None, self._head
            while current is not None:
                if current.value == value:
                    if previous is None:
                        self._head = current.next
                    else:
                        previous.next = current.next
                    if current is self._tail:
                        self._tail = previous
                    self._size -= 1
                    return True
                previous, current = current, current.next
            return False

        def __len__(self):
            return self._size

        def __iter__(self):
            current = self._head
            while current is not None:
                yield current.value
                current = current.next

        def __contains__(self, value):
            return any(item == value for item in self)


    def test_linked_list():
        lst = SinglyLinkedList()
        check("new list is empty", len(lst) == 0)
        lst.push_back("b")
        lst.push_back("c")
        lst.push_front("a")
        check("front/back order", list(lst) == ["a", "b", "c"])
        check("membership", "b" in lst and "z" not in lst)
        check("pop_front returns head", lst.pop_front() == "a")
        check("remove middle", lst.remove("b") and list(lst) == ["c"])
        check("remove missing is False", lst.remove("zzz") is False)
        check("remove tail fixes tail", lst.remove("c") and len(lst) == 0)
        lst.push_back("again")        # tail must still work after emptying
        check("reusable after empty", list(lst) == ["again"])
        empty = SinglyLinkedList()
        try:
            empty.pop_front()
            check("pop empty raises", False)
        except IndexError:
            check("pop empty raises", True)


    # =========================== Stack and Queue ===========================
    class Stack:
        """LIFO built on our DynamicArray — composition, not reinvention."""

        def __init__(self):
            self._items = DynamicArray()

        def push(self, value):
            self._items.append(value)

        def pop(self):
            if len(self._items) == 0:
                raise IndexError("pop from an empty stack")
            return self._items.pop_back()

        def peek(self):
            if len(self._items) == 0:
                raise IndexError("peek at an empty stack")
            return self._items[len(self._items) - 1]

        def __len__(self):
            return len(self._items)


    class Queue:
        """FIFO built on our SinglyLinkedList: O(1) enqueue and dequeue."""

        def __init__(self):
            self._items = SinglyLinkedList()

        def enqueue(self, value):
            self._items.push_back(value)

        def dequeue(self):
            if len(self._items) == 0:
                raise IndexError("dequeue from an empty queue")
            return self._items.pop_front()

        def __len__(self):
            return len(self._items)


    def test_stack_and_queue():
        stack = Stack()
        for ch in "abc":
            stack.push(ch)
        check("stack is LIFO", stack.pop() == "c" and stack.pop() == "b")
        check("peek does not remove", stack.peek() == "a" and len(stack) == 1)
        queue = Queue()
        for ch in "abc":
            queue.enqueue(ch)
        check("queue is FIFO", queue.dequeue() == "a" and queue.dequeue() == "b")
        check("queue size tracks", len(queue) == 1)
        try:
            Stack().pop()
            check("empty stack raises", False)
        except IndexError:
            check("empty stack raises", True)
        try:
            Queue().dequeue()
            check("empty queue raises", False)
        except IndexError:
            check("empty queue raises", True)


    # =============================== MinHeap ===============================
    class MinHeap:
        """Array-backed binary min-heap: the smallest item sits at index 0.

        Children of index i live at 2i+1 and 2i+2; the parent at (i-1)//2.
        """

        def __init__(self):
            self._items = []

        def push(self, value):
            """Add at the end, then sift up until the parent is smaller."""
            self._items.append(value)
            i = len(self._items) - 1
            while i > 0:
                parent = (i - 1) // 2
                if self._items[i] >= self._items[parent]:
                    break
                self._items[i], self._items[parent] = \
                    self._items[parent], self._items[i]
                i = parent

        def pop_min(self):
            """Remove the root, promote the last item, sift it down."""
            if not self._items:
                raise IndexError("pop_min from an empty heap")
            smallest = self._items[0]
            last = self._items.pop()
            if self._items:
                self._items[0] = last
                self._sift_down(0)
            return smallest

        def _sift_down(self, i):
            n = len(self._items)
            while True:
                left, right = 2 * i + 1, 2 * i + 2
                smallest = i
                if left < n and self._items[left] < self._items[smallest]:
                    smallest = left
                if right < n and self._items[right] < self._items[smallest]:
                    smallest = right
                if smallest == i:
                    return
                self._items[i], self._items[smallest] = \
                    self._items[smallest], self._items[i]
                i = smallest

        def peek(self):
            if not self._items:
                raise IndexError("peek at an empty heap")
            return self._items[0]

        def __len__(self):
            return len(self._items)

        def __contains__(self, value):
            return value in self._items

        def __iter__(self):
            """Yield items smallest-first without disturbing this heap."""
            clone = MinHeap()
            clone._items = list(self._items)
            while len(clone):
                yield clone.pop_min()


    def test_min_heap():
        heap = MinHeap()
        random.seed(7)
        values = random.sample(range(100), 20)
        for v in values:
            heap.push(v)
        check("size after pushes", len(heap) == 20)
        check("peek is the minimum", heap.peek() == min(values))
        check("membership", values[0] in heap and 555 not in heap)
        drained = [heap.pop_min() for _ in range(20)]
        check("pops come out sorted", drained == sorted(values))
        check("heap is empty after", len(heap) == 0)
        try:
            heap.pop_min()
            check("empty heap raises", False)
        except IndexError:
            check("empty heap raises", True)


    # ========================== protocols in action ========================
    def test_protocols():
        """len(), `in`, and for-loops work on ALL our structures."""
        arr = DynamicArray()
        lst = SinglyLinkedList()
        heap = MinHeap()
        for v in [3, 1, 2]:
            arr.append(v)
            lst.push_back(v)
            heap.push(v)
        for structure in (arr, lst, heap):
            name = type(structure).__name__
            check(f"len works on {name}", len(structure) == 3)
            check(f"'in' works on {name}", 2 in structure)
        check("for-loop on DynamicArray", list(arr) == [3, 1, 2])
        check("for-loop on SinglyLinkedList", list(lst) == [3, 1, 2])
        check("for-loop on MinHeap is sorted", list(heap) == [1, 2, 3])
        check("iterating did not drain heap", len(heap) == 3)


    # =============================== driver ================================
    print("Testing the library:")
    run_suite("DynamicArray", test_dynamic_array)
    run_suite("SinglyLinkedList", test_linked_list)
    run_suite("Stack + Queue", test_stack_and_queue)
    run_suite("MinHeap", test_min_heap)
    run_suite("protocols", test_protocols)

    total = results["pass"] + results["fail"]
    print(f"\n{results['pass']}/{total} checks passed", end="")
    print(" — library is healthy!" if results["fail"] == 0
          else " — fix the FAILs above.")
    ```

    Break something on purpose — flip a `<` in `_sift_down`, or delete the
    tail update in `remove` — and watch which checks catch it. A test batch
    you have *seen fail* is a test batch you can trust.

## Going further

- **BST with the full delete.** Add a `BinarySearchTree` with `insert`,
  `contains`, in-order `__iter__` (it should yield sorted values — a free
  test!), and `delete` handling all three cases from
  [20.2 BST operations](../../ch20-bst/02-bst-ops.md): leaf, one child, and
  two children via the in-order successor. The two-child case is the
  hardest ten lines in this whole project.
- **DoublyLinkedList.** Add `prev` references and O(1) `pop_back`, then
  re-run your Queue on top of it unchanged — if the adapter needs edits,
  your abstraction leaked.
- **Shrink the DynamicArray.** Halve capacity when the array drops below a
  quarter full, and prove with `resizes` that a grow-shrink-grow cycle
  doesn't thrash.
- **Benchmark it.** Use `time.perf_counter()` as in
  [16.2 Measuring running time](../../ch16-complexity/02-timing.md) to race
  your DynamicArray against the built-in `list` — then appreciate what C
  gets you.
- **Generics, Java-style.** Your structures already hold any type. Write
  the Java equivalent of `Stack<String>` in a side-by-side comparison and
  see [18.1 ADTs and generics](../../ch18-linked-lists/01-adts-generics.md)
  for why Java makes you say the type out loud.
