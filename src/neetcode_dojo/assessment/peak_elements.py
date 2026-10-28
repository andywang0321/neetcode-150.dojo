"""QUARANTINED assessment for `peak_elements` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, checker, oracle, reference


@oracle("peak_elements")
def _find_a_peak_oracle(nums: list[int]) -> int:
    for i in range(len(nums) - 1):
        if nums[i] > nums[i + 1]:
            return i
    return len(nums) - 1


@cases("peak_elements")
def _find_a_peak_case(n: int, rng: random.Random) -> tuple[list, int]:
    n = max(1, min(n, 12))
    # Bitonic arrays: strictly increasing then strictly decreasing, exactly
    # one peak — "leftmost peak" is unambiguous for any correct answer.
    peak_idx = rng.randrange(n)
    left: list[int] = []
    if peak_idx > 0:
        left = [rng.randint(1, 20)]
        for _ in range(peak_idx - 1):
            left.append(left[-1] + rng.randint(1, 10))
    peak_value = (left[-1] if left else rng.randint(1, 20)) + rng.randint(1, 10)
    right: list[int] = []
    if peak_idx < n - 1:
        right = [peak_value - rng.randint(1, 10)]
        for _ in range(n - peak_idx - 2):
            right.append(right[-1] - rng.randint(1, 10))
    return [left + [peak_value] + right], peak_idx


@reference("peak_elements")
def find_a_peak(nums: list[int]) -> int:
    lo, hi = 0, len(nums) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] < nums[mid + 1]:
            lo = mid + 1
        else:
            hi = mid
    return lo


@checker("is_peak")
def _is_peak(module, got, args) -> bool:
    """got is the index of any peak in args[0] (strictly greater than its
    existing neighbors; endpoints beat their single neighbor)."""
    nums = args[0]
    if not isinstance(got, int) or not 0 <= got < len(nums):
        return False
    left = nums[got - 1] if got > 0 else float("-inf")
    right = nums[got + 1] if got < len(nums) - 1 else float("-inf")
    return nums[got] > left and nums[got] > right
