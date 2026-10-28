"""QUARANTINED assessment for `search-in-rotated-sorted-array` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("search-in-rotated-sorted-array")
def _search_in_rotated_sorted_array_oracle(nums: list[int], target: int) -> int:
    for i, value in enumerate(nums):
        if value == target:
            return i
    return -1


@cases("search-in-rotated-sorted-array")
def _search_in_rotated_sorted_array_case(n: int, rng: random.Random) -> tuple[list, int]:
    n = max(1, min(n, 12))  # the statement's own constraint: 1 <= nums.length
    ascending = sorted(rng.sample(range(-10_000, 10_001), n))  # unique, inside [-10^4, 10^4]
    # k = 0 is the "possibly rotated" reading of the constraints (the parenthetical
    # k >= 1 describes a genuine rotation; the constraint line admits nums sorted).
    k = rng.randrange(n) if n > 1 else 0
    nums = ascending[k:] + ascending[:k]
    if rng.random() < 0.5:
        target = rng.choice(nums)
    else:  # a target that is genuinely absent: the "-1" path, not a lucky hit
        present = set(nums)
        target = rng.randint(-10_000, 10_000)
        while target in present:
            target = target + 1 if target < 10_000 else -10_000
    return [nums, target], _search_in_rotated_sorted_array_oracle(nums, target)


@inputs("search-in-rotated-sorted-array")
def _search_in_rotated_sorted_array_profiler(n: int, rng: random.Random) -> list:
    """Distinct ascending values rotated by n//2, with an ABSENT target inside the
    statement's range: the search must run its loop to exhaustion (no lucky
    midpoint hit) and a linear student scan must read every element.

    This input was omitted at first because a correct, C-accelerated student
    (pivot + bisect) was named "better than the reference — O(1)" in 2 of 8 runs;
    `growth.verdict` now refuses a better-than-declared claim against a
    sub-linear class (v0.14), and the batch verifier re-measured the input on the
    current rule: correct pivot search 6/6 "matches", correct pivot+bisect 5/6
    "matches" and 1/6 "unresolved", a linear scan 6/6 "worse — O(n)" (15-19x)."""
    n = max(1, min(n, 5000))
    values = list(range(n))
    rotated = values[n // 2:] + values[:n // 2]
    return [rotated, 10_000]  # absent, and inside -10^4 <= target <= 10^4


@reference("search-in-rotated-sorted-array")
def _search_in_rotated_sorted_array_reference(nums: list[int], target: int) -> int:
    """Canonical O(log n): one half is always sorted, so the target's side of the
    wrap is decidable from the sorted half alone. Distinct values are guaranteed
    by the statement, so no tie handling is needed."""
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if nums[mid] == target:
            return mid
        if nums[lo] <= nums[mid]:  # the left half is sorted
            if nums[lo] <= target < nums[mid]:
                hi = mid - 1
            else:
                lo = mid + 1
        else:  # the right half is sorted
            if nums[mid] < target <= nums[hi]:
                lo = mid + 1
            else:
                hi = mid - 1
    return -1


@measure("search-in-rotated-sorted-array")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
