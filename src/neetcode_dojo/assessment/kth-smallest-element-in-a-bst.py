"""QUARANTINED assessment for `kth-smallest-element-in-a-bst` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


def _kth_smallest_element_in_a_bst_build(rng: random.Random, values: list[int]) -> list | None:
    """A BST over ascending distinct ``values``: the root of each range is picked
    at random, so the shape is what a uniformly random insertion order produces
    and the node count is exactly len(values)."""
    if not values:
        return None
    root = rng.randrange(len(values))
    return [
        values[root],
        _kth_smallest_element_in_a_bst_build(rng, values[:root]),
        _kth_smallest_element_in_a_bst_build(rng, values[root + 1 :]),
    ]


def _kth_smallest_element_in_a_bst_tree(rng: random.Random, size: int) -> list:
    """A BST of exactly ``size`` nodes with DISTINCT values in [0, 10^4] — the
    statement's own value range, and a BST's values have to be distinct for it
    to be a BST. Three quarters of the cases are a random-insertion-order shape;
    the rest are a degenerate spine, where the k-th smallest is the k-th node
    along it — the shape that breaks a solution which only walks the left spine
    from the root."""
    values = sorted(rng.sample(range(0, 10_001), size))
    if rng.random() < 0.25:
        spine: list | None = None
        if rng.random() < 0.5:  # right-leaning: the smallest value is the root
            for value in reversed(values):
                spine = [value, None, spine]
        else:  # left-leaning: the smallest value is the deepest node
            for value in values:
                spine = [value, spine, None]
        return spine
    return _kth_smallest_element_in_a_bst_build(rng, values)


def _kth_smallest_element_in_a_bst_balanced(lo: int, hi: int) -> list | None:
    """A height-balanced BST with the keys lo..hi: the middle key of the range
    goes at the root, so the in-order walk is lo..hi and the tree is a BST by
    construction. (Placed before the profiler block it serves so that every
    helper sits inside the span the fragment's decorators mark for replacement.)"""
    if lo > hi:
        return None
    mid = (lo + hi) // 2
    return [
        mid,
        _kth_smallest_element_in_a_bst_balanced(lo, mid - 1),
        _kth_smallest_element_in_a_bst_balanced(mid + 1, hi),
    ]


@oracle("kth-smallest-element-in-a-bst")
def _kth_smallest_element_in_a_bst_oracle(root: list | None, k: int) -> int:
    """Brute force: collect every value with a plain traversal that uses nothing
    about the BST property, sort, and read the k-th. O(n log n), and correct for
    any shape — which is what makes it a real differential against the
    reference's in-order walk. The statement guarantees 1 <= k <= n; outside
    that there is no k-th smallest, so this refuses rather than invent one."""
    values: list[int] = []
    stack = [root]
    while stack:
        node = stack.pop()
        if node is None:
            continue
        values.append(node[0])
        stack.append(node[1])
        stack.append(node[2])
    if not 1 <= k <= len(values):
        raise ValueError(f"k={k} is outside the statement's 1 <= k <= n (n={len(values)})")
    values.sort()
    return values[k - 1]


@cases("kth-smallest-element-in-a-bst")
def _kth_smallest_element_in_a_bst_case(n: int, rng: random.Random) -> tuple[list, int]:
    n = max(1, min(n, 12))  # the statement's node range is [1, 10^4]
    tree = _kth_smallest_element_in_a_bst_tree(rng, n)
    k = rng.randint(1, n)  # the statement's guarantee 1 <= k <= n, by construction
    return [tree, k], _kth_smallest_element_in_a_bst_oracle(tree, k)


@inputs("kth-smallest-element-in-a-bst")
def _kth_smallest_element_in_a_bst_profiler(n: int, rng: random.Random) -> list:
    """A perfectly height-balanced BST over the keys 0..n-1: exactly n nodes,
    depth log n, in-order = 0..n-1, so it is a valid BST with values inside the
    statement's [0, 10^4] at every rung of the ladder (6400 at the top, so the
    largest key is 6399). The shared `_complete_tree` cannot be used here: it
    labels node i with i, and that array-index labelling puts a left child
    (2i+1) above its own parent, so it is not a BST at all — and this statement
    guarantees the input is one. k = n, so the answer is the largest value and
    the in-order walk has to reach the very last node: no implementation can
    stop early, and k stays inside the statement's 1 <= k <= n. Balanced rather
    than a spine so a recursive solution runs at depth log n instead of n."""
    size = max(1, n)
    return [_kth_smallest_element_in_a_bst_balanced(0, size - 1), size]


@reference("kth-smallest-element-in-a-bst")
def _kth_smallest_element_in_a_bst_reference(root: list | None, k: int) -> int:
    """Canonical: walk the BST in order with an explicit stack, so the values
    arrive ascending and the k-th one visited is the answer — O(h) space, and it
    stops as soon as k nodes have been counted instead of materializing the
    whole traversal. Every node is pushed at most once, so the walk is O(n) in
    the worst case (k = n) and O(h + k) in general. The statement guarantees
    1 <= k <= n; outside that there is no answer to return."""
    remaining = k
    stack: list[list] = []
    node = root
    while stack or node is not None:
        while node is not None:
            stack.append(node)
            node = node[1]
        node = stack.pop()
        remaining -= 1
        if remaining == 0:
            return node[0]
        node = node[2]
    raise ValueError(f"k={k} is outside the statement's 1 <= k <= n")


@measure("kth-smallest-element-in-a-bst")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
