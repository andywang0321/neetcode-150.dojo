"""QUARANTINED assessment for `three_sum` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("three_sum")
def _three_sum_oracle(nums: list[int]) -> list[list[int]]:
    seen: set[tuple[int, int, int]] = set()
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            for k in range(j + 1, len(nums)):
                if nums[i] + nums[j] + nums[k] == 0:
                    seen.add(tuple(sorted((nums[i], nums[j], nums[k]))))
    return [list(t) for t in sorted(seen)]


@cases("three_sum")
def _three_sum_case(n: int, rng: random.Random) -> tuple[list, list, dict]:
    n = max(3, min(n, 12))
    nums = [rng.randint(-8, 8) for _ in range(n)]
    if rng.random() < 0.6:
        a = rng.randint(-6, 6)
        b = rng.randint(-6, 6)
        nums.extend([a, b, -(a + b)])  # embed a guaranteed zero-sum triple
        rng.shuffle(nums)
    return [nums], _three_sum_oracle(nums), {"compare": "sorted"}


@inputs("three_sum")
def _three_sum_profiler(n: int, rng: random.Random) -> list:
    return [[rng.randint(-20, 20) for _ in range(n)]]


@reference("three_sum")
def three_sum(nums: list[int]) -> list[list[int]]:
    nums.sort()
    n = len(nums)
    res = []
    for i in range(n - 2):
        if nums[i] > 0:
            break
        if i > 0 and nums[i] == nums[i - 1]:
            continue
        lo, hi = i + 1, n - 1
        target = -nums[i]
        while lo < hi:
            s = nums[lo] + nums[hi]
            if s < target:
                lo += 1
            elif s > target:
                hi -= 1
            else:
                res.append([nums[i], nums[lo], nums[hi]])
                lo += 1
                hi -= 1
                while lo < hi and nums[lo] == nums[lo - 1]:
                    lo += 1
                while lo < hi and nums[hi] == nums[hi + 1]:
                    hi -= 1
    return res


@measure("three_sum")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
