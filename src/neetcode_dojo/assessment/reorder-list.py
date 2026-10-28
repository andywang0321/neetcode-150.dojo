"""QUARANTINED assessment for `reorder-list` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("reorder-list")
def _reorder_list_oracle(head: list[int]) -> None:
    """Brute force: peel the values off the two ends alternately - front, back,
    front, back - which is the statement's pattern written directly, with no
    notion of halves or reversal. The result is written back with a slice
    assignment, so the list the caller holds is the reordered one, and that
    post-call argument list is exactly what dojo's "mutates" verdict compares.
    Total on an empty or single-node list (the statement requires at least one
    node)."""
    order: list[int] = []
    lo = 0
    hi = len(head) - 1
    take_front = True
    while lo <= hi:
        if take_front:
            order.append(head[lo])
            lo += 1
        else:
            order.append(head[hi])
            hi -= 1
        take_front = not take_front
    head[:] = order


@cases("reorder-list")
def _reorder_list_case(
    n: int, rng: random.Random
) -> tuple[list, list[list[int]], dict]:
    size = max(1, min(n, 12))  # the statement's range is 1 <= nodes <= 5 * 10^4
    head = [rng.randint(1, 1000) for _ in range(size)]
    expected = list(head)
    _reorder_list_oracle(expected)
    # A "mutates" case: expected is the ARGUMENT LIST as it must stand after the
    # call, not the (None) return value - the same shape the visible tests use.
    return [head], [expected], {"compare": "mutates"}


@inputs("reorder-list")
def _reorder_list_profiler(n: int, rng: random.Random) -> list:
    # A ramp of n values inside the statement's [1, 1000]. Both sides are
    # length-driven - the alternating peel and reverse-then-interleave both touch
    # every node - and every size the probe uses is orders of magnitude above the
    # < 3 nodes where a "nothing to do" early return is legitimate, so no ladder
    # point can exit early. Adjacent values differ, so a reorder that lost,
    # duplicated or misplaced a node cannot digest-match the reference.
    size = max(3, min(n, 10_000))
    return [[1 + (i % 1000) for i in range(size)]]


@reference("reorder-list")
def _reorder_list_reference(head: list[int]) -> None:
    # The canonical three steps over the list of node values. Split at the middle
    # (the first half takes the extra node when the length is odd), reverse the
    # second half in place with a swap loop - the pointer reversal, with indices
    # standing in for the links - then interleave the two halves. The interleave
    # is the one step a plain list cannot do with O(1) extra space (it is an
    # in-place perfect shuffle), so the merged order is built in a temporary list
    # and written back into the argument. Returning early below three nodes is the
    # statement's own [L0, Ln] identity, and no probe size comes near it.
    size = len(head)
    if size < 3:
        return
    mid = (size + 1) // 2
    lo = mid
    hi = size - 1
    while lo < hi:
        head[lo], head[hi] = head[hi], head[lo]
        lo += 1
        hi -= 1
    order: list[int] = []
    for i in range(size - mid):
        order.append(head[i])
        order.append(head[mid + i])
    if size % 2:
        order.append(head[mid - 1])
    head[:] = order


@measure("reorder-list")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    mutates."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'mutates'}
