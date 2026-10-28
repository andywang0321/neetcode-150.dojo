"""QUARANTINED assessment for `kth-largest-element-in-an-array` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("kth-largest-element-in-an-array")
def _kth_largest_element_in_an_array_oracle(nums: list[int], k: int) -> int:
    """Brute force: sort the whole array and read the k-th from the top. The
    statement's constraint is 1 <= k <= nums.length, so an empty array is out of
    contract; this stays total on one instead of raising."""
    if not nums:
        return None
    return sorted(nums)[len(nums) - k]


@cases("kth-largest-element-in-an-array")
def _kth_largest_element_in_an_array_case(n: int, rng: random.Random) -> tuple[list, int]:
    n = max(1, min(n, 12))  # the statement's own constraint: 1 <= k <= nums.length
    # A small span is what makes "the k-th largest in sorted order, not the k-th
    # distinct element" bite: with 3 or 40 distinct values the answer is a value
    # that occurs several times, where an index-into-sorted-set solution is wrong.
    span = rng.choice([3, 40, 20_001])
    nums = [rng.randint(-10_000, -10_000 + span - 1) for _ in range(n)]
    if rng.random() < 0.3:  # the statement's own bounds, exactly
        nums[rng.randrange(n)] = rng.choice([-10_000, 10_000])
    k = rng.randint(1, n)
    return [nums, k], _kth_largest_element_in_an_array_oracle(nums, k)


@inputs("kth-largest-element-in-an-array")
def _kth_largest_element_in_an_array_profiler(n: int, rng: random.Random) -> list:
    # Values across the statement's full range (-10^4..10^4) in a random order,
    # with a middle rank: neither the "k == 1" (the maximum) nor the "k == n"
    # (the minimum) shortcut is available, so a size-k heap pays an O(log k) push
    # for every element and a quickselect partitions the live range at every
    # level. Nothing early-exits and nothing is pre-sorted.
    nums = [rng.randint(-10_000, 10_000) for _ in range(max(1, n))]
    return [nums, max(1, len(nums) // 2)]


@reference("kth-largest-element-in-an-array")
def _kth_largest_element_in_an_array_reference(nums: list[int], k: int) -> int:
    """Canonical quickselect — the statement's own "without sorting". Partition
    the live range around a median-of-three pivot into <, == and > bands, then
    walk into the band that holds the k-th largest: O(n) on average, in place
    (O(1) extra space). The three-way partition also keeps an all-equal array
    linear, where a two-way partition degrades to O(n^2), and the pivot rule is
    deterministic (no clock, no rng), so the probe's baseline is reproducible.
    """
    target = len(nums) - k  # its index in ascending order
    lo, hi = 0, len(nums) - 1
    while True:
        pivot = sorted((nums[lo], nums[(lo + hi) // 2], nums[hi]))[1]
        lt, i, gt = lo, lo, hi
        while i <= gt:
            if nums[i] < pivot:
                nums[lt], nums[i] = nums[i], nums[lt]
                lt += 1
                i += 1
            elif nums[i] > pivot:
                nums[gt], nums[i] = nums[i], nums[gt]
                gt -= 1
            else:
                i += 1
        # nums[lt:gt + 1] is exactly the pivot's band, and target never leaves
        # [lo, hi], so one of the three branches always answers while the other
        # two strictly shrink the range.
        if target < lt:
            hi = lt - 1
        elif target > gt:
            lo = gt + 1
        else:
            return pivot


@measure("kth-largest-element-in-an-array")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
