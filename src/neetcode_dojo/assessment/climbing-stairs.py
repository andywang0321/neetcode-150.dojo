"""QUARANTINED assessment for `climbing-stairs` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("climbing-stairs")
def _climbing_stairs_oracle(n: int) -> int:
    """Brute force by the statement's own definition: the last move was a single
    step (leaving n - 1) or a double step (leaving n - 2), so the count is the sum
    of the two smaller staircases. The memo is the one concession to the probe --
    the unmemoized recurrence makes about 3.7e9 calls at the statement's own
    maximum of 45 (counted with a DP over the call tree; the growth is ~1.62^n,
    so it is hopeless well below the bound) and flow._oracle_confirms runs the
    oracle IN PROCESS at whatever size a student and the reference disagree at,
    so an exponential oracle could hang a live session instead of reporting a
    finding. Total on
    n <= 0: there is exactly one way to climb nothing."""
    memo = {0: 1, 1: 1}

    def ways(k: int) -> int:
        if k < 0:
            return 0
        if k in memo:
            return memo[k]
        memo[k] = ways(k - 1) + ways(k - 2)
        return memo[k]

    return ways(n)


@cases("climbing-stairs")
def _climbing_stairs_case(n: int, rng: random.Random) -> tuple[list, int]:
    # A scalar input has no shape to randomize: the case size IS the staircase
    # (the counting-bits convention), clamped into the statement's constraints and
    # kept small on purpose -- the judge's stdout budget carries one case per draw,
    # and 1..12 already drives both halves of the recurrence. Scale belongs to the
    # profiler input, and the two ends of the stated range are pinned by visible
    # tests 3 and 4.
    n = max(1, min(n, 12))  # the statement's floor: n >= 1
    return [n], _climbing_stairs_oracle(n)


@inputs("climbing-stairs")
def _climbing_stairs_profiler(n: int, rng: random.Random) -> list:
    # The input is the staircase length itself, capped at the statement's 45 by
    # probe_max_n and floored at its 1. The floor is not cosmetic: ladder(45) is
    # [0, 1, 2, 5, 11, 22, 45], so the probe does ask for n = 0, which the
    # statement excludes and where the two legitimate conventions (0 ways, or 1
    # way to climb nothing) disagree -- the floor keeps both of those rungs on
    # n = 1 rather than inviting a disagreement the problem never defines. Neither
    # side can early-exit above it: the reference's loop runs exactly n - 1 times
    # whatever n is, and the extra rungs the floor collapses are the two smallest.
    return [max(1, min(n, 45))]


@reference("climbing-stairs")
def _climbing_stairs_reference(n: int) -> int:
    # The canonical rolling pair: ways(0) = ways(1) = 1 and
    # ways(k) = ways(k - 1) + ways(k - 2), so n - 1 additions reach ways(n) with
    # two live values and no array -- O(n) time, O(1) extra space. The n <= 0
    # branch returns 1 (the empty climb), the same convention the oracle uses; the
    # generator's and the profiler input's floors keep both of them on n >= 1.
    if n <= 0:
        return 1
    prev, curr = 1, 1
    for _ in range(n - 1):
        prev, curr = curr, prev + curr
    return curr


@measure("climbing-stairs")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
