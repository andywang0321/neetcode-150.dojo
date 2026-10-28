"""QUARANTINED assessment for `same-tree` (transcribed from the pre-split registry).

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


def _same_tree_nodes(tree: list | None) -> list[list]:
    """Every node of a tree, in level order; empty for the empty tree."""
    nodes: list[list] = []
    queue, i = [tree], 0
    while i < len(queue):
        node = queue[i]
        i += 1
        if node is None:
            continue
        nodes.append(node)
        queue.append(node[1])
        queue.append(node[2])
    return nodes


@oracle("same-tree")
def _same_tree_oracle(p: list | None, q: list | None) -> bool:
    """Brute force by canonical form: flatten each tree to its preorder walk
    with an explicit null marker for every missing child, then compare. That
    serialization determines a binary tree uniquely, so equality of the two
    canonical forms is exactly "structurally identical, same values". Iterative
    and one-sided — no simultaneous recursion, no mutation — so it is a
    different program from the reference. Total on two empty trees (both
    flatten to [None])."""

    def flatten(node: list | None) -> list:
        out: list = []
        stack = [node]
        while stack:
            current = stack.pop()
            if current is None:
                out.append(None)  # the marker that makes the walk unambiguous
                continue
            out.append(current[0])
            stack.append(current[2])  # right first, so left is popped first
            stack.append(current[1])
        return out

    return flatten(p) == flatten(q)


@cases("same-tree")
def _same_tree_case(n: int, rng: random.Random) -> tuple[list, bool]:
    n = max(0, min(n, 12))  # the statement allows 0..100 nodes per tree; 0 is empty
    # Two _random_tree calls on the SAME seed build the same tree twice, as two
    # distinct objects: a random pair would almost never be equal, and sharing
    # one object would let a `p is q` shortcut pass. Values are 0..9, inside
    # -10^4..10^4.
    seed = rng.randrange(1 << 31)
    p = _random_tree(random.Random(seed), n)
    q = _random_tree(random.Random(seed), n)
    nodes = _same_tree_nodes(q)
    roll = rng.random()
    if not nodes or roll < 1 / 3:
        pass  # identical (example 1's shape; the whole tree must be compared)
    elif roll < 2 / 3:
        rng.choice(nodes)[0] += 1  # same structure, one different value
    else:
        # A structural difference with the same value multiset — example 3's
        # shape. Only a node whose two subtrees actually differ will do: swapping
        # two equal subtrees is invisible, so that case falls back to a value.
        swappable = [node for node in nodes if node[1] != node[2]]
        if swappable:
            node = rng.choice(swappable)
            node[1], node[2] = node[2], node[1]
        else:
            rng.choice(nodes)[0] += 1
    return [p, q], _same_tree_oracle(p, q)


@inputs("same-tree")
def _same_tree_profiler(n: int, rng: random.Random) -> list:
    # Two IDENTICAL complete trees of ~n/2 nodes each, from two calls so they are
    # equal but distinct objects (one shared object would let `p is q` pass at
    # scale). Identical is the worst case in work: the answer is true, so no
    # implementation can stop before the last node has been compared — a pair
    # that differs somewhere would let a lucky traversal order finish early.
    # Depth is log2(n/2), 12 at the ladder's top, and values are _complete_tree's
    # 0..n/2-1, inside the statement's -10^4..10^4.
    n = max(2, min(n, 10_000))  # the statement's own bound is 10^4 nodes per tree
    half = n // 2
    return [_complete_tree(half), _complete_tree(half)]


@reference("same-tree")
def _same_tree_reference(p: list | None, q: list | None) -> bool:
    """The canonical solution: walk both trees together, so the two empty cases
    are the same tree and any structural difference (one side None, the other a
    subtree) is a difference. O(min(n, m)) time, O(h) stack."""
    if p is None or q is None:
        return p is None and q is None
    if p[0] != q[0]:
        return False
    return _same_tree_reference(p[1], q[1]) and _same_tree_reference(p[2], q[2])


@measure("same-tree")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
