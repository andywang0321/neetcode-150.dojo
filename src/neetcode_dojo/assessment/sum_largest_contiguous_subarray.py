"""QUARANTINED assessment for `sum_largest_contiguous_subarray` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("sum_largest_contiguous_subarray")
def _sum_largest_subarray_oracle(A: list[int]) -> int:
    best = 0
    for i in range(len(A)):
        total = 0
        for j in range(i, len(A)):
            total += A[j]
            best = max(best, total)
    return best


@cases("sum_largest_contiguous_subarray")
def _sum_largest_case(n: int, rng: random.Random) -> tuple[list, int]:
    n = max(0, min(n, 12))
    A = [rng.randint(-10, 10) for _ in range(n)]
    return [A], _sum_largest_subarray_oracle(A)


@inputs("sum_largest_contiguous_subarray")
def _sum_largest_profiler(n: int, rng: random.Random) -> list:
    return [[rng.randint(-100, 100) for _ in range(n)]]


@reference("sum_largest_contiguous_subarray")
def sum_largest_subarray(A: list[int]) -> int:
    best = 0
    current = 0
    for x in A:
        current += x
        if current < 0:
            current = 0
        elif current > best:
            best = current
    return best


@measure("sum_largest_contiguous_subarray")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
