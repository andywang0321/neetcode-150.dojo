"""QUARANTINED assessment for `binary-tree-maximum-path-sum` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


def _binary_tree_maximum_path_sum_shape(
    rng: random.Random, n: int, low: int, high: int
) -> list | None:
    """A random tree with exactly n nodes and values in [low, high]. One draw in
    four is a chain (left-only or right-only): on a chain the answer is the best
    contiguous-run sum, a different exercise from a branching tree, and the shape
    a uniformly random split almost never reaches."""
    if n <= 0:
        return None
    if n > 2 and rng.random() < 0.25:
        if rng.random() < 0.5:
            return [rng.randint(low, high), _binary_tree_maximum_path_sum_shape(rng, n - 1, low, high), None]
        return [rng.randint(low, high), None, _binary_tree_maximum_path_sum_shape(rng, n - 1, low, high)]
    left = rng.randrange(n)  # 0..n-1 nodes go left, the rest right
    return [
        rng.randint(low, high),
        _binary_tree_maximum_path_sum_shape(rng, left, low, high),
        _binary_tree_maximum_path_sum_shape(rng, n - 1 - left, low, high),
    ]


@oracle("binary-tree-maximum-path-sum")
def _binary_tree_maximum_path_sum_oracle(root: list | None) -> int:
    """Brute force: a path is fixed by its two endpoints, so try every ordered
    pair of nodes and add up the unique path between them -- the values from `a`
    up to the lowest common ancestor (the shared prefix of the two root paths
    identifies it) plus the values from there down to `b`. `a == b` covers the
    single-node path, so an ALL-NEGATIVE tree is answered with its largest (least
    negative) node value and never with 0: "the maximum path sum of any
    non-empty path" is a maximum over actual paths. O(n^2 * height), and
    deliberately not the intended DP; total on the empty tree, which the
    statement's "at least one node" excludes."""
    ids: dict[int, list[int]] = {}
    values: dict[int, list[int]] = {}
    nodes: list = []

    def walk(node: list | None, path_ids: list[int], path_values: list[int]) -> None:
        if node is None:
            return
        here_ids = path_ids + [id(node)]
        here_values = path_values + [node[0]]
        ids[id(node)] = here_ids
        values[id(node)] = here_values
        nodes.append(node)
        walk(node[1], here_ids, here_values)
        walk(node[2], here_ids, here_values)

    walk(root, [], [])
    best = None
    for a in nodes:
        a_ids, a_values = ids[id(a)], values[id(a)]
        for b in nodes:
            b_ids, b_values = ids[id(b)], values[id(b)]
            shared = 0
            while (
                shared < len(a_ids)
                and shared < len(b_ids)
                and a_ids[shared] == b_ids[shared]
            ):
                shared += 1  # ids, never values: equal values can sit in two branches
            # shared >= 1 always (both paths start at the root), so shared - 1 is
            # the LCA: [LCA..a] from a's path plus [..b] below the LCA from b's.
            total = sum(a_values[shared - 1 :]) + sum(b_values[shared:])
            best = total if best is None else max(best, total)
    return 0 if best is None else best


@cases("binary-tree-maximum-path-sum")
def _binary_tree_maximum_path_sum_case(n: int, rng: random.Random) -> tuple[list, int]:
    n = max(1, min(n, 12))  # the statement's own floor: at least one node
    # One draw in three is an ALL-NEGATIVE tree (values in -1000..-1) on purpose.
    # "Any non-empty path" means the answer there is the largest node value, never
    # 0 -- precisely the case a `best = 0` (or `max(0, ...)`-seeded) accumulator
    # gets wrong, and the self-check asserts both that such a case was generated
    # and that its expected answer is negative.
    if rng.random() < 0.34:
        low, high = -1000, -1
    elif rng.random() < 0.5:
        low, high = -9, 9  # small values: zeros, duplicates, near-ties
    else:
        low, high = -1000, 1000  # the statement's full value range
    tree = _binary_tree_maximum_path_sum_shape(rng, n, low, high)
    return [tree], _binary_tree_maximum_path_sum_oracle(tree)


@inputs("binary-tree-maximum-path-sum")
def _binary_tree_maximum_path_sum_profiler(n: int, rng: random.Random) -> list:
    # A complete (balanced) tree of exactly n nodes with ALL-NEGATIVE values in
    # the statement's -1000..-1 range. Balanced so a recursive solution measures
    # its algorithm rather than CPython's stack; no implementation can
    # early-exit (no node's subtree gain is known before it is visited); and with
    # every value negative the answer is the largest (least negative) node value,
    # so the classic `best = 0` seed also surfaces AT SCALE as an output mismatch
    # against the reference, not only in the small generated cases. Values cycle
    # -1..-1000 and repeat, which the statement's constraints allow.
    counter = [0]

    def build(i: int) -> list | None:
        if i >= n:
            return None
        value = -(1 + counter[0] % 1000)
        counter[0] += 1
        return [value, build(2 * i + 1), build(2 * i + 2)]

    return [build(0)]


@reference("binary-tree-maximum-path-sum")
def _binary_tree_maximum_path_sum_reference(root: list | None) -> int:
    """The intended O(n) time / O(h) space: one post-order walk. `gain(node)` is
    the best sum of a downward path that STARTS at `node` and may stop anywhere
    below it, so a negative branch can simply be dropped (`max(0, ...)`) -- a path
    is free to end before it. The best path THROUGH a node is the node plus the
    best gain on each side, which is what updates the answer. `best` starts at
    None rather than 0: for an all-negative tree the answer is the largest node
    value, because the statement maximizes over NON-EMPTY paths (a 0 seed silently
    invents the empty path)."""
    best = None

    def gain(node: list | None) -> int:
        nonlocal best
        if node is None:
            return 0
        left = gain(node[1])
        right = gain(node[2])
        through = node[0] + max(left, 0) + max(right, 0)
        best = through if best is None else max(best, through)
        return node[0] + max(left, right, 0)  # downward: at most one side continues

    gain(root)
    return 0 if best is None else best


@measure("binary-tree-maximum-path-sum")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
