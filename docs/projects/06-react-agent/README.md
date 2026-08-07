# Project 6 · A ReAct Agent from Scratch

[Chapter 30](../../ch30-agents/index.md) built an agent in ninety lines and
then broke it four different ways. This project builds the version that
survives being broken: a tool registry that validates arguments before it
runs anything, a parser that hands the model a *repair message* instead of a
traceback, a loop guard, a step budget, a memory that summarises itself when
the context bill gets too high, a tracer that prints the whole episode as a
span tree, and a five-task eval that tells you whether any of it works.

No framework. That is the point — every framework in
[30.4](../../ch30-agents/04-frameworks.md) is these same parts with
configuration on top, and you will read their source much faster having
written yours.

## What you'll build

An agent that solves a task no single tool can, and a harness that measures
it. Here is the tail of the trace, the span tree, and the eval:

```text
--- step 4 ------------------------------------------------
Thought: The answer must be in feet; look up the factor.
Action: wiki {"query": "metres to feet"}
Observation: Unit conversion: one metre is 3.28084 feet.
[memory] over budget at 156 tokens: summarised 2 turn(s) into 2 facts, history now 108 (budget 120)
--- step 5 ------------------------------------------------
Thought: Convert the 191 m gap into feet.
Action: calc {"expression": "191 * 3.28084"}
Observation: 191 * 3.28084 = 626.6404
...
--- step 8 ------------------------------------------------
Thought: I have the gap, in feet, saved and verified.
Final Answer: The Eiffel Tower is 626.6404 ft taller than the Great Pyramid, saved as note 'height_gap'.

agent.run                                 steps=8 solved=True
├─ step.1
│  ├─ llm.decide                          ctx=168
│  ├─ tool.wiki                           ok=True
│  └─ memory.append                       turns=1 facts=0
...
├─ step.4
│  ├─ llm.decide                          ctx=286
│  ├─ tool.wiki                           ok=True
│  └─ memory.append                       turns=2 facts=2
│     └─ memory.summarise                 moved=2 facts=2

task             ok  steps  repairs  guards  tool errs  peak ctx
height gap        Y      8        0       0          0       309
typo recovery     Y      4        0       1          0       276
bad tool name     Y      3        0       0          1       242
bad formatting    Y      3        1       0          0       241
never stops       N     10        0       9          0       309

success rate            4/5 = 80%
median steps to success 3.5
guard activations       loop 10, parse repairs 1, tool errors 1
```

Four of five tasks succeed, and the one that fails does so *safely* — the
step budget stops it after ten steps and the loop guard fires nine times on
the way. That last row is the whole reason the guards exist.

## What it exercises

- [30.1 The agent loop and ReAct](../../ch30-agents/01-agent-loop-react.md)
  — the Thought/Action/Observation cycle, the step budget, the loop guard,
  and the rule that *your program* writes the `Observation` lines.
- [30.4 Frameworks and production concerns](../../ch30-agents/04-frameworks.md)
  — spans, traces, and the reason a swallowed error must still be recorded.
- [29.3 Agent memory and context management](../../ch29-memory-rag/03-agent-memory.md)
  — the context is a budget you pay every turn; summarise the old, keep the
  recent.
- [28.1 Function calling and JSON Schema](../../ch28-tools-mcp/01-function-calling.md)
  — arguments arrive as JSON and get validated before anything runs.
- [Chapter 13 · Program Design](../../ch13-design/index.md) — five small
  classes with one job each, assembled by a loop that knows about none of
  their internals.
- [Chapter 41 · Regular Expressions](../../ch41-regex/index.md) — the
  policy reads its numbers back out of earlier observations with `re`,
  which is what makes it *react* rather than replay.

## Milestones

### Milestone 1 — the bare loop

**Goal:** `run_agent(goal, llm, registry, max_steps)` with a transcript
string, a policy that is any callable taking text and returning text, and a
hard step budget. One tool is enough to start.

**Done when...** a policy that returns `Final Answer:` on its second reply
finishes in two steps; a policy that never returns one stops at `max_steps`
and returns no answer; and the loop prints a readable
Thought / Action / Observation block per step.

??? tip "Hint"

    Write the budget into the signature on the very first draft. A `while
    True` you intend to fix later is how you find out what your API bill
    looks like:

    ```python
    def run(goal, policy, tools, max_steps=4):
        """The whole idea: the POLICY decides what happens next, not you."""
        transcript = f"Goal: {goal}\n"
        for step in range(1, max_steps + 1):
            action = policy(transcript)
            if action == "STOP":
                return f"finished in {step} steps"
            transcript += f"Observation: {tools[action](transcript)}\n"
        return f"budget of {max_steps} steps exhausted"

    tools = {"count": lambda t: f"{len(t)} characters so far"}
    print(run("count things", lambda t: "STOP" if "characters" in t
              else "count", tools))
    print(run("count things", lambda t: "count", tools))
    ```

    The second call is the important one. It is not a bug in the policy that
    you can fix; it is a property of handing control flow to something you
    do not control.

### Milestone 2 — a tool registry that validates

**Goal:** a `Tool` holding a name, a description, a parameter spec (`type`,
`required`, `help`) and a function; a `Registry` that can `describe()` itself
as prompt text and `call(name, arguments)` without ever raising.

**Done when...** an unknown tool name returns a `TOOL ERROR` string that
*lists the available tools*; a missing or misspelled argument returns an
`ARGUMENT ERROR` naming it; an exception inside a tool becomes text; and
`registry.describe()` produces a menu you would be happy to paste into a
prompt.

??? tip "Hint"

    Every error string an agent can see is a prompt, so write it like one.
    Compare the two messages below: only one of them lets the next step
    succeed.

    ```python
    TOOLS = {"wiki": lambda q: f"article about {q}", "calc": lambda e: "42"}

    def call_bad(name, argument):
        if name not in TOOLS:
            return "error: unknown tool"
        return TOOLS[name](argument)

    def call_good(name, argument):
        if name not in TOOLS:
            return (f"TOOL ERROR: no tool named {name!r}. Available tools: "
                    f"{', '.join(TOOLS)}.")
        return TOOLS[name](argument)

    print(call_bad("web_search", "Paris"))
    print(call_good("web_search", "Paris"))
    ```

    Never write `tools[name](...)` without checking membership first. A
    `KeyError` kills the run; a corrective observation costs one step, and
    [30.1](../../ch30-agents/01-agent-loop-react.md) shows the model
    recovering from exactly this message.

### Milestone 3 — a parser with a repair path

**Goal:** `parse(reply)` returning kind `final`, `act`, or `unparsed`. Take
`Action Input` as a **JSON object** so arguments are named and typed, and
make every `unparsed` result carry a `repair` string written for the model.

**Done when...** a well-formed reply parses; a reply with `Action` and no
`Action Input` produces a repair message that shows the expected JSON shape;
`Action Input: query=Paris` produces a repair message quoting what it
actually received; a JSON array instead of an object is rejected; and the
loop feeds that repair message back as the observation instead of crashing.

??? tip "Hint"

    Order matters when you scan for field names: `Action Input` must be
    tested before `Action`, or every input line is parsed as an action.

    ```python
    import json

    def parse(reply):
        fields = {}
        for line in reply.splitlines():
            for tag in ("Thought", "Action Input", "Action", "Final Answer"):
                if line.strip().startswith(tag + ":"):
                    fields[tag] = line.strip()[len(tag) + 1:].strip()
                    break                       # longest tag wins
        if "Action Input" not in fields:
            return {"kind": "unparsed",
                    "repair": "PARSE ERROR: add an 'Action Input:' line "
                              'containing a JSON object, e.g. {"query": "x"}.'}
        try:
            return {"kind": "act", "arguments": json.loads(fields["Action Input"])}
        except json.JSONDecodeError:
            return {"kind": "unparsed",
                    "repair": f"PARSE ERROR: Action Input was "
                              f"{fields['Action Input']!r}, which is not JSON."}

    print(parse('Action: wiki\nAction Input: {"query": "Paris"}'))
    print(parse("Action: wiki\nAction Input: query=Paris"))
    ```

    A repair message that quotes what the model actually sent is worth far
    more than one that only restates the rule, because the model can see the
    difference between the two.

### Milestone 4 — memory on a token budget

**Goal:** a `BudgetedMemory` that assembles the prompt from a fixed prefix
(goal plus tool menu) and a *history* (distilled facts plus the last `keep`
turns verbatim). When the history exceeds `budget`, roll the oldest turns
into facts until it fits.

**Done when...** the history stays under budget while there are more than
`keep` turns to compress; the facts a later step depends on survive the
compression; and you can print the exact context the model saw on its last
call and read it as a sensible prompt.

??? tip "Hint"

    Split the prompt into the part that cannot shrink and the part that can.
    The goal and the tool menu are fixed overhead on every single call — in
    our run, 168 of the final 309 tokens — and no summariser may touch them.

    ```python
    def approx_tokens(text):
        """Rough English rule of thumb: about four characters per token."""
        return len(text) // 4

    turns = [f"Thought: step {i}\nObservation: result {i}" for i in range(1, 6)]
    keep, budget = 2, 12
    facts = []
    while approx_tokens("\n".join(facts + turns)) > budget and len(turns) > keep:
        oldest, turns = turns[0], turns[1:]
        facts.append("- " + oldest.splitlines()[-1])
    print("facts:", facts)
    print("verbatim:", len(turns), "turns")
    print("history:", approx_tokens("\n".join(facts + turns)), "tokens")
    ```

    Notice what the compression throws away: the `Thought` lines, which are
    reasoning about a situation that has already resolved. That is why
    keeping observations while dropping thoughts compresses so well — and
    why a summariser that drops an observation breaks the agent two steps
    later.

### Milestone 5 — the guards

**Goal:** three guards, all of which write into the transcript rather than
raising: the step budget from milestone 1, a **loop guard** that fingerprints
each action as `(tool, normalised arguments)` and refuses a repeat, and the
tool/argument errors from milestone 2.

**Done when...** a policy that misspells a lookup and repeats the identical
call gets `LOOP GUARD: you already ran … Try a different action or input.`
on its second attempt, changes its input on the third, and finishes on the
fourth; and a policy that never stops burns exactly `max_steps` steps and
returns no answer.

??? tip "Hint"

    Normalising the fingerprint is what makes the guard fire at all —
    without it, `"Eiffel Tower"` and `" eiffel tower "` are two different
    actions:

    ```python
    import json

    def fingerprint(tool, arguments):
        return tool, json.dumps({k: str(v).strip().lower()
                                 for k, v in sorted(arguments.items())})

    a = fingerprint("wiki", {"query": "Eiffel Tower"})
    b = fingerprint("wiki", {"query": " eiffel tower "})
    print(a)
    print("same action?", a == b)
    ```

    The cost is false positives: two genuinely different calls that differ
    only in case are treated as a repeat. For a tool where whitespace or
    case is meaningful — a shell command, a password check — fingerprint the
    raw arguments instead.

### Milestone 6 — tracing, then a five-task eval

**Goal:** a `Tracer` whose `span(name, **attributes)` context manager records
nesting from a stack and prints a tree, plus an eval over five tasks that
reports success rate, median steps to success, and the guard counts.

**Done when...** the tree shows `agent.run` at the root with one `step.N`
subtree each, `memory.summarise` nested *inside* `memory.append` on the steps
where it fired, no wall-clock numbers anywhere, and an eval table with one
row per task and a success rate at the bottom.

??? tip "Hint"

    Use a tick counter, not a clock. A trace with real timings is different
    on every run, so you cannot diff two runs or paste one into a bug
    report:

    ```python
    import contextlib

    class Tracer:
        def __init__(self):
            self.roots, self._stack, self.clock = [], [], 0

        @contextlib.contextmanager
        def span(self, name):
            node = {"name": name, "depth": len(self._stack), "children": []}
            (self._stack[-1]["children"] if self._stack
             else self.roots).append(node)
            self._stack.append(node)
            self.clock += 1
            try:
                yield node
            finally:
                self.clock += 1
                self._stack.pop()

    tracer = Tracer()
    with tracer.span("agent.run"):
        with tracer.span("tool.wiki"):
            pass
        with tracer.span("tool.calc"):
            pass
    print(tracer.roots[0]["name"], "->",
          [c["name"] for c in tracer.roots[0]["children"]],
          f"({tracer.clock} ticks)")
    ```

    Record errors as a span *attribute* and re-raise, so a failure the agent
    catches and ignores still shows up in the tree. An agent quietly
    retrying around a broken tool looks perfectly healthy from the outside.

## Reference implementation

Build yours milestone by milestone — the guards are much easier to
appreciate after you have watched a run without them.

??? success "Full reference implementation"

    ```python
    """A ReAct agent: tools, a parser, guards, budgeted memory, and a tracer."""
    import contextlib
    import json
    import re
    from dataclasses import dataclass, field
    from statistics import median

    # ============================== the tracer ================================


    class Tracer:
        """Records nested spans and prints them as a tree.

        A real tracer — LangSmith, Arize Phoenix, W&B Weave — stamps wall-clock
        times and ships spans to a server. Ours counts ticks instead, so the
        printed tree is byte-identical on every machine and every run.
        """

        def __init__(self):
            self.roots, self._stack, self.clock = [], [], 0

        @contextlib.contextmanager
        def span(self, name, **attributes):
            """Open one span; nesting comes from the stack, not from the caller."""
            node = {"name": name, "attributes": attributes, "children": [],
                    "start": self.clock, "end": None, "error": None}
            parent = self._stack[-1]["children"] if self._stack else self.roots
            parent.append(node)
            self._stack.append(node)
            self.clock += 1
            try:
                yield node
            except Exception as exc:
                node["error"] = type(exc).__name__     # errors are attributes
                raise
            finally:
                self.clock += 1
                node["end"] = self.clock
                self._stack.pop()

        def count(self):
            """(spans, spans that recorded an error) over the whole tree."""
            total = errors = 0
            stack = list(self.roots)
            while stack:
                node = stack.pop()
                total += 1
                errors += node["error"] is not None
                stack.extend(node["children"])
            return total, errors

        def print_tree(self):
            """Print every span, deepest last, with no timings to drift."""
            def walk(node, prefix, is_last, is_root):
                attributes = " ".join(f"{k}={v}" for k, v in
                                      node["attributes"].items())
                flag = f"  !! {node['error']}" if node["error"] else ""
                head = "" if is_root else ("└─ " if is_last else "├─ ")
                label = f"{prefix}{head}{node['name']}"
                print(f"{label:<42}{attributes}{flag}".rstrip())
                child_prefix = prefix + ("" if is_root else
                                         ("   " if is_last else "│  "))
                for i, child in enumerate(node["children"]):
                    walk(child, child_prefix, i == len(node["children"]) - 1, False)

            for i, root in enumerate(self.roots):
                walk(root, "", i == len(self.roots) - 1, True)


    # =========================== the tool registry ============================
    class Tool:
        """A Python function plus the metadata a model needs to choose it."""

        def __init__(self, name, description, params, fn):
            self.name, self.description, self.params, self.fn = (
                name, description, params, fn)

        def problems(self, arguments):
            """Validate arguments before running. Empty list means go ahead."""
            found = []
            for key, spec in sorted(self.params.items()):
                if spec["required"] and key not in arguments:
                    found.append(f"missing required argument {key!r} "
                                 f"({spec['help']})")
            for key, value in sorted(arguments.items()):
                if key not in self.params:
                    found.append(f"unknown argument {key!r}; this tool takes "
                                 f"{sorted(self.params)}")
                elif not isinstance(value, self.params[key]["type"]):
                    found.append(f"argument {key!r} must be a "
                                 f"{self.params[key]['type'].__name__}")
            return found

        def signature(self):
            return ", ".join(f"{k}: {v['type'].__name__}"
                             for k, v in sorted(self.params.items()))


    class Registry:
        """The tool menu. Its `describe()` output goes straight into the prompt."""

        def __init__(self):
            self.tools = {}

        def add(self, name, description, params, fn):
            self.tools[name] = Tool(name, description, params, fn)
            return self

        def describe(self):
            return "\n".join(f"- {t.name}({t.signature()}): {t.description}"
                             for t in self.tools.values())

        def call(self, name, arguments):
            """Run one tool. Returns (ok, observation) — never raises upward.

            Every failure comes back as *text the model can read*, because the
            model is the only thing that can recover from it.
            """
            if name not in self.tools:
                return False, (f"TOOL ERROR: no tool named {name!r}. Available "
                               f"tools: {', '.join(self.tools)}.")
            tool = self.tools[name]
            problems = tool.problems(arguments)
            if problems:
                return False, "ARGUMENT ERROR: " + "; ".join(problems)
            try:
                return True, str(tool.fn(**arguments))
            except Exception as exc:
                return False, f"TOOL ERROR: {type(exc).__name__}: {exc}"


    # ================================ tools ===================================
    WIKI = {
        "eiffel tower": "The Eiffel Tower stands in Paris, France. Height: 330 m.",
        "great pyramid": "The Great Pyramid of Giza is near Cairo. Height: 139 m.",
        "empire state building": "The Empire State Building is in New York. "
                                 "Height: 443 m.",
        "metres to feet": "Unit conversion: one metre is 3.28084 feet.",
    }


    def wiki(query):
        """Look a title up in a four-article in-memory encyclopedia."""
        key = query.strip().strip('"').lower()
        for title, article in WIKI.items():
            if key in title or title in key:
                return article
        return f"No article titled {query!r}. Known titles: {', '.join(WIKI)}."


    def calc(expression):
        """Arithmetic on two numbers. We match the three parts with a regular
        expression instead of calling eval() on model output — a calculator can
        only ever return a number, but eval() can do anything."""
        match = re.fullmatch(r"\s*(-?[\d.]+)\s*([-+*/])\s*(-?[\d.]+)\s*",
                             expression)
        if not match:
            raise ValueError("calc takes '<number> <op> <number>', e.g. '12 * 4'")
        left, operator, right = float(match[1]), match[2], float(match[3])
        if operator == "/" and right == 0:
            raise ZeroDivisionError("division by zero")
        value = {"+": left + right, "-": left - right, "*": left * right,
                 "/": left / right if right else 0.0}[operator]
        return f"{expression.strip()} = {round(value, 4)}"


    NOTEBOOK = {}          # the tool state the agent is allowed to mutate


    def save_note(key, text):
        """Write one note. Idempotent: saving the same key twice is one note."""
        NOTEBOOK[key] = text
        return f"saved note {key!r} ({len(text)} characters)"


    def list_notes():
        """Read the notebook back, so a mutation is observable."""
        if not NOTEBOOK:
            return "notebook: (empty)"
        return "notebook: " + ", ".join(sorted(NOTEBOOK))


    def build_registry():
        """Descriptions are prompts. Every one names its units and its failure."""
        return (Registry()
                .add("wiki", "Look up one landmark or unit-conversion article by "
                             "title. Returns the article text, or a line listing "
                             "the known titles if there is no match.",
                     {"query": {"type": str, "required": True,
                                "help": "an article title, e.g. Eiffel Tower"}},
                     wiki)
                .add("calc", "Evaluate one arithmetic expression on exactly two "
                             "numbers, e.g. '330 - 139'. Returns "
                             "'<expression> = <value>' rounded to 4 decimals.",
                     {"expression": {"type": str, "required": True,
                                     "help": "'<number> <op> <number>'"}},
                     calc)
                .add("save_note", "Store a short piece of text under a key so it "
                                  "survives the rest of the run. Overwrites an "
                                  "existing key.",
                     {"key": {"type": str, "required": True,
                              "help": "a short identifier"},
                      "text": {"type": str, "required": True,
                               "help": "the text to store"}},
                     save_note)
                .add("list_notes", "List the keys currently in the notebook. "
                                   "Takes no arguments.",
                     {}, list_notes))


    # ================================ parser ==================================
    FIELDS = ("Thought", "Action Input", "Action", "Final Answer")


    def parse(reply):
        """Turn a model reply into a decision dict.

        Returns kind 'final', 'act', or 'unparsed' — and 'unparsed' carries a
        `repair` message written *for the model*, because that message is the
        only thing that can make the next reply better.
        """
        fields = {}
        for line in reply.splitlines():
            for tag in FIELDS:                    # longest tags first: see FIELDS
                if line.strip().startswith(tag + ":"):
                    fields[tag] = line.strip()[len(tag) + 1:].strip()
                    break
        if "Final Answer" in fields:
            return {"kind": "final", "text": fields["Final Answer"], **fields}
        if "Action" not in fields:
            return {"kind": "unparsed", "repair": (
                "PARSE ERROR: reply with 'Action:' and 'Action Input:' lines, "
                "or with a 'Final Answer:' line."), **fields}
        if "Action Input" not in fields:
            return {"kind": "unparsed", "repair": (
                "PARSE ERROR: you gave an Action with no 'Action Input:' line. "
                'Action Input must be a JSON object, e.g. {"query": "Paris"}.'),
                **fields}
        try:
            arguments = json.loads(fields["Action Input"])
        except json.JSONDecodeError:
            return {"kind": "unparsed", "repair": (
                f"PARSE ERROR: Action Input was {fields['Action Input']!r}, which "
                'is not JSON. Send a JSON object, e.g. {"query": "Paris"}.'),
                **fields}
        if not isinstance(arguments, dict):
            return {"kind": "unparsed", "repair": (
                "PARSE ERROR: Action Input must be a JSON *object* with named "
                "arguments, not a bare value."), **fields}
        return {"kind": "act", "tool": fields["Action"], "arguments": arguments,
                **fields}


    # ================================ memory ==================================
    def approx_tokens(text):
        """Rough English rule of thumb: about four characters per token."""
        return len(text) // 4


    def summarise_turns(turns):
        """Stand-in for 'ask the model to distil these turns into facts'.

        Rule-based so the output is identical on every run, but it does the same
        job a real summariser does: throw away the reasoning and the mechanics,
        keep what an observation actually established.
        """
        facts = []
        for turn in turns:
            for line in turn["observation"].splitlines():
                line = line.strip()
                if line and line not in facts:
                    facts.append(line)
        return facts


    class BudgetedMemory:
        """Goal + tool menu + distilled facts + the last few turns verbatim.

        A ReAct transcript only ever grows, and you resend all of it every step,
        so the history is a budget you pay on every call. The *prefix* — goal
        plus tool menu — is fixed overhead and is not negotiable; the budget
        governs the history. When the history exceeds it, the oldest turns are
        summarised into facts until it fits, and the newest `keep` turns are
        never touched.
        """

        def __init__(self, goal, tool_menu, budget=120, keep=2,
                     summarise=summarise_turns, tracer=None):
            self.goal, self.tool_menu = goal, tool_menu
            self.budget, self.keep, self.summarise = budget, keep, summarise
            self.tracer = tracer
            self.turns, self.facts = [], []
            self.summarised_turns = 0
            self.peak_tokens = 0
            self.last_shrink = (0, 0)      # history tokens before -> after

        @contextlib.contextmanager
        def _span(self, name):
            """Trace this work if a tracer is attached; stay silent if not."""
            if self.tracer is None:
                yield {"attributes": {}}
            else:
                with self.tracer.span(name) as node:
                    yield node

        def prefix(self):
            """The part of the prompt that never changes — and never shrinks."""
            return f"Goal: {self.goal}\nTools you may use:\n{self.tool_menu}"

        def history(self):
            """Distilled facts plus the recent turns, verbatim."""
            parts = []
            if self.facts:
                parts.append("Established so far:")
                parts += [f"- {fact}" for fact in self.facts]
            if self.turns:
                parts.append("Recent steps:")
                for turn in self.turns:
                    parts.append(f"Thought: {turn['thought']}")
                    parts.append(f"Action: {turn['action']}")
                    parts.append(f"Observation: {turn['observation']}")
            return "\n".join(parts)

        def context(self):
            """Assemble the prompt exactly as the model will see it."""
            return f"{self.prefix()}\n{self.history()}" if self.turns or self.facts \
                else self.prefix()

        def add(self, thought, action, observation):
            """Record one step, then shrink the history if it is over budget."""
            self.turns.append({"thought": thought, "action": action,
                               "observation": observation})
            moved = self._shrink()
            self.peak_tokens = max(self.peak_tokens, approx_tokens(self.context()))
            return moved

        def over_budget(self):
            return approx_tokens(self.history()) > self.budget

        def _shrink(self):
            """Roll the oldest turns into facts until the history fits."""
            if not self.over_budget():
                return 0
            before = approx_tokens(self.history())
            with self._span("memory.summarise") as span:
                moved = 0
                while self.over_budget() and len(self.turns) > self.keep:
                    oldest, self.turns = self.turns[:1], self.turns[1:]
                    for fact in self.summarise(oldest):
                        if fact not in self.facts:
                            self.facts.append(fact)
                    moved += 1
                span["attributes"].update(moved=moved, facts=len(self.facts))
            self.last_shrink = (before, approx_tokens(self.history()))
            self.summarised_turns += moved
            return moved


    # =============================== the loop =================================
    @dataclass
    class RunResult:
        """Everything an eval needs to know about one episode."""
        goal: str
        answer: str = None
        steps: int = 0
        repairs: int = 0
        guard_hits: int = 0
        tool_errors: int = 0
        peak_tokens: int = 0
        summarised: int = 0
        actions: list = field(default_factory=list)

        @property
        def solved(self):
            return self.answer is not None


    def fingerprint(tool, arguments):
        """An action's identity: the tool plus its normalised arguments."""
        return tool, json.dumps({k: str(v).strip().lower()
                                 for k, v in sorted(arguments.items())})


    def run_agent(goal, llm, registry, tracer=None, max_steps=10, budget=120,
                  verbose=True):
        """The agent loop: decide, act, observe, remember — with every guard on."""
        tracer = tracer or Tracer()
        memory = BudgetedMemory(goal, registry.describe(), budget=budget,
                                tracer=tracer)
        result = RunResult(goal)
        seen = set()

        with tracer.span("agent.run", steps=0) as run_span:
            for step in range(1, max_steps + 1):
                result.steps = step
                with tracer.span(f"step.{step}"):
                    with tracer.span("llm.decide") as decide_span:
                        context = memory.context()
                        decide_span["attributes"]["ctx"] = approx_tokens(context)
                        reply = llm(context)          # <-- the one line to swap
                    decision = parse(reply)
                    thought = decision.get("Thought", "(none given)")
                    if verbose:
                        print(f"--- step {step} " + "-" * 48)
                        print(f"Thought: {thought}")

                    if decision["kind"] == "final":
                        result.answer = decision["text"]
                        if verbose:
                            print(f"Final Answer: {result.answer}")
                        run_span["attributes"]["steps"] = step
                        run_span["attributes"]["solved"] = True
                        result.peak_tokens = memory.peak_tokens
                        result.summarised = memory.summarised_turns
                        return result, memory, tracer

                    if decision["kind"] == "unparsed":
                        result.repairs += 1
                        action, observation = "(unparsed reply)", decision["repair"]
                        with tracer.span("guard.parse_repair"):
                            pass
                    else:
                        tool = decision["tool"]
                        arguments = decision["arguments"]
                        action = f"{tool} {json.dumps(arguments, sort_keys=True)}"
                        mark = fingerprint(tool, arguments)
                        if mark in seen:
                            result.guard_hits += 1
                            observation = (
                                f"LOOP GUARD: you already ran {action} and it did "
                                "not help. Try a different action or input.")
                            with tracer.span("guard.loop", action=tool):
                                pass
                        else:
                            seen.add(mark)
                            with tracer.span(f"tool.{tool}") as tool_span:
                                ok, observation = registry.call(tool, arguments)
                                tool_span["attributes"]["ok"] = ok
                            result.tool_errors += not ok
                            result.actions.append(action)

                    if verbose:
                        print(f"Action: {action}")
                        print(f"Observation: {observation}")

                    with tracer.span("memory.append") as memory_span:
                        moved = memory.add(thought, action, observation)
                        memory_span["attributes"]["turns"] = len(memory.turns)
                        memory_span["attributes"]["facts"] = len(memory.facts)
                    if moved and verbose:
                        was, now = memory.last_shrink
                        print(f"[memory] over budget at {was} tokens: summarised "
                              f"{moved} turn(s) into {len(memory.facts)} facts, "
                              f"history now {now} (budget {memory.budget})")

            result.summarised = memory.summarised_turns
            result.peak_tokens = memory.peak_tokens
            run_span["attributes"]["steps"] = result.steps
            run_span["attributes"]["solved"] = False
            if verbose:
                print(f"--- budget of {max_steps} steps exhausted, no answer ---")
            return result, memory, tracer


    # ============================== the policies ==============================
    class HeightGapLLM:
        """A rule-based policy standing in for a real chat model.

        A real model is a function from prompt text to reply text, and so is
        this. Every rule fires on something still MISSING from the context and
        reads its numbers back out of earlier observations, so the policy reacts
        to what the tools returned instead of replaying a script.
        """

        def __call__(self, context):
            def act(tool, arguments, thought):
                return (f"Thought: {thought}\nAction: {tool}\n"
                        f"Action Input: {json.dumps(arguments)}")

            if "Height: 330 m" not in context:
                return act("wiki", {"query": "Eiffel Tower"},
                           "I need the tower's height before I can compare.")
            if "Height: 139 m" not in context:
                return act("wiki", {"query": "Great Pyramid"},
                           "Now the pyramid's height, for the same reason.")
            tall, short = re.findall(r"Height: (\d+) m", context)[:2]
            if "= 191.0" not in context:
                return act("calc", {"expression": f"{tall} - {short}"},
                           "Both heights are in metres, so subtract them.")
            if "3.28084" not in context:
                return act("wiki", {"query": "metres to feet"},
                           "The answer must be in feet; look up the factor.")
            factor = re.search(r"one metre is ([\d.]+) feet", context)[1]
            if "= 626.6404" not in context:
                return act("calc", {"expression": f"191 * {factor}"},
                           "Convert the 191 m gap into feet.")
            if "saved note" not in context:
                return act("save_note",
                           {"key": "height_gap",
                            "text": "Eiffel Tower is 626.6404 ft taller than the "
                                    "Great Pyramid."},
                           "Store the result before I lose it.")
            if "notebook:" not in context:
                return act("list_notes", {},
                           "Confirm the note really landed in the notebook.")
            return ("Thought: I have the gap, in feet, saved and verified.\n"
                    "Final Answer: The Eiffel Tower is 626.6404 ft taller than "
                    "the Great Pyramid, saved as note 'height_gap'.")


    class TypoLLM:
        """Misspells a title, repeats the mistake, then reads the loop guard."""

        def __call__(self, context):
            if "Height: 139 m" in context:
                return "Thought: Found it.\nFinal Answer: 139 metres."
            if "LOOP GUARD" not in context:
                return ('Thought: Look the pyramid up.\nAction: wiki\n'
                        'Action Input: {"query": "Grate Pyramid"}')
            return ('Thought: That exact call already failed; fix my spelling.\n'
                    'Action: wiki\nAction Input: {"query": "Great Pyramid"}')


    class HallucinatingLLM:
        """Invents a tool, then recovers from an error message that lists the
        real ones."""

        def __call__(self, context):
            if "TOOL ERROR" not in context:
                return ('Thought: I will search the web for the height.\n'
                        'Action: web_search\n'
                        'Action Input: {"query": "Eiffel Tower height"}')
            if "Height: 330 m" not in context:
                return ('Thought: There is no web_search here, but wiki exists.\n'
                        'Action: wiki\nAction Input: {"query": "Eiffel Tower"}')
            return "Thought: Done.\nFinal Answer: 330 metres."


    class SloppyFormatLLM:
        """Sends a non-JSON Action Input, then reads the repair message."""

        def __call__(self, context):
            if "PARSE ERROR" not in context:
                return ("Thought: Just look it up.\nAction: wiki\n"
                        "Action Input: query=Empire State Building")
            if "Height: 443 m" not in context:
                return ('Thought: Action Input has to be a JSON object.\n'
                        'Action: wiki\n'
                        'Action Input: {"query": "Empire State Building"}')
            return "Thought: Done.\nFinal Answer: 443 metres."


    class StubbornLLM:
        """An entirely realistic bug: it never decides that it is finished."""

        def __call__(self, context):
            return ('Thought: Let me double-check the height one more time.\n'
                    'Action: wiki\nAction Input: {"query": "Eiffel Tower"}')


    # ================================ driver ==================================
    GOAL = ("How much taller is the Eiffel Tower than the Great Pyramid, in "
            "feet? Save the answer as a note called 'height_gap'.")

    print("=" * 64)
    print("A. one multi-step task, traced end to end")
    print("=" * 64)
    result, memory, tracer = run_agent(GOAL, HeightGapLLM(), build_registry())

    print("\n" + "=" * 64)
    print("B. the span tree")
    print("=" * 64)
    tracer.print_tree()
    spans, errors = tracer.count()
    print(f"\n{spans} spans, {tracer.clock} ticks, {errors} error(s), "
          f"{result.steps} steps")

    print("\n" + "=" * 64)
    print("C. what the model saw on its last call")
    print("=" * 64)
    print(memory.context())
    print(f"\nfixed prefix {approx_tokens(memory.prefix()):>4} tokens "
          f"(goal + tool menu)")
    print(f"history      {approx_tokens(memory.history()):>4} tokens "
          f"(budget {memory.budget}): {len(memory.facts)} facts, "
          f"{len(memory.turns)} turns verbatim, "
          f"{memory.summarised_turns} turns summarised away")
    print(f"whole prompt {approx_tokens(memory.context()):>4} tokens; "
          f"peak this run {memory.peak_tokens}")

    print("\n" + "=" * 64)
    print("D. a five-task eval")
    print("=" * 64)
    TASKS = [
        ("height gap", GOAL, HeightGapLLM, "626.6404"),
        ("typo recovery", "How tall is the Great Pyramid?", TypoLLM, "139"),
        ("bad tool name", "How tall is the Eiffel Tower?", HallucinatingLLM, "330"),
        ("bad formatting", "How tall is the Empire State Building?",
         SloppyFormatLLM, "443"),
        ("never stops", "How tall is the Eiffel Tower?", StubbornLLM, "330"),
    ]

    print(f"{'task':<16}{'ok':>3}{'steps':>7}{'repairs':>9}{'guards':>8}"
          f"{'tool errs':>11}{'peak ctx':>10}")
    runs = []
    for name, goal, policy, needle in TASKS:
        NOTEBOOK.clear()
        run, mem, _ = run_agent(goal, policy(), build_registry(),
                                tracer=Tracer(), verbose=False)
        ok = run.solved and needle in run.answer
        runs.append((name, ok, run))
        print(f"{name:<16}{'Y' if ok else 'N':>3}{run.steps:>7}{run.repairs:>9}"
              f"{run.guard_hits:>8}{run.tool_errors:>11}{run.peak_tokens:>10}")

    wins = [run for _, ok, run in runs if ok]
    print(f"\nsuccess rate            {len(wins)}/{len(runs)} "
          f"= {len(wins) / len(runs):.0%}")
    print(f"median steps to success {median(r.steps for r in wins):.1f}")
    print(f"guard activations       loop {sum(r.guard_hits for _, _, r in runs)}, "
          f"parse repairs {sum(r.repairs for _, _, r in runs)}, "
          f"tool errors {sum(r.tool_errors for _, _, r in runs)}")
    failures = [name for name, ok, _ in runs if not ok]
    print(f"failures                {failures or 'none'}")
    ```

    Two numbers in that output are worth arguing with. The history ends at
    **140 tokens against a budget of 120**, because five facts plus two
    verbatim turns is the floor: `keep` protects the recent turns and
    nothing re-compresses the fact list, so the budget is a target the
    summariser aims at rather than a wall. The fix is
    [29.3's hierarchical summary trees](../../ch29-memory-rag/03-agent-memory.md)
    — summarise the summaries — and it is the first thing to add. The other
    number is `median steps to success 3.5`, which is a median over four
    successes of wildly different difficulty; report steps *per task*
    alongside it, or an easy task will hide a regression on a hard one.

## Swapping in a real model

`run_agent` mentions the model on exactly one line — `reply = llm(context)`
— because the policy's contract is the contract a chat API already offers:
text in, text out. Replacing the stand-in is that line and nothing else.
This is not runnable here because it needs a network and an API key, which
is precisely why the rest of the project uses `FakeLLM`:

```text
# before — deterministic, offline, free, and identical on every machine:
reply = llm(context)

# after — a hosted chat model. MODEL_ID is whatever id your provider documents:
reply = client.messages.create(
    model=MODEL_ID,
    max_tokens=512,
    messages=[{"role": "user", "content": context}],
).content[0].text
```

Everything else — the registry, the parser, the repair path, the loop guard,
the budget, the memory, the tracer, the eval — is provider-independent
plumbing you would keep exactly as written. That ratio is the honest summary
of agent engineering: one line of model, several hundred lines of the parts
that make the model's mistakes survivable.

## Going further

- **Plan-then-execute mode.** Before step 1, ask the policy for a numbered
  plan, then execute it step by step and re-plan only when an observation
  contradicts it. Add a `plan` field to the memory prefix so every later
  step sees it. Measure both modes on the same five tasks: as
  [30.2](../../ch30-agents/02-planning-reflection.md) argues, planning
  usually costs steps on easy tasks and saves them on long ones, and your
  eval table is exactly the instrument for finding out where the crossover
  is for *your* tasks.
- **A reflection pass.** After a `Final Answer`, run one more model call
  that criticises the answer against the goal and either approves it or
  returns a concrete objection; on an objection, put the critique in the
  transcript and continue the loop. Cap reflections at one or two —
  [30.2](../../ch30-agents/02-planning-reflection.md) shows the returns
  falling off fast, and an uncapped critic is a second infinite loop.
- **A second agent as a tool.** Wrap `run_agent` itself as a tool named
  `research(question)` with its own budget, and give the outer agent access
  to it. You now have the simplest multi-agent system from
  [30.3](../../ch30-agents/03-multi-agent.md) — and its first bug, which is
  that budgets do not compose: ten outer steps times ten inner steps is a
  hundred model calls.
- **Trajectory logging.** Write each episode to JSONL in the schema from
  [32.3](../../ch32-data/03-trajectories.md), one line per run, with every
  step's tool, arguments, observation and guard flags. Then compute the
  trajectory metrics from
  [33.2](../../ch33-eval/02-eval-harness.md): clean-trajectory rate,
  tool-error rate, and steps to success. A successful run that tripped the
  loop guard nine times is not the same product as one that did not.
- **Better tool descriptions, measured.** Replace the descriptions with
  vague one-word versions (`"Searches."`, `"Computes."`), rerun the eval,
  and watch the success rate move without touching the policy. Then put
  them back. It is the cheapest experiment in this whole book, and it
  settles the "do we need a bigger model" argument in about four minutes.
- **Parallel tool calls.** Let the policy emit a JSON *array* of actions and
  execute them in order within one step, merging the observations. Your
  parser already rejects arrays with a repair message, so start by deciding
  what the new contract is — then notice how much of the loop guard has to
  change when a step can contain more than one action.
