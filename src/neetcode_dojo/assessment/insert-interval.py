"""QUARANTINED assessment for `insert-interval` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("insert-interval")
def _insert_interval_oracle(
    intervals: list[list[int]], newInterval: list[int]
) -> list[list[int]]:
    # Brute force, and a different mechanism from the reference's single sweep:
    # pool the input intervals with the new one, then close the relation
    # "these two share at least one point" -- the statement's own definition of
    # overlapping -- until no such pair is left, replacing each such group by its
    # union [min start, max end], and sort the result. Nothing here assumes the
    # input is sorted by start or that its intervals are disjoint (the statement
    # promises both, but an oracle should not need the promise), it never looks
    # at an interval once per phase, and it is total: the empty input returns
    # [[newInterval]] because the new interval is always in the pool.
    pooled = [list(iv) for iv in intervals] + [list(newInterval)]
    components: list[list[int]] = []
    while pooled:
        lo, hi = pooled.pop()
        changed = True
        while changed:
            changed = False
            rest = []
            for other in pooled:
                if max(lo, other[0]) <= min(hi, other[1]):
                    lo, hi = min(lo, other[0]), max(hi, other[1])
                    changed = True
                else:
                    rest.append(other)
            pooled = rest
        components.append([lo, hi])
    components.sort()
    return components


@cases("insert-interval")
def _insert_interval_case(
    n: int, rng: random.Random
) -> tuple[list, list]:
    # n counts the EXISTING intervals: the statement allows 0 <= intervals.length
    # <= 10^4 and the caller sends 0..12, so the clamp's floor of 0 is real and
    # the empty array is a case the generator actually emits.
    #
    # The starts come from a 5-spaced grid, which makes two of the statement's
    # promises structural rather than hoped for: the array is sorted by starti,
    # and no two of its intervals touch (two intervals that share a point are
    # overlapping by the statement's own definition, so a valid input has at
    # least one unused integer between consecutive intervals -- an end is at most
    # start + 4 and the next start is at least this start + 5).
    #
    # Lengths are 1..4, and one case in four turns exactly one interval into a
    # zero-length one (end = start), which the constraint 0 <= starti <= endi
    # allows: the degenerate shape is covered without every case being about it,
    # and starti <= endi is structural in both branches. The new interval is a
    # separate draw and is zero-length in about one case in seven.
    #
    # Every value stays inside the statement's 0..10^5: the largest end any
    # branch can produce is 80 + 6 = 86.
    count = max(0, min(n, 12))
    starts = sorted(rng.sample(range(0, 80, 5), count))
    intervals = [[s, s + rng.randint(1, 4)] for s in starts]
    if intervals and rng.random() < 0.25:
        flattened = intervals[rng.randrange(len(intervals))]
        flattened[1] = flattened[0]  # a zero-length interval, still inside the grid
    start = rng.randint(0, 80)
    new_interval = [start, start + rng.randint(0, 6)]
    return [intervals, new_interval], _insert_interval_oracle(intervals, new_interval)


@inputs("insert-interval")
def _insert_interval_profiler(n: int, rng: random.Random) -> list:
    # n intervals of the kind the statement guarantees -- sorted by starti, no
    # two sharing a point, every value inside 0 <= starti <= endi <= 10^5 (the
    # largest end is 2n + 1 = 12801 at the probe's n = 6400) -- plus a new
    # interval that spans all of them:
    #
    #     intervals = [[0, 1], [2, 3], ..., [2n-2, 2n-1]],  newInterval = [0, 2n]
    #
    # Which path does that force? The reference's three phases are (1) copy the
    # intervals that end before the new start, (2) absorb every interval that
    # starts at or before the new end, (3) copy the tail. Here (1) copies nothing
    # and (3) copies nothing, so phase (2) -- the only phase that does per-element
    # work beyond an append (a min, a max and a list rebuild) -- runs all n times,
    # and the answer is the single interval [0, 2n]. Placing the new interval
    # before or after everything instead would move the same n elements through
    # the cheap phases and leave the expensive one empty, which is the wrong side
    # of the worst case. There is no early exit to defend against on either side:
    # an implementation must read every interval to know where the new one goes
    # (a bisect-based one still has to copy the tail), and with the output being
    # one interval there is nothing for an output-driven shortcut to skip either.
    count = max(0, n)
    intervals = [[2 * i, 2 * i + 1] for i in range(count)]
    return [intervals, [0, 2 * count]]


@reference("insert-interval")
def _insert_interval_reference(
    intervals: list[list[int]], newInterval: list[int]
) -> list[list[int]]:
    """Canonical one-pass sweep, O(n) time and O(1) space beyond the returned
    list (n = the number of intervals): the input is already sorted by starti, so

      1. every interval that ends strictly before the new one starts is copied
         through untouched,
      2. from the first interval that does not, every interval that starts at or
         before the new end is absorbed -- `<=`, because the statement counts two
         intervals that share even a single point as overlapping, so a new
         interval starting exactly where an interval ends merges with it
         (Example 2: [4,8] swallows [8,10]),
      3. the merged interval is emitted, then the untouched tail is copied.

    The two boundaries are the whole problem, and they are not symmetric: phase 1
    tests `intervals[i][1] < start` (strict, so an interval that ends exactly at
    the new start is absorbed in phase 2 rather than copied), phase 2 tests
    `intervals[i][0] <= end` (non-strict, for the same reason)."""
    start, end = newInterval[0], newInterval[1]
    out: list[list[int]] = []
    i = 0
    total = len(intervals)
    while i < total and intervals[i][1] < start:
        out.append(intervals[i])
        i += 1
    while i < total and intervals[i][0] <= end:
        start = min(start, intervals[i][0])
        end = max(end, intervals[i][1])
        i += 1
    out.append([start, end])
    out.extend(intervals[i:])
    return out


@measure("insert-interval")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
