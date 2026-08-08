# Chapter 36 · Exercises

## The chapter in brief

- A hash table does not search for a key, it **computes the key's address** —
  which is why its cost never learns how many keys are stored
  ([36.1](01-hash-tables.md)).
- A good hash function is **deterministic, uniform, fast, and avalanching**,
  and a plain sum of character codes fails three of those four.
- Uniformity is measurable: chi-squared should land near $m$, and about
  $m e^{-n/m}$ buckets should come out empty.
- The **table size** is half the design — a power of two keeps only the low
  bits, so either use a prime or stir the bits first.
- A key's hash must never change while it is stored, which is why only
  immutable objects are hashable and why `__eq__` and `__hash__` must be
  written together.
- **Collisions are certain and they arrive early**: a million-bucket table
  collides after about 1178 keys, at 0.1% full
  ([36.2](02-collisions-resizing.md)).
- Cost depends on the **load factor** $\alpha = n/m$ and on nothing else, so
  resizing — grow, then rehash every key — is what turns "depends on $\alpha$"
  into $O(1)$.
- Open addressing must delete with a **tombstone**; clearing the slot strands
  every key whose probe sequence ran through it.
- Doubling makes insertion **amortized $O(1)$**, because the total pairs moved
  stays under $2n$ — though one insert in a few thousand is expensive.
- Adversarial keys turn $O(1)$ into $O(n)$ — **hash flooding** — which is why
  CPython randomizes string hashing and Java tree-ifies long chains.
- A **trie** stores the key as a *path*, making every operation $O(L)$ in the
  query length, independent of $n$, and prefix queries nearly free
  ([36.3](03-tries.md)).
- Deleting from a trie prunes only nodes that are **childless and unmarked**,
  and the climb stops at the first node that fails that test.
- A **skip list** reaches $O(\log n)$ *expected* with coin flips instead of
  rotations, trusting its own randomness rather than the input's
  ([36.4](04-skip-lists.md)).

### Key terms

| Term | What it means |
| --- | --- |
| [hash function](../concept-index.md#h) | turns any key into an integer; a modulo turns that into a slot |
| [hash table](../concept-index.md#h) | a direct-address table with a hash function in front |
| [collision](../concept-index.md#c) | two keys landing in one bucket — legal, unavoidable, handled |
| [load factor](../concept-index.md#l) | $\alpha = n/m$, the only number a hash table's cost depends on |
| [separate chaining](../concept-index.md#s) | one list per bucket; degrades gently, costs pointers |
| [open addressing](../concept-index.md#o) | every entry inside the table, collisions resolved by probing |
| primary clustering | linear probing's runs of occupied slots, which grow at both ends |
| [tombstone](../concept-index.md#t) | a "deleted, keep probing" marker that keeps a probe sequence intact |
| [amortized cost](../appendix/B-big-o.md) | the average per operation over a long run, even when one is expensive |
| hash flooding | an attack that feeds a server deliberately colliding keys |
| [trie](../concept-index.md#t) | tree where the key is spelled by the path, one character per edge |
| radix tree (PATRICIA) | trie with single-child chains collapsed into one labelled edge |
| [skip list](../concept-index.md#s) | stacked sorted linked lists with coin-flipped express lanes |
| update array | the per-level predecessors a skip-list splice needs |

Now put it to work. Hashing rewards arithmetic on paper: work out the bucket,
then check the machine. Tries and skip lists reward drawing the structure
before touching the keyboard. The first three exercises are pencil-first on
purpose, the middle four are repairs and measurements, and the last one is a
small engineering project that combines two chapters' worth of structures into
the cache that sits in front of half the software you use.

### Exercise 36.1 — Bucket arithmetic by hand ●

A hash table has **12 buckets** and uses the weak hash from
[36.1](01-hash-tables.md): `weak_hash(s) = sum(ord(c) for c in s)`.

Work out on paper, before running anything, which bucket each of these keys
lands in, and whether any two of them collide:

`"ada"`, `"bob"`, `"cy"`, `"dee"`, `"eve"`

Useful codes: `a`=97, `b`=98, `c`=99, `d`=100, `e`=101, `o`=111, `v`=118,
`y`=121.

??? success "Solution"

    | key | sum | $\bmod 12$ |
    |---|---|---|
    | `"ada"` | $97+100+97 = 294$ | 6 |
    | `"bob"` | $98+111+98 = 307$ | 7 |
    | `"cy"` | $99+121 = 220$ | 4 |
    | `"dee"` | $100+101+101 = 302$ | 2 |
    | `"eve"` | $101+118+101 = 320$ | 8 |

    No two of these collide — five keys, five different buckets. That is
    luck, not design: with 5 keys in 12 buckets the birthday formula puts
    the chance of *some* collision at about 62%, so a clean table like this
    one is the minority outcome.

    ```python
    def weak_hash(s):
        return sum(ord(c) for c in s)

    buckets = [[] for _ in range(12)]
    for key in ["ada", "bob", "cy", "dee", "eve"]:
        i = weak_hash(key) % 12
        buckets[i].append(key)
        print(f"{key:<5} sum {weak_hash(key):>4}  ->  bucket {i:>2}")

    print("\nchain lengths:", [len(b) for b in buckets])
    print("any collisions:", any(len(b) > 1 for b in buckets))
    ```

    The lesson is the method, not the answer: *hash, then modulo, then look
    only in that one bucket.*

### Exercise 36.2 — Find the bug in a hash function ●

A colleague wrote this and reports that their hash table "gets slow with a
few thousand keys, but the tests all pass".

```python
def hash_word(word):
    h = 7
    for ch in word:
        h = 31 * ord(ch)
    return h
```

**Predict before running:** over a list of 20 five-letter English words, how
many distinct values will `hash_word` produce? Then find the bug, fix it,
and measure both versions.

??? success "Solution"

    The accumulator is thrown away. The line should be
    `h = 31 * h + ord(ch)`; as written, each pass *overwrites* `h`, so after
    the loop `h` is `31 * ord(word[-1])` — the hash depends on the **last
    character only**. There are at most 26 possible outputs no matter how
    many words you feed it, so the table degenerates into 26 long chains.

    The tests pass because the function is still deterministic and the table
    still returns correct answers: a bad hash costs *speed*, never
    correctness, which is exactly why this class of bug survives review.

    ```python
    def hash_word(word):          # BROKEN
        h = 7
        for ch in word:
            h = 31 * ord(ch)
        return h

    def hash_word_fixed(word):    # the accumulator is kept
        h = 7
        for ch in word:
            h = (31 * h + ord(ch)) & 0xFFFFFFFF
        return h

    words = ("apple bread chair dance eagle flame grape house ivory joker "
             "knife lemon maple night ocean paper queen river stone table").split()

    print("words:", len(words))
    print("broken -> distinct hashes:", len(set(hash_word(w) for w in words)))
    print("fixed  -> distinct hashes:", len(set(hash_word_fixed(w) for w in words)))

    for name, fn in (("broken", hash_word), ("fixed", hash_word_fixed)):
        counts = [0] * 8
        for w in words:
            counts[fn(w) % 8] += 1
        print(f"{name:<7} 8 buckets -> {counts}, fullest {max(counts)}")
    ```

    ```text
    words: 20
    broken -> distinct hashes: 6
    fixed  -> distinct hashes: 20
    broken  8 buckets -> [0, 0, 3, 10, 2, 0, 4, 1], fullest 10
    fixed   8 buckets -> [0, 3, 1, 2, 5, 3, 4, 2], fullest 5
    ```

    Twenty words, **six** distinct hashes — the six distinct final letters —
    and one bucket holding half the dictionary. The fixed version gives 20
    distinct hashes and a fullest bucket of 5.

    A second, subtler version of the same bug is `for ch in word[:4]` — a
    "performance optimisation" that makes every URL beginning `http` hash
    identically. Any hash that ignores part of the key ignores part of the
    key's information.

### Exercise 36.3 — Predict the collisions ●●

**Predict before running.** A hash table has 16 buckets and a good,
uniformly distributed hash function.

1. You insert 4 keys. What is the probability that at least two share a
   bucket?
2. How many keys can you insert before that probability passes 50%?
3. Your table has a million buckets. Same question — how many keys before a
   collision is more likely than not?

Write your three guesses down, then compute them with the birthday formula
from [36.2](02-collisions-resizing.md).

??? success "Solution"

    Most people guess far too high on all three. The answers are **33%**,
    **5 keys**, and **1178 keys** — the last one on a table that is
    0.1% full.

    ```python
    import math

    def p_collision(k, m):
        clear = 1.0
        for i in range(k):
            clear *= (m - i) / m
        return 1 - clear

    print("m = 16:")
    for k in (2, 4, 6, 8):
        print(f"   {k} keys -> P(collision) = {p_collision(k, 16):.3f}")

    for m in (16, 1_000_000):
        k = 1
        while p_collision(k, m) < 0.5:
            k += 1
        print(f"m = {m:>9}: 50% is passed at {k:>5} keys "
              f"(1.177*sqrt(m) = {1.1774 * math.sqrt(m):.0f})")
    ```

    The rule of thumb worth memorising is $k \approx 1.177\sqrt{m}$: the
    number of keys before a collision grows only with the **square root** of
    the table size. Any design that assumes "the table is big, so collisions
    are rare" is wrong.

### Exercise 36.4 — Repair a table that deletes without tombstones ●●

This open-addressed table works perfectly until something is deleted.

```python
class BrokenTable:
    def __init__(self, capacity=8):
        self.slots = [None] * capacity

    def put(self, key):
        i = key % len(self.slots)
        while self.slots[i] is not None:
            if self.slots[i] == key:
                return
            i = (i + 1) % len(self.slots)
        self.slots[i] = key

    def find(self, key):
        i = key % len(self.slots)
        while self.slots[i] is not None:
            if self.slots[i] == key:
                return True
            i = (i + 1) % len(self.slots)
        return False

    def remove(self, key):
        i = key % len(self.slots)
        while self.slots[i] is not None:
            if self.slots[i] == key:
                self.slots[i] = None       # <-- the bug
                return True
            i = (i + 1) % len(self.slots)
        return False
```

Insert 5, 13, 21 (all with home slot 5), delete 13, and show that `find(21)`
now fails. Then fix `remove` so that it does not. Your fixed table must
still let a later insertion reuse the freed space.

??? success "Solution"

    Deleting must leave a **tombstone**: a marker meaning "keep probing".
    Searches walk past it; insertions may overwrite it.

    ```python
    TOMB = object()                       # unique marker, distinct from None

    class FixedTable:
        def __init__(self, capacity=8):
            self.slots = [None] * capacity

        def put(self, key):
            m = len(self.slots)
            i = key % m
            first_tomb = None
            while self.slots[i] is not None:
                if self.slots[i] is TOMB:
                    if first_tomb is None:
                        first_tomb = i    # remember, but keep checking
                elif self.slots[i] == key:
                    return                # already present
                i = (i + 1) % m
            self.slots[first_tomb if first_tomb is not None else i] = key

        def find(self, key):
            m = len(self.slots)
            i = key % m
            while self.slots[i] is not None:
                if self.slots[i] is not TOMB and self.slots[i] == key:
                    return True
                i = (i + 1) % m           # walks straight past a tombstone
            return False

        def remove(self, key):
            m = len(self.slots)
            i = key % m
            while self.slots[i] is not None:
                if self.slots[i] is not TOMB and self.slots[i] == key:
                    self.slots[i] = TOMB
                    return True
                i = (i + 1) % m
            return False

        def layout(self):
            return ["." if s is None else "X" if s is TOMB else str(s)
                    for s in self.slots]

    t = FixedTable()
    for k in (5, 13, 21):
        t.put(k)
    print("after inserts :", t.layout())
    print("find(21):", t.find(21))

    t.remove(13)
    print("after remove  :", t.layout())
    print("find(13):", t.find(13), "  find(21):", t.find(21), "<- still found")

    t.put(29)                             # 29 % 8 == 5: reuses the tombstone
    print("after put(29) :", t.layout())
    print("find(29):", t.find(29), " find(21):", t.find(21))
    ```

    Note the detail in `put`: it remembers the *first* tombstone but keeps
    probing to the end of the cluster, because the key might already be
    stored further along. Writing into the tombstone immediately would
    create a duplicate.

### Exercise 36.5 — Prefix counting on a trie ●●

Add `count_with_prefix(prefix)` to the trie from [36.3](03-tries.md):
how many stored words begin with `prefix`? The obvious implementation
collects the whole subtree and takes its length, which costs time
proportional to the number of answers. Do better: make it $O(L)$, the length
of the prefix, no matter how many words match.

??? success "Solution"

    Store a counter on every node: how many words *pass through* it. Insert
    increments the counter on each node along the path, delete decrements.
    Then the answer is one walk down and one field read.

    ```python
    class CountingTrieNode:
        __slots__ = ("children", "is_word", "passing")
        def __init__(self):
            self.children = {}
            self.is_word = False
            self.passing = 0          # words that go through this node

    class CountingTrie:
        def __init__(self):
            self.root = CountingTrieNode()

        def insert(self, word):
            node = self.root
            path = [node]
            for ch in word:
                node = node.children.setdefault(ch, CountingTrieNode())
                path.append(node)
            if node.is_word:
                return False          # duplicate: do not double-count
            node.is_word = True
            for n in path:
                n.passing += 1        # includes the root: total word count
            return True

        def count_with_prefix(self, prefix):
            node = self.root
            for ch in prefix:
                node = node.children.get(ch)
                if node is None:
                    return 0
            return node.passing       # O(len(prefix)), whatever the answer

        def collect(self, prefix):    # the slow way, for cross-checking
            node = self.root
            for ch in prefix:
                node = node.children.get(ch)
                if node is None:
                    return []
            out = []
            def dfs(n, suffix):
                if n.is_word:
                    out.append(prefix + "".join(suffix))
                for ch in sorted(n.children):
                    suffix.append(ch)
                    dfs(n.children[ch], suffix)
                    suffix.pop()
            dfs(node, [])
            return out

    words = ("program programming programmer project promise property "
             "protocol prototype process print python path pattern "
             "package parse parser param").split()
    t = CountingTrie()
    for w in words:
        t.insert(w)
    t.insert("program")               # duplicate must not be counted twice

    print(f"{'prefix':<10}{'count':>7}{'matches agree?':>17}")
    for prefix in ("p", "pr", "pro", "prog", "pa", "par", "pz", ""):
        n = t.count_with_prefix(prefix)
        print(f"{prefix!r:<10}{n:>7}{str(n == len(t.collect(prefix))):>17}")
    ```

    ```text
    prefix      count   matches agree?
    'p'            17             True
    'pr'           10             True
    'pro'           9             True
    'prog'          3             True
    'pa'            6             True
    'par'           3             True
    'pz'            0             True
    ''             17             True
    ```

    The empty prefix returns the size of the whole trie for free, which is a
    neat way to see that `passing` on the root is just `len()`. Supporting
    deletion means decrementing the same counters and pruning nodes whose
    `passing` reaches zero.

### Exercise 36.6 — Prove that trie lookup ignores $n$ ●●

Claim: a trie lookup costs $O(L)$ in the length of the *query*, and does not
depend on how many words the trie holds. Design and run an experiment that
tests it. Your experiment should hold the query length fixed, grow the
dictionary by at least a factor of ten, and report a per-lookup time.

Predict first: over a 10× growth in dictionary size, by what factor will the
lookup time change?

??? success "Solution"

    The prediction is **1×** — no change at all — and the measurement should
    land within noise of that. Fix the query length, vary $n$, time the same
    lookups.

    ```python
    import random, string, time

    class TrieNode:
        __slots__ = ("children", "is_word")
        def __init__(self):
            self.children, self.is_word = {}, False

    def build(words):
        root = TrieNode()
        for w in words:
            node = root
            for ch in w:
                nxt = node.children.get(ch)
                if nxt is None:
                    nxt = TrieNode()
                    node.children[ch] = nxt
                node = nxt
            node.is_word = True
        return root

    def search(root, word):
        node = root
        for ch in word:
            node = node.children.get(ch)
            if node is None:
                return False
        return node.is_word

    rng = random.Random(7)
    pool = set()
    while len(pool) < 20_000:
        pool.add("".join(rng.choice(string.ascii_lowercase) for _ in range(6)))
    pool = sorted(pool)

    print(f"{'n words':>9}{'lookup (us)':>13}{'x first row':>13}")
    baseline = None
    for n in (200, 2_000, 20_000):
        words = pool[:n]
        root = build(words)
        probes = [words[i * (n // 4)] for i in range(4)]   # all length 6
        R = 4000
        t0 = time.perf_counter()
        for _ in range(R):
            for p in probes:
                search(root, p)
        per = (time.perf_counter() - t0) / (R * 4) * 1e6
        baseline = baseline or per
        print(f"{n:>9}{per:>13.3f}{per / baseline:>12.2f}x")
    ```

    A hundredfold growth in the dictionary, and the lookup column does not
    move: six characters in, six dictionary lookups, out. Contrast a sorted
    list, where the same experiment would show binary search growing with
    $\log n$, and a plain list, where it would grow with $n$.

### Exercise 36.7 — Hand-trace a skip-list search ●●

Here is a skip list, printed with the `render()` helper from
[36.4](04-skip-lists.md) (`H` is the header, `.` means "this key is not in
this lane"):

```text
L2:   H   .   .   .  25   .   .  58   .   .   .
L1:   H   .   .  14  25  31   .  58   .   .  84
L0:   H   3   9  14  25  31  41  58  62  77  84
```

On paper, trace `search(41)`. Write down, in order, every step right and
every drop. How many key comparisons does it make? Then do the same for
`search(50)`, which is not present.

??? success "Solution"

    `search(41)`: start at the header on L2.

    | at | level | next key | decision |
    |---|---|---|---|
    | H | 2 | 25 | $25 < 41$ → step right |
    | 25 | 2 | 58 | $58 \not< 41$ → drop |
    | 25 | 1 | 31 | $31 < 41$ → step right |
    | 31 | 1 | 58 | $58 \not< 41$ → drop |
    | 31 | 0 | 41 | $41 \not< 41$ → drop |
    | 31 | — | 41 | next node is 41 → **found** |

    Five comparisons. `search(50)` takes the identical route as far as L0
    and then goes one step further: 41 < 50, so it steps right to 41; 58 is
    not < 50, so it stops; the next node is 58, which is not 50 — **not
    found**, six comparisons. Both searches make five or six comparisons
    where the plain sorted linked list of [36.4](04-skip-lists.md) needed
    six for 41 and seven for 50, and the gap widens with $n$.

    ```python
    import random

    class SkipNode:
        __slots__ = ("key", "value", "forward")
        def __init__(self, key, value, level):
            self.key, self.value = key, value
            self.forward = [None] * (level + 1)

    class SkipList:
        def __init__(self, seed=136, p=0.5, max_level=16):
            self.p, self.max_level = p, max_level
            self.header = SkipNode(None, None, max_level)
            self.level, self._size = 0, 0
            self.rng = random.Random(seed)
            self.comparisons = 0

        def random_level(self):
            level = 0
            while self.rng.random() < self.p and level < self.max_level:
                level += 1
            return level

        def _predecessors(self, key):
            update = [self.header] * (self.max_level + 1)
            node = self.header
            for i in range(self.level, -1, -1):
                nxt = node.forward[i]
                while nxt is not None and nxt.key < key:
                    self.comparisons += 1
                    node = nxt
                    nxt = node.forward[i]
                if nxt is not None:
                    self.comparisons += 1
                update[i] = node
            return update, node.forward[0]

        def insert(self, key, value):
            update, candidate = self._predecessors(key)
            if candidate is not None and candidate.key == key:
                candidate.value = value
                return False
            level = self.random_level()
            if level > self.level:
                for i in range(self.level + 1, level + 1):
                    update[i] = self.header
                self.level = level
            node = SkipNode(key, value, level)
            for i in range(level + 1):
                node.forward[i] = update[i].forward[i]
                update[i].forward[i] = node
            self._size += 1
            return True

        def search(self, key):
            _, candidate = self._predecessors(key)
            return candidate is not None and candidate.key == key

    sl = SkipList(seed=136)
    for k in [3, 9, 14, 25, 31, 41, 58, 62, 77, 84]:
        sl.insert(k, k)

    for target in (41, 50):
        before = sl.comparisons
        found = sl.search(target)
        print(f"search({target}): found={found!s:<5} "
              f"comparisons={sl.comparisons - before}")
    ```

### Exercise 36.8 — An LRU cache from a dict and a doubly linked list ●●●

A **least-recently-used cache** holds at most `capacity` items. Reading or
writing a key marks it as most recently used; when the cache is full, the
*least* recently used item is evicted. Every operation must be $O(1)$ — no
scanning, no sorting.

Neither structure can do this alone. A `dict` finds a key in $O(1)$ but
knows nothing about recency order. A
[doubly linked list](../ch18-linked-lists/03-doubly-linked.md) maintains an
order and can move or unlink a node in $O(1)$ — but only if you already
*have* the node, and finding it costs $O(n)$.

Combine them: the dict maps `key -> node`, and the node lives in a doubly
linked list ordered most-recently-used first.

Implement `LRUCache` with `get(key)`, `put(key, value)`, and `__len__`.
Verify that the eviction order is right and that a `get` genuinely rescues
an item from eviction.

??? success "Solution"

    Two sentinel nodes (`head` and `tail`) remove every special case: the
    list is never empty, so no `if node is None` checks are needed anywhere
    in the pointer surgery.

    ```python
    class LRUNode:
        __slots__ = ("key", "value", "prev", "next")
        def __init__(self, key=None, value=None):
            self.key, self.value = key, value
            self.prev = self.next = None

    class LRUCache:
        """dict for O(1) lookup + doubly linked list for O(1) reordering."""

        def __init__(self, capacity):
            self.capacity = capacity
            self.table = {}                      # key -> LRUNode
            self.head = LRUNode()                # sentinel: most recent side
            self.tail = LRUNode()                # sentinel: least recent side
            self.head.next = self.tail
            self.tail.prev = self.head
            self.evictions = []

        # ---- the two list primitives, both O(1)
        def _unlink(self, node):
            node.prev.next = node.next
            node.next.prev = node.prev

        def _push_front(self, node):
            node.prev = self.head
            node.next = self.head.next
            self.head.next.prev = node
            self.head.next = node

        # ---- the cache interface
        def get(self, key, default=None):
            node = self.table.get(key)
            if node is None:
                return default
            self._unlink(node)                   # touch: move to the front
            self._push_front(node)
            return node.value

        def put(self, key, value):
            node = self.table.get(key)
            if node is not None:
                node.value = value
                self._unlink(node)
                self._push_front(node)
                return
            if len(self.table) == self.capacity:
                victim = self.tail.prev          # the least recently used
                self._unlink(victim)
                del self.table[victim.key]
                self.evictions.append(victim.key)
            node = LRUNode(key, value)
            self.table[key] = node
            self._push_front(node)

        def __len__(self):
            return len(self.table)

        def __contains__(self, key):
            return key in self.table

        def order(self):
            """Keys from most to least recently used."""
            out, node = [], self.head.next
            while node is not self.tail:
                out.append(node.key)
                node = node.next
            return out


    cache = LRUCache(capacity=3)
    for key in "abc":
        cache.put(key, key.upper())
    print("after a, b, c      :", cache.order())

    print("get('a') ->", cache.get("a"), " order now:", cache.order())

    cache.put("d", "D")                          # full: evict least recent
    print("after put('d')     :", cache.order(), " evicted:", cache.evictions)
    print("'b' still cached?  :", "b" in cache, "   'a' rescued by get:",
          "a" in cache)

    cache.put("c", "C2")                         # update moves c to front
    print("after put('c','C2'):", cache.order(), " value:", cache.get("c"))

    for key in "efg":
        cache.put(key, key.upper())
    print("after e, f, g      :", cache.order())
    print("eviction order     :", cache.evictions)
    print("len:", len(cache), " capacity respected:", len(cache) <= 3)
    print("miss returns default:", cache.get("zzz", "<not cached>"))
    ```

    ```text
    after a, b, c      : ['c', 'b', 'a']
    get('a') -> A  order now: ['a', 'c', 'b']
    after put('d')     : ['d', 'a', 'c']  evicted: ['b']
    'b' still cached?  : False    'a' rescued by get: True
    after put('c','C2'): ['c', 'd', 'a']  value: C2
    after e, f, g      : ['g', 'f', 'e']
    eviction order     : ['b', 'a', 'd', 'c']
    len: 3  capacity respected: True
    miss returns default: <not cached>
    ```

    Read the third line carefully: `b` was evicted, not `a`, even though `a`
    was inserted first. The `get("a")` moved it to the front and `b` became
    the least recently used — recency, not age, is what the list tracks.

    Every operation touches a fixed number of pointers and one dictionary
    entry, so all of them are $O(1)$ — including eviction, because
    `self.tail.prev` *is* the victim; nothing has to be searched for. This
    exact pairing is what `functools.lru_cache` uses internally, what a CPU
    cache approximates in hardware, and what sits in front of most database
    query paths. It is also the classic answer to the interview question
    "design a cache", and now you have written it.

    A worthwhile extension: add a `stats()` method counting hits and misses,
    then measure the hit rate on a realistic access pattern where 20% of the
    keys receive 80% of the requests. You will find that a cache holding a
    fifth of the keys catches most of the traffic — the reason caching works
    at all.
