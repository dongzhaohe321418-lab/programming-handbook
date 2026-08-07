# 42.2 HTTP and a web server from scratch

[Section 42.1](01-html-css.md) built a page. This section answers the question
that page raises: how did the text get from a machine you have never met into
the tab in front of you? The answer is a protocol so simple you could type it
by hand — and by the end of this page you will have, because the centrepiece
here is not a diagram but a **working web server core in pure Python**: a
request parser, a router with path parameters, handlers, a response serializer,
and a middleware chain. It has no sockets and no network, which means it runs
right here in your browser. Everything it does is exactly what Flask, Express,
and Spring Boot do, minus the network plumbing and the twelve years of edge
cases.

## What happens when you type a URL

Between pressing ++enter++ and seeing a page, six distinct things happen, each
of which can fail in its own way.

```mermaid
sequenceDiagram
    autonumber
    participant B as Browser
    participant D as DNS resolver
    participant S as Server 93.184.216.34
    B->>D: Which address is teahouse.example?
    D-->>B: 93.184.216.34
    B->>S: TCP handshake — SYN, SYN-ACK, ACK
    B->>S: TLS handshake — certificate, key agreement
    B->>S: GET /guide HTTP/1.1 (encrypted)
    S->>S: route, run handler, build response
    S-->>B: 200 OK + the HTML text
    B->>B: parse HTML into the DOM
    B->>S: GET /style.css, /app.js, /teapot.png
    S-->>B: 200 OK for each
    B->>B: style, lay out, paint
```

1. **DNS** turns the human name `teahouse.example` into a numeric IP address,
   the way a phone book turns a name into a number. Answers are cached, which
   is why a domain change takes hours to reach everyone.
2. **TCP** opens a reliable, ordered byte stream to that address on a port
   (80 for HTTP, 443 for HTTPS) with a three-message handshake.
3. **TLS** — the S in HTTPS — negotiates encryption over that stream and
   checks the server's certificate, so nobody between you and the server can
   read or alter the traffic.
4. **The HTTP request** goes out: a few lines of text saying which document is
   wanted and on whose behalf.
5. **The server** matches the path to a handler, runs it, and sends back a
   response: a status line, headers, and a body.
6. **The browser renders**: parses the HTML into the DOM of
   [42.1](01-html-css.md), discovers it needs a stylesheet, a script, and some
   images, requests those too, then styles, lays out, and paints.

Only step 5 is your program. Everything else is infrastructure — but knowing
where each piece sits is what turns "the site is down" into a diagnosis.

## The URL, dissected

A URL packs six fields into one string, and Python's `urllib.parse` — the tool
[41.2](../ch41-regex/02-groups-parsing.md) told you to reach for instead of a
mega-pattern — pulls them apart properly, escapes and all.

```python
from urllib.parse import urlsplit, parse_qs, urlencode, quote, unquote

URL = "https://ada:s3cret@teahouse.example:8443/guide/green?q=cold+brew&page=2#steps"

parts = urlsplit(URL)
rows = [
    ("scheme",   parts.scheme,                            "how to talk: http, https, mailto"),
    ("userinfo", f"{parts.username}:{parts.password}",    "legacy; never use it"),
    ("host",     parts.hostname,                          "which machine — DNS resolves this"),
    ("port",     str(parts.port),                         "default 80 for http, 443 for https"),
    ("path",     parts.path,                              "which resource on that machine"),
    ("query",    parts.query,                             "parameters for the resource"),
    ("fragment", parts.fragment,                          "scroll target — never sent!"),
]
for name, value, note in rows:
    print(f"{name:<9}{value:<19}{note}")
print()

print("query as a dict:", parse_qs(parts.query))
print("note '+' became a space:", parse_qs(parts.query)["q"])
print("building one    :", urlencode({"q": "green tea", "page": 2}))
print("escaping a path :", quote("/notes/green tea & oolong.html"))
print("and back        :", unquote("/notes/green%20tea%20%26%20oolong.html"))
```

```text
scheme   https              how to talk: http, https, mailto
userinfo ada:s3cret         legacy; never use it
host     teahouse.example   which machine — DNS resolves this
port     8443               default 80 for http, 443 for https
path     /guide/green       which resource on that machine
query    q=cold+brew&page=2 parameters for the resource
fragment steps              scroll target — never sent!

query as a dict: {'q': ['cold brew'], 'page': ['2']}
note '+' became a space: ['cold brew']
building one    : q=green+tea&page=2
escaping a path : /notes/green%20tea%20%26%20oolong.html
and back        : /notes/green tea & oolong.html
```

Three details that catch people out. The **fragment** (`#steps`) never leaves
the browser — the server has no idea which anchor you jumped to. The **query
string** is a convention, not a rule: `?q=cold+brew&page=2` is just text, and
`parse_qs` decodes `+` as a space and `%26` as `&` because someone agreed to
encode them that way. And a value must be **percent-encoded** before it goes in
a URL, which is what `quote` and `urlencode` are for — hand-concatenating user
text into a URL is how you get a broken link or an injected parameter.

## HTTP is plain text you could type

Here is a complete, real HTTP request. Every line ends with a carriage return
and a line feed (`\r\n`), and a blank line separates the headers from the body.

```text
POST /api/subscribe HTTP/1.1
Host: teahouse.example
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)
Accept: application/json
Content-Type: application/json
Content-Length: 38
Cookie: session=8f3a91c0; theme=dark

{"email": "ada@example.org", "cadence": "weekly"}
```

And a complete response:

```text
HTTP/1.1 201 Created
Date: Tue, 05 Mar 2024 10:12:44 GMT
Server: nginx/1.24.0
Content-Type: application/json; charset=utf-8
Content-Length: 52
Set-Cookie: session=8f3a91c0; HttpOnly; Secure; SameSite=Lax
Cache-Control: no-store

{"id": 1042, "email": "ada@example.org", "ok": true}
```

That is the entire protocol. A **start line**, then **headers** (one
`Name: value` per line, names case-insensitive), then a blank line, then an
optional **body**. Request start line: method, target, version. Response start
line: version, status code, reason phrase. HTTP/2 and HTTP/3 compress and
multiplex these same messages in binary — the *model* on this page is
unchanged, which is why learning the text form is not learning a legacy skill.

### Methods, and what "safe" and "idempotent" mean

| Method | Purpose | Safe? | Idempotent? | Has a body? |
|---|---|---|---|---|
| `GET` | fetch a resource | yes | yes | no |
| `HEAD` | fetch only the headers | yes | yes | no |
| `POST` | create, or "do something" | **no** | **no** | yes |
| `PUT` | replace a resource entirely | no | yes | yes |
| `PATCH` | modify part of a resource | no | not required | yes |
| `DELETE` | remove a resource | no | yes | rarely |
| `OPTIONS` | ask what is allowed | yes | yes | no |

**Safe** means the request does not change anything on the server, so a
browser, a search-engine crawler, or a link prefetcher may issue it freely
without asking. **Idempotent** means doing it twice has the same effect as
doing it once — `PUT /users/42` with the same body lands on the same state
whether it arrives once or five times, but `POST /orders` five times creates
five orders. This is not pedantry: it decides whether a client may safely retry
after a timeout, and it is exactly why browsers show "confirm form
resubmission" when you refresh after a `POST`.

### Status codes worth knowing

The first digit is the family; learn the families and the dozen codes below and
you can read almost any log.

| Code | Meaning | When you send it |
|---|---|---|
| `200 OK` | success, body follows | the normal answer to a `GET` |
| `201 Created` | a new resource exists | after a successful `POST`; add a `Location` header |
| `204 No Content` | success, deliberately empty | a `DELETE` that worked |
| `301 Moved Permanently` | new address, cache it | site restructure |
| `302 Found` / `303 See Other` | temporary redirect | after a login `POST`, send them to the dashboard |
| `304 Not Modified` | your cached copy is still good | conditional `GET` with `If-None-Match` |
| `400 Bad Request` | the request is malformed | unparseable body, missing required field |
| `401 Unauthorized` | you are not authenticated | no credentials, or bad ones (badly named — it means *unauthenticated*) |
| `403 Forbidden` | authenticated, but not allowed | a normal user hitting `/admin` |
| `404 Not Found` | no such resource | a typo'd path |
| `405 Method Not Allowed` | wrong verb for this path | `DELETE /login`; you must send an `Allow` header |
| `409 Conflict` | state clash | that email is already registered |
| `429 Too Many Requests` | rate limited | slow down |
| `500 Internal Server Error` | your code raised | a bug — never leak the traceback to the client |
| `502` / `503` / `504` | bad gateway, unavailable, timeout | the upstream service is unwell |

The dividing line matters more than any individual code: **4xx is the client's
fault, 5xx is the server's fault.** Returning `200 OK` with `{"error": "..."}`
in the body — a shockingly common design — breaks every retry policy, monitor,
and cache between you and your user, all of which read the status code and
nothing else.

### Headers and bodies

Headers are metadata about the message. A handful appear constantly:

| Header | Direction | Says |
|---|---|---|
| `Host` | request | which site, since one IP serves many (required in HTTP/1.1) |
| `Content-Type` | both | how to interpret the body: `text/html`, `application/json`, `image/png` |
| `Content-Length` | both | how many bytes the body has, so the reader knows when to stop |
| `Accept` | request | which types the client can handle |
| `Authorization` | request | credentials, usually `Bearer <token>` |
| `User-Agent` | request | which client (routinely lied about) |
| `Cookie` / `Set-Cookie` | request / response | see below |
| `Cache-Control` | both | how long this may be reused |
| `Location` | response | where to go after a redirect, or where the new resource lives |

The body is *just bytes*; `Content-Type` is the only thing that says what they
mean. Send JSON with `Content-Type: text/html` and the browser will try to
render it as a page — the bytes were fine, the label was wrong.

## Statelessness, cookies, sessions, and tokens

HTTP has **no memory**. Every request arrives as if it were the first one ever
sent; the server has no idea that the request for `/account` came from the same
person who just posted to `/login`. That design is why the web scales — any
server in a fleet can answer any request — and it is why logging in needs a
trick.

The trick is a **cookie**: a small named string the server asks the browser to
store and send back on every subsequent request to that site.

```mermaid
sequenceDiagram
    participant B as Browser
    participant S as Server
    B->>S: POST /login  (email, password)
    S->>S: check the password, create session 8f3a91c0
    S-->>B: 303 See Other + Set-Cookie: session=8f3a91c0; HttpOnly; Secure
    Note over B: browser stores the cookie for teahouse.example
    B->>S: GET /account   Cookie: session=8f3a91c0
    S->>S: look up 8f3a91c0 in the session store -> user 42
    S-->>B: 200 OK  "Hello Ada"
    B->>S: POST /logout  Cookie: session=8f3a91c0
    S->>S: delete the session
    S-->>B: 303 + Set-Cookie: session=; Max-Age=0
```

There are three common shapes, and the difference is *where the state lives*:

- **Session cookie** (drawn above). The cookie holds a meaningless random id;
  everything real — which user, when they logged in — lives in a table on the
  server. Logging out is a `DELETE` on that table, so revocation is instant.
- **Signed cookie**. The cookie holds the data itself plus a cryptographic
  signature, so the server can verify the browser did not edit it without
  storing anything. Cheap; but revoking early is awkward.
- **Bearer token** (typically a JWT), sent in `Authorization: Bearer …` rather
  than a cookie. The normal choice for APIs and mobile apps, because there is
  no browser to manage cookies. Same trade-off as a signed cookie: nothing to
  look up, nothing easy to revoke, so keep the lifetime short.

!!! warning "Cookie flags are not optional"

    - **`HttpOnly`** — JavaScript cannot read this cookie. Without it, a single
      cross-site scripting hole (see [42.3](03-javascript.md)) lets an attacker
      read the session id out of `document.cookie` and become the user. Every
      session cookie must have it.
    - **`Secure`** — only ever sent over HTTPS, so it cannot leak on a café
      network.
    - **`SameSite=Lax`** (or `Strict`) — not sent on cross-site requests, which
      blocks most cross-site request forgery, where another site quietly submits
      a form to yours using the victim's cookie.

    `Set-Cookie: session=abc` with none of these is a session waiting to be
    stolen.

## The centrepiece: an HTTP server's brain, in Python

A web server does two separable jobs. It moves bytes over a socket, and it
turns a request into a response. The first job is the operating system's kind
of work; the second is *all of your application*, and it needs no network at
all. We are going to write the second job completely, feed it hand-written
request strings, and print the exact bytes it would send back.

### Step 1 — parse a request

```python
from dataclasses import dataclass
from urllib.parse import urlsplit, parse_qs


class BadRequest(Exception):
    """The bytes on the wire are not a valid HTTP request."""


@dataclass
class Request:
    method: str
    path: str
    query: dict
    version: str
    headers: dict
    body: str

    def header(self, name, default=None):
        return self.headers.get(name.lower(), default)


METHODS = {"GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"}


def parse_request(raw):
    head, _, body = raw.partition("\r\n\r\n")   # blank line ends the headers
    lines = head.split("\r\n")

    bits = lines[0].split(" ")                  # "GET /path?q=1 HTTP/1.1"
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
        headers[name.strip().lower()] = value.strip()   # names are case-insensitive

    url = urlsplit(target)
    return Request(method=method,
                   path=url.path or "/",
                   query={k: v[0] for k, v in parse_qs(url.query).items()},
                   version=version,
                   headers=headers,
                   body=body)


RAW = ("POST /api/subscribe?ref=newsletter HTTP/1.1\r\n"
       "Host: teahouse.example\r\n"
       "Content-Type: application/json\r\n"
       "Content-Length: 30\r\n"
       "\r\n"
       '{"email": "ada@example.org"}')

req = parse_request(RAW)
print("method  :", req.method)
print("path    :", req.path)
print("query   :", req.query)
print("version :", req.version)
print("headers :", req.headers)
print("body    :", req.body)
print("lookup is case-insensitive:", req.header("CONTENT-TYPE"))

BAD = ["GET /x",                                      # no version
       "GIMME /x HTTP/1.1",                           # invented method
       "GET /x HTTP/1.1\r\nHost teahouse.example"]    # header with no colon
for bad in BAD:
    try:
        parse_request(bad)
    except BadRequest as e:
        print("rejected:", e)
```

```text
method  : POST
path    : /api/subscribe
query   : {'ref': 'newsletter'}
version : HTTP/1.1
headers : {'host': 'teahouse.example', 'content-type': 'application/json', 'content-length': '30'}
body    : {"email": "ada@example.org"}
lookup is case-insensitive: application/json
rejected: malformed request line: 'GET /x'
rejected: unknown method 'GIMME'
rejected: malformed header line: 'Host teahouse.example'
```

Forty lines and a raw byte string has become an object with fields. Note the
two deliberate decisions: header names are **lower-cased on the way in** so
lookups never depend on how the client capitalised them, and anything
unparseable raises `BadRequest` rather than returning a half-built object —
that exception becomes a `400` in a moment.

### Step 2 — serialize a response

```python
# continues
from dataclasses import dataclass, field

REASON = {200: "OK", 201: "Created", 204: "No Content",
          301: "Moved Permanently", 303: "See Other", 304: "Not Modified",
          400: "Bad Request", 401: "Unauthorized", 403: "Forbidden",
          404: "Not Found", 405: "Method Not Allowed", 409: "Conflict",
          500: "Internal Server Error"}


@dataclass
class Response:
    status: int = 200
    headers: dict = field(default_factory=dict)
    body: str = ""

    def wire(self):
        """Exactly the text that would go down the socket."""
        head = [f"HTTP/1.1 {self.status} {REASON.get(self.status, 'Unknown')}"]
        headers = dict(self.headers)
        headers.setdefault("Content-Type", "text/plain; charset=utf-8")
        headers["Content-Length"] = str(len(self.body.encode("utf-8")))
        for name, value in headers.items():
            head.append(f"{name}: {value}")
        return "\r\n".join(head) + "\r\n\r\n" + self.body


demo = Response(201, {"Location": "/api/users/1042",
                      "Content-Type": "application/json"},
                '{"id": 1042}')
print(repr(demo.wire()))
print()
print(demo.wire().replace("\r\n", "\n"))
```

```text
'HTTP/1.1 201 Created\r\nLocation: /api/users/1042\r\nContent-Type: application/json\r\nContent-Length: 12\r\n\r\n{"id": 1042}'

HTTP/1.1 201 Created
Location: /api/users/1042
Content-Type: application/json
Content-Length: 12

{"id": 1042}
```

The `repr` is the honest view: `\r\n` everywhere, one blank line before the
body. `Content-Length` is computed from the **encoded** bytes, not the
character count — `len("café")` is 4 but its UTF-8 encoding is 5 bytes, and a
client that trusts a wrong length either truncates your page or hangs waiting
for a byte that never comes.

### Step 3 — route with path parameters

Real applications do not serve `/users/42` from a table of every user id; they
declare a **template** — `/users/{user_id}` — and extract the value. That is a
regex with a named group, built exactly as
[41.2](../ch41-regex/02-groups-parsing.md) built one, using `re.sub` with a
**replacement function** to convert the template into a pattern.

```python
# continues
import re

PARAM = re.compile(r"\{(\w+)(?::(int))?\}")        # {name} or {name:int}


def template_to_regex(template):
    def replace(m):
        name, kind = m.group(1), m.group(2)
        piece = r"\d+" if kind == "int" else r"[^/]+"   # a segment never spans "/"
        return f"(?P<{name}>{piece})"
    return re.compile("^" + PARAM.sub(replace, template) + "$")


class MethodNotAllowed(Exception):
    def __init__(self, allowed):
        super().__init__(", ".join(allowed))
        self.allowed = allowed


class Router:
    def __init__(self):
        self.routes = []                        # first match wins, so order matters

    def route(self, method, template):
        pattern = template_to_regex(template)
        def register(handler):
            self.routes.append((method, pattern, handler, template))
            return handler
        return register                         # used as a decorator

    def resolve(self, request):
        wrong_method = set()
        for method, pattern, handler, _template in self.routes:
            m = pattern.match(request.path)
            if m is None:
                continue
            if method != request.method:
                wrong_method.add(method)        # path matched, verb did not
                continue
            params = {k: int(v) if v.isdigit() else v
                      for k, v in m.groupdict().items()}
            return handler, params
        if wrong_method:
            raise MethodNotAllowed(sorted(wrong_method))
        return None, None                       # nothing matched: a 404


for template in ["/", "/users/{user_id:int}", "/notes/{slug}/edit"]:
    print(f"{template:<24} -> {template_to_regex(template).pattern}")

print()
app = Router()


@app.route("GET", "/users/{user_id:int}")
def user_page(request, params):
    name = {42: "Ada", 7: "Grace"}.get(params["user_id"])
    if name is None:
        return Response(404, {}, f"no user {params['user_id']}")
    short = request.query.get("fmt") == "short"
    body = f"<h1>{name}</h1>" if short else f"<h1>{name}</h1><p>id {params['user_id']}</p>"
    return Response(200, {"Content-Type": "text/html; charset=utf-8"}, body)


@app.route("GET", "/api/users/{user_id:int}")
def user_json(request, params):
    import json
    name = {42: "Ada", 7: "Grace"}.get(params["user_id"])
    payload = {"id": params["user_id"], "name": name} if name else {"error": "not found"}
    return Response(200 if name else 404, {"Content-Type": "application/json"},
                    json.dumps(payload))


for path in ["/users/42", "/users/ada", "/api/users/7", "/teapot"]:
    probe = Request("GET", path, {}, "HTTP/1.1", {}, "")
    handler, params = app.resolve(probe)
    print(f"{path:<16} -> {handler.__name__ if handler else 'no route (404)':<12} {params}")
```

```text
/                        -> ^/$
/users/{user_id:int}     -> ^/users/(?P<user_id>\d+)$
/notes/{slug}/edit       -> ^/notes/(?P<slug>[^/]+)/edit$

/users/42        -> user_page    {'user_id': 42}
/users/ada       -> no route (404) None
/api/users/7     -> user_json    {'user_id': 7}
/teapot          -> no route (404) None
```

`/users/ada` does not match, because `{user_id:int}` compiled to `\d+`. That is
type validation happening in the router, before your handler runs — a small
thing that removes a whole category of `int()` crashes. And `[^/]+` rather than
`.+` is the point [41.2](../ch41-regex/02-groups-parsing.md) laboured: a path
segment stops at the next slash, and a negated character class says so
directly.

### Step 4 — middleware, and the whole thing running

**Middleware** is a function that wraps a handler: it can inspect the request
before, inspect the response after, or short-circuit and answer by itself. The
chain is built by wrapping outward, so the first entry in the list is the
outermost layer and sees everything.

```python
# continues
LOG = []


def logging_middleware(next_handler):
    def wrapped(request, params):
        response = next_handler(request, params)
        LOG.append(f"{request.method} {request.path} -> {response.status}")
        return response
    return wrapped


def auth_middleware(next_handler):
    def wrapped(request, params):
        if request.path.startswith("/api/"):
            if request.header("authorization") != "Bearer demo-token":
                return Response(401, {"WWW-Authenticate": "Bearer"},
                                "missing or invalid token")   # short-circuit
        return next_handler(request, params)
    return wrapped


MIDDLEWARE = [logging_middleware, auth_middleware]     # outermost first


def handle(raw):
    """The whole server, from wire bytes to wire bytes."""
    try:
        request = parse_request(raw)
    except BadRequest as e:
        return Response(400, {}, f"Bad Request: {e}").wire()

    try:
        handler, params = app.resolve(request)
    except MethodNotAllowed as e:
        return Response(405, {"Allow": ", ".join(e.allowed)},
                        "method not allowed").wire()

    if handler is None:
        def handler(request, params):
            return Response(404, {}, f"no route for {request.path}")
        params = {}

    chain = handler
    for layer in reversed(MIDDLEWARE):        # wrap from the inside out
        chain = layer(chain)

    try:
        response = chain(request, params)
    except Exception as e:                    # a handler bug must not kill the server
        response = Response(500, {}, f"internal error: {type(e).__name__}")
    return response.wire()


REQUESTS = [
    "GET /users/42?fmt=short HTTP/1.1\r\nHost: teahouse.example\r\n\r\n",
    "GET /api/users/7 HTTP/1.1\r\nHost: teahouse.example\r\n"
    "Authorization: Bearer demo-token\r\n\r\n",
    "GET /api/users/7 HTTP/1.1\r\nHost: teahouse.example\r\n\r\n",
    "GET /teapot HTTP/1.1\r\nHost: teahouse.example\r\n\r\n",
    "GIMME /users/42 RIGHT-NOW\r\n\r\n",
]

for raw in REQUESTS:
    print("=" * 60)
    print("--> " + raw.split("\r\n")[0])
    print("-" * 60)
    print(handle(raw).replace("\r\n", "\n"))
    print()

print("access log:")
for line in LOG:
    print("   ", line)
```

```text
============================================================
--> GET /users/42?fmt=short HTTP/1.1
------------------------------------------------------------
HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8
Content-Length: 12

<h1>Ada</h1>

============================================================
--> GET /api/users/7 HTTP/1.1
------------------------------------------------------------
HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 26

{"id": 7, "name": "Grace"}

============================================================
--> GET /api/users/7 HTTP/1.1
------------------------------------------------------------
HTTP/1.1 401 Unauthorized
WWW-Authenticate: Bearer
Content-Type: text/plain; charset=utf-8
Content-Length: 24

missing or invalid token

============================================================
--> GET /teapot HTTP/1.1
------------------------------------------------------------
HTTP/1.1 404 Not Found
Content-Type: text/plain; charset=utf-8
Content-Length: 20

no route for /teapot

============================================================
--> GIMME /users/42 RIGHT-NOW
------------------------------------------------------------
HTTP/1.1 400 Bad Request
Content-Type: text/plain; charset=utf-8
Content-Length: 35

Bad Request: unknown method 'GIMME'

access log:
    GET /users/42 -> 200
    GET /api/users/7 -> 200
    GET /api/users/7 -> 401
    GET /teapot -> 404

```

Read the access log carefully: it has **four** lines for **five** requests. The
malformed one never reached the middleware, because parsing failed before
routing began — which is exactly right, and exactly why a real server's error
log and access log are different files.

Everything else is worth naming, because these are the parts of every web
framework you will ever use:

- the **request object** — raw bytes turned into fields your code can read;
- the **router** — a table from `(method, pattern)` to a function, with typed
  path parameters extracted by a named group;
- the **handler** — a plain function taking a request and returning a status,
  headers, and a body. Your entire application is a pile of these;
- the **middleware chain** — cross-cutting concerns (logging, authentication,
  compression, rate limiting, sessions) written once and applied to every route,
  with the ability to short-circuit, as `auth_middleware` did for the 401;
- the **error boundary** — `BadRequest` becomes 400, no route becomes 404, the
  wrong verb becomes 405, and an unexpected exception becomes 500 with the
  traceback kept on the server;
- the **serializer** — an object turned back into exact wire bytes.

You have written the core of a web framework. Flask's `@app.route("/users/<int:user_id>")`
is the decorator above; Express's `app.use(...)` is `MIDDLEWARE`; Spring's
`@GetMapping("/users/{id}")` is `template_to_regex`. The remaining code in
those projects is sockets, concurrency, templating, and a decade of edge cases —
important, but no longer mysterious.

## REST and JSON APIs

Most servers today serve two audiences: browsers (which want HTML) and other
programs (which want data). The data half is usually a **JSON API** organised
by the **REST** convention: URLs name *resources* (nouns), and the HTTP method
says what to do to them (verbs).

| Intent | REST | Not this |
|---|---|---|
| list notes | `GET /api/notes` | `GET /api/getAllNotes` |
| one note | `GET /api/notes/42` | `GET /api/note?action=fetch&id=42` |
| create | `POST /api/notes` → `201` + `Location` | `GET /api/createNote?text=…` |
| replace | `PUT /api/notes/42` | `POST /api/updateNote` |
| delete | `DELETE /api/notes/42` → `204` | `GET /api/deleteNote?id=42` |

The last row is not a style quibble. `GET` is *safe*, so a browser prefetcher,
a crawler, or an antivirus link-scanner may follow it — and sites really have
had their content deleted by a search engine dutifully crawling every
`/deleteNote?id=` link on the page.

Adding a JSON endpoint to the router you already have takes nine lines. This
one accepts a `POST`, parses the body, validates it, and answers `201` with a
`Location` header — or `400` if the body is not what it claims to be.

```python
# continues
import json

NOTES = {}
NEXT_ID = 1042


@app.route("POST", "/api/notes")
def create_note(request, params):
    global NEXT_ID
    if request.header("content-type", "").split(";")[0] != "application/json":
        return Response(400, {"Content-Type": "application/json"},
                        json.dumps({"error": "expected application/json"}))
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError as e:
        return Response(400, {"Content-Type": "application/json"},
                        json.dumps({"error": f"invalid JSON: {e.msg}"}))
    text = payload.get("text")
    if not isinstance(text, str) or not text.strip():
        return Response(400, {"Content-Type": "application/json"},
                        json.dumps({"error": "field 'text' is required"}))

    note_id = NEXT_ID
    NEXT_ID += 1
    NOTES[note_id] = text.strip()
    return Response(201, {"Content-Type": "application/json",
                          "Location": f"/api/notes/{note_id}"},
                    json.dumps({"id": note_id, "text": NOTES[note_id]}))


@app.route("GET", "/api/notes")
def list_notes(request, params):
    return Response(200, {"Content-Type": "application/json"},
                    json.dumps({"notes": [{"id": k, "text": v}
                                          for k, v in sorted(NOTES.items())]}))


AUTH = "Authorization: Bearer demo-token\r\n"
CT = "Content-Type: application/json\r\n"
API_REQUESTS = [
    f'POST /api/notes HTTP/1.1\r\n{AUTH}{CT}\r\n{{"text": "steep 3 min"}}',
    f'POST /api/notes HTTP/1.1\r\n{AUTH}{CT}\r\n{{"text": ""}}',
    f'POST /api/notes HTTP/1.1\r\n{AUTH}{CT}\r\n{{not json at all}}',
    f"GET /api/notes HTTP/1.1\r\n{AUTH}\r\n",
    f"DELETE /api/notes HTTP/1.1\r\n{AUTH}\r\n",
]

for raw in API_REQUESTS:
    print("--> " + raw.split("\r\n")[0], "  body:", raw.split("\r\n\r\n")[1] or "(none)")
    wire = handle(raw)                      # call ONCE: a POST is not idempotent
    print("   ", wire.split("\r\n")[0], "|", wire.split("\r\n\r\n")[1])
    print()
```

```text
--> POST /api/notes HTTP/1.1   body: {"text": "steep 3 min"}
    HTTP/1.1 201 Created | {"id": 1042, "text": "steep 3 min"}

--> POST /api/notes HTTP/1.1   body: {"text": ""}
    HTTP/1.1 400 Bad Request | {"error": "field 'text' is required"}

--> POST /api/notes HTTP/1.1   body: {not json at all}
    HTTP/1.1 400 Bad Request | {"error": "invalid JSON: Expecting property name enclosed in double quotes"}

--> GET /api/notes HTTP/1.1   body: (none)
    HTTP/1.1 200 OK | {"notes": [{"id": 1042, "text": "steep 3 min"}]}

--> DELETE /api/notes HTTP/1.1   body: (none)
    HTTP/1.1 405 Method Not Allowed | method not allowed
```

Four things to notice. Only the **first** `POST` created a note, so the `GET`
lists exactly one — the two rejected posts never reached the store, which is
what validating *before* mutating buys you. The two `400`s distinguish "your
JSON is broken" from "your JSON is fine but the field is missing", and both
answer in JSON, because a client that asked for JSON should not receive an HTML
error page. The `GET` and the `POST` share a path and differ only by method,
and `resolve` handles that because the route table is keyed on the pair. And
the `DELETE` produced `405` rather than `404`: the path exists, the verb does
not, and the `Allow` header tells the client which verbs would have worked.

!!! note "Idempotency in your own hands"

    `create_note` is **not** idempotent by design: send it twice and you get
    two notes. If you want a client to be able to retry safely after a timeout,
    either use `PUT /api/notes/{id}` with a client-chosen id, or accept an
    `Idempotency-Key` header and remember it. Payment APIs do the latter.

## The ten-line real version

Everything above is the interesting half. The boring half — accept a TCP
connection, read bytes until the headers end, write bytes back — is in the
standard library. This is a complete static file server; the Run button cannot
execute it because it opens a socket, so save it and run it on your own
machine.

```text
# serve.py — run this on your own machine, not in the browser
from http.server import HTTPServer, SimpleHTTPRequestHandler

server = HTTPServer(("127.0.0.1", 8000), SimpleHTTPRequestHandler)
print("serving this folder at http://127.0.0.1:8000  (Ctrl-C to stop)")
server.serve_forever()
```

```console
$ cd folder-with-your-page-html
$ python serve.py
serving this folder at http://127.0.0.1:8000  (Ctrl-C to stop)

# or skip the file entirely — the module has a command-line interface:
$ python -m http.server 8000
```

Then open `http://127.0.0.1:8000/page.html` and you are looking at the page
from [42.1](01-html-css.md), delivered over real HTTP. `127.0.0.1` is
**localhost**, your own machine; nobody else can reach it. This server is for
development only — it is single-threaded and has no security hardening
whatsoever.

For applications, nobody writes the router by hand. Four you will meet:

- **Flask** (Python) — a microframework. You write
  `@app.route("/users/<int:user_id>")` above a function that returns a string
  or a response; everything else (sessions, templating via Jinja) is opt-in.
  The closest real thing to what you just built.
- **FastAPI** (Python) — asynchronous, and built around type hints: annotate a
  handler's parameters and it validates the request, converts the types, and
  generates interactive OpenAPI documentation from the same annotations.
- **Express** (JavaScript, on Node.js) — the middleware idea taken to its
  logical end. `app.use(...)` stacks layers, and `app.get("/users/:id", …)` is
  the route table above with a different punctuation for path parameters.
- **Spring Boot** (Java) — the enterprise standard, and what a Java course
  reaches for. A class annotated `@RestController` with methods annotated
  `@GetMapping("/users/{id}")`; the framework wires dependencies, serialises
  JSON, and embeds a Tomcat server so the application is a runnable jar.

## Static versus dynamic, and templates

A **static** response is a file read off disk and sent unchanged — HTML, CSS,
images, the JavaScript bundle. It is cacheable, fast, and safely served by a
CDN. A **dynamic** response is built per request by your code, because it
depends on who is asking or on data that changes. The usual way to build one is
a **template**: an HTML file with placeholders (`{{ user.name }}`, `{% for note
in notes %}`) that a template engine fills in — Jinja for Flask, Thymeleaf for
Spring, EJS for Express. It is the mail-merge idea from
[Chapter 14.3](../ch14-beyond/03-guis-and-beyond.md), industrialised, and its
one non-negotiable feature is **auto-escaping**: a template engine converts
`<` to `&lt;` in every substituted value by default, which is what stops a user
whose name is `<script>` from running code in every other user's browser.

## Security: the short version that actually matters

**Never trust anything that arrives in a request.** Not the body, not the query
string, not the path, not the headers, not the cookies — all of it is typed by
a stranger, and the form you wrote is not the only way to send it.

- **SQL injection.** Building a query by string concatenation —
  `"SELECT * FROM users WHERE email = '" + email + "'"` — lets input like
  `' OR '1'='1` rewrite your query. The fix is **parameterised queries**
  (`cursor.execute("… WHERE email = ?", (email,))`), where the driver sends the
  query and the data separately so the data can never become syntax. There is
  no correct way to do this with string formatting.
- **Cross-site scripting (XSS).** Putting user text into a page without
  escaping lets them inject `<script>`. Escape on output, always; let your
  template engine do it; see [42.3](03-javascript.md) for the client-side half.
- **Command injection and path traversal.** Never build a shell command from
  input, and never join user text onto a filesystem path — `../../etc/passwd`
  is a real filename.
- **Validate on the server, always.** The HTML `required` attribute stops
  nobody; the check that matters is the one in `create_note` above.
- **CORS is a browser rule, not a server defence.** The same-origin policy stops
  JavaScript on `evil.example` from *reading* a response from
  `teahouse.example`; `Access-Control-Allow-Origin` is how a server opts out of
  that restriction for named origins. It protects your users' browsers from
  other sites — it does nothing to stop anyone sending your server whatever they
  like with `curl`, so never treat CORS as authentication.
- **HTTPS everywhere.** Without TLS, every password, cookie, and page is
  readable and *editable* by anything between the user and you. Certificates
  are free, and `Strict-Transport-Security` tells browsers never to try plain
  HTTP for your domain again.

!!! warning "Common mistakes"

    - **Returning `200` with an error in the body.** Caches, retries, monitors,
      and client libraries all read the status code. Use `4xx` and `5xx`.
    - **Forgetting `Content-Length` or getting it wrong.** Compute it from the
      **encoded bytes**, not `len(string)`, or a non-ASCII page truncates.
    - **Treating `GET` as a way to change data.** It is defined as safe, so
      crawlers and prefetchers will follow every link on your page.
    - **Trusting the client.** Hidden form fields, disabled buttons, and
      `required` attributes are user-interface polish, not enforcement.
    - **Session cookies without `HttpOnly`, `Secure`, and `SameSite`.** One
      scripting hole then costs you every logged-in account.
    - **Leaking tracebacks in a 500.** The stack trace goes to your log; the
      client gets a plain apology and, ideally, an error id to quote.

## Check your understanding

??? success "1. Why can a browser safely retry a `GET` after a timeout, but not a `POST`?"

    `GET` is defined as **safe** (it changes nothing) and **idempotent**
    (repeating it has the same effect as doing it once), so a retry can never
    cause harm. `POST` is neither: it means "create something" or "do
    something", and a second delivery creates a second thing. That is exactly
    why browsers pop up a confirmation before re-submitting a form. If you need
    a retryable write, use `PUT` with a client-chosen id, or accept an
    idempotency key.

??? success "2. A request arrives for `/api/notes` with the verb `DELETE`, and no such route exists. Why is `405` more useful than `404`?"

    `404` says "there is nothing at this address"; `405` says "the address is
    real, your verb is not allowed here" and is required to carry an `Allow`
    header listing the verbs that are. The client learns something actionable,
    and a monitoring system can tell a broken link apart from a client using
    the wrong method. The runnable router distinguishes them by remembering
    which methods had a *path* match while looking for a *method* match.

??? success "3. HTTP is stateless. How does a site remember you are logged in?"

    It does not — the browser does the remembering. The server sends
    `Set-Cookie: session=<random id>` once; the browser attaches
    `Cookie: session=<id>` to every later request to that site; the server
    looks the id up in a session store. Nothing about the *protocol* has
    memory, and every request still stands alone — which is what lets any
    server in a fleet answer it. The cookie must carry `HttpOnly` (so
    JavaScript cannot read it), `Secure` (HTTPS only), and `SameSite` (not sent
    from other sites).

??? success "4. In the runnable server, why does the malformed request never appear in the access log?"

    The access log is written by `logging_middleware`, which only runs as part
    of the handler chain — and the chain is only built *after* the request has
    been parsed and routed. `parse_request` raised `BadRequest` first, so
    `handle` returned a `400` immediately and never reached the middleware.
    Real servers behave the same way, which is why malformed traffic shows up
    in an error log rather than the access log.
