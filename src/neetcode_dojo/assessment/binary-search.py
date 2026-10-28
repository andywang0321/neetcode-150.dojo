"""QUARANTINED assessment for `binary-search` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


def _binary_search_absent_target(nums: list[int], rng: random.Random) -> int:
    """A target inside the statement's own range that is not in ``nums``."""
    present = set(nums)
    for _ in range(64):
        candidate = rng.randint(-9_999, 9_999)
        if candidate not in present:
            return candidate
    # Unreachable with <= 12 values drawn from 19_999, kept so this is total.
    return next(v for v in range(-9_999, 10_000) if v not in present)


@oracle("binary-search")
def _binary_search_oracle(nums: list[int], target: int) -> int:
    # Brute force: read the array left to right and stop at the first match.
    # The statement promises unique values, so the first match is the only one,
    # and a full pass without a match is the -1.
    for i, value in enumerate(nums):
        if value == target:
            return i
    return -1


@cases("binary-search")
def _binary_search_case(n: int, rng: random.Random) -> tuple[list, int]:
    n = max(1, min(n, 12))  # the statement's floor: nums.length >= 1
    # Ascending and unique (the statement's own two promises), every value
    # strictly inside -10^4 < nums[i] < 10^4.
    nums = sorted(rng.sample(range(-9_999, 10_000), n))
    if rng.random() < 0.5:
        target = rng.choice(nums)  # a hit, the shape both examples have
    else:
        target = _binary_search_absent_target(nums, rng)  # a miss
    return [nums, target], _binary_search_oracle(nums, target)


@inputs("binary-search")
def _binary_search_profiler(n: int, rng: random.Random) -> list:
    # Both ways this input could let something finish early are closed. The
    # target is ABSENT, so a binary search cannot stop at a lucky midpoint but
    # must run its loop to exhaustion; it sits in the gap just below the LARGEST
    # element, a deepest gap for this midpoint scheme (one round deeper than a
    # mid-array miss at every size I measured); and it is strictly inside the
    # value span, so the `target > nums[-1]` short-circuit a linear scan might
    # use cannot fire and a linear scan must read all n. Values are all odd and
    # the target is even (the miss is structural, not luck), and every value and
    # the target are strictly inside the statement's -10^4 < nums[i], target <
    # 10^4 range. n is capped at the statement's own 10^4 (the probe's ladder
    # stops at 6400) and floored at 2 so the top gap exists.
    n = max(2, min(n, 10_000))
    nums = [-9_999 + 2 * i for i in range(n)]
    target = nums[-2] + 1
    return [nums, target]


@reference("binary-search")
def _binary_search_reference(nums: list[int], target: int) -> int:
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if nums[mid] == target:
            return mid
        if nums[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1


@measure("binary-search")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
