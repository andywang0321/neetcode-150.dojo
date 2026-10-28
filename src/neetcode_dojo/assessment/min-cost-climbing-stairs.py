"""QUARANTINED assessment for `min-cost-climbing-stairs` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("min-cost-climbing-stairs")
def _min_cost_climbing_stairs_oracle(cost: list[int]) -> int:
    """Brute force by the statement's own recursion, read from the top down:
    standing on step i costs cost[i] and then commits you to one or two further
    steps, and every index at or past the top costs nothing. best[] holds one entry
    per step -- the recurrence written out in full rather than rolled into two
    variables, and the answer is min(best[0], best[1]), which is the statement's
    own "you can start from index 0 or index 1". It is deliberately not a
    recursion, and that is the probe's constraint: the statement's bound is 1000
    steps, a recursive form of this same recurrence would be ~1000 frames deep
    against CPython's default limit, and the probe measures at the top of that
    range. Total on the empty array and on a one-step array (0 and cost[0]), which
    the statement's 2 <= cost.length excludes and the generator never emits."""
    n = len(cost)
    best = [0] * (n + 2)  # best[i] = cheapest way from step i up to the top
    for i in range(n - 1, -1, -1):
        best[i] = cost[i] + min(best[i + 1], best[i + 2])
    return min(best[0], best[1])


@cases("min-cost-climbing-stairs")
def _min_cost_climbing_stairs_case(n: int, rng: random.Random) -> tuple[list, int]:
    # The caller sends 0..12; the statement's own floor is 2, so 0 and 1 become 2
    # -- an empty or single-step staircase is outside the problem and inventing an
    # answer for it would be inventing one. A third of the draws use costs 0..3
    # (zeros, ties and near-ties: the uniform range below essentially never draws a
    # zero at all, and "a free step" is exactly what visible test 4 pins), the rest
    # use the statement's full 0 <= cost[i] <= 999.
    n = max(2, min(n, 12))
    if rng.random() < 1 / 3:
        cost = [rng.randint(0, 3) for _ in range(n)]
    else:
        cost = [rng.randint(0, 999) for _ in range(n)]
    return [cost], _min_cost_climbing_stairs_oracle(cost)


@inputs("min-cost-climbing-stairs")
def _min_cost_climbing_stairs_profiler(n: int, rng: random.Random) -> list:
    # Length n, capped at the statement's own 1000 steps by probe_max_n and floored
    # at its own 2. Neither implementation has a branch on cost[i] -- both DP passes
    # always touch all n steps -- so no value choice can make either side
    # early-exit, and the shape's only job is to be the full-length input. The
    # values are where the care went, and they are measured rather than asserted:
    # every fifth step costs the statement's maximum 999 and the rest cost 1, so
    # the answer is not constant in n (8, 18, 37, 74, 149, 299, 599 at this
    # problem's ladder rungs) and all four shortcut answers I checked differ from
    # the optimum at EVERY rung -- paying every other step from index 0 and from
    # index 1, and the "always step to the cheaper of the next two stairs" greedy
    # from either start (each checked against the real DP). A period of 3 was my
    # first choice and it failed that last test: the greedy matched the optimum at
    # six of the seven rungs. An all-equal array, the obvious alternative, is
    # matched by the from-index-0 shortcut at every even length. Values stay
    # inside 0 <= cost[i] <= 999.
    n = max(2, min(n, 1000))
    return [[999 if i % 5 == 0 else 1 for i in range(n)]]


@reference("min-cost-climbing-stairs")
def _min_cost_climbing_stairs_reference(cost: list[int]) -> int:
    # The canonical forward rolling pair: dp[i] = cost[i] + min(dp[i - 1],
    # dp[i - 2]) with both seeds at 0, which is the statement's "you can start from
    # index 0, or the step with index 1" (starting is free; only the steps you
    # stand on are paid for). One pass, two live values, O(n) time and O(1) extra
    # space -- no array and no recursion.
    prev2 = prev1 = 0
    for step in cost:
        prev2, prev1 = prev1, min(prev2, prev1) + step
    return min(prev2, prev1)


@measure("min-cost-climbing-stairs")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
