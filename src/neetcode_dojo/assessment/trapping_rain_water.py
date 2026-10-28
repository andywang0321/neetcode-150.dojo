"""QUARANTINED assessment for `trapping_rain_water` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("trapping_rain_water")
def _trap_oracle(height: list[int]) -> int:
    total = 0
    for i in range(len(height)):
        left = max(height[: i + 1])
        right = max(height[i:])
        total += min(left, right) - height[i]
    return total


@cases("trapping_rain_water")
def _trap_case(n: int, rng: random.Random) -> tuple[list, int]:
    n = max(0, min(n, 12))
    height = [rng.randint(0, 8) for _ in range(n)]
    return [height], _trap_oracle(height)


@inputs("trapping_rain_water")
def _trap_profiler(n: int, rng: random.Random) -> list:
    return [[rng.randint(0, n) for _ in range(n)]]


@reference("trapping_rain_water")
def trap(height: list[int]) -> int:
    n = len(height)
    if n == 0:
        return 0
    left_max = [0] * n
    right_max = [0] * n
    left_max[0] = height[0]
    for i in range(1, n):
        left_max[i] = max(left_max[i - 1], height[i])
    right_max[n - 1] = height[n - 1]
    for i in range(n - 2, -1, -1):
        right_max[i] = max(right_max[i + 1], height[i])
    total = 0
    for i in range(n):
        total += min(left_max[i], right_max[i]) - height[i]
    return total


@measure("trapping_rain_water")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
