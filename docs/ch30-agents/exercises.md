# Chapter 30 · Exercises

Eight problems on agent loops, planning, teams and production plumbing. They
build on [30.1](01-agent-loop-react.md), [30.2](02-planning-reflection.md),
[30.3](03-multi-agent.md) and [30.4](04-frameworks.md), and every solution runs
in the browser. Exercise 30.2 asks you to *predict* the output before you run
it — write your prediction down first; the gap between it and the printed
result is where the learning is.

Nothing here calls a model or touches the network. Where a model is needed it
is a deterministic rule-based stand-in, and every solution is self-contained so
you can run it on its own.

---

### Exercise 30.1 — Find the bug in the trace (●)

Here is a real-looking ReAct trace. The agent has three tools: `wiki`
(look things up), `calc` (arithmetic on two numbers) and `fx` (currency
conversion, using a rate of 0.93 USD to EUR). The final answer is wrong.

```text
Goal: What do 14 licences cost in euros?

--- step 1 ---
Thought: I need the licence price first.
Action: wiki
Action Input: licence price
Observation: The standard licence costs 1499 USD.
--- step 2 ---
Thought: 14 licences at 1499 USD each is 20,086 USD.
Action: fx
Action Input: 20086 USD to EUR
Observation: 20086.0 USD = 18679.98 EUR
--- step 3 ---
Thought: I have the euro total.
Final Answer: 14 licences cost 18,679.98 EUR.
```

Answer three questions: **(a)** exactly which line contains the mistake;
**(b)** what structural rule the agent broke, in one sentence; **(c)** what
step 2 should have been.

??? success "Solution"

    **(a)** The `Thought` on step 2. `14 × 1499` is not 20,086.

    **(b)** The agent did arithmetic *in its reasoning* instead of calling the
    `calc` tool. Everything after that inherits the error, and it inherits it
    invisibly: the `fx` tool was called correctly, its observation is correct
    for the number it was given, and the final answer is confidently wrong.
    This is the failure that opened
    [28.1](../ch28-tools-mcp/01-function-calling.md) — a model predicts digits,
    it does not carry tens.

    **(c)** `Action: calc` / `Action Input: 14 * 1499`, and only then the `fx`
    call on whatever `calc` returned.

    ```python
    """Recompute the trace to locate the damage."""
    PRICE_USD, UNITS, RATE_USD_EUR = 1499, 14, 0.93

    claimed_usd = 20086                    # from the step-2 Thought line
    actual_usd = UNITS * PRICE_USD         # what calc would have returned

    print(f"the Thought claimed : {claimed_usd:,} USD")
    print(f"the calculator says : {actual_usd:,} USD")
    print(f"error               : {actual_usd - claimed_usd:,} USD")
    print(f"claimed final answer: {claimed_usd * RATE_USD_EUR:,.2f} EUR")
    print(f"correct answer      : {actual_usd * RATE_USD_EUR:,.2f} EUR")
    ```

    The 900-USD slip becomes an 837-EUR error in the answer. The fix in
    practice is a tool description that says it out loud: *"Use this for ANY
    calculation, however easy it looks — never do arithmetic yourself."*

---

### Exercise 30.2 — Predict the reliability numbers (●)

**Write your prediction down before running this.** The code models a
multi-step agent two ways: plain, and with one automatic retry per step (so a
step fails only if both attempts fail). Predict all four printed lines.

```text
def success(p, n):
    return p ** n

def success_with_retry(p, n):
    return (1 - (1 - p) ** 2) ** n

for p in (0.90, 0.95):
    print(f"p={p:.2f}  n=10: plain={success(p, 10):.4f}  "
          f"one retry={success_with_retry(p, 10):.4f}")
```

Then answer: at $p = 0.90$ **with** one retry per step, how many steps can you
run before whole-task success drops below 50%? And without retries?

??? success "Solution"

    Plain at $p=0.9$: $0.9^{10} = 0.3487$. With one retry each step succeeds
    with probability $1 - 0.1^2 = 0.99$, so the task succeeds with
    $0.99^{10} = 0.9044$. At $p=0.95$: $0.5987$ plain, and
    $(1 - 0.05^2)^{10} = 0.9975^{10} = 0.9753$ with a retry.

    ```python
    """Compounding reliability, with and without a retry per step."""
    def success(p, n):
        return p ** n

    def success_with_retry(p, n):
        """One retry per step: a step only fails if BOTH attempts fail."""
        return (1 - (1 - p) ** 2) ** n

    for p in (0.90, 0.95):
        print(f"p={p:.2f}  n=10: plain={success(p, 10):.4f}  "
              f"one retry={success_with_retry(p, 10):.4f}")

    n = 1
    while success_with_retry(0.90, n) >= 0.50:
        n += 1
    print(f"with one retry at p=0.90, success drops below 50% at n={n}")
    print("without retries it drops below 50% at n="
          f"{next(k for k in range(1, 100) if success(0.90, k) < 0.50)}")
    ```

    The headline: 7 steps without retries, **69 steps with them**. A single
    retry per step turns a per-step failure rate of $1-p$ into $(1-p)^2$, and
    because that number sits in an exponent the effect on the whole task is
    enormous. This is why "make each step retryable" beats "make each step
    better" as a first move — and why a *verifier* that tells you a step failed
    is worth so much (30.2), since you cannot retry a failure you did not
    detect.

---

### Exercise 30.3 — Add a tool and a loop guard (●●)

Extend the ReAct agent from 30.1 with a fourth tool, `fx`, that converts
currency using the format `'250 EUR to USD'` with **uppercase** ISO codes, and
add loop detection so a repeated identical action gets a corrective
observation instead of a repeated failure.

The policy below misformats the call the first time (lowercase codes), repeats
it, then fixes it once it sees the guard. Make the agent finish in four steps.

*Careful:* 30.1 fingerprinted actions as `(tool, input.strip().lower())`. Think
about whether that normalisation is right here.

??? success "Solution"

    ```python
    """A ReAct agent with a currency tool and a loop guard."""
    import re

    CURRENCY = {("EUR", "USD"): 1.08, ("USD", "EUR"): 0.93}

    def fx(text):
        """Convert currency: '250 EUR to USD'. Codes must be uppercase."""
        m = re.fullmatch(r"\s*([\d.]+)\s*([A-Z]{3})\s+to\s+([A-Z]{3})\s*", text)
        if not m:
            return ("Error: expected '<amount> <FROM> to <TO>' with uppercase "
                    "codes, e.g. '250 EUR to USD'.")
        amount, src, dst = float(m[1]), m[2], m[3]
        if (src, dst) not in CURRENCY:
            return f"Error: no rate for {src}->{dst}. Known: {sorted(CURRENCY)}."
        return f"{amount} {src} = {round(amount * CURRENCY[(src, dst)], 2)} {dst}"

    TOOLS = {"fx": fx}

    def parse(reply):
        fields = {}
        for line in reply.splitlines():
            for tag in ("Thought", "Action Input", "Action", "Final Answer"):
                if line.strip().startswith(tag + ":"):
                    fields[tag] = line.strip()[len(tag) + 1:].strip()
                    break
        if "Final Answer" in fields:
            return {"kind": "final", **fields}
        if "Action" in fields and "Action Input" in fields:
            return {"kind": "act", **fields}
        return {"kind": "unparsed", **fields}

    def run_react(llm, goal, tools, max_steps=6):
        transcript, seen = f"Goal: {goal}\n", set()
        for step in range(1, max_steps + 1):
            reply = llm(transcript)
            decision = parse(reply)
            if decision["kind"] == "final":
                print(f"step {step}: FINAL -> {decision['Final Answer']}")
                return decision["Final Answer"]
            if decision["kind"] == "unparsed":
                observation = "PARSE ERROR: use Action/Action Input or Final Answer."
            else:
                action, arg = decision["Action"], decision["Action Input"]
                # NOT .lower(): for this tool, case is meaningful.
                key = (action, arg.strip())
                if key in seen:
                    observation = (f"LOOP GUARD: {action}({arg!r}) was already "
                                   "tried and did not help. Change the action "
                                   "or the input.")
                elif action not in tools:
                    observation = (f"TOOL ERROR: no tool named {action!r}. "
                                   f"Available: {', '.join(tools)}.")
                else:
                    seen.add(key)
                    observation = tools[action](arg)
                print(f"step {step}: {action}({arg!r})\n         -> {observation}")
            transcript += reply + f"\nObservation: {observation}\n"
        print(f"budget of {max_steps} steps exhausted")
        return None

    class LLM:
        """Lowercases the codes, repeats the mistake, then reads the guard."""
        def __call__(self, transcript):
            if "= " in transcript and "USD" in transcript:
                return "Thought: Got it.\nFinal Answer: 250 EUR is 270.0 USD."
            if "LOOP GUARD" in transcript:
                return ("Thought: Use uppercase codes as the tool asked.\n"
                        "Action: fx\nAction Input: 250 EUR to USD")
            return ("Thought: Convert the price.\n"
                    "Action: fx\nAction Input: 250 eur to usd")

    run_react(LLM(), "How many dollars is 250 euros?", TOOLS)
    ```

    Four steps: bad format, guard, corrected call, answer. The trap is the
    normalisation. If you fingerprint with `.strip().lower()`, then
    `'250 eur to usd'` and `'250 EUR to USD'` collapse to the same key, the
    guard fires on the *corrected* call, and the agent never escapes — a false
    positive that burns the whole budget. Normalise only what the tool itself
    ignores.

---

### Exercise 30.4 — Majority vote on a scripted sample set (●●)

You have seven sampled answers to "what is the total?", written as free text.
Self-consistency needs comparable answers, so first extract a **key** from each
sample, then take the majority. Print the extracted keys, the tally, the
winner, and what the first sample alone would have said.

```text
"About 40 dollars."            "The answer is 42 dollars."
"The answer is 42."            "I make it 42 dollars in total."
"Roughly 43 dollars."          "42 dollars, give or take."
"It comes to 84 dollars."
```

??? success "Solution"

    ```python
    """Extract a comparable key from each sample, then vote."""
    import re
    from collections import Counter

    SAMPLES = [
        "About 40 dollars.", "The answer is 42 dollars.", "The answer is 42.",
        "I make it 42 dollars in total.", "Roughly 43 dollars.",
        "42 dollars, give or take.", "It comes to 84 dollars.",
    ]

    def extract_key(text):
        """The comparable part: the first whole number in the sample."""
        m = re.search(r"\b(\d+)\b", text)
        return int(m[1]) if m else None

    keys = [extract_key(s) for s in SAMPLES]
    tally = Counter(k for k in keys if k is not None)
    winner, votes = tally.most_common(1)[0]

    print("extracted keys:", keys)
    print("tally         :", dict(tally))
    print(f"majority      : {winner} with {votes}/{len(SAMPLES)} votes")
    print("first sample alone would have said:", keys[0])
    ```

    The first sample says 40 and is wrong; the majority says 42 and is right,
    because the three wrong answers split across 40, 43 and 84 while the four
    right ones agree. Two lessons. First, **extraction is the whole trick** —
    without `extract_key` all seven strings are distinct and the vote is
    1-1-1-1-1-1-1. Second, this only works when errors are diverse: if the
    model were wrong the *same* way every time, the majority would be
    confidently wrong.

---

### Exercise 30.5 — Turn a chain into plan → execute → replan (●●)

Here is a linear chain that prices an order. It has a bug it cannot notice: it
never checks stock, so it happily prices 20 units of an item you have 12 of.

```text
def chain(order):
    price = order["units"] * 20           # 20 EUR per unit
    usd = price * 1.08                    # EUR -> USD
    return f"{order['units']} widgets = {usd:.2f} USD"
```

Rewrite it as a plan (`check_stock` → `price` → `to_usd`), an executor that
*returns* errors instead of raising, and a replanner that reduces the order to
the available quantity and retries the same slot. Print both the chain's answer
and the agent's, and cap the replans.

??? success "Solution"

    ```python
    """A linear chain, and the same task as plan -> execute -> replan."""
    RATE_EUR_USD = 1.08
    STOCK = {"widget": 12}

    def chain(order):
        """The original: three fixed stages, no check, no recovery."""
        price = order["units"] * 20
        return f"{order['units']} widgets = {price * RATE_EUR_USD:.2f} USD"

    def planner(order):
        return [{"id": 1, "tool": "check_stock", "arg": order["item"]},
                {"id": 2, "tool": "price", "arg": order["units"]},
                {"id": 3, "tool": "to_usd", "arg": "the price"}]

    def replanner(steps, failed, error, order):
        """Repair: reduce the order to what is actually in stock."""
        if "only" in error:
            order["units"] = STOCK[order["item"]]
            return [dict(s, arg=order["units"]) if s["id"] == 2 else s
                    for s in steps]
        return None                                   # no repair known

    class Executor:
        def __init__(self, order):
            self.order, self.value = order, None

        def run(self, step):
            """Returns (value, error). Never raises at the caller."""
            if step["tool"] == "check_stock":
                have = STOCK.get(step["arg"], 0)
                if have < self.order["units"]:
                    return None, f"Error: only {have} in stock"
                return have, None
            if step["tool"] == "price":
                self.value = step["arg"] * 20
                return self.value, None
            if step["tool"] == "to_usd":
                self.value *= RATE_EUR_USD
                return round(self.value, 2), None
            return None, f"Error: unknown tool {step['tool']!r}"

    order = {"item": "widget", "units": 20}
    print("chain (no recovery):", chain(order))

    steps, executor = planner(order), Executor(order)
    i, replans, MAX_REPLANS = 0, 0, 2
    while i < len(steps):
        step = steps[i]
        value, error = executor.run(step)
        if error:
            print(f"  {step['id']}. {step['tool']} -> {error}")
            revised = (replanner(steps, step, error, order)
                       if replans < MAX_REPLANS else None)
            if revised is None:
                print("  giving up: no repair available")
                break
            replans += 1
            steps = revised
            print(f"     replanned: units now {order['units']}")
            continue                                  # retry the SAME slot
        print(f"  {step['id']}. {step['tool']}({step['arg']}) -> {value}")
        i += 1
    print(f"answer: {executor.value:.2f} USD for {order['units']} units "
          f"(after {replans} replan)")
    ```

    The chain confidently returns `432.00 USD` for stock that does not exist.
    The agent detects the shortfall at step 1, replans, and returns
    `259.20 USD` for 12 units. Note the two rules from 30.2 doing the work:
    the executor **returns** the error so the replanner can read it, and
    `continue` retries the *same* slot rather than skipping past it.

---

### Exercise 30.6 — Design the message schema for a 3-agent system (●●)

You are building a support-inbox team: a **triage** agent that reads incoming
mail, a **knowledge** agent that searches the help centre, and a **responder**
that writes the reply. Design the message type and a validator.

Requirements: every message must carry a sender, a recipient, a `kind` from a
closed vocabulary, a `ticket_id` for correlation, and a turn number starting at
1. No agent may message itself. Certain sender/kind pairs must carry specific
body fields — a knowledge `result` must carry `snippets` **and** `confidence`;
a responder `done` must carry `reply`. Validate one good and two bad messages
and print the problems.

??? success "Solution"

    ```python
    """A message schema for a 3-agent support team, plus a validator."""
    from dataclasses import dataclass, field, asdict

    AGENTS = {"triage", "knowledge", "responder"}
    KINDS = {"request", "result", "error", "done"}

    @dataclass(frozen=True)
    class Message:
        sender: str
        recipient: str
        kind: str
        ticket_id: str          # correlation id: ties a whole run together
        turn: int
        body: dict = field(default_factory=dict)

    REQUIRED_BODY = {           # (sender, kind) -> fields the body must have
        ("triage", "request"):     {"text"},
        ("knowledge", "result"):   {"snippets", "confidence"},
        ("knowledge", "error"):    {"reason"},
        ("responder", "result"):   {"reply"},
        ("responder", "error"):    {"reason"},
        ("responder", "done"):     {"reply"},
    }

    def validate(msg):
        """Returns a list of problems; an empty list means well formed."""
        problems = []
        if msg.sender not in AGENTS:
            problems.append(f"unknown sender {msg.sender!r}")
        if msg.recipient not in AGENTS:
            problems.append(f"unknown recipient {msg.recipient!r}")
        if msg.sender == msg.recipient:
            problems.append("an agent may not message itself")
        if msg.kind not in KINDS:
            problems.append(f"kind {msg.kind!r} not in {sorted(KINDS)}")
        if not msg.ticket_id:
            problems.append("ticket_id is required for correlation")
        if msg.turn < 1:
            problems.append("turn must start at 1")
        for key in sorted(REQUIRED_BODY.get((msg.sender, msg.kind), set())
                          - set(msg.body)):
            problems.append(f"body is missing {key!r}")
        return problems

    good = Message("knowledge", "responder", "result", "T-19", 3,
                   {"snippets": ["the refund window is 30 days"],
                    "confidence": 0.8})
    bad1 = Message("knowledge", "knowledge", "reslt", "", 0, {"snippets": []})
    bad2 = Message("knowledge", "responder", "result", "T-19", 2,
                   {"snippets": []})            # no confidence

    print("good ->", validate(good) or "ok")
    for problem in validate(bad1):
        print("bad1 ->", problem)
    for problem in validate(bad2):
        print("bad2 ->", problem)
    print("\nserialised:", asdict(good))
    ```

    Four design choices worth defending in a review. **`frozen=True`**: a
    message is a record of the past, so nobody may edit one after sending.
    **A closed `kind` vocabulary**: `done` is what termination checks look for,
    and you cannot write a termination check against free-form strings.
    **`ticket_id`**: with several runs in flight, correlation is the only way
    to read the log. **Per-(sender, kind) body requirements**: `bad2` is the
    interesting case — it is a perfectly well-formed message that is missing
    the `confidence` the responder needs to decide whether to escalate, and
    only a schema catches that.

---

### Exercise 30.7 — Backoff scheduling with jitter (●●)

Implement a retry schedule: exponential backoff with a base of 0.4 s, a factor
of 2, a cap of 10 s, and **equal jitter** (wait a random time between half the
ceiling and the full ceiling). Print a table of attempt, ceiling, actual wait
and cumulative wait for 5 waits. Then write `should_retry(status)` that retries
only transient HTTP failures. Nothing may sleep, and the output must be
reproducible.

??? success "Solution"

    ```python
    """Backoff schedule with equal jitter — simulated, seeded, never slept."""
    import random

    RETRYABLE = {408, 429, 500, 502, 503, 504}   # transient
    # 400, 401, 403, 404, 422 are permanent: retrying repeats the same error.

    def schedule(waits=5, base=0.4, factor=2.0, cap=10.0, seed=1):
        """Return (attempt, ceiling, wait, cumulative) rows. Seeded, so the
        table is identical every run — which is how you unit-test backoff."""
        rng = random.Random(seed)
        rows, total = [], 0.0
        for attempt in range(1, waits + 1):
            ceiling = min(cap, base * factor ** (attempt - 1))
            wait = rng.uniform(ceiling / 2, ceiling)      # equal jitter
            total += wait
            rows.append((attempt, ceiling, wait, total))
        return rows

    def should_retry(status):
        """Retry transient failures only."""
        return status in RETRYABLE

    print(f"{'attempt':>7} {'ceiling':>8} {'wait':>7} {'cumulative':>11}")
    for attempt, ceiling, wait, total in schedule():
        print(f"{attempt:>7} {ceiling:>7.2f}s {wait:>6.2f}s {total:>10.2f}s")

    print()
    for status in (200, 400, 429, 503):
        print(f"status {status}: retry? {should_retry(status)}")
    ```

    The ceilings double — 0.40, 0.80, 1.60, 3.20, 6.40 — and would flatten at
    the 10-second cap on the next step. Two points to hold on to. **Jitter is
    not decoration**: without it, every client that failed at the same instant
    retries at the same instant, recreating the overload they are backing off
    from. **Classify before you retry**: a 400 will fail identically five
    times, so retrying it just multiplies the same error and delays the real
    report by ten seconds.

---

### Exercise 30.8 — Checkpoint and resume (●●●)

Take the state-graph agent from [30.4](04-frameworks.md) and make it
**durable**: after a crash, a fresh process must pick up exactly where the old
one stopped, with no repeated work beyond the interrupted node.

Requirements: write a JSON checkpoint containing the *next node to run* and the
full state, **before** each node runs; simulate a crash inside `review` on the
first run; then load the checkpoint in a second run and finish the task. Print
both runs and the final artifact.

Think about *when* to checkpoint — before or after the node — and why.

??? success "Solution"

    ```python
    """A durable state-graph agent: checkpoint, crash, resume, finish."""
    import json

    NOTES = {"Larkspur-2": ["launched 2021", "orbit 705 km", "4-band imager"]}
    END = "__end__"
    CHECKPOINT = "agent_checkpoint.json"

    def research(state):
        state["findings"] = NOTES.get(state["topic"], [])
        return state

    def write(state):
        keep = state["findings"] if state["revisions"] else state["findings"][:1]
        state["draft"] = f"{state['topic']}: " + "; ".join(keep) + "."
        return state

    def review(state):
        if state.get("crash_here") and not state.get("resumed"):
            raise RuntimeError("simulated crash inside review")
        state["missing"] = [f for f in state["findings"]
                            if f not in state["draft"]]
        state["approved"] = not state["missing"]
        return state

    def route_from_review(state):
        if state["approved"] or state["revisions"] >= 2:
            return END
        state["revisions"] += 1
        return "write"

    NODES = {"research": research, "write": write, "review": review}
    EDGES = {"research": "write", "write": "review"}
    CONDITIONAL = {"review": route_from_review}

    def save(node, state):
        """Checkpoint = (what to run next, everything needed to run it)."""
        with open(CHECKPOINT, "w", encoding="utf-8") as fh:
            json.dump({"next_node": node, "state": state}, fh)

    def load():
        with open(CHECKPOINT, encoding="utf-8") as fh:
            snapshot = json.load(fh)
        return snapshot["next_node"], snapshot["state"]

    def run(node, state, max_steps=12):
        for step in range(1, max_steps + 1):
            save(node, state)                  # BEFORE the node runs
            state = NODES[node](state)
            nxt = (CONDITIONAL[node](state) if node in CONDITIONAL
                   else EDGES.get(node, END))
            print(f"  step {step}: {node:<9} -> {nxt}")
            if nxt == END:
                save(END, state)
                return state
            node = nxt
        raise RuntimeError(f"graph did not terminate in {max_steps} steps")

    start = {"topic": "Larkspur-2", "findings": [], "draft": "", "missing": [],
             "approved": False, "revisions": 0, "crash_here": True}

    print("first run:")
    try:
        run("research", start)
    except RuntimeError as exc:
        print("  CRASH:", exc)

    node, state = load()
    print(f"\ncheckpoint holds next_node={node!r} draft={state['draft']!r}")

    state["resumed"] = True                    # the bug is fixed / retry allowed
    print("resumed run:")
    final = run(node, state)
    print("\nfinal draft :", final["draft"])
    print("approved    :", final["approved"])
    ```

    The first run gets through `research` and `write` and dies inside `review`.
    The checkpoint holds `next_node='review'` and the thin first draft, so the
    resumed run re-runs only `review` and then completes the revision cycle.

    **Why checkpoint *before* the node, not after?** Because a node that
    crashes half-way must be re-runnable. If you saved after each node, a crash
    inside `review` would leave the last checkpoint pointing at `write`, and
    you would redo `write` too — and worse, you would have no record that
    `review` was ever attempted. Saving before means the checkpoint always
    names the node that has *not yet successfully completed*.

    **The catch this design does not solve:** re-running a node means its side
    effects happen twice. `review` is pure, so re-running it is free. A node
    that sends an email is not, which is exactly why 30.4 pairs checkpointing
    with **idempotency keys** — the checkpoint decides *what* to redo, the
    idempotency key decides what redoing is allowed to do.

    This is also the honest measure of what a framework gives you.
    Checkpointing a flat dict is thirty lines. Checkpointing a live object
    graph, with concurrent branches, resumable streams, and a human approval
    that may arrive next Tuesday, is not — and that is the row of the 30.4
    comparison table worth paying for.
