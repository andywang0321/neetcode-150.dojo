"""QUARANTINED assessment for `kth-largest-element-in-a-stream` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, oracle, reference


@oracle("kth-largest-element-in-a-stream")
def _kth_largest_element_in_a_stream_oracle(ops: list[list]) -> list:
    """Brute force: keep every score the stream has produced and re-sort the whole
    pool on each add. The leading __init__ op is where the oracle learns k and the
    initial scores — the same one list the judge replays and the gate passes in."""
    pool: list[int] = []
    k = 0
    out: list = []
    for op in ops:
        method, *args = op
        if method == "__init__":
            k, nums = args
            pool = list(nums)
            out.append(None)
        elif method == "add":
            pool.append(args[0])
            out.append(sorted(pool)[-k])
        else:  # pragma: no cover - the generator only emits these two methods
            raise ValueError(f"unknown op {method}")
    return out


@cases("kth-largest-element-in-a-stream")
def _kth_largest_element_in_a_stream_case(n: int, rng: random.Random) -> tuple[list, list, dict]:
    n = max(1, min(n, 12))
    size = rng.randint(0, n)  # the statement's own constraint: 0 <= nums.length
    k = rng.randint(1, size + 1)  # the statement's own constraint: k <= nums.length + 1
    count = rng.randint(1, n)  # at least one add: k <= nums.length + 1 is what makes
    #                             the k-th largest exist as soon as one score arrives
    if rng.random() < 0.5:
        # A tiny value range, so duplicate scores dominate and the answer sits at a
        # tie; a heap capped at k has to return the k-th largest anyway.
        nums = [rng.randint(-5, 5) for _ in range(size)]
        adds = [rng.randint(-5, 5) for _ in range(count)]
    else:
        nums = [rng.randint(-10_000, 10_000) for _ in range(size)]  # the stated range
        adds = [rng.randint(-10_000, 10_000) for _ in range(count)]
    ops = [["__init__", k, list(nums)]] + [["add", val] for val in adds]
    ctor_args = [k, list(nums)]
    return [], _kth_largest_element_in_a_stream_oracle(ops), {
        "ops": ops,
        "ctor_args": ctor_args,
    }


@reference("kth-largest-element-in-a-stream")
def _kth_largest_element_in_a_stream_reference(ops: list[list]) -> list:
    """Canonical KthLargest, written as the op-list driver the registry convention
    calls (curator._case_findings passes the op list, never ctor_args): a min-heap
    that never holds more than k scores, so each add is O(log k) and the heap is
    O(k) — the statement's target. The constructor heapifies the initial scores and
    trims them to k."""
    import heapq

    heap: list[int] = []
    k = 0
    out: list = []
    for op in ops:
        method, *args = op
        if method == "__init__":
            k, nums = args
            heap = list(nums)
            heapq.heapify(heap)
            while len(heap) > k:
                heapq.heappop(heap)
            out.append(None)
        elif method == "add":
            val = args[0]
            if len(heap) < k:
                heapq.heappush(heap, val)
            elif val > heap[0]:
                heapq.heapreplace(heap, val)
            out.append(heap[0])
        else:  # pragma: no cover - the generator only emits these two methods
            raise ValueError(f"unknown op {method}")
    return out
