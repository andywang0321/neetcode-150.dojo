"""QUARANTINED assessment for `merge-k-sorted-lists` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("merge-k-sorted-lists")
def _merge_k_sorted_lists_oracle(lists: list[list[int]]) -> list[int]:
    """Brute force: at every output position, scan the current head of all k
    lists and take the smallest. O(total * k) with no heap and no sorting, so
    the differential against the reference is a real one."""
    positions = [0] * len(lists)
    out: list[int] = []
    while True:
        best = None
        best_index = -1
        for index, head in enumerate(lists):
            if positions[index] < len(head):
                value = head[positions[index]]
                if best is None or value < best:
                    best, best_index = value, index
        if best_index < 0:
            return out
        out.append(best)
        positions[best_index] += 1


@cases("merge-k-sorted-lists")
def _merge_k_sorted_lists_case(n: int, rng: random.Random) -> tuple[list, list]:
    # The statement's own ranges: 0 <= k == lists.length <= 10^4, 0 <=
    # lists[i].length <= 500, -10^4 <= lists[i][j] <= 10^4, every list ascending.
    # n (the caller's 0..12) only sizes the shape, so the cases cover the shapes
    # the constraints allow: k = 0 (example 2), a single empty list (example 3),
    # empty lists among non-empty ones, and duplicate values across lists.
    # Values come from -20..20 so duplicates are frequent.
    n = max(0, min(n, 12))
    k = rng.randint(0, n + 1) if n else 0
    lists: list[list[int]] = []
    for _ in range(k):
        length = rng.randint(0, 3)
        lists.append(sorted(rng.randint(-20, 20) for _ in range(length)))
    return [lists], _merge_k_sorted_lists_oracle(lists)


@inputs("merge-k-sorted-lists")
def _merge_k_sorted_lists_profiler(n: int, rng: random.Random) -> list:
    # k = n // 2 lists of two nodes, the values being the ranks 0..n-1 handed out
    # in *merge* order: list j holds [order[j], k + order[j]], so the merged
    # sequence is 0, 1, 2, ... while every list is ascending as the statement
    # requires. Values stay inside -10^4..10^4 (the largest is n - 1 <= 6399 on
    # the probe's ladder), k = n/2 <= 3200 <= 10^4, and the total node count is n.
    #
    # k grows with n on purpose, and that is what makes the measurement say
    # something about this problem: every step of the merge pops a *different*
    # list (the heads interleave perfectly across all k of them), so the heap
    # stays at its full k entries for nearly the whole merge and a solution that
    # merges the lists one at a time pays its whole O(n * k). With k held
    # constant, log k would be a constant and the problem's own difficulty — how
    # many lists are being merged — would vanish from the measurement.
    #
    # The list order is scrambled (Knuth's multiplicative constant mod 2**32, a
    # bijection, so `order` is a permutation) for a reason that is the v0.11
    # early-exit lesson in a new costume: with the lists left in rank order,
    # concatenating them in list order nearly sorts the input, and a
    # collect-and-sort solution is then measured on timsort's best case instead
    # of its real n log n — it came back "better than the reference — O(n)" on
    # exactly that artifact. Scrambled, no implementation sees a lucky shape.
    n = max(1, n)
    k = max(1, n // 2)
    per = max(1, n // k)
    order = sorted(range(k), key=lambda j: (j * 2654435761) % 2**32)
    return [[[i * k + order[j] for i in range(per)] for j in range(k)]]


@reference("merge-k-sorted-lists")
def _merge_k_sorted_lists_reference(lists: list[list[int]]) -> list[int]:
    """Canonical k-way merge: one heap entry per non-empty list, pop the smallest
    head and push that list's next node — O(n log k) time and O(k) space, where n
    is the total number of nodes and k the number of lists."""
    import heapq

    heap: list[tuple[int, int, int]] = []
    for index, head in enumerate(lists):
        if head:
            heap.append((head[0], index, 0))
    heapq.heapify(heap)
    out: list[int] = []
    while heap:
        value, index, position = heapq.heappop(heap)
        out.append(value)
        position += 1
        if position < len(lists[index]):
            heapq.heappush(heap, (lists[index][position], index, position))
    return out


@measure("merge-k-sorted-lists")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
