"""QUARANTINED assessment for `minimum-interval-to-include-each-query` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("minimum-interval-to-include-each-query")
def _minimum_interval_to_include_each_query_oracle(
    intervals: list[list[int]], queries: list[int]
) -> list[int]:
    # Brute force: every interval against every query, keeping the smallest size
    # that covers it, -1 when nothing does. Total on empty intervals (all -1)
    # and on empty queries ([]).
    answers = []
    for point in queries:
        best = -1
        for left, right in intervals:
            if left <= point <= right:
                size = right - left + 1
                if best == -1 or size < best:
                    best = size
        answers.append(best)
    return answers


@cases("minimum-interval-to-include-each-query")
def _minimum_interval_to_include_each_query_case(
    n: int, rng: random.Random
) -> tuple[list, list[int]]:
    n = max(1, min(n, 12))  # the statement's own ranges: 1 <= intervals.length, 1 <= queries.length
    intervals = []
    for _ in range(n):
        left = rng.randint(1, 10)
        intervals.append([left, left + rng.randint(0, 4)])  # 1 <= left_i <= right_i
    queries = [rng.randint(1, 12) for _ in range(rng.randint(1, n))]
    if n >= 2 and rng.random() < 0.5:
        # Reuse a query value and a neighbouring interval's endpoint: the
        # inclusive boundary and the answer-at-every-position are what the
        # examples pin least (they never repeat a query).
        queries[rng.randrange(len(queries))] = intervals[0][1]
    return [intervals, queries], _minimum_interval_to_include_each_query_oracle(
        intervals, queries
    )


@inputs("minimum-interval-to-include-each-query")
def _minimum_interval_to_include_each_query_profiler(n: int, rng: random.Random) -> list:
    # Half the budget intervals, half queries: the brute force's cost is exactly
    # (intervals x queries), so an even split is what makes it pay for the whole
    # input, while the sweep gets one sort on each side. The intervals start one
    # unit apart, so their union covers every position a query can hit (nothing
    # is trivially -1), and their lengths cycle through (2,3,5,8,13,21,34,55), so
    # short intervals expire as the sweep advances -- the heap really pops --
    # while long ones keep later queries covered, so the per-query work never
    # collapses. Both lists are shuffled: the statement promises neither order,
    # and a sorted list is one ascending run that Timsort finishes in O(n). Every
    # value stays inside 1 <= left_i <= right_i <= 10^7 and 1 <= queries[j] <= 10^7.
    m = max(1, n // 2)
    q = max(1, n - m)
    lengths = (2, 3, 5, 8, 13, 21, 34, 55)
    intervals = [[1 + i, i + lengths[i % len(lengths)]] for i in range(m)]
    span = m + lengths[(m - 1) % len(lengths)]
    queries = [1 + (j * span) // q for j in range(q)]
    rng.shuffle(intervals)
    rng.shuffle(queries)
    return [intervals, queries]


@reference("minimum-interval-to-include-each-query")
def _minimum_interval_to_include_each_query_reference(
    intervals: list[list[int]], queries: list[int]
) -> list[int]:
    import heapq  # the probe runs this snippet alone; imports must be inside it

    by_left = sorted(intervals)
    order = sorted(range(len(queries)), key=lambda index: queries[index])
    answers = [-1] * len(queries)
    heap: list[tuple[int, int]] = []  # (size, right), smallest size on top
    nxt = 0
    for index in order:
        point = queries[index]
        while nxt < len(by_left) and by_left[nxt][0] <= point:
            left, right = by_left[nxt]
            heapq.heappush(heap, (right - left + 1, right))
            nxt += 1
        while heap and heap[0][1] < point:
            heapq.heappop(heap)  # ends before the query; one ending at it stays
        if heap:
            answers[index] = heap[0][0]
    return answers


@measure("minimum-interval-to-include-each-query")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
