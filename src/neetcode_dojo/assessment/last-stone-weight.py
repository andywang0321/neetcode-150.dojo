"""QUARANTINED assessment for `last-stone-weight` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, oracle, reference


@oracle("last-stone-weight")
def _last_stone_weight_oracle(stones: list[int]) -> int:
    """Brute force: re-sort the whole pile every turn and smash the two heaviest.
    Total on the empty list and on a one-stone list (the constraints exclude the
    first, but the gate and the generator may reach it) — no stones left is 0."""
    pile = list(stones)
    while len(pile) > 1:
        pile.sort()
        y = pile.pop()
        x = pile.pop()
        if x != y:
            pile.append(y - x)
    return pile[0] if pile else 0


@cases("last-stone-weight")
def _last_stone_weight_case(n: int, rng: random.Random) -> tuple[list, int]:
    n = max(1, min(n, 12))  # the statement's own constraint: 1 <= stones.length <= 30
    roll = rng.random()
    if roll < 0.35:
        # Every stone the same weight: each smash destroys both, so the answer is 0
        # for an even count and that weight for an odd one — the x == y rule.
        stones = [rng.randint(1, 1000)] * n
    elif roll < 0.7:
        # A tiny weight range, so ties are frequent and unequal pairs leave equal
        # remnants behind on later turns.
        stones = [rng.randint(1, 6) for _ in range(n)]
    else:
        stones = [rng.randint(1, 1000) for _ in range(n)]  # the stated range
    return [stones], _last_stone_weight_oracle(stones)


@reference("last-stone-weight")
def _last_stone_weight_reference(stones: list[int]) -> int:
    """Canonical max-heap: a min-heap of negated weights, so the two heaviest are two
    O(log n) pops and at most one O(log n) push per turn — O(n log n) time and O(n)
    space, the statement's target. The heap is a fresh copy, so the argument list is
    never mutated."""
    import heapq

    heap = [-weight for weight in stones]
    heapq.heapify(heap)
    while len(heap) > 1:
        y = -heapq.heappop(heap)
        x = -heapq.heappop(heap)
        if x != y:
            heapq.heappush(heap, -(y - x))
    return -heap[0] if heap else 0
