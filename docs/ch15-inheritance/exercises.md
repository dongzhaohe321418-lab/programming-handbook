# Exercises

Work these in order — they climb from reading inherited code to designing
your own contracts. For every exercise: attempt first, peek second.

### Exercise 15.1 — Predict the chain ●

Read this program carefully and **write down the exact output** — every
line, in order — before you run it.

```python
class Instrument:
    def __init__(self, name):
        print("Instrument.__init__")
        self.name = name

    def play(self):
        print(f"{self.name} makes music")

class Guitar(Instrument):
    def __init__(self, name, strings):
        print("Guitar.__init__ begins")
        super().__init__(name)
        print("Guitar.__init__ ends")
        self.strings = strings

g = Guitar("Les Paul", 6)
g.play()
```

??? success "Solution"

    The predicted output is:

    ```text
    Guitar.__init__ begins
    Instrument.__init__
    Guitar.__init__ ends
    Les Paul makes music
    ```

    ```python
    class Instrument:
        def __init__(self, name):
            print("Instrument.__init__")
            self.name = name

        def play(self):
            print(f"{self.name} makes music")

    class Guitar(Instrument):
        def __init__(self, name, strings):
            print("Guitar.__init__ begins")
            super().__init__(name)
            print("Guitar.__init__ ends")
            self.strings = strings

    g = Guitar("Les Paul", 6)
    g.play()
    ```

    The child's constructor starts, *pauses* at `super().__init__` while
    the parent runs to completion, then resumes. `play` is inherited
    unchanged, and `self.name` exists because the chained parent
    constructor created it.

### Exercise 15.2 — An Animal chorus ●

Build a small hierarchy: a base class `Animal` with an `__init__` storing
`name` and a method `speak` that prints `<name> says ...` (a generic
sound). Then write `Dog`, `Cat`, and `Cow` subclasses that override `speak`
with `woof`, `meow`, and `moo`. Finish with a list containing one of each
and a single loop that makes them all speak.

??? success "Solution"

    ```python
    class Animal:
        def __init__(self, name):
            self.name = name

        def speak(self):
            print(f"{self.name} says ...")

    class Dog(Animal):
        def speak(self):
            print(f"{self.name} says woof")

    class Cat(Animal):
        def speak(self):
            print(f"{self.name} says meow")

    class Cow(Animal):
        def speak(self):
            print(f"{self.name} says moo")

    farm = [Dog("Rex"), Cat("Mia"), Cow("Bella")]
    for animal in farm:
        animal.speak()
    ```

    Only `Animal` defines `__init__` — the subclasses inherit it. The loop
    is the polymorphism payoff: one call site, three overrides.

### Exercise 15.3 — Repair the half-built object ●●

This program crashes. Explain *why the crash happens on the last line
rather than during construction*, then fix the bug with a one-line change.

```python
# raises AttributeError
class Employee:
    def __init__(self, name):
        self.name = name

class Manager(Employee):
    def __init__(self, name, team_size):
        self.team_size = team_size     # something is missing here

m = Manager("Sam", 8)
print(m.name, "manages", m.team_size, "people")
```

??? success "Solution"

    `Manager` defines its own `__init__`, which *replaces* the inherited
    one — so `Employee.__init__` never runs and `self.name` is never
    created. Construction succeeds because Python doesn't require any
    particular attributes; the failure waits until `m.name` is touched.
    The fix is to chain:

    ```python
    class Employee:
        def __init__(self, name):
            self.name = name

    class Manager(Employee):
        def __init__(self, name, team_size):
            super().__init__(name)         # the missing line
            self.team_size = team_size

    m = Manager("Sam", 8)
    print(m.name, "manages", m.team_size, "people")
    ```

### Exercise 15.4 — Inheritance or composition? ●●

For each design, apply the is-a test and say whether inheritance is
appropriate. For any bad ones, name the better relationship.

1. `class SavingsAccount(BankAccount)`
2. `class Car(Engine)`
3. `class Circle(Point)` — "a circle is a point plus a radius"
4. `class Duck(Animal)`

Then rewrite design 2 correctly in code, with an `Engine` that can
`start()` and a `Car` whose `drive()` uses it.

??? success "Solution"

    1. **Good.** A savings account is a bank account; it will extend
       deposit/withdraw behaviour.
    2. **Bad.** A car is not an engine — it *has* one. Composition.
    3. **Bad, though it looks clever.** A circle is not a point; it has a
       *centre* which is a point. Inheriting would make `Circle` answer
       point questions it shouldn't. Composition: `self.centre = Point(...)`.
    4. **Good.** A duck is an animal (and it quacks).

    ```python
    class Engine:
        def start(self):
            print("Engine humming.")

    class Car:
        def __init__(self):
            self.engine = Engine()    # has-a, not is-a

        def drive(self):
            self.engine.start()
            print("Car rolling.")

    Car().drive()
    ```

    The is-a sentence test catches 2 and 3 immediately: "a car is an
    engine" and "a circle is a point" both sound wrong out loud.

### Exercise 15.5 — Extend, don't replace ●●

Start from this base class:

```python
class Logger:
    def log(self, message):
        print(f"LOG: {message}")
```

Write `TimestampLogger(Logger)` whose `log` prints `[t=<n>]` before the
normal output — *without copying* the parent's formatting — and where
`<n>` counts how many messages this logger has handled (1, 2, 3, …). You
will need an `__init__`, a counter attribute, and a `super()` call.

??? success "Solution"

    ```python
    class Logger:
        def log(self, message):
            print(f"LOG: {message}")

    class TimestampLogger(Logger):
        def __init__(self):
            self.count = 0

        def log(self, message):
            self.count += 1
            print(f"[t={self.count}] ", end="")
            super().log(message)          # reuse, don't re-implement

    tl = TimestampLogger()
    tl.log("server started")
    tl.log("user logged in")
    ```

    The override adds its stamp and then delegates upward, so any future
    improvement to `Logger.log` is inherited automatically. (Base `Logger`
    needs no `__init__`; `TimestampLogger` adds one for its counter.)

### Exercise 15.6 — A Comparable protocol ●●

Java sorts objects that implement `Comparable`; Python sorts objects that
support `<`. Give this `Student` class a `__lt__(self, other)` method that
compares by GPA, then sort a list of students and print them best-first.
Add a `__repr__` so the printed list is readable.

```text
class Student:
    def __init__(self, name, gpa):
        self.name = name
        self.gpa = gpa
```

??? success "Solution"

    ```python
    class Student:
        def __init__(self, name, gpa):
            self.name = name
            self.gpa = gpa

        def __lt__(self, other):          # the "comparable" protocol
            return self.gpa < other.gpa

        def __repr__(self):
            return f"Student({self.name!r}, {self.gpa})"

    roster = [Student("Ada", 3.9), Student("Ben", 3.4), Student("Cyn", 3.7)]
    print(sorted(roster, reverse=True))
    ```

    `sorted` never asks what a `Student` is — it only needs `<` to work
    between elements. Implementing `__lt__` is joining a protocol, exactly
    like Java's `compareTo`, but with no interface declaration required:
    duck typing again.

### Exercise 15.7 — Abstract base drill ●●●

Define an ABC `Sensor` with an abstract method `read(self)` and a concrete
method `report(self)` that prints `<ClassName>: <value>` using `read`.
Then:

1. show that instantiating `Sensor` raises `TypeError` (as a separate,
   expected-to-fail snippet),
2. implement `FakeThermometer` (returns a fixed 21.5) and `Dice`
   (returns a seeded random roll), and
3. loop over one of each, calling `report`.

??? success "Solution"

    The contract refuses to be instantiated:

    ```python
    # raises TypeError
    from abc import ABC, abstractmethod

    class Sensor(ABC):
        @abstractmethod
        def read(self):
            """Return the current measurement."""

    s = Sensor()
    ```

    And the working implementations:

    ```python
    import random
    from abc import ABC, abstractmethod

    class Sensor(ABC):
        @abstractmethod
        def read(self):
            """Return the current measurement."""

        def report(self):
            print(f"{type(self).__name__}: {self.read()}")

    class FakeThermometer(Sensor):
        def read(self):
            return 21.5

    class Dice(Sensor):
        def read(self):
            return random.randint(1, 6)

    random.seed(3)
    for sensor in [FakeThermometer(), Dice()]:
        sensor.report()
    ```

    `report` lives once in the ABC and calls the abstract `read` — the
    same skeleton-plus-specifics pattern as `Shape.describe`, but now the
    "specifics" part is machine-enforced.

### Exercise 15.8 — A plug-in exporter ●●●

You are shipping a report tool. Core function:

```text
def export(data, formatter):
    print(formatter.format(data))
```

Design a `Formatter` ABC with abstract `format(self, data)`, then implement
`CSVFormatter` (comma-separated, one line per row) and `JSONFormatter`
(use the `json` module) for data shaped like
`[{"name": "Ada", "score": 91}, {"name": "Ben", "score": 84}]`.
Drive both through `export` without changing it. Finally, add a third
"plug-in" of your own design (e.g. a Markdown table) — confirm `export`
still needs no edits.

??? success "Solution"

    ```python
    import json
    from abc import ABC, abstractmethod

    class Formatter(ABC):
        @abstractmethod
        def format(self, data):
            """Return the data as a string in this format."""

    class CSVFormatter(Formatter):
        def format(self, data):
            lines = [",".join(row) for row in
                     ([str(v) for v in item.values()] for item in data)]
            return "\n".join(lines)

    class JSONFormatter(Formatter):
        def format(self, data):
            return json.dumps(data, indent=2)

    class MarkdownFormatter(Formatter):           # the third plug-in
        def format(self, data):
            header = "| name | score |\n| --- | --- |"
            rows = [f"| {d['name']} | {d['score']} |" for d in data]
            return "\n".join([header] + rows)

    def export(data, formatter):                  # written once, never edited
        print(formatter.format(data))

    data = [{"name": "Ada", "score": 91}, {"name": "Ben", "score": 84}]
    for fmt in [CSVFormatter(), JSONFormatter(), MarkdownFormatter()]:
        print(f"--- {type(fmt).__name__} ---")
        export(data, fmt)
    ```

    `export` depends only on the contract, so formatters are genuinely
    pluggable — the essence of every real plug-in system, from text
    editors to web frameworks. The ABC guarantees each plug-in actually
    provides `format` before it can even be constructed.
