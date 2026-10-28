"""QUARANTINED assessment for `reverse-nodes-in-k-group` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("reverse-nodes-in-k-group")
def _reverse_nodes_in_k_group_oracle(head: list[int], k: int) -> list[int]:
    """Brute force: cut the list into blocks of k, hand each *complete* block to
    reversed(), and append the leftover tail untouched. Total on the empty list
    and on k < 1 as well, neither of which is inside the statement's own range
    (1 <= k <= n) — hence the guard instead of a division by k."""
    n = len(head)
    blocks = n // k if k >= 1 else 0
    out: list[int] = []
    for block in range(blocks):
        out.extend(reversed(head[block * k : (block + 1) * k]))
    out.extend(head[blocks * k :])
    return out


@cases("reverse-nodes-in-k-group")
def _reverse_nodes_in_k_group_case(n: int, rng: random.Random) -> tuple[list, list]:
    # The statement's ranges: 1 <= k <= n <= 5000 and 0 <= Node.val <= 1000, so n
    # clamps to at least 1 (the caller sends 0..12) and k is drawn from [1, n].
    # About a third of the cases draw from a three-value alphabet: repeated values
    # are what catch a solution that reorders the values instead of the positions.
    n = max(1, min(n, 12))
    k = rng.randint(1, n)
    if rng.random() < 0.35:
        head = [rng.randint(0, 2) for _ in range(n)]
    else:
        head = [rng.randint(0, 1000) for _ in range(n)]
    return [head, k], _reverse_nodes_in_k_group_oracle(head, k)


@inputs("reverse-nodes-in-k-group")
def _reverse_nodes_in_k_group_profiler(n: int, rng: random.Random) -> list:
    # One list of n nodes with k = 6 (k = n below six nodes, because the statement
    # requires k <= n): every node but the tail sits in a complete block, and the
    # leftover exercises the "left-out nodes remain as they are" path. k = 6 is
    # chosen so that leftover is never 0 and never 1 at any ladder point — the
    # ladder is 100, 200, ..., 6400, which are 2 or 4 modulo 6, whereas k = 3
    # leaves exactly one node at 100/400/1600/6400, and reversing a one-node block
    # is a no-op, so at those sizes a "reverse the tail as well" bug would be
    # invisible. Values respect 0 <= Node.val <= 1000 (i % 1001). Nothing can
    # early-exit: reversing a block has to touch every node.
    n = max(1, n)
    k = 6 if n >= 6 else max(1, n)
    return [[i % 1001 for i in range(n)], k]


@reference("reverse-nodes-in-k-group")
def _reverse_nodes_in_k_group_reference(head: list[int], k: int) -> list[int]:
    """Canonical O(n) time and O(1) extra space: reverse every complete block of k
    in place with the two-pointer swap the ListNode version performs, then leave
    the tail alone. It reverses the list it is given and returns that same list —
    the relinking solution's own contract, and what keeps the reference's space
    baseline at O(1) rather than the O(n) a slice-based answer allocates (which is
    exactly what the statement's follow-up rules out). k < 1 is outside the
    statement's range and leaves the list untouched."""
    n = len(head)
    start = 0
    while k >= 1 and start + k <= n:
        lo, hi = start, start + k - 1
        while lo < hi:
            head[lo], head[hi] = head[hi], head[lo]
            lo += 1
            hi -= 1
        start += k
    return head


@measure("reverse-nodes-in-k-group")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
