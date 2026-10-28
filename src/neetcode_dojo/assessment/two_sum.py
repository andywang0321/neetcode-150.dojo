"""QUARANTINED assessment for `two_sum` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("two_sum")
def _twosum_oracle(nums: list[int], target: int) -> list[int]:
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []


@cases("two_sum")
def _twosum_case(n: int, rng: random.Random) -> tuple[list, list]:
    n = max(2, min(n, 12))
    nums = rng.sample(range(-20, 21), n)
    i, j = rng.sample(range(n), 2)
    target = nums[i] + nums[j]
    pairs = [(a, b) for a in range(n) for b in range(a + 1, n) if nums[a] + nums[b] == target]
    while len(pairs) != 1:  # the prompt guarantees exactly one valid pair
        nums = rng.sample(range(-20, 21), n)
        i, j = rng.sample(range(n), 2)
        target = nums[i] + nums[j]
        pairs = [(a, b) for a in range(n) for b in range(a + 1, n) if nums[a] + nums[b] == target]
    return [nums, target], [pairs[0][0], pairs[0][1]]


@inputs("two_sum")
def _two_sum_profiler(n: int, rng: random.Random) -> list:
    values = list(range(n))
    rng.shuffle(values)
    return [values, -(sum(values)) - 1]  # absent target: full scan for everyone


@reference("two_sum")
def twosum(nums: list[int], target: int) -> list[int]:
    seen = {}
    for i, x in enumerate(nums):
        need = target - x
        if need in seen:
            return [seen[need], i]
        seen[x] = i
    return []


@measure("two_sum")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
