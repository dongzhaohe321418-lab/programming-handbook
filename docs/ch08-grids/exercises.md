# Exercises

## The chapter in brief

- A grid is just a list of lists, read `grid[row][col]` one bracket at a time —
  row first, column second, with `len(grid)` rows and `len(grid[0])` columns
  ([8.1](01-2d-arrays.md)).
- Swapping those two indexes is *the* classic grid bug: it crashes on a
  rectangular grid and silently mirrors your data on a square one.
- Build grids with nested loops or `[[0] * cols for _ in range(rows)]` — never
  `[[0] * cols] * rows`, which makes every "row" the same aliased list.
- Row sums are easy because each row *is* a list; column sums need the
  inverted loop, `c` outside and `r` inside, still reading `grid[r][c]`.
- Rows may be **ragged**, so careful code asks `len(grid[r])` instead of
  assuming `len(grid[0])` fits all — and NumPy's 2-D arrays give up that
  freedom in exchange for `shape`, `grid[r, c]`, and `sum(axis=...)`.
- A list argument is passed as a **reference**, so mutating it reaches the
  caller while rebinding it never does — and Java behaves identically, because
  it passes *references by value*: the arrow is copied, the object is shared
  ([8.2](02-arrays-functions.md)).
- The library convention is worth adopting: an in-place function returns
  `None`, and a function that returns a useful list left its argument
  untouched. Say which in the docstring.
- Linear search checks each element from the front, reports the *first* match,
  and keeps its "not found" answer *after* the loop; the worst case costs $n$
  comparisons ([8.3](03-first-algorithms.md)).
- Selection sort maintains an **invariant** — after pass $i$ the first $i+1$
  slots hold their final values — and always makes $n(n-1)/2$ comparisons,
  which is why it is $O(n^2)$ whatever the input.
- Insertion sort has the same worst case but exploits nearly sorted data; in
  real programs you call `sorted()` for a new list or `.sort()` to sort in
  place.
- A unit test is one `assert` about one fact, named for what it checks and
  building its own fresh data — and the **edges** come first: empty, single
  element, duplicates, already sorted ([8.4](04-unit-testing.md)).
- pytest and JUnit automate discovery and reporting, and test-first means red
  before green: a test you have never seen fail is decoration, not protection.

### Key terms

| Term | One-line reminder |
| --- | --- |
| [two-dimensional array](../concept-index.md#t) | a grid stored as a list (or array) whose elements are rows |
| row-major order | visiting cells top to bottom, left to right — rows on the outer loop |
| ragged grid | a grid whose rows do not all have the same length |
| [mutation vs rebinding](../concept-index.md#m) | changing the object at the end of the arrow vs re-aiming the arrow itself |
| pass references by value | the callee gets a copy of the arrow; the object itself is shared |
| [linear search](../concept-index.md#l) | check each element from the front, stopping at the first match |
| [selection sort](../concept-index.md#s) | repeatedly swap the smallest remaining value to the front |
| [insertion sort](../concept-index.md#i) | slide each new value left into place among the already-sorted ones |
| [invariant](../concept-index.md#i) | a statement true every time you check it, such as "the first $i+1$ slots are final" |
| [`assert` statement](../concept-index.md#a) | the testing atom: silent when true, `AssertionError` when false |
| [unit test](../concept-index.md#u) | one automated check of one fact about one function |
| edge case | the empty, single-element, duplicate, or already-sorted input where bugs live |
| regression | working behaviour that a later change silently breaks |

## The exercises

These exercises rehearse the whole chapter: grids, reference behaviour,
the first algorithms, and testing. Exercises 8.1 and 8.6 ask for
*predictions* — write your answer down before running anything, then
check yourself honestly.

### Exercise 8.1 — Predict the print (●)

This program prints two lines. Write both down exactly, then run it.
If your prediction was wrong, re-read
[Section 8.1](01-2d-arrays.md) on the `*` trap.

```python
row = [0, 0]
grid = [row, row, row]
grid[0][1] = 7
print(grid)
print(row)
```

??? success "Solution"

    ```python
    row = [0, 0]
    grid = [row, row, row]   # three references to the SAME list
    grid[0][1] = 7
    print(grid)              # [[0, 7], [0, 7], [0, 7]]
    print(row)               # [0, 7]
    ```

    All three "rows" of the grid are aliases of the one list named
    `row`, so writing through `grid[0]` changes what you see through
    `grid[1]`, `grid[2]`, *and* `row` itself. The independent-rows fix:
    `grid = [[0, 0] for _ in range(3)]`.

### Exercise 8.2 — Row sums and column sums (●)

For the grid below, compute and print the list of row sums and the
list of column sums. Check one of each by hand before trusting your
program.

```text
grid = [[3, 1, 4],
        [1, 5, 9],
        [2, 6, 5]]
```

??? success "Solution"

    ```python
    grid = [[3, 1, 4],
            [1, 5, 9],
            [2, 6, 5]]

    row_sums = []
    for row in grid:
        row_sums.append(sum(row))

    col_sums = []
    for c in range(len(grid[0])):
        total = 0
        for r in range(len(grid)):
            total += grid[r][c]
        col_sums.append(total)

    print("row sums   :", row_sums)   # [8, 15, 13]
    print("column sums:", col_sums)   # [6, 12, 18]
    ```

    Rows come cheap because each row *is* a list. Columns require the
    inverted nested loop — fix a column `c`, walk down the rows — since
    no list object holds a column.

### Exercise 8.3 — Diagonal sums (●●)

For a square grid, the *main diagonal* runs top-left to bottom-right
and the *anti-diagonal* top-right to bottom-left. Compute both sums for
the grid of Exercise 8.2, each with a **single** (non-nested) loop.
Hint: on the main diagonal, how are the row and column index related?
On the anti-diagonal?

??? success "Solution"

    ```python
    grid = [[3, 1, 4],
            [1, 5, 9],
            [2, 6, 5]]
    n = len(grid)

    main_diag = 0
    anti_diag = 0
    for i in range(n):
        main_diag += grid[i][i]              # row == col
        anti_diag += grid[i][n - 1 - i]      # col counts down as row counts up

    print("main diagonal:", main_diag)   # 3 + 5 + 5 = 13
    print("anti diagonal:", anti_diag)   # 4 + 5 + 2 = 11
    ```

    The insight is turning a geometric pattern into an index relation:
    main diagonal cells satisfy $c = r$; anti-diagonal cells satisfy
    $c = n - 1 - r$. One index variable then drives both.

### Exercise 8.4 — Two ways to double (●●)

Write both `doubled(values)` (returns a **new** list, argument
untouched) and `double_in_place(values)` (mutates, returns `None`).
Demonstrate with prints that the first leaves its argument alone and
the second changes it. Which docstring convention from
[Section 8.2](02-arrays-functions.md) does each follow?

??? success "Solution"

    ```python
    def doubled(values):
        """Return a NEW list with each element doubled."""
        result = []
        for v in values:
            result.append(v * 2)
        return result

    def double_in_place(values):
        """Double each element of values itself. Returns None."""
        for i in range(len(values)):
            values[i] *= 2

    a = [1, 2, 3]
    print(doubled(a))    # [2, 4, 6]
    print(a)             # [1, 2, 3]  — untouched

    double_in_place(a)
    print(a)             # [2, 4, 6]  — mutated
    ```

    `doubled` builds and returns a fresh list (and would keep working
    if its first line copied nothing — it never writes to `values`).
    `double_in_place` writes through the shared reference with
    `values[i] *= 2`, so the caller's list changes; following
    convention, it returns `None`.

### Exercise 8.5 — Implement and test `reverse_in_place` (●●)

Write `reverse_in_place(values)`: it reverses the list **in place**
(no new list, return `None`) by swapping elements pairwise from the
two ends toward the middle. Then write a mini-suite in the style of
[Section 8.4](04-unit-testing.md): tests for the empty list, a single
element, an even length, and an odd length, plus a driver that reports
pass/fail counts.

??? success "Solution"

    ```python
    def reverse_in_place(values):
        """Reverse values in place. Returns None."""
        left = 0
        right = len(values) - 1
        while left < right:
            values[left], values[right] = values[right], values[left]
            left += 1
            right -= 1

    def test_empty():
        data = []
        reverse_in_place(data)
        assert data == []

    def test_single():
        data = [7]
        reverse_in_place(data)
        assert data == [7]

    def test_even_length():
        data = [1, 2, 3, 4]
        reverse_in_place(data)
        assert data == [4, 3, 2, 1]

    def test_odd_length():
        data = [1, 2, 3, 4, 5]
        reverse_in_place(data)
        assert data == [5, 4, 3, 2, 1]

    def run_tests():
        tests = [test_empty, test_single, test_even_length, test_odd_length]
        passed = failed = 0
        for test in tests:
            try:
                test()
            except AssertionError:
                failed += 1
                print("FAIL ", test.__name__)
            else:
                passed += 1
                print("ok   ", test.__name__)
        print(f"{passed} passed, {failed} failed")

    run_tests()
    ```

    The two-pointer swap meets in the middle: for even lengths the
    pointers cross, for odd lengths they land on the middle element,
    which needs no swap — and `while left < right` handles both, plus
    the empty and single-element edges, with no special cases.

### Exercise 8.6 — Predict the step count (●●)

Before running anything: exactly how many comparisons does selection
sort make on a **6-element** list? Does your answer change if the list
is already sorted? Write down both answers, then verify them with the
comparison-counting version from
[Section 8.3](03-first-algorithms.md).

??? success "Solution"

    ```python
    def selection_sort_counting(values):
        comparisons = 0
        n = len(values)
        for i in range(n - 1):
            min_i = i
            for j in range(i + 1, n):
                comparisons += 1
                if values[j] < values[min_i]:
                    min_i = j
            values[i], values[min_i] = values[min_i], values[i]
        return comparisons

    shuffled = [12, 3, 44, 8, 20, 1]
    already  = [1, 3, 8, 12, 20, 44]
    print("shuffled      :", selection_sort_counting(shuffled))
    print("already sorted:", selection_sort_counting(already))
    ```

    Both lines print `15`: the formula $n(n-1)/2 = 6 \times 5 / 2$
    gives 15, and sortedness makes no difference — selection sort scans
    the entire unsorted region every pass regardless of what it finds.
    (Insertion sort, by contrast, would exploit the sorted input.)

### Exercise 8.7 — Tic-tac-toe referee (●●●)

A tic-tac-toe board is a $3 \times 3$ grid of `"X"`, `"O"`, and `" "` (a
space). Write `winner(board)` that returns `"X"` or `"O"` if that
player owns three in a row — any row, any column, or either diagonal —
and `None` otherwise. Test all four cases: a row win, a column win, a
diagonal win, and a full board with no winner.

??? success "Solution"

    ```python
    def winner(board):
        """Return "X" or "O" if one has three in a row, else None."""
        lines = []
        for r in range(3):                       # the three rows
            lines.append([board[r][0], board[r][1], board[r][2]])
        for c in range(3):                       # the three columns
            lines.append([board[0][c], board[1][c], board[2][c]])
        lines.append([board[0][0], board[1][1], board[2][2]])   # main diag
        lines.append([board[0][2], board[1][1], board[2][0]])   # anti diag

        for line in lines:
            if line[0] != " " and line == [line[0]] * 3:
                return line[0]
        return None

    row_win  = [["X", "X", "X"], ["O", "O", " "], [" ", " ", " "]]
    col_win  = [["O", "X", " "], ["O", "X", " "], ["O", " ", "X"]]
    diag_win = [["X", "O", " "], ["O", "X", " "], [" ", "O", "X"]]
    no_win   = [["X", "O", "X"], ["X", "O", "O"], ["O", "X", "X"]]

    assert winner(row_win) == "X"
    assert winner(col_win) == "O"
    assert winner(diag_win) == "X"
    assert winner(no_win) is None
    print("all referee tests pass")
    ```

    The clean strategy: instead of eight tangled `if`s, *collect* all
    eight possible lines into a list of lists, then judge every line
    with the same two-part test — first cell isn't blank, and all three
    cells equal the first. The `line[0] != " "` guard matters: three
    blanks match each other but crown no winner.

### Exercise 8.8 — Transpose (●●●)

The *transpose* of a grid swaps rows with columns: cell
$(r, c)$ moves to $(c, r)$, so a $2 \times 3$ grid becomes
$3 \times 2$. Write `transpose(grid)` returning a **new** grid, and
verify that `transpose([[1, 2, 3], [4, 5, 6]])` equals
`[[1, 4], [2, 5], [3, 6]]`. Beware the aliasing trap when creating the
result.

??? success "Solution"

    ```python
    def transpose(grid):
        """Return a new grid with rows and columns swapped."""
        rows = len(grid)
        cols = len(grid[0])
        result = [[0] * rows for _ in range(cols)]   # cols x rows, fresh rows
        for r in range(rows):
            for c in range(cols):
                result[c][r] = grid[r][c]
        return result

    original = [[1, 2, 3],
                [4, 5, 6]]
    flipped = transpose(original)
    print(flipped)                    # [[1, 4], [2, 5], [3, 6]]
    assert flipped == [[1, 4], [2, 5], [3, 6]]
    assert original == [[1, 2, 3], [4, 5, 6]]   # untouched
    print("transpose test passes")
    ```

    Two details carry all the difficulty. The result's dimensions are
    *swapped* — `cols` rows of `rows` cells — and it must be built with
    the comprehension, not `[[0] * rows] * cols`, or every output row
    would be the same aliased list. The copy line `result[c][r] =
    grid[r][c]` is the whole algorithm: indexes swapped, nothing else.
