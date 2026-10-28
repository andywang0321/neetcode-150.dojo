"""QUARANTINED assessment for `merge-intervals` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("merge-intervals")
def _merge_intervals_oracle(intervals: list[list[int]]) -> list[list[int]]:
    # Brute force, and a different mechanism from the reference's sort-and-sweep:
    # treat the intervals as a graph whose edges join two intervals that share at
    # least one point (the statement's own reading of "overlapping", which its
    # Example 2 spells out for [1,4] and [4,5]) and take the connected components
    # -- one component at a time, by closing a group over every interval still in
    # the pool -- replacing each component by its union [min start, max end]. The
    # components are then sorted for the canonical order. Nothing here depends on
    # the input being sorted (the statement does not promise it) or on its
    # intervals being disjoint, and it is total: the empty list returns [].
    pooled = [list(iv) for iv in intervals]
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


@cases("merge-intervals")
def _merge_intervals_case(n: int, rng: random.Random) -> tuple[list, list, dict]:
    # 1 <= intervals.length <= 10^4, so the clamp's floor is 1 (the caller sends
    # 0..12 and the statement has no empty input) and 0 <= starti <= endi <= 10^4
    # -- lengths are drawn 1..3, with one case in five turning exactly one interval
    # into a zero-length one (end = start, which the non-strict bound allows), so
    # the degenerate shape is covered without every case being about it.
    #
    # The value range is kept small (starts 0..12, ends at most 15) so that
    # overlaps, exact duplicates and touches all happen often, and the order is
    # SHUFFLED on purpose: the statement says nothing about the input being
    # sorted, so an implementation that forgets to sort has to fail here (the
    # third Example, [[4,7],[1,4]] -> [[1,7]], is the statement's own warning that
    # the input may arrive out of order).
    #
    # The verdict tag rides on every case: the answer is the set of merged
    # intervals, whose order the statement leaves free, so the cases are judged
    # order-insensitively ("compare": "sorted") while the oracle still emits the
    # canonical ascending order.
    count = max(1, min(n, 12))
    intervals = []
    for _ in range(count):
        start = rng.randint(0, 12)
        intervals.append([start, start + rng.randint(1, 3)])
    if rng.random() < 0.2:
        flattened = intervals[rng.randrange(len(intervals))]
        flattened[1] = flattened[0]  # a zero-length interval, still 0 <= start <= end
    rng.shuffle(intervals)
    return [intervals], _merge_intervals_oracle(intervals), {"compare": "sorted"}


@inputs("merge-intervals")
def _merge_intervals_profiler(n: int, rng: random.Random) -> list:
    # n intervals that touch end-to-start -- [0, 1], [1, 2], ..., [n-1, n] -- with
    # every value inside the statement's 0 <= starti <= endi <= 10^4 (the largest
    # end is n = 6400 at the probe's top of the ladder).
    #
    # Why this shape: consecutive intervals share a point, so the sort-and-sweep
    # takes its MERGE branch on every single iteration -- it never appends a
    # second interval and never falls back to copying -- and the whole array
    # collapses to [0, n]. That is the worst case for the sweep, and there is no
    # early exit on the other side either: the input must be read in full to be
    # ordered, and an implementation cannot know that everything merges without
    # walking all of it.
    #
    # The ORDER is scrambled, which is the part that is easy to get wrong: the
    # reference sorts, and Python's sort is Timsort, whose best case on input that
    # already ascends is one detected run -- O(n) comparisons. Handing it the chain
    # in its natural order would quietly delete the n log n term this problem is
    # about, from BOTH sides of the paired measurement, and the ladder's ratios
    # would then describe something the problem never asked about. The generator
    # receives the probe's own seeded rng (random.Random(SEED) in probe.run_probe),
    # so the scramble is reproducible run to run.
    count = max(1, n)
    intervals = [[i, i + 1] for i in range(count)]
    rng.shuffle(intervals)
    return [intervals]


@reference("merge-intervals")
def _merge_intervals_reference(intervals: list[list[int]]) -> list[list[int]]:
    """Canonical sort-and-sweep: O(n log n) time (the sort dominates) and O(n)
    space for the ordered copy plus the result, where n is the number of
    intervals. The input is NOT sorted, so ordering by start is the first real
    step; after that one pass is enough, because intervals that share a point are
    merged by extending the last interval in the result -- `iv[0] <= last_end`
    and not `<`, since the statement counts touching as overlapping (its Example
    2 merges [1,4] with [4,5]) -- and an interval that starts after the last end
    cannot overlap anything already emitted. The result is therefore ascending by
    start and its intervals do not even touch, which is the canonical order the
    visible tests show."""
    ordered = sorted(intervals, key=lambda iv: iv[0])
    merged: list[list[int]] = []
    for iv in ordered:
        if merged and iv[0] <= merged[-1][1]:
            if iv[1] > merged[-1][1]:
                merged[-1][1] = iv[1]
        else:
            merged.append([iv[0], iv[1]])
    return merged


@measure("merge-intervals")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    sorted."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'sorted'}
