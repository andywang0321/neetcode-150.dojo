"""QUARANTINED assessment for `subtree-of-another-tree` (transcribed from the pre-split registry).

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


def _subtree_of_another_tree_same(a: list | None, b: list | None) -> bool:
    """Structural equality of two nested-list trees, iteratively."""
    pairs = [(a, b)]
    while pairs:
        x, y = pairs.pop()
        if x is None or y is None:
            if (x is None) != (y is None):
                return False
            continue
        if x[0] != y[0]:
            return False
        pairs.append((x[1], y[1]))
        pairs.append((x[2], y[2]))
    return True


def _subtree_of_another_tree_nodes(root: list | None) -> list[list]:
    """Every non-empty node of a nested-list tree, in preorder."""
    out: list[list] = []
    stack = [root]
    while stack:
        node = stack.pop()
        if node is None:
            continue
        out.append(node)
        stack.append(node[1])
        stack.append(node[2])
    return out


def _subtree_of_another_tree_clone(node: list | None) -> list | None:
    """A structural copy, so a generated case never aliases root's own nodes as
    subRoot (the two arguments are independent trees either way, but a shared
    object in a stored case is a trap for whoever reads it next)."""
    if node is None:
        return None
    return [
        node[0],
        _subtree_of_another_tree_clone(node[1]),
        _subtree_of_another_tree_clone(node[2]),
    ]


@oracle("subtree-of-another-tree")
def _subtree_of_another_tree_oracle(root: list | None, sub_root: list | None) -> bool:
    """Brute force: every node of root is a candidate, and a candidate qualifies
    when its subtree is structurally identical to subRoot. Both walks use an
    explicit stack, so the oracle also survives the probe's largest input when a
    mismatch has to be confirmed at that size (no recursion limit anywhere)."""
    if sub_root is None:
        return True  # the empty tree is a subtree of every tree (never generated)
    stack = [root]
    while stack:
        node = stack.pop()
        if node is None:
            continue
        if _subtree_of_another_tree_same(node, sub_root):
            return True
        stack.append(node[1])
        stack.append(node[2])
    return False


@cases("subtree-of-another-tree")
def _subtree_of_another_tree_case(n: int, rng: random.Random) -> tuple[list, bool]:
    n = max(1, min(n, 12))  # the statement's floor: both trees have >= 1 node
    root = _random_tree(rng, n)
    if rng.random() < 0.5:
        # A true case by construction: subRoot is the subtree of a node of root
        # (the root itself when the root node is drawn -- the statement's own
        # "the tree could also be considered as a subtree of itself").
        node = rng.choice(_subtree_of_another_tree_nodes(root))
        sub = _subtree_of_another_tree_clone(node)
    else:
        # An independent tree, which may still occur in root by accident: the
        # expected value always comes from the oracle, never from this branch.
        sub = _random_tree(rng, max(1, min(n, 12)))
    return [root, sub], _subtree_of_another_tree_oracle(root, sub)


@inputs("subtree-of-another-tree")
def _subtree_of_another_tree_profiler(n: int, rng: random.Random) -> list:
    """A complete root tree of n nodes paired with a 3-node subRoot that cannot
    occur in it: root holds the values 0..n-1 (n <= 2000 here) and subRoot's root
    value is 10_000, the statement's own upper bound for a value, which root
    never holds. No candidate can match, so the compare-each-node solution walks
    all n nodes (nothing early-exits) and a serialization solution scans its
    whole encoding. The tree is complete rather than a spine so that recursive
    student solutions stay far inside the recursion limit, and its size is capped
    at the statement's 2000 nodes by probe_max_n."""
    # No size clamp beyond the sentinel's own invariant: a complete tree of
    # 0..size-1 nodes holds 10_000 only once size > 10_000, and every real ladder
    # is far below that (probe_max_n = 2000 here, 6400 by default). An internal
    # clamp would be worse than useless -- see the notes.
    size = max(1, min(n, 10_000))
    return [
        _complete_tree(size),
        [10_000, [9_999, None, None], [9_998, None, None]],
    ]


@reference("subtree-of-another-tree")
def _subtree_of_another_tree_reference(root: list | None, sub_root: list | None) -> bool:
    """The canonical intended solution: compare every node of root with subRoot,
    structurally, recursing into both children when the comparison fails --
    O(n * m) worst case, which is the declared target, and O(n + m) on a balanced
    pair. Self-contained: the two helpers are nested, because the probe runs this
    function's own source in its own subprocess."""
    def same(a: list | None, b: list | None) -> bool:
        if a is None or b is None:
            return a is None and b is None
        return a[0] == b[0] and same(a[1], b[1]) and same(a[2], b[2])

    def walk(node: list | None) -> bool:
        if node is None:
            return False
        return same(node, sub_root) or walk(node[1]) or walk(node[2])

    if sub_root is None:
        return True
    return walk(root)


@measure("subtree-of-another-tree")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
