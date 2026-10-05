# Pilot v2: final human review

All 24 entries were accepted by the project owner after reviewing this revision.
The frozen evaluation set is `eval_sets/v1` (version `1f48f2e04ef7`).
No Anthropic API calls were made to prepare or record the review.

Use only the pinned PEP corpus. Equivalent correct wording is acceptable.
Evidence: [full source packet](pilot-review.md). Further edits require a new eval-set version.
Unanswerable items test abstention; their attached passages are background only.

## pilot-001 / exact_term

Does PEP 484 require Python to enforce type hints at runtime?

**Expected answer:** No. PEP 484 does not require runtime type checking.

## pilot-002 / exact_term

According to PEP 604, what does X | Y mean in a type annotation?

**Expected answer:** A union type, equivalent to Union[X, Y].

## pilot-003 / exact_term

According to PEP 655, what do Required[] and NotRequired[] mean for a TypedDict key?

**Expected answer:** Required[] means the key must be present; NotRequired[] means it may be absent.

## pilot-004 / exact_term

What syntax does PEP 572 introduce for assigning a value within an expression?

**Expected answer:** NAME := expr.

## pilot-005 / lookup

What file extension and archive format does a Python wheel use?

**Expected answer:** The .whl extension and ZIP archive format.

## pilot-006 / lookup

Which methods form the context-manager protocol described by PEP 343?

**Expected answer:** The methods __enter__() and __exit__().

## pilot-007 / lookup

Which file does PEP 621 use for project core metadata?

**Expected answer:** pyproject.toml.

## pilot-008 / lookup

Which asynchronous expression forms does PEP 530 add?

**Expected answer:** List, set and dict comprehensions, and generator expressions.

## pilot-009 / conceptual

Why does PEP 526 favor annotation syntax over type comments for parsing?

**Expected answer:** Its rationale says annotation syntax can be parsed with ast, while type comments require a custom parser.

## pilot-010 / conceptual

Why does PEP 621 require dynamic metadata to be declared explicitly?

**Expected answer:** To distinguish metadata that will be supplied later from metadata that is simply missing.

## pilot-011 / conceptual

According to PEP 380, why is a simple loop that re-yields values insufficient for full generator delegation?

**Expected answer:** It does not by itself handle the caller's send(), throw() and close() interactions with the subgenerator.

## pilot-012 / conceptual

Why does PEP 723 propose metadata inside standalone scripts?

**Expected answer:** So tools can discover a script's runtime requirements without a separate project file or tool-specific metadata format.

## pilot-013 / comparison

What type-annotation features do PEP 585 and PEP 604 add?

**Expected answer:** PEP 585 adds generic parameter syntax to standard collections; PEP 604 adds X | Y syntax for union types.

## pilot-014 / comparison

What asynchronous features do PEP 525 and PEP 530 add?

**Expected answer:** PEP 525 adds asynchronous generators; PEP 530 adds asynchronous comprehensions and generator expressions.

## pilot-015 / comparison

Where do PEP 621 and PEP 723 place metadata?

**Expected answer:** PEP 621 places project core metadata in pyproject.toml; PEP 723 embeds script metadata in the script itself.

## pilot-016 / comparison

Which is the pattern-matching specification and which is the tutorial: PEP 634 or PEP 636?

**Expected answer:** PEP 634 is the specification; PEP 636 is the tutorial.

## pilot-017 / multi_hop

Which PEP defines the field-annotation syntax used by data classes, and what limitation does it identify for type comments on uninitialized variables?

**Expected answer:** PEP 526. Type comments cannot annotate an undefined variable without initializing it, for example to None.

## pilot-018 / multi_hop

Which native-coroutine PEP does PEP 525 build on, and does that earlier proposal require a specific event-loop implementation?

**Expected answer:** PEP 492. It is not tied to a specific event-loop implementation.

## pilot-019 / multi_hop

Which rationale PEP does PEP 636 point to, and what type-or-shape checking idiom does its Motivation section show match replacing?

**Expected answer:** PEP 635. It shows match replacing an if/elif/else chain that checks an object's type or shape.

## pilot-020 / multi_hop

Which type-hinting PEP does PEP 544 extend, and does that earlier proposal require runtime type checking?

**Expected answer:** PEP 484. It does not require runtime type checking.

## pilot-021 / unanswerable

What is this RAG platform's production database password?

**Expected answer:** The provided PEP corpus does not contain that information.

## pilot-022 / unanswerable

What was this project's Anthropic API bill for September 2026?

**Expected answer:** The provided PEP corpus does not contain that information.

## pilot-023 / unanswerable

What is this RAG service's measured 95th-percentile response time in production?

**Expected answer:** The provided PEP corpus does not contain that information.

## pilot-024 / unanswerable

What issue was reported in support ticket ACME-9382?

**Expected answer:** The provided PEP corpus does not contain that information.
