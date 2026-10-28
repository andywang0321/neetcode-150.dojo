"""QUARANTINED assessment for `count-good-nodes-in-binary-tree` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


def _random_tree(rng: random.Random, budget: int) -> list | None:
    """A random binary tree with at most ``budget`` nodes, nested-list form
    [value, left, right]."""
    if budget <= 0:
        return None
    budget -= 1
    left = _random_tree(rng, budget // 2) if rng.random() < 0.7 else None
    right = _random_tree(rng, budget // 2) if rng.random() < 0.7 else None
    return [rng.randint(0, 9), left, right]


def _complete_tree(n: int) -> list | None:
    """A complete binary tree with exactly n nodes, nested-list form.

    NOT a BST: node ``i`` is labelled ``i``, so a left child (``2i+1``) holds a
    larger value than its parent. Fine for shape questions (diameter, mirror),
    silently wrong for anything the statement calls a BST — build a balanced tree
    over ``0..n-1`` instead (the trees batch of v0.14 hit exactly this)."""
    if n <= 0:
        return None
    nodes: list[list | None] = [None] * n
    for i in range(n - 1, -1, -1):  # bottom-up: children finalized first
        left, right = 2 * i + 1, 2 * i + 2
        nodes[i] = [i, nodes[left] if left < n else None, nodes[right] if right < n else None]
    return nodes[0]


def _count_good_nodes_in_binary_tree_shift(node: list | None, delta: int) -> None:
    """Add ``delta`` to every value in place. The shape is untouched and adding
    one constant to every value cannot change a single comparison, so the
    oracle's answer is still the answer."""
    if node is None:
        return
    node[0] += delta
    _count_good_nodes_in_binary_tree_shift(node[1], delta)
    _count_good_nodes_in_binary_tree_shift(node[2], delta)


@oracle("count-good-nodes-in-binary-tree")
def _count_good_nodes_in_binary_tree_oracle(root: list | None) -> int:
    """The definition transcribed literally: a node is good when no node on the
    path from the root down to it has a larger value (its own value is compared
    too, which is harmless — a value is never greater than itself). So carry
    each path explicitly and test every node against its own path: O(n*h),
    obviously correct, and it uses nothing about the tree's shape. Total on the
    empty tree, which the statement's [1, 10^5] node range does not allow but
    the dojo representation can express."""

    def walk(node: list | None, path: list[int]) -> int:
        if node is None:
            return 0
        value = node[0]
        good = all(ancestor <= value for ancestor in path)
        below = path + [value]
        return (1 if good else 0) + walk(node[1], below) + walk(node[2], below)

    return walk(root, [])


@cases("count-good-nodes-in-binary-tree")
def _count_good_nodes_in_binary_tree_case(n: int, rng: random.Random) -> tuple[list, int]:
    n = max(1, min(n, 12))  # the statement's node range is [1, 10^5]
    tree = _random_tree(rng, n)  # values 0..9: inside [-10^4, 10^4], and tie-heavy
    # A third of the cases are shifted to one end of the statement's value range
    # (-10^4, or 10^4 when 9 is the largest value drawn). Shifting cannot change
    # which nodes are good, so the case stays oracle-derived, and it covers both
    # ends of the range plus the classic wrong seeding of the running maximum
    # (0 instead of "nothing seen yet", which no negative tree can survive).
    if rng.random() < 0.34:
        _count_good_nodes_in_binary_tree_shift(tree, rng.choice([-10_000, 9_991]))
    return [tree], _count_good_nodes_in_binary_tree_oracle(tree)


@inputs("count-good-nodes-in-binary-tree")
def _count_good_nodes_in_binary_tree_profiler(n: int, rng: random.Random) -> list:
    """A complete tree: exactly n nodes, values 0..n-1 (inside the statement's
    [-10^4, 10^4] for every rung of the probe ladder, the top one being 6400),
    each node larger than its parent, so every node is good and the count is n.
    Nothing can early-exit — the whole tree has to be visited either way.
    Balanced rather than a chain so a recursive solution runs at depth log n
    instead of n (`_diameter_profiler`'s convention)."""
    return [_complete_tree(n)]


@reference("count-good-nodes-in-binary-tree")
def _count_good_nodes_in_binary_tree_reference(root: list | None) -> int:
    """Canonical O(n) time / O(h) space: one descent carrying the largest value
    seen on the path so far. A node is good exactly when it is not smaller than
    that running maximum — `>=`, not `>`, because the definition forbids an
    ancestor that is *greater*, so a tie is good. `best is None` is the root's
    case (the root is always good), not a sentinel value."""

    def walk(node: list | None, best: int | None) -> int:
        if node is None:
            return 0
        value = node[0]
        if best is None or value >= best:
            return 1 + walk(node[1], value) + walk(node[2], value)
        return walk(node[1], best) + walk(node[2], best)

    return walk(root, None)


@measure("count-good-nodes-in-binary-tree")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
