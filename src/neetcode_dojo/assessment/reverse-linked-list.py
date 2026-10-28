"""QUARANTINED assessment for `reverse-linked-list` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("reverse-linked-list")
def _reverse_linked_list_oracle(head: list[int]) -> list[int]:
    """Brute force: walk the list from the front and push every value onto the
    front of the result, so the node read first ends up last. Obviously correct,
    deliberately not the intended technique, and O(n^2) because each insert moves
    everything already placed. Total on the empty list, which the statement's
    [0, 5000] node range allows and the generator emits."""
    out: list[int] = []
    for value in head:
        out.insert(0, value)
    return out


@cases("reverse-linked-list")
def _reverse_linked_list_case(n: int, rng: random.Random) -> tuple[list, list[int]]:
    n = max(0, min(n, 12))  # the statement's node range is [0, 5000]; the floor is 0 on purpose
    # Values are inside the statement's [-5000, 5000]. Duplicates are allowed
    # (nothing promises distinct node values) and no value changes the work.
    head = [rng.randint(-5000, 5000) for _ in range(n)]
    return [head], _reverse_linked_list_oracle(head)


@inputs("reverse-linked-list")
def _reverse_linked_list_profiler(n: int, rng: random.Random) -> list:
    # Reversal has no early exit on either side: every node is visited and placed
    # whatever the values are, so this input's only jobs are to be legal and to be
    # UNAMBIGUOUS. A strictly increasing ramp inside [-5000, 5000] is both: the
    # values are distinct for every size the probe can ask for (n <= 3200 here, and
    # 10001 distinct values exist), so the digest the probe compares is a real
    # statement about the permutation. With a repeating pattern a solution that
    # dropped or duplicated a node could still match.
    size = max(1, n)
    return [[-5000 + (i % 10001) for i in range(size)]]


@reference("reverse-linked-list")
def _reverse_linked_list_reference(head: list[int]) -> list[int]:
    # The iterative reversal over dojo's list of node values: walk the indices
    # from the last node back to the head and append each value - the relinking
    # loop with the index standing in for the `next` pointer. O(n) time and O(1)
    # extra space: the returned list is the only thing it allocates, and it does
    # not touch the argument.
    out: list[int] = []
    for i in range(len(head) - 1, -1, -1):
        out.append(head[i])
    return out


@measure("reverse-linked-list")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
