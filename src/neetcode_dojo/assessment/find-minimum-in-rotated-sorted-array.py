"""QUARANTINED assessment for `find-minimum-in-rotated-sorted-array` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("find-minimum-in-rotated-sorted-array")
def _find_minimum_in_rotated_sorted_array_oracle(nums: list[int]) -> int | None:
    best = None
    for value in nums:
        if best is None or value < best:
            best = value
    return best


@cases("find-minimum-in-rotated-sorted-array")
def _find_minimum_in_rotated_sorted_array_case(n: int, rng: random.Random) -> tuple[list, int]:
    n = max(1, min(n, 12))  # the statement's own constraint: 1 <= n
    ascending = sorted(rng.sample(range(-5_000, 5_001), n))  # unique, inside [-5000, 5000]
    # k = 0 is the "rotated n times" case the statement allows explicitly (its
    # example 3, [11,13,15,17], is exactly that).
    k = rng.randrange(n)
    nums = ascending[k:] + ascending[:k]
    return [nums], _find_minimum_in_rotated_sorted_array_oracle(nums)


@inputs("find-minimum-in-rotated-sorted-array")
def _find_minimum_in_rotated_sorted_array_profiler(n: int, rng: random.Random) -> list:
    """Ascending distinct values rotated LEFT by one: the single descent sits at
    the very end, so the reference's loop runs to exhaustion and no linear
    shortcut (min(nums), or a scan stopping at the first inversion) can exit
    early on anything but the last comparison.

    Omitted at first for the sibling's reason (a false "better — O(1)" for a
    correct C-accelerated student); the sub-linear guard in `growth.verdict`
    removes that risk, and the batch verifier measured the input on the current
    rule: the verifier measured correct 3/3 "matches" (1.02-1.27x), a
    C-accelerated keyed variant 1/3 "matches" and 2/3 "unresolved", and min(nums)
    1/3 "worse — O(n)" (14.5x) plus 2/3 "unresolved" — the weak payoff is the
    reason this input is the pair's marginal one."""
    n = max(1, min(n, 5000))
    values = list(range(n))
    return [values[1:] + values[:1]]


@reference("find-minimum-in-rotated-sorted-array")
def _find_minimum_in_rotated_sorted_array_reference(nums: list[int]) -> int | None:
    """Canonical O(log n): compare the middle with the last element — if it is
    larger, the minimum is to its right, otherwise it is at or left of it."""
    if not nums:
        return None
    lo, hi = 0, len(nums) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] > nums[hi]:
            lo = mid + 1
        else:
            hi = mid
    return nums[lo]


@measure("find-minimum-in-rotated-sorted-array")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
