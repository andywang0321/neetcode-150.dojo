"""QUARANTINED assessment for `target-sum` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("target-sum")
def _target_sum_oracle(nums: list[int], target: int) -> int:
    # Brute force over the 2^n expressions the statement defines: every number
    # takes '+' or '-', and the walk counts the assignments whose total is the
    # target. No memo is needed -- the statement caps the length at 20, so the
    # tree has at most 2^20 leaves -- and a literal enumeration of expressions
    # cannot share a mistake with the reference's subset-sum fold. Zeros are
    # counted like every other number: '+0' and '-0' are two distinct expressions
    # that both add nothing, so nums = [0, 0] answers 4 for target 0, never 1.
    # Total on the empty list (the empty expression sums to 0) and on negative
    # values, which it folds in literally.
    def walk(i: int, total: int) -> int:
        if i == len(nums):
            return 1 if total == target else 0
        return walk(i + 1, total + nums[i]) + walk(i + 1, total - nums[i])

    return walk(0, 0)


@cases("target-sum")
def _target_sum_case(n: int, rng: random.Random) -> tuple[list, int]:
    # Four shapes, all inside the statement's constraints (1 <= nums.length <= 20,
    # 0 <= nums[i] <= 1000, 0 <= sum(nums) <= 1000, -1000 <= target <= 1000).
    # sum(nums) <= 1000 is the bound a per-value draw from 0..1000 breaks by an
    # order of magnitude, so every shape that draws values uses 0..1000 // n:
    #   * all zeros -- every expression evaluates to 0, so the count is 2^n for
    #     target 0 and 0 for anything else. This is the shape that catches a
    #     subset-sum implementation which drops zeros: it would answer 1 where
    #     2^n is right;
    #   * a reachable target -- the signs are drawn first and the target is the
    #     total they produce, so the answer is at least 1;
    #   * an impossible target -- strictly above sum(nums), with the values kept
    #     small so the target stays inside +-1000; must answer 0;
    #   * a plain draw, where reachable and impossible targets both occur.
    # expected always comes from the oracle.
    n = max(1, min(n, 12))
    mode = n % 4
    if mode == 0:
        nums = [0] * n
        target = rng.choice([0, rng.randint(1, 1000), -rng.randint(1, 1000)])
    elif mode == 1:
        nums = [rng.randint(0, 1000 // n) for _ in range(n)]
        target = sum(rng.choice([1, -1]) * value for value in nums)
    elif mode == 2:
        nums = [rng.randint(0, 500 // n) for _ in range(n)]
        target = sum(nums) + rng.randint(1, 500)
        if rng.random() < 0.5:
            target = -target
    else:
        nums = [rng.randint(0, 1000 // n) for _ in range(n)]
        target = rng.randint(-1000, 1000)
    return [nums, target], _target_sum_oracle(nums, target)


@inputs("target-sum")
def _target_sum_profiler(n: int, rng: random.Random) -> list:
    # Two statement bounds meet here, and they are why the sizes stop at 20:
    # nums.length <= 20 (probe_max_n -- the default ladder would measure 6400)
    # and sum(nums) <= 1000 (so no shape may draw per value up to 1000).
    #
    # The sum budget is spent to make the reachable totals as wide as the
    # constraints allow: 1, 2, 4, ... 256 covers every total from 0 to 511, and
    # any value added afterwards that is <= (coverage + 1) extends that
    # contiguous coverage by itself, so filling the remaining slots with equal
    # shares keeps coverage contiguous up to the total. That is the difference
    # between a memoized search visiting ~n * s (index, remaining) states and an
    # all-equal array leaving only a sparse arithmetic progression of totals,
    # where the memo collapses to a handful of states and measures nothing.
    #
    # target is 0 for an even total and 1 for an odd one: total + target stays
    # even, so the subset-sum reduction cannot answer from its parity check and
    # must run the whole sweep -- and a small target keeps a pruning memoized
    # search from throwing most of its own states away (target = sum, by
    # contrast, prunes the entire '-' branch immediately).
    n = max(1, min(n, 20))
    values: list[int] = []
    total = 0
    step = 1
    while len(values) < n and total + step + (n - len(values) - 1) <= 1000:
        values.append(step)
        total += step
        step *= 2
    slots = n - len(values)
    if slots:
        share = max(1, (1000 - total) // slots)
        values.extend([share] * slots)
        total += share * slots
    return [values, total % 2]


@reference("target-sum")
def _target_sum_reference(nums: list[int], target: int) -> int:
    # The canonical reduction: if the numbers carrying '+' sum to p, then
    # p - (total - p) = target, so p = (total + target) / 2 and the answer is the
    # number of subsets of nums summing to that p. The fold is the usual
    # one-dimensional subset-sum DP, swept downward so no number is used twice:
    # O(n * p) time, O(p) space, with p <= sum(nums) / 2.
    #
    # Zeros stay in the fold -- unlike a textbook subset-sum input, a zero is not
    # free to drop, because '+0' and '-0' are two different expressions that both
    # add nothing and each should double the count. The downward sweep with value
    # 0 visits range(p, -1, -1) and doubles every entry, which is that doubling.
    #
    # The two early answers are the reduction's own invalid cases: a target
    # beyond +-total (no assignment can reach it) and a half-integer p (no subset
    # can have a fractional sum). Negative values are outside the statement's
    # 0 <= nums[i] and are dropped, so below 0 the oracle -- which walks the
    # literal expression definition -- is the authority and the two may differ;
    # neither the generator nor the profiler input emits one.
    values = [value for value in nums if value >= 0]
    total = sum(values)
    if target > total or target < -total:
        return 0
    if (total + target) % 2:
        return 0
    positive = (total + target) // 2
    ways = [0] * (positive + 1)
    ways[0] = 1
    for value in values:
        for partial in range(positive, value - 1, -1):
            ways[partial] += ways[partial - value]
    return ways[positive]


@measure("target-sum")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
