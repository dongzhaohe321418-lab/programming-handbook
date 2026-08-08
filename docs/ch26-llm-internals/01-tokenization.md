# 26.1 From text to tokens

A language model is a pile of numbers — millions of them, arranged in
matrices — and matrices can only multiply numbers. They cannot multiply the
letter `h`. So before a model sees a single word of your prompt, something
must turn your text into a list of integers, and turn the model's integers
back into text. That something is the **tokenizer**, and it is the least
glamorous, most consequential piece of the whole stack: it decides what the
model can perceive, how long your context is, and what you get billed. Most
of the famous "the model is stupid" screenshots on the internet are really
screenshots of tokenization.

## Vocabulary and IDs

A tokenizer is two lookup tables. One maps each **token** (a piece of text)
to an integer **ID**; the other maps IDs back to text. The set of all tokens
is the **vocabulary**. The simplest possible choice of token is a single
character:

```python
text = "cat sat"

vocab = sorted(set(text))                    # every distinct character
stoi = {ch: i for i, ch in enumerate(vocab)}  # string -> integer
itos = {i: ch for ch, i in stoi.items()}      # integer -> string

print("vocabulary :", vocab)
print("vocab size :", len(vocab))

ids = [stoi[ch] for ch in text]
print("encoded    :", ids)
print("decoded    :", "".join(itos[i] for i in ids))
```

That is genuinely all a tokenizer is, structurally. Everything that follows
is about choosing *better pieces* than single characters.

## Three ways to cut text up

| Granularity | Vocab size | Sequence length | Unknown words |
| --- | --- | --- | --- |
| Characters | tiny (~100) | very long | impossible — every word is spellable |
| Words | huge (100k+) | short | fatal — anything unseen becomes `<unk>` |
| **Subwords** | ~30k–200k | medium | handled — rare words split into known pieces |

The two extremes are both bad, and they are bad in opposite directions:

```python
sentence = "the unhappiness of an unkind cat"

char_tokens = list(sentence)
word_tokens = sentence.split()
print("characters:", len(char_tokens), "tokens, vocab from this text:",
      len(set(char_tokens)))
print("words     :", len(word_tokens), "tokens, vocab from this text:",
      len(set(word_tokens)))

# A word-level tokenizer trained on a corpus that never contained
# "unhappiness" simply cannot represent it:
known = {"the", "of", "an", "unkind", "cat", "happy", "happiness"}
print("word-level view:", [w if w in known else "<unk>" for w in word_tokens])
```

Each extreme fails in its own direction:

- **Characters make the sequence more than five times longer.** Attention cost
  grows with the *square* of the sequence length (Section 26.2), so a longer
  sequence is expensive out of all proportion.
- **Words make the sequence short but throw away real information.** `<unk>`
  erases the fact that *unhappiness* is *un* + *happiness*.

**Subword** tokenization takes the deal in the middle: common words stay
whole, rare words break into reusable fragments, and nothing is ever
unrepresentable.

## Byte-pair encoding, built from scratch

**Byte-pair encoding (BPE)** is the algorithm behind the tokenizers of
essentially every modern LLM. It is greedy and almost embarrassingly simple:

1. Start with every word split into single characters.
2. Count every adjacent pair of symbols across the corpus.
3. Merge the most frequent pair everywhere — it becomes one new symbol.
4. Repeat for a fixed number of merges.

The result is a **merge list**: an ordered recipe of "glue these two pieces
together". Frequent letter sequences (`th`, `ing`, `ness`) become single
tokens because they earn their place statistically, not because a linguist
put them there. Here is the whole trainer:

```python
from collections import Counter

CORPUS = """
a happy dog and a happy cat share the happiness of a walk
kindness and happiness are learned slowly
an unhappy cat is an unkind cat and an unkind cat is unhappy
unkindness and sadness follow unkind acts
the sadness of an unhappy dog is real sadness
kindness undoes unkindness and happiness undoes sadness
"""

def symbols(word):
    """A word as a tuple of symbols; '_' marks the end of the word."""
    return tuple(list(word) + ["_"])

def pair_counts(vocab):
    counts = Counter()
    for syms, freq in vocab.items():
        for pair in zip(syms, syms[1:]):     # every adjacent pair
            counts[pair] += freq
    return counts

def merge_pair(vocab, pair):
    """Replace every occurrence of `pair` by the glued-together symbol."""
    out = {}
    for syms, freq in vocab.items():
        new, i = [], 0
        while i < len(syms):
            if i + 1 < len(syms) and (syms[i], syms[i + 1]) == pair:
                new.append(syms[i] + syms[i + 1])
                i += 2
            else:
                new.append(syms[i])
                i += 1
        out[tuple(new)] = freq
    return out

def train_bpe(text, n_merges):
    vocab = {symbols(w): f for w, f in Counter(text.lower().split()).items()}
    merges = []
    for _ in range(n_merges):
        counts = pair_counts(vocab)
        if not counts:
            break
        # most frequent pair; ties broken alphabetically so runs are repeatable
        pair = min(counts.items(), key=lambda kv: (-kv[1], kv[0]))[0]
        merges.append((pair, counts[pair]))
        vocab = merge_pair(vocab, pair)
    return merges

merges = train_bpe(CORPUS, 20)
print(f"{len(merges)} merges learned from {len(CORPUS.split())} words\n")
for step, (pair, count) in enumerate(merges, start=1):
    glued = pair[0] + pair[1]
    print(f"{step:>2}. {pair[0] + ' + ' + pair[1]:<16} -> {glued:<10} (seen {count}x)")
```

Read that list top to bottom and you are watching a vocabulary being born:

- **Step 1** glues `s` to the end-of-word marker, because plural endings are
  everywhere.
- **By step 5** the tokenizer owns the suffix `ness_` as a single symbol.
- **By step 8** it owns the stem `happ`.
- **By step 10** it owns the negation prefix `un`.

Nobody told it about English morphology. Those are simply the pairs that paid
off.

### Encoding with the merge list

To tokenize a *new* word, apply the learned merges in the order they were
learned, always taking the earliest-learned merge available:

```python
# continues
rank = {pair: i for i, (pair, _count) in enumerate(merges)}

def encode_word(word):
    syms = list(symbols(word))
    while True:
        options = [(rank[p], i) for i, p in enumerate(zip(syms, syms[1:])) if p in rank]
        if not options:
            return syms
        _, i = min(options)                  # earliest-learned merge wins
        syms[i:i + 2] = [syms[i] + syms[i + 1]]

def encode(text):
    return [t for w in text.lower().split() for t in encode_word(w)]

def decode(tokens):
    return "".join(tokens).replace("_", " ").strip()

# the finished vocabulary: base characters plus every merged symbol
base = {c for w in CORPUS.lower().split() for c in symbols(w)}
token_list = sorted(base | {a + b for (a, b), _c in merges})
token_id = {t: i for i, t in enumerate(token_list)}
print("vocabulary size:", len(token_list))

for word in ["happy", "happiness", "kindness", "unhappiness", "unkindly"]:
    print(f"{word:<12} -> {encode_word(word)}")

round_trip = "an unkind cat"
print("\ntokens:", encode(round_trip))
print("IDs   :", [token_id[t] for t in encode(round_trip)])
print("decode:", repr(decode(encode(round_trip))))
print("round-trip ok:", decode(encode(round_trip)) == round_trip)
```

Look at **`unhappiness`**. That exact word never appears in the corpus — but
the tokenizer does not blink. It emits `un`, `happ`, `i`, `ness_`: a prefix,
a stem, a joint, a suffix. A word-level tokenizer would have produced
`<unk>` and destroyed the meaning; a character tokenizer would have produced
eleven tokens. This is the entire reason BPE won.

!!! note "This is the real algorithm, at toy scale"
    The trainer above is faithful — GPT-2, Llama, and Mistral tokenizers are
    trained by the same loop. What is toy is the scale: 40-odd words and 20
    merges here versus hundreds of gigabytes and 50,000–200,000 merges
    there. Real implementations also work on **raw bytes** rather than
    characters, so every possible input (emoji, Korean, binary junk) is
    representable and nothing is ever `<unk>`.

## A token is not a word

Once you have run a tokenizer over a few kinds of text, "context window of
128,000 tokens" stops being an abstract number. English prose that looks
like the training data packs tightly; everything else costs more.

```python
# continues
samples = {
    "familiar English": "an unkind cat and an unhappy dog",
    "unseen English  ": "the astronaut recalibrated",
    "digits          ": "2026 8 7",
    "code            ": "def f(x): return x*2",
    "punctuation     ": "wow!!! ... really???",
    "non-English     ": "猫はとても不幸です",
}
print(f"{'text kind':<17} {'chars':>5} {'words':>5} {'tokens':>6}  chars/token")
for kind, s in samples.items():
    n_tok = len(encode(s))
    print(f"{kind} {len(s):>5} {len(s.split()):>5} {n_tok:>6}  {len(s) / n_tok:>10.2f}")
```

Read the last column. Familiar English packs over two characters into every
token, while everything else collapses towards **one character per token**.
Digits, punctuation, code, and Japanese never won a merge in this corpus, so
they fall back to their raw pieces.

Real tokenizers show exactly this pattern for exactly this reason. One
trained mostly on English web text spends several times more tokens per
sentence on Hindi, Thai, or Chinese than on English — same meaning, several
times the price, several times the context window consumed.

!!! info "Whitespace is not free"
    Modern byte-level BPE attaches the leading space to a word, so `"the"`
    and `" the"` are **different tokens** with different IDs. That is why
    indentation-heavy code and text with trailing spaces tokenize
    surprisingly badly, and why a stray space at the end of a prompt can
    nudge a model's output.

## Why tokenization explains weird LLM failures

### Counting letters

Ask a model how many `s` are in *happiness* and it may well get it wrong.
Here is why: it never sees the letters.

```python
# continues
word = "happiness"
pieces = encode_word(word)
print("what you see :", list(word))
print("what it sees :", pieces)
print("as opaque IDs:", [token_id[p] for p in pieces], "<- no letters in here")
print("letters hidden inside each ID:", [len(p.rstrip('_')) for p in pieces])
```

To the model, `happ` is not the letters h-a-p-p. It is one ID — a row number
in a lookup table, no more spelled-out than the number 12 is.

Counting characters therefore requires the model to have *memorised the
spelling of every token* and then do arithmetic on that memory. It is a
genuinely hard task presented in a maximally unhelpful format, like being
asked to count the strokes in a word you only ever hear spoken.

### Arithmetic and digit alignment

The same effect wrecks arithmetic. Watch what a BPE trained on numbers does:

```python
# continues
NUMBERS = "2020 2021 2022 2023 2024 2025 100 200 300 1000 2000 3000 " * 4
num_merges = train_bpe(NUMBERS, 6)
num_rank = {pair: i for i, (pair, _c) in enumerate(num_merges)}

def encode_number(s):
    syms = list(symbols(s))
    while True:
        options = [(num_rank[p], i) for i, p in enumerate(zip(syms, syms[1:]))
                   if p in num_rank]
        if not options:
            return [t for t in (x.rstrip("_") for x in syms) if t]
        _, i = min(options)
        syms[i:i + 2] = [syms[i] + syms[i + 1]]

for s in ["2025", "1234", "2000", "999"]:
    print(f"{s:>5} -> {str(encode_number(s)):<28} {len(encode_number(s))} tokens")
```

Look at how differently the same four-digit shape gets cut up:

- `2025` arrives as two chunks, `202` + `5`.
- `1234` arrives digit by digit.
- `2000` arrives as `2` + `000`.

The units digit lands in a different token position in every one of them. So
"add these two numbers" is not the tidy column-aligned task it is for you —
the model has to learn arithmetic through a shredder. (Newer tokenizers
deliberately split digits into fixed groups to reduce exactly this problem,
and models still lean on tools for real arithmetic.)

## Context windows are measured in tokens

Every limit you will ever hit is counted in tokens, not words or characters:
the context window, the price per million, and the memory the model spends
remembering the conversation while it generates (Section 26.3 computes that
one). For ordinary English, a useful rule of thumb is **about 4 characters
or about 0.75 words per token**:

```python
def token_estimate(words):
    """English prose: roughly 4/3 of a token per word."""
    return round(words * 4 / 3)

page_words = 500                      # one typical page of a book
for window in [4_096, 32_768, 128_000, 1_000_000]:
    pages = window / token_estimate(page_words)
    print(f"{window:>9,} tokens  ~=  {pages:>6.1f} pages of English prose")
```

Two consequences are worth internalising now:

- **The window is shared.** Your system prompt, the documents you paste, the
  conversation so far, and the model's own reply all draw from one budget.
- **Cost and latency grow with it.** Attention work grows quadratically with
  sequence length and cache memory grows linearly, which is why every
  long-context system spends its ingenuity on exactly those two curves.

## Special tokens and chat templates

Vocabularies contain a few tokens that are not text at all. They are control
signals, usually written in angle brackets so they cannot collide with real
text:

| Token | Name | Job |
| --- | --- | --- |
| `<bos>` | beginning of sequence | marks the start of input |
| `<eos>` | end of sequence | the model emits it to say "I'm done" |
| `<pad>` | padding | filler so a batch of sequences is rectangular |
| `<unk>` | unknown | fallback for unrepresentable text (rare in byte-level BPE) |

A chat model is still just a next-token predictor. "Roles" are an illusion
created by wrapping the conversation in special tokens before tokenizing —
the **chat template**. A typical one looks like this:

```text
<bos><|system|>
You are a helpful assistant.<|end|>
<|user|>
What is 2 + 2?<|end|>
<|assistant|>
4<|eos|>
```

The exact markers differ per model family and are shipped *with* the model.
Using the wrong template is a classic silent bug: the model still answers,
just noticeably worse, because the prompt no longer looks like its training
data. Two practical rules follow:

1. **Never invent your own role markers.** Use the template that ships with
   the checkpoint.
2. **Remember that `<eos>` is what stops generation** (Section 26.4). It is a
   token in the vocabulary like any other.

!!! warning "Common mistakes"
    - **Assuming one word = one token.** Budget with a tokenizer, not with
      `len(text.split())`. Code, JSON, non-English text, and long numbers
      can cost two to four times more tokens than the word count suggests.
    - **Blaming the model for spelling and counting errors.** "How many r's
      in strawberry" is a tokenization artefact, not evidence about
      reasoning. Ask for character work through a tool instead.
    - **Mixing tokenizers between models.** IDs are model-specific; token
      42 in one vocabulary is unrelated to token 42 in another. Always use
      the tokenizer shipped with the checkpoint.
    - **Forgetting the reply shares the window.** If your prompt fills the
      context, there is no room left to answer, and the request either
      truncates or errors.

## Check your understanding

1. Why does BPE merge `'s'` with the end-of-word marker before it merges
   anything else on our corpus?

    ??? success "Answer"

        Because that is the most frequent adjacent pair in the training
        text — plural and possessive endings are everywhere, so `s_`
        earns the very first merge. BPE has no linguistic knowledge; it
        only counts.

2. A word-level tokenizer meets the word `tokenizers` for the first time.
   What does it emit, and what does a BPE tokenizer emit instead?

    ??? success "Answer"

        The word-level tokenizer emits `<unk>` — the word is simply not in
        its table, and all information is lost. BPE emits several known
        pieces (something like `token`, `izer`, `s`), so the model still
        sees the stem and the suffixes and can generalise from words it
        has seen.

3. You are charged per token. Which costs more to send: 1,000 words of
   English prose, or 1,000 "words" of minified JSON? Why?

    ??? success "Answer"

        The JSON, usually by a wide margin. Braces, quotes, colons, random
        identifiers, and long numbers rarely form high-frequency pairs, so
        they fall back to short pieces or single characters — many more
        tokens per visible character than ordinary prose.

4. Our tokenizer split `unhappiness` into `un`, `happ`, `i`, `ness_`. Why
   is that better for the model than a single `<unk>` token, even though
   `unhappiness` never appeared in training?

    ??? success "Answer"

        Because every piece is a token the model has seen thousands of
        times in other words. It can compose the meaning — negation
        prefix, familiar stem, noun-forming suffix — instead of receiving
        a black hole. Generalising to unseen words is exactly what subword
        tokenization buys.
