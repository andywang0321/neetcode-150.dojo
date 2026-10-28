"""QUARANTINED assessment for `subsets` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, oracle, reference


@oracle("subsets")
def _subsets_oracle(nums: list[int]) -> list[list[int]]:
    # Brute force by construction rather than by bit tricks: start from the empty
    # subset and let every value double the collection — every subset built so far
    # without the value, then the same subset with it. Correct by induction (a
    # subset either contains this value or it does not), and it emits the
    # statement's own example order, which is the canonical form of a set answer.
    out: list[list[int]] = [[]]
    for value in nums:
        out.extend([subset + [value] for subset in out])
    return out


@cases("subsets")
def _subsets_case(n: int, rng: random.Random) -> tuple[list, list, dict]:
    # The statement's constraints, upheld exactly: 1 <= nums.length <= 10,
    # -10 <= nums[i] <= 10, and "All the numbers of nums are unique" — n distinct
    # values drawn from the statement's own range. Distinctness is what keeps the
    # answer a *set*: with a repeated value the same subset of values would be
    # reachable as two different subsets and equality judging would be ambiguous
    # (a correct solution choosing the other copy would be false-failed). The cap
    # of 10 is what keeps the answer real but small: 1024 subsets at the top.
    n = max(1, min(n, 10))
    nums = rng.sample(range(-10, 11), n)
    if rng.random() < 0.5:
        nums.sort()  # the statement's examples are ascending; an unordered input is legal too
    return [nums], _subsets_oracle(nums), {"compare": "sorted"}


@reference("subsets")
def _subsets_reference(nums: list[int]) -> list[list[int]]:
    """Canonical bitmask enumeration: subset k is the set of positions where bit i
    of k is set, so all 2^n subsets come out of one loop with no recursion —
    O(n * 2^n) time (each of the 2^n masks scans the n values) and O(n) auxiliary
    space beyond the answer itself.

    The order is the statement's own example order ([], [1], [2], [1,2], ...);
    every case carries "compare": "sorted", so any order is legal and this is
    only the canonical form."""
    n = len(nums)
    out: list[list[int]] = []
    for mask in range(1 << n):
        out.append([nums[i] for i in range(n) if mask >> i & 1])
    return out
