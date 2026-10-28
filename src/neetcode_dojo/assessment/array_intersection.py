"""QUARANTINED assessment for `array_intersection` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("array_intersection")
def _intersection_oracle(A: list[int], B: list[int]) -> list[int]:
    return sorted(set(A) & set(B))


@cases("array_intersection")
def _intersection_case(n: int, rng: random.Random) -> tuple[list, list, dict]:
    n = max(0, min(n, 12))
    A = [rng.randint(-5, 5) for _ in range(rng.randint(0, n))]
    B = [rng.randint(-5, 5) for _ in range(rng.randint(0, n))]
    return [A, B], _intersection_oracle(A, B), {"compare": "sorted"}


@inputs("array_intersection")
def _intersection_profiler(n: int, rng: random.Random) -> list:
    return [list(range(n)), list(range(n // 2, n + n // 2))]


@reference("array_intersection")
def _intersection_reference(A: list[int], B: list[int]) -> list[int]:
    return sorted(set(A) & set(B))


@measure("array_intersection")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
