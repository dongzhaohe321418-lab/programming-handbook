# Exercises

Every one of these is a pointer-surgery drill: **draw the before/after
picture first**, number the assignments, and only then code. Exercises reuse
this minimal setup — paste it mentally in front of every solution:

```python
class Node:
    def __init__(self, value):
        self.value = value
        self.next = None

def build(values):
    """Build a chain from a Python list; return the head (or None)."""
    head = None
    for v in reversed(values):
        node = Node(v)
        node.next = head
        head = node
    return head

def show(head):
    parts = []
    while head is not None:
        parts.append(str(head.value))
        head = head.next
    return " -> ".join(parts) + " -> None" if parts else "(empty)"

print(show(build([1, 2, 3])))
```

### Exercise 18.1 — Predict the aliases ●

Without running it, predict all three printed lines. The lesson is that
node variables are references, not copies.

```text
a = Node(1)
b = Node(2)
a.next = b
c = a.next        # what does c refer to?
c.value = 20
print(b.value)
b.next = Node(3)
print(a.next.next.value)
print(a.next is c)
```

??? success "Solution"

    ```python
    class Node:
        def __init__(self, value):
            self.value = value
            self.next = None

    a = Node(1)
    b = Node(2)
    a.next = b
    c = a.next
    c.value = 20
    print(b.value)
    b.next = Node(3)
    print(a.next.next.value)
    print(a.next is c)
    ```

    Prints `20`, `3`, `True`: `c = a.next` makes `c` a second name for the
    *same* node object as `b`, so every change through one name is visible
    through all of them.

### Exercise 18.2 — Length by walking ●

Write `length(head)` that counts the nodes by traversal (no `_size`
attribute allowed). It must return `0` for an empty chain
(`length(None)`).

??? success "Solution"

    ```python
    class Node:
        def __init__(self, value):
            self.value = value
            self.next = None

    def build(values):
        head = None
        for v in reversed(values):
            node = Node(v)
            node.next = head
            head = node
        return head

    def length(head):
        count = 0
        walker = head
        while walker is not None:
            count += 1
            walker = walker.next
        return count

    print(length(build([10, 20, 30])))
    print(length(build([])))
    print(length(build([7])))
    ```

    Prints `3`, `0`, `1` — the standard traversal with a counter, and
    `None` in means the loop body never runs, giving `0` for free.

### Exercise 18.3 — insert_after: draw, then code ●●

Write `insert_after(node, value)` that splices a new node holding `value`
immediately after `node`. Draw the before/after picture first, decide
which of the two assignments must come first, and explain why in a
comment. Then insert `15` after the `10` in `10 -> 20 -> 30`.

??? success "Solution"

    ```python
    class Node:
        def __init__(self, value):
            self.value = value
            self.next = None

    def build(values):
        head = None
        for v in reversed(values):
            node = Node(v)
            node.next = head
            head = node
        return head

    def show(head):
        parts = []
        while head is not None:
            parts.append(str(head.value))
            head = head.next
        return " -> ".join(parts) + " -> None" if parts else "(empty)"

    def insert_after(node, value):
        fresh = Node(value)
        fresh.next = node.next   # step 1: aim fresh at node's old successor
        node.next = fresh        # step 2: only now re-aim node at fresh

    head = build([10, 20, 30])
    insert_after(head, 15)
    print(show(head))
    ```

    Prints `10 -> 15 -> 20 -> 30 -> None`. Step 1 must run first: it reads
    `node.next` while it still holds the old successor. Swapped, `fresh.next`
    would read the already-updated `node.next` and aim `fresh` at itself.

### Exercise 18.4 — Delete the last node ●●

Write `delete_last(head)` that removes the final node and returns the (new)
head. Handle three cases: empty chain, single node, longer chain — for the
last one you must stop the walk at the *second-to-last* node. Why can't a
singly linked list do this in $O(1)$ even with a `tail` reference?

??? success "Solution"

    ```python
    class Node:
        def __init__(self, value):
            self.value = value
            self.next = None

    def build(values):
        head = None
        for v in reversed(values):
            node = Node(v)
            node.next = head
            head = node
        return head

    def show(head):
        parts = []
        while head is not None:
            parts.append(str(head.value))
            head = head.next
        return " -> ".join(parts) + " -> None" if parts else "(empty)"

    def delete_last(head):
        if head is None or head.next is None:
            return None                    # empty or single node: now empty
        walker = head
        while walker.next.next is not None:   # stop at second-to-last
            walker = walker.next
        walker.next = None                 # cut the last node loose
        return head

    print(show(delete_last(build([1, 2, 3, 4]))))
    print(show(delete_last(build([7]))))
    print(show(delete_last(build([]))))
    ```

    Prints `1 -> 2 -> 3 -> None`, then `(empty)` twice. Even holding a
    `tail` reference, deletion needs the node *before* the tail to re-aim
    its `next` — and a singly linked node cannot look backwards, so a walk
    is unavoidable. (A doubly linked list fixes exactly this.)

### Exercise 18.5 — Middle in one pass ●●

Write `middle(head)` that returns the middle node's value using the
*slow/fast* trick: two walkers, one advancing one step per loop, the other
two steps. When the fast walker runs off the end, the slow one stands at
the middle. Test on chains of odd length 5 and even length 6 (for even
length, return the second of the two middles).

??? success "Solution"

    ```python
    class Node:
        def __init__(self, value):
            self.value = value
            self.next = None

    def build(values):
        head = None
        for v in reversed(values):
            node = Node(v)
            node.next = head
            head = node
        return head

    def middle(head):
        slow = fast = head
        while fast is not None and fast.next is not None:
            slow = slow.next        # 1 step
            fast = fast.next.next   # 2 steps
        return slow.value

    print(middle(build([1, 2, 3, 4, 5])))
    print(middle(build([1, 2, 3, 4, 5, 6])))
    ```

    Prints `3` and `4`: the fast walker covers ground twice as quickly, so
    it reaches the end exactly when the slow walker reaches the middle —
    one pass, no length count needed.

### Exercise 18.6 — Reverse a linked list ●●

Write `reverse(head)` that reverses the chain *in place* (re-aim the
existing `next` references; build no new nodes) and returns the new head.
You will need three walkers: `prev`, `cur`, and a saved `nxt` — draw one
loop iteration before coding, and mind the order: save `cur.next` before
overwriting it.

??? success "Solution"

    ```python
    class Node:
        def __init__(self, value):
            self.value = value
            self.next = None

    def build(values):
        head = None
        for v in reversed(values):
            node = Node(v)
            node.next = head
            head = node
        return head

    def show(head):
        parts = []
        while head is not None:
            parts.append(str(head.value))
            head = head.next
        return " -> ".join(parts) + " -> None" if parts else "(empty)"

    def reverse(head):
        prev = None
        cur = head
        while cur is not None:
            nxt = cur.next     # save the road ahead BEFORE overwriting it
            cur.next = prev    # flip this node's arrow backwards
            prev = cur         # advance both walkers
            cur = nxt
        return prev            # prev ends on the old last node = new head

    print(show(reverse(build([1, 2, 3, 4, 5]))))
    print(show(reverse(build([]))))
    ```

    Prints `5 -> 4 -> 3 -> 2 -> 1 -> None` and `(empty)`. Each iteration
    flips exactly one arrow; `nxt` is the safety copy that keeps the rest
    of the chain reachable — omit it and the list is destroyed after one
    step.

### Exercise 18.7 — Detect a cycle: Floyd's algorithm ●●●

If a chain's last node points back into the chain, every traversal loops
forever. Write `has_cycle(head)` using Floyd's slow/fast walkers: if there
is a cycle, the fast walker eventually laps the slow one and they meet
(`slow is fast`); if not, the fast walker hits `None`. Test on a straight
chain and on one where you deliberately link the tail back to the second
node. (Why must the comparison be `is`, not `==`?)

??? success "Solution"

    ```python
    class Node:
        def __init__(self, value):
            self.value = value
            self.next = None

    def build(values):
        head = None
        for v in reversed(values):
            node = Node(v)
            node.next = head
            head = node
        return head

    def has_cycle(head):
        slow = fast = head
        while fast is not None and fast.next is not None:
            slow = slow.next
            fast = fast.next.next
            if slow is fast:          # same OBJECT: fast lapped slow
                return True
        return False                  # fast fell off: no cycle

    straight = build([1, 2, 3, 4, 5])
    print(has_cycle(straight))

    looped = build([1, 2, 3, 4, 5])
    tail = looped
    while tail.next is not None:
        tail = tail.next
    tail.next = looped.next           # tail points back at node 2
    print(has_cycle(looped))
    ```

    Prints `False` then `True`. Inside a cycle the fast walker gains one
    node on the slow walker per iteration, so it must land exactly on it —
    and `is` is required because we mean "the same node object", not "a
    node with an equal value" (values may repeat; identity cannot).

### Exercise 18.8 — The sentinel refactor ●●●

This working function inserts a value into a *sorted* chain, but needs two
code paths — one for insertion at the front (including the empty chain),
one for everywhere else:

```text
def insert_sorted(head, value):
    fresh = Node(value)
    if head is None or value <= head.value:   # special case: new front
        fresh.next = head
        return fresh
    prev = head
    while prev.next is not None and prev.next.value < value:
        prev = prev.next
    fresh.next = prev.next
    prev.next = fresh
    return head
```

Refactor it to use a temporary **dummy head** (a sentinel for the duration
of one call): create `dummy = Node(None)` with `dummy.next = head`, run
*one* general walk-and-splice, and return `dummy.next`. Verify that
inserting into an empty chain, at the front, in the middle, and at the end
all traverse the same code path.

??? success "Solution"

    ```python
    class Node:
        def __init__(self, value):
            self.value = value
            self.next = None

    def show(head):
        parts = []
        while head is not None:
            parts.append(str(head.value))
            head = head.next
        return " -> ".join(parts) + " -> None" if parts else "(empty)"

    def insert_sorted(head, value):
        dummy = Node(None)        # temporary sentinel in front of the chain
        dummy.next = head
        prev = dummy              # prev can now NEVER be None
        while prev.next is not None and prev.next.value < value:
            prev = prev.next
        fresh = Node(value)
        fresh.next = prev.next    # the one general splice
        prev.next = fresh
        return dummy.next         # real head: whatever follows the sentinel

    head = None
    for v in [30, 10, 20, 5, 40]:     # empty, front, middle, front, end
        head = insert_sorted(head, v)
    print(show(head))
    ```

    Prints `5 -> 10 -> 20 -> 30 -> 40 -> None`. Because `prev` starts at
    the dummy, "insert at the front" is just "splice after `prev`" like
    every other case — the front-vs-middle `if` disappears, which is the
    whole sentinel argument from
    [section 18.3](03-doubly-linked.md) in miniature.
