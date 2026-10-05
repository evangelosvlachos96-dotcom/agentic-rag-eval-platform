# PEP evaluation pilot: accepted source packet

24 assistant-authored questions, four per category, accepted by the project owner.
The accepted labels are frozen in `eval_sets/v1` at version `1f48f2e04ef7`.
This is a small pilot, not an independently annotated benchmark. Zero Anthropic API calls.
Corpus: python/peps@94a7775f23fd6eb7c527cf8180dab4542c5da622; dataset: 27b46e65f45d.

Review answer accuracy, all supporting sources, question category and ambiguity.
Unanswerable examples are easy out-of-domain cases; add harder near-misses later.
Multi-hop drafts follow a PEP reference to a fact in the referenced document.
Verify both steps; multiple labels alone do not prove difficulty.
Use only this pinned corpus. Accept equivalent wording, not only exact answer strings.
For each item, accept, edit or reject via `rag eval review`.

## pilot-001 / exact_term

Does PEP 484 require Python to enforce type hints at runtime?

**Draft answer:** No. PEP 484 does not require runtime type checking.

[PEP 484: Abstract](https://github.com/python/peps/blob/94a7775f23fd6eb7c527cf8180dab4542c5da622/peps/pep-0484.rst)

### Type Hints > Abstract

```text
:pep:`3107` introduced syntax for function annotations, but the semantics
were deliberately left undefined.  There has now been enough 3rd party
usage for static type analysis that the community would benefit from
a standard vocabulary and baseline tools within the standard library.

This PEP introduces a provisional module to provide these standard
definitions and tools, along with some conventions for situations
where annotations are not available.

Note that this PEP still explicitly does NOT prevent other uses of
annotations, nor does it require (or forbid) any particular processing
of annotations, even when they conform to this specification.  It
simply enables better coordination, as :pep:`333` did for web frameworks.

For example, here is a simple function whose argument and return type
are declared in the annotations::

  def greeting(name: str) -> str:
      return 'Hello ' + name

While these annotations are available at runtime through the usual
``__annotations__`` attribute, *no type checking happens at runtime*.
Instead, the proposal assumes the existence of a separate off-line
type checker which users can run over their source code voluntarily.
Essentially, such a type checker acts as a very powerful linter.
(While it would of course be possible for individual users to employ
a similar checker at run time for Design By Contract enforcement or
JIT optimization, those tools are not yet as mature.)
```

### Type Hints > Abstract

```text
The proposal is strongly inspired by `mypy <mypy_>`_.  For example, the
type "sequence of integers" can be written as ``Sequence[int]``.  The
square brackets mean that no new syntax needs to be added to the
language.  The example here uses a custom type ``Sequence``, imported
from a pure-Python module ``typing``.  The ``Sequence[int]`` notation
works at runtime by implementing ``__getitem__()`` in the metaclass
(but its significance is primarily to an offline type checker).

The type system supports unions, generic types, and a special type
named ``Any`` which is consistent with (i.e. assignable to and from) all
types.  This latter feature is taken from the idea of gradual typing.
Gradual typing and the full type system are explained in :pep:`483`.

Other approaches from which we have borrowed or to which ours can be
compared and contrasted are described in :pep:`482`.
```

## pilot-002 / exact_term

According to PEP 604, what does X | Y mean in a type annotation?

**Draft answer:** A union type, equivalent to Union[X, Y].

[PEP 604: Abstract](https://github.com/python/peps/blob/94a7775f23fd6eb7c527cf8180dab4542c5da622/peps/pep-0604.rst)

### Allow writing union types as ``X | Y`` > Abstract

```text
This PEP proposes overloading the ``|`` operator on types to allow
writing ``Union[X, Y]`` as ``X | Y``, and allows it to appear in
``isinstance`` and ``issubclass`` calls.
```

## pilot-003 / exact_term

According to PEP 655, what do Required[] and NotRequired[] mean for a TypedDict key?

**Draft answer:** Required[] means the key must be present; NotRequired[] means it may be absent.

[PEP 655: Abstract](https://github.com/python/peps/blob/94a7775f23fd6eb7c527cf8180dab4542c5da622/peps/pep-0655.rst)

### Marking individual TypedDict items as required or potentially-missing > Abstract

```text
:pep:`589` defines notation
for declaring a TypedDict with all required keys and notation for defining
a TypedDict with :pep:`all potentially-missing keys <589#totality>`, however it
does not provide a mechanism to declare some keys as required and others
as potentially-missing. This PEP introduces two new notations:
``Required[]``, which can be used on individual items of a
TypedDict to mark them as required, and
``NotRequired[]``, which can be used on individual items
to mark them as potentially-missing.

This PEP makes no Python grammar changes. Correct usage
of required and potentially-missing keys of TypedDicts is intended to be
enforced only by static type checkers and need not be enforced by
Python itself at runtime.
```

## pilot-004 / exact_term

What syntax does PEP 572 introduce for assigning a value within an expression?

**Draft answer:** NAME := expr.

[PEP 572: Abstract](https://github.com/python/peps/blob/94a7775f23fd6eb7c527cf8180dab4542c5da622/peps/pep-0572.rst)

### Assignment Expressions > Abstract

```text
This is a proposal for creating a way to assign to variables within an
expression using the notation ``NAME := expr``.

As part of this change, there is also an update to dictionary comprehension
evaluation order to ensure key expressions are executed before value
expressions (allowing the key to be bound to a name and then re-used as part of
calculating the corresponding value).

During discussion of this PEP, the operator became informally known as
"the walrus operator". The construct's formal name is "Assignment Expressions"
(as per the PEP title), but they may also be referred to as "Named Expressions"
(e.g. the CPython reference implementation uses that name internally).
```

## pilot-005 / lookup

What file extension and archive format does a Python wheel use?

**Draft answer:** The .whl extension and ZIP archive format.

[PEP 427: Abstract](https://github.com/python/peps/blob/94a7775f23fd6eb7c527cf8180dab4542c5da622/peps/pep-0427.rst)

### The Wheel Binary Package Format 1.0 > Abstract

```text
This PEP describes a built-package format for Python called "wheel".

A wheel is a ZIP-format archive with a specially formatted file name and
the ``.whl`` extension.  It contains a single distribution nearly as it
would be installed according to :pep:`376` with a particular installation
scheme.  Although a specialized installer is recommended, a wheel file
may be installed by simply unpacking into site-packages with the standard
'unzip' tool while preserving enough information to spread its contents
out onto their final paths at any later time.
```

## pilot-006 / lookup

Which methods form the context-manager protocol described by PEP 343?

**Draft answer:** The methods __enter__() and __exit__().

[PEP 343: Abstract](https://github.com/python/peps/blob/94a7775f23fd6eb7c527cf8180dab4542c5da622/peps/pep-0343.rst)

### The "with" Statement > Abstract

```text
This PEP adds a new statement "with" to the Python language to make
it possible to factor out standard uses of ``try/finally`` statements.

In this PEP, context managers provide ``__enter__()`` and ``__exit__()``
methods that are invoked on entry to and exit from the body of the
with statement.
```

## pilot-007 / lookup

Which file does PEP 621 use for project core metadata?

**Draft answer:** pyproject.toml.

[PEP 621: Abstract](https://github.com/python/peps/blob/94a7775f23fd6eb7c527cf8180dab4542c5da622/peps/pep-0621.rst)

### Storing project metadata in pyproject.toml > Abstract

```text
This PEP specifies how to write a project's `core metadata`_ in a
``pyproject.toml`` file for packaging-related tools to consume.
```

## pilot-008 / lookup

Which asynchronous expression forms does PEP 530 add?

**Draft answer:** List, set and dict comprehensions, and generator expressions.

[PEP 530: Abstract](https://github.com/python/peps/blob/94a7775f23fd6eb7c527cf8180dab4542c5da622/peps/pep-0530.rst)

### Asynchronous Comprehensions > Abstract

```text
:pep:`492` and :pep:`525` introduce support for native coroutines and
asynchronous generators using ``async`` / ``await`` syntax.  This PEP
proposes to add asynchronous versions of list, set, dict comprehensions
and generator expressions.
```

## pilot-009 / conceptual

Why does PEP 526 favor annotation syntax over type comments for parsing?

**Draft answer:** Its rationale says annotation syntax can be parsed with ast, while type comments require a custom parser.

[PEP 526: Rationale](https://github.com/python/peps/blob/94a7775f23fd6eb7c527cf8180dab4542c5da622/peps/pep-0526.rst)

### Syntax for Variable Annotations > Rationale

```text
Although type comments work well enough, the fact that they're
expressed through comments has some downsides:

- Text editors often highlight comments differently from type annotations.

- There's no way to annotate the type of an undefined variable; one needs to
  initialize it to ``None`` (e.g. ``a = None # type: int``).

- Variables annotated in a conditional branch are difficult to read::

    if some_value:
        my_var = function() # type: Logger
    else:
        my_var = another_function() # Why isn't there a type here?

- Since type comments aren't actually part of the language, if a Python script
  wants to parse them, it requires a custom parser instead of just using
  ``ast``.

- Type comments are used a lot in typeshed. Migrating typeshed to use
  the variable annotation syntax instead of type comments would improve
  readability of stubs.

- In situations where normal comments and type comments are used together, it is
  difficult to distinguish them::

    path = None  # type: Optional[str]  # Path to module source

- It's impossible to retrieve the annotations at runtime outside of
  attempting to find the module's source code and parse it at runtime,
  which is inelegant, to say the least.

The majority of these issues can be alleviated by making the syntax
a core part of the language. Moreover, having a dedicated annotation syntax
for class and instance variables (in addition to method annotations) will
pave the way to static duck-typing as a complement to nominal typing defined
by :pep:`484`.
```

## pilot-010 / conceptual

Why does PEP 621 require dynamic metadata to be declared explicitly?

**Draft answer:** To distinguish metadata that will be supplied later from metadata that is simply missing.

[PEP 621: Motivation](https://github.com/python/peps/blob/94a7775f23fd6eb7c527cf8180dab4542c5da622/peps/pep-0621.rst)

### Storing project metadata in pyproject.toml > Motivation

```text
The key motivators of this PEP are:

- Encourage users to specify core metadata statically for speed,
  ease of specification, unambiguity, and deterministic consumption by
  build back-ends
- Provide a tool-agnostic way of specifying metadata for ease of
  learning and transitioning between build back-ends
- Allow for more code sharing between build back-ends for the
  "boring parts" of a project's metadata

To speak specifically to the motivation for static metadata, that has
been an overall goal of the packaging ecosystem for some time. As
such, making it easy to specify metadata statically is important. This
also means that raising the cost of specifying data as dynamic is
acceptable as users should skew towards wanting to provide static
metadata.

Requiring the distinction between static and dynamic metadata also
helps with disambiguation for when metadata isn't specified. When any
metadata *may* be dynamic, it means you never know if the absence of
metadata is on purpose or because it is to be provided later. By
requiring that dynamic metadata be specified, it disambiguates the
intent when metadata goes unspecified.
```

### Storing project metadata in pyproject.toml > Motivation

```text
This PEP does **not** attempt to standardize all possible metadata
required by a build back-end, only the metadata covered by the
`core metadata`_ specification which are very common across projects
and would stand to benefit from being static and consistently
specified. This means build back-ends are still free and able to
innovate around patterns like how to specify the files to include in a
wheel. There is also an included escape hatch for users and build
back-ends to use when they choose to partially opt-out of this PEP
(compared to opting-out of this PEP entirely, which is also possible).

This PEP is also not trying to change the underlying `core metadata`_
in any way. Such considerations should be done in a separate PEP which
may lead to changes or additions to what this PEP specifies.
```

## pilot-011 / conceptual

According to PEP 380, why is a simple loop that re-yields values insufficient for full generator delegation?

**Draft answer:** It does not by itself handle the caller's send(), throw() and close() interactions with the subgenerator.

[PEP 380: Motivation](https://github.com/python/peps/blob/94a7775f23fd6eb7c527cf8180dab4542c5da622/peps/pep-0380.rst)

### Syntax for Delegating to a Subgenerator > Motivation

```text
A Python generator is a form of coroutine, but has the limitation that
it can only yield to its immediate caller.  This means that a piece of
code containing a ``yield`` cannot be factored out and put into a
separate function in the same way as other code.  Performing such a
factoring causes the called function to itself become a generator, and
it is necessary to explicitly iterate over this second generator and
re-yield any values that it produces.

If yielding of values is the only concern, this can be performed
without much difficulty using a loop such as

::

    for v in g:
        yield v

However, if the subgenerator is to interact properly with the caller
in the case of calls to ``send()``, ``throw()`` and ``close()``,
things become considerably more difficult.  As will be seen later, the
necessary code is very complicated, and it is tricky to handle all the
corner cases correctly.

A new syntax will be proposed to address this issue.  In the simplest
use cases, it will be equivalent to the above for-loop, but it will
also handle the full range of generator behaviour, and allow generator
code to be refactored in a simple and straightforward way.
```

## pilot-012 / conceptual

Why does PEP 723 propose metadata inside standalone scripts?

**Draft answer:** So tools can discover a script's runtime requirements without a separate project file or tool-specific metadata format.

[PEP 723: Motivation](https://github.com/python/peps/blob/94a7775f23fd6eb7c527cf8180dab4542c5da622/peps/pep-0723.rst)

### Inline script metadata > Motivation

```text
Python is routinely used as a scripting language, with Python scripts as a
(better) alternative to shell scripts, batch files, etc. When Python code is
structured as a script, it is usually stored as a single file and does not
expect the availability of any other local code that may be used for imports.
As such, it is possible to share with others over arbitrary text-based means
such as email, a URL to the script, or even a chat window. Code that is
structured like this may live as a single file forever, never becoming a
full-fledged project with its own directory and ``pyproject.toml`` file.

An issue that users encounter with this approach is that there is no standard
mechanism to define metadata for tools whose job it is to execute such scripts.
For example, a tool that runs a script may need to know which dependencies are
required or the supported version(s) of Python.

There is currently no standard tool that addresses this issue, and this PEP
does *not* attempt to define one. However, any tool that *does* address this
issue will need to know what the runtime requirements of scripts are. By
defining a standard format for storing such metadata, existing tools, as well
as any future tools, will be able to obtain that information without requiring
users to include tool-specific metadata in their scripts.
```

## pilot-013 / comparison

What type-annotation features do PEP 585 and PEP 604 add?

**Draft answer:** PEP 585 adds generic parameter syntax to standard collections; PEP 604 adds X | Y syntax for union types.

[PEP 585: Abstract](https://github.com/python/peps/blob/94a7775f23fd6eb7c527cf8180dab4542c5da622/peps/pep-0585.rst) | [PEP 604: Abstract](https://github.com/python/peps/blob/94a7775f23fd6eb7c527cf8180dab4542c5da622/peps/pep-0604.rst)

### Type Hinting Generics In Standard Collections > Abstract

```text
Static typing as defined by PEPs 484, 526, 544, 560, and 563 was built
incrementally on top of the existing Python runtime and constrained by
existing syntax and runtime behavior.  This led to the existence of
a duplicated collection hierarchy in the ``typing`` module due to
generics (for example ``typing.List`` and the built-in ``list``).

This PEP proposes to enable support for the generics syntax in all
standard collections currently available in the ``typing`` module.
```

### Allow writing union types as ``X | Y`` > Abstract

```text
This PEP proposes overloading the ``|`` operator on types to allow
writing ``Union[X, Y]`` as ``X | Y``, and allows it to appear in
``isinstance`` and ``issubclass`` calls.
```

## pilot-014 / comparison

What asynchronous features do PEP 525 and PEP 530 add?

**Draft answer:** PEP 525 adds asynchronous generators; PEP 530 adds asynchronous comprehensions and generator expressions.

[PEP 525: Abstract](https://github.com/python/peps/blob/94a7775f23fd6eb7c527cf8180dab4542c5da622/peps/pep-0525.rst) | [PEP 530: Abstract](https://github.com/python/peps/blob/94a7775f23fd6eb7c527cf8180dab4542c5da622/peps/pep-0530.rst)

### Asynchronous Generators > Abstract

```text
:pep:`492` introduced support for native coroutines and ``async``/``await``
syntax to Python 3.5.  It is proposed here to extend Python's
asynchronous capabilities by adding support for
*asynchronous generators*.
```

### Asynchronous Comprehensions > Abstract

```text
:pep:`492` and :pep:`525` introduce support for native coroutines and
asynchronous generators using ``async`` / ``await`` syntax.  This PEP
proposes to add asynchronous versions of list, set, dict comprehensions
and generator expressions.
```

## pilot-015 / comparison

Where do PEP 621 and PEP 723 place metadata?

**Draft answer:** PEP 621 places project core metadata in pyproject.toml; PEP 723 embeds script metadata in the script itself.

[PEP 621: Abstract](https://github.com/python/peps/blob/94a7775f23fd6eb7c527cf8180dab4542c5da622/peps/pep-0621.rst) | [PEP 723: Abstract](https://github.com/python/peps/blob/94a7775f23fd6eb7c527cf8180dab4542c5da622/peps/pep-0723.rst)

### Storing project metadata in pyproject.toml > Abstract

```text
This PEP specifies how to write a project's `core metadata`_ in a
``pyproject.toml`` file for packaging-related tools to consume.
```

### Inline script metadata > Abstract

```text
This PEP specifies a metadata format that can be embedded in single-file Python
scripts to assist launchers, IDEs and other external tools which may need to
interact with such scripts.
```

## pilot-016 / comparison

Which is the pattern-matching specification and which is the tutorial: PEP 634 or PEP 636?

**Draft answer:** PEP 634 is the specification; PEP 636 is the tutorial.

[PEP 634: Abstract](https://github.com/python/peps/blob/94a7775f23fd6eb7c527cf8180dab4542c5da622/peps/pep-0634.rst) | [PEP 636: Abstract](https://github.com/python/peps/blob/94a7775f23fd6eb7c527cf8180dab4542c5da622/peps/pep-0636.rst)

### Structural Pattern Matching: Specification > Abstract

```text
This PEP provides the technical specification for the match
statement.  It replaces :pep:`622`, which is hereby split in three parts:

- :pep:`634`: Specification
- :pep:`635`: Motivation and Rationale
- :pep:`636`: Tutorial

This PEP is intentionally devoid of commentary; the motivation and all
explanations of our design choices are in :pep:`635`.  First-time readers
are encouraged to start with :pep:`636`, which provides a gentler
introduction to the concepts, syntax and semantics of patterns.
```

### Structural Pattern Matching: Tutorial > Abstract

```text
This PEP is a tutorial for the pattern matching introduced by :pep:`634`.

:pep:`622` proposed syntax for pattern matching, which received detailed discussion
both from the community and the Steering Council. A frequent concern was
about how easy it would be to explain (and learn) this feature. This PEP
addresses that concern providing the kind of document which developers could use
to learn about pattern matching in Python.

This is considered supporting material for :pep:`634` (the technical specification
for pattern matching) and :pep:`635` (the motivation and rationale for having pattern
matching and design considerations).

For readers who are looking more for a quick review than for a tutorial,
see `Appendix A <PEP 636 Appendix A_>`_.
```

## pilot-017 / multi_hop

Which PEP defines the field-annotation syntax used by data classes, and what limitation does it identify for type comments on uninitialized variables?

**Draft answer:** PEP 526. Type comments cannot annotate an undefined variable without initializing it, for example to None.

[PEP 557: Abstract](https://github.com/python/peps/blob/94a7775f23fd6eb7c527cf8180dab4542c5da622/peps/pep-0557.rst) | [PEP 526: Rationale](https://github.com/python/peps/blob/94a7775f23fd6eb7c527cf8180dab4542c5da622/peps/pep-0526.rst)

### Data Classes > Abstract

```text
This PEP describes an addition to the standard library called Data
Classes.  Although they use a very different mechanism, Data Classes
can be thought of as "mutable namedtuples with defaults".  Because
Data Classes use normal class definition syntax, you are free to use
inheritance, metaclasses, docstrings, user-defined methods, class
factories, and other Python class features.

A class decorator is provided which inspects a class definition for
variables with type annotations as defined in :pep:`526`, "Syntax for
Variable Annotations".  In this document, such variables are called
fields.  Using these fields, the decorator adds generated method
definitions to the class to support instance initialization, a repr,
comparison methods, and optionally other methods as described in the
Specification_ section.  Such a class is called a Data Class, but
there's really nothing special about the class: the decorator adds
generated methods to the class and returns the same class it was
given.

As an example::

  @dataclass
  class InventoryItem:
      '''Class for keeping track of an item in inventory.'''
      name: str
      unit_price: float
      quantity_on_hand: int = 0

      def total_cost(self) -> float:
          return self.unit_price * self.quantity_on_hand

The ``@dataclass`` decorator will add the equivalent of these methods
to the InventoryItem class::
```

### Data Classes > Abstract

```text
def total_cost(self) -> float:
          return self.unit_price * self.quantity_on_hand

The ``@dataclass`` decorator will add the equivalent of these methods
to the InventoryItem class::
```

### Data Classes > Abstract

```text
The ``@dataclass`` decorator will add the equivalent of these methods
to the InventoryItem class::
```

### Data Classes > Abstract

```text
def __init__(self, name: str, unit_price: float, quantity_on_hand: int = 0) -> None:
      self.name = name
      self.unit_price = unit_price
      self.quantity_on_hand = quantity_on_hand
  def __repr__(self):
      return f'InventoryItem(name={self.name!r}, unit_price={self.unit_price!r}, quantity_on_hand={self.quantity_on_hand!r})'
  def __eq__(self, other):
      if other.__class__ is self.__class__:
          return (self.name, self.unit_price, self.quantity_on_hand) == (other.name, other.unit_price, other.quantity_on_hand)
      return NotImplemented
  def __ne__(self, other):
      if other.__class__ is self.__class__:
          return (self.name, self.unit_price, self.quantity_on_hand) != (other.name, other.unit_price, other.quantity_on_hand)
      return NotImplemented
  def __lt__(self, other):
      if other.__class__ is self.__class__:
          return (self.name, self.unit_price, self.quantity_on_hand) < (other.name, other.unit_price, other.quantity_on_hand)
      return NotImplemented
  def __le__(self, other):
      if other.__class__ is self.__class__:
          return (self.name, self.unit_price, self.quantity_on_hand) <= (other.name, other.unit_price, other.quantity_on_hand)
      return NotImplemented
  def __gt__(self, other):
      if other.__class__ is self.__class__:
          return (self.name, self.unit_price, self.quantity_on_hand) > (other.name, other.unit_price, other.quantity_on_hand)
      return NotImplemented
  def __ge__(self, other):
      if other.__class__ is self.__class__:
          return (self.name, self.unit_price,
```

### Data Classes > Abstract

```text
self.quantity_on_hand) >= (other.name, other.unit_price, other.quantity_on_hand)
      return NotImplemented

Data Classes save you from writing and maintaining these methods.
```

### Syntax for Variable Annotations > Rationale

```text
Although type comments work well enough, the fact that they're
expressed through comments has some downsides:

- Text editors often highlight comments differently from type annotations.

- There's no way to annotate the type of an undefined variable; one needs to
  initialize it to ``None`` (e.g. ``a = None # type: int``).

- Variables annotated in a conditional branch are difficult to read::

    if some_value:
        my_var = function() # type: Logger
    else:
        my_var = another_function() # Why isn't there a type here?

- Since type comments aren't actually part of the language, if a Python script
  wants to parse them, it requires a custom parser instead of just using
  ``ast``.

- Type comments are used a lot in typeshed. Migrating typeshed to use
  the variable annotation syntax instead of type comments would improve
  readability of stubs.

- In situations where normal comments and type comments are used together, it is
  difficult to distinguish them::

    path = None  # type: Optional[str]  # Path to module source

- It's impossible to retrieve the annotations at runtime outside of
  attempting to find the module's source code and parse it at runtime,
  which is inelegant, to say the least.

The majority of these issues can be alleviated by making the syntax
a core part of the language. Moreover, having a dedicated annotation syntax
for class and instance variables (in addition to method annotations) will
pave the way to static duck-typing as a complement to nominal typing defined
by :pep:`484`.
```

## pilot-018 / multi_hop

Which native-coroutine PEP does PEP 525 build on, and does that earlier proposal require a specific event-loop implementation?

**Draft answer:** PEP 492. It is not tied to a specific event-loop implementation.

[PEP 525: Abstract](https://github.com/python/peps/blob/94a7775f23fd6eb7c527cf8180dab4542c5da622/peps/pep-0525.rst) | [PEP 492: Abstract](https://github.com/python/peps/blob/94a7775f23fd6eb7c527cf8180dab4542c5da622/peps/pep-0492.rst)

### Asynchronous Generators > Abstract

```text
:pep:`492` introduced support for native coroutines and ``async``/``await``
syntax to Python 3.5.  It is proposed here to extend Python's
asynchronous capabilities by adding support for
*asynchronous generators*.
```

### Coroutines with async and await syntax > Abstract

```text
The growth of Internet and general connectivity has triggered the
proportionate need for responsive and scalable code.  This proposal
aims to answer that need by making writing explicitly asynchronous,
concurrent Python code easier and more Pythonic.

It is proposed to make *coroutines* a proper standalone concept in
Python, and introduce new supporting syntax.  The ultimate goal
is to help establish a common, easily approachable, mental
model of asynchronous programming in Python and make it as close to
synchronous programming as possible.

This PEP assumes that the asynchronous tasks are scheduled and
coordinated by an Event Loop similar to that of stdlib module
``asyncio.events.AbstractEventLoop``.  While the PEP is not tied to any
specific Event Loop implementation, it is relevant only to the kind of
coroutine that uses ``yield`` as a signal to the scheduler, indicating
that the coroutine will be waiting until an event (such as IO) is
completed.

We believe that the changes proposed here will help keep Python
relevant and competitive in a quickly growing area of asynchronous
programming, as many other languages have adopted, or are planning to
adopt, similar features: [2]_, [5]_, [6]_, [7]_, [8]_, [10]_.
```

## pilot-019 / multi_hop

Which rationale PEP does PEP 636 point to, and what type-or-shape checking idiom does its Motivation section show match replacing?

**Draft answer:** PEP 635. It shows match replacing an if/elif/else chain that checks an object's type or shape.

[PEP 636: Abstract](https://github.com/python/peps/blob/94a7775f23fd6eb7c527cf8180dab4542c5da622/peps/pep-0636.rst) | [PEP 635: Motivation](https://github.com/python/peps/blob/94a7775f23fd6eb7c527cf8180dab4542c5da622/peps/pep-0635.rst)

### Structural Pattern Matching: Tutorial > Abstract

```text
This PEP is a tutorial for the pattern matching introduced by :pep:`634`.

:pep:`622` proposed syntax for pattern matching, which received detailed discussion
both from the community and the Steering Council. A frequent concern was
about how easy it would be to explain (and learn) this feature. This PEP
addresses that concern providing the kind of document which developers could use
to learn about pattern matching in Python.

This is considered supporting material for :pep:`634` (the technical specification
for pattern matching) and :pep:`635` (the motivation and rationale for having pattern
matching and design considerations).

For readers who are looking more for a quick review than for a tutorial,
see `Appendix A <PEP 636 Appendix A_>`_.
```

### Structural Pattern Matching: Motivation and Rationale > Motivation

```text
(Structural) pattern matching syntax is found in many languages, from
Haskell, Erlang and Scala to Elixir and Ruby.  (A proposal for
JavaScript is also under consideration.)

Python already supports a limited form of this through sequence
unpacking assignments, which the new proposal leverages.

Several other common Python idioms are also relevant:

- The ``if ... elif ... elif ... else`` idiom is often used to find
  out the type or shape of an object in an ad-hoc fashion, using one
  or more checks like ``isinstance(x, cls)``, ``hasattr(x, "attr")``,
  ``len(x) == n`` or ``"key" in x`` as guards to select an applicable
  block.  The block can then assume ``x`` supports the interface
  checked by the guard.  For example::

    if isinstance(x, tuple) and len(x) == 2:
        host, port = x
        mode = "http"
    elif isinstance(x, tuple) and len(x) == 3:
        host, port, mode = x
    # Etc.

  Code like this is more elegantly rendered using ``match``::

    match x:
        case host, port:
            mode = "http"
        case host, port, mode:
            pass
        # Etc.

- AST traversal code often looks for nodes matching a given pattern,
  for example the code to detect a node of the shape "A + B * C" might
  look like this::

    if (isinstance(node, BinOp) and node.op == "+"
            and isinstance(node.right, BinOp) and node.right.op == "*"):
        a, b, c = node.left, node.right.left, node.right.right
        # Handle a + b*c

  Using ``match`` this becomes more readable::
```

### Structural Pattern Matching: Motivation and Rationale > Motivation

```text
Using ``match`` this becomes more readable::

    match node:
        case BinOp("+", a, BinOp("*", b, c)):
            # Handle a + b*c

We believe that adding pattern matching to Python will enable Python
users to write cleaner, more readable code for examples like those
above, and many others.

For a more academic discussion to this proposal, see [1]_.
```

## pilot-020 / multi_hop

Which type-hinting PEP does PEP 544 extend, and does that earlier proposal require runtime type checking?

**Draft answer:** PEP 484. It does not require runtime type checking.

[PEP 544: Abstract](https://github.com/python/peps/blob/94a7775f23fd6eb7c527cf8180dab4542c5da622/peps/pep-0544.rst) | [PEP 484: Abstract](https://github.com/python/peps/blob/94a7775f23fd6eb7c527cf8180dab4542c5da622/peps/pep-0484.rst)

### Protocols: Structural subtyping (static duck typing) > Abstract

```text
Type hints introduced in :pep:`484` can be used to specify type metadata
for static type checkers and other third party tools. However, :pep:`484`
only specifies the semantics of *nominal* subtyping. In this PEP we specify
static and runtime semantics of protocol classes that will provide a support
for *structural* subtyping (static duck typing).


.. _PEP 544 rationale:
```

### Type Hints > Abstract

```text
:pep:`3107` introduced syntax for function annotations, but the semantics
were deliberately left undefined.  There has now been enough 3rd party
usage for static type analysis that the community would benefit from
a standard vocabulary and baseline tools within the standard library.

This PEP introduces a provisional module to provide these standard
definitions and tools, along with some conventions for situations
where annotations are not available.

Note that this PEP still explicitly does NOT prevent other uses of
annotations, nor does it require (or forbid) any particular processing
of annotations, even when they conform to this specification.  It
simply enables better coordination, as :pep:`333` did for web frameworks.

For example, here is a simple function whose argument and return type
are declared in the annotations::

  def greeting(name: str) -> str:
      return 'Hello ' + name

While these annotations are available at runtime through the usual
``__annotations__`` attribute, *no type checking happens at runtime*.
Instead, the proposal assumes the existence of a separate off-line
type checker which users can run over their source code voluntarily.
Essentially, such a type checker acts as a very powerful linter.
(While it would of course be possible for individual users to employ
a similar checker at run time for Design By Contract enforcement or
JIT optimization, those tools are not yet as mature.)
```

### Type Hints > Abstract

```text
The proposal is strongly inspired by `mypy <mypy_>`_.  For example, the
type "sequence of integers" can be written as ``Sequence[int]``.  The
square brackets mean that no new syntax needs to be added to the
language.  The example here uses a custom type ``Sequence``, imported
from a pure-Python module ``typing``.  The ``Sequence[int]`` notation
works at runtime by implementing ``__getitem__()`` in the metaclass
(but its significance is primarily to an offline type checker).

The type system supports unions, generic types, and a special type
named ``Any`` which is consistent with (i.e. assignable to and from) all
types.  This latter feature is taken from the idea of gradual typing.
Gradual typing and the full type system are explained in :pep:`483`.

Other approaches from which we have borrowed or to which ours can be
compared and contrasted are described in :pep:`482`.
```

## pilot-021 / unanswerable

What is this RAG platform's production database password?

**Draft answer:** The provided PEP corpus does not contain that information.

[PEP 621: Abstract](https://github.com/python/peps/blob/94a7775f23fd6eb7c527cf8180dab4542c5da622/peps/pep-0621.rst)

Attached passage is background only, not supporting evidence.

### Storing project metadata in pyproject.toml > Abstract

```text
This PEP specifies how to write a project's `core metadata`_ in a
``pyproject.toml`` file for packaging-related tools to consume.
```

## pilot-022 / unanswerable

What was this project's Anthropic API bill for September 2026?

**Draft answer:** The provided PEP corpus does not contain that information.

[PEP 723: Abstract](https://github.com/python/peps/blob/94a7775f23fd6eb7c527cf8180dab4542c5da622/peps/pep-0723.rst)

Attached passage is background only, not supporting evidence.

### Inline script metadata > Abstract

```text
This PEP specifies a metadata format that can be embedded in single-file Python
scripts to assist launchers, IDEs and other external tools which may need to
interact with such scripts.
```

## pilot-023 / unanswerable

What is this RAG service's measured 95th-percentile response time in production?

**Draft answer:** The provided PEP corpus does not contain that information.

[PEP 492: Abstract](https://github.com/python/peps/blob/94a7775f23fd6eb7c527cf8180dab4542c5da622/peps/pep-0492.rst)

Attached passage is background only, not supporting evidence.

### Coroutines with async and await syntax > Abstract

```text
The growth of Internet and general connectivity has triggered the
proportionate need for responsive and scalable code.  This proposal
aims to answer that need by making writing explicitly asynchronous,
concurrent Python code easier and more Pythonic.

It is proposed to make *coroutines* a proper standalone concept in
Python, and introduce new supporting syntax.  The ultimate goal
is to help establish a common, easily approachable, mental
model of asynchronous programming in Python and make it as close to
synchronous programming as possible.

This PEP assumes that the asynchronous tasks are scheduled and
coordinated by an Event Loop similar to that of stdlib module
``asyncio.events.AbstractEventLoop``.  While the PEP is not tied to any
specific Event Loop implementation, it is relevant only to the kind of
coroutine that uses ``yield`` as a signal to the scheduler, indicating
that the coroutine will be waiting until an event (such as IO) is
completed.

We believe that the changes proposed here will help keep Python
relevant and competitive in a quickly growing area of asynchronous
programming, as many other languages have adopted, or are planning to
adopt, similar features: [2]_, [5]_, [6]_, [7]_, [8]_, [10]_.
```

## pilot-024 / unanswerable

What issue was reported in support ticket ACME-9382?

**Draft answer:** The provided PEP corpus does not contain that information.

[PEP 343: Abstract](https://github.com/python/peps/blob/94a7775f23fd6eb7c527cf8180dab4542c5da622/peps/pep-0343.rst)

Attached passage is background only, not supporting evidence.

### The "with" Statement > Abstract

```text
This PEP adds a new statement "with" to the Python language to make
it possible to factor out standard uses of ``try/finally`` statements.

In this PEP, context managers provide ``__enter__()`` and ``__exit__()``
methods that are invoked on entry to and exit from the body of the
with statement.
```
