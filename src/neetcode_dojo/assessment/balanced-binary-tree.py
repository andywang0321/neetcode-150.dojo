"""QUARANTINED assessment for `balanced-binary-tree` (transcribed from the pre-split registry).

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


@oracle("balanced-binary-tree")
def _balanced_binary_tree_oracle(root: list | None) -> bool:
    """Brute force: the definition applied at every node — compute both
    subtree heights in full and check they differ by at most one. O(n log n) on
    a balanced tree and O(n^2) on a path, and it shares no code with the
    intended solution. Total on None (true, for the same reason an empty tree
    has no node to violate anything)."""

    def height(node: list | None) -> int:
        if node is None:
            return 0
        return 1 + max(height(node[1]), height(node[2]))

    def check(node: list | None) -> bool:
        if node is None:
            return True
        if abs(height(node[1]) - height(node[2])) > 1:
            return False
        return check(node[1]) and check(node[2])

    return check(root)


@cases("balanced-binary-tree")
def _balanced_binary_tree_case(n: int, rng: random.Random) -> tuple[list, bool]:
    n = max(0, min(n, 12))  # the statement allows 0..5000 nodes; 0 is the empty tree
    roll = rng.random()
    if n == 0:
        tree = None
    elif roll < 1 / 3:
        # Every level full to the last: balanced by construction, so the TRUE
        # branch is exercised by a shape no implementation can decide early.
        tree = _complete_tree(rng.randint(0, n))
    elif roll < 2 / 3:
        # Ragged: _random_tree splits its budget in half per child, so one side
        # is often cut off while the other keeps a subtree two levels deep.
        tree = _random_tree(rng, 2 * n)
    else:
        # A root with a single child — the shape the statement's own example 2
        # is built from, and by far the most reliable way to be unbalanced at
        # SMALL sizes: _random_tree on its own is never unbalanced below budget
        # 8 (measured 0%), because halving the budget caps the depth, whereas a
        # lone child makes the two heights 0 and h differ as soon as h >= 2.
        tree = [rng.randint(0, 9), _random_tree(rng, 2 * n), None]
    return [tree], _balanced_binary_tree_oracle(tree)


@inputs("balanced-binary-tree")
def _balanced_binary_tree_profiler(n: int, rng: random.Random) -> list:
    # A complete tree with exactly n nodes. It is balanced, so the intended
    # bottom-up solution has to walk all n nodes — its -1 has nowhere to fire —
    # and the naive "height at every node" solution pays its full extra factor
    # instead of stopping at the first bad node. Depth is log2(n), 13 at the
    # ladder's top, so recursion is not what gets measured. n is clamped at the
    # statement's own 5000 nodes, which is exactly the probe_max_n below, so the
    # size the probe asks for is the size the generator builds; values are
    # _complete_tree's 0..n-1, inside the statement's -10^4..10^4.
    n = max(1, min(n, 5000))
    return [_complete_tree(n)]


@reference("balanced-binary-tree")
def _balanced_binary_tree_reference(root: list | None) -> bool:
    """The canonical bottom-up solution: one post-order pass returning a
    subtree's height, or -1 the moment a subtree is unbalanced — so every node
    is visited exactly once and the -1 propagates without any further work.
    The empty tree is 0 and therefore balanced."""

    def height_or_fail(node: list | None) -> int:
        if node is None:
            return 0
        left = height_or_fail(node[1])
        if left == -1:
            return -1
        right = height_or_fail(node[2])
        if right == -1:
            return -1
        if abs(left - right) > 1:
            return -1
        return 1 + max(left, right)

    return height_or_fail(root) != -1


@measure("balanced-binary-tree")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
