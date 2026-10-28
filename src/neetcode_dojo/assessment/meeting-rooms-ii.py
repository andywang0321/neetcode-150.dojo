"""QUARANTINED assessment for `meeting-rooms-ii` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("meeting-rooms-ii")
def _meeting_rooms_ii_oracle(intervals: list[list[int]]) -> int:
    # The answer is the largest number of meetings running at the same instant,
    # and that instant can always be taken to be a meeting's start, so counting
    # the meetings in progress at every start is exact. O(n^2), and deliberately
    # NOT "how many intervals overlap this one": [0,10] overlaps both [1,2] and
    # [3,4], but those two never run together, so that count says 3 where the
    # answer is 2.
    best = 0
    for start, _ in intervals:
        active = sum(
            1 for other_start, other_end in intervals if other_start <= start < other_end
        )
        if active > best:
            best = active
    return best


@cases("meeting-rooms-ii")
def _meeting_rooms_ii_case(n: int, rng: random.Random) -> tuple[list, int]:
    n = max(1, min(n, 12))  # the statement's own range: 1 <= intervals.length
    intervals = []
    for _ in range(n):
        start = rng.randint(0, 10)
        intervals.append([start, start + rng.randint(1, 4)])  # 0 <= start < end
    if n >= 2 and rng.random() < 0.3:
        # Force the boundary the statement names explicitly: a meeting that ends
        # at t frees its room for one starting at t, so this pair needs one room.
        intervals[1] = [intervals[0][1], intervals[0][1] + rng.randint(1, 3)]
    return [intervals], _meeting_rooms_ii_oracle(intervals)


@inputs("meeting-rooms-ii")
def _meeting_rooms_ii_profiler(n: int, rng: random.Random) -> list:
    # A fixed-width sliding window inside 0 <= start < end <= 10^6: meeting i runs
    # [i, i + n//2]. The peak occupancy is n//2 and it is sustained over the
    # second half of the starts; after the first n//2 starts every step both
    # frees a room and takes one, so the sweep's inner loop is never dead (the
    # all-overlapping variant, the other obvious worst case, would leave it dead
    # while costing the same). Shuffled, because a sorted list is one ascending
    # run -- Timsort finishes it in O(n).
    width = max(1, n // 2)
    intervals = [[i, i + width] for i in range(n)]
    rng.shuffle(intervals)
    return [intervals]


@reference("meeting-rooms-ii")
def _meeting_rooms_ii_reference(intervals: list[list[int]]) -> int:
    starts = sorted(interval[0] for interval in intervals)
    ends = sorted(interval[1] for interval in intervals)
    rooms = 0
    best = 0
    freed = 0
    for start in starts:
        # a meeting ending at t frees its room for a meeting starting at t
        while freed < len(ends) and ends[freed] <= start:
            rooms -= 1
            freed += 1
        rooms += 1
        if rooms > best:
            best = rooms
    return best


@measure("meeting-rooms-ii")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
