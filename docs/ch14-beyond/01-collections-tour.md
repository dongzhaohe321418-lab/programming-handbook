# 14.1 Sets, maps, and dictionaries

A list can hold anything, so it is tempting to hold *everything* in
lists — and to spend your life scanning them. But many programs do not
need an ordered sequence; they need "no duplicates", or "look this up by
name", or "keep these three values together". Python ships a purpose-built
collection for each of those needs, and using the right one makes code
shorter, clearer, and — as the next section will measure — dramatically
faster.

## Sets: uniqueness and instant membership

A **set** is an unordered collection with no duplicates. Build one with
braces or with `set(...)`, and duplicates simply vanish:

```python
votes = ["ada", "bob", "ada", "carol", "bob", "ada"]
voters = set(votes)              # duplicates collapse
print(len(votes), "votes from", len(voters), "distinct voters")
print(sorted(voters))            # sets are unordered — sort to display
```

The output:

```text
6 votes from 3 distinct voters
['ada', 'bob', 'carol']
```

Note the `sorted(...)` on the last line: a set has **no reliable order**,
so printing one directly can list elements differently from run to run.
When you want stable output, sort first.

The second superpower is the `in` operator. Asking `x in some_list`
scans the list item by item; asking `x in some_set` uses a hash-based
trick to jump almost straight to the answer, no matter how large the set
is. Section [14.2](02-choosing-algorithms.md) puts a stopwatch on this
difference — it is not subtle. The trick itself is called a **hash
table**, and it is not magic you have to take on faith forever:
[Section 36.1](../ch36-hashing-tries/01-hash-tables.md) has you build a
working `dict` — `get`, `put`, `remove`, `in` — out of nothing but a list
and one arithmetic idea, and
[36.2](../ch36-hashing-tries/02-collisions-resizing.md) deals with what
happens when two keys want the same slot.

Sets also support the operations you know from mathematics: union
(`|`), intersection (`&`), and difference (`-`). They turn "compare
these two groups" problems into one-liners:

```python
maya_friends = {"ali", "bo", "cam", "dre"}
liam_friends = {"bo", "cam", "eve"}

print(sorted(maya_friends & liam_friends))   # both — intersection
print(sorted(maya_friends | liam_friends))   # either — union
print(sorted(maya_friends - liam_friends))   # Maya's only — difference
```

```text
['bo', 'cam']
['ali', 'bo', 'cam', 'dre', 'eve']
['ali', 'dre']
```

One trap before moving on: `{}` is **not** an empty set.

```python
empty_braces = {}
print(type(empty_braces))        # a dict! braces default to dictionaries
print(type(set()))               # the only way to write an empty set
```

## Dictionaries: the workhorse

A **dictionary** (`dict`) maps **keys** to **values** — a phone book
maps names to numbers, a gradebook maps students to scores, a web
server maps URLs to pages. If lists are the collection you learn first,
dicts are the one working Python programmers use most.

```python
ages = {"Ada": 36, "Grace": 45}      # key: value pairs
ages["Alan"] = 41                    # add or replace
print(ages["Grace"])                 # look up by key
print(ages.get("Linus", 0))          # look up with a default
print("Ada" in ages)                 # membership tests the KEYS

for name, age in ages.items():       # iterate over pairs
    print(f"{name} is {age}")
```

```text
45
0
True
Ada is 36
Grace is 45
Alan is 41
```

Three details carry most of the day-to-day work:

- **Missing keys.** `d[key]` raises `KeyError`, while `d.get(key, default)`
  returns your fallback instead. Reach for `get` whenever absence is normal
  rather than a bug.
- **`in` checks the keys**, never the values.
- **Order is insertion order.** Since Python 3.7 a dict remembers the order
  pairs were added, which is why the loop's output is predictable. It is
  *not* sorted — sort explicitly if that is what you want.

The classic dict pattern is counting. Watch `get` do the heavy lifting:

```python
text = "the quick brown fox jumps over the lazy dog the fox"
counts = {}
for word in text.split():
    counts[word] = counts.get(word, 0) + 1   # 0 the first time we see it

for word, n in sorted(counts.items()):       # alphabetical, for display
    print(f"{word:>5}: {n}")
```

```text
brown: 1
  dog: 1
  fox: 2
jumps: 1
 lazy: 1
 over: 1
quick: 1
  the: 3
```

Read the counting line slowly: for a new word, `get` returns `0` and we
store `1`; for a repeat, `get` returns the running count and we store
one more. Ten lines of list-scanning logic, replaced by one.

Java's counterparts are `HashSet` and `HashMap`, and your Java course
will lean on them heavily:

=== "Python"

    ```python
    ages = {}
    ages["Ada"] = 36
    ages["Grace"] = 45
    print(ages.get("Alan", 0))
    print("Ada" in ages)
    print(len(ages))
    ```

=== "Java"

    ```java
    import java.util.HashMap;

    HashMap<String, Integer> ages = new HashMap<>();
    ages.put("Ada", 36);
    ages.put("Grace", 45);
    System.out.println(ages.getOrDefault("Alan", 0));
    System.out.println(ages.containsKey("Ada"));
    System.out.println(ages.size());
    ```

| Python `dict` / `set` | Java `HashMap` / `HashSet` |
| --- | --- |
| `d[k] = v` | `map.put(k, v)` |
| `d[k]` | `map.get(k)` |
| `d.get(k, default)` | `map.getOrDefault(k, default)` |
| `k in d` | `map.containsKey(k)` |
| `del d[k]` | `map.remove(k)` |
| `len(d)` | `map.size()` |
| `s.add(x)` | `set.add(x)` |
| `x in s` | `set.contains(x)` |
| `s.remove(x)` | `set.remove(x)` |

!!! info "Java corner"
    Java also ships `Properties`, a specialised string-to-string map
    traditionally used for configuration files full of lines like
    `user.language=en`. Where Java reaches for `Properties`, Python
    simply uses a `dict` of strings.

## Tuples: small immutable records

A **tuple** groups a few values that belong together — a point's
`(x, y)`, a date's `(year, month, day)` — and, unlike a list, can never
be changed after creation. That sounds like a limitation; it is actually
a feature twice over. First, **unpacking** makes tuples pleasant to use:

```python
point = (3, 4)
x, y = point                     # unpacking: one name per slot
print(f"x={x}, y={y}")

trip = ("MSP", "ORD", 344)       # a small record: origin, dest, miles
origin, dest, miles = trip
print(f"{origin} to {dest}: {miles} miles")
```

Second, immutability is what makes a tuple **hashable** — eligible to be
a dictionary key or a set element. Lists are changeable, so Python
refuses them as keys:

```python
# raises TypeError
seating = {}
seating[["1", "A"]] = "Ada Lam"      # a list can't be a dict key
```

Tuples step in exactly here. Remember the airline of
[Chapter 13](../ch13-design/03-multi-class.md)? A seat map is naturally
a dict keyed by `(row, letter)` pairs:

```python
seating = {}
seating[(1, "A")] = "Ada Lam"
seating[(2, "C")] = "Ben Osei"
print(seating.get((1, "A"), "free"))
print(seating.get((1, "B"), "free"))
```

```text
Ada Lam
free
```

And of course a tuple defends itself:

```python
# raises TypeError
point = (3, 4)
point[0] = 99        # tuples cannot be modified
```

## Choosing a collection

Three questions settle almost every case:

1. **Does order matter?**
2. **Are duplicates meaningful?**
3. **How do you look things up** — by position, by key, or by "is it there?"

| You need … | Reach for | Because |
| --- | --- | --- |
| an ordered sequence to index, slice, and grow | `list` | keeps order, allows duplicates |
| uniqueness, or fast "have we seen this?" | `set` | hash lookup, duplicates impossible |
| values found by a meaningful key | `dict` | key to value in one step |
| a small fixed record that never changes | `tuple` | immutable, unpackable, usable as a key |

When in doubt, ask what the *lookup* looks like. `scores[3]` wants a
list; `scores["Ada"]` wants a dict; `if "Ada" in finished:` wants a set;
`(row, col)` as a key wants tuples inside a dict.

## Two gifts from the standard library

Once you know the counting and grouping patterns, Python hands you both,
pre-built, in the `collections` module. `Counter` is a dict specialised
for tallying, and `defaultdict` invents a starting value the first time
a missing key appears:

```python
from collections import Counter, defaultdict

letters = Counter("mississippi")
print(letters.most_common(3))        # top three, most frequent first

by_first = defaultdict(list)         # missing key? start with []
for name in ["ada", "grace", "alan", "guido", "gina"]:
    by_first[name[0]].append(name)
for letter in sorted(by_first):
    print(letter, by_first[letter])
```

```text
[('i', 4), ('s', 4), ('p', 2)]
a ['ada', 'alan']
g ['grace', 'guido', 'gina']
```

Neither does anything you could not write yourself with `get` — they
just say it in one line instead of four. Prefer them once you recognise
the pattern; write the `get` version until you do.

!!! warning "Common mistakes"

    - **Expecting order from a set.** Sets reorder freely; printing one
      directly gives arbitrary (and run-to-run unstable) order. Sort
      before displaying: `sorted(my_set)`.
    - **`d[key]` on a key that might be absent.** That raises
      `KeyError`. If absence is an ordinary case, use
      `d.get(key, default)`.
    - **Using a list as a dict key.** `TypeError: unhashable type` —
      keys must be immutable. Convert the list to a tuple.
    - **Writing `{}` for an empty set.** `{}` is an empty *dict*; an
      empty set is spelled `set()`.
    - **Adding or removing while looping.** Mutating a dict or set
      inside a `for` loop over it raises `RuntimeError`. Loop over a
      copy (`list(d)`) or build the changes separately.

## Check your understanding

1. Why is `x in big_set` fast while `x in big_list` is slow?

    ??? success "Answer"
        A list must be scanned element by element until a match is
        found, so the work grows with the list's length. A set stores
        elements by their hash, letting Python jump (almost) directly to
        where `x` would live — roughly the same tiny cost no matter how
        big the set is.

2. What is the difference between `counts["fox"]` and
   `counts.get("fox", 0)` when `"fox"` is not in `counts`?

    ??? success "Answer"
        `counts["fox"]` raises `KeyError`; `counts.get("fox", 0)`
        returns the default `0` and leaves the dict unchanged. That
        default is what makes the one-line counting pattern work.

3. `(2, "C")` may be a dictionary key but `[2, "C"]` may not. What
   property makes the difference, and why does it matter to the dict?

    ??? success "Answer"
        The tuple is immutable and therefore hashable. A dict files each
        key by its hash; if a key could change after filing (as a list
        can), its hash would change and the dict could never find it
        again — so Python forbids unhashable keys outright.
