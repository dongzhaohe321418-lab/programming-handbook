# Chapter 42 · Web and GUI Development

Every program you have written so far talks to a terminal. You print, the
terminal shows text; you read a file, the terminal shows more text. That is a
complete and honest way to write software, and it is also *not how anybody
outside this book experiences a program*. The software people actually use has
a window, or a page, or both — and the machinery that puts it there is the last
big piece of general programming knowledge that Parts I–IV left out. This
chapter installs it.

There are really only two families of user interface, and they share a
surprising amount of skeleton. A **web application** is a program whose events
arrive as HTTP requests over a network: a browser asks for a URL, your code
builds a response, the browser turns that response into a picture. A **desktop
application** is a program whose events arrive from a window system: the user
clicks, your handler runs, the toolkit repaints. Underneath both sits the same
idea you already met in
[Chapter 14.3](../ch14-beyond/03-guis-and-beyond.md) — a queue of events, a
dictionary of handlers, and a loop that dispatches. What changes is the
vocabulary, the failure modes, and the amount of stuff between your function
and the pixel.

The awkward part of teaching this in a browser-run book is that the Run button
cannot render a web page, open a network socket, or pop up a desktop window.
So this chapter does something better than pretending. Every piece of real
HTML, CSS, JavaScript, and JavaFX appears in its own fence with instructions to
**save it to a file on your own machine and open it**, exactly as you would at
work. And every concept underneath those languages is rebuilt in runnable
Python: a DOM parser and CSS selector matcher, an HTTP request parser and
router with middleware, an event loop with a microtask queue, and a GUI layout
and hit-testing engine. By the end you will have written, and watched run, the
core of a web framework, a CSS engine, a JavaScript runtime, and a widget
toolkit. Frameworks stop being magic the moment you have built the small
honest version.

## After this chapter you can …

- explain what a web page *is* — a text document a browser parses into a tree —
  and write correct, semantic, accessible HTML from an empty file;
- use CSS confidently: the three ways to attach it, every common selector,
  specificity (and how to debug a rule that will not apply), the box model and
  `box-sizing: border-box`, flexbox, and mobile-first media queries;
- parse HTML into a node tree with `html.parser` and implement a CSS selector
  matcher that resolves tag, class, id, and descendant selectors;
- narrate every step between typing a URL and seeing a page: DNS, TCP, TLS,
  the HTTP request, the server, the response, the render;
- read and write raw HTTP by hand — request line, methods, status codes,
  headers, body — and explain why the protocol is stateless and what cookies,
  sessions, and tokens do about it;
- build the brain of a web server in pure Python: a request parser, a regex
  router with path parameters, handlers, a response serializer, and a
  middleware chain;
- name what Flask, FastAPI, Express, and Spring Boot actually do for you, and
  start a real static server with `http.server` in one line;
- design a JSON API, and state the security rules — never trust input, escape
  on output, use parameterised queries, prefer HTTPS;
- write browser JavaScript as a Python programmer: `let`/`const`, `===`,
  truthiness, arrow functions, objects, and the DOM API;
- attach event listeners, use the event object, and explain bubbling and
  `preventDefault`;
- explain the event loop, the task queue, and the microtask queue well enough
  to predict the output order of any `setTimeout`/promise puzzle;
- use `fetch` with `async`/`await` to call a JSON endpoint and update a page;
- build a desktop GUI in JavaFX — `Application`, `Stage`, `Scene`, controls,
  layout panes, lambda handlers, properties and binding, FXML, CSS, and
  background work with `Task` and `Platform.runLater()`;
- state the UI-thread rule and diagnose the frozen-window bug;
- implement a widget tree with a layout pass, hit testing, event bubbling, and
  dirty-tracking re-render;
- choose sensibly between a web app, a desktop app, and a terminal program.

## Prerequisites

- [Chapter 9 · Collections](../ch09-collections/index.md) — dictionaries are
  the header map, the router table, and the handler registry.
- [Chapter 12 · Classes](../ch12-classes/index.md) and
  [Chapter 13 · Design](../ch13-design/index.md) — nodes, widgets, requests, and
  responses are all small classes; the GUI model is a composite tree.
- [Chapter 14.3 · GUIs and other directions](../ch14-beyond/03-guis-and-beyond.md)
  — the event-loop idea and the first `tkinter` sketch. This chapter assumes it
  and does not repeat it.
- [Chapter 17 · Recursion](../ch17-recursion/index.md) — a DOM tree and a widget
  tree are walked recursively, and so are layout and rendering.
- [Chapter 41 · Regular Expressions](../ch41-regex/index.md) — the router turns
  `/users/{id}` into a pattern with a named group, straight out of
  [41.2](../ch41-regex/02-groups-parsing.md).
- Helpful, not required:
  [Chapter 23.1](../ch23-os/01-os-processes.md) for threads and scheduling —
  the reason a single-threaded UI freezes; and
  [Chapter 39.1](../ch39-streams/01-lambdas.md) for lambdas, which are how
  JavaFX and JavaScript both write event handlers.

## Sections

1. [42.1 HTML and CSS](01-html-css.md) — what a page really is, the document
   tree, HTML elements and semantics, forms, tables, ids versus classes,
   the browser's famous error tolerance; then CSS: attaching styles, every
   selector type, a specificity table, a "why isn't my style applying" triage,
   the box model and `border-box`, flexbox, grid, and mobile-first responsive
   design — plus a runnable DOM parser and CSS selector matcher in Python.
2. [42.2 HTTP and a web server from scratch](02-http-server.md) — DNS to
   pixels in one sequence diagram, the URL dissected, HTTP as plain text,
   methods, status codes, headers, cookies and sessions; then the centrepiece:
   a request parser, a regex router with path parameters, handlers, a response
   serializer, and a middleware chain, all in runnable Python, followed by the
   ten-line real version and an honest security section.
3. [42.3 JavaScript in the browser](03-javascript.md) — JavaScript for a Python
   programmer, the DOM API and why `textContent` beats `innerHTML`, events and
   bubbling, a complete save-and-open interactive page, then asynchrony from
   first principles: the single thread, the task queue, the microtask queue,
   callbacks to promises to `async`/`await`, `fetch`, modules, build steps, and
   frameworks — with a runnable Python model of the event loop that predicts
   the classic ordering puzzle.
4. [42.4 Desktop GUIs — JavaFX and tkinter](04-desktop-gui.md) — when a desktop
   app is the right answer, the universal GUI concepts, JavaFX in full
   (`Stage`, `Scene`, controls, panes, lambdas, properties and binding, FXML,
   CSS, `Task`), the same app in tkinter, and a runnable headless GUI engine in
   Python with layout, hit testing, bubbling, and dirty-tracked re-render.
5. [Exercises](exercises.md) — fix broken and inaccessible HTML, resolve a
   specificity fight, parse a raw HTTP request by hand, add a route, predict
   the event-loop output, find and fix an XSS hole, extend the widget model,
   and finish by adding cookie-based sessions to the router you built.
