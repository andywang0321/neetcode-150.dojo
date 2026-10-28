"""QUARANTINED assessment for `sliding-window-maximum` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("sliding-window-maximum")
def _sliding_window_maximum_oracle(nums: list[int], k: int) -> list[int]:
    """Brute force: recompute the maximum of every window from scratch."""
    return [max(nums[i : i + k]) for i in range(len(nums) - k + 1)]


@cases("sliding-window-maximum")
def _sliding_window_maximum_case(n: int, rng: random.Random) -> tuple[list, list]:
    n = max(1, min(n, 12))  # the statement's own constraint: 1 <= nums.length
    if rng.random() < 0.5:
        nums = [rng.randint(-4, 4) for _ in range(n)]  # ties and negatives
    else:
        nums = [rng.randint(-10_000, 10_000) for _ in range(n)]  # the stated range
    k = rng.randint(1, n)  # the statement's own constraint: 1 <= k <= nums.length
    return [nums, k], _sliding_window_maximum_oracle(nums, k)


@inputs("sliding-window-maximum")
def _sliding_window_maximum_profiler(n: int, rng: random.Random) -> list:
    # Strictly decreasing and inside the statement's value range: the monotonic
    # deque never pops from the back, so it fills to k and every index is pushed
    # once and popped once (its amortized worst case), while a heap solution
    # keeps k live entries and pops one stale one per step. A random or
    # increasing array lets the deque stay at size 1 and measures the best case.
    size = max(2, n)
    nums = [max(-10_000, 10_000 - i) for i in range(size)]
    return [nums, max(1, size // 2)]


@reference("sliding-window-maximum")
def _sliding_window_maximum_reference(nums: list[int], k: int) -> list[int]:
    """Monotonic deque of indices -- the intended O(n) time and O(k) space."""
    from collections import deque

    window: deque[int] = deque()  # indices, their values decreasing
    out: list[int] = []
    for i, value in enumerate(nums):
        while window and nums[window[-1]] <= value:
            window.pop()
        window.append(i)
        if window[0] <= i - k:
            window.popleft()  # the front has left the window
        if i >= k - 1:
            out.append(nums[window[0]])
    return out


@measure("sliding-window-maximum")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
