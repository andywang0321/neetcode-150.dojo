"""QUARANTINED assessment for `mirror_image_binary_tree` (transcribed from the pre-split registry).

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


def _mirror_of(node: list | None) -> list | None:
    if node is None:
        return None
    return [node[0], _mirror_of(node[2]), _mirror_of(node[1])]


def _mirror_tree(rng: random.Random, budget: int) -> list | None:
    """A random symmetric tree (a mirror image of itself)."""
    if budget <= 0:
        return None
    budget -= 1
    left = _random_tree(rng, budget // 2) if rng.random() < 0.8 else None
    return [rng.randint(0, 9), left, _mirror_of(left)]


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


@oracle("mirror_image_binary_tree")
def _is_mirror_oracle(root: list | None) -> bool:
    def check(a: list | None, b: list | None) -> bool:
        if a is None or b is None:
            return a is None and b is None
        return a[0] == b[0] and check(a[1], b[2]) and check(a[2], b[1])

    return check(root, root)


@cases("mirror_image_binary_tree")
def _is_mirror_case(n: int, rng: random.Random) -> tuple[list, bool]:
    n = max(0, min(n, 15))
    if n == 0:
        tree = None
    elif rng.random() < 0.5:
        tree = _mirror_tree(rng, n)
    else:
        tree = _random_tree(rng, n)
    return [tree], _is_mirror_oracle(tree)


@inputs("mirror_image_binary_tree")
def _is_mirror_profiler(n: int, rng: random.Random) -> list:
    return [_complete_tree(n)]


@reference("mirror_image_binary_tree")
def is_mirror(root: list | None) -> bool:
    if root is None:
        return True

    stack = [(root[1], root[2])]
    while stack:
        a, b = stack.pop()
        if a is None or b is None:
            if a is not b:
                return False
            continue
        if a[0] != b[0]:
            return False
        stack.append((a[1], b[2]))
        stack.append((a[2], b[1]))
    return True


@measure("mirror_image_binary_tree")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
