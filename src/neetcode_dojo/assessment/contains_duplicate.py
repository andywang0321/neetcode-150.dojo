"""QUARANTINED assessment for `contains_duplicate` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("contains_duplicate")
def _contains_duplicate_oracle(nums: list[int]) -> bool:
    return len(nums) != len(set(nums))


@cases("contains_duplicate")
def _contains_duplicate_case(n: int, rng: random.Random) -> tuple[list, bool]:
    n = max(0, min(n, 12))
    nums = [rng.randint(-5, 5) for _ in range(n)]
    if n >= 2 and rng.random() < 0.5:
        nums[rng.randrange(n)] = nums[0]  # force a duplicate
    return [nums], _contains_duplicate_oracle(nums)


@inputs("contains_duplicate")
def _contains_duplicate_profiler(n: int, rng: random.Random) -> list:
    values = list(range(n))  # all distinct: no early exit for anyone
    rng.shuffle(values)
    return [values]


@reference("contains_duplicate")
def _contains_duplicate_reference(nums: list[int]) -> bool:
    return len(nums) != len(set(nums))


@measure("contains_duplicate")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
