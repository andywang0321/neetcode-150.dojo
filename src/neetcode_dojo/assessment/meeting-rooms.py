"""QUARANTINED assessment for `meeting-rooms` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("meeting-rooms")
def _meeting_rooms_oracle(intervals: list[list[int]]) -> bool:
    # Every pair, checked as a pair: two meetings clash when their interiors
    # intersect, so one ending exactly when the next starts is not a clash.
    for i in range(len(intervals)):
        for j in range(i + 1, len(intervals)):
            if intervals[i][0] < intervals[j][1] and intervals[j][0] < intervals[i][1]:
                return False
    return True


@cases("meeting-rooms")
def _meeting_rooms_case(n: int, rng: random.Random) -> tuple[list, bool]:
    n = max(0, min(n, 12))  # the statement's own range: 0 <= intervals.length
    intervals = []
    for _ in range(n):
        start = rng.randint(0, 10)
        intervals.append([start, start + rng.randint(1, 4)])  # 0 <= start < end
    if n >= 2 and rng.random() < 0.3:
        # Force the boundary the statement names explicitly: the next meeting
        # starts exactly when this one ends, which is *not* a clash.
        intervals[1] = [intervals[0][1], intervals[0][1] + rng.randint(1, 3)]
    return [intervals], _meeting_rooms_oracle(intervals)


@inputs("meeting-rooms")
def _meeting_rooms_profiler(n: int, rng: random.Random) -> list:
    # n disjoint meetings ([0,1], [2,3], ...) inside 0 <= start < end <= 10^6,
    # then shuffled. Disjoint, so no pair clashes: the oracle's all-pairs scan
    # runs to the end and the reference's early return never fires. Shuffled,
    # because a sorted list is one ascending run -- Timsort finishes it in O(n),
    # which would measure a correct n log n solution as linear.
    intervals = [[2 * i, 2 * i + 1] for i in range(n)]
    rng.shuffle(intervals)
    return [intervals]


@reference("meeting-rooms")
def _meeting_rooms_reference(intervals: list[list[int]]) -> bool:
    intervals.sort()  # in place: the target is O(1) space beyond the input
    for i in range(1, len(intervals)):
        if intervals[i][0] < intervals[i - 1][1]:
            return False
    return True


@measure("meeting-rooms")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
