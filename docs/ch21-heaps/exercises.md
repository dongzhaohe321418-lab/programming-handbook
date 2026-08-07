# Exercises

Drills first — the index math and paper traces build the muscle memory that
makes the harder heap problems routine. Do the traces with pencil and paper
*before* running the verification code; the point of a trace is to catch
your mental model in the act.

### Exercise 21.1 — Family tree arithmetic ●

Without running anything, compute on paper for a 0-based heap list of
length 13: (a) the children of index 4; (b) the parent of index 9; (c) the
index of the *last* node that has at least one child. Then check yourself
with code.

??? success "Solution"

    ```python
    n = 13
    print("children of 4:", 2 * 4 + 1, "and", 2 * 4 + 2)
    print("parent of 9:  ", (9 - 1) // 2)

    # last parent: the parent of the last element (index n-1)
    print("last parent:  ", (n - 1 - 1) // 2)

    # verify: index 5 has a left child, index 6 does not
    print("left child of 5 exists:", 2 * 5 + 1 < n)
    print("left child of 6 exists:", 2 * 6 + 1 < n)
    ```

    The children of 4 are 9 and 10; the parent of 9 is 4. The last parent
    is $\lfloor (n-2)/2 \rfloor = 5$: every index after it is a leaf, a
    fact that heap-building algorithms exploit to skip half the array.

### Exercise 21.2 — Heap or not? Predict first ●

For each list below, decide *on paper* whether it is a valid min-heap, and
if not, name the offending parent–child pair. Then run the checker.

`[3, 7, 4, 8, 9, 6]` · `[3, 7, 4, 8, 6, 2]` · `[1, 2, 2, 2, 1, 2]` ·
`[10, 20, 15, 30]` · `[5, 4]`

??? success "Solution"

    ```python
    def is_min_heap(items):
        for i in range(1, len(items)):
            parent = (i - 1) // 2
            if items[parent] > items[i]:
                return False, f"items[{parent}]={items[parent]} > items[{i}]={items[i]}"
        return True, "valid"

    for lst in [[3, 7, 4, 8, 9, 6],
                [3, 7, 4, 8, 6, 2],
                [1, 2, 2, 2, 1, 2],
                [10, 20, 15, 30],
                [5, 4]]:
        ok, why = is_min_heap(lst)
        print(f"{str(lst):<22} {ok}  ({why})")
    ```

    The traps: `[3, 7, 4, 8, 6, 2]` is doubly broken — 6 (index 4) sits
    under 7 (index 1), and 2 (index 5) sits under 4 (index 2) — and the
    checker reports the first violation it meets, the 7/6 pair.
    `[1, 2, 2, 2, 1, 2]` fails because the 1 at index 4 has
    parent 2 (index 1) — duplicates are fine, but a *strictly smaller*
    child is not; `[5, 4]` fails at the root. Equal parent and child, as in
    `[1, 2, 2, 2, ...]`'s legal pairs, never violates $\le$.

### Exercise 21.3 — Trace a sift-up on paper ●●

Insert `2` into the min-heap `[1, 3, 6, 5, 4, 8, 7]`. On paper, write the
list after the append and after every swap. How many swaps happen? Then
verify with code.

??? success "Solution"

    ```python
    def sift_up(heap, i):
        while i > 0:
            parent = (i - 1) // 2
            if heap[parent] <= heap[i]:
                break
            heap[parent], heap[i] = heap[i], heap[parent]
            print(f"swap {i} <-> {parent}: {heap}")
            i = parent

    heap = [1, 3, 6, 5, 4, 8, 7]
    heap.append(2)
    print(f"appended:  {heap}")
    sift_up(heap, len(heap) - 1)
    print(f"final:     {heap}")
    ```

    Two swaps. `2` lands at index 7 (parent index 3, value 5): swap gives
    `[1, 3, 6, 2, 4, 8, 7, 5]`. Now its parent is index 1 (value 3): swap
    gives `[1, 2, 6, 3, 4, 8, 7, 5]`. Its parent is the root `1`, which is
    smaller — stop. The `6` subtree never even noticed.

### Exercise 21.4 — Trace an extract-min on paper ●●

Extract the minimum from `[2, 4, 3, 9, 5, 8]`. On paper: which value
teleports to the root, which child does it swap with at each step (and
*why that child*), and what is the final list? Verify with code.

??? success "Solution"

    ```python
    def sift_down(heap, i):
        n = len(heap)
        while True:
            left, right = 2 * i + 1, 2 * i + 2
            smallest = i
            if left < n and heap[left] < heap[smallest]:
                smallest = left
            if right < n and heap[right] < heap[smallest]:
                smallest = right
            if smallest == i:
                break
            heap[i], heap[smallest] = heap[smallest], heap[i]
            print(f"swap {i} <-> {smallest}: {heap}")
            i = smallest

    heap = [2, 4, 3, 9, 5, 8]
    minimum, heap[0] = heap[0], heap[-1]
    heap.pop()
    print(f"extracted {minimum}; start: {heap}")
    sift_down(heap, 0)
    print(f"final: {heap}")
    ```

    The last element `8` moves to the root: `[8, 4, 3, 9, 5]`. Its children
    are 4 and 3; we swap with **3** (the smaller — swapping with 4 would put
    4 above 3, breaking the heap): `[3, 4, 8, 9, 5]`. Now `8` sits at index
    2 with no children in range — done. Final: `[3, 4, 8, 9, 5]`.

### Exercise 21.5 — A max-heap validator ●●

Write `is_max_heap(items)` — every parent **$\ge$** its children — and test it
on `[9, 7, 8, 1, 5, 6]`, `[9, 7, 8, 1, 5, 10]`, and `[5, 5, 5]`. Then
answer: can a list be both a valid min-heap *and* a valid max-heap?

??? success "Solution"

    ```python
    def is_min_heap(items):
        for i in range(1, len(items)):
            if items[(i - 1) // 2] > items[i]:
                return False
        return True

    def is_max_heap(items):
        for i in range(1, len(items)):
            if items[(i - 1) // 2] < items[i]:
                return False
        return True

    print(is_max_heap([9, 7, 8, 1, 5, 6]))    # True
    print(is_max_heap([9, 7, 8, 1, 5, 10]))   # False: 10's parent is 8
    print(is_max_heap([5, 5, 5]))             # True

    # both at once?
    both = [5, 5, 5]
    print(is_min_heap(both) and is_max_heap(both))   # True!
    ```

    Yes — exactly when every parent *equals* its children, i.e. all
    elements along every parent–child edge are equal (for a heap of one
    value repeated, or any list of length $\le 1$). Both properties allow
    equality; only strict inequality in some direction rules one out.

### Exercise 21.6 — Where can the second-smallest hide? ●●

In a min-heap with all-distinct values, prove to yourself that the
second-smallest value must be a **child of the root**, then write
`second_smallest(heap)` that finds it in $O(1)$ without popping. Test on
`[1, 5, 2, 9, 7, 4, 3]`.

??? success "Solution"

    ```python
    def second_smallest(heap):
        if len(heap) < 2:
            raise ValueError("need at least two items")
        if len(heap) == 2:
            return heap[1]
        return min(heap[1], heap[2])

    print(second_smallest([1, 5, 2, 9, 7, 4, 3]))   # 2
    print(second_smallest([1, 3]))                   # 3
    ```

    Why must it be at index 1 or 2? Every node other than the root sits
    below *some* root child, and along any downward path values only grow
    (each parent < each child, since values are distinct). So any
    grandchild is bigger than the child above it — a grandchild can never
    be second-best. Only the two children of the root are candidates.

### Exercise 21.7 — Top-k the wrong way and the right way ●●

Using `heapq`, find the 3 *smallest* values in
`[42, 7, 19, 88, 3, 65, 21, 54]` two ways: (a) `heapify` the whole list and
pop three times; (b) `heapq.nsmallest`. Predict both outputs, then check
they agree. Which approach would you pick if the list had a billion items
but you could only afford to store a handful?

??? success "Solution"

    ```python
    import heapq

    data = [42, 7, 19, 88, 3, 65, 21, 54]

    heap = list(data)
    heapq.heapify(heap)
    way_a = [heapq.heappop(heap) for _ in range(3)]

    way_b = heapq.nsmallest(3, data)

    print(way_a)          # [3, 7, 19]
    print(way_b)          # [3, 7, 19]
    print(way_a == way_b)
    ```

    Both print `[3, 7, 19]`. For a billion items, (a) needs the entire list
    in memory to heapify; the size-k pattern behind `nsmallest` streams
    through holding only $k$ candidates ($O(n \log k)$ time, $O(k)$ space)
    — that's the one you want.

### Exercise 21.8 — Merge k sorted lists ●●●

You have several *already sorted* lists and want one sorted list containing
everything. Concatenate-and-sort works but ignores the head start. Do it
the classic way instead: push each list's first element into a heap as a
tuple `(value, list_index, position)`; repeatedly pop the smallest and push
the next element from the same source list. Merge
`[1, 4, 9]`, `[2, 3, 11]`, and `[0, 8, 10]`, and check the result against
`sorted()`.

??? success "Solution"

    ```python
    import heapq

    def merge_k(lists):
        heap = []
        for li, lst in enumerate(lists):
            if lst:
                heap.append((lst[0], li, 0))
        heapq.heapify(heap)

        merged = []
        while heap:
            value, li, pos = heapq.heappop(heap)
            merged.append(value)
            if pos + 1 < len(lists[li]):
                heapq.heappush(heap, (lists[li][pos + 1], li, pos + 1))
        return merged

    lists = [[1, 4, 9], [2, 3, 11], [0, 8, 10]]
    result = merge_k(lists)
    print(result)
    print(result == sorted(lists[0] + lists[1] + lists[2]))
    ```

    The heap never holds more than $k$ entries (one "front-runner" per
    list), so each of the $n$ total elements costs one pop and at most one
    push at $O(\log k)$: total $O(n \log k)$, versus $O(n \log n)$ for
    concatenate-and-sort. This is the merge engine inside external sorting
    and `heapq.merge` — and you will meet its two-list special case again
    in [merge sort](../ch22-sorting/02-merge-quick.md).
