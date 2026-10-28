"""QUARANTINED assessment for `house-robber` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("house-robber")
def _house_robber_oracle(nums: list[int]) -> int:
    """Brute force by the statement's own choice: at house i the robber either
    skips it, or takes it and is then forced to skip i + 1 -- so the best from i is
    max(best(i + 1), nums[i] + best(i + 2)). Memoized on i, which is what keeps the
    oracle runnable at the statement's own 100-house bound: the unmemoized tree makes about
    1.9e21 calls at the statement's own 100 houses (counted with a DP over the
    call tree -- only 102 of those calls are distinct states) and
    flow._oracle_confirms runs the oracle IN PROCESS at a disputed size. Total on the empty list (no houses, no money), which the statement's
    length >= 1 excludes and the generator never emits."""
    n = len(nums)
    memo: dict[int, int] = {}

    def best(i: int) -> int:
        if i >= n:
            return 0
        if i in memo:
            return memo[i]
        memo[i] = max(best(i + 1), nums[i] + best(i + 2))
        return memo[i]

    return best(0)


@cases("house-robber")
def _house_robber_case(n: int, rng: random.Random) -> tuple[list, int]:
    # n is clamped into [1, 12]: the statement's floor is 1 house, so the caller's
    # 0 becomes a single house rather than an empty street. A third of the draws
    # use money 0..3 (zeros, ties, and the all-important "a house worth nothing
    # still blocks its neighbours" case, which the uniform range below essentially
    # never produces); the rest use the statement's full 0 <= nums[i] <= 400.
    n = max(1, min(n, 12))
    if rng.random() < 1 / 3:
        nums = [rng.randint(0, 3) for _ in range(n)]
    else:
        nums = [rng.randint(0, 400) for _ in range(n)]
    return [nums], _house_robber_oracle(nums)


@inputs("house-robber")
def _house_robber_profiler(n: int, rng: random.Random) -> list:
    # The statement's own example-1 pattern, repeated to length n: 1, 2, 3, 1,
    # 1, 2, 3, 1, ... No implementation here can early-exit at any value -- the
    # rolling DP and the memoized oracle both walk all n houses -- so the values'
    # job is the digest, and this pattern does it in a way an all-equal array does
    # not: measured, the "take the larger of each adjacent pair" greedy that this
    # problem is famous for answers 5, 7, 15, 31, 62, 125 against the optimum's
    # 4, 6, 12, 25, 50, 100 at the rungs n = 3, 6, 12, 25, 50, 100, while an
    # all-400 array lets that same greedy agree exactly (2400 at n = 12, 20000 at
    # n = 100). Values are 1..3, inside 0 <= nums[i] <= 400, and n is capped at the
    # statement's own 100 houses by probe_max_n. At n = 1 the two coincide (there
    # is no pair to choose between), so the smallest rung's digest is weak by
    # construction -- a stub returning 1 agrees there too, which is the accepted
    # weakness documented in the notes.
    n = max(1, min(n, 100))
    return [[(1, 2, 3, 1)[i % 4] for i in range(n)]]


@reference("house-robber")
def _house_robber_reference(nums: list[int]) -> int:
    # The canonical rolling pair: prev2 and prev1 are the best take for the two
    # houses before i, and house i either extends prev2 (rob it) or keeps prev1
    # (skip it). One pass, two live values, no array and no recursion -- O(n) time
    # and O(1) extra space, which is the space-optimized target. Total on the
    # empty list (0), which the statement's length >= 1 excludes.
    prev2 = prev1 = 0
    for money in nums:
        prev2, prev1 = prev1, max(prev1, prev2 + money)
    return prev1


@measure("house-robber")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
