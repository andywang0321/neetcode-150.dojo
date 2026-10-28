"""QUARANTINED assessment for `maximum-depth-of-binary-tree` (transcribed from the pre-split registry).

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


def _maximum_depth_of_binary_tree_in_range(tree: list | None) -> list | None:
    """Relabel a tree's values into the statement's -100..100, shape untouched.

    ``_complete_tree`` labels node i with i, so at probe sizes its values run up
    to n - 1 and leave the statement's own range (the v0.12 value-fidelity
    lesson) — even though depth does not depend on any value."""
    stack, i = [tree], 0
    while stack:
        node = stack.pop()
        if node is None:
            continue
        node[0] = -100 + (i % 201)  # sweeps -100..100, then repeats
        i += 1
        stack.append(node[1])
        stack.append(node[2])
    return tree


@oracle("maximum-depth-of-binary-tree")
def _maximum_depth_of_binary_tree_oracle(root: list | None) -> int:
    """Brute force: build every root-to-leaf path explicitly and take the
    longest — the statement's definition, spelled out. Total on the empty
    tree, which has no path and therefore depth 0."""

    def paths(node: list | None) -> list[list[int]]:
        if node is None:
            return []
        if node[1] is None and node[2] is None:
            return [[node[0]]]
        return [[node[0]] + rest for rest in paths(node[1]) + paths(node[2])]

    return max((len(path) for path in paths(root)), default=0)


@cases("maximum-depth-of-binary-tree")
def _maximum_depth_of_binary_tree_case(n: int, rng: random.Random) -> tuple[list, int]:
    n = max(0, min(n, 12))  # the statement allows 0..10^4 nodes; 0 is the empty tree
    tree = _random_tree(rng, n)  # ragged shapes; values 0..9, inside -100..100
    return [tree], _maximum_depth_of_binary_tree_oracle(tree)


@inputs("maximum-depth-of-binary-tree")
def _maximum_depth_of_binary_tree_profiler(n: int, rng: random.Random) -> list:
    # A complete tree with exactly n nodes: a depth-first or breadth-first
    # solution must reach every node to know the deepest one (nothing here lets
    # either stop early — the deepest level is full), and its log2(n) depth (13
    # at the ladder's top) keeps the measurement about the algorithm rather than
    # about CPython's recursion limit. n is clamped at the statement's own 10^4,
    # which is above the ladder's top, so the generator never reports a size
    # smaller than the one the probe asked for.
    n = max(1, min(n, 10_000))
    return [_maximum_depth_of_binary_tree_in_range(_complete_tree(n))]


@reference("maximum-depth-of-binary-tree")
def _maximum_depth_of_binary_tree_reference(root: list | None) -> int:
    """The canonical recursion: a node's depth is one more than the deeper of
    its two subtrees, and the empty tree is 0."""
    if root is None:
        return 0
    return 1 + max(
        _maximum_depth_of_binary_tree_reference(root[1]),
        _maximum_depth_of_binary_tree_reference(root[2]),
    )


@measure("maximum-depth-of-binary-tree")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
