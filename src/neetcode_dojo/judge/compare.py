"""Per-case verdict semantics, shared by the judge harness and the case runner.

These functions live here so the harness and the parent apply exactly one
implementation of a case's meaning: a case cannot mean one thing inside the
subprocess and another in the test that admits it.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any


def canonical(value: Any) -> Any:
    """Deep-sort lists (and dicts by key) for order-insensitive compare."""

    def list_key(item: Any) -> str:
        return json.dumps(item, sort_keys=True, default=str)

    def dict_key(item: tuple[str, Any]) -> str:
        return json.dumps(item[0], sort_keys=True, default=str)

    if isinstance(value, list):
        return sorted((canonical(item) for item in value), key=list_key)
    if isinstance(value, dict):
        return [(key, canonical(item)) for key, item in sorted(value.items(), key=dict_key)]
    return value


def rounded(value: Any, ndigits: int) -> Any:
    if isinstance(value, float):
        return round(value, ndigits)
    if isinstance(value, list):
        return [rounded(item, ndigits) for item in value]
    if isinstance(value, dict):
        return {key: rounded(item, ndigits) for key, item in value.items()}
    return value


def approx_equal(a: Any, b: Any, tol: float) -> bool:
    if isinstance(a, int | float) and isinstance(b, int | float):
        if isinstance(a, float) or isinstance(b, float):
            return abs(a - b) <= tol
        return a == b
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(approx_equal(x, y, tol) for x, y in zip(a, b, strict=True))
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(approx_equal(a[key], b[key], tol) for key in a)
    return a == b


def check_equal(got: Any, expected: Any, mode: str) -> bool:
    """Apply one case's verdict mode. Default is strict JSON equality.

    ``"none"`` means the *measurement* does not compare outputs (several answers
    are valid); on a judge case the pre-port behaviour was strict equality, and
    it stays that way so a case tagged ``none`` can never become a free pass."""
    if mode.startswith("approx"):
        tol = float(mode.split(":", 1)[1]) if ":" in mode else 1e-9
        return approx_equal(got, expected, tol)
    if mode.startswith("rounded"):
        ndigits = int(mode.split(":", 1)[1]) if ":" in mode else 4
        got, expected = rounded(got, ndigits), rounded(expected, ndigits)
    elif mode == "sorted":
        got, expected = canonical(got), canonical(expected)
    return json.dumps(got, sort_keys=True) == json.dumps(expected, sort_keys=True)


def case_verdict(case: Mapping[str, Any], got: Any, args: Any) -> bool:
    """Judge one case's outcome, with ``"mutates"`` semantics applied.

    ``got`` is the call's return value and ``args`` the argument list as it stands
    *after* the call. A ``"mutates"`` case is one where the item's contract is the
    effect on its arguments — "modify in place, return nothing" (an in-place
    rotation, a zeroing pass) — so the value under comparison is the post-call
    argument list, not the (``None``) return:

        {"args": [[[1, 2], [3, 4]]], "expected": [[[3, 1], [4, 2]]],
         "compare": "mutates"}

    Every other mode compares the return value, unchanged."""
    if case.get("compare") == "mutates":
        return check_equal(args, case.get("expected"), "strict")
    return check_equal(got, case.get("expected"), str(case.get("compare", "strict")))
