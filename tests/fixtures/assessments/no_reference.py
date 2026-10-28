"""Test fixture assessment: a measurement plan with no reference baseline."""

import random

from neetcode_dojo.registry import cases, inputs, measure


@cases("no_reference")
def _cases(n: int, rng: random.Random) -> tuple[list, int]:
    values = [rng.randint(0, 9) for _ in range(max(1, n))]
    return [values], len(values)


@inputs("no_reference")
def _inputs(n: int, rng: random.Random) -> list:
    return [list(range(n))]


@measure("no_reference")
def _measure(ctx: dict) -> dict:
    return {"axis": "n", "sizes": [32, 64, 128, 256], "baseline": "none", "compare": "strict"}
