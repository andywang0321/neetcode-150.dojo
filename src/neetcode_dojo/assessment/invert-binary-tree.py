"""QUARANTINED assessment for `invert-binary-tree` (transcribed from the pre-split registry).

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


def _invert_binary_tree_in_range(tree: list | None) -> list | None:
    """Relabel a tree's values into the statement's -100..100, shape untouched.

    ``_complete_tree`` labels node i with i, so at probe sizes its values run
    up to n - 1 and leave the statement's own range (the v0.12 value-fidelity
    lesson) — even though no implementation's cost depends on these values."""
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


@oracle("invert-binary-tree")
def _invert_binary_tree_oracle(root: list | None) -> list | None:
    """The definition made literal: at every node the two children are
    exchanged, so the inverted tree is [value, inverted right, inverted left].
    It BUILDS the mirror instead of swapping in place — that is what keeps the
    oracle a different program from the reference — and it is total on None."""
    if root is None:
        return None
    return [root[0], _invert_binary_tree_oracle(root[2]), _invert_binary_tree_oracle(root[1])]


@cases("invert-binary-tree")
def _invert_binary_tree_case(n: int, rng: random.Random) -> tuple[list, list | None]:
    n = max(0, min(n, 12))  # the statement allows 0..100 nodes; 0 is the empty tree
    tree = _random_tree(rng, n)  # ragged shapes; values 0..9, inside -100..100
    return [tree], _invert_binary_tree_oracle(tree)


@inputs("invert-binary-tree")
def _invert_binary_tree_profiler(n: int, rng: random.Random) -> list:
    # A complete tree with exactly n nodes: every node is present and must be
    # reached, so the swap has nothing to early-exit on — and neither has an
    # explicit-stack or a queue version. Its depth is log2(n), 13 at the
    # ladder's top, so what is measured is the algorithm and not CPython's
    # recursion limit. See notes for why a path (the worst shape for a DFS
    # stack's space) cannot be used at probe scale at all.
    return [_invert_binary_tree_in_range(_complete_tree(n))]


@reference("invert-binary-tree")
def _invert_binary_tree_reference(root: list | None) -> list | None:
    """The canonical solution: exchange the two children at every node, in
    place, then invert the already-swapped children and return the root. The
    probe hands every call a fresh copy of the arguments, so mutating them is
    safe there; a caller that needs a case's args after the call must copy them
    first (see notes)."""
    if root is None:
        return None
    root[1], root[2] = root[2], root[1]
    _invert_binary_tree_reference(root[1])
    _invert_binary_tree_reference(root[2])
    return root


@measure("invert-binary-tree")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
