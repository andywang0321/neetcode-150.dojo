"""QUARANTINED assessment for `construct-binary-tree-from-preorder-and-inorder-traversal` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


def _construct_binary_tree_from_preorder_and_inorder_traversal_shape(
    rng: random.Random, n: int
) -> list | None:
    """A random binary-tree SHAPE with exactly n nodes ([None placeholder, left,
    right]; None = missing child). One draw in four is one of the two degenerate
    chains -- shapes a uniformly random split almost never reaches and the ones a
    "the tree is roughly balanced" assumption breaks on."""
    if n <= 0:
        return None
    if n > 2 and rng.random() < 0.25:
        if rng.random() < 0.5:
            return [None, _construct_binary_tree_from_preorder_and_inorder_traversal_shape(rng, n - 1), None]
        return [None, None, _construct_binary_tree_from_preorder_and_inorder_traversal_shape(rng, n - 1)]
    left = rng.randrange(n)  # 0..n-1 nodes go left, the rest right
    return [
        None,
        _construct_binary_tree_from_preorder_and_inorder_traversal_shape(rng, left),
        _construct_binary_tree_from_preorder_and_inorder_traversal_shape(rng, n - 1 - left),
    ]


def _construct_binary_tree_from_preorder_and_inorder_traversal_label(
    node: list | None, values
) -> list | None:
    """Fill a shape with `values` in preorder, so the labelled tree's own
    preorder traversal IS the sequence that was handed in."""
    if node is None:
        return None
    return [
        next(values),
        _construct_binary_tree_from_preorder_and_inorder_traversal_label(node[1], values),
        _construct_binary_tree_from_preorder_and_inorder_traversal_label(node[2], values),
    ]


def _construct_binary_tree_from_preorder_and_inorder_traversal_preorder(
    node: list | None,
) -> list[int]:
    if node is None:
        return []
    return (
        [node[0]]
        + _construct_binary_tree_from_preorder_and_inorder_traversal_preorder(node[1])
        + _construct_binary_tree_from_preorder_and_inorder_traversal_preorder(node[2])
    )


def _construct_binary_tree_from_preorder_and_inorder_traversal_inorder(
    node: list | None,
) -> list[int]:
    if node is None:
        return []
    return (
        _construct_binary_tree_from_preorder_and_inorder_traversal_inorder(node[1])
        + [node[0]]
        + _construct_binary_tree_from_preorder_and_inorder_traversal_inorder(node[2])
    )


def _construct_binary_tree_from_preorder_and_inorder_traversal_balanced(
    n: int,
) -> list | None:
    """A complete (balanced) tree with exactly n nodes, labelled 0..n-1. Built
    here rather than reusing the registry's `_complete_tree` so the fragment's
    blocks are self-contained (the self-check in AUTHORING.md execs them with
    only `random`/`math` in scope)."""
    if n <= 0:
        return None
    nodes: list[list | None] = [None] * n
    for i in range(n - 1, -1, -1):
        left, right = 2 * i + 1, 2 * i + 2
        nodes[i] = [i, nodes[left] if left < n else None, nodes[right] if right < n else None]
    return nodes[0]


@oracle("construct-binary-tree-from-preorder-and-inorder-traversal")
def _construct_binary_tree_from_preorder_and_inorder_traversal_oracle(
    preorder: list[int], inorder: list[int]
) -> list | None:
    """Brute force: the root is the front of preorder, a linear scan finds it in
    inorder, and the two slices recurse. The scan is the brute-force part -- the
    intended solution precomputes those positions once. O(n^2) time and space
    (every level copies its slices); total on the empty pair, which the
    statement's length >= 1 excludes."""
    if not preorder:
        return None
    root = preorder[0]
    split = inorder.index(root)  # the statement's values are unique: exactly one hit
    return [
        root,
        _construct_binary_tree_from_preorder_and_inorder_traversal_oracle(
            preorder[1 : split + 1], inorder[:split]
        ),
        _construct_binary_tree_from_preorder_and_inorder_traversal_oracle(
            preorder[split + 1 :], inorder[split + 1 :]
        ),
    ]


@cases("construct-binary-tree-from-preorder-and-inorder-traversal")
def _construct_binary_tree_from_preorder_and_inorder_traversal_case(
    n: int, rng: random.Random
) -> tuple[list, list]:
    n = max(1, min(n, 12))  # the statement's own floor: 1 <= preorder.length
    # A REAL tree's two traversals, so every generated pair is valid by
    # construction. `values` is a sample of DISTINCT ints inside the statement's
    # -3000..3000 -- the statement promises unique values, and distinctness is
    # also what makes the (preorder, inorder) pair determine exactly one tree
    # (which is why the case can be judged by strict equality). Labelling in
    # preorder makes the emitted preorder the sampled list itself.
    values = rng.sample(range(-3000, 3001), n)
    tree = _construct_binary_tree_from_preorder_and_inorder_traversal_label(
        _construct_binary_tree_from_preorder_and_inorder_traversal_shape(rng, n), iter(values)
    )
    return [
        _construct_binary_tree_from_preorder_and_inorder_traversal_preorder(tree),
        _construct_binary_tree_from_preorder_and_inorder_traversal_inorder(tree),
    ], tree


@inputs("construct-binary-tree-from-preorder-and-inorder-traversal")
def _construct_binary_tree_from_preorder_and_inorder_traversal_profiler(
    n: int, rng: random.Random
) -> list:
    # A complete (balanced) tree of exactly n nodes, with distinct values inside
    # the statement's -3000..3000 assigned in preorder. Balanced on purpose: a
    # deep chain is the naive implementation's real worst case, but at 3000 nodes
    # it is also deeper than CPython's recursion limit, so it would measure the
    # interpreter's stack for every recursive solution -- the reference included
    # -- instead of the algorithm (the same reason _diameter_profiler is a
    # complete tree). Neither implementation can early-exit: both walk all of
    # both arrays at every size. probe_max_n keeps the ladder inside the
    # statement's own 3000-node cap, so the value range holds at every measured
    # size.
    size = max(1, min(n, 3000))
    values = rng.sample(range(-3000, 3001), size)
    tree = _construct_binary_tree_from_preorder_and_inorder_traversal_label(
        _construct_binary_tree_from_preorder_and_inorder_traversal_balanced(size), iter(values)
    )
    return [
        _construct_binary_tree_from_preorder_and_inorder_traversal_preorder(tree),
        _construct_binary_tree_from_preorder_and_inorder_traversal_inorder(tree),
    ]


@reference("construct-binary-tree-from-preorder-and-inorder-traversal")
def _construct_binary_tree_from_preorder_and_inorder_traversal_reference(
    preorder: list[int], inorder: list[int]
) -> list | None:
    """The intended O(n): one pass maps every value to its inorder position, then
    a recursive build consumes preorder left to right, using the current
    subtree's inorder bounds to know where it ends. No slicing and no rescanning,
    so it is linear in the number of nodes."""
    position = {value: i for i, value in enumerate(inorder)}
    cursor = 0

    def build(lo: int, hi: int) -> list | None:
        nonlocal cursor
        if lo > hi:
            return None  # an empty inorder range is a missing child
        value = preorder[cursor]
        cursor += 1
        mid = position[value]
        left = build(lo, mid - 1)
        right = build(mid + 1, hi)
        return [value, left, right]

    return build(0, len(inorder) - 1)


@measure("construct-binary-tree-from-preorder-and-inorder-traversal")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
