"""QUARANTINED assessment for `house-robber-ii` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("house-robber-ii")
def _house_robber_ii_oracle(nums: list[int]) -> int:
    """Brute force over the take/skip tree, with the circle carried as STATE: the
    walk remembers whether the previous house was taken and whether HOUSE 0 was
    taken, and the only place the circle bites is the last house -- taking it is
    illegal exactly when house 0 was taken. The unmemoized tree branches twice at
    every house, so it is exponential; memoizing on (i, prev_taken, first_taken)
    cuts it to at most 4n states and ~8n calls (depth n <= 100, far inside the
    recursion limit, so flow._oracle_confirms can run it at a disputed size). This deliberately does NOT use the two-line split -- that is
    the insight the problem teaches and what the reference implements, so the
    differential is a real one. Total on the empty list and on a single house."""
    n = len(nums)
    memo: dict[tuple[int, bool, bool], int] = {}

    def best(i: int, prev_taken: bool, first_taken: bool) -> int:
        if i == n:
            return 0
        key = (i, prev_taken, first_taken)
        if key in memo:
            return memo[key]
        out = best(i + 1, False, first_taken)  # skip house i
        if not (prev_taken or (i == n - 1 and first_taken)):
            out = max(out, nums[i] + best(i + 1, True, first_taken or i == 0))
        memo[key] = out
        return out

    return best(0, False, False)


@cases("house-robber-ii")
def _house_robber_ii_case(n: int, rng: random.Random) -> tuple[list, int]:
    # n is clamped into [1, 12] with the statement's own floor of 1 house. The
    # shapes are built rather than left to chance, because the uniform draw almost
    # never produces the two cases the problem is ABOUT -- which of the two ends
    # the optimum robs. Measured over the 200 draws the self-check makes: the
    # wraparound (the circle answering strictly less than the same array on a
    # street) binds in 61.0% of ALL cases -- 67.4% over a 4000-draw sample -- and
    # in 87.8% of the draws with n >= 3 (87.4% over 4000); the residual is the
    # n <= 2 cases, where the wraparound cannot bind at all because two houses are
    # adjacent on a street too. Among those n >= 3 draws (139 of the 200) the
    # "rob the first" branch wins strictly in 50.4%, the "rob the last" mirror in
    # 43.9%, and 5.8% are ties that both branches achieve (over 4000 draws:
    # 48.1%, 49.1% and 2.8%). ONE roll picks the family, so the weights below are
    # real quarters rather than a chain of conditional draws (the first version of
    # this generator drew again in each `elif`, which made the last family a ninth
    # of the cases instead of a quarter). Values are inside 0 <= nums[i] <= 1000
    # throughout; expected always comes from the oracle.
    n = max(1, min(n, 12))
    if n == 1:
        # A single house is its own neighbour, so the answer is that house; the
        # statement's own "the first house is the neighbor of the last one" is what
        # makes this a shape worth emitting (a two-line split has to special-case
        # it, and the reference does).
        nums = [rng.randint(0, 1000)]
    else:
        roll = rng.random()
        if roll < 0.25:
            # ROB THE FIRST: house 0 is the prize at 900-1000, the last house is
            # worth 300-400 and the interior is cheap, so the branch that excludes
            # the last house wins AND the linear answer (which would take both
            # ends) is strictly larger -- the shape where ignoring the circle
            # returns a wrong answer.
            nums = ([rng.randint(900, 1000)]
                    + [rng.randint(0, 20) for _ in range(n - 2)]
                    + [rng.randint(300, 400)])
        elif roll < 0.5:
            # ROB THE LAST: the mirror image, drawn independently so the two
            # families are not the same case reversed.
            nums = ([rng.randint(300, 400)]
                    + [rng.randint(0, 20) for _ in range(n - 2)]
                    + [rng.randint(900, 1000)])
        elif roll < 0.75:
            # BOTH ENDS are the prize (700-1000 each) and the interior is cheap:
            # the circle is what decides, and neither branch dominates.
            nums = ([rng.randint(700, 1000)]
                    + [rng.randint(0, 20) for _ in range(n - 2)]
                    + [rng.randint(700, 1000)])
        else:
            # The statement's full range: breadth, and the cases nobody built.
            nums = [rng.randint(0, 1000) for _ in range(n)]
    return [nums], _house_robber_ii_oracle(nums)


@inputs("house-robber-ii")
def _house_robber_ii_profiler(n: int, rng: random.Random) -> list:
    # Both ends at the top of the statement's value range and every interior house
    # worthless (0), capped at the statement's own 100 houses by probe_max_n. Two
    # properties, both measured at every rung of [1, 3, 6, 12, 25, 50, 100]:
    # (1) the wraparound binds wherever it can -- n >= 3 -- because the linear
    # answer takes BOTH ends (1000 + 999 = 1999) while the circle can take only
    # one of them (1000), so a solution that ignores the circle is caught by the
    # probe's output check at every measured size; (2) the 1000/999 asymmetry makes
    # the branch that excludes the last house strictly the winner (1000 vs 999), so
    # a solution that implements only the other branch is caught too. Neither side
    # can early-exit: the reference runs both of its lines over ~n houses and the
    # memoized oracle fills its whole state space (it branches on take and skip in
    # every state, whatever the money is). Values are the statement's own extremes
    # (0, 999, 1000) and n = 1 is its own floor. Accepted weakness: the answer is
    # 1000 at every rung, so a stub returning a constant would agree at scale --
    # the same weakness the trees batch documents for its bool digests; small-size
    # correctness is the judge's job.
    n = max(1, min(n, 100))
    if n == 1:
        return [[1000]]
    return [[1000] + [0] * (n - 2) + [999]]


@reference("house-robber-ii")
def _house_robber_ii_reference(nums: list[int]) -> int:
    # The canonical decomposition: on the circle you either rob house 0 -- and then
    # house n - 1 is out of reach, so the problem is the plain street over
    # 0..n - 2 -- or you do not rob house 0, and it is the plain street over
    # 1..n - 1. Two rolling-pair passes, no array and no slice, so O(n) time and
    # O(1) extra space. The helper is NESTED on purpose: judge.reference_source
    # hands the probe only inspect.getsource(entry), so a sibling function would
    # be a NameError in the probe's subprocess.
    def line(lo: int, hi: int) -> int:
        prev2 = prev1 = 0
        for i in range(lo, hi + 1):
            prev2, prev1 = prev1, max(prev1, prev2 + nums[i])
        return prev1

    n = len(nums)
    if n == 0:
        return 0
    if n == 1:
        return nums[0]  # a single house is its own neighbour: take it and stop
    return max(line(0, n - 2), line(1, n - 1))


@measure("house-robber-ii")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
