# 28.2 Structured output and constrained decoding

The loop in [Section 28.1](01-function-calling.md) rests on an assumption we
never examined: that the model's reply *parses*. Real models are trained to
be helpful, and helpful things say "Sure! Here's the JSON you asked for:"
before the JSON, or wrap it in a markdown fence, or add a friendly closing
sentence. Every one of those makes `json.loads` throw. This section is about
the two families of fixes — clean up afterwards, or make the mistake
impossible in the first place — and the second one is a genuinely beautiful
mechanism.

## "Respond in JSON" and the five ways it breaks

Asking nicely gets you most of the way, which is exactly what makes it
dangerous: it works in testing and fails at 3 a.m. Here are six replies
collected from the same prompt — one good, five broken in ways you will
meet within your first week.

```python
import json

samples = [
    '{"city": "Oslo", "temp_c": -3}',
    'Sure! Here is the JSON you asked for:\n{"city": "Oslo", "temp_c": -3}',
    '```json\n{"city": "Oslo", "temp_c": -3}\n```',
    '{"city": "Oslo", "temp_c": -3,}',
    "{'city': 'Oslo', 'temp_c': -3}",
    '{"city": "Oslo", "temp_c":',
]
labels = ["clean", "chatty preamble", "markdown fence",
          "trailing comma", "Python quotes", "truncated"]

for label, text in zip(labels, samples):
    try:
        json.loads(text)
        print(f"{label:16} OK")
    except ValueError as exc:
        print(f"{label:16} FAILED — {exc}")
```

One in six. The failures are not random noise, though — they are a short,
stable list, which means most of them are *repairable*.

Two of these deserve naming:

- **The trailing comma** is legal in JavaScript and in Python but illegal in
  JSON, so models trained on code emit it constantly.
- **The truncated reply** is different in kind: it is what a hit token limit
  looks like. No cleverness recovers the missing half of a message that was
  never generated, and pretending otherwise silently invents data.

## A repair function that knows what it cannot fix

```python
import ast
import json
import re

def repair_json(text):
    """Best-effort recovery of a JSON object from a model reply.
    Raises ValueError when the text is beyond honest repair."""
    # 1. Drop a markdown code fence if one wraps the payload.
    fenced = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
    if fenced:
        text = fenced.group(1)

    # 2. Keep only the first balanced {...} region, dropping any prose
    #    before or after it.
    start = text.find("{")
    if start == -1:
        raise ValueError("no JSON object found in reply")
    depth, end = 0, None
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    if end is None:
        raise ValueError("unbalanced braces — the reply was cut off")
    candidate = text[start:end]

    # 3. Remove trailing commas before } or ].
    candidate = re.sub(r",\s*([}\]])", r"\1", candidate)

    try:
        return json.loads(candidate)
    except ValueError:
        pass

    # 4. Last resort: Python-literal syntax (single quotes, True/None).
    #    ast.literal_eval parses literals ONLY — it cannot call functions
    #    or import modules, so it is not the eval() we banned in 28.1.
    try:
        value = ast.literal_eval(candidate)
    except (ValueError, SyntaxError) as exc:
        raise ValueError(f"unrepairable: {exc}") from None
    if not isinstance(value, dict):
        raise ValueError("repaired text is not an object")
    return value


samples = [
    '{"city": "Oslo", "temp_c": -3}',
    'Sure! Here is the JSON you asked for:\n{"city": "Oslo", "temp_c": -3}\nLet me know if you need Fahrenheit!',
    '```json\n{"city": "Oslo", "temp_c": -3}\n```',
    '{"city": "Oslo", "temp_c": -3,}',
    "{'city': 'Oslo', 'temp_c': -3}",
    '{"city": "Oslo", "temp_c":',
]
labels = ["clean", "chatty preamble", "markdown fence",
          "trailing comma", "Python quotes", "truncated"]

for label, text in zip(labels, samples):
    try:
        print(f"{label:16} -> {repair_json(text)}")
    except ValueError as exc:
        print(f"{label:16} -> REJECTED ({exc})")
```

Five recovered, one honestly refused. That last line is the important one: a
repair function that *guesses* at truncated data is worse than no repair
function, because it turns a loud failure into a quiet wrong answer.

**Repair syntax, never semantics.**

```python
# raises JSONDecodeError
import json

# What a reply looks like when the model hit its max_tokens limit:
json.loads('{"city": "Oslo", "temp_c":')
```

Prompting can reduce the rate of all this. Four things help:

- **Say "output only JSON, no prose"** in the instruction.
- **Include one example** of the exact output you want.
- **Set a stop sequence** so the model cannot ramble past the closing brace.
- **Pre-fill the start of the assistant's reply with a `{`** (on APIs that
  allow it) so the model resumes inside an object. That is an assistant
  prefix, not the prefill *phase* of
  [27.1](../ch27-inference/01-kv-cache.md).

None of it is a guarantee. For a guarantee you have to go a level down, into
sampling.

## Constrained decoding: masking the logits

Recall from [Section 26.4](../ch26-llm-internals/04-sampling.md) how a token
is chosen: the model produces one **logit** per vocabulary entry, softmax
turns those scores into probabilities, and you sample from that
distribution. The insight behind constrained decoding is almost too simple:

> If a token would make the output ungrammatical, set its logit to
> $-\infty$ before the softmax. Its probability becomes exactly zero, so it
> can never be sampled. The model is free to choose among the tokens that
> keep the output valid — and *only* those.

Formally, with a mask $m_i \in \{0, 1\}$ marking which tokens the grammar
allows in the current state:

$$
P(\text{token } i) = \frac{\exp(z_i / T) \cdot m_i}
                          {\sum_j \exp(z_j / T) \cdot m_j}
$$

The guarantee is structural, not statistical. It does not depend on the
model being cooperative, well-prompted, or even good. Here it is, running:
one toy vocabulary, one grammar written as a state machine, one model whose
"logits" are random numbers.

```python
import json
import numpy as np

VOCAB = ["{", "}", ":", ",", '"name"', '"age"', '"ada"', '"grace"',
         "17", "42", "Sure", "!", " here", " is"]

class JsonGrammar:
    """Which tokens keep us on a path to a valid JSON object."""
    KEYS = {'"name"', '"age"'}
    VALUES = {'"name"': {'"ada"', '"grace"'}, '"age"': {"17", "42"}}

    def __init__(self):
        self.state, self.used, self.key = "start", set(), None

    def allowed(self):
        if self.state == "start":
            return {"{"}
        if self.state == "key":
            return self.KEYS - self.used
        if self.state == "colon":
            return {":"}
        if self.state == "value":
            return self.VALUES[self.key]
        if self.state == "after_value":
            return {"}", ","} if self.KEYS - self.used else {"}"}
        return set()

    def advance(self, token):
        if self.state == "start":
            self.state = "key"
        elif self.state == "key":
            self.key, self.state = token, "colon"
            self.used.add(token)
        elif self.state == "colon":
            self.state = "value"
        elif self.state == "value":
            self.state = "after_value"
        elif self.state == "after_value":
            self.state = "done" if token == "}" else "key"

    def done(self):
        return self.state == "done"


def softmax(z):
    z = z - z.max()
    e = np.exp(z)
    return e / e.sum()

def sample(logits, rng):
    return int(rng.choice(len(logits), p=softmax(logits)))

# --- 1. The model, unconstrained ---------------------------------------
rng = np.random.default_rng(0)
tokens = [VOCAB[sample(rng.normal(size=len(VOCAB)), rng)] for _ in range(9)]
raw = "".join(tokens)
print("unconstrained:", raw)
try:
    json.loads(raw)
except ValueError as exc:
    print("  json.loads ->", exc)

# --- 2. The same model, same logits, with a grammar mask ---------------
rng = np.random.default_rng(0)     # identical random stream
grammar, tokens = JsonGrammar(), []
while not grammar.done():
    logits = rng.normal(size=len(VOCAB))
    mask = np.array([tok in grammar.allowed() for tok in VOCAB])
    masked = np.where(mask, logits, -np.inf)     # forbidden -> probability 0
    tok = VOCAB[sample(masked, rng)]
    print(f"  step {len(tokens) + 1}: {int(mask.sum())}/{len(VOCAB)} tokens "
          f"legal {sorted(grammar.allowed())} -> {tok!r}")
    tokens.append(tok)
    grammar.advance(tok)

text = "".join(tokens)
print("constrained  :", text)
print("  json.loads ->", json.loads(text))
```

Look at what happened. The *model* did not change — same weights, same random
stream, same scores. All that changed is which tokens were reachable at each
step, and the output went from unparseable noise to a JSON object that
`json.loads` accepts on the first try.

Watch how the freedom varies. At step 1 exactly one token out of fourteen is
legal, so the model has no choice at all; at the value step it picks freely
between two legal values. That is the whole trick, and it is why structured
output can be *guaranteed* rather than hoped for.

Real implementations differ from ours in scale, not in kind:

- the vocabulary is 30k–200k tokens rather than 14, so masks are computed
  with a precompiled index rather than a Python `in` test;
- the grammar comes from a JSON Schema, a regular expression, or a
  context-free grammar, compiled into a finite-state machine whose states
  map to allowed-token sets;
- tokens do not line up with grammar symbols — one token may be `", "` or
  `{"` — so the machine works over *token* boundaries, which is the fiddly
  engineering part;
- the mask has to be recomputed every step, which costs a little latency;
  good implementations cache masks per state so the cost is near zero.

The general idea covers more than JSON:

- **A regex** like `[0-9]{4}-[0-9]{2}-[0-9]{2}` constrains output to an ISO
  date.
- **A context-free grammar** can constrain output to valid SQL, valid Python,
  or a domain-specific format of your own.
- **A JSON Schema** compiles down to the same machinery, with `enum` becoming
  a literal alternation and `"type": "integer"` becoming a digit loop.

## The library landscape

You will not write mask code yourself. Here is who does, and what layer they
work at. (Framework details move fast — treat this as the shape of the
landscape, and check current docs for exact parameter names.)

| Tool | What it is | Runs where |
| --- | --- | --- |
| **Outlines** | Python library that compiles JSON Schema, regex, or a CFG into token masks driven by a finite-state machine | In your process, with a local model |
| **Instructor** | Wraps provider SDKs; you declare a **Pydantic** model, it generates the schema, validates the reply, and retries with the error | Client side, over any API |
| **llama.cpp GBNF** | Grammar files in a BNF-like syntax, enforced inside the sampler of a local GGUF model | Local inference engine |
| **vLLM guided decoding** | Server-side parameters (`guided_json`, `guided_regex`, `guided_grammar`) backed by grammar engines such as Outlines or XGrammar | Your own inference server |
| **Provider-native structured outputs** | You pass a JSON Schema with the request; the provider constrains decoding on its side and returns conforming JSON | Hosted API |

The Instructor style is worth seeing because it reads so differently — the
schema is just a class, and the return value is a typed object rather than a
dict:

```text
# Instructor + Pydantic — needs `pip install instructor pydantic` and an
# API key, so it gets no Run button here.
from pydantic import BaseModel, Field
import instructor

class Weather(BaseModel):
    city: str
    temp_c: float = Field(description="Temperature in degrees Celsius")

client = instructor.from_openai(OpenAI())     # or from_anthropic(...)

weather = client.chat.completions.create(
    model="...",
    response_model=Weather,                   # <- the schema
    max_retries=3,                            # <- validate, then re-ask
    messages=[{"role": "user", "content": "Weather in Oslo right now?"}],
)
print(weather.temp_c + 1)      # a real float, not a string, not a dict
```

Notice `max_retries`. Even the ergonomic library is doing the humble thing
underneath: ask, validate, and if validation fails, ask again with the
complaint attached.

## Tradeoffs: constraints are not free

**Constrained decoding guarantees *syntax*, never *sense*.** A schema-valid
`{"city": "Oslo", "temp_c": 900}` is still wrong, and a model that does not
know the answer will now produce a confidently well-formed wrong answer
instead of an obviously broken one. Validation of values — ranges, enums,
cross-field consistency — remains your job.

It can also cost quality, because a schema that fights the model's natural
output forces tokens the model considers unlikely. The classic case: demanding
a bare `{"answer": ...}` denies the model any room to reason, and on
multi-step problems that is a measurable loss. The fix is to put the reasoning
*inside* the schema — a `"reasoning": {"type": "string"}` field declared
**before** `"answer"`, since JSON is generated in order and the model can
attend to what it already wrote.

Two more sharp edges:

- **Unbounded whitespace in a grammar lets a model stall**, emitting spaces
  forever without ever violating the rules.
- **An overly rigid schema can force a fabrication.** A model that wanted to
  say "I don't know" now has to invent a value; where that matters, allow a
  `null` or an explicit `"unknown"` enum member.

### The three ways to get structured output

| Approach | Guarantee | Needs | Catches bad *values*? |
| --- | --- | --- | --- |
| **Prompt only** ("reply in JSON") | none — it is a request | nothing | no |
| **Constrained decoding** | syntax is guaranteed by construction | a local model or a provider that supports it | no |
| **Validate and retry** | none per attempt, high over a few | nothing | **yes** — any check you can write |

They are complementary, not rivals. Most production systems use native
structured outputs for the shape and validation-with-retry for everything the
shape cannot express.

The retry approach works with every provider and needs no infrastructure:
**validate and retry**, feeding the error back as feedback.

```python
import json

class FakeLLM:
    """Stands in for a real API. Fails twice, then complies — a very
    realistic pattern for a mid-sized model."""

    def __init__(self):
        self.calls = 0

    def respond(self, prompt):
        self.calls += 1
        if self.calls == 1:
            return "Sure! Here's the JSON:\n{'city': 'Oslo', 'temp_c': -3}"
        if self.calls == 2:
            return '{"city": "Oslo", "temp_c": "minus three"}'
        return '{"city": "Oslo", "temp_c": -3}'


def check(data):
    """Tiny schema check: both fields present, temp_c a real number."""
    problems = []
    for field in ("city", "temp_c"):
        if field not in data:
            problems.append(f"missing field '{field}'")
    if "temp_c" in data and not isinstance(data["temp_c"], (int, float)):
        problems.append("'temp_c' must be a number, not a string")
    return problems


def ask_for_json(llm, prompt, attempts=4):
    feedback = ""
    for attempt in range(1, attempts + 1):
        raw = llm.respond(prompt + feedback)
        try:
            data = json.loads(raw)
        except ValueError as exc:
            print(f"attempt {attempt}: not JSON ({exc.args[0]})")
            feedback = ("\nYour previous reply was not valid JSON. "
                        "Reply with a JSON object and nothing else.")
            continue
        problems = check(data)
        if problems:
            print(f"attempt {attempt}: schema problems {problems}")
            feedback = "\nYour previous reply had: " + "; ".join(problems)
            continue
        print(f"attempt {attempt}: accepted {data}")
        return data
    raise RuntimeError(f"no valid output after {attempts} attempts")

print("result:", ask_for_json(FakeLLM(), "Weather in Oslo? Reply as JSON."))
```

Three attempts, one valid object, and the loop is twenty lines.

Retry is strictly weaker than constrained decoding: it can fail, and each
failure costs a full round trip. But it works against any API, it catches
semantic problems a grammar cannot, and **the feedback string is doing real
teaching** — attaching the validation error is what makes attempt 2 different
from attempt 1.

!!! warning "Common mistakes"

    - **Trusting a repair function to fix truncation.** Unbalanced braces
      mean data is missing; inventing it turns a visible error into an
      invisible one. Raise, and raise the token limit.
    - **Using `eval()` to parse "almost JSON".** `ast.literal_eval` handles
      Python-literal syntax safely; `eval` hands your process to whoever
      influenced the model's output.
    - **Assuming constrained decoding makes answers correct.** It makes them
      *parseable*. Range checks, enums, and cross-field rules are still on
      you.
    - **Putting `"answer"` first in a schema that also has `"reasoning"`.**
      Generation is left to right; a field the model writes first cannot
      depend on one it writes later.
    - **Retrying without telling the model what went wrong.** A bare retry
      re-rolls the same dice. Attaching the validation error is what makes
      attempt 2 different from attempt 1.

## Check your understanding

1. In one sentence, why does logit masking *guarantee* valid output where
   prompting only makes it likely?

    ??? success "Answer"
        Because a masked token's probability is exactly zero, so no sampling
        strategy at any temperature can ever choose it — the guarantee comes
        from the mechanics of sampling rather than from the model's
        willingness to follow instructions.

2. A colleague's repair function fixes the truncated sample by appending
   `null}`. What is wrong with that?

    ??? success "Answer"
        It fabricates data. The model never generated a value for `temp_c`,
        and silently substituting `null` (or `0`, or `""`) means a wrong
        number flows downstream with no error anywhere. The right responses
        are to reject the reply, retry, and raise the token limit — a loud
        failure you can see beats a quiet one you cannot.

3. You constrain a model to `{"answer": <number>}` and accuracy on word
   problems drops. Explain, and fix the schema.

    ??? success "Answer"
        The schema leaves no room for intermediate steps, so the model must
        emit the final number as its very first content token — it cannot
        work through the problem. Add a reasoning field *before* the answer:
        `{"reasoning": {"type": "string"}, "answer": {"type": "number"}}`
        with `"required": ["reasoning", "answer"]`. Because JSON is generated
        left to right, the model writes its reasoning first and can attend to
        it when producing the number.

4. Which of these can constrained decoding enforce: a valid ISO date, a
   temperature between $-90$ and $60$, a city that actually exists?

    ??? success "Answer"
        The date, easily — it is a regular expression over characters. The
        numeric range, only partially: a grammar can force a digit pattern,
        but expressing "at most 60" as a grammar is awkward and you should
        validate it after parsing instead. The real city, not at all — that
        is a fact about the world, and no grammar knows the world. Grammars
        enforce form; validation and tools enforce truth.
