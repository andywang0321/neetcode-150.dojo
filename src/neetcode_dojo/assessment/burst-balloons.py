"""QUARANTINED assessment for `burst-balloons` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("burst-balloons")
def _burst_balloons_oracle(nums: list[int]) -> int:
    """Exhaustive "which balloon do I burst FIRST?" recursion, memoized on the
    sequence of balloons still standing.

    The statement read literally, with no interval DP and no "last balloon"
    decomposition: bursting the i-th balloon of the standing sequence pays
    (left neighbour, or a pad 1 when there is none) * value * (right neighbour, or
    1), and what is left over is that same sequence with one element removed -- so
    the recursion tries EVERY balloon as the first burst of the current sequence
    and keeps the best total. The pads are the statement's own out-of-bounds
    sentence; the search order is the statement's own "burst the balloons wisely".

    What the memo assumes, stated because everything else rests on it: the coins
    still obtainable depend only on the SEQUENCE of standing values (the pads are
    the constant 1), so two different burst histories that leave the same
    remaining sequence have the same optimum. That is precisely the recursion's
    state, so the memo cannot disagree with the unmemoized walk -- it only
    declines to repeat it. It is also what makes the oracle usable: n = 12 is 12!
    burst orders, while the memo visits the DISTINCT remaining sequences, which is
    2^n - 1 when the values are distinct and collapses to n + 1 when they are all
    equal. That matters beyond the generator: flow._oracle_confirms runs the
    oracle IN PROCESS, with no timeout, at whatever size a student and the
    reference disagreed at, so an oracle that cannot finish at the top of the
    probe's ladder would hang a live session instead of reporting a finding (the
    reason climbing-stairs' oracle carries a memo too). Measured on this machine:
    for the profiler input's repeated value, 0.05 s at the ladder's top rung
    (150 balloons) and 0.19 s even at the statement's own 300; for twenty distinct
    values, 12.6 s at n = 20. The same program, and the profiler input is chosen to
    stay on the first side of that cliff (see @profiler_input).
    Total by construction over everything the generator can produce, the empty
    array included: no balloons, no coins, 0. Values are never assumed positive
    (the statement allows 0) and `top` starts at 0, so an all-zero array answers 0
    rather than raising or returning a sentinel.
    """
    memo: dict[tuple[int, ...], int] = {}

    def best(standing: tuple[int, ...]) -> int:
        if not standing:
            return 0
        cached = memo.get(standing)
        if cached is not None:
            return cached
        top = 0
        for index, value in enumerate(standing):
            left = standing[index - 1] if index > 0 else 1
            right = standing[index + 1] if index + 1 < len(standing) else 1
            coins = left * value * right + best(standing[:index] + standing[index + 1:])
            if coins > top:
                top = coins
        memo[standing] = top
        return top

    return best(tuple(nums))


@cases("burst-balloons")
def _burst_balloons_case(n: int, rng: random.Random) -> tuple[list, int]:
    # Six shapes, all inside the statement's value bound (0 <= nums[i] <= 100) and
    # its length bound (n <= 300; the caller sends 0..12, so `size` is the length
    # and nothing is clamped away). Fractions over the draws: the empty array 10%,
    # a plain uniform draw 30%, all zeros 15%, all 100s 15%, a {0, 100} mixture
    # 15%, and small values from 1..4 15%. The caller's n is itself uniform on
    # 0..12, though, and size == 0 forces the empty array whichever branch the roll
    # picked -- so the realized mix over 200 generated cases (the author's
    # self-check, n = rng.randint(0, 12)) was empty 38, uniform 50, zeros 22,
    # hundreds 28, mixture 25, small 37: 19% / 25% / 11% / 14% / 12.5% / 18.5%. Each
    # shape is here for a stated reason rather than for coverage theatre:
    #   * the empty array is the input the statement's constraint line (1 <= n)
    #     excludes but its own rule defines -- bust nothing, collect 0 -- and it is
    #     pinned as a visible test as well, so both sides are on record;
    #   * the uniform draw is the only shape that reaches the whole 0..100 range,
    #     endpoints included;
    #   * all zeros makes the answer 0 for a different reason (every product is 0),
    #     which is where an implementation that "cancels" the balloon it just burst
    #     by dividing -- the classic wrong turn on this problem -- either raises or
    #     drifts off the answer;
    #   * all 100s pins the top of the value range and the largest totals the
    #     length bound allows;
    #   * the {0, 100} mixture is the shape where a zero balloon is genuinely
    #     useful as a separator (bursting next to it is free, so it should be kept
    #     until last), and where a greedy that avoids zeros is punished;
    #   * the 1..4 draw is where the statement's example-1 pattern repeats at small
    #     size: with duplicates and small values a "burst the smallest neighbour
    #     product first" greedy is measurably suboptimal, so the generated set can
    #     fail a greedy solution rather than only the visible examples doing so
    #     (the author's self-check asserts at least one generated case where the
    #     greedy's total is below the oracle's).
    # Expected always comes from the oracle, never from the reference.
    size = max(0, min(n, 12))
    roll = rng.random()
    if size == 0 or roll < 0.10:
        nums = []
    elif roll < 0.40:
        nums = [rng.randint(0, 100) for _ in range(size)]
    elif roll < 0.55:
        nums = [0] * size
    elif roll < 0.70:
        nums = [100] * size
    elif roll < 0.85:
        nums = [rng.choice([0, 100]) for _ in range(size)]
    else:
        nums = [rng.randint(1, 4) for _ in range(size)]
    return [nums], _burst_balloons_oracle(nums)


@inputs("burst-balloons")
def _burst_balloons_profiler(n: int, rng: random.Random) -> list:
    # One repeated value, at the top of the statement's own range (0 <= nums[i] <=
    # 100) and capped at 150 balloons -- half the statement's length bound, which is
    # why probe_max_n is 150. The cap is not about the algorithm (it is 0.78 s
    # untraced at the statement's own 300) but about the probe's measurement
    # protocol: the space call runs under tracemalloc, whose per-allocation
    # bookkeeping is superlinear, and this DP allocates once per table cell and
    # once per inner-loop arithmetic result -- 13.9 s in that phase alone at
    # n = 300, 15.6 s for the whole harness run against the probe's 20 s per-run
    # timeout. The offline probe smoke reproduced exactly that, as "the reference
    # failed at n = 300: timed out after 20s". At 150 the whole run costs 1.7 s
    # (0.05 s untraced), which leaves a student's slower implementation room
    # inside the same timeout.
    #
    # The work the profiler input has to force is the interval DP's, and that work
    # does not depend on the values at all: the canonical table fills
    # (n + 2)(n + 1)/2 windows with an inner loop over each window's split points,
    # so Theta(n^3) regardless of what the balloons are worth -- there is no
    # value-dependent early exit to take, on either side. What the values DO decide
    # is whether the oracle can still confirm a disagreement at that size: with the
    # values all equal, every remaining sequence of a given length is the same
    # tuple, so the oracle's memo holds n + 1 states instead of 2^n - 1 and the
    # in-process confirmation path stays fast (0.19 s at n = 300, measured; the
    # same call with distinct values takes 12.6 s at n = 20). The repeated value is
    # therefore load-bearing, and the cost of that choice is stated in the notes: a
    # student whose own memo is keyed on the remaining values would also collapse
    # on this input and measure as if polynomial.
    #
    # The input ignores `rng` on purpose. flow._oracle_confirms regenerates the
    # profiler input for the disputed size with its OWN rng (random.Random(f
    # "confirm-{n}")), so a size-dependent random draw would have the oracle
    # confirm a different input than the one the student disagreed on; a
    # deterministic input is the only way that check compares like with like.
    length = max(1, min(n, 150))  # the statement's floor; the cap is probe_max_n
    return [[100] * length]


@reference("burst-balloons")
def _burst_balloons_reference(nums: list[int]) -> int:
    """Canonical interval DP, O(n^3) time and O(n^2) space: pad both ends with the
    statement's out-of-bounds 1 and let table[left][right] be the most coins
    obtainable from bursting every balloon STRICTLY between the two still-standing
    boundary balloons left and right. The split point `last` is the balloon burst
    LAST in that window -- which is exactly why the multiplication is
    values[left] * values[last] * values[right]: by the time `last` goes, every
    balloon between the boundaries is already gone, so its neighbours are the two
    boundaries themselves. The table is filled by increasing window width, so both
    sub-windows are final before they are read, and the answer is the whole padded
    window's entry (0 for an empty array, where the two pads face each other)."""
    values = [1, *nums, 1]
    size = len(values)
    table = [[0] * size for _ in range(size)]
    for width in range(2, size):
        for left in range(size - width):
            right = left + width
            boundary = values[left] * values[right]
            row = table[left]
            best = 0
            for last in range(left + 1, right):
                coins = row[last] + table[last][right] + boundary * values[last]
                if coins > best:
                    best = coins
            row[right] = best
    return table[0][size - 1]


@measure("burst-balloons")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
