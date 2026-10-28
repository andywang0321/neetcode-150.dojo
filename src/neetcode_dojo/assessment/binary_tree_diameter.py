"""QUARANTINED assessment for `binary_tree_diameter` (transcribed from the pre-split registry).

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


@oracle("binary_tree_diameter")
def _diameter_oracle(root: list | None) -> int:
    best = 0

    def visit(node: list | None) -> int:
        nonlocal best
        if node is None:
            return 0
        left = visit(node[1])
        right = visit(node[2])
        best = max(best, left + right)
        return 1 + max(left, right)

    visit(root)
    return best


@cases("binary_tree_diameter")
def _diameter_case(n: int, rng: random.Random) -> tuple[list, int]:
    n = max(1, min(n, 15))
    tree = _random_tree(rng, n)
    return [tree], _diameter_oracle(tree)


@inputs("binary_tree_diameter")
def _diameter_profiler(n: int, rng: random.Random) -> list:
    return [_complete_tree(n)]  # balanced: log-depth, so no recursion blowup


@reference("binary_tree_diameter")
def diameter(root: list | None) -> int:
    best = 0

    def visit(node: list | None) -> int:
        nonlocal best
        if node is None:
            return 0
        left = visit(node[1])
        right = visit(node[2])
        best = max(best, left + right)
        return 1 + max(left, right)

    visit(root)
    return best


@measure("binary_tree_diameter")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
