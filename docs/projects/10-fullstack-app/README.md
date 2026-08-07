# Project 10 · Full-Stack Mini App

This is the portfolio piece. By the end you will have a **bookmark manager**
that runs on your own machine: a page you can open in a browser, a JSON API
behind it, validation that rejects nonsense, a file that survives a restart, a
test suite that proves it all works, and a one-command way to start the whole
thing. Nothing here is a toy simulation of a web app — it *is* a web app,
about six hundred lines of Python and one HTML file, with no framework and no
third-party packages at all.

The Run buttons on this page execute the entire back end, because the
interesting half of a web server — parsing, routing, validating, storing —
needs no network. Only the socket layer, the browser, and the build commands
have to leave the page, and each of those arrives here as a file you save and
run yourself.

## What you'll build

Six files in one folder:

```text
bookmarks/
├── bookmarks.py        the store, the validation, the router  (runs here)
├── server.py           ~50 lines of socket plumbing           (run locally)
├── index.html          the whole front end, one file          (open locally)
├── test_bookmarks.py   53 assertions over store and router    (runs here)
├── Makefile            make install / make test / make serve
└── run.sh              one command: set up, test, serve
```

The back end, driven by hand-written requests, prints the exact bytes it
would put on the wire:

```text
the request, exactly as it would arrive:
POST /bookmarks HTTP/1.1
Content-Type: application/json

{"url": "https://docs.python.org/3/library/re.html", "title": "Python re module", "tags": ["python", "regex"]}

the response, exactly as it would leave:
HTTP/1.1 201 Created
Location: /bookmarks/1
Content-Type: application/json; charset=utf-8
Content-Length: 119

{"id": 1, "url": "https://docs.python.org/3/library/re.html", "title": "Python re module", "tags": ["python", "regex"]}
```

And the suite that guards it:

```text
Testing the bookmark service:
  BookmarkStore            9 checks
  validation              13 checks
  search                   6 checks
  JSONL persistence        4 checks
  router happy paths      10 checks
  router error paths      11 checks

53/53 checks passed — ship it.
```

## What it exercises

- [42.2 HTTP and a web server from scratch](../../ch42-web-gui/02-http-server.md)
  — the request parser, the router, the response serializer, and the status
  codes, taken further here: `409`, `415`, and a `204` that carries nothing.
- [42.1 HTML and CSS](../../ch42-web-gui/01-html-css.md) and
  [42.3 JavaScript in the browser](../../ch42-web-gui/03-javascript.md) — the
  page, the layout, `fetch`, and the DOM updates.
- [41.2 Groups, greediness, and real parsing](../../ch41-regex/02-groups-parsing.md)
  — URL and tag validation, route templates compiled to named-group patterns,
  and the one line of `re.escape` that keeps user text out of your patterns.
- [11.2 Reading and writing files](../../ch11-files/02-read-write.md) — JSONL
  persistence, written and read back.
- [40.3 Make and build systems](../../ch40-toolchain/03-make.md) and
  [40.1 Bash scripting](../../ch40-toolchain/01-bash.md) — the `Makefile` and
  the `run.sh` that make the project one command to start.
- [40.4 JUnit and testing](../../ch40-toolchain/04-junit.md) and
  [8.4 Unit testing](../../ch08-grids/04-unit-testing.md) — arrange, act,
  assert, and an exit code that a build system can read.
- [10.2 Exceptions](../../ch10-exceptions/02-exceptions.md) — an exception
  type per failure mode, each mapped to exactly one status code.

## Milestones

### Milestone 1 — the data layer

**Goal:** a `Bookmark` record (`id`, `url`, `title`, `tags`) and a
`BookmarkStore` with `add`, `get`, `delete`, `all`, `search`, `save(path)`,
and `load(path)`. Persistence is **JSONL**: one JSON object per line. Ids are
assigned by the store, never by the caller, and never reused.

**Done when...** adding two bookmarks and deleting the first leaves the second
with its original id; a third gets id 3, not id 2; `save` then `load` in the
same run reproduces the records exactly; a reloaded store's next id continues
past the highest it saw; and a corrupt line makes `load` raise rather than
silently skip.

??? tip "Hint"

    JSONL is the format to reach for when you want a file you can append to,
    `grep`, and stream. Write it and read it back in one go:

    ```python
    import json

    rows = [{"id": 1, "url": "https://a.example", "tags": ["x"]},
            {"id": 2, "url": "https://b.example", "tags": []}]

    with open("demo.jsonl", "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")      # one object, one line

    with open("demo.jsonl", encoding="utf-8") as f:
        back = [json.loads(line) for line in f if line.strip()]

    print(back == rows, "->", back[1])
    ```

    One JSON *array* for the whole file would force you to rewrite the entire
    thing on every change and to hold it all in memory to read it. One object
    per line costs you nothing and buys `tail -f`, `wc -l`, and append.

### Milestone 2 — the HTTP layer

**Goal:** `parse_request(raw)` turning wire text into a `Request`, a
`Response` that serializes back to exact bytes, a `Router` that compiles
`/bookmarks/{mark_id:int}` into a named-group pattern, and `dispatch(raw)`
tying them together. Five routes: `GET`/`POST` on `/bookmarks`, `GET`/`DELETE`
on `/bookmarks/{mark_id:int}`, and `GET /bookmarks/search`.

**Done when...** a hard-coded list of raw requests prints correct wire
responses for every case: `201` with a `Location` header, `200`, `404` for a
missing id *and* for an unknown path, `405` with an `Allow` header when the
path matches but the verb does not, `400` for malformed request lines and
broken JSON, and `204` with **no body, no `Content-Type`, and no
`Content-Length`** for a successful delete.

??? tip "Hint"

    The router is one `re.sub` that rewrites a readable template into a
    pattern, exactly as [42.2](../../ch42-web-gui/02-http-server.md) does:

    ```python
    import re

    PARAM = re.compile(r"\{(\w+):int\}")

    def compile_route(template):
        return re.compile(
            "^" + PARAM.sub(lambda m: rf"(?P<{m.group(1)}>\d+)", template) + "$")

    for template in ["/bookmarks", "/bookmarks/search",
                     "/bookmarks/{mark_id:int}"]:
        print(f"{template:<28} {compile_route(template).pattern}")

    pattern = compile_route("/bookmarks/{mark_id:int}")
    for path in ["/bookmarks/42", "/bookmarks/search", "/bookmarks/42/edit"]:
        m = pattern.match(path)
        print(f"{path:<22} {m.groupdict() if m else 'no match'}")
    ```

    Look at the second line of output: `/bookmarks/search` does **not** match
    `/bookmarks/{mark_id:int}`, because `{...:int}` compiled to `\d+`. That is
    why the search route and the by-id route can coexist without any
    registration-order trickery — the type constraint disambiguates them.

### Milestone 3 — input handling with regex

**Goal:** `clean_url`, `clean_title`, and `clean_tags`, each raising
`ValidationError` with a message the client can show a human. URLs must be
`http` or `https` with a plausible dotted host; tags are 1–20 characters of
lowercase letters, digits, and hyphens, normalised and de-duplicated; titles
have their whitespace collapsed and their length capped. Then
`GET /bookmarks/search?q=…&tag=…`, doing a case-insensitive substring match
over title and URL.

**Done when...** `ftp://…`, `example.org` with no scheme, `http://localhost/x`
(no dot in the host), and a URL containing a space are all rejected with
distinct messages; `"Python"` as a tag becomes `"python"` while `"web dev"` is
rejected; searching for `.*` returns **zero** results rather than everything.

??? tip "Hint"

    That last acceptance criterion is the whole lesson. User text must be
    escaped before it becomes part of a pattern — the regex equivalent of the
    parameterised query from
    [42.2](../../ch42-web-gui/02-http-server.md)'s security section:

    ```python
    import re

    titles = ["Python docs", "Regex cheatsheet", "HTTP guide"]

    for needle in [".*", "python", "P.thon"]:
        raw = [t for t in titles if re.search(needle, t, re.IGNORECASE)]
        safe = [t for t in titles
                if re.search(re.escape(needle), t, re.IGNORECASE)]
        print(f"{needle:<8} raw pattern -> {len(raw)} hits    "
              f"escaped -> {len(safe)} hits")
    ```

    And keep the URL pattern **flat**. Anchored, no nested quantifiers, with
    the fiddly host rules in ordinary Python underneath:

    ```python
    import re

    URL_RE = re.compile(r"^https?://(?P<host>[A-Za-z0-9.-]+)"
                        r"(?::(?P<port>\d{1,5}))?(?P<rest>/[^\s]*)?$")

    for candidate in ["https://a.example/x?y=1", "http://a.example:8000/",
                      "ftp://a.example", "example.org", "https://a.example/a b"]:
        m = URL_RE.match(candidate)
        print(f"{candidate:<28} {m.groupdict() if m else 'rejected'}")
    ```

    [41.2](../../ch41-regex/02-groups-parsing.md) ends with a table saying not
    to write a mega-pattern for URLs. This one is deliberately *permissive*:
    it catches typos and wrong schemes, and leaves "does this page exist?" to
    the only authority that can answer it — fetching it.

### Milestone 4 — the front end

**Goal:** one `index.html` containing the markup, a `<style>` block, and a
`<script>` block: a form that `POST`s a new bookmark, a search box that hits
the search endpoint as you type, a list rendered from `GET /bookmarks`, and a
delete button per row. Every failure path shows a message instead of failing
silently.

**Done when...** you have saved the file, started the server from Milestone 5,
opened `http://127.0.0.1:8000/`, and added, searched for, and deleted a
bookmark — with the list updating each time and a wrong URL producing a
readable error under the form rather than a silent no-op.

The markup is three regions: a form, a search box, and an empty list the
script will fill.

```html
<form id="add-form">
  <input id="url" type="url" placeholder="https://example.org/page" required>
  <input id="title" type="text" placeholder="What is it?" required>
  <button type="submit">Add</button>
</form>

<input id="search" type="search" placeholder="Search title, URL or #tag">
<p id="status" role="status"></p>
<ul id="list"></ul>
```

The CSS is a grid for the form and a flex row per bookmark — the two layout
tools from [42.1](../../ch42-web-gui/01-html-css.md):

```css
form { display: grid; gap: .5rem; grid-template-columns: 1fr 1fr auto; }
li   { border-top: 1px solid #dfe3e8; padding: .7rem 0;
       display: flex; gap: .5rem; align-items: baseline; }
.grow { flex: 1; }
@media (max-width: 34rem) { form { grid-template-columns: 1fr; } }
```

And the JavaScript is four functions. This is the heart of it — note what
happens to a non-2xx status, and note `textContent`:

```javascript
const API = "/bookmarks";

/* fetch resolves for 404 and 500 too — the status code is our job. */
async function callApi(path, options = {}) {
  const response = await fetch(path, options);
  if (response.status === 204) return null;        // no body to parse
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.error || response.statusText);
  return payload;
}

function render(bookmarks) {
  listEl.replaceChildren();
  for (const mark of bookmarks) {
    const row = document.createElement("li");
    const link = document.createElement("a");
    link.href = mark.url;
    link.textContent = mark.title;    // textContent, never innerHTML:
    row.append(link);                 // a title of "<script>" stays text
    listEl.append(row);
  }
}
```

??? tip "Hint"

    `textContent` versus `innerHTML` is the entire cross-site-scripting
    lesson in one property name. Here is what the difference actually
    produces, modelled in Python:

    ```python
    import html

    title = '<img src=x onerror="steal(document.cookie)">'

    print("innerHTML would insert this into the page as MARKUP:")
    print("   ", title)
    print("textContent inserts this, as TEXT:")
    print("   ", html.escape(title))
    ```

    The escaped version renders as visible, harmless characters. The raw one
    is a live `<img>` tag whose `onerror` runs in every visitor's browser.
    `textContent` does the escaping for you, which is why the rule is
    *build the DOM, do not build HTML strings*.

    Two more habits worth copying from the reference file: wrap every
    `fetch` in `try`/`catch` and put the message somewhere visible, and
    **debounce** the search box with `setTimeout` so typing "python" sends
    one request rather than six.

### Milestone 5 — the real server

**Goal:** `server.py`, the socket half. It imports `dispatch` from your core,
serves `index.html` at `/`, translates each incoming request back into the raw
text your parser expects, and writes the response your `Response` object
describes. It saves the store to `bookmarks.jsonl` after every write.

**Done when...** `python server.py` starts, `http://127.0.0.1:8000/` shows the
page, the browser's network panel shows your status codes, and the app still
has your bookmarks after you stop and restart it.

Save this next to `bookmarks.py` and `index.html`. The Run button cannot
execute it — it opens a socket — which is exactly why the previous four
milestones were written so they do not need one.

```text
"""server.py — the socket half. Run this on your own machine.

The routing, validation, and storage all live in bookmarks.py and never
touch the network. This file only moves bytes and saves the file.
"""
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from bookmarks import BookmarkStore, dispatch, use_store

DATA = Path("bookmarks.jsonl")
INDEX = Path("index.html").read_bytes()
STORE = use_store(BookmarkStore.load(DATA) if DATA.exists() else BookmarkStore())


class BookmarkHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _send(self, status, body, headers):
        self.send_response(status)
        for name, value in headers.items():
            self.send_header(name, value)
        self.end_headers()
        if body:
            self.wfile.write(body)

    def _serve(self):
        if self.path in ("/", "/index.html"):
            self._send(200, INDEX, {"Content-Type": "text/html; charset=utf-8",
                                    "Content-Length": str(len(INDEX))})
            return
        length = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(length).decode("utf-8")
        raw = (f"{self.command} {self.path} HTTP/1.1\r\n"
               + "".join(f"{k}: {v}\r\n" for k, v in self.headers.items())
               + "\r\n" + body)
        response = dispatch(raw)                 # the runnable core, unchanged
        self._send(response.status, response.body.encode("utf-8"),
                   response.final_headers())
        if self.command in ("POST", "DELETE"):
            STORE.save(DATA)                     # crude, honest persistence

    do_GET = do_POST = do_DELETE = _serve

    def log_message(self, fmt, *args):
        print(f"{self.command:<7}{self.path:<28}{fmt % args}")


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    print(f"bookmarks on http://127.0.0.1:{port}   (Ctrl-C to stop)")
    ThreadingHTTPServer(("127.0.0.1", port), BookmarkHandler).serve_forever()
```

That is the whole network layer: fifty-odd lines, none of which know what a
bookmark is.

??? tip "Hint"

    Prove it works from the command line before you open a browser — `curl`
    shows you the status codes a browser hides:

    ```console
    $ python server.py &
    bookmarks on http://127.0.0.1:8000   (Ctrl-C to stop)

    $ curl -i -X POST http://127.0.0.1:8000/bookmarks \
        -H 'Content-Type: application/json' \
        -d '{"url":"https://docs.python.org/3/","title":"Python docs","tags":["python"]}'
    HTTP/1.1 201 Created
    Location: /bookmarks/1
    Content-Type: application/json; charset=utf-8
    Content-Length: 90

    {"id": 1, "url": "https://docs.python.org/3/", "title": "Python docs", "tags": ["python"]}

    $ curl -s 'http://127.0.0.1:8000/bookmarks/search?tag=python' | python -m json.tool
    $ curl -i -X DELETE http://127.0.0.1:8000/bookmarks/1 | head -1
    HTTP/1.1 204 No Content
    ```

    Serving the page from the *same* origin as the API is what lets the
    front end call `/bookmarks` with no CORS configuration at all. Open
    `index.html` as a `file://` URL instead and the browser will block every
    request — the same-origin rule from
    [42.2](../../ch42-web-gui/02-http-server.md), doing its job.

### Milestone 6 — automation

**Goal:** a `Makefile` and a `run.sh`, so that a stranger who clones the
folder can get from nothing to a running app without reading anything.

**Done when...** `make test` creates a virtual environment if needed and runs
the suite; `make serve` runs the tests *first* and only starts the server if
they pass; `make clean` removes the environment, the caches, and the data
file; and `./run.sh 8080` does the whole sequence on a port of your choosing.

```makefile
# Makefile — tab-indented recipes, as ever.
PY      := python3
VENV    := .venv
BIN     := $(VENV)/bin
PORT    ?= 8000

.PHONY: all install test serve clean

all: test

$(BIN)/python:
	$(PY) -m venv $(VENV)

install: $(BIN)/python
	$(BIN)/python -m pip install --quiet --upgrade pip
	@echo "no third-party packages needed: this app is stdlib only"

test: install
	$(BIN)/python test_bookmarks.py

serve: test
	$(BIN)/python server.py $(PORT)

clean:
	rm -rf $(VENV) __pycache__ *.jsonl
```

`serve: test` is the load-bearing line. It is not a convenience — it makes it
*impossible* to start a server whose tests fail, because the dependency graph
from [40.3](../../ch40-toolchain/03-make.md) will not let you.

And the shell version, for people who would rather not have `make` involved:

```console
#!/usr/bin/env bash
# run.sh — set up, test, and serve the bookmark app.
set -euo pipefail

PORT="${1:-8000}"
VENV=".venv"

if [ ! -d "$VENV" ]; then
    echo "==> creating $VENV"
    python3 -m venv "$VENV"
fi
"$VENV/bin/python" -m pip install --quiet --upgrade pip

echo "==> tests"
if ! "$VENV/bin/python" test_bookmarks.py; then
    echo "tests failed — not starting the server" >&2
    exit 1
fi

echo "==> serving on http://127.0.0.1:$PORT   (Ctrl-C to stop)"
exec "$VENV/bin/python" server.py "$PORT"
```

```console
$ chmod +x run.sh
$ ./run.sh 8080
==> tests
Testing the bookmark service:
  ...
53/53 checks passed — ship it.
==> serving on http://127.0.0.1:8080   (Ctrl-C to stop)
```

??? tip "Hint"

    Three details that are easy to get wrong and annoying to debug.

    **Recipe lines must start with a real tab.** Spaces give you
    `*** missing separator.  Stop.` — the single most notorious wart in
    `make`, and [40.3](../../ch40-toolchain/03-make.md) says so at length.

    **`$(BIN)/python` is a file target, not a phony one.** That is what makes
    the virtual environment build once and be skipped thereafter: it is a
    real file, so `make` compares timestamps and does nothing on the second
    run. `install`, `test`, `serve`, and `clean` are commands, so they are
    `.PHONY`.

    **`set -euo pipefail` and `exec`.** The first line stops the script at the
    first failing command, on the first undefined variable, and on a failure
    anywhere in a pipeline — see [40.1](../../ch40-toolchain/01-bash.md).
    `exec` replaces the shell with the server process so that ++ctrl+c++
    reaches Python directly instead of orphaning it.

### Milestone 7 — the tests

**Goal:** an assert-based suite over both halves — the store on its own and
the router through raw request strings — grouped into named batches that each
report how many checks they ran, ending in a pass/fail summary. The router
tests must start from a **fresh store** so they cannot depend on each other.

**Done when...** the suite reports 53 checks and every one passes, running
either through the Run button or as `python test_bookmarks.py`, exiting `0`
when green and `1` when red so `make` can tell the difference. Deliberately
break something — delete the `re.escape` call — and confirm exactly one check
turns red and names itself.

??? tip "Hint"

    Test isolation is a *design* problem before it is a testing problem. The
    handlers read a module-level `STORE`, so the tests need a supported way
    to replace it — one three-line function, and every test starts clean:

    ```python
    STORE = {"data": "the real one"}

    def use_store(store):
        """Swap the store the handlers see. This is what makes tests honest."""
        global STORE
        STORE = store
        return store

    def handler():
        return STORE["data"]

    print("before:", handler())
    use_store({"data": "a fresh empty store"})
    print("after :", handler())
    ```

    For asserting failures, a tiny helper beats a `try`/`except` in every
    test, and it is stricter than `pytest.raises` about *which* exception:

    ```python
    def raises(exc_type, fn, *args):
        try:
            fn(*args)
        except exc_type:
            return True
        except Exception:
            return False      # the WRONG exception is still a failure
        return False

    print(raises(ValueError, int, "abc"))       # True
    print(raises(TypeError, int, "abc"))        # False — wrong type
    print(raises(ValueError, int, "7"))         # False — no exception
    ```

## Reference implementation

The Python core — data layer, validation, HTTP messages, routing, and the
suite — in one runnable block, followed by the exact output.

??? success "Full reference implementation — the Python core"

    ```python
    """Bookmark manager: store, validation, router, and tests — no socket needed."""
    import json
    import re
    from dataclasses import dataclass, field
    from urllib.parse import urlsplit, parse_qs

    # ======================== layer 1: validation ============================
    URL_RE = re.compile(
        r"^https?://"                    # scheme: http or https, nothing else
        r"(?P<host>[A-Za-z0-9.-]+)"      # host: letters, digits, dots, hyphens
        r"(?::(?P<port>\d{1,5}))?"       # optional :port
        r"(?P<rest>/[^\s]*)?$"           # optional /path?query#fragment
    )
    TAG_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,19}$")


    class ValidationError(Exception):
        """The submitted bookmark is not acceptable; the message says why."""


    class Conflict(Exception):
        """This URL is already bookmarked."""


    def clean_url(raw):
        """Accept a plausible http(s) URL; reject the rest with a reason."""
        if not isinstance(raw, str) or not raw.strip():
            raise ValidationError("field 'url' is required")
        url = raw.strip()
        m = URL_RE.match(url)
        if m is None:
            raise ValidationError(f"not an http(s) URL: {url!r}")
        host = m.group("host")
        # The pattern stays flat and readable; the fiddly host rules are plain
        # Python, because a mega-pattern encoding them would be unreadable and
        # still wrong — the lesson of 41.2's "email addresses" row.
        if ("." not in host or host.startswith((".", "-"))
                or host.endswith((".", "-"))):
            raise ValidationError(f"implausible host {host!r}")
        return url


    def clean_title(raw):
        """Require a non-blank title; collapse whitespace; cap the length."""
        if not isinstance(raw, str) or not raw.strip():
            raise ValidationError("field 'title' is required")
        title = " ".join(raw.split())
        if len(title) > 120:
            raise ValidationError("title is longer than 120 characters")
        return title


    def clean_tags(raw):
        """Lowercase, de-duplicate, and enforce the tag shape."""
        if raw is None:
            return []
        if not isinstance(raw, list):
            raise ValidationError("field 'tags' must be a list")
        tags = []
        for tag in raw:
            clean = tag.strip().lower() if isinstance(tag, str) else None
            if clean is None or not TAG_RE.match(clean):
                raise ValidationError(
                    f"bad tag {tag!r}: use 1-20 lowercase letters, digits or '-'")
            if clean not in tags:
                tags.append(clean)
        return tags


    # ========================== layer 2: the store ===========================
    @dataclass
    class Bookmark:
        id: int
        url: str
        title: str
        tags: list = field(default_factory=list)

        def as_dict(self):
            return {"id": self.id, "url": self.url,
                    "title": self.title, "tags": list(self.tags)}


    class BookmarkStore:
        """An in-memory table of bookmarks that can persist itself as JSONL."""

        def __init__(self):
            self._items = {}
            self._next_id = 1

        def add(self, url, title, tags=None):
            """Validate, reject duplicates, assign an id, store. Returns the record."""
            url = clean_url(url)
            title = clean_title(title)
            tags = clean_tags(tags)
            for existing in self._items.values():
                if existing.url == url:
                    raise Conflict(f"already bookmarked as #{existing.id}")
            mark = Bookmark(self._next_id, url, title, tags)
            self._items[mark.id] = mark
            self._next_id += 1
            return mark

        def get(self, mark_id):
            return self._items.get(mark_id)

        def delete(self, mark_id):
            return self._items.pop(mark_id, None) is not None

        def all(self):
            return [self._items[k] for k in sorted(self._items)]

        def next_id(self):
            return self._next_id

        def search(self, text=None, tag=None):
            """Case-insensitive substring over title and url, plus a tag filter."""
            found = self.all()
            if text:
                needle = re.compile(re.escape(text), re.IGNORECASE)  # escape it!
                found = [m for m in found
                         if needle.search(m.title) or needle.search(m.url)]
            if tag:
                found = [m for m in found if tag.strip().lower() in m.tags]
            return found

        def save(self, path):
            """One JSON object per line — appendable, greppable, streamable."""
            with open(path, "w", encoding="utf-8") as f:
                for mark in self.all():
                    f.write(json.dumps(mark.as_dict()) + "\n")
            return path

        @classmethod
        def load(cls, path):
            """Read a JSONL file back, keeping ids and continuing the sequence."""
            store = cls()
            with open(path, encoding="utf-8") as f:
                for lineno, line in enumerate(f, start=1):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        row = json.loads(line)
                        mark = Bookmark(int(row["id"]), row["url"],
                                        row["title"], list(row["tags"]))
                    except (json.JSONDecodeError, KeyError, TypeError) as exc:
                        raise ValidationError(
                            f"{path} line {lineno}: {type(exc).__name__}") from exc
                    store._items[mark.id] = mark
                    store._next_id = max(store._next_id, mark.id + 1)
            return store

        def __len__(self):
            return len(self._items)


    # ======================= layer 3: HTTP messages ==========================
    class BadRequest(Exception):
        """The bytes on the wire are not a valid HTTP request."""


    class UnsupportedMedia(Exception):
        """Content-Type was not application/json."""


    METHODS = {"GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"}
    REASON = {200: "OK", 201: "Created", 204: "No Content", 400: "Bad Request",
              404: "Not Found", 405: "Method Not Allowed", 409: "Conflict",
              415: "Unsupported Media Type", 500: "Internal Server Error"}


    @dataclass
    class Request:
        method: str
        path: str
        query: dict
        headers: dict
        body: str

        def header(self, name, default=None):
            return self.headers.get(name.lower(), default)


    @dataclass
    class Response:
        status: int = 200
        headers: dict = field(default_factory=dict)
        body: str = ""

        def final_headers(self):
            """The headers actually sent — one place, so the socket half agrees."""
            headers = dict(self.headers)
            if self.status != 204:              # 204 must carry no body at all
                headers.setdefault("Content-Type",
                                   "application/json; charset=utf-8")
                headers["Content-Length"] = str(len(self.body.encode("utf-8")))
            return headers

        def wire(self):
            """Exactly the bytes that would go down the socket."""
            head = [f"HTTP/1.1 {self.status} {REASON.get(self.status, 'Unknown')}"]
            head += [f"{name}: {value}"
                     for name, value in self.final_headers().items()]
            return "\r\n".join(head) + "\r\n\r\n" + self.body


    def json_response(status, payload, extra=None):
        return Response(status, dict(extra or {}), json.dumps(payload))


    def parse_request(raw):
        """Raw text -> Request. Raises BadRequest on anything malformed."""
        head, _, body = raw.partition("\r\n\r\n")   # a blank line ends the headers
        lines = head.split("\r\n")
        bits = lines[0].split(" ")
        if len(bits) != 3:
            raise BadRequest(f"malformed request line: {lines[0]!r}")
        method, target, version = bits
        if method not in METHODS:
            raise BadRequest(f"unknown method {method!r}")
        if not version.startswith("HTTP/"):
            raise BadRequest(f"not an HTTP version: {version!r}")
        headers = {}
        for line in lines[1:]:
            name, sep, value = line.partition(":")
            if not sep:
                raise BadRequest(f"malformed header line: {line!r}")
            headers[name.strip().lower()] = value.strip()   # names are caseless
        url = urlsplit(target)
        return Request(method, url.path or "/",
                       {k: v[0] for k, v in parse_qs(url.query).items()},
                       headers, body)


    # ========================== layer 4: routing =============================
    PARAM = re.compile(r"\{(\w+):int\}")


    class MethodNotAllowed(Exception):
        def __init__(self, allowed):
            super().__init__(", ".join(allowed))
            self.allowed = allowed


    class Router:
        """A table of (method, path pattern) -> handler. First match wins."""

        def __init__(self):
            self.routes = []

        def route(self, method, template):
            pattern = re.compile(
                "^" + PARAM.sub(lambda m: rf"(?P<{m.group(1)}>\d+)", template) + "$")

            def register(handler):
                self.routes.append((method, pattern, handler))
                return handler
            return register                          # used as a decorator

        def resolve(self, request):
            wrong_method = set()
            for method, pattern, handler in self.routes:
                m = pattern.match(request.path)
                if m is None:
                    continue
                if method != request.method:
                    wrong_method.add(method)         # path matched, verb did not
                    continue
                return handler, {k: int(v) for k, v in m.groupdict().items()}
            if wrong_method:
                raise MethodNotAllowed(sorted(wrong_method))
            return None, None


    app = Router()
    STORE = BookmarkStore()


    def use_store(store):
        """Swap the store the handlers see. This is what makes the tests honest."""
        global STORE
        STORE = store
        return store


    def read_json(request):
        """Body -> dict, or raise the exception that names the right status."""
        kind = (request.header("content-type") or "").split(";")[0].strip()
        if kind != "application/json":
            raise UnsupportedMedia(kind)
        try:
            payload = json.loads(request.body)
        except json.JSONDecodeError as exc:
            raise ValidationError(f"invalid JSON: {exc.msg}") from exc
        if not isinstance(payload, dict):
            raise ValidationError("body must be a JSON object")
        return payload


    @app.route("GET", "/bookmarks")
    def list_bookmarks(request, params):
        return json_response(200, {"bookmarks": [m.as_dict() for m in STORE.all()]})


    @app.route("GET", "/bookmarks/search")
    def search_bookmarks(request, params):
        hits = STORE.search(request.query.get("q"), request.query.get("tag"))
        return json_response(200, {"count": len(hits),
                                   "bookmarks": [m.as_dict() for m in hits]})


    @app.route("POST", "/bookmarks")
    def create_bookmark(request, params):
        payload = read_json(request)
        mark = STORE.add(payload.get("url"), payload.get("title"),
                         payload.get("tags"))
        return json_response(201, mark.as_dict(),
                             {"Location": f"/bookmarks/{mark.id}"})


    @app.route("GET", "/bookmarks/{mark_id:int}")
    def show_bookmark(request, params):
        mark = STORE.get(params["mark_id"])
        if mark is None:
            return json_response(404, {"error": f"no bookmark #{params['mark_id']}"})
        return json_response(200, mark.as_dict())


    @app.route("DELETE", "/bookmarks/{mark_id:int}")
    def delete_bookmark(request, params):
        if not STORE.delete(params["mark_id"]):
            return json_response(404, {"error": f"no bookmark #{params['mark_id']}"})
        return Response(204)


    def dispatch(raw):
        """Wire bytes in, a Response out. Every error becomes a status code."""
        try:
            request = parse_request(raw)
        except BadRequest as exc:
            return json_response(400, {"error": str(exc)})
        try:
            handler, params = app.resolve(request)
        except MethodNotAllowed as exc:
            return json_response(405, {"error": "method not allowed"},
                                 {"Allow": ", ".join(exc.allowed)})
        if handler is None:
            return json_response(404, {"error": f"no route for {request.path}"})
        try:
            return handler(request, params)
        except UnsupportedMedia as exc:
            got = str(exc) or "nothing"
            return json_response(
                415, {"error": f"expected application/json, got {got}"})
        except ValidationError as exc:
            return json_response(400, {"error": str(exc)})
        except Conflict as exc:
            return json_response(409, {"error": str(exc)})
        except Exception as exc:                     # never leak a traceback
            return json_response(500, {"error": type(exc).__name__})


    def handle(raw):
        """The whole back end: wire bytes in, wire bytes out."""
        return dispatch(raw).wire()


    def status_of(wire):
        """The status code out of a raw response — the tests' workhorse."""
        return int(wire.split(" ")[1])


    def body_of(wire):
        return json.loads(wire.split("\r\n\r\n", 1)[1] or "null")


    def header_of(wire, name):
        for line in wire.split("\r\n\r\n")[0].split("\r\n")[1:]:
            key, _, value = line.partition(":")
            if key.strip().lower() == name.lower():
                return value.strip()
        return None


    # ============================= layer 5: tests ============================
    def run_tests():
        """An assert-style suite over the store and the router."""
        results = {"pass": 0, "fail": 0}

        def check(name, condition):
            if condition:
                results["pass"] += 1
            else:
                results["fail"] += 1
                print(f"     FAIL: {name}")

        def suite(title, fn):
            before = results["pass"] + results["fail"]
            fn()
            ran = results["pass"] + results["fail"] - before
            print(f"  {title:<22} {ran:>3} checks")

        def raises(exc_type, fn, *args, **kwargs):
            try:
                fn(*args, **kwargs)
            except exc_type:
                return True
            except Exception:
                return False
            return False

        def test_store():
            store = BookmarkStore()
            a = store.add("https://example.org/a", "  Alpha   page  ", ["Read"])
            check("ids start at 1", a.id == 1)
            check("title whitespace collapsed", a.title == "Alpha page")
            check("tags lowercased", a.tags == ["read"])
            b = store.add("https://example.org/b", "Beta", ["read", "READ", "b"])
            check("tags de-duplicated", b.tags == ["read", "b"])
            check("len tracks", len(store) == 2)
            check("get by id", store.get(1) is a and store.get(99) is None)
            check("duplicate url conflicts",
                  raises(Conflict, store.add, "https://example.org/a", "again"))
            check("delete returns True then False",
                  store.delete(2) and not store.delete(2))
            check("ids are never reused", store.add(
                "https://example.org/c", "Gamma").id == 3)

        def test_validation():
            check("ftp rejected",
                  raises(ValidationError, clean_url, "ftp://files.example/x"))
            check("bare word rejected",
                  raises(ValidationError, clean_url, "example.org"))
            check("dotless host rejected",
                  raises(ValidationError, clean_url, "http://localhost/x"))
            check("space inside url rejected",
                  raises(ValidationError, clean_url, "https://a.example/a b"))
            check("plain https accepted",
                  clean_url("  https://a.example  ") == "https://a.example")
            check("port and path accepted",
                  clean_url("http://a.example:8000/x?y=1#z")
                  == "http://a.example:8000/x?y=1#z")
            check("empty title rejected",
                  raises(ValidationError, clean_title, "   "))
            check("long title rejected",
                  raises(ValidationError, clean_title, "x" * 121))
            check("uppercase tag is normalised, not rejected",
                  clean_tags(["Python"]) == ["python"])
            check("spaced tag rejected",
                  raises(ValidationError, clean_tags, ["web dev"]))
            check("21-character tag rejected",
                  raises(ValidationError, clean_tags, ["a" * 21]))
            check("non-list tags rejected",
                  raises(ValidationError, clean_tags, "python"))
            check("missing tags means no tags", clean_tags(None) == [])

        def test_search():
            store = BookmarkStore()
            store.add("https://docs.python.org/3/", "Python docs", ["python"])
            store.add("https://example.org/regex", "Regex cheatsheet", ["regex"])
            check("search is case-insensitive", len(store.search("PYTHON")) == 1)
            check("search covers the url too", len(store.search("example.org")) == 1)
            check("tag filter works", len(store.search(tag="regex")) == 1)
            check("text and tag combine",
                  len(store.search("python", tag="regex")) == 0)
            check("no query returns everything", len(store.search()) == 2)
            check("regex metacharacters are escaped, not executed",
                  store.search(".*") == [])

        def test_persistence():
            store = BookmarkStore()
            store.add("https://a.example/1", "One", ["x"])
            store.add("https://a.example/2", "Two")
            store.delete(1)
            store.save("test_bookmarks.jsonl")
            back = BookmarkStore.load("test_bookmarks.jsonl")
            check("round trip preserves records",
                  [m.as_dict() for m in back.all()]
                  == [m.as_dict() for m in store.all()])
            check("ids survive the round trip", back.get(2) is not None)
            check("next id continues past the highest", back.next_id() == 3)
            with open("broken.jsonl", "w", encoding="utf-8") as f:
                f.write('{"id": 1, "url": "https://a.example", "title": "ok",'
                        ' "tags": []}\n')
                f.write("{ not json at all }\n")
            check("a corrupt line is reported, not swallowed",
                  raises(ValidationError, BookmarkStore.load, "broken.jsonl"))

        def test_router():
            use_store(BookmarkStore())
            body = json.dumps({"url": "https://a.example/x", "title": "X",
                               "tags": ["t"]})
            created = handle(f"POST /bookmarks HTTP/1.1\r\n"
                             f"Content-Type: application/json\r\n\r\n{body}")
            check("POST returns 201", status_of(created) == 201)
            check("POST sets Location",
                  header_of(created, "Location") == "/bookmarks/1")
            check("POST echoes the record", body_of(created)["url"]
                  == "https://a.example/x")
            check("GET one returns 200",
                  status_of(handle("GET /bookmarks/1 HTTP/1.1\r\n\r\n")) == 200)
            check("GET missing returns 404",
                  status_of(handle("GET /bookmarks/77 HTTP/1.1\r\n\r\n")) == 404)
            listed = handle("GET /bookmarks HTTP/1.1\r\n\r\n")
            check("GET list returns the one record",
                  len(body_of(listed)["bookmarks"]) == 1)
            found = handle("GET /bookmarks/search?q=a.example HTTP/1.1\r\n\r\n")
            check("search endpoint is not swallowed by /bookmarks/{id}",
                  status_of(found) == 200 and body_of(found)["count"] == 1)
            deleted = handle("DELETE /bookmarks/1 HTTP/1.1\r\n\r\n")
            check("DELETE returns 204", status_of(deleted) == 204)
            check("204 carries no body and no Content-Length",
                  deleted.endswith("\r\n\r\n")
                  and header_of(deleted, "Content-Length") is None)
            check("DELETE twice returns 404",
                  status_of(handle("DELETE /bookmarks/1 HTTP/1.1\r\n\r\n")) == 404)

        def test_error_paths():
            use_store(BookmarkStore())
            json_hdr = "Content-Type: application/json\r\n"
            cases = [
                (400, f"POST /bookmarks HTTP/1.1\r\n{json_hdr}\r\n{{oops}}"),
                (400, f'POST /bookmarks HTTP/1.1\r\n{json_hdr}\r\n{{"url": '
                      '"ftp://a.example", "title": "no"}'),
                (400, f'POST /bookmarks HTTP/1.1\r\n{json_hdr}\r\n{{"url": '
                      '"https://a.example", "title": ""}'),
                (400, f'POST /bookmarks HTTP/1.1\r\n{json_hdr}\r\n[1, 2, 3]'),
                (415, "POST /bookmarks HTTP/1.1\r\n"
                      "Content-Type: text/plain\r\n\r\nhello"),
                (415, "POST /bookmarks HTTP/1.1\r\n\r\n{}"),
                (404, "GET /favourites HTTP/1.1\r\n\r\n"),
                (400, "GIMME /bookmarks RIGHT-NOW\r\n\r\n"),
                (400, "GET /bookmarks HTTP/1.1\r\nHost example.org\r\n\r\n"),
            ]
            for expected, raw in cases:
                got = status_of(handle(raw))
                check(f"{raw.splitlines()[0][:34]!r} -> {expected}",
                      got == expected)
            wrong_verb = handle("PUT /bookmarks HTTP/1.1\r\n\r\n")
            check("wrong verb is 405, not 404", status_of(wrong_verb) == 405)
            check("405 names the allowed verbs",
                  header_of(wrong_verb, "Allow") == "GET, POST")

        print("Testing the bookmark service:")
        suite("BookmarkStore", test_store)
        suite("validation", test_validation)
        suite("search", test_search)
        suite("JSONL persistence", test_persistence)
        suite("router happy paths", test_router)
        suite("router error paths", test_error_paths)
        total = results["pass"] + results["fail"]
        print(f"\n{results['pass']}/{total} checks passed", end="")
        print(" — ship it." if results["fail"] == 0 else " — fix the FAILs above.")
        return results


    # ============================== the driver ===============================
    def show(raw):
        """Print a request's first line and the exact bytes that come back."""
        print("--> " + raw.split("\r\n")[0])
        print(handle(raw).replace("\r\n", "\n"))
        print()


    def show_summary(raw):
        """For long bodies: the status line plus a readable digest."""
        wire = handle(raw)
        print("--> " + raw.split("\r\n")[0])
        print("   " + wire.split("\r\n")[0])
        payload = body_of(wire)
        for mark in payload["bookmarks"]:
            print(f"    #{mark['id']} {mark['title']:<20} {mark['tags']}")
        print(f"    ({payload['count']} hits)\n")


    JSON = "Content-Type: application/json\r\n"
    SEED = [
        ("https://docs.python.org/3/library/re.html", "Python re module",
         ["python", "regex"]),
        ("https://developer.mozilla.org/en-US/docs/Web/HTTP", "MDN HTTP guide",
         ["http", "web"]),
        ("https://www.gnu.org/software/make/manual/", "GNU Make manual",
         ["make", "build"]),
        ("https://docs.python.org/3/library/http.server.html", "http.server docs",
         ["python", "http"]),
    ]

    use_store(BookmarkStore())
    print("=" * 70)
    print("1. creating bookmarks — the raw bytes both ways")
    print("=" * 70)
    first = json.dumps({"url": SEED[0][0], "title": SEED[0][1],
                        "tags": SEED[0][2]})
    first_raw = f"POST /bookmarks HTTP/1.1\r\n{JSON}\r\n{first}"
    print("the request, exactly as it would arrive:")
    print(first_raw.replace("\r\n", "\n"))
    print("\nthe response, exactly as it would leave:")
    print(handle(first_raw).replace("\r\n", "\n"))
    print()
    for url, title, tags in SEED[1:]:
        handle(f"POST /bookmarks HTTP/1.1\r\n{JSON}\r\n"
               + json.dumps({"url": url, "title": title, "tags": tags}))
    print(f"(the other {len(SEED) - 1} were posted quietly; "
          f"the store now holds {len(STORE)})")

    print()
    print("=" * 70)
    print("2. the paths that go wrong")
    print("=" * 70)
    show(f'POST /bookmarks HTTP/1.1\r\n{JSON}\r\n'
         '{"url": "ftp://files.example", "title": "nope"}')
    show(f'POST /bookmarks HTTP/1.1\r\n{JSON}\r\n'
         '{"url": "https://a.example/x", "title": "bad tags", "tags": ["Web Dev"]}')
    show(f'POST /bookmarks HTTP/1.1\r\n{JSON}\r\n'
         '{"url": "https://docs.python.org/3/library/re.html", "title": "again"}')
    show("POST /bookmarks HTTP/1.1\r\nContent-Type: text/plain\r\n\r\nhello")
    show("GET /bookmarks/999 HTTP/1.1\r\n\r\n")
    show("PUT /bookmarks HTTP/1.1\r\n\r\n")
    show("GET /favourites HTTP/1.1\r\n\r\n")
    show("GIMME /bookmarks RIGHT-NOW\r\n\r\n")

    print("=" * 70)
    print("3. reading, searching, deleting")
    print("=" * 70)
    show("GET /bookmarks/2 HTTP/1.1\r\n\r\n")
    show_summary("GET /bookmarks/search?q=python HTTP/1.1\r\n\r\n")
    show_summary("GET /bookmarks/search?tag=http HTTP/1.1\r\n\r\n")
    show_summary("GET /bookmarks/search?q=.* HTTP/1.1\r\n\r\n")
    show("DELETE /bookmarks/3 HTTP/1.1\r\n\r\n")
    show("GET /bookmarks/3 HTTP/1.1\r\n\r\n")

    print("=" * 70)
    print("4. persistence: write JSONL, read it back")
    print("=" * 70)
    STORE.save("bookmarks.jsonl")
    with open("bookmarks.jsonl", encoding="utf-8") as f:
        print(f.read(), end="")
    reloaded = BookmarkStore.load("bookmarks.jsonl")
    print(f"reloaded {len(reloaded)} bookmarks; the next new id would be "
          f"{reloaded.next_id()}")
    print("round trip identical:",
          [m.as_dict() for m in reloaded.all()]
          == [m.as_dict() for m in STORE.all()])

    print()
    print("=" * 70)
    print("5. the test suite")
    print("=" * 70)
    run_tests()
    ```

    Running it prints:

    ```text
    ======================================================================
    1. creating bookmarks — the raw bytes both ways
    ======================================================================
    the request, exactly as it would arrive:
    POST /bookmarks HTTP/1.1
    Content-Type: application/json

    {"url": "https://docs.python.org/3/library/re.html", "title": "Python re module", "tags": ["python", "regex"]}

    the response, exactly as it would leave:
    HTTP/1.1 201 Created
    Location: /bookmarks/1
    Content-Type: application/json; charset=utf-8
    Content-Length: 119

    {"id": 1, "url": "https://docs.python.org/3/library/re.html", "title": "Python re module", "tags": ["python", "regex"]}

    (the other 3 were posted quietly; the store now holds 4)

    ======================================================================
    2. the paths that go wrong
    ======================================================================
    --> POST /bookmarks HTTP/1.1
    HTTP/1.1 400 Bad Request
    Content-Type: application/json; charset=utf-8
    Content-Length: 54

    {"error": "not an http(s) URL: 'ftp://files.example'"}

    --> POST /bookmarks HTTP/1.1
    HTTP/1.1 400 Bad Request
    Content-Type: application/json; charset=utf-8
    Content-Length: 73

    {"error": "bad tag 'Web Dev': use 1-20 lowercase letters, digits or '-'"}

    --> POST /bookmarks HTTP/1.1
    HTTP/1.1 409 Conflict
    Content-Type: application/json; charset=utf-8
    Content-Length: 37

    {"error": "already bookmarked as #1"}

    --> POST /bookmarks HTTP/1.1
    HTTP/1.1 415 Unsupported Media Type
    Content-Type: application/json; charset=utf-8
    Content-Length: 54

    {"error": "expected application/json, got text/plain"}

    --> GET /bookmarks/999 HTTP/1.1
    HTTP/1.1 404 Not Found
    Content-Type: application/json; charset=utf-8
    Content-Length: 29

    {"error": "no bookmark #999"}

    --> PUT /bookmarks HTTP/1.1
    HTTP/1.1 405 Method Not Allowed
    Allow: GET, POST
    Content-Type: application/json; charset=utf-8
    Content-Length: 31

    {"error": "method not allowed"}

    --> GET /favourites HTTP/1.1
    HTTP/1.1 404 Not Found
    Content-Type: application/json; charset=utf-8
    Content-Length: 37

    {"error": "no route for /favourites"}

    --> GIMME /bookmarks RIGHT-NOW
    HTTP/1.1 400 Bad Request
    Content-Type: application/json; charset=utf-8
    Content-Length: 35

    {"error": "unknown method 'GIMME'"}

    ======================================================================
    3. reading, searching, deleting
    ======================================================================
    --> GET /bookmarks/2 HTTP/1.1
    HTTP/1.1 200 OK
    Content-Type: application/json; charset=utf-8
    Content-Length: 121

    {"id": 2, "url": "https://developer.mozilla.org/en-US/docs/Web/HTTP", "title": "MDN HTTP guide", "tags": ["http", "web"]}

    --> GET /bookmarks/search?q=python HTTP/1.1
       HTTP/1.1 200 OK
        #1 Python re module     ['python', 'regex']
        #4 http.server docs     ['python', 'http']
        (2 hits)

    --> GET /bookmarks/search?tag=http HTTP/1.1
       HTTP/1.1 200 OK
        #2 MDN HTTP guide       ['http', 'web']
        #4 http.server docs     ['python', 'http']
        (2 hits)

    --> GET /bookmarks/search?q=.* HTTP/1.1
       HTTP/1.1 200 OK
        (0 hits)

    --> DELETE /bookmarks/3 HTTP/1.1
    HTTP/1.1 204 No Content



    --> GET /bookmarks/3 HTTP/1.1
    HTTP/1.1 404 Not Found
    Content-Type: application/json; charset=utf-8
    Content-Length: 27

    {"error": "no bookmark #3"}

    ======================================================================
    4. persistence: write JSONL, read it back
    ======================================================================
    {"id": 1, "url": "https://docs.python.org/3/library/re.html", "title": "Python re module", "tags": ["python", "regex"]}
    {"id": 2, "url": "https://developer.mozilla.org/en-US/docs/Web/HTTP", "title": "MDN HTTP guide", "tags": ["http", "web"]}
    {"id": 4, "url": "https://docs.python.org/3/library/http.server.html", "title": "http.server docs", "tags": ["python", "http"]}
    reloaded 3 bookmarks; the next new id would be 5
    round trip identical: True

    ======================================================================
    5. the test suite
    ======================================================================
    Testing the bookmark service:
      BookmarkStore            9 checks
      validation              13 checks
      search                   6 checks
      JSONL persistence        4 checks
      router happy paths      10 checks
      router error paths      11 checks

    53/53 checks passed — ship it.
    ```

    Six things in that output are worth a second look.

    **The 415 and the 409 are not decoration.** `Content-Type: text/plain` on
    a JSON endpoint is a *media type* problem, not a malformed-body problem,
    and a URL you have already saved is a *state* conflict, not a validation
    error. Three different failures, three different codes, three different
    things a client can do about it.

    **The `204` really is empty** — no `Content-Type`, no `Content-Length`, no
    body, just a status line and a blank line. That is what the standard
    requires, and it is why `Response.final_headers` special-cases it in one
    place that both the runnable core and `server.py` share.

    **Searching for `.*` returns nothing.** `re.escape` turned the user's text
    into a literal, so it looked for a full stop followed by an asterisk and
    correctly found none. Without that one call, a search box is a way for
    strangers to run patterns on your server.

    **The JSONL file has no id 3.** It was deleted, and `load` continues the
    sequence at 5 rather than filling the gap — because a deleted id may still
    be in somebody's bookmarks bar, and re-using it would silently point them
    at a different page.

    **The malformed request never reaches a handler.** `GIMME` fails in
    `parse_request`, so `dispatch` answers `400` before routing begins: the
    error boundary is layered, and the outermost layer is the parser.

    **53 checks is not many.** It is enough to have caught every bug we made
    writing this, which is the only measure of a suite that matters.

The complete front end. Save it as `index.html` beside `server.py`, start the
server, and open `http://127.0.0.1:8000/`.

??? success "Full reference implementation — `index.html`"

    ```html
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Bookmarks</title>
    <style>
      :root { --ink: #1f2933; --muted: #6b7785; --line: #dfe3e8; --accent: #00695c; }
      * { box-sizing: border-box; }
      body { font: 16px/1.5 system-ui, sans-serif; color: var(--ink);
             max-width: 44rem; margin: 2rem auto; padding: 0 1rem; }
      h1 { margin: 0 0 .25rem; font-size: 1.6rem; }
      .sub { color: var(--muted); margin: 0 0 1.5rem; }
      form { display: grid; gap: .5rem; grid-template-columns: 1fr 1fr auto;
             margin-bottom: 1rem; }
      input { padding: .5rem .6rem; border: 1px solid var(--line);
              border-radius: 6px; font: inherit; }
      button { padding: .5rem .9rem; border: 0; border-radius: 6px;
               background: var(--accent); color: #fff; font: inherit;
               cursor: pointer; }
      button.link { background: none; color: var(--muted); padding: 0 .3rem; }
      button.link:hover { color: #b00020; }
      #search { width: 100%; margin-bottom: 1rem; }
      #status { min-height: 1.5rem; color: var(--muted); margin: 0 0 .5rem; }
      #status.bad { color: #b00020; }
      ul { list-style: none; padding: 0; margin: 0; }
      li { border-top: 1px solid var(--line); padding: .7rem 0;
           display: flex; gap: .5rem; align-items: baseline; }
      li a { color: var(--accent); text-decoration: none; font-weight: 600; }
      li a:hover { text-decoration: underline; }
      .url { color: var(--muted); font-size: .85rem; word-break: break-all; }
      .tag { background: #e0f2f1; color: var(--accent); border-radius: 999px;
             padding: .1rem .55rem; font-size: .75rem; }
      .grow { flex: 1; }
      @media (max-width: 34rem) { form { grid-template-columns: 1fr; } }
    </style>
    </head>
    <body>
      <h1>Bookmarks</h1>
      <p class="sub">A page talking to the API you wrote.</p>

      <form id="add-form">
        <input id="url" type="url" placeholder="https://example.org/page" required>
        <input id="title" type="text" placeholder="What is it?" required>
        <button type="submit">Add</button>
      </form>

      <input id="search" type="search" placeholder="Search title, URL or #tag">
      <p id="status" role="status"></p>
      <ul id="list"></ul>

    <script>
    const API = "/bookmarks";
    const listEl = document.querySelector("#list");
    const statusEl = document.querySelector("#status");

    function say(text, bad = false) {
      statusEl.textContent = text;
      statusEl.classList.toggle("bad", bad);
    }

    /* fetch resolves for 404 and 500 too — the status code is our job. */
    async function callApi(path, options = {}) {
      const response = await fetch(path, options);
      if (response.status === 204) return null;
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.error || response.statusText);
      return payload;
    }

    function render(bookmarks) {
      listEl.replaceChildren();
      if (bookmarks.length === 0) {
        const empty = document.createElement("li");
        empty.textContent = "Nothing here yet.";
        listEl.append(empty);
        return;
      }
      for (const mark of bookmarks) {
        const row = document.createElement("li");
        const main = document.createElement("div");
        main.className = "grow";

        const link = document.createElement("a");
        link.href = mark.url;
        link.textContent = mark.title;      // textContent, never innerHTML: a
        link.rel = "noopener noreferrer";   // title of "<script>" stays text
        main.append(link);

        const url = document.createElement("div");
        url.className = "url";
        url.textContent = mark.url;
        main.append(url);
        row.append(main);

        for (const tag of mark.tags) {
          const chip = document.createElement("span");
          chip.className = "tag";
          chip.textContent = tag;
          row.append(chip);
        }

        const remove = document.createElement("button");
        remove.className = "link";
        remove.type = "button";
        remove.textContent = "delete";
        remove.addEventListener("click", () => destroy(mark.id));
        row.append(remove);

        listEl.append(row);
      }
    }

    async function refresh() {
      const query = document.querySelector("#search").value.trim();
      try {
        if (query === "") {
          const data = await callApi(API);
          render(data.bookmarks);
          say(`${data.bookmarks.length} bookmarks`);
        } else {
          const key = query.startsWith("#") ? "tag" : "q";
          const term = query.startsWith("#") ? query.slice(1) : query;
          const data = await callApi(
            `${API}/search?${key}=${encodeURIComponent(term)}`);
          render(data.bookmarks);
          say(`${data.count} match "${query}"`);
        }
      } catch (err) {
        say(`could not load: ${err.message}`, true);
      }
    }

    async function destroy(id) {
      try {
        await callApi(`${API}/${id}`, { method: "DELETE" });
        await refresh();
      } catch (err) {
        say(`could not delete: ${err.message}`, true);
      }
    }

    document.querySelector("#add-form").addEventListener("submit", async (event) => {
      event.preventDefault();
      const url = document.querySelector("#url");
      const title = document.querySelector("#title");
      const tags = title.value.match(/#[a-z0-9-]+/gi) || [];
      try {
        say("saving…");
        await callApi(API, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            url: url.value,
            title: title.value.replace(/#[a-z0-9-]+/gi, "").trim(),
            tags: tags.map((t) => t.slice(1).toLowerCase()),
          }),
        });
        url.value = "";
        title.value = "";
        await refresh();
      } catch (err) {
        say(`could not save: ${err.message}`, true);   // ALWAYS handle this
      }
    });

    let timer;
    document.querySelector("#search").addEventListener("input", () => {
      clearTimeout(timer);            // debounce: one request after typing stops
      timer = setTimeout(refresh, 200);
    });

    refresh();
    </script>
    </body>
    </html>
    ```

## Going further

- **Sessions and auth.** Add `POST /login`, hand back
  `Set-Cookie: session=<random>; HttpOnly; Secure; SameSite=Lax`, keep a
  server-side session table, and scope every bookmark to a user id. The
  cookie-flag warning in
  [42.2](../../ch42-web-gui/02-http-server.md) is the part to get right
  first — a session cookie without `HttpOnly` is a session waiting to be
  stolen.
- **Pagination.** `GET /bookmarks?limit=20&offset=40`, with the total count in
  the body. Then discover why real APIs prefer *cursor* pagination: with
  offsets, deleting a record while someone is paging makes them skip one.
- **A real database.** Swap `BookmarkStore` for one backed by `sqlite3` —
  standard library, one file, real transactions, real indexes. Keep the class's
  method signatures identical and the router, the tests, and the front end
  should not need a single edit. If they do, your layers were leakier than you
  thought.
- **`PUT` and `PATCH`.** Add editing. `PUT /bookmarks/42` replaces the whole
  record and is idempotent; `PATCH` merges a partial one. Decide what a `PUT`
  to a non-existent id should do, and defend your answer.
- **Deployment.** `python server.py` is a development server: single process,
  no TLS, no request limits, no hardening. Real deployment means a production
  server (gunicorn or uvicorn behind nginx or Caddy), a process manager that
  restarts it, HTTPS certificates, and a place for logs. Write down what would
  break if a hundred people used your app at once — then fix the first item on
  that list.
- **Rate limiting as middleware.** Add the middleware chain from
  [42.2](../../ch42-web-gui/02-http-server.md) and use it for a per-client
  request budget answering `429 Too Many Requests`. Because it is a wrapper, it
  applies to every route at once and needs no handler to know about it.
- **A proper front end.** Rebuild `index.html` in a framework and compare:
  how much of your hand-written `render` disappears, and how much new
  machinery arrives to replace it. Both halves of that answer are worth
  knowing before you pick a tool for a real project.
