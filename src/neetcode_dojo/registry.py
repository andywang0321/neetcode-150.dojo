"""What a private assessment module registers with — the curriculum's own registry.

A copied `assessment/<item>.py` imports these decorators and registers what it
provides. The surface is the old engine's `dojo.curriculum.registry` surface, so a
ported module changes only its import line:

- ``@oracle(id)``    — the brute-force correctness anchor
- ``@cases(id)``     — small judge cases: ``(n, rng) -> (args, expected[, extras])``
- ``@inputs(id)``    — one measurement-ladder rung: ``(n, rng) -> args``
- ``@reference(id)`` — the canonical solution the student is paired against
- ``@rubric(id)``    — the dimensions a judged item is graded on
- ``@measure(id)``   — the measurement *plan* (axis, sizes, baseline, compare)
- ``@checker(name)`` — a predicate a case may tag with ``{"predicate": name}``

**`@cases` and `@inputs` are different jobs.** `@cases` is asked for small inputs
and must attach the expected answer, because the judge compares against it.
`@inputs` is asked for one input at one rung of the ladder and must not, because the
measurement pairs the student against the reference on the same input. A generator
written for small inputs and reused for the ladder clamps them, and then every rung
measures the same tiny input.

**This module is stdlib-only and imports nothing from a server or engine**, because
it is imported inside the assessment subprocess next to untrusted student code.

Registrations are global to the process. The loader runs one assessment module per
bounded child, so two items can never see each other's registrations.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

type Registration = Callable[..., Any]
type Decorator = Callable[[Registration], Registration]
type Registrar = Callable[[str], Decorator]

#: item id -> callable(*args) -> expected output.
ORACLES: dict[str, Registration] = {}

#: item id -> (n, rng) -> (args, expected) or (args, expected, extras).
CASES: dict[str, Registration] = {}

#: item id -> (n, rng) -> args, for one rung of the measurement ladder.
INPUTS: dict[str, Registration] = {}

#: item id -> callable(*args) -> canonical output (the paired baseline).
REFERENCES: dict[str, Registration] = {}

#: item id -> callable() -> {"dimensions": [...], "pass": ...}.
RUBRICS: dict[str, Registration] = {}

#: item id -> callable(ctx) -> the measurement plan (data, never a callable).
MEASURES: dict[str, Registration] = {}

#: name -> (module, got, args) -> bool, for cases tagged {"predicate": name}.
CHECKERS: dict[str, Registration] = {}

#: The stores by the name the format uses, so a loader and its harness can talk
#: about kinds without a second list drifting out of step with this one.
STORES: dict[str, dict[str, Registration]] = {
    "oracle": ORACLES,
    "cases": CASES,
    "inputs": INPUTS,
    "reference": REFERENCES,
    "rubric": RUBRICS,
    "measure": MEASURES,
    "checker": CHECKERS,
}

#: The kinds whose registration name must be an item id in the same curriculum.
ITEM_KINDS: tuple[str, ...] = ("oracle", "cases", "inputs", "reference", "rubric", "measure")


def _registrar(store: dict[str, Registration], kind: str) -> Registrar:
    def decorator(name: str) -> Decorator:
        if not isinstance(name, str) or not name:
            raise ValueError(f"@{kind} needs a non-empty registration name")

        def register(fn: Registration) -> Registration:
            store[name] = fn
            return fn

        return register

    return decorator


def oracle(name: str) -> Decorator:
    """The correctness anchor. Prefer the obvious implementation: it is the one
    you can trust, and it is allowed to be far too slow to measure."""
    return _registrar(ORACLES, "oracle")(name)


def cases(name: str) -> Decorator:
    """Small judge cases with their expected answers attached."""
    return _registrar(CASES, "cases")(name)


def inputs(name: str) -> Decorator:
    """One input at one rung of the measurement ladder, with no expected answer."""
    return _registrar(INPUTS, "inputs")(name)


def reference(name: str) -> Decorator:
    """The canonical, intended-complexity solution: the paired baseline."""
    return _registrar(REFERENCES, "reference")(name)


def rubric(name: str) -> Decorator:
    """The dimensions a judged item is scored on."""
    return _registrar(RUBRICS, "rubric")(name)


def measure(name: str) -> Decorator:
    """The measurement policy: what to measure, or that it is not measurable."""
    return _registrar(MEASURES, "measure")(name)


def checker(name: str) -> Decorator:
    """A predicate a generated case may reference as ``{"predicate": name}``."""
    return _registrar(CHECKERS, "checker")(name)


def registrations() -> dict[str, list[str]]:
    """The registered names by kind — what a probe reports back to the loader."""
    return {kind: sorted(store) for kind, store in STORES.items()}


def reset() -> None:
    """Forget every registration. For tests and a harness that loads more than one
    module in one process."""
    for store in STORES.values():
        store.clear()
