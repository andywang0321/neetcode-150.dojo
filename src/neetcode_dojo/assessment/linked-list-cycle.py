"""QUARANTINED assessment for `linked-list-cycle` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("linked-list-cycle")
def _linked_list_cycle_oracle(next_node: list[int]) -> bool:
    """Brute force: walk the successor chain from node 0 and remember every node
    visited. A revisit is the statement's own definition of a cycle; a -1 is the
    end of the list. Total on the empty list (which the statement's [0, 10^4]
    node range allows and the generator emits): no nodes, no cycle."""
    seen: set[int] = set()
    if not next_node:
        return False
    node = 0
    while node != -1:
        if node in seen:
            return True
        seen.add(node)
        node = next_node[node]
    return False


@cases("linked-list-cycle")
def _linked_list_cycle_case(n: int, rng: random.Random) -> tuple[list, bool]:
    n = max(0, min(n, 12))  # the statement's node range is [0, 10^4]
    # next_node[i] is the index of node i's successor; the last node closes the
    # cycle at pos (or ends the list with -1). With n = 0 there is no node to
    # point anywhere, so pos is not drawn at all (randint(0, -1) would raise).
    next_node = [i + 1 for i in range(n)]
    if n:
        pos = -1 if rng.random() < 0.4 else rng.randint(0, n - 1)
        next_node[-1] = pos
    return [next_node], _linked_list_cycle_oracle(next_node)


@inputs("linked-list-cycle")
def _linked_list_cycle_profiler(n: int, rng: random.Random) -> list:
    """One ring of n nodes: the successor chain is 0 -> 1 -> ... -> n-1 -> 0, so
    the tortoise and the hare have to walk the whole ring before they meet and
    neither implementation can exit early. Node count is clamped to the
    statement's 10^4."""
    size = max(2, n)
    next_node = [i + 1 for i in range(size)]
    next_node[-1] = 0
    return [next_node]


@reference("linked-list-cycle")
def _linked_list_cycle_reference(next_node: list[int]) -> bool:
    # Floyd's tortoise and hare, the statement's follow-up: two pointers, no
    # extra memory. A -1 ends the list at either pointer, so a walk that reaches
    # null has no cycle.
    if not next_node:
        return False
    slow = 0
    fast = 0
    while True:
        fast = next_node[fast]
        if fast == -1:
            return False
        fast = next_node[fast]
        if fast == -1:
            return False
        slow = next_node[slow]
        if fast == slow:
            return True


@measure("linked-list-cycle")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
