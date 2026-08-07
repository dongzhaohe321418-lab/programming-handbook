# C · Glossary

Every term this handbook expects you to know, defined the way this handbook
uses it. Each entry links to the chapter that teaches the idea properly —
the definition is the reminder, the chapter is the lesson.

## A

**abstract data type (ADT)**
:   A contract describing *what* a collection can do — its operations and
    their rules — with no commitment to *how*. "A stack offers push and
    pop, last-in-first-out" is an ADT; an array is one way to build it.
    See [Chapter 18.1](../ch18-linked-lists/01-adts-generics.md).

**algorithm**
:   A precise, finite recipe for solving a problem — defined independently
    of any programming language. See
    [Chapter 8.3](../ch08-grids/03-first-algorithms.md).

**aliasing**
:   Two or more names referring to the *same* object, so a change through
    one name is visible through all of them. The classic source of
    "spooky action at a distance" bugs. See
    [Chapter 9.1](../ch09-collections/01-references.md).

**amortized cost**
:   The cost of an operation averaged over a long run of operations.
    `list.append` is occasionally $O(n)$ (a resize) but amortized $O(1)$.
    See [Chapter 9.2](../ch09-collections/02-dynamic-lists.md).

**argument**
:   The actual value you pass to a function when calling it — the filling
    for a *parameter*. In `area(3, 4)`, the arguments are `3` and `4`.
    See [Chapter 3.3](../ch03-functions/03-writing-functions.md).

**array**
:   A fixed-size block of same-typed elements sitting side by side in
    memory, giving $O(1)$ access by index. Java's `int[]` is one; Python's
    `list` is its more flexible cousin. See
    [Chapter 7.1](../ch07-arrays/01-arrays-vs-lists.md).

**assignment**
:   Binding a name to a value: `x = 7`. In this book's mental model,
    assignment attaches a label to an object — it never copies the object.
    See [Chapter 2.1](../ch02-data/01-variables-types.md).

**attribute**
:   A variable that lives inside an object, reached with a dot:
    `dog.name`. Java calls these *fields* or *instance variables*.
    See [Chapter 12.1](../ch12-classes/01-class-anatomy.md).

## B

**base case**
:   The input a recursive function handles *without* calling itself — the
    floor that stops the recursion from falling forever. See
    [Chapter 17.2](../ch17-recursion/02-classic-recursion.md).

**big-O notation**
:   The standard way to describe how an algorithm's cost grows with input
    size, ignoring constants: $O(n)$, $O(n \log n)$, $O(n^2)$. See
    [Chapter 16.1](../ch16-complexity/01-big-o.md) and
    [Appendix B](B-big-o.md).

**binary**
:   Base-2 numbering, using only 0 and 1 — the native tongue of hardware,
    because a wire is either on or off. See
    [Chapter 0.2](../ch00-machine/02-binary.md).

**binary search**
:   Finding a value in *sorted* data by repeatedly halving the candidates:
    $O(\log n)$. See [Chapter 22.3](../ch22-sorting/03-searching.md).

**binary search tree (BST)**
:   A binary tree obeying one invariant everywhere: left subtree smaller,
    right subtree larger. Search follows one root-to-leaf path. See
    [Chapter 20](../ch20-bst/index.md).

**bit**
:   One binary digit — a single 0 or 1, the smallest unit of information.
    Eight of them make a byte. See
    [Chapter 0.2](../ch00-machine/02-binary.md).

**Boolean**
:   A value that is exactly `True` or `False`; the answer type of every
    comparison and the fuel of every `if`. See
    [Chapter 4.1](../ch04-branching/01-booleans-logic.md).

**bytecode**
:   The compact instruction set a language's *virtual machine* executes —
    what Python compiles your `.py` into behind the scenes, and what
    `javac` puts in `.class` files. See
    [Chapter 0.3](../ch00-machine/03-programs.md) and
    [Chapter 23.3](../ch23-os/03-interpreters-vms.md).

## C

**call stack**
:   The runtime's stack of *frames*, one per function call in progress;
    calling pushes a frame, returning pops it. Recursion is this stack
    doing the bookkeeping for you. See
    [Chapter 17.1](../ch17-recursion/01-call-stack.md).

**class**
:   A blueprint for objects: it declares the attributes each instance
    carries and the methods it can perform. See
    [Chapter 12.1](../ch12-classes/01-class-anatomy.md).

**collision**
:   In a hash table, two different keys landing in the same bucket.
    Inevitable by the pigeonhole principle; handled by chaining or
    probing. See [Chapter 25.1](../ch25-next/01-cs400-preview.md).

**command line**
:   The text interface where you type commands to the operating system —
    where `python`, `git`, and your own CLI programs run. See
    [Chapter 1.1](../ch01-tools/01-command-line.md).

**compiler**
:   A translator that converts a whole program into another form (machine
    code or bytecode) *before* it runs, reporting errors up front. See
    [Chapter 0.3](../ch00-machine/03-programs.md).

**composition**
:   Building a class *out of* other objects ("a `Library` has `Book`s")
    rather than inheriting from them ("is a"). Usually the safer design.
    See [Chapter 13.3](../ch13-design/03-multi-class.md).

**constructor**
:   The special routine that runs when an object is created — Python's
    `__init__`, Java's `ClassName(...)` — responsible for putting the new
    object into a valid starting state. See
    [Chapter 12.1](../ch12-classes/01-class-anatomy.md).

**CPU**
:   The central processing unit: the chip that fetches, decodes, and
    executes instructions, billions of times per second. See
    [Chapter 0.1](../ch00-machine/01-hardware.md).

## D

**data structure**
:   A concrete arrangement of data in memory plus the algorithms that
    maintain it — arrays, linked lists, trees, heaps, hash tables. Part
    III of this book, in one word.

**dictionary**
:   Python's built-in key → value mapping (`dict`), implemented as a hash
    table; Java's counterpart is `HashMap`. See
    [Chapter 14.1](../ch14-beyond/01-collections-tour.md).

**dispatch (dynamic)**
:   Choosing *which* method body runs based on the actual class of the
    object at runtime — the machinery behind polymorphism. See
    [Chapter 15.2](../ch15-inheritance/02-polymorphism.md).

**divide and conquer**
:   Solving a problem by splitting it into smaller copies of itself,
    solving those (often recursively), and combining the results — the
    strategy behind merge sort and quicksort. See
    [Chapter 22.2](../ch22-sorting/02-merge-quick.md).

## E

**encapsulation**
:   Hiding an object's internal data behind a public set of methods, so
    the object controls its own state and can protect its invariants. See
    [Chapter 13.1](../ch13-design/01-encapsulation.md).

**exception**
:   An object representing a runtime error, *thrown* at the point of
    failure and *caught* (or not) somewhere up the call stack. See
    [Chapter 10.2](../ch10-exceptions/02-exceptions.md).

**expression**
:   Any piece of code that evaluates to a value: `2 + 3`, `len(name)`,
    `x > 0`. Statements *do*; expressions *are*. See
    [Chapter 2](../ch02-data/index.md).

## F

**floating point**
:   The binary format (`float`/`double`) computers use for real numbers —
    fast, compact, and slightly *approximate*, which is why
    `0.1 + 0.2 != 0.3`. See
    [Chapter 5.1](../ch05-under-the-hood/01-numeric-pitfalls.md).

**frame**
:   One entry on the call stack, holding a single function call's local
    variables and its bookmark for where to resume. See
    [Chapter 17.1](../ch17-recursion/01-call-stack.md).

**function**
:   A named, reusable block of code that takes parameters and (usually)
    returns a value. Inside a class it is called a method. See
    [Chapter 3.3](../ch03-functions/03-writing-functions.md).

## G

**garbage collection**
:   The runtime's automatic reclamation of memory whose objects can no
    longer be reached by any reference — the reason Python and Java have
    no `free()`. See
    [Chapter 9.3](../ch09-collections/03-objects-in-memory.md).

**generics**
:   Writing one class or method that works for many element types —
    Java's `ArrayList<String>` — with the compiler checking consistency.
    Python gets the same flexibility via dynamic typing plus optional
    hints like `list[str]`. See
    [Chapter 18.1](../ch18-linked-lists/01-adts-generics.md).

**graph**
:   A set of nodes plus a set of edges connecting pairs of them — the
    universal shape of networks: friendships, roads, links, dependencies.
    See [Chapter 25.1](../ch25-next/01-cs400-preview.md).

## H

**hash function**
:   A function that turns a key of any size into a fixed-size number,
    deterministically; combined with modulo it picks a hash-table bucket.
    See [Chapter 25.1](../ch25-next/01-cs400-preview.md).

**hash table**
:   The structure behind `dict`, `set`, `HashMap`, `HashSet`: hash the
    key, jump straight to a bucket, average $O(1)$ lookup. See
    [Chapter 14.1](../ch14-beyond/01-collections-tour.md) and
    [Chapter 25.1](../ch25-next/01-cs400-preview.md).

**heap (data structure)**
:   A complete binary tree where every parent outranks its children,
    giving $O(1)$ access to the minimum (or maximum) and $O(\log n)$
    insert/remove — the engine of priority queues. *Unrelated to the
    memory heap below; the name collision is historical accident.* See
    [Chapter 21.1](../ch21-heaps/01-heap-property.md).

**heap (memory region)**
:   The area of a process's memory where objects live, managed by the
    allocator and the garbage collector — as opposed to the stack, which
    holds call frames. *Not* the tree structure above. See
    [Chapter 5.3](../ch05-under-the-hood/03-stack-heap.md).

## I

**identity**
:   Whether two names refer to the *same object* (`is`, `id()`), as
    opposed to equal values (`==`). See
    [Chapter 4.3](../ch04-branching/03-equality-identity.md).

**immutability**
:   The property of objects that cannot be changed after creation —
    Python's `str`, `int`, and `tuple`. "Modifying" one actually builds a
    new object. See [Chapter 3.2](../ch03-functions/02-strings.md).

**inheritance**
:   Defining a class as a specialised version of another ("a `Puppy` *is
    a* `Dog`"), receiving its attributes and methods and overriding some.
    See [Chapter 15.1](../ch15-inheritance/01-inheritance.md).

**instance**
:   One concrete object built from a class: `Dog("Rex")` creates an
    instance of `Dog`. See
    [Chapter 12.1](../ch12-classes/01-class-anatomy.md).

**instance variable**
:   An attribute owned by one particular instance — each `Dog` has its
    own `name`. Java declares them as fields; Python creates them in
    `__init__`. See [Chapter 12.1](../ch12-classes/01-class-anatomy.md).

**interface**
:   A pure contract — method signatures with no implementation — that a
    class promises to fulfil (`implements Comparable`). Java's tool for
    "same abilities, unrelated families". See
    [Chapter 15.3](../ch15-inheritance/03-interfaces.md).

**interpreter**
:   A program that reads and executes your code directly, statement by
    statement, instead of translating it all in advance. CPython is one
    (with a compile-to-bytecode step inside). See
    [Chapter 0.3](../ch00-machine/03-programs.md) and
    [Chapter 23.3](../ch23-os/03-interpreters-vms.md).

**invariant**
:   A condition that must hold before and after every operation on a
    structure — the BST's "left smaller, right larger", the heap's
    "parent outranks children". Correctness arguments are invariant
    arguments. See [Chapter 20.2](../ch20-bst/02-bst-ops.md).

**iterator**
:   An object that hands out a sequence's elements one at a time on
    demand — the machinery under every `for x in xs`. See
    [Chapter 19.1](../ch19-stacks-queues/01-iterators.md).

## J

**JIT compiler**
:   A *just-in-time* compiler: a virtual machine component that watches
    running bytecode and compiles the hot parts to machine code on the
    fly — a big reason the JVM is fast. See
    [Chapter 23.3](../ch23-os/03-interpreters-vms.md).

## L

**linked list**
:   A chain of nodes, each holding a value and a reference to the next —
    $O(1)$ insertion at the ends you track, $O(n)$ access by position.
    See [Chapter 18.2](../ch18-linked-lists/02-singly-linked.md).

**list**
:   Python's built-in growable sequence, implemented as a dynamic array —
    despite the name, it is *not* a linked list. See
    [Chapter 7.1](../ch07-arrays/01-arrays-vs-lists.md).

**loop**
:   A statement that repeats a block: `while` repeats while a condition
    holds, `for` walks a sequence. See [Chapter 6](../ch06-loops/index.md).

## M

**method**
:   A function that belongs to an object and is called through it:
    `name.upper()`, `dog.bark()`. See
    [Chapter 3.1](../ch03-functions/01-using-objects.md).

**modulo**
:   The remainder operator `%`: `17 % 5` is `2`. The workhorse of
    even/odd tests, wrap-around counters, and hash-bucket selection. See
    [Chapter 2.3](../ch02-data/03-operators.md).

**mutation**
:   Changing an object in place (`xs.append(4)`) rather than rebinding a
    name to a new object — visible through every alias of that object.
    See [Chapter 9.1](../ch09-collections/01-references.md).

## N

**namespace**
:   A mapping from names to objects — each module, function call, and
    class gets its own, which is why the same name can mean different
    things in different places. See
    [Chapter 5.4](../ch05-under-the-hood/04-overloading-imports.md).

**None**
:   Python's "no value here" object (Java: `null`) — the default return
    of a function without `return`, and the standard sign of "not found".
    Test for it with `is None`. See
    [Chapter 4.3](../ch04-branching/03-equality-identity.md).

## O

**object**
:   A bundle of data (attributes) plus the operations that belong to it
    (methods), living on the heap and reached through references. See
    [Chapter 3.1](../ch03-functions/01-using-objects.md) and
    [Chapter 9.3](../ch09-collections/03-objects-in-memory.md).

**overflow**
:   What happens when a fixed-width number exceeds its range and wraps
    around — a real hazard for Java's 32-bit `int`, impossible for
    Python's unlimited integers. See
    [Chapter 5.1](../ch05-under-the-hood/01-numeric-pitfalls.md).

**overloading**
:   One method name with several parameter lists, chosen by argument
    types at compile time — a Java feature Python replaces with default
    arguments. See
    [Chapter 5.4](../ch05-under-the-hood/04-overloading-imports.md).

**overriding**
:   A subclass redefining a method it inherited, so its own version runs
    instead — the partner mechanism of dynamic dispatch. See
    [Chapter 15.1](../ch15-inheritance/01-inheritance.md).

## P

**parameter**
:   A named slot in a function definition that receives an argument at
    call time — in `def area(w, h):`, the parameters are `w` and `h`.
    See [Chapter 3.3](../ch03-functions/03-writing-functions.md).

**polymorphism**
:   Code written against a general type doing the right specific thing
    for each actual object — one `animal.speak()` call, many behaviours.
    See [Chapter 15.2](../ch15-inheritance/02-polymorphism.md).

**priority queue**
:   An ADT where you always remove the *most important* item rather than
    the oldest — almost always implemented with a binary heap. See
    [Chapter 21.2](../ch21-heaps/02-priority-queues.md).

**process**
:   One running program as the operating system sees it: its own memory
    space, its own resources, scheduled on and off the CPU. See
    [Chapter 23.1](../ch23-os/01-os-processes.md).

## Q

**queue**
:   First-in, first-out: enqueue at the back, dequeue from the front —
    the fair waiting line, and the engine of breadth-first search. See
    [Chapter 19.3](../ch19-stacks-queues/03-queues.md).

## R

**recursion**
:   A function solving a problem by calling itself on smaller inputs,
    down to a base case. See [Chapter 17](../ch17-recursion/index.md).

**reference**
:   The "arrow" a variable actually holds: not the object itself but
    where to find it. Copying a variable copies the arrow, not the
    object. See [Chapter 9.1](../ch09-collections/01-references.md).

**return value**
:   The result a function hands back to its caller via `return`; a
    Python function without one returns `None`. See
    [Chapter 3.3](../ch03-functions/03-writing-functions.md).

**rotation**
:   A constant-time re-wiring of a parent–child link in a BST that
    reduces height while preserving the ordering invariant — the repair
    move of AVL and red-black trees. See
    [Chapter 25.1](../ch25-next/01-cs400-preview.md).

## S

**scope**
:   The region of code where a name is visible — a variable created
    inside a function exists only there. See
    [Chapter 3.3](../ch03-functions/03-writing-functions.md).

**sentinel**
:   A special value marking a boundary, such as "stop when the input is
    `-1`" or `None` marking the end of a linked list. See
    [Chapter 6.1](../ch06-loops/01-while.md).

**short-circuit evaluation**
:   `and`/`or` (Java `&&`/`||`) skipping the right side once the left
    side settles the answer — and why
    `x != 0 and 10 / x > 1` is safe written in that order. See
    [Chapter 5.2](../ch05-under-the-hood/02-shortcuts-gotchas.md).

**stability (of a sort)**
:   A sorting algorithm is stable if items that compare equal keep their
    original relative order — crucial when sorting already-sorted data by
    a second key. See
    [Chapter 22.1](../ch22-sorting/01-elementary-sorts.md).

**stack (data structure)**
:   Last-in, first-out: push and pop at one end only — undo histories,
    matched brackets, and the call stack's namesake. See
    [Chapter 19.2](../ch19-stacks-queues/02-stacks.md).

**stack trace**
:   The report printed when an exception goes uncaught: the chain of
    calls that led to the failure. Python prints the failure point
    *last*; Java prints it first. See
    [Chapter 10.3](../ch10-exceptions/03-stack-traces.md).

**string**
:   An immutable sequence of characters — `str` in Python, `String` in
    Java. See [Chapter 3.2](../ch03-functions/02-strings.md).

## T

**traversal**
:   Visiting every element of a structure exactly once — walking a list
    front to back, or a tree in pre-, in-, or post-order. See
    [Chapter 20.3](../ch20-bst/03-traversals-balance.md).

**truthiness**
:   Python's willingness to treat any value as a Boolean: empty
    containers, `0`, `""`, and `None` count as false; nearly everything
    else counts as true. See
    [Chapter 4.1](../ch04-branching/01-booleans-logic.md).

**two's complement**
:   The standard binary encoding of negative integers, chosen so that
    ordinary addition circuitry works for signed numbers too. See
    [Chapter 2.2](../ch02-data/02-number-systems.md).

**type**
:   The classification that determines what a value is and what you can
    do with it: `int`, `str`, `bool`, `Dog`. Python checks types at run
    time; Java at compile time. See
    [Chapter 2.1](../ch02-data/01-variables-types.md).

## U

**UML class diagram**
:   The standard boxes-and-arrows notation for sketching classes, their
    members, and their relationships before writing code. See
    [Chapter 13.2](../ch13-design/02-uml.md).

**unit test**
:   A small automated check that one piece of code behaves as specified —
    written once, run forever after every change. See
    [Chapter 8.4](../ch08-grids/04-unit-testing.md) and
    [Chapter 24.2](../ch24-practice/02-testing.md).

## V

**variable**
:   A name bound to a value. In Python, a label attached to an object; in
    Java, a typed box holding a primitive or a reference. See
    [Chapter 2.1](../ch02-data/01-variables-types.md).

**virtual machine**
:   A program that pretends to be a CPU for some bytecode — the JVM for
    Java, CPython's inner loop for Python — buying portability at the
    cost of a translation layer. See
    [Chapter 23.3](../ch23-os/03-interpreters-vms.md).
