# Exercises

## The chapter in brief

- A **class** is a blueprint and an **instance** is one object built from it —
  `str` is a class, `"hello"` and `"goodbye"` are two instances
  ([12.1](01-class-anatomy.md)).
- `__init__` runs automatically whenever an object is constructed, and stores
  that object's state through `self`.
- `self` is nothing but the first parameter: `rex.bark()` *is*
  `Dog.bark(rex)`, which is why omitting it gives "takes 0 positional
  arguments but 1 was given".
- Every instance carries its own attributes, so ageing one dog leaves every
  other dog untouched.
- `__repr__` **returns** the string Python uses wherever the object is
  displayed — `print`, error messages, and each element of a printed list.
- Attribute lookup checks the instance first and falls back to the class,
  which is what makes a **class attribute** shared, and shadowable by an
  instance attribute of the same name.
- Java's field, constructor, `this`, and `static` field map one-for-one onto
  Python's instance attribute, `__init__`, `self`, and class attribute.
- Classes are grown **in stages**: the smallest useful version first, run it,
  then add the payoff methods ([12.2](02-worked-examples.md)).
- Methods should **return** their answers rather than print them, and every
  method should apply the same policy to the awkward empty case.
- **Composition** is one object holding others — a `DogHouse` HAS-A list of
  `Dog`s — and whole objects, not bare strings, are what flow between them.
- A first draft of a design comes from the problem statement: nouns become
  classes, verbs become methods.
- A rule enforced inside exactly one method is a rule that costs exactly one
  edit when the requirements change.

### Key terms

| Term | Reminder |
| --- | --- |
| [class](../concept-index.md) | the blueprint: what data an object carries and what it can do |
| [instance](../concept-index.md) | one object built from that blueprint |
| [constructor](../concept-index.md) | Java's name for the job `__init__` does at construction time |
| `self` | the object the method was called on, arriving as the first parameter |
| attribute | a variable stored on the object itself, written `self.something` |
| [method](../concept-index.md) | a function that lives in a class and works on one instance |
| [`__repr__`](../concept-index.md) | the self-description Python prints for your object |
| [class attribute vs instance attribute](../concept-index.md) | one shared copy versus one copy per object |
| [composition](../concept-index.md) | an object holding other objects — the HAS-A relationship |

Now build a few of your own.

Before writing any class, run the designer's checklist from the
[worked examples](02-worked-examples.md): find the nouns (classes and
attributes), find the verbs (methods), and decide the awkward cases up
front. Attempt each exercise before opening the solution — with classes, the
learning happens in the writing.

### Exercise 12.1 — A class of your own (●)

Write a `Cat` class whose `__init__` stores a `name`, and whose `meow()`
method prints `<name> says: Meow!`. Create two cats with different names and
make each one meow, proving they keep separate state.

??? success "Solution"

    ```python
    class Cat:
        def __init__(self, name):
            self.name = name

        def meow(self):
            print(f"{self.name} says: Meow!")

    whiskers = Cat("Whiskers")
    mochi = Cat("Mochi")

    whiskers.meow()
    mochi.meow()
    ```

    Each construction call runs `__init__` on a fresh object, so each cat
    carries its own `name`; inside `meow`, `self` is whichever cat sits
    before the dot.

### Exercise 12.2 — Rectangle: area and perimeter (●)

Write a `Rectangle` class storing `width` and `height`, with methods
`area()` and `perimeter()` that **return** (not print) their results. Check
it on a 4 × 3 rectangle: area 12, perimeter 14.

??? success "Solution"

    ```python
    class Rectangle:
        def __init__(self, width, height):
            self.width = width
            self.height = height

        def area(self):
            return self.width * self.height

        def perimeter(self):
            return 2 * (self.width + self.height)

    r = Rectangle(4, 3)
    print("area:", r.area())
    print("perimeter:", r.perimeter())
    ```

    Both methods compute purely from the object's own attributes — no
    parameters needed, because everything they require rode in on `self`.

### Exercise 12.3 — Click counter (●)

Build a `ClickCounter` with a `total` starting at 0, a `click()` method that
adds 1, and a `reset()` that sets it back to 0. Click three times, print the
total, reset, click once more, and print again (expect `3` then `1`).

??? success "Solution"

    ```python
    class ClickCounter:
        def __init__(self):
            self.total = 0

        def click(self):
            self.total += 1

        def reset(self):
            self.total = 0

    counter = ClickCounter()
    counter.click()
    counter.click()
    counter.click()
    print(counter.total)

    counter.reset()
    counter.click()
    print(counter.total)
    ```

    The whole point of an object is state that persists between method
    calls: each `click()` finds `total` exactly where the last one left it.

### Exercise 12.4 — Rectangle: scale (●●)

Extend Exercise 12.2 with a `scale(factor)` method that multiplies **both**
dimensions in place, and a `__repr__` like `Rectangle(4x3)`. Scale a 4 × 3
rectangle by 2 and confirm the area quadruples (from 12 to 48) — a factor of
$2^2$, since both sides doubled.

??? success "Solution"

    ```python
    class Rectangle:
        def __init__(self, width, height):
            self.width = width
            self.height = height

        def __repr__(self):
            return f"Rectangle({self.width}x{self.height})"

        def area(self):
            return self.width * self.height

        def scale(self, factor):
            self.width *= factor
            self.height *= factor

    r = Rectangle(4, 3)
    print(r, "area:", r.area())

    r.scale(2)
    print(r, "area:", r.area())
    ```

    `scale` *mutates* the object — the same rectangle changes size. A
    reasonable alternative design returns a brand-new scaled `Rectangle`
    and leaves the original untouched; either is fine, as long as the
    method's name and documentation make the choice clear.

### Exercise 12.5 — Predict the output: shared or not? (●●)

This program mixes class attributes and instance attributes. Write down all
four lines of output **before** running it.

```text
class Robot:
    factory = "Acme"

    def __init__(self, name):
        self.name = name

r1 = Robot("R2")
r2 = Robot("C3")
print(r1.factory, r2.factory)

Robot.factory = "Globex"
print(r1.factory, r2.factory)

r1.factory = "HomeMade"
print(r1.factory, r2.factory)
print(Robot.factory)
```

??? success "Solution"

    ```python
    class Robot:
        factory = "Acme"

        def __init__(self, name):
            self.name = name

    r1 = Robot("R2")
    r2 = Robot("C3")
    print(r1.factory, r2.factory)

    Robot.factory = "Globex"
    print(r1.factory, r2.factory)

    r1.factory = "HomeMade"
    print(r1.factory, r2.factory)
    print(Robot.factory)
    ```

    Output: `Acme Acme`, then `Globex Globex`, then `HomeMade Globex`, then
    `Globex`. Attribute lookup checks the instance first, then falls back to
    the class — so changing `Robot.factory` affects every robot *without*
    its own copy, while `r1.factory = "HomeMade"` creates an instance
    attribute that shadows the shared one on `r1` alone.

### Exercise 12.6 — BankAccount with guards (●●)

Write a `BankAccount` storing an `owner` and a `balance`. `deposit(amount)`
must refuse amounts that are zero or negative; `withdraw(amount)` must also
refuse amounts larger than the balance. Both return `True` on success and
`False` on refusal, and refusals must leave the balance unchanged. Add a
`__repr__`, then test: deposit 50, deposit −20, withdraw 200, withdraw 75 on
an account opened with 100.

??? success "Solution"

    ```python
    class BankAccount:
        def __init__(self, owner, balance=0):
            self.owner = owner
            self.balance = balance

        def __repr__(self):
            return f"BankAccount({self.owner!r}, balance={self.balance})"

        def deposit(self, amount):
            if amount <= 0:
                return False
            self.balance += amount
            return True

        def withdraw(self, amount):
            if amount <= 0 or amount > self.balance:
                return False
            self.balance -= amount
            return True

    acct = BankAccount("Kim", 100)
    print(acct.deposit(50))    # True   (balance 150)
    print(acct.deposit(-20))   # False  (refused)
    print(acct.withdraw(200))  # False  (more than the balance)
    print(acct.withdraw(75))   # True   (balance 75)
    print(acct)
    ```

    The guards run *before* any state changes, so a refused operation
    leaves the object exactly as it found it. This guard-first shape is how
    classes keep their promises — the balance can never go negative because
    no method allows it to.

### Exercise 12.7 — Playlist of Songs (●●●)

Composition time. Write a `Song` class (`title`, `seconds`, and a
`__repr__`), and a `Playlist` that HAS-A list of songs with methods
`add(song)`, `total_seconds()`, and `longest()` (returning the longest
`Song`, or `None` for an empty playlist). Add three songs and print the
playlist's total time as `minutes:seconds` — `divmod(total, 60)` splits it
in one step.

??? success "Solution"

    ```python
    class Song:
        def __init__(self, title, seconds):
            self.title = title
            self.seconds = seconds

        def __repr__(self):
            return f"Song({self.title!r}, {self.seconds}s)"


    class Playlist:
        def __init__(self, name):
            self.name = name
            self.songs = []

        def add(self, song):
            self.songs.append(song)

        def total_seconds(self):
            total = 0
            for song in self.songs:
                total += song.seconds
            return total

        def longest(self):
            if len(self.songs) == 0:
                return None
            longest = self.songs[0]
            for song in self.songs:
                if song.seconds > longest.seconds:
                    longest = song
            return longest

    mix = Playlist("Road Trip")
    mix.add(Song("Highway Song", 210))
    mix.add(Song("Detour", 185))
    mix.add(Song("Long Straight Road", 240))

    minutes, seconds = divmod(mix.total_seconds(), 60)
    print(f"total: {minutes}:{seconds:02d}")
    print("longest:", mix.longest())
    ```

    Prints `total: 10:35` and `longest: Song('Long Straight Road', 240s)`.
    The playlist never looks inside a song beyond asking for `seconds` —
    each class minds its own data, which is composition working as
    intended.

### Exercise 12.8 — Puppies count half (●●●)

The [worked examples](02-worked-examples.md) claimed that changing the
capacity rule to "puppies under one year count half" would touch only the
`DogHouse`. Prove it. Give `Dog` an `age`, then rewrite `DogHouse` with a
`load()` method (the current total, counting puppies as 0.5) and an `add`
that refuses any dog who would push `load()` past `capacity`. In a house
with capacity 2, show that one adult and two puppies fit, but a third puppy
is refused.

??? success "Solution"

    ```python
    class Dog:
        def __init__(self, name, age):
            self.name = name
            self.age = age

        def __repr__(self):
            return f"Dog({self.name!r}, age={self.age})"


    class DogHouse:
        def __init__(self, capacity):
            self.capacity = capacity
            self.dogs = []

        def __repr__(self):
            return f"DogHouse(load {self.load()}/{self.capacity}: {self.dogs})"

        def load(self):
            total = 0
            for dog in self.dogs:
                total += 0.5 if dog.age < 1 else 1
            return total

        def add(self, dog):
            cost = 0.5 if dog.age < 1 else 1
            if self.load() + cost > self.capacity:
                return False
            self.dogs.append(dog)
            return True

    house = DogHouse(2)
    print(house.add(Dog("Rex", 3)))       # adult: True  (load 1)
    print(house.add(Dog("Pip", 0.5)))     # puppy: True  (load 1.5)
    print(house.add(Dog("Dot", 0.4)))     # puppy: True  (load 2.0)
    print(house.add(Dog("Taz", 0.2)))     # puppy: False (would be 2.5)
    print(house)
    ```

    Only `DogHouse` changed — `Dog` merely gained the `age` attribute the
    rule needs, and no code *outside* the classes needed to know the rule
    exists. That is the localizing power of putting rules behind methods,
    and [encapsulation](../ch13-design/01-encapsulation.md) will make the
    arrangement tamper-proof.
