# 15.2 Polymorphism and casting

Inheritance gave our shapes a shared home for common code. Its real payoff,
though, is what it does to the *code that uses* the shapes: you can put a
circle, a rectangle, and a triangle into one list and process them with one
loop that never asks which is which. That ability — one piece of code, many
underlying types, each behaving in its own way — is called **polymorphism**
(from Greek: "many shapes", fittingly), and it is the single most useful
idea in this chapter.

## One loop, many shapes

Here is the whole trick in one runnable example. Watch the loop at the
bottom: it calls `shape.area()` on every element, yet three *different*
`area` methods end up running.

```python
import math

class Shape:
    def describe(self):
        print(f"{type(self).__name__:<10} area = {self.area():7.2f}")

class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius

    def area(self):
        return math.pi * self.radius ** 2

class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height

class Triangle(Shape):
    def __init__(self, base, height):
        self.base = base
        self.height = height

    def area(self):
        return 0.5 * self.base * self.height

shapes = [Circle(1), Rectangle(3, 4), Triangle(6, 2), Circle(2.5)]

total = 0.0
for shape in shapes:              # one loop — no ifs, no type checks
    shape.describe()
    total += shape.area()

print(f"Total area: {total:.2f}")
```

The loop body is written against the *general* idea of a shape, but each
iteration produces the answer for the *specific* shape in hand. Adding a
brand-new `Hexagon` class tomorrow would require **zero changes** to this
loop — that is the property that makes large programs extensible.

## Dispatch happens per object, at runtime

How does one line of code run three different methods? When Python executes
`shape.area()`, it does *not* care what the variable was declared as (there
are no declarations); it looks at the object currently in `shape`, finds
that object's class, and searches that class (then its parents, in MRO
order) for `area`. The decision is made freshly on every call — this is
called **dynamic dispatch** or *runtime method resolution*. You can watch
the decision being made:

```python
# continues
for shape in shapes:
    chosen = type(shape).area          # the method dispatch will pick
    print(f"{type(shape).__name__:<10} -> runs {chosen.__qualname__}")
```

Same expression, four lookups, three different winners. Overriding plus
dynamic dispatch *is* polymorphism: the base class fixes the vocabulary
(`area`, `describe`), and each subclass supplies its own verse.

## The same list in Java: supertypes and casting

Java reaches the same destination, but its static type system makes you
declare the "general idea" explicitly. A `List<Shape>` may hold circles and
rectangles because each *is a* `Shape` — the conversion from `Circle` to
`Shape` (called **upcasting**) happens implicitly. Going the other way,
from the general type back down to a specific one (**downcasting**),
requires an explicit cast, and a wrong cast crashes:

=== "Python"

    ```python
    # continues
    mixed = [Circle(1), Rectangle(3, 4)]    # just a list — no declared type

    for item in mixed:
        print(item.area())                  # dispatch picks the right method

    first = mixed[0]
    print(first.radius)                     # fine: the object IS a Circle
    ```

=== "Java"

    ```java
    List<Shape> mixed = new ArrayList<>();
    mixed.add(new Circle(1));          // upcast Circle -> Shape: implicit
    mixed.add(new Rectangle(3, 4));

    for (Shape s : mixed) {
        System.out.println(s.area());  // dynamic dispatch, same as Python
    }

    Shape first = mixed.get(0);
    // first.radius;                   // compile error: Shape has no radius
    if (first instanceof Circle c) {   // check, then downcast (Java 17 style)
        System.out.println(c.radius);  // now the Circle-specific field works
    }
    ```

The `instanceof` guard exists because an unguarded downcast is a gamble.
If the element is actually a `Rectangle`, the program dies at runtime:

```text
Circle c = (Circle) mixed.get(1);     // but element 1 is a Rectangle...

Exception in thread "main" java.lang.ClassCastException:
    class Rectangle cannot be cast to class Circle
```

Python has no casts at all — a variable is just a name for an object, and
the object always knows its own class. The equivalent risk in Python is
simply calling a method or attribute the object doesn't have, which raises
`AttributeError` at the moment of use.

## Duck typing: Python's shortcut

Here is where Python quietly departs from Java. The polymorphic loop above
never actually *checks* that the elements inherit from `Shape` — it only
calls `.area()` on them. So any object with an `area` method can join the
party, related or not:

```python
# continues
class Pizza:                          # no inheritance — not a Shape at all
    def __init__(self, diameter):
        self.diameter = diameter

    def area(self):
        return math.pi * (self.diameter / 2) ** 2

menu = shapes + [Pizza(12)]
for item in menu:
    print(f"{type(item).__name__:<10} area = {item.area():7.2f}")
```

This style is called **duck typing**, after the saying "if it walks like a
duck and quacks like a duck, it's a duck": Python code cares about *what an
object can do*, not *what family it belongs to*. In Java this example is
impossible — `Pizza` could not enter a `List<Shape>` without declaring a
relationship to `Shape`. Duck typing makes Python nimble; the price is that
nothing checks the contract until the method is actually called.

## `isinstance`: smell or necessity?

Since any object always knows its class, Python offers
`isinstance(obj, SomeClass)` — the counterpart of Java's `instanceof`. Used
carelessly, it is a smell: a chain of type checks is polymorphism done by
hand, and it breaks the "add a class, change nothing" property:

```python
# continues
def clumsy_area(shape):               # anti-example: don't write this
    if isinstance(shape, Circle):
        return math.pi * shape.radius ** 2
    elif isinstance(shape, Rectangle):
        return shape.width * shape.height
    else:
        raise TypeError("unknown shape")   # Triangle? Pizza? Hexagon? crash.

print(f"{clumsy_area(Circle(1)):.2f}")
```

Every new shape forces an edit to `clumsy_area` — exactly the maintenance
trap the polymorphic loop avoided. The rule of thumb: **if you are choosing
behaviour based on type, push that behaviour into the classes as a method.**

`isinstance` does have honest jobs, though: validating inputs at a system
boundary ("this function requires a `Shape`; fail loudly and early
otherwise"), and handling genuinely different *kinds* of input, as in
`isinstance(x, str)` vs a list of strings. Checking to fail fast is fine;
checking to *branch on every subclass* is the smell.

## Everyday polymorphism: `__str__` and `__repr__`

You have been using polymorphism since your first `print`. When Python
prints an object, it calls the object's `__str__` method — and because
that is an ordinary method lookup, *your* classes can override it:

```python
class Fraction:
    def __init__(self, num, den):
        self.num = num
        self.den = den

    def __str__(self):                # what print() and str() show
        return f"{self.num}/{self.den}"

    def __repr__(self):               # what containers and debuggers show
        return f"Fraction({self.num}, {self.den})"

half = Fraction(1, 2)
print(half)                           # print uses __str__
print([half, Fraction(3, 4)])         # lists use each element's __repr__
```

`print` was written decades before your `Fraction` class existed, yet it
displays fractions perfectly — because it dispatches to whatever `__str__`
the object provides. Convention: `__str__` is for people (friendly),
`__repr__` is for programmers (unambiguous, ideally looks like the code to
recreate the object). If you define only `__repr__`, `print` falls back to
it, so when in doubt write `__repr__` first.

!!! warning "Common mistakes"

    - **Writing type-check chains instead of methods.** A ladder of
      `isinstance` tests that selects behaviour is hand-rolled dispatch;
      move each branch into the corresponding class as an override.
    - **Expecting the variable, not the object, to decide.** In Python the
      *object's* class picks the method — always. There is no Java-style
      "declared type" that could hide a subclass override.
    - **Forgetting that duck typing checks nothing early.** If one element
      of a list lacks the method your loop calls, the crash happens
      mid-loop at runtime, not when the list was built. Test with mixed
      lists.
    - **Defining `__str__` but expecting it inside containers.** Printing a
      list shows each element's `__repr__`, not `__str__` — define both
      (or just `__repr__`) to avoid `<__main__.Fraction object at 0x...>`
      surprises.

## Check your understanding

1. In the shapes loop, `shape.area()` appears once in the source code, yet
   different method bodies run. What single piece of information decides
   which body runs on each iteration?

    ??? success "Answer"

        The class of the object currently bound to `shape`. On each call,
        Python looks up `area` starting from `type(shape)` and walking the
        MRO — the decision is per object, at runtime (dynamic dispatch).

2. Why does the Java version need `List<Shape>` while Python's list needs
   no element type at all?

    ??? success "Answer"

        Java's compiler must be able to verify, before the program runs,
        that every element supports the methods the loop calls — so the
        elements need a common declared supertype. Python defers all
        checking to the moment each method is called, so the list can hold
        anything; objects lacking the method fail only when reached.

3. Is `isinstance` in this function a smell or a necessity?

    ```text
    def total_area(items):
        if not all(isinstance(x, Shape) for x in items):
            raise TypeError("total_area needs Shapes")
        return sum(x.area() for x in items)
    ```

    ??? success "Answer"

        A defensible necessity: it validates input once, at the boundary,
        to fail early with a clear message — it does not branch behaviour
        per subclass. (In idiomatic Python many would drop the check and
        rely on duck typing; both positions are respectable.)

4. `print(my_object)` shows `<__main__.Point object at 0x7f...>`. Which
   method should you add to fix this, and why does adding it work?

    ??? success "Answer"

        Add `__str__` (or `__repr__`, which `print` falls back to).
        `print` calls `str(obj)`, which dispatches to the object's own
        `__str__` — overriding it is ordinary polymorphism, so your
        version wins over the default inherited from `object`.
