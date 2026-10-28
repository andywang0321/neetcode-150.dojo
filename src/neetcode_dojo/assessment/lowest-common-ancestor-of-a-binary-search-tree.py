"""QUARANTINED assessment for `lowest-common-ancestor-of-a-binary-search-tree` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


def _lowest_common_ancestor_of_a_binary_search_tree_insert(
    root: list | None, value: int
) -> list:
    """Iterative BST insert; the generator only ever inserts distinct values, so
    the result is a BST with exactly one node per value."""
    node = [value, None, None]
    if root is None:
        return node
    cur = root
    while True:
        if value < cur[0]:
            if cur[1] is None:
                cur[1] = node
                return root
            cur = cur[1]
        else:
            if cur[2] is None:
                cur[2] = node
                return root
            cur = cur[2]


def _lowest_common_ancestor_of_a_binary_search_tree_values(root: list | None) -> list[int]:
    """Every value in the tree, in preorder. The generator draws p and q from
    this list, which is how "p and q will exist in the BST" is upheld by
    construction rather than by hope."""
    out: list[int] = []
    stack = [root]
    while stack:
        node = stack.pop()
        if node is None:
            continue
        out.append(node[0])
        stack.append(node[1])
        stack.append(node[2])
    return out


def _lowest_common_ancestor_of_a_binary_search_tree_balanced(values: list[int]) -> list | None:
    """A height-balanced BST over distinct sorted values, built middle-out:
    height = log2(n), which keeps recursive student solutions far inside the
    recursion limit at every probe size."""
    if not values:
        return None
    mid = len(values) // 2
    return [
        values[mid],
        _lowest_common_ancestor_of_a_binary_search_tree_balanced(values[:mid]),
        _lowest_common_ancestor_of_a_binary_search_tree_balanced(values[mid + 1 :]),
    ]


@oracle("lowest-common-ancestor-of-a-binary-search-tree")
def _lowest_common_ancestor_of_a_binary_search_tree_oracle(
    root: list | None, p: int, q: int
) -> int | None:
    """Brute force that never looks at the BST ordering: record every node's
    parent, walk p's ancestor chain up to the root, then climb from q to the
    first node on that chain -- the LCA by definition.

    Ignoring the ordering is the point. The reference descends by comparing
    values, so the two agree only when the generated tree really is a BST with
    unique values: a generator that broke either guarantee would show up as
    oracle/reference disagreement on every generated case rather than as a
    silent wrong expected value.

    Values are the node identity here (the statement guarantees they are
    unique), which is also how p and q arrive: as the two nodes' values.
    """
    if root is None:
        return None
    parent: dict[int, int | None] = {root[0]: None}
    stack = [root]
    while stack:
        node = stack.pop()
        for child in (node[1], node[2]):
            if child is not None:
                parent[child[0]] = node[0]
                stack.append(child)
    if p not in parent or q not in parent:
        return None  # the statement guarantees both exist; stay total anyway
    ancestors = set()
    cur: int | None = p
    while cur is not None:
        ancestors.add(cur)
        cur = parent[cur]
    cur = q
    while cur not in ancestors:
        cur = parent[cur]
    return cur


@cases("lowest-common-ancestor-of-a-binary-search-tree")
def _lowest_common_ancestor_of_a_binary_search_tree_case(
    n: int, rng: random.Random
) -> tuple[list, int]:
    n = max(2, min(n, 12))  # the statement's floor: the tree has >= 2 nodes
    if rng.random() < 0.25:
        # The statement's own value extremes, so the boundary comparisons are
        # exercised (no other value is anywhere near them).
        values = [-(10**9), 10**9] + rng.sample(range(-38, 39), n - 2)
    else:
        values = rng.sample(range(-30, 31), n)
    if rng.random() < 0.25:
        values.sort()  # ascending insertion order: a right-leaning chain
    root = None
    for value in values:
        root = _lowest_common_ancestor_of_a_binary_search_tree_insert(root, value)
    p, q = rng.sample(_lowest_common_ancestor_of_a_binary_search_tree_values(root), 2)
    return [root, p, q], _lowest_common_ancestor_of_a_binary_search_tree_oracle(root, p, q)


@inputs("lowest-common-ancestor-of-a-binary-search-tree")
def _lowest_common_ancestor_of_a_binary_search_tree_profiler(
    n: int, rng: random.Random
) -> list:
    """A balanced BST of n distinct values (0..n-1, inside the statement's
    +-10^9) with p and q at the bottom of the left spine: p is the deepest
    left-spine node and q is its parent, so the intended descent has to walk the
    whole height instead of stopping at the root, and the parent-walk oracle
    still traverses every node. Nothing early-exits on either side.

    The tree is balanced rather than a spine because the declared target is O(h)
    and a spine of 6400 nodes would exceed Python's recursion limit for any
    recursive student solution -- the corpus's existing tree profilers are
    balanced for the same reason. p != q and both values exist by construction.
    """
    size = max(2, n)
    root = _lowest_common_ancestor_of_a_binary_search_tree_balanced(list(range(size)))
    child, parent = root, root[0]
    while child[1] is not None:
        parent = child[0]
        child = child[1]
    return [root, child[0], parent]


@reference("lowest-common-ancestor-of-a-binary-search-tree")
def _lowest_common_ancestor_of_a_binary_search_tree_reference(
    root: list | None, p: int, q: int
) -> int | None:
    """The intended O(h) / O(1) descent: while both targets lie on the same side
    of the current node, follow that side. The first node that separates them --
    or that is one of them, since a node is a descendant of itself -- is the
    lowest common ancestor. Iterative, so no input can exhaust the stack."""
    node = root
    while node is not None:
        value = node[0]
        if p < value and q < value:
            node = node[1]
        elif p > value and q > value:
            node = node[2]
        else:
            return value
    return None


@measure("lowest-common-ancestor-of-a-binary-search-tree")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
