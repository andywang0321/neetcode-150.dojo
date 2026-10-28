"""QUARANTINED assessment for `container_with_most_water` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("container_with_most_water")
def _max_area_oracle(height: list[int]) -> int:
    best = 0
    for i in range(len(height)):
        for j in range(i + 1, len(height)):
            best = max(best, min(height[i], height[j]) * (j - i))
    return best


@cases("container_with_most_water")
def _max_area_case(n: int, rng: random.Random) -> tuple[list, int]:
    n = max(2, min(n, 12))
    height = [rng.randint(0, 10) for _ in range(n)]
    return [height], _max_area_oracle(height)


@inputs("container_with_most_water")
def _max_area_profiler(n: int, rng: random.Random) -> list:
    return [[rng.randint(1, 100) for _ in range(n)]]


@reference("container_with_most_water")
def max_area(height: list[int]) -> int:
    left, right = 0, len(height) - 1
    best = 0
    while left < right:
        h = min(height[left], height[right])
        area = h * (right - left)
        if area > best:
            best = area
        if height[left] < height[right]:
            left += 1
        else:
            right -= 1
    return best


@measure("container_with_most_water")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
