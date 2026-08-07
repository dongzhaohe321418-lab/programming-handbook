# 13.1 Encapsulation and access control

Every object carries data, and some of that data has rules: a bank balance
must never go negative, a temperature can never drop below absolute zero, a
seat cannot hold two passengers. A rule that must stay true for an object's
entire lifetime is called an **invariant**, and the central question of
class design is: *who is responsible for keeping the invariant true?* If
the answer is "everyone who ever touches the object", the invariant is
doomed. **Encapsulation** is the discipline of hiding an object's data
behind a small set of methods so that the class — and only the class —
enforces its own rules.

## An invariant under attack

Here is a bank account written the way Chapter 12 taught, with everything
out in the open. The comment states the invariant; nothing in the code
defends it.

```python
class BankAccount:
    """Invariant: balance must never go negative."""

    def __init__(self, owner, balance):
        self.owner = owner
        self.balance = balance

acct = BankAccount("Maya", 100.0)
acct.balance -= 250          # nothing stops this line
print(acct.balance)
```

The output is `-150.0`. No error, no warning — the account is quietly
corrupted, and the bug will surface later, far from this line. The
attribute `balance` is a public field: any code, anywhere, can set it to
anything. The invariant exists only in a comment, and comments do not
execute.

## The protected version

The fix is to move the balance behind methods that check the rules. By
convention (much more on this below), we rename the attribute `_balance` —
the leading underscore is Python's signal for "internal, please do not
touch".

```python
class BankAccount:
    """Invariant: balance must never go negative."""

    def __init__(self, owner, opening):
        self.owner = owner
        self._balance = opening      # internal — hands off

    def withdraw(self, amount):
        if amount <= 0 or amount > self._balance:
            return False             # refuse, politely
        self._balance -= amount
        return True

    def balance(self):
        return self._balance

acct = BankAccount("Maya", 100.0)
print(acct.withdraw(250))    # too much — refused
print(acct.balance())
print(acct.withdraw(30))     # within the rules
print(acct.balance())
```

The output:

```text
False
100.0
True
70.0
```

The over-withdrawal is refused and the balance survives. Notice the shape
of the design: *one* class contains *all* the code that can change
`_balance`, so there is exactly one place to check the invariant — and
exactly one place to look when something goes wrong. That locality is the
real prize of encapsulation, and it matters more as programs grow.

## How Java locks the door

Your Java course spends serious time on **access modifiers** — keywords
that make the compiler enforce what Python merely requests. The same
account looks like this in each language:

=== "Java"

    ```java
    public class BankAccount {
        private double balance;          // this class only — enforced

        public BankAccount(double opening) {
            balance = opening;
        }

        public double getBalance() {
            return balance;
        }
    }
    // elsewhere: acct.balance = -150;   <-- does not compile
    ```

=== "Python"

    ```python
    class BankAccount:
        def __init__(self, opening):
            self._balance = opening      # "private" by politeness only

        def balance(self):
            return self._balance

    acct = BankAccount(100.0)
    acct._balance = -150     # legal — but you broke the social contract
    print(acct.balance())
    ```

In Java, writing `acct.balance = -150;` from outside the class is a
*compile-time error* — the program never even starts. Java offers four
levels of visibility; the middle two involve **packages**, Java's way of
grouping related classes into named folders (`java.util`, `bank.accounts`):

| Modifier | Who can see the member |
| --- | --- |
| `public` | everyone, everywhere |
| `protected` | the same package, plus subclasses anywhere |
| *(no modifier)* — "package-private" | the same package only |
| `private` | the same class only |

## Python's convention system

Python has no `private` keyword. Instead it has a naming convention with
three levels, and one of them does something surprising under the hood:

| Spelling | Meaning | Enforced? |
| --- | --- | --- |
| `name` | public — part of the class's official interface | — |
| `_name` | internal — "please don't touch" | no, purely convention |
| `__name` | strongly internal — Python *mangles* the name | only by renaming |

The double underscore triggers **name mangling**: inside class `Robot`,
the attribute `__serial` is silently renamed to `_Robot__serial`. Watch it
happen:

```python
class Robot:
    def __init__(self):
        self.name = "R2"          # public
        self._battery = 90        # internal by convention
        self.__serial = "XJ-42"   # name-mangled

r = Robot()
print(r.name)
print(r._battery)                 # allowed — just impolite
print(list(vars(r)))              # the attribute names actually stored
print(r._Robot__serial)           # the mangled name still works
```

The output:

```text
R2
90
['name', '_battery', '_Robot__serial']
XJ-42
```

The third line reveals the trick: the object has no attribute called
`__serial` at all — it stores `_Robot__serial`. That is why the
straightforward spelling fails from outside:

```python
# raises AttributeError
class Robot:
    def __init__(self):
        self.__serial = "XJ-42"

r = Robot()
print(r.__serial)     # no such name outside the class
```

Name mangling exists to prevent *accidental* clashes between a class and
its subclasses, not to provide security — as you just saw, anyone who
types the mangled name gets in. Most Python code uses a single underscore
and good manners.

## Properties: attribute access with a guard inside

The protected `BankAccount` above forces callers to write
`acct.balance()` with parentheses. Java programmers accept `getBalance()`
as the price of safety. Python offers something better: a **property**
turns attribute *syntax* into method *calls*, so callers write plain
`t.celsius` and `t.celsius = 25` while your validation code runs invisibly
underneath.

```python
class Thermostat:
    def __init__(self, celsius):
        self.celsius = celsius        # this line runs the setter below!

    @property
    def celsius(self):                # runs on every READ of t.celsius
        return self._celsius

    @celsius.setter
    def celsius(self, value):         # runs on every WRITE to t.celsius
        if value < -273.15:
            raise ValueError(f"{value} is below absolute zero")
        self._celsius = value

    @property
    def fahrenheit(self):             # derived and read-only
        return self._celsius * 9 / 5 + 32

t = Thermostat(20)
print(t.celsius)
t.celsius = 25                        # looks like assignment, runs the guard
print(t.fahrenheit)
```

The output is `20` then `77.0`. Three things to absorb:

1. `@property` marks the *getter*; `@celsius.setter` marks the *setter*.
   The real data lives in `self._celsius` — a different name, or the
   setter would call itself forever.
2. Even `__init__` says `self.celsius = celsius`, so construction goes
   through the same guard. Invalid objects cannot even be born.
3. `fahrenheit` has a getter and no setter, making it **read-only** and
   always consistent with the Celsius value — it is computed, never
   stored.

And the guard really guards:

```python
# raises ValueError
class Thermostat:
    def __init__(self, celsius):
        self.celsius = celsius

    @property
    def celsius(self):
        return self._celsius

    @celsius.setter
    def celsius(self, value):
        if value < -273.15:
            raise ValueError(f"{value} is below absolute zero")
        self._celsius = value

t = Thermostat(20)
t.celsius = -400          # colder than physics allows
```

Writing to a property that has no setter is also an error — which is
exactly how you make a read-only attribute:

```python
# raises AttributeError
class BankAccount:
    def __init__(self, opening):
        self._balance = opening

    @property
    def balance(self):
        return self._balance

acct = BankAccount(100.0)
acct.balance = 1_000_000      # no setter — refused
```

Java has no properties, so Java code needs `getX()` / `setX()` methods
from day one — if a field starts public and later needs validation,
switching it to a method changes every caller. Python code can start with
a plain public attribute and *retrofit* a property later with zero changes
to calling code. That is why idiomatic Python does **not** write
`get_`/`set_` methods:

=== "Python"

    ```python
    class Thermostat:
        def __init__(self, celsius):
            self._celsius = celsius

        @property
        def celsius(self):
            return self._celsius

    t = Thermostat(20)
    print(t.celsius)         # attribute syntax, guarded underneath
    ```

=== "Java"

    ```java
    public class Thermostat {
        private double celsius;

        public Thermostat(double celsius) {
            setCelsius(celsius);
        }

        public double getCelsius() { return celsius; }

        public void setCelsius(double value) {
            if (value < -273.15) {
                throw new IllegalArgumentException("below absolute zero");
            }
            celsius = value;
        }
    }
    // Thermostat t = new Thermostat(20);
    // t.setCelsius(25);            // explicit method calls, always
    ```

## Enforcement versus convention — the honest comparison

| | Java | Python |
| --- | --- | --- |
| Who stops misuse | the compiler, before the program runs | nobody — naming conventions and code review |
| "Private" means | `private`, enforced | `_name` (request) or `__name` (mangled) |
| Cost of bypassing | contortions (reflection) | just type the mangled name |
| Guarded access looks like | `t.setCelsius(25)` | `t.celsius = 25` via a property |
| Philosophy | make misuse impossible | "we are all consenting adults" |

Neither system is *security* — a determined programmer defeats both, and
real security lives elsewhere (operating systems, cryptography). Both are
**communication**: they tell the next programmer which parts of a class
are a stable public promise and which are internals that may change
without warning. Java writes that message in a form the compiler checks;
Python writes it in a form humans check. The design skill — deciding what
to expose and what to hide — is identical in both languages, and it is the
skill this chapter is really about.

!!! warning "Common mistakes"

    - **Recursive setter.** Inside the setter, writing `self.celsius =
      value` instead of `self._celsius = value` calls the setter from the
      setter, forever — the program dies with `RecursionError`. The stored
      attribute must have a *different* name than the property.
    - **Believing `__name` is secure.** It is a rename, nothing more.
      Anyone can read `obj._ClassName__name`. Use it to avoid subclass
      clashes, not to "protect" secrets.
    - **Leaking a mutable internal.** A method that does `return
      self._items` hands the caller the real list — they can `.append()`
      past all your checks. Return a copy (`list(self._items)`) or a
      tuple. Exercise 13.1 hunts exactly this bug.
    - **Writing Java in Python.** Reflexively adding `get_x()` and
      `set_x(v)` for every attribute is noise in Python. Start with a
      plain attribute; add a property only when a rule appears.

## Check your understanding

1. What is an invariant, and why did the first `BankAccount` fail to
   maintain one?

    ??? success "Answer"
        An invariant is a condition that must remain true for an object's
        whole lifetime — here, *balance never negative*. The first version
        stored the balance in a public attribute, so any code anywhere
        could assign a value that breaks the rule; the class had no
        opportunity to check anything.

2. Inside class `Spaceship`, an attribute is written `self.__fuel`. What
   name is actually stored on the object, and what happens if outside code
   evaluates `ship.__fuel`?

    ??? success "Answer"
        Name mangling stores it as `_Spaceship__fuel`. Evaluating
        `ship.__fuel` outside the class raises `AttributeError`, because
        no attribute literally named `__fuel` exists — though
        `ship._Spaceship__fuel` would (impolitely) work.

3. Why do Java classes need getters and setters from the very first
   version, while Python classes can safely begin with plain public
   attributes?

    ??? success "Answer"
        In Java, changing a public field into a method later breaks every
        caller (`acct.balance` versus `acct.getBalance()` are different
        syntax). In Python, a plain attribute can be replaced by a
        `@property` with the same name — callers keep writing
        `acct.balance` and never notice the guard that appeared beneath
        it.
