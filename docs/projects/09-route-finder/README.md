# Project 9 · Route Finder (Graphs)

Every mapping application you have ever used is the same handful of algorithms
running over the same handful of data structures. This project builds one:
a fifteen-district city map with real coordinates and real road lengths, then
four algorithms on top of it that answer four genuinely different questions —
*fewest turns?*, *fastest?*, *fastest, without exploring the whole city?*, and
*which roads must we keep?* — finishing with a printed routing report and a
drawn map with the chosen route highlighted.

## What you'll build

One program, one map, four algorithms, and two artifacts. First the report:

```text
--- A* versus Dijkstra (both stop when the goal is settled) ---
from       to             min  Dijkstra   A*   saved
Harbour    Airport       18.2        13   11     15%
University Docks         14.7        14   10     29%
Riverside  Foundry       18.0        14   10     29%
Meadows    Market        16.8        12   11      8%
Harbour    Meadows       23.0        15   15      0%
TOTAL                                68   57     16%
```

and, one stanza out of the routing report that follows it:

```text
University -> Docks
   fastest (5 roads): University -> Cathedral -> Parkside -> Museum -> Airport -> Docks
            14.7 min, 13.6 km
   fewest hops (5): University -> Cathedral -> Market -> Station -> Foundry -> Docks
            19.0 min, 13.0 km (+4.3 min)
```

Read those four lines twice. Both routes take five roads. Both are about
thirteen and a half kilometres. One of them takes four and a half minutes
longer, because it never touches the motorway. "Shortest" was never one
question.

Second, the map itself, drawn with matplotlib: districts as dots, roads as
lines whose thickness tracks the speed limit, and the chosen route in red.

## What it exercises

- [37.1 Representing graphs](../../ch37-graphs/01-representations.md) — the
  adjacency list, built once from a plain edge table and validated.
- [37.2 Breadth-first and depth-first search](../../ch37-graphs/02-traversal.md)
  — BFS, parent pointers, and path reconstruction.
- [37.3 Shortest paths](../../ch37-graphs/03-shortest-paths.md) — Dijkstra with
  lazy deletion, and A\* with a heuristic you have to *prove* admissible.
- [37.4 Minimum spanning trees](../../ch37-graphs/04-mst.md) — Kruskal and
  union-find, answering a question shortest paths cannot.
- [Chapter 21 · Heaps and Priority Queues](../../ch21-heaps/index.md) — the
  binary heap doing the deciding inside both Dijkstra and A\*.
- [19.3 Queues](../../ch19-stacks-queues/03-queues.md) — the FIFO that makes
  BFS's fewest-hops guarantee true.
- [Chapter 12 · Writing Your Own Classes](../../ch12-classes/index.md) — one
  `RoadMap` class that owns the data and hands out neighbours.

## Milestones

### Milestone 1 — the map, and a loader that refuses bad data

**Goal:** write a `RoadMap` class built from two tables: `PLACES`, mapping a
district name to an `(x, y)` coordinate in kilometres, and `ROADS`, a list of
`(end, end, length_km, speed_kmh)` tuples. The constructor fills an adjacency
dictionary in **both** directions (roads are two-way), derives each road's
travel time as $60 \times \text{km} / \text{km/h}$ minutes, and refuses input
that cannot be real.

**Done when...** a fifteen-district map with twenty-four roads loads and
reports `48 road ends / 15 districts = 3.2 roads per district`; a road naming
an unknown district raises `ValueError`; a duplicate road raises `ValueError`;
and — the interesting check — a road whose stated length is *shorter than the
straight-line distance between its endpoints* raises `ValueError`, because no
road beats the crow.

??? tip "Hint"

    Store neighbours as a dict of dicts, so `adj[u][v]` is one lookup rather
    than a scan, and put both directions in on one line:

    ```python
    import math

    places = {"A": (0.0, 0.0), "B": (3.0, 4.0)}
    adj = {name: {} for name in places}

    def crow_km(u, v):
        (x1, y1), (x2, y2) = places[u], places[v]
        return math.hypot(x2 - x1, y2 - y1)

    for a, b, km, kmh in [("A", "B", 6.0, 50)]:
        if km < crow_km(a, b):
            raise ValueError("a road cannot be shorter than the straight line")
        adj[a][b] = adj[b][a] = (60.0 * km / kmh, km, kmh)

    print("straight line A-B:", crow_km("A", "B"), "km")
    print("the road         :", adj["A"]["B"][1], "km,",
          f"{adj['A']['B'][0]:.1f} min at {adj['A']['B'][2]} km/h")
    ```

    That validator is not decoration. Milestone 4's whole optimality
    guarantee rests on it being true of every road in the table.

### Milestone 2 — BFS for fewest hops, with the route printed

**Goal:** `fewest_hops(cmap, src, dst)` — a breadth-first search that records
a `parent` map as it goes and reconstructs the path by walking parents
backwards from the destination and reversing.

**Done when...** `Harbour` to `Meadows` comes back as a three-road route,
`University` to `Docks` as a five-road one, an unreachable destination
returns `None` rather than crashing, and the source-to-source query returns a
one-element path. Sort each vertex's neighbours before enqueuing them so two
runs never disagree about which equally-short route you get.

??? tip "Hint"

    One dictionary does two jobs — it is the `visited` set *and* the
    parent-pointer table, which is why the `if v not in parent` test is the
    only cycle protection BFS needs:

    ```python
    from collections import deque

    adj = {"A": ["B", "C"], "B": ["A", "D"], "C": ["A", "D"], "D": ["B", "C"]}

    def hops(src, dst):
        parent = {src: None}
        queue = deque([src])
        while queue:
            u = queue.popleft()
            if u == dst:
                break
            for v in sorted(adj[u]):
                if v not in parent:
                    parent[v] = u
                    queue.append(v)
        if dst not in parent:
            return None
        path, cur = [], dst
        while cur is not None:
            path.append(cur)
            cur = parent[cur]
        return path[::-1]

    print(hops("A", "D"), hops("A", "A"), hops("A", "Z"))
    ```

    Parent pointers run *backwards*, which is why the path is built and then
    reversed. Trying to walk forwards needs a child map you never built.

### Milestone 3 — Dijkstra for the fastest route, with a step trace

**Goal:** `dijkstra(cmap, src, trace=False)` returning `(dist, parent)` over
travel **times**, using `heapq` and lazy deletion — push improved distances as
new entries and discard stale pops with a `settled` set. With `trace=True` it
prints one line per settle: the step number, the district settled, its final
minutes, how many entries are still on the heap, and which neighbours
improved.

**Done when...** the trace from `Harbour` settles all fifteen districts in
non-decreasing order of distance, ends with an empty heap, and reports
`Airport` at `18.2` minutes via
`Harbour -> Old Town -> Cathedral -> Parkside -> Museum -> Airport`. Check one
number by hand against the road table; if it matches, the rest will.

??? tip "Hint"

    `heapq` pops the smallest tuple, so `(minutes, name)` orders by minutes
    and breaks ties on the name. The staleness check is not optional —
    without it every outdated entry re-relaxes its whole neighbourhood:

    ```python
    import heapq

    heap = [(0.0, "Harbour")]
    heapq.heappush(heap, (9.4, "Market"))
    heapq.heappush(heap, (4.8, "Old Town"))
    heapq.heappush(heap, (12.0, "Market"))     # a stale copy, left to rot

    settled = set()
    while heap:
        d, u = heapq.heappop(heap)
        if u in settled:
            print(f"  discard stale {u} at {d}")
            continue
        settled.add(u)
        print(f"settle {u:<9} {d:>5.1f} min")
    ```

    Floating-point minutes need a tolerance when you compare: write
    `if alt < dist[v] - 1e-9:` rather than `if alt < dist[v]:`, or a route
    that is equal-but-for-rounding will be "improved" forever.

### Milestone 4 — A\*, and the heuristic you must justify

**Goal:** one function, `best_route(cmap, src, goal, guided)`, that is
Dijkstra when `guided` is `False` and A\* when it is `True`, stopping the
moment the goal is settled and counting how many districts it expanded. The
heuristic is the straight-line distance to the goal — **converted to minutes
at the map's top speed**:

$$
h(v) = \frac{60 \cdot \lVert v - \text{goal} \rVert}{\text{fastest speed on the map}}
$$

**Done when...** A\* returns exactly the same cost as Dijkstra on every query
(assert it), a printed table reports both expansion counts and the percentage
saved, and a separate check confirms the heuristic never overestimates: run
Dijkstra *from the goal* and verify $h(v) \le \text{true}(v)$ for all fifteen
districts.

??? tip "Hint"

    The units matter more than the code. Weights are **minutes**; the crow
    flies in **kilometres**; mixing them is the classic silent A\* bug that
    [37.3](../../ch37-graphs/03-shortest-paths.md) warns about.

    ```python
    import math

    TOP_SPEED = 90          # km/h — the fastest road anywhere on the map
    crow_km = math.hypot(11 - 7, 3 - 4)        # Museum to Airport

    print(f"crow flight        : {crow_km:.2f} km")
    print(f"as minutes at 90   : {60 * crow_km / TOP_SPEED:.1f}  <- admissible")
    print(f"crow km read as min: {crow_km:.1f}  <- would OVERestimate a "
          "motorway leg")
    print("real Museum->Airport: 4.3 km at 90 km/h =",
          f"{60 * 4.3 / 90:.1f} min")
    ```

    Why $h$ is safe: any route from $v$ to the goal is at least
    $\lVert v - \text{goal} \rVert$ kilometres long (Milestone 1's validator
    guarantees that road by road), and no leg of it is driven faster than the
    top speed — so no route can take fewer minutes than $h(v)$. The same
    argument one edge at a time gives $h(u) - h(v) \le \text{minutes}(u, v)$,
    which is **consistency**, and consistency is what makes it safe to settle
    a district once and never reconsider it.

### Milestone 5 — the cheapest network to keep, with Kruskal

**Goal:** the council can only afford to resurface some of the roads, and
every district must stay reachable. That is a **minimum spanning tree** over
road *lengths* — a different weight from Milestones 3 and 4, because paving
costs kilometres, not minutes. Sort the roads by length and walk the list,
accepting an edge whenever `UnionFind.union` reports that it joined two
different components, and stopping at $V - 1$ edges.

**Done when...** the tree has exactly 14 roads for 15 districts, union-find
ends with one component, the kept roads total `34.5` of the network's `74.7`
km — 54% less tarmac — and the run reports both the cycle-closing rejection
and the fact that the early exit never examined the nine longest roads.

??? tip "Hint"

    Union-find with union by rank and path compression is about twenty lines,
    and `union` returning a boolean *is* the cycle test:

    ```python
    parent = {x: x for x in "ABCD"}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]      # path halving
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra == rb:
            return False                        # already joined: a cycle
        parent[rb] = ra
        return True

    for a, b in [("A", "B"), ("C", "D"), ("B", "D"), ("A", "C")]:
        print(f"union({a}, {b}) ->",
              "accept" if union(a, b) else "REJECT, would close a cycle")
    ```

    Do not expect the MST to contain your fastest routes. It usually will
    not: an MST minimises the *total*, and cares nothing for any individual
    journey.

### Milestone 6 — the routing report and the drawn map

**Goal:** a driver that runs several origin–destination queries and, for
each, prints the fastest route with its minutes and kilometres, plus the
fewest-hops route whenever BFS disagrees — with the time penalty spelled out.
Then draw the map: every road as a line segment between its endpoints'
coordinates, thickness scaled by speed limit, length printed at the midpoint,
districts as labelled dots, and one highlighted route on top.

**Done when...** the report shows at least three queries where fewest hops
costs real minutes (`Meadows -> Market` should cost `+7.6 min`), and the
figure has labelled axes in kilometres, an equal aspect ratio so the geometry
is honest, a legend naming the highlighted route, and every district labelled.

??? tip "Hint"

    Drawing a graph is just drawing each edge as a two-point line. Equal
    aspect ratio matters here — without it the picture stretches and the
    straight-line heuristic stops looking straight:

    ```python
    import matplotlib.pyplot as plt

    places = {"Harbour": (0, 0), "Old Town": (2, 1), "Market": (4, 0)}
    roads = [("Harbour", "Old Town", 2.4), ("Old Town", "Market", 2.3)]

    for a, b, km in roads:
        xs = [places[a][0], places[b][0]]
        ys = [places[a][1], places[b][1]]
        plt.plot(xs, ys, color="0.75", lw=2, zorder=1)
        plt.text(sum(xs) / 2, sum(ys) / 2, f"{km}", fontsize=8, ha="center")
    for name, (x, y) in places.items():
        plt.scatter([x], [y], s=60, color="#00897b", zorder=3)
        plt.annotate(name, (x, y), textcoords="offset points", xytext=(6, 5))
    plt.gca().set_aspect("equal")
    plt.xlabel("kilometres east")
    plt.ylabel("kilometres north")
    plt.title("three districts, two roads")
    ```

    `zorder` decides what covers what: roads at 1, the highlighted route at
    3, dots at 4, labels at 5. Get it wrong and your route hides under the
    grey roads.

## Reference implementation

Build it milestone by milestone; the reference is here to compare against
once your version runs.

??? success "Full reference implementation"

    ```python
    """Route Finder: one city map, four graph algorithms, one routing report."""
    import heapq
    import math
    from collections import deque

    import matplotlib.pyplot as plt

    # ====================== the map, written as data ======================
    # district -> (x, y) in kilometres east and north of the harbour
    PLACES = {
        "Harbour":    (0.0, 0.0),
        "Old Town":   (2.0, 1.0),
        "Market":     (4.0, 0.0),
        "Cathedral":  (3.0, 3.0),
        "University": (1.0, 4.0),
        "Parkside":   (5.0, 3.0),
        "Station":    (6.0, 1.0),
        "Foundry":    (8.0, 0.0),
        "Museum":     (7.0, 4.0),
        "Hillcrest":  (9.0, 6.0),
        "Riverside":  (2.0, 6.0),
        "Northgate":  (5.0, 7.0),
        "Meadows":    (8.0, 8.0),
        "Docks":     (10.0, 1.0),
        "Airport":   (11.0, 3.0),
    }

    # (end, end, road length in km, speed limit in km/h) — roads are two-way
    ROADS = [
        ("Harbour", "Old Town", 2.4, 30), ("Harbour", "University", 4.6, 40),
        ("Harbour", "Riverside", 6.5, 40), ("Old Town", "Market", 2.3, 30),
        ("Old Town", "Cathedral", 2.5, 30), ("Old Town", "University", 3.4, 30),
        ("Market", "Cathedral", 3.4, 30), ("Market", "Station", 2.4, 50),
        ("Cathedral", "Parkside", 2.2, 50), ("Cathedral", "University", 2.4, 30),
        ("University", "Riverside", 2.3, 30), ("Parkside", "Station", 2.5, 50),
        ("Parkside", "Museum", 2.4, 50), ("Parkside", "Northgate", 4.2, 30),
        ("Station", "Foundry", 2.5, 50), ("Foundry", "Docks", 2.3, 90),
        ("Foundry", "Museum", 4.3, 50), ("Museum", "Hillcrest", 2.9, 50),
        ("Museum", "Airport", 4.3, 90), ("Docks", "Airport", 2.3, 90),
        ("Hillcrest", "Meadows", 2.3, 30), ("Hillcrest", "Airport", 3.7, 50),
        ("Northgate", "Meadows", 3.3, 30), ("Northgate", "Riverside", 3.3, 30),
    ]


    class RoadMap:
        """An undirected weighted graph of districts, as adjacency lists."""

        def __init__(self, places, roads):
            self.places = dict(places)
            self.adj = {name: {} for name in places}
            self.roads = []
            for a, b, km, kmh in roads:
                for end in (a, b):
                    if end not in self.places:
                        raise ValueError(f"road to unknown district {end!r}")
                if b in self.adj[a]:
                    raise ValueError(f"duplicate road {a}-{b}")
                straight = self.crow_km(a, b)
                if km < straight - 1e-9:
                    raise ValueError(
                        f"road {a}-{b} is {km} km but the straight line is "
                        f"{straight:.2f} km — no road beats the crow")
                minutes = 60.0 * km / kmh
                self.adj[a][b] = self.adj[b][a] = (minutes, km, kmh)
                self.roads.append((a, b, km, kmh))
            self.top_speed = max(kmh for *_, kmh in self.roads)

        def crow_km(self, u, v):
            """Straight-line distance, which no route can beat."""
            (x1, y1), (x2, y2) = self.places[u], self.places[v]
            return math.hypot(x2 - x1, y2 - y1)

        def minutes(self, u, v):
            return self.adj[u][v][0]

        def km(self, u, v):
            return self.adj[u][v][1]

        def neighbours(self, v):
            """Sorted, so every run of every algorithm is reproducible."""
            return sorted(self.adj[v])

        def optimism(self, v, goal):
            """Admissible A* heuristic: crow-flight km at the top speed."""
            return 60.0 * self.crow_km(v, goal) / self.top_speed

        def route_cost(self, path):
            """(minutes, kilometres) for a list of consecutive districts."""
            return (sum(self.minutes(a, b) for a, b in zip(path, path[1:])),
                    sum(self.km(a, b) for a, b in zip(path, path[1:])))

        def __len__(self):
            return len(self.places)


    def follow(parent, target):
        """Walk parent pointers back to the source, then reverse."""
        path = []
        while target is not None:
            path.append(target)
            target = parent[target]
        return path[::-1]


    # ========================= BFS: fewest hops ===========================
    def fewest_hops(cmap, src, dst):
        """Breadth-first search: the fewest-roads route, ignoring speed."""
        parent, queue = {src: None}, deque([src])
        while queue:
            u = queue.popleft()
            if u == dst:
                return follow(parent, dst)
            for v in cmap.neighbours(u):
                if v not in parent:          # the visited set and the tree
                    parent[v] = u
                    queue.append(v)
        return None                          # unreachable


    # ===================== Dijkstra: fastest, traced ======================
    def dijkstra(cmap, src, trace=False):
        """Fastest minutes from src to every district, with lazy deletion."""
        dist = {v: math.inf for v in cmap.places}
        parent = {v: None for v in cmap.places}
        dist[src] = 0.0
        settled, heap, step = set(), [(0.0, src)], 0
        if trace:
            print(f"{'step':>4}  {'settled':<11}{'min':>6}{'heap':>6}"
                  "   improved")
        while heap:
            d, u = heapq.heappop(heap)
            if u in settled:                 # a stale entry: throw it away
                continue
            settled.add(u)
            step += 1
            improved = []
            for v in cmap.neighbours(u):
                alt = d + cmap.minutes(u, v)
                if alt < dist[v] - 1e-9:     # tolerance: these are floats
                    dist[v], parent[v] = alt, u
                    heapq.heappush(heap, (alt, v))
                    improved.append(f"{v} {alt:.0f}")
            if trace:
                print(f"{step:>4}  {u:<11}{d:>6.1f}{len(heap):>6}   "
                      f"{', '.join(improved) if improved else '-'}")
        return dist, parent


    # ================ one route, with or without a hunch ==================
    def best_route(cmap, src, goal, guided):
        """Dijkstra when guided is False, A* when True. Counts expansions."""
        g = {src: 0.0}
        parent = {src: None}
        h = cmap.optimism(src, goal) if guided else 0.0
        # (f = g + h, g, district): heapq compares f, then g, then the name —
        # all three are comparable, so a tie can never raise.
        heap = [(h, 0.0, src)]
        settled, expanded = set(), 0
        while heap:
            _f, cost, u = heapq.heappop(heap)
            if u in settled:
                continue
            settled.add(u)
            expanded += 1
            if u == goal:                    # stop the moment it is final
                return cost, follow(parent, goal), expanded
            for v in cmap.neighbours(u):
                alt = cost + cmap.minutes(u, v)
                if alt < g.get(v, math.inf) - 1e-9:
                    g[v], parent[v] = alt, u
                    guess = cmap.optimism(v, goal) if guided else 0.0
                    heapq.heappush(heap, (alt + guess, alt, v))
        return math.inf, None, expanded      # the goal is unreachable


    # ============ Kruskal + union-find: what to resurface =================
    class UnionFind:
        """Disjoint sets with union by rank and path compression."""

        def __init__(self, items):
            self.parent = {x: x for x in items}
            self.rank = {x: 0 for x in items}
            self.groups = len(self.parent)

        def find(self, x):
            root = x
            while self.parent[root] != root:
                root = self.parent[root]
            while self.parent[x] != root:            # flatten the path
                self.parent[x], x = root, self.parent[x]
            return root

        def union(self, a, b):
            """True if this joined two groups; False if it would make a cycle."""
            ra, rb = self.find(a), self.find(b)
            if ra == rb:
                return False
            if self.rank[ra] < self.rank[rb]:
                ra, rb = rb, ra
            self.parent[rb] = ra
            if self.rank[ra] == self.rank[rb]:
                self.rank[ra] += 1
            self.groups -= 1
            return True


    def kruskal(cmap):
        """Cheapest set of roads, by length, that keeps everything reachable."""
        uf = UnionFind(cmap.places)
        tree, rejected, examined = [], [], 0
        for a, b, km, kmh in sorted(cmap.roads, key=lambda r: (r[2], r[0], r[1])):
            examined += 1
            if uf.union(a, b):
                tree.append((a, b, km, kmh))
                if len(tree) == len(cmap) - 1:
                    break                    # V-1 edges: nothing else can help
            else:
                rejected.append((a, b, km))
        return tree, rejected, examined, uf.groups


    # =============================== driver ===============================
    city = RoadMap(PLACES, ROADS)
    ends = sum(len(city.adj[v]) for v in city.adj)
    print(f"Riverport: {len(city)} districts, {len(city.roads)} roads, "
          f"top speed {city.top_speed} km/h")
    print(f"           {ends} road ends / {len(city)} districts = "
          f"{ends / len(city):.1f} roads per district")

    print("\n--- Dijkstra from Harbour ---")
    dist, parent = dijkstra(city, "Harbour", trace=True)
    print("\nfastest minutes from Harbour:")
    for place in sorted(dist, key=lambda p: dist[p]):
        print(f"  {place:<11}{dist[place]:>6.1f} min   "
              f"{' -> '.join(follow(parent, place))}")

    print("\n--- is the heuristic admissible? (goal: Airport) ---")
    truth, _ = dijkstra(city, "Airport")       # undirected: truth[v] is v->goal
    gaps = [(truth[v] - city.optimism(v, "Airport"), v) for v in city.places]
    print(f"  never overestimates: {all(gap >= -1e-9 for gap, _ in gaps)}")
    print(f"  tightest guess: {min(gaps)[1]} (under by {min(gaps)[0]:.1f} min)")
    print(f"  loosest guess : {max(gaps)[1]} (under by {max(gaps)[0]:.1f} min)")

    print("\n--- A* versus Dijkstra (both stop when the goal is settled) ---")
    print(f"{'from':<11}{'to':<11}{'min':>7}{'Dijkstra':>10}{'A*':>5}{'saved':>8}")
    QUERIES = [("Harbour", "Airport"), ("University", "Docks"),
               ("Riverside", "Foundry"), ("Meadows", "Market"),
               ("Harbour", "Meadows")]
    total_plain = total_star = 0
    for src, dst in QUERIES:
        plain_cost, plain_path, plain_n = best_route(city, src, dst, guided=False)
        star_cost, star_path, star_n = best_route(city, src, dst, guided=True)
        assert abs(plain_cost - star_cost) < 1e-9, "A* must stay optimal"
        total_plain += plain_n
        total_star += star_n
        print(f"{src:<11}{dst:<11}{star_cost:>7.1f}{plain_n:>10}{star_n:>5}"
              f"{1 - star_n / plain_n:>8.0%}")
    print(f"{'TOTAL':<11}{'':<11}{'':>7}{total_plain:>10}{total_star:>5}"
          f"{1 - total_star / total_plain:>8.0%}")

    print("\n--- cheapest network to resurface (Kruskal) ---")
    tree, rejected, examined, groups = kruskal(city)
    for i in range(0, len(tree), 2):
        print(("  " + "".join(f"{a + '-' + b:<24}{km:>5.1f} km   "
                              for a, b, km, _ in tree[i:i + 2])).rstrip())
    kept = sum(km for *_, km, _ in tree)
    whole = sum(km for *_, km, _ in city.roads)
    print(f"  kept {len(tree)} roads = V - 1, leaving {groups} component")
    print(f"  rejected as cycle-closing: "
          f"{', '.join(f'{a}-{b} {km:.1f} km' for a, b, km in rejected)}")
    print(f"  examined {examined} of {len(city.roads)} roads; the early exit "
          f"never looked at the {len(city.roads) - examined} longest")
    print(f"  {kept:.1f} km resurfaced instead of {whole:.1f} km — "
          f"{1 - kept / whole:.0%} less tarmac")

    print("\n--- routing report ---")
    for src, dst in QUERIES:
        minutes, path, _ = best_route(city, src, dst, guided=True)
        _, km = city.route_cost(path)
        hops = fewest_hops(city, src, dst)
        hop_min, hop_km = city.route_cost(hops)
        print(f"{src} -> {dst}")
        print(f"   fastest ({len(path) - 1} roads): {' -> '.join(path)}")
        print(f"            {minutes:.1f} min, {km:.1f} km")
        if hops != path:
            print(f"   fewest hops ({len(hops) - 1}): {' -> '.join(hops)}")
            print(f"            {hop_min:.1f} min, {hop_km:.1f} km "
                  f"(+{hop_min - minutes:.1f} min)")
        else:
            print("   fewest hops: the same route")

    # ---------------------------- the map ---------------------------------
    HIGHLIGHT = best_route(city, "Harbour", "Airport", guided=True)[1]
    fig, ax = plt.subplots(figsize=(9, 6))
    for a, b, km, kmh in city.roads:
        xs = [city.places[a][0], city.places[b][0]]
        ys = [city.places[a][1], city.places[b][1]]
        ax.plot(xs, ys, color="0.75", lw=0.6 + kmh / 30, zorder=1)
        ax.text(sum(xs) / 2, sum(ys) / 2, f"{km:.1f}", fontsize=6,
                color="0.45", ha="center", va="center", zorder=2)
    ax.plot([city.places[p][0] for p in HIGHLIGHT],
            [city.places[p][1] for p in HIGHLIGHT],
            color="crimson", lw=3, alpha=0.75, zorder=3,
            label="fastest Harbour to Airport")
    ax.scatter([p[0] for p in city.places.values()],
               [p[1] for p in city.places.values()],
               s=60, color="#00897b", zorder=4)
    for name, (x, y) in city.places.items():
        ax.annotate(name, (x, y), textcoords="offset points", xytext=(6, 5),
                    fontsize=8, zorder=5)
    ax.set_xlabel("kilometres east of the harbour")
    ax.set_ylabel("kilometres north of the harbour")
    ax.set_title("Riverport road map — edge labels are road lengths in km")
    ax.legend(loc="upper left")
    ax.margins(0.10)
    ax.set_aspect("equal")
    ax.grid(alpha=0.25)
    fig.tight_layout()
    ```

    The full run prints this. Compare it against yours line by line — a
    routing bug hides beautifully inside a plausible-looking route.

    ```text
    Riverport: 15 districts, 24 roads, top speed 90 km/h
               48 road ends / 15 districts = 3.2 roads per district

    --- Dijkstra from Harbour ---
    step  settled       min  heap   improved
       1  Harbour       0.0     3   Old Town 5, Riverside 10, University 7
       2  Old Town      4.8     4   Cathedral 10, Market 9
       3  University    6.9     3   -
       4  Market        9.4     3   Station 12
       5  Riverside     9.8     3   Northgate 16
       6  Cathedral     9.8     3   Parkside 12
       7  Station      12.3     3   Foundry 15
       8  Parkside     12.4     3   Museum 15
       9  Foundry      15.3     3   Docks 17
      10  Museum       15.3     4   Airport 18, Hillcrest 19
      11  Northgate    16.4     4   Meadows 23
      12  Docks        16.8     3   -
      13  Airport      18.2     2   -
      14  Hillcrest    18.8     1   -
      15  Meadows      23.0     0   -

    fastest minutes from Harbour:
      Harbour       0.0 min   Harbour
      Old Town      4.8 min   Harbour -> Old Town
      University    6.9 min   Harbour -> University
      Market        9.4 min   Harbour -> Old Town -> Market
      Riverside     9.8 min   Harbour -> Riverside
      Cathedral     9.8 min   Harbour -> Old Town -> Cathedral
      Station      12.3 min   Harbour -> Old Town -> Market -> Station
      Parkside     12.4 min   Harbour -> Old Town -> Cathedral -> Parkside
      Foundry      15.3 min   Harbour -> Old Town -> Market -> Station -> Foundry
      Museum       15.3 min   Harbour -> Old Town -> Cathedral -> Parkside -> Museum
      Northgate    16.4 min   Harbour -> Riverside -> Northgate
      Docks        16.8 min   Harbour -> Old Town -> Market -> Station -> Foundry -> Docks
      Airport      18.2 min   Harbour -> Old Town -> Cathedral -> Parkside -> Museum -> Airport
      Hillcrest    18.8 min   Harbour -> Old Town -> Cathedral -> Parkside -> Museum -> Hillcrest
      Meadows      23.0 min   Harbour -> Riverside -> Northgate -> Meadows

    --- is the heuristic admissible? (goal: Airport) ---
      never overestimates: True
      tightest guess: Airport (under by 0.0 min)
      loosest guess : Riverside (under by 11.5 min)

    --- A* versus Dijkstra (both stop when the goal is settled) ---
    from       to             min  Dijkstra   A*   saved
    Harbour    Airport       18.2        13   11     15%
    University Docks         14.7        14   10     29%
    Riverside  Foundry       18.0        14   10     29%
    Meadows    Market        16.8        12   11      8%
    Harbour    Meadows       23.0        15   15      0%
    TOTAL                                68   57     16%

    --- cheapest network to resurface (Kruskal) ---
      Cathedral-Parkside        2.2 km   Docks-Airport             2.3 km
      Foundry-Docks             2.3 km   Hillcrest-Meadows         2.3 km
      Old Town-Market           2.3 km   University-Riverside      2.3 km
      Cathedral-University      2.4 km   Harbour-Old Town          2.4 km
      Market-Station            2.4 km   Parkside-Museum           2.4 km
      Old Town-Cathedral        2.5 km   Station-Foundry           2.5 km
      Museum-Hillcrest          2.9 km   Northgate-Meadows         3.3 km
      kept 14 roads = V - 1, leaving 1 component
      rejected as cycle-closing: Parkside-Station 2.5 km
      examined 15 of 24 roads; the early exit never looked at the 9 longest
      34.5 km resurfaced instead of 74.7 km — 54% less tarmac

    --- routing report ---
    Harbour -> Airport
       fastest (5 roads): Harbour -> Old Town -> Cathedral -> Parkside -> Museum -> Airport
                18.2 min, 13.8 km
       fewest hops: the same route
    University -> Docks
       fastest (5 roads): University -> Cathedral -> Parkside -> Museum -> Airport -> Docks
                14.7 min, 13.6 km
       fewest hops (5): University -> Cathedral -> Market -> Station -> Foundry -> Docks
                19.0 min, 13.0 km (+4.3 min)
    Riverside -> Foundry
       fastest (5 roads): Riverside -> University -> Cathedral -> Parkside -> Station -> Foundry
                18.0 min, 11.9 km
       fewest hops (4): Riverside -> Northgate -> Parkside -> Museum -> Foundry
                23.0 min, 14.2 km (+5.0 min)
    Meadows -> Market
       fastest (5 roads): Meadows -> Hillcrest -> Museum -> Parkside -> Station -> Market
                16.8 min, 12.5 km
       fewest hops (4): Meadows -> Northgate -> Parkside -> Cathedral -> Market
                24.4 min, 13.1 km (+7.6 min)
    Harbour -> Meadows
       fastest (3 roads): Harbour -> Riverside -> Northgate -> Meadows
                23.0 min, 13.1 km
       fewest hops: the same route
    ```

    Four things in that output repay a second look.

    **The `Harbour -> Meadows` row of the A\* table saves nothing at all.**
    Fifteen expansions with the heuristic, fifteen without. Meadows sits in
    the far north-east corner and the only routes to it are long; by the time
    A\* has a candidate at 23 minutes, every other district's $f$ is below
    that, so every district gets settled anyway. This is the honest shape of
    the result: **a heuristic helps in proportion to how well it predicts**,
    and on a fifteen-node map with one goal in a corner it sometimes predicts
    nothing useful. Scale the map to ten thousand intersections and the same
    heuristic saves orders of magnitude — which is why every real router uses
    it.

    **`University -> Docks` goes east past the Airport and doubles back.**
    The fastest route leaves the Docks' own side of the city, takes the
    90 km/h motorway, and comes back. Dijkstra found it because it prices
    minutes; BFS could not, because it prices roads.

    **The MST contains almost none of the fast roads and both motorway
    legs.** Foundry–Docks and Docks–Airport are in it because they are short,
    not because they are quick — and Parkside–Station, a perfectly good
    2.5 km road, is rejected because by the time Kruskal reaches it both ends
    are already connected through Cathedral.

    **`Harbour -> Airport` is the same route for both questions.** When the
    fewest-hops route happens to also be fastest, nothing is wrong — it just
    means the map's geometry and its speed limits agree for once.

## Going further

- **One-way streets and turn restrictions.** Make `ROADS` directed by adding
  a flag, and stop writing `adj[b][a]` for one-way entries. Everything except
  the MST still works unchanged — Dijkstra and BFS never assumed symmetry —
  which is itself the lesson: minimum spanning trees are *defined* only for
  undirected graphs, as [37.4](../../ch37-graphs/04-mst.md) warns. Turn
  restrictions ("no left turn from Market into Station") need a bigger idea:
  make the vertices *(district, arrived-from)* pairs, so a turn becomes an
  edge and can simply be omitted.
- **Time-dependent weights.** Give each road a rush-hour multiplier and make
  `minutes(u, v, at_time)` take a departure time. Dijkstra still works
  provided the network is **FIFO** — leaving later can never get you there
  earlier — and quietly breaks if it is not. Print the same five queries at
  08:00 and at 22:00 and watch the routes change.
- **Bidirectional search.** Run two Dijkstras, one forward from the source
  and one backward from the goal, and stop when their settled sets touch. On
  a road network this roughly halves the explored area; the subtlety is the
  stopping rule, because the first shared district is *not* necessarily on
  the best route.
- **k-shortest paths.** Yen's algorithm finds the second-, third-, and
  fourth-best routes by repeatedly banning one edge of the best route and
  re-running the search. Offer the driver three options with their times, the
  way a real navigation app does.
- **Grow the map.** Generate a 60×60 grid of intersections with random
  speeds, then re-run the A\*-versus-Dijkstra table. The savings column
  stops being single digits — this is where the heuristic earns its keep, and
  where the expansion counts finally make the point on their own.
- **Betweenness, cheaply.** Run BFS from every district and count how often
  each one appears on a shortest route. The winner is the district whose
  closure would hurt most — the same computation that ranks routers in a
  network and junctions in a city.
