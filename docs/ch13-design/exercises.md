# Exercises

Design skills grow by designing. The early exercises sharpen your
encapsulation instincts; the middle ones make you draw and read UML; the
last two extend the chapter's running systems. Attempt each one before
opening the solution — especially the prediction in Exercise 13.2.

### Exercise 13.1 — Find the encapsulation leak ●

This class checks every sticker on the way in, yet its invariant still
gets broken. Run it, explain *how* the empty name got in, and fix the
class so the attack fails.

```python
class StickerAlbum:
    """Invariant: no empty sticker names."""

    def __init__(self):
        self._stickers = []

    def add(self, sticker):
        if sticker != "":
            self._stickers.append(sticker)

    def get_stickers(self):
        return self._stickers

album = StickerAlbum()
album.add("comet")
album.add("")                        # blocked by the check — good
album.get_stickers().append("")      # and yet ...
print(album.get_stickers())
```

??? success "Solution"

    `get_stickers` returns the *actual internal list*, so the caller's
    `.append("")` edits the album's private data directly, bypassing
    `add` and its check. Return a copy instead:

    ```python
    class StickerAlbum:
        """Invariant: no empty sticker names."""

        def __init__(self):
            self._stickers = []

        def add(self, sticker):
            if sticker != "":
                self._stickers.append(sticker)

        def get_stickers(self):
            return list(self._stickers)   # a copy — internals stay safe

    album = StickerAlbum()
    album.add("comet")
    album.get_stickers().append("")       # mutates only the copy
    print(album.get_stickers())
    ```

    Now the output is `['comet']`. Encapsulation is only as strong as
    its weakest accessor: guarding writes is pointless if a getter hands
    out the mutable original.

### Exercise 13.2 — Predict the output ●

Without running it, write down the four lines this prints (or whether
any line raises an error). Then run it and check yourself.

```text
class Gadget:
    def __init__(self):
        self.model = "GX"
        self._battery = 50
        self.__pin = 1234

g = Gadget()
print(g.model)
print(g._battery)
print("_Gadget__pin" in vars(g))
print(g._Gadget__pin)
```

??? success "Solution"

    ```python
    class Gadget:
        def __init__(self):
            self.model = "GX"
            self._battery = 50
            self.__pin = 1234

    g = Gadget()
    print(g.model)
    print(g._battery)
    print("_Gadget__pin" in vars(g))
    print(g._Gadget__pin)
    ```

    It prints `GX`, `50`, `True`, `1234`. The single underscore is pure
    convention, so `g._battery` works; the double underscore is mangled
    to `_Gadget__pin`, which is why that name appears in `vars(g)` and
    why accessing it directly succeeds (only `g.__pin` would raise
    `AttributeError`).

### Exercise 13.3 — A guarded score ●●

Write a class `Exam` whose `score` property accepts only values from 0
to 100 inclusive and raises `ValueError` otherwise — including in the
constructor. Demonstrate that a valid update works and an invalid one is
rejected *without* corrupting the stored value.

??? success "Solution"

    ```python
    class Exam:
        def __init__(self, score):
            self.score = score            # runs the setter below

        @property
        def score(self):
            return self._score

        @score.setter
        def score(self, value):
            if not 0 <= value <= 100:
                raise ValueError(f"score must be 0-100, got {value}")
            self._score = value

    e = Exam(88)
    e.score = 95
    print(e.score)
    try:
        e.score = 130
    except ValueError as err:
        print("rejected:", err)
    print(e.score)                        # unchanged by the failed write
    ```

    Output: `95`, then `rejected: score must be 0-100, got 130`, then
    `95` again. Because `__init__` assigns through the property, even
    `Exam(999)` would be refused at birth.

### Exercise 13.4 — UML from a prose spec ●●

Draw a mermaid `classDiagram` for this specification, then write the
matching Python skeleton:

> A music app has playlists. A **playlist** has a name and creates its
> own **song entries** from a title and an artist; a song entry belongs
> to exactly one playlist. A **listener** has a display name and can
> follow many playlists, which exist independently of any listener.

??? success "Solution"

    The playlist *creates* its songs — composition. The listener follows
    playlists that live independently — aggregation.

    ```mermaid
    classDiagram
        class Playlist {
            +str name
            -List~Song~ _songs
            +add(title, artist) None
        }
        class Song {
            +str title
            +str artist
        }
        class Listener {
            +str display_name
            -List~Playlist~ _following
            +follow(playlist) None
        }
        Playlist "1" *-- "0..*" Song
        Listener "0..*" o-- "0..*" Playlist : follows
    ```

    ```python
    class Song:
        def __init__(self, title, artist):
            self.title = title
            self.artist = artist


    class Playlist:
        def __init__(self, name):
            self.name = name
            self._songs = []

        def add(self, title, artist):
            self._songs.append(Song(title, artist))   # built inside


    class Listener:
        def __init__(self, display_name):
            self.display_name = display_name
            self._following = []

        def follow(self, playlist):
            self._following.append(playlist)          # made elsewhere


    mix = Playlist("Focus Mix")
    mix.add("Rain Study", "Lo Anders")
    fan = Listener("night_owl")
    fan.follow(mix)
    print(f"{fan.display_name} follows '{mix.name}'")
    ```

    The code mirrors the arrows exactly: `Playlist.add` constructs
    `Song` objects itself (composition), while `Listener.follow` stores
    playlists handed in from outside (aggregation).

### Exercise 13.5 — From code to diagram ●●

Read this working code and draw its mermaid class diagram, choosing the
right arrow for each relationship.

```python
class Enclosure:
    def __init__(self, label):
        self.label = label

class Animal:
    def __init__(self, name, enclosure):
        self.name = name
        self.enclosure = enclosure       # a lasting reference

class Zoo:
    def __init__(self, name):
        self.name = name
        self._enclosures = [Enclosure("north wing"),
                            Enclosure("south wing")]
        self._animals = []

    def admit(self, animal):
        self._animals.append(animal)

zoo = Zoo("Hillside Zoo")
rex = Animal("Rex", zoo._enclosures[0])
zoo.admit(rex)
print(f"{rex.name} lives in the {rex.enclosure.label}")
```

??? success "Solution"

    ```mermaid
    classDiagram
        class Zoo {
            +str name
            -List~Enclosure~ _enclosures
            -List~Animal~ _animals
            +admit(animal) None
        }
        class Animal {
            +str name
            +Enclosure enclosure
        }
        class Enclosure {
            +str label
        }
        Zoo "1" *-- "2" Enclosure
        Zoo "1" o-- "0..*" Animal : admits
        Animal --> Enclosure : lives in
    ```

    ```python
    class Enclosure:
        def __init__(self, label):
            self.label = label

    class Animal:
        def __init__(self, name, enclosure):
            self.name = name
            self.enclosure = enclosure

    class Zoo:
        def __init__(self, name):
            self.name = name
            self._enclosures = [Enclosure("north wing"),
                                Enclosure("south wing")]
            self._animals = []

        def admit(self, animal):
            self._animals.append(animal)

    zoo = Zoo("Hillside Zoo")
    print("Zoo *-- Enclosure: built in __init__, owned outright")
    print("Zoo o-- Animal: admitted from outside, lives independently")
    print("Animal --> Enclosure: a lasting peer reference")
    ```

    The giveaways: `Zoo` constructs its enclosures itself (composition),
    `admit` stores animals created elsewhere (aggregation), and each
    animal keeps a plain reference to its enclosure (association). As a
    bonus, notice the scenario reaching into `zoo._enclosures[0]` — a
    politeness violation this chapter taught you to spot; a `Zoo` method
    for assigning enclosures would be cleaner.

### Exercise 13.6 — A read-only derived property ●●

Write a `Circle` class where `radius` must be positive (`ValueError`
otherwise) and `area` is a **read-only** property computed from the
radius. Show that changing the radius changes the area, and that
assigning to `area` fails.

??? success "Solution"

    ```python
    import math

    class Circle:
        def __init__(self, radius):
            self.radius = radius

        @property
        def radius(self):
            return self._radius

        @radius.setter
        def radius(self, value):
            if value <= 0:
                raise ValueError("radius must be positive")
            self._radius = value

        @property
        def area(self):                   # no setter: read-only
            return math.pi * self._radius ** 2

    c = Circle(2)
    print(f"{c.area:.2f}")
    c.radius = 3
    print(f"{c.area:.2f}")
    try:
        c.area = 100
    except AttributeError:
        print("area is read-only")
    ```

    Output: `12.57`, `28.27`, `area is read-only`. Because `area` is
    computed on every read, it can never disagree with the radius —
    a stored `area` attribute could.

### Exercise 13.7 — Add a waitlist to the airline ●●●

Extend the airline system from
[13.3](03-multi-class.md): when a passenger asks for a seat that is
taken, add them to a first-come-first-served **waitlist** instead of
just refusing. When any reservation is cancelled, the freed seat should
go automatically to the first waitlisted passenger, and `cancel` should
return that new reservation (or `None` if nobody was waiting).

??? success "Solution"

    ```python
    class Seat:
        def __init__(self, number):
            self.number = number
            self.occupant = None

        def is_free(self):
            return self.occupant is None


    class Passenger:
        def __init__(self, name):
            self.name = name


    class Reservation:
        def __init__(self, passenger, seat, flight_number):
            self.passenger = passenger
            self.seat = seat
            self.flight_number = flight_number

        def __str__(self):
            return (f"{self.passenger.name} -> seat {self.seat.number} "
                    f"on {self.flight_number}")


    class Flight:
        ROWS = (1,)
        LETTERS = ("A", "B")              # tiny flight: fills up fast

        def __init__(self, number):
            self.number = number
            self._seats = [Seat(f"{r}{l}")
                           for r in self.ROWS for l in self.LETTERS]
            self._waitlist = []           # Passengers, in arrival order

        def find_seat(self, seat_number):
            for seat in self._seats:
                if seat.number == seat_number:
                    return seat
            return None

        def book(self, passenger, seat_number):
            seat = self.find_seat(seat_number)
            if seat is None:
                return None
            if not seat.is_free():
                self._waitlist.append(passenger)
                return None
            seat.occupant = passenger
            return Reservation(passenger, seat, self.number)

        def cancel(self, reservation):
            seat = reservation.seat
            seat.occupant = None
            if self._waitlist:
                next_up = self._waitlist.pop(0)     # first in line
                return self.book(next_up, seat.number)
            return None


    flight = Flight("NW222")
    ada = Passenger("Ada Lam")
    ben = Passenger("Ben Osei")

    res_ada = flight.book(ada, "1A")
    print(f"Booked: {res_ada}")
    print(f"Ben tries 1A: {flight.book(ben, '1A')}")   # waitlisted
    promoted = flight.cancel(res_ada)
    print(f"Promoted from waitlist: {promoted}")
    ```

    Output:

    ```text
    Booked: Ada Lam -> seat 1A on NW222
    Ben tries 1A: None
    Promoted from waitlist: Ben Osei -> seat 1A on NW222
    ```

    The elegant part: `cancel` promotes the waitlisted passenger by
    calling the *existing* `book` method, so the claiming rule still
    lives in exactly one place.

### Exercise 13.8 — Implement `Library.check_out` ●●●

The [Library skeleton in 13.2](02-uml.md) left `check_out(isbn,
member_id)` returning `False` unconditionally. Implement it: find the
book and the member, refuse if either is missing or the book is out,
otherwise mark the book checked out, add it to the member's borrowed
list, and return `True`. Keep the underscore rule: `Library` should not
poke `_checked_out` or `_borrowed` directly — give `Book` and `Member`
small methods instead.

??? success "Solution"

    ```python
    class Book:
        def __init__(self, title, isbn):
            self.title = title
            self.isbn = isbn
            self._checked_out = False

        def is_available(self):
            return not self._checked_out

        def mark_checked_out(self):
            self._checked_out = True


    class Member:
        def __init__(self, name, member_id):
            self.name = name
            self.member_id = member_id
            self._borrowed = []

        def take(self, book):
            self._borrowed.append(book)


    class Library:
        def __init__(self, name):
            self.name = name
            self._books = []
            self._members = []

        def add_book(self, book):
            self._books.append(book)

        def register(self, member):
            self._members.append(member)

        def check_out(self, isbn, member_id):
            book = None
            for b in self._books:
                if b.isbn == isbn:
                    book = b
            member = None
            for m in self._members:
                if m.member_id == member_id:
                    member = m
            if book is None or member is None or not book.is_available():
                return False
            book.mark_checked_out()      # Book changes its own state
            member.take(book)            # Member changes its own state
            return True


    lib = Library("Riverside Branch")
    novel = Book("A Tour of the Machine", "978-1-0000-0001-1")
    lib.add_book(novel)
    lib.register(Member("Sam Ortiz", 4021))

    print(lib.check_out("978-1-0000-0001-1", 4021))   # True
    print(lib.check_out("978-1-0000-0001-1", 4021))   # already out
    print(novel.is_available())
    ```

    Output: `True`, `False`, `False`. The library *coordinates* the
    transaction, but each object mutates only its own private state —
    the same ownership discipline as `Flight.book` in 13.3.
