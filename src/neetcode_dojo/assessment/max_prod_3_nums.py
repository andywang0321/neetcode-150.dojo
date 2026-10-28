"""QUARANTINED assessment for `max_prod_3_nums` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("max_prod_3_nums")
def _max_tri_prod_oracle(A: list[int]) -> int:
    best = -(10**18)
    for i in range(len(A)):
        for j in range(i + 1, len(A)):
            for k in range(j + 1, len(A)):
                best = max(best, A[i] * A[j] * A[k])
    return best


@cases("max_prod_3_nums")
def _max_tri_prod_case(n: int, rng: random.Random) -> tuple[list, int]:
    n = max(3, min(n, 12))
    A = [rng.randint(-10, 10) for _ in range(n)]
    return [A], _max_tri_prod_oracle(A)


@inputs("max_prod_3_nums")
def _max_tri_prod_profiler(n: int, rng: random.Random) -> list:
    return [[rng.randint(-100, 100) for _ in range(n)]]


@reference("max_prod_3_nums")
def max_tri_prod(A: list[int]) -> int:
    A.sort()
    return max(A[-1] * A[-2] * A[-3], A[0] * A[1] * A[-1])


@measure("max_prod_3_nums")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
