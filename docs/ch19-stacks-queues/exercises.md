# Exercises

Work these in order — they start with prediction drills and end with a
classic interview favourite. For each *predict* exercise, commit to an
answer on paper **before** pressing Run.

### Exercise 19.1 — Predict the stack ●

A list is used as a stack (top = end). Predict the four lines this prints,
then run it to check.

```python
stack = []
stack.append("a")
stack.append("b")
print(stack.pop())
stack.append("c")
stack.append("d")
print(stack.pop())
print(stack.pop())
print(stack)
```

??? success "Solution"

    ```python
    stack = []
    stack.append("a")
    stack.append("b")
    print(stack.pop())   # b  (last in so far)
    stack.append("c")
    stack.append("d")
    print(stack.pop())   # d
    print(stack.pop())   # c
    print(stack)         # ['a']  - a never reached the top
    ```

    The output is `b`, `d`, `c`, `['a']`. Every `pop` takes whatever was
    pushed most recently — `a` went on first, so it is served last and is
    still waiting at the end.

### Exercise 19.2 — Reverse a string with a stack ●

Write `reverse(text)` that pushes every character onto a stack, then pops
them all into a new string. Why does this reverse the text?

??? success "Solution"

    ```python
    def reverse(text):
        stack = []
        for ch in text:
            stack.append(ch)
        out = []
        while stack:
            out.append(stack.pop())
        return "".join(out)

    print(reverse("stacks"))
    print(reverse("racecar"))
    ```

    This prints `skcats` and `racecar`. The last character pushed is the
    first popped, so the pops replay the string back to front — LIFO *is*
    reversal.

### Exercise 19.3 — Predict the queue jumper ●

A `deque` is used as a queue — but someone cuts in line with `appendleft`.
Predict the three printed lines, then run it.

```python
from collections import deque

line = deque()
line.append("ana")
line.append("ben")
print(line.popleft())
line.append("cho")
line.appendleft("vip")     # cutting in at the FRONT
print(line.popleft())
print(list(line))
```

??? success "Solution"

    ```python
    from collections import deque

    line = deque()
    line.append("ana")
    line.append("ben")
    print(line.popleft())    # ana - normal FIFO service
    line.append("cho")
    line.appendleft("vip")   # line is now: vip, ben, cho
    print(line.popleft())    # vip - the queue jumper is served next
    print(list(line))        # ['ben', 'cho']
    ```

    The output is `ana`, `vip`, `['ben', 'cho']`. A deque happily adds at
    either end — the FIFO *discipline* only holds if your code sticks to
    `append` at the back and `popleft` at the front.

### Exercise 19.4 — Evaluate postfix with a stack ●●

In **postfix notation** the operator comes *after* its operands:
`3 4 + 2 *` means $(3 + 4) \times 2$. No parentheses are ever needed.
Evaluate it with a stack: scan the tokens; push every number; on an
operator, pop the top two numbers (careful — the *first* pop is the *right*
operand), apply the operator, and push the result. The final answer is the
lone value left on the stack.

Write `eval_postfix(expr)` and test it on `"3 4 + 2 *"` and
`"5 1 2 + 4 * + 3 -"`.

??? success "Solution"

    ```python
    def eval_postfix(expr):
        stack = []
        for token in expr.split():
            if token in {"+", "-", "*", "/"}:
                right = stack.pop()      # top of stack = RIGHT operand
                left = stack.pop()
                if token == "+":
                    stack.append(left + right)
                elif token == "-":
                    stack.append(left - right)
                elif token == "*":
                    stack.append(left * right)
                else:
                    stack.append(left / right)
            else:
                stack.append(float(token))
        return stack.pop()

    print(eval_postfix("3 4 + 2 *"))          # (3 + 4) * 2
    print(eval_postfix("5 1 2 + 4 * + 3 -"))  # 5 + (1 + 2) * 4 - 3
    ```

    Both expressions print `14.0`. The stack holds exactly the values whose
    operator has not arrived yet — which is why postfix needs no
    parentheses, and why real interpreters and calculators evaluate
    expressions this way.

### Exercise 19.5 — Hot potato (Josephus) ●●

Children stand in a circle passing a potato. Every third pass ($k = 3$),
whoever holds the potato is out; the last child remaining wins. Simulate
this with a queue: passing = move the front child to the back; elimination
= dequeue for good. Print each eliminated child and the winner for
`["Ana", "Ben", "Cho", "Dev", "Eli"]` with `k = 3`.

??? success "Solution"

    ```python
    from collections import deque

    def hot_potato(names, k):
        circle = deque(names)
        while len(circle) > 1:
            for _ in range(k - 1):
                circle.append(circle.popleft())   # pass the potato
            print("out:", circle.popleft())       # k-th holder is out
        return circle[0]

    print("winner:", hot_potato(["Ana", "Ben", "Cho", "Dev", "Eli"], 3))
    ```

    The output is `out: Cho`, `out: Ana`, `out: Eli`, `out: Ben`,
    `winner: Dev`. Rotating the front to the back makes the queue behave
    like a circle — this is the ancient *Josephus problem*, and the
    queue-rotation trick is its standard simulation.

### Exercise 19.6 — Palindrome checker with a deque ●●

A palindrome reads the same forwards and backwards. A deque can check one
elegantly, because it pops from *both* ends: repeatedly compare
`popleft()` with `pop()` until at most one character remains. Ignore
spaces, punctuation, and letter case — test on `"racecar"`,
`"Never odd or even"`, and `"queue"`.

??? success "Solution"

    ```python
    from collections import deque

    def is_palindrome(text):
        letters = deque(ch.lower() for ch in text if ch.isalpha())
        while len(letters) > 1:
            if letters.popleft() != letters.pop():
                return False
        return True

    for phrase in ["racecar", "Never odd or even", "queue"]:
        print(f"{phrase!r}: {is_palindrome(phrase)}")
    ```

    The three lines report `True`, `True`, `False`. Each loop step compares
    the outermost surviving pair and discards it — possible only because a
    deque gives $O(1)$ removal at both ends.

### Exercise 19.7 — Report the first bracket error ●●

Upgrade section 19.2's bracket checker into a linter: `first_error(text)`
returns the **index** of the first problematic character — a closer that
matches nothing, or (if the text ends with brackets still open) the first
unclosed opener. Return `-1` if the text is balanced. Hint: push
`(char, index)` pairs instead of bare characters.

Test on `"()"`, `"([)]"`, `"(()"`, and `"]"`.

??? success "Solution"

    ```python
    def first_error(text):
        pairs = {")": "(", "]": "[", "}": "{"}
        stack = []                          # holds (opener, index) pairs
        for i, ch in enumerate(text):
            if ch in "([{":
                stack.append((ch, i))
            elif ch in ")]}":
                if not stack or stack.pop()[0] != pairs[ch]:
                    return i                # this closer is the problem
        if stack:
            return stack[0][1]              # first opener never closed
        return -1

    for text in ["()", "([)]", "(()", "]"]:
        print(f"{text!r}: first problem at index {first_error(text)}")
    ```

    The output is `-1`, `2`, `0`, `0`. Storing the index alongside each
    opener costs nothing extra and turns a yes/no checker into a tool that
    can point at the offending character — exactly how editors underline
    the bracket that broke your code.

### Exercise 19.8 — A queue built from two stacks ●●●

You are given only stacks (push/pop at one end) and must build a FIFO
queue. The classic solution uses two: `enqueue` pushes onto an *inbox*
stack; `dequeue` pops from an *outbox* stack — and whenever the outbox is
empty, it refills by popping *everything* from the inbox (which reverses
the order, turning LIFO into FIFO). Implement `QueueFromStacks` and verify
FIFO order with interleaved operations. Why is `dequeue` still $O(1)$
*amortised* even though a refill is $O(n)$?

??? success "Solution"

    ```python
    class QueueFromStacks:
        def __init__(self):
            self._inbox = []      # newest arrivals on top
            self._outbox = []     # oldest arrivals on top (reversed inbox)

        def enqueue(self, item):
            self._inbox.append(item)

        def dequeue(self):
            if not self._outbox:              # refill only when empty
                while self._inbox:
                    self._outbox.append(self._inbox.pop())
            return self._outbox.pop()

    q = QueueFromStacks()
    q.enqueue(1)
    q.enqueue(2)
    print(q.dequeue())   # 1
    q.enqueue(3)
    print(q.dequeue())   # 2
    print(q.dequeue())   # 3
    ```

    The output is `1`, `2`, `3` — perfect FIFO from two LIFOs, because one
    reversal (into the inbox) followed by a second reversal (into the
    outbox) restores arrival order. The amortised argument: each element is
    pushed at most twice and popped at most twice over its whole lifetime
    (once per stack), so $n$ operations cost at most $\approx 4n$ stack
    steps — an average of $O(1)$ per operation even though one unlucky
    `dequeue` occasionally pays for a full refill.
