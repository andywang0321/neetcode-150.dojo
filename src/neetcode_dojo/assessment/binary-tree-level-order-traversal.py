"""QUARANTINED assessment for `binary-tree-level-order-traversal` (transcribed from the pre-split registry).

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


def _binary_tree_level_order_traversal_spine(n: int) -> list | None:
    """A chain of n nodes, each with only a left child (values 0..n-1)."""
    node: list | None = None
    for value in range(n - 1, -1, -1):
        node = [value, node, None]
    return node


def _binary_tree_level_order_traversal_complete(n: int) -> list | None:
    """A complete tree of exactly n nodes whose values stay inside the
    statement's [-1000, 1000]. It is the shared _complete_tree, relabelled: that
    helper names node i with the value i, which leaves the stated range above
    n = 1001 -- and a profiler input's *values* must respect the statement, not
    just its shape (the v0.12 products_of_array_except_self lesson)."""
    nodes: list[list | None] = [None] * n
    for i in range(n - 1, -1, -1):  # bottom-up: children finalized first
        left, right = 2 * i + 1, 2 * i + 2
        nodes[i] = [
            i % 2001 - 1000,
            nodes[left] if left < n else None,
            nodes[right] if right < n else None,
        ]
    return nodes[0]


@oracle("binary-tree-level-order-traversal")
def _binary_tree_level_order_traversal_oracle(root: list | None) -> list[list[int]]:
    """Brute force: one full depth-first walk (explicit stack, preorder left to
    right) that appends every node's value to its own depth's list. Nothing here
    derives the levels from a queue, so it is a genuinely different traversal
    from the reference's level sweep. Depths are first reached in increasing
    order -- a node at depth d is only reached through its ancestors -- so the
    buckets are appended to in level order."""
    out: list[list[int]] = []
    if root is None:
        return out
    stack = [(root, 0)]
    while stack:
        node, depth = stack.pop()
        if depth == len(out):
            out.append([node[0]])
        else:
            out[depth].append(node[0])
        if node[2] is not None:
            stack.append((node[2], depth + 1))  # pushed first, so left pops first
        if node[1] is not None:
            stack.append((node[1], depth + 1))
    return out


@cases("binary-tree-level-order-traversal")
def _binary_tree_level_order_traversal_case(
    n: int, rng: random.Random
) -> tuple[list, list[list[int]]]:
    n = max(0, min(n, 12))  # the statement allows an empty tree (0 nodes)
    if n and rng.random() < 0.25:
        # One node per level: the degenerate shape _random_tree's halving budget
        # cannot build, and the one that breaks a level sweep which assumes a
        # left child comes with a right child.
        tree = _binary_tree_level_order_traversal_spine(n)
    else:
        tree = _random_tree(rng, n)
    return [tree], _binary_tree_level_order_traversal_oracle(tree)


@inputs("binary-tree-level-order-traversal")
def _binary_tree_level_order_traversal_profiler(n: int, rng: random.Random) -> list:
    """A complete tree of n nodes: every one of them is visited and the output
    holds all n values, so no implementation can early-exit, and both a BFS and
    a DFS pay for the whole tree. The shape is complete rather than a spine so a
    recursive solution sees a depth of ~11 rather than n, and probe_max_n = 2000
    keeps the measured tree inside the statement's own node bound."""
    # No internal cap: the live ladder is already cut at the statement's 2000
    # nodes by probe_max_n, and a second clamp here would silently rebuild the
    # same tree for every ladder size above it (measured -- see the notes).
    return [_binary_tree_level_order_traversal_complete(max(1, n))]


@reference("binary-tree-level-order-traversal")
def _binary_tree_level_order_traversal_reference(root: list | None) -> list[list[int]]:
    """The canonical BFS: one queue, and each round of the outer loop drains
    exactly one level (len(queue) - head is that level's width). O(n) time,
    O(n) space including the output."""
    if root is None:
        return []
    out: list[list[int]] = []
    queue: list[list] = [root]
    head = 0
    while head < len(queue):
        level: list[int] = []
        for _ in range(len(queue) - head):
            node = queue[head]
            head += 1
            level.append(node[0])
            if node[1] is not None:
                queue.append(node[1])
            if node[2] is not None:
                queue.append(node[2])
        out.append(level)
    return out


@measure("binary-tree-level-order-traversal")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
