"""QUARANTINED assessment for `two_sum_2` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("two_sum_2")
def _two_sum_2_oracle(numbers: list[int], target: int) -> list[int]:
    for i in range(len(numbers)):
        for j in range(i + 1, len(numbers)):
            if numbers[i] + numbers[j] == target:
                return [i + 1, j + 1]
    return []


@cases("two_sum_2")
def _two_sum_2_case(n: int, rng: random.Random) -> tuple[list, list]:
    n = max(2, min(n, 12))
    numbers = sorted(rng.sample(range(-10, 11), n))
    i, j = rng.sample(range(n), 2)
    target = numbers[i] + numbers[j]
    pairs = [(a, b) for a in range(n) for b in range(a + 1, n) if numbers[a] + numbers[b] == target]
    while len(pairs) != 1:  # the prompt guarantees exactly one valid pair
        numbers = sorted(rng.sample(range(-10, 11), n))
        i, j = rng.sample(range(n), 2)
        target = numbers[i] + numbers[j]
        pairs = [(a, b) for a in range(n) for b in range(a + 1, n) if numbers[a] + numbers[b] == target]
    return [numbers, target], [pairs[0][0] + 1, pairs[0][1] + 1]


@inputs("two_sum_2")
def _two_sum_2_profiler(n: int, rng: random.Random) -> list:
    return [list(range(1, n + 1)), 3 * n + 5]  # absent target: full scan


@reference("two_sum_2")
def two_sum_2(numbers: list[int], target: int) -> list[int]:
    left, right = 0, len(numbers) - 1
    while left < right:
        s = numbers[left] + numbers[right]
        if s == target:
            return [left + 1, right + 1]
        elif s < target:
            left += 1
        else:
            right -= 1
    return []


@measure("two_sum_2")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
