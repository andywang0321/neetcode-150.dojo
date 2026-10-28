"""QUARANTINED assessment for `remove-nth-node-from-end-of-list` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, oracle, reference


@oracle("remove-nth-node-from-end-of-list")
def _remove_nth_node_from_end_of_list_oracle(head: list[int], n: int) -> list[int]:
    """Brute force in the two-pass shape the problem is usually taught in: count
    the nodes, work out which index the nth node from the end is, and rebuild the
    list without it. Total on the empty list and on an n outside the statement's
    1 <= n <= sz (nothing is removed), which keeps the differential total even
    though the generator never emits one."""
    size = len(head)
    cut = size - n
    return [head[i] for i in range(size) if i != cut]


@cases("remove-nth-node-from-end-of-list")
def _remove_nth_node_from_end_of_list_case(
    n: int, rng: random.Random
) -> tuple[list, list[int]]:
    size = max(1, min(n, 12))  # the statement's range is 1 <= sz <= 30, so the floor is 1
    head = [rng.randint(0, 100) for _ in range(size)]
    # k is the statement's n, renamed so it cannot be confused with the caller's
    # size parameter. Drawn from [1, size] inclusive at both ends: k = size removes
    # the head, which is the classic off-by-one and IS generated.
    k = rng.randint(1, size)
    return [head, k], _remove_nth_node_from_end_of_list_oracle(head, k)


@reference("remove-nth-node-from-end-of-list")
def _remove_nth_node_from_end_of_list_reference(head: list[int], n: int) -> list[int]:
    # The statement's follow-up, one walk over the nodes: two indices a gap of n
    # apart. `fast` starts n ahead of `slow`, so when `fast` runs off the end,
    # `slow` sits exactly on the nth node from the end (that gap is what makes the
    # count-from-the-end distance work, and it is why no length is needed first).
    # Writing the survivors into a new list is this representation's unlink - the
    # returned list is the only thing the function allocates.
    size = len(head)
    if n < 1 or n > size:
        return list(head)  # outside 1 <= n <= sz: nothing to remove
    slow = 0
    fast = n
    while fast < size:
        slow += 1
        fast += 1
    out: list[int] = []
    for i in range(size):
        if i != slow:
            out.append(head[i])
    return out
