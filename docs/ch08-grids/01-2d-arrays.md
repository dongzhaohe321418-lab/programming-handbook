# 8.1 Two-dimensional arrays

A chessboard, a spreadsheet, a pixel image, a seating chart — a huge
share of real data is naturally a **grid**: values arranged in rows and
columns. Neither Python nor Java needs a new data structure for this.
A grid is simply a list whose elements are lists — in Java, an array of
arrays. Master one new indexing habit, `grid[row][col]`, and dodge one
famous construction trap, and everything you know about lists carries
straight over.

## A grid is a list of lists

Write each row as an inner list, and collect the rows in an outer list:

```python
grid = [
    [7, 2, 9, 1],    # row 0
    [4, 8, 3, 6],    # row 1
    [5, 0, 2, 7],    # row 2
]

print(grid[1])       # one whole row
print(grid[1][3])    # one cell of that row
print(len(grid))     # number of rows
print(len(grid[0]))  # number of columns (length of a row)
```

```text
[4, 8, 3, 6]
6
3
4
```

Read `grid[1][3]` left to right, one bracket at a time: `grid[1]` picks
row 1 (the list `[4, 8, 3, 6]`), then `[3]` picks the element at index 3
*within that row* — the cell `6`. There is no magic two-dimensional
lookup, just ordinary list indexing applied twice.

=== "Python"

    ```python
    grid = [
        [7, 2, 9, 1],
        [4, 8, 3, 6],
        [5, 0, 2, 7],
    ]
    print(grid[1][3])
    ```

=== "Java"

    ```java
    int[][] grid = {
        {7, 2, 9, 1},
        {4, 8, 3, 6},
        {5, 0, 2, 7},
    };
    System.out.println(grid[1][3]);   // 6

    int[][] blank = new int[3][4];    // 3 rows x 4 cols, all zeros
    System.out.println(blank.length);      // 3 (rows)
    System.out.println(blank[0].length);   // 4 (columns)
    ```

Java's `int[][]` is literally an array whose elements are `int[]`
arrays, and `new int[3][4]` allocates three rows of four zeroed cells.

## Which index is which?

The convention in both languages: **first bracket = row, second bracket
= column**. Row numbers grow *downward*, column numbers grow *rightward*
— like reading a page, not like $(x, y)$ graph coordinates. Draw it once
and keep the picture:

```text
             col 0   col 1   col 2   col 3
row 0     [    7       2       9       1   ]
row 1     [    4       8       3       6   ]
row 2     [    5       0       2       7   ]

grid[1][3]  ->  down to row 1, across to col 3  ->  6
grid[3][1]  ->  row 3 does not exist            ->  IndexError
```

Swapping the two indexes is *the* classic grid bug. Sometimes you get
lucky and it crashes (as above); on a square grid it silently reads the
mirrored cell instead, which is far worse. When in doubt, print
`grid[r]` first — if it isn't the row you expected, your indexes are
transposed.

## Building grids

Small fixed grids come from literals, as above. To build an
$R \times C$ grid of zeros, the honest way is a pair of nested loops —
make each row from scratch, then append it:

```python
rows, cols = 3, 4

grid = []
for r in range(rows):
    row = []
    for c in range(cols):
        row.append(0)
    grid.append(row)

grid[0][0] = 99          # prove the rows are independent
print(grid)
```

```text
[[99, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
```

Only row 0 changed — exactly what we want.

### The `[[0] * cols] * rows` trap

Chapter 7 showed that `[0] * 4` builds `[0, 0, 0, 0]`, so it is very
tempting to build the whole grid the same way:

```python
grid = [[0] * 4] * 3     # looks reasonable...
grid[0][0] = 99          # change ONE cell
print(grid)              # ...but watch what happens
```

```text
[[99, 0, 0, 0], [99, 0, 0, 0], [99, 0, 0, 0]]
```

One assignment changed "all three rows" — because there is only **one
row**. The outer `* 3` does not build three lists; it copies the
*reference* to the single inner list three times, so `grid[0]`,
`grid[1]`, and `grid[2]` are three names for the same object (they are
**aliases**). The memory picture from
[Section 7.1](../ch07-arrays/01-arrays-vs-lists.md) explains it: a list
holds arrows, and `* 3` duplicated the arrow, not the thing it points
to.

### The comprehension fix

The idiomatic fix is a list comprehension whose body *runs* once per
row, manufacturing a fresh inner list each time:

```python
grid = [[0] * 4 for _ in range(3)]   # three INDEPENDENT rows
grid[0][0] = 99
print(grid)
```

```text
[[99, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
```

(`_` is a conventional name for a loop variable you never use.) The
inner `[0] * 4` is safe because the elements are plain numbers, which
you can never modify in place — only replace.

!!! tip "The rule of thumb for `*`"
    `*` is fine for a flat list of numbers, and wrong whenever the thing
    being repeated is itself a list.

## Traversing a grid

The standard traversal is **row-major**: an outer loop over rows, an
inner loop over the cells of each row — top to bottom, left to right,
like reading. Summing every cell is the accumulate pattern with a
second loop wrapped around it:

```python
grid = [
    [7, 2, 9, 1],
    [4, 8, 3, 6],
    [5, 0, 2, 7],
]

total = 0
for row in grid:            # each row is a list...
    for value in row:       # ...so loop over it like any list
        total += value

print("grid total:", total)
```

This prints `grid total: 54`. When you need *positions* — to modify
cells, or to relate cells across rows — use indexed loops instead:
`for r in range(len(grid))` outside, `for c in range(len(grid[0]))`
inside, and `grid[r][c]` in the body.

### Row sums vs column sums

Row sums are easy: each row is a list, so `sum(row)` does one row.
Column sums are the instructive case — a column is *not* stored
anywhere as a list, so you must walk down the rows collecting
`grid[r][c]` for a fixed `c`:

```python
grid = [
    [7, 2, 9, 1],
    [4, 8, 3, 6],
    [5, 0, 2, 7],
]

row_sums = []
for row in grid:
    row_sums.append(sum(row))
print("row sums   :", row_sums)

col_sums = []
for c in range(len(grid[0])):        # for each column...
    total = 0
    for r in range(len(grid)):       # ...walk down the rows
        total += grid[r][c]
    col_sums.append(total)
print("column sums:", col_sums)
```

```text
row sums   : [19, 21, 14]
column sums: [16, 10, 14, 14]
```

Check one by hand: column 0 is $7 + 4 + 5 = 16$. Notice the loops are
*inverted* for columns — `c` on the outside, `r` on the inside — and the
cell access is still `grid[r][c]`, never `grid[c][r]`.

## Ragged rows

Nothing forces every row to have the same length. A grid whose rows
differ is called **ragged** (or *jagged*), and both languages allow it:

```python
triangle = [
    [1],
    [1, 1],
    [1, 2, 1],
]

for row in triangle:
    print(len(row), row)
```

```text
1 [1]
2 [1, 1]
3 [1, 2, 1]
```

!!! info "Java corner"
    Java arrays-of-arrays can be ragged too: declare the outer array
    only, then attach rows of any length.

    ```java
    int[][] triangle = new int[3][];   // rows not yet allocated
    triangle[0] = new int[]{1};
    triangle[1] = new int[]{1, 1};
    triangle[2] = new int[]{1, 2, 1};
    ```

Ragged grids are why careful code asks `len(grid[r])` for the length of
*that particular row* rather than assuming `len(grid[0])` fits all.
When your data genuinely is rectangular, though, keep it rectangular —
most grid code assumes it.

## A NumPy 2-D preview

NumPy's arrays extend naturally to two dimensions, and for rectangular
numeric grids they are both faster and more convenient:

```python
import numpy as np

grid = np.array([
    [7, 2, 9, 1],
    [4, 8, 3, 6],
    [5, 0, 2, 7],
])

print(grid.shape)          # (rows, columns) in one tuple
print(grid[1, 2])          # one pair of brackets, comma inside
print(grid.sum())          # whole grid
print(grid.sum(axis=0))    # column sums
print(grid.sum(axis=1))    # row sums
```

```text
(3, 4)
3
54
[16 10 14 14]
[19 21 14]
```

Three luxuries to notice:

- **`shape` reports both dimensions at once**, as a single tuple.
- **Indexing takes one pair of brackets**, `grid[r, c]`, with a comma inside
  instead of `grid[r][c]`.
- **The row and column sums we hand-rolled above are one call each** —
  `axis=0` collapses the rows (summing down each column) and `axis=1`
  collapses the columns.

NumPy arrays must be rectangular — no ragged rows — which is part of how
they earn their speed.

!!! warning "Common mistakes"
    - **`[[0] * cols] * rows`.** Every "row" is the same list; writing
      one cell writes the whole column of your dreams into every row.
      Use `[[0] * cols for _ in range(rows)]`.
    - **Swapping row and column.** `grid[c][r]` crashes on
      non-square grids if you're lucky and silently mirrors the data if
      you're not. First bracket is the row. Always.
    - **Assuming rectangularity.** On a ragged grid,
      `range(len(grid[0]))` as the inner loop either misses cells or
      raises `IndexError`. Use `len(grid[r])` when rows may vary.
    - **Mixing up `len(grid)` and `len(grid[0])`.** The first is the
      row count, the second the column count. Getting them backwards
      swaps your loop bounds — another crash that only shows up on
      non-square grids.

## Check your understanding

1. For the grid `g = [[1, 2], [3, 4], [5, 6]]`, what are `len(g)`,
   `len(g[0])`, and `g[2][0]`?

    ??? success "Answer"
        `len(g)` is 3 (rows), `len(g[0])` is 2 (columns), and `g[2][0]`
        is 5 — row 2 is `[5, 6]`, and index 0 within it is 5.

2. Why does `[[""] * 3] * 2` misbehave while `["x"] * 3` is fine?

    ??? success "Answer"
        `*` copies references. For `["x"] * 3` the referenced things are
        strings, which cannot be modified in place — you can only
        *replace* a slot, which affects that slot alone. In
        `[[""] * 3] * 2` the referenced thing is a *list*, which can be
        modified in place through any of its aliases, so both "rows"
        change together.

3. To compute column sums with explicit indexes, which loop goes on the
   outside, and what expression reads each cell?

    ??? success "Answer"
        The column loop goes outside (`for c in
        range(len(grid[0]))`), the row loop inside, and each cell is
        read as `grid[r][c]` — the row index still comes first even
        though the column is fixed.

4. What does `arr.shape` return for
   `arr = np.array([[1, 2, 3], [4, 5, 6]])`, and what is `arr[0, 2]`?

    ??? success "Answer"
        `shape` is `(2, 3)` — 2 rows, 3 columns. `arr[0, 2]` is 3: row
        0 is `[1, 2, 3]` and column index 2 within it holds 3.
