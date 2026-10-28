"""QUARANTINED assessment for `missing-number` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("missing-number")
def _missing_number_oracle(nums: list[int]) -> int:
    # Brute force, read straight off the statement's own sentence: walk the range
    # 0..n and return the first value the array does not contain. Total for any
    # input at all (including the empty list, which the statement's 1 <= n
    # excludes); the final return is unreachable while the input really is n
    # distinct values drawn from 0..n, and is kept only so this is total.
    for candidate in range(len(nums) + 1):
        if candidate not in nums:
            return candidate
    return len(nums) + 1


@cases("missing-number")
def _missing_number_case(n: int, rng: random.Random) -> tuple[list, int]:
    size = max(1, min(n, 12))  # the statement's own floor: n = nums.length >= 1
    candidates = list(range(size + 1))  # 0..n inclusive: n + 1 values, n present
    candidates.pop(rng.randrange(size + 1))  # exactly one of them goes missing
    rng.shuffle(candidates)
    return [candidates], _missing_number_oracle(candidates)


@inputs("missing-number")
def _missing_number_profiler(n: int, rng: random.Random) -> list:
    # The missing value is n itself, the LAST candidate of the range 0..n, and
    # the n present values are a shuffled 0..n-1 — inside 0 <= nums[i] <= n and
    # with n == nums.length, which is the statement's own shape. Two early exits
    # are closed by that choice: a solution that scans candidate values in order
    # (the brute-force shape) has to reach the very last one before it can
    # answer, and a position-based shortcut (`nums[i] != i` after an in-place
    # sort or cycle walk) cannot land on a lucky index, because the shuffle
    # destroys every positional pattern while the answer stays fixed at n.
    # Neither the reference (one XOR per element) nor the oracle can stop early.
    n = max(1, min(n, 10_000))  # the statement's own bound: 1 <= n <= 10^4
    values = list(range(n))
    rng.shuffle(values)
    return [values]


@reference("missing-number")
def _missing_number_reference(nums: list[int]) -> int:
    # XOR of every index and every value: each value that is present cancels
    # against its own index, so what survives is the missing one. Seeding with
    # len(nums) is what puts the n-th candidate into the fold (the array holds
    # the other n indices, never n itself when the answer is n). One pass, one
    # register: O(n) time and O(1) space, the statement's follow-up. Standalone
    # by design — the probe runs this in its own subprocess.
    missing = len(nums)
    for index, value in enumerate(nums):
        missing ^= index ^ value
    return missing


@measure("missing-number")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
