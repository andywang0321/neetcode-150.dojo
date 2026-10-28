"""QUARANTINED assessment for `partition-equal-subset-sum` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("partition-equal-subset-sum")
def _partition_equal_subset_sum_oracle(nums: list[int]) -> bool:
    # Brute force over the reachable sums: start from {0} and let every element
    # add itself to each sum reachable WITHOUT it -- the comprehension is built
    # from the previous set, so no element can be used twice, and what is left in
    # the set is exactly the set of subset sums. The answer is whether half the
    # total is one of them. Different data structure and different order from the
    # reference's downward sweep over a flag array, and total on the empty list
    # (the two empty subsets match at 0, which is what the reference answers too;
    # the statement's length >= 1 excludes that input). A value <= 0 is skipped on
    # both sides: the statement's values are >= 1, so that is off-constraint, and
    # skipping keeps the two implementations agreeing there as well.
    usable = [value for value in nums if value > 0]
    total = sum(usable)
    if total % 2:
        return False
    reachable = {0}
    for value in usable:
        reachable |= {partial + value for partial in reachable}
    return total // 2 in reachable


@cases("partition-equal-subset-sum")
def _partition_equal_subset_sum_case(n: int, rng: random.Random) -> tuple[list, bool]:
    # Four shapes, all inside the statement's constraints (1 <= nums.length <= 200,
    # 1 <= nums[i] <= 100): an odd total, which the parity rule alone settles (the
    # statement's own example 2 has that shape), a constructed split (two identical
    # halves, so a True answer exists by construction rather than by luck), all
    # equal values (the shape the profiler input uses at scale), and a plain draw.
    # The expected value always comes from the oracle.
    n = max(1, min(n, 12))
    mode = n % 4
    if mode == 0:
        values = [rng.randint(1, 100) for _ in range(n)]
        if sum(values) % 2 == 0:
            index = rng.randrange(n)
            values[index] = values[index] + 1 if values[index] < 100 else 99
    elif mode == 1:
        half = [rng.randint(1, 50) for _ in range(n // 2)]
        values = half + half + ([rng.randint(1, 50)] if n % 2 else [])
    elif mode == 2:
        values = [rng.choice([2, 7, 100])] * n
    else:
        values = [rng.randint(1, 100) for _ in range(n)]
    return [values], _partition_equal_subset_sum_oracle(values)


@inputs("partition-equal-subset-sum")
def _partition_equal_subset_sum_profiler(n: int, rng: random.Random) -> list:
    # n - 1 copies of 100 plus one 98, clamped to the statement's own length bound
    # (200, hence probe_max_n). Three properties, in order of importance.
    # (1) The values respect the statement's element bound (1 <= nums[i] <= 100).
    #     That bound is what keeps a correct DP measuring at its own class: the
    #     target is half the total, so the total being at most 100 * n is what
    #     makes the intended n * target sweep quadratic in n rather than something
    #     worse (the v0.12 products_of_array_except_self lesson: values outside
    #     the problem's own guarantee made a correct O(n) solution measure as
    #     superlinear).
    # (2) The total (100 * n - 2) is EVEN at every size, so the parity shortcut
    #     cannot answer before any work is done, and the target (50 * n - 1) is
    #     UNREACHABLE at every size: subset sums are 100 * a + 98 * b, i.e. 0 or 98
    #     modulo 100, while the target is 49 modulo 100 for odd n and 99 for even
    #     n. So the answer is False everywhere on the ladder and nothing can
    #     early-exit on a hit -- which is the point, because a True instance lets a
    #     take-first search reach the target in O(n) steps and measure like the
    #     reference while being quadratic in the worst case.
    # (3) The total is as large as the constraints allow at this size, so the
    #     target (half of it) is as large as it can be and the DP's flag array is
    #     at its widest.
    size = max(1, min(int(n), 200))
    return [[100] * (size - 1) + [98]]


@reference("partition-equal-subset-sum")
def _partition_equal_subset_sum_reference(nums: list[int]) -> bool:
    # The canonical one-dimensional subset-sum DP: reachable[s] is True when some
    # subset of the values seen so far sums to s. Every value is visited for s
    # running DOWNWARD from the target, which is what keeps each value usable at
    # most once (an ascending sweep would let one value be counted repeatedly -- the
    # unbound-knapsack mistake). O(n * target) time and O(target) space, with the
    # flags in a bytearray so the space the probe measures is the DP's own state
    # rather than a list of boxed ints. A value <= 0 is skipped: the statement's
    # values are >= 1, and skipping keeps this side in step with the oracle
    # off-constraint. Total on the empty list and on a zero target, where
    # reachable[0] is already True.
    usable = [value for value in nums if value > 0]
    total = sum(usable)
    if total % 2:
        return False
    target = total // 2
    reachable = bytearray(target + 1)
    reachable[0] = 1
    for value in usable:
        for partial in range(target, value - 1, -1):
            if reachable[partial - value]:
                reachable[partial] = 1
    return bool(reachable[target])


@measure("partition-equal-subset-sum")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
