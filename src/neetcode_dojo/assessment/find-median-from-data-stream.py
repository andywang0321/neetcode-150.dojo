"""QUARANTINED assessment for `find-median-from-data-stream` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, oracle, reference


@oracle("find-median-from-data-stream")
def _find_median_from_data_stream_oracle(ops: list[list]) -> list:
    """Brute force: keep every value and re-sort on demand. The median is the
    statement's own definition applied to the sorted list, with no heap and no
    size invariant to get wrong."""
    values: list[int] = []
    out: list = []
    for op in ops:
        method, *args = op
        if method == "addNum":
            values.append(args[0])
            out.append(None)
        elif method == "findMedian":
            ordered = sorted(values)
            count = len(ordered)
            if count % 2:
                out.append(float(ordered[count // 2]))
            else:
                out.append((ordered[count // 2 - 1] + ordered[count // 2]) / 2)
        else:  # pragma: no cover - generators only emit the two methods
            raise ValueError(f"unknown op {method}")
    return out


@cases("find-median-from-data-stream")
def _find_median_from_data_stream_case(n: int, rng: random.Random) -> tuple[list, list, dict]:
    """Deterministic op stream, one fresh instance per case (the harness builds
    it), the statement's own value range, and findMedian only after at least one
    addNum -- the statement guarantees that, so a violating case would be
    off-contract. Half the value draws come from a narrow band so duplicates and
    equal-median runs actually occur."""
    steps = 2 * max(1, min(n, 12)) + 1
    ops: list[list] = []
    added = 0
    for step in range(steps):
        if added == 0 or step % 3 == 0:
            value = rng.randint(-4, 4) if rng.random() < 0.5 else rng.randint(-100_000, 100_000)
            ops.append(["addNum", value])
            added += 1
        else:
            ops.append(["findMedian"])
            if added == 0:  # pragma: no cover - the branch above guarantees one
                ops.append(["addNum", 0])
                added += 1
    return [], _find_median_from_data_stream_oracle(ops), {"ops": ops}


@reference("find-median-from-data-stream")
def _find_median_from_data_stream_reference(ops: list[list]) -> list:
    """The op-list driver over the canonical two-heap split: a max-heap of the
    lower half and a min-heap of the upper half, kept within one element of each
    other, so addNum costs O(log n) and findMedian reads the tops. Written as a
    driver because the probe pairs one entry point on both sides and a class
    cannot be driven that way (min_stack, time-based-key-value-store)."""
    import heapq

    low: list[int] = []  # max-heap, stored negated
    high: list[int] = []  # min-heap
    out: list = []
    for op in ops:
        method, *args = op
        if method == "addNum":
            value = args[0]
            heapq.heappush(low, -value)
            heapq.heappush(high, -heapq.heappop(low))
            if len(high) > len(low):
                heapq.heappush(low, -heapq.heappop(high))
            out.append(None)
        elif method == "findMedian":
            if len(low) > len(high):
                out.append(float(-low[0]))
            else:
                out.append((-low[0] + high[0]) / 2)
        else:  # pragma: no cover - generators only emit the two methods
            raise ValueError(f"unknown op {method}")
    return out
