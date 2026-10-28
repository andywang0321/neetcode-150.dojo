"""QUARANTINED assessment for `largest_rectangle_in_histogram` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("largest_rectangle_in_histogram")
def _largest_rectangle_oracle(heights: list[int]) -> int:
    best = 0
    for i in range(len(heights)):
        low = heights[i]
        for j in range(i, len(heights)):
            low = min(low, heights[j])
            best = max(best, low * (j - i + 1))
    return best


@cases("largest_rectangle_in_histogram")
def _largest_rectangle_case(n: int, rng: random.Random) -> tuple[list, int]:
    n = max(0, min(n, 12))
    heights = [rng.randint(0, 10) for _ in range(n)]
    return [heights], _largest_rectangle_oracle(heights)


@inputs("largest_rectangle_in_histogram")
def _largest_rectangle_profiler(n: int, rng: random.Random) -> list:
    return [list(range(1, n + 1))]  # increasing bars: no pops until the end


@reference("largest_rectangle_in_histogram")
def largest_rectangle(heights: list[int]) -> int:
    stack = []
    best = 0
    for i, h in enumerate(heights):
        start = i
        while stack and stack[-1][1] > h:
            idx, height = stack.pop()
            best = max(best, height * (i - idx))
            start = idx
        stack.append((start, h))
    n = len(heights)
    for idx, height in stack:
        best = max(best, height * (n - idx))
    return best


@measure("largest_rectangle_in_histogram")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
