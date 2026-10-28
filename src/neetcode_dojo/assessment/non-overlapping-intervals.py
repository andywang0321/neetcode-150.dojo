"""QUARANTINED assessment for `non-overlapping-intervals` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("non-overlapping-intervals")
def _non_overlapping_intervals_oracle(intervals: list[list[int]]) -> int:
    # Brute force over the structure of the answer, not over subsets (a subset
    # sweep would be 2^n, which the statement's n = 10^5 makes meaningless even
    # for a trust anchor): removing as few intervals as possible leaves the
    # LARGEST set of pairwise non-overlapping ones, so this computes the longest
    # such chain with the obvious O(n^2) DP and subtracts.
    #
    # Sort a copy by (start, end) first. A chain's intervals are pairwise
    # non-overlapping, so their starts are distinct and the chain appears in this
    # order as a subsequence -- no valid chain is lost by sorting. dp[i] is the
    # longest chain whose last interval is i, and j may precede i exactly when
    # ordered[j][1] <= ordered[i][0]: `<=` and not `<`, because the statement
    # says intervals that only touch at a point are NON-overlapping, so [1,2] and
    # [2,3] may both be kept.
    ordered = sorted(([iv[0], iv[1]] for iv in intervals), key=lambda iv: (iv[0], iv[1]))
    best = 0
    dp = [1] * len(ordered)
    for i in range(len(ordered)):
        for j in range(i):
            if ordered[j][1] <= ordered[i][0] and dp[j] + 1 > dp[i]:
                dp[i] = dp[j] + 1
        if dp[i] > best:
            best = dp[i]
    return len(ordered) - best


@cases("non-overlapping-intervals")
def _non_overlapping_intervals_case(n: int, rng: random.Random) -> tuple[list, int]:
    # 1 <= intervals.length <= 10^5, so the clamp's floor of 1 is real (the caller
    # sends 0..12 and the statement has no empty input), and the value bound is
    # -5 * 10^4 <= starti < endi <= 5 * 10^4 -- a STRICT inequality, so every
    # interval built here has length >= 1 and the zero-length interval that LC 57
    # and LC 56 allow is a constraint VIOLATION here. All values stay inside
    # -10..15. The coordinate range is kept small so overlaps are common.
    #
    # Three shapes, one case in three each, because the interesting failures live
    # in different corners:
    #   * TOUCHING CHAIN -- consecutive intervals share an endpoint
    #     (start_{k+1} == end_k). The statement says such a pair does not overlap
    #     ("[1, 2] and [2, 3] are non-overlapping"), so nothing has to be removed
    #     and the answer is 0; it is also the only shape that fails a greedy
    #     written with `>` where `>=` is required.
    #   * COPIES -- the same interval `count` times, which is Example 2's shape:
    #     all of them bar one must go, so the answer is count - 1.
    #   * FREE -- independent random intervals, where overlaps, duplicates and
    #     incidental touches all occur and the answer is somewhere in between.
    # The freed order is shuffled in the chain and free modes: the statement
    # promises nothing about the input's order.
    count = max(1, min(n, 12))
    mode = rng.randrange(3)
    if mode == 0:
        intervals = []
        cursor = rng.randint(-10, 10)
        for _ in range(count):
            length = rng.randint(1, 3)
            intervals.append([cursor, cursor + length])
            cursor += length  # the next start IS this end: they touch, not overlap
        rng.shuffle(intervals)
    elif mode == 1:
        start = rng.randint(-10, 10)
        end = start + rng.randint(1, 5)
        intervals = [[start, end] for _ in range(count)]
    else:
        intervals = []
        for _ in range(count):
            start = rng.randint(-10, 10)
            intervals.append([start, start + rng.randint(1, 5)])
        rng.shuffle(intervals)
    return [intervals], _non_overlapping_intervals_oracle(intervals)


@inputs("non-overlapping-intervals")
def _non_overlapping_intervals_profiler(n: int, rng: random.Random) -> list:
    # n intervals that touch end-to-start -- [0, 1], [1, 2], ..., [n-1, n] -- in a
    # scrambled order. The values respect the statement's STRICT bound
    # -5 * 10^4 <= starti < endi <= 5 * 10^4 with room to spare (the largest end
    # is n = 6400) and every interval has length 1, so no zero-length input is
    # ever generated.
    #
    # Why this shape: nothing early-exits. The intended greedy reads all n
    # intervals, and here it takes its `start >= last_end` branch on every single
    # one of them (each interval starts exactly where the running end stopped),
    # keeping all n -- so the answer is 0 at every size and the sweep is exercised
    # on the touching-equality side of the comparison rather than on the easy
    # "strictly after" side. The O(n^2) oracle, which has no early exit either,
    # sees the same chain and finds it entirely keepable.
    #
    # The ORDER is the part that is easy to get wrong: the reference sorts by end,
    # and Python's sort is Timsort, whose best case on input that already ascends
    # is one detected run -- O(n) comparisons. Handing it the chain in its natural
    # order would delete the n log n term this problem is about from BOTH sides of
    # the paired measurement. The rng is the probe's own seeded generator
    # (probe.run_probe builds one random.Random(SEED) for the whole ladder), so
    # the scramble is reproducible.
    count = max(1, n)
    intervals = [[i, i + 1] for i in range(count)]
    rng.shuffle(intervals)
    return [intervals]


@reference("non-overlapping-intervals")
def _non_overlapping_intervals_reference(intervals: list[list[int]]) -> int:
    """Canonical greedy: O(n log n) time and O(n) space for the copy ordered by
    end, where n is the number of intervals.

    Order by END and keep every interval that starts at or after the last kept
    end. Earliest-finishing-first is what makes the greedy optimal -- the interval
    that ends first can always be swapped into an optimal solution -- and the
    comparison is `start >= last_end` and not `>`: the statement says intervals
    that only touch at a point are non-overlapping, so an interval starting
    exactly where the last one ended is kept and not counted as a removal. The
    count of kept intervals is the largest non-overlapping set, and every other
    interval has to be removed."""
    ordered = sorted(intervals, key=lambda iv: iv[1])
    kept = 0
    last_end = None
    for start, end in ordered:
        if last_end is None or start >= last_end:
            kept += 1
            last_end = end
    return len(intervals) - kept


@measure("non-overlapping-intervals")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
