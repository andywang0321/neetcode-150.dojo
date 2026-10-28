"""QUARANTINED assessment for `binary-tree-right-side-view` (transcribed from the pre-split registry).

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


def _binary_tree_right_side_view_spine(n: int) -> list | None:
    """A chain of n nodes, each with only a left child (values 0..n-1): every
    level holds a single node, so all n of them are visible from the right."""
    node: list | None = None
    for value in range(n - 1, -1, -1):
        node = [value, node, None]
    return node


def _binary_tree_right_side_view_complete(n: int) -> list | None:
    """A complete tree of exactly n nodes whose values stay inside the
    statement's [-100, 100]. It is the shared _complete_tree, relabelled: that
    helper names node i with the value i, which leaves the stated range above
    n = 101 -- and a profiler input's *values* must respect the statement, not
    just its shape (the v0.12 products_of_array_except_self lesson)."""
    nodes: list[list | None] = [None] * n
    for i in range(n - 1, -1, -1):  # bottom-up: children finalized first
        left, right = 2 * i + 1, 2 * i + 2
        nodes[i] = [
            i % 201 - 100,
            nodes[left] if left < n else None,
            nodes[right] if right < n else None,
        ]
    return nodes[0]


@oracle("binary-tree-right-side-view")
def _binary_tree_right_side_view_oracle(root: list | None) -> list[int]:
    """Brute force: one full depth-first walk (explicit stack, preorder left to
    right) that writes every node's value into its own depth's slot and keeps
    the last write. The last node visited at a depth is that depth's rightmost
    one, and nothing here derives the answer from a level queue, so the
    differential against the reference's level sweep is real."""
    out: list[int] = []
    if root is None:
        return out
    stack = [(root, 0)]
    while stack:
        node, depth = stack.pop()
        if depth == len(out):
            out.append(node[0])  # a depth is first reached through its ancestors
        else:
            out[depth] = node[0]
        if node[2] is not None:
            stack.append((node[2], depth + 1))  # pushed first, so left pops first
        if node[1] is not None:
            stack.append((node[1], depth + 1))
    return out


@cases("binary-tree-right-side-view")
def _binary_tree_right_side_view_case(n: int, rng: random.Random) -> tuple[list, list[int]]:
    n = max(0, min(n, 12))  # the statement allows an empty tree (0 nodes)
    if n and rng.random() < 0.25:
        # One node per level: the degenerate shape _random_tree's halving budget
        # cannot build, where the right-side view is the whole tree.
        tree = _binary_tree_right_side_view_spine(n)
    else:
        tree = _random_tree(rng, n)
    return [tree], _binary_tree_right_side_view_oracle(tree)


@inputs("binary-tree-right-side-view")
def _binary_tree_right_side_view_profiler(n: int, rng: random.Random) -> list:
    """A complete tree of n nodes: which node is rightmost on a level can only
    be known after visiting that level, so a BFS and a DFS both walk all n nodes
    and neither can early-exit. The shape is complete rather than a spine so a
    recursive solution stays shallow, and n is capped at the statement's own
    100 nodes by probe_max_n (the default ladder would have measured 6400)."""
    # No internal cap: probe_max_n = 100 already cuts the live ladder at the
    # statement's own node bound, and a second clamp here would silently rebuild
    # the same tree for every ladder size above it (measured -- see the notes).
    return [_binary_tree_right_side_view_complete(max(1, n))]


@reference("binary-tree-right-side-view")
def _binary_tree_right_side_view_reference(root: list | None) -> list[int]:
    """The canonical level sweep: a BFS queue drained one level at a time, taking
    the last node dequeued on each level -- the one that is visible from the
    right. O(n) time, O(n) space."""
    if root is None:
        return []
    out: list[int] = []
    queue: list[list] = [root]
    head = 0
    while head < len(queue):
        last = root[0]
        for _ in range(len(queue) - head):
            node = queue[head]
            head += 1
            last = node[0]
            if node[1] is not None:
                queue.append(node[1])
            if node[2] is not None:
                queue.append(node[2])
        out.append(last)  # every level has at least one node
    return out


@measure("binary-tree-right-side-view")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
