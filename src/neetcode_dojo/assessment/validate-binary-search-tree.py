"""QUARANTINED assessment for `validate-binary-search-tree` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


def _validate_binary_search_tree_all_less(node: list | None, bound: int) -> bool:
    if node is None:
        return True
    return (
        node[0] < bound
        and _validate_binary_search_tree_all_less(node[1], bound)
        and _validate_binary_search_tree_all_less(node[2], bound)
    )


def _validate_binary_search_tree_all_greater(node: list | None, bound: int) -> bool:
    if node is None:
        return True
    return (
        node[0] > bound
        and _validate_binary_search_tree_all_greater(node[1], bound)
        and _validate_binary_search_tree_all_greater(node[2], bound)
    )


def _validate_binary_search_tree_build(rng: random.Random, values: list[int]) -> list | None:
    """A valid BST over ``values`` (ascending and distinct): the root of each
    range is picked at random, which is the shape a uniformly random insertion
    order produces. Every root is strictly inside the range it splits, so the
    result is a BST of exactly len(values) nodes whatever the picks are."""
    if not values:
        return None
    root = rng.randrange(len(values))
    return [
        values[root],
        _validate_binary_search_tree_build(rng, values[:root]),
        _validate_binary_search_tree_build(rng, values[root + 1 :]),
    ]


def _validate_binary_search_tree_values(rng: random.Random, size: int) -> list[int]:
    """``size`` distinct ascending values inside the statement's
    [-2^31, 2^31 - 1]: a small range most of the time, and the range's two ends
    a quarter of the time — a solution that seeds "no bound yet" with the bound
    itself instead of None only fails on a value that reaches it."""
    if rng.random() < 0.25:
        pool = [-(2**31) + i for i in range(6)] + [2**31 - 1 - i for i in range(6)]
        return sorted(rng.sample(pool, size))
    return sorted(rng.sample(range(-60, 61), size))


def _validate_binary_search_tree_local_break(rng: random.Random, root: list) -> list:
    """Copy the root's value into one of its children: the very comparison a
    parent-only check looks at now fails (a left child equal to its parent, or a
    right child equal to it), so this is the trap's complement — an invalid tree
    the shallow check does reject. Needs two or more nodes: a rooted tree that
    size always has a root with a child."""
    child = rng.choice([side for side in (1, 2) if root[side] is not None])
    root[child][0] = root[0]
    return root


def _validate_binary_search_tree_trap(rng: random.Random, size: int) -> list:
    """A tree of exactly ``size`` nodes that EVERY parent-only check accepts and
    that is not a BST — the case this problem is famous for.

    A root-to-node path is built first, every value strictly inside the interval
    the path implies. Step one takes a wide gap and step two turns (right then
    left, or left then right), and after a turn the path implies an interval
    with BOTH ends known: the root's value on one side and the previous node's
    on the other. The node at the end of the path then takes a value that breaks
    the end its own parent cannot see — a left child a value at or below the
    lower bound (its parent sits above that bound, so the value is still smaller
    than its parent), a right child a value at or above the upper bound. So
    every parent-child comparison in the tree holds while the tree is not a BST.
    The nodes left over hang off the root's free side, where the path implies no
    bound at all, so they are valid: the violation is the only one.
    """
    root_value = rng.randint(-9, 9)
    gap = rng.randint(4, 8)
    first_right = rng.random() < 0.5
    root: list = [root_value, None, None]
    node = root
    lo: int | None = None
    hi: int | None = None
    last_right = first_right
    steps = [first_right, not first_right]  # the turn is what sets both ends
    if size >= 5 and rng.random() < 0.5:
        steps.append(rng.random() < 0.5)  # a third step: the trap at depth 3
    taken = 0  # a step that cannot fit is skipped, so count what was walked
    for right in steps:
        if lo is None and hi is None:  # first step: a gap wide enough to turn in
            low = node[0] + gap if right else node[0] - gap - 4
            high = node[0] + gap + 4 if right else node[0] - gap
        elif right:
            low = node[0] + 2
            high = node[0] + 6 if hi is None else hi - 2
        else:
            high = node[0] - 2
            low = node[0] - 6 if lo is None else lo + 2
        if low > high:
            break  # no integer left strictly inside the interval: the path ends
        value = rng.randint(low, min(high, low + 4))
        child: list = [value, None, None]
        if right:
            node[2] = child
            lo = node[0]
        else:
            node[1] = child
            hi = node[0]
        node, last_right = child, right
        taken += 1
    extra = size - 1 - taken
    if extra > 0:
        if first_right:  # the root's left side: everything below the root is valid
            root[1] = _validate_binary_search_tree_build(
                rng, sorted(rng.sample(range(root_value - 40, root_value), extra))
            )
        else:
            root[2] = _validate_binary_search_tree_build(
                rng, sorted(rng.sample(range(root_value + 1, root_value + 41), extra))
            )
    # Break the end the parent's own comparison cannot see. Both ends are known
    # because the path turned; were this ever to fall through, the tree would
    # simply be a valid one — the expected value is the oracle's either way.
    if last_right and hi is not None:
        node[0] = hi + rng.randint(0, 2)
    elif not last_right and lo is not None:
        node[0] = lo - rng.randint(0, 2)
    return root


def _validate_binary_search_tree_balanced(lo: int, hi: int) -> list | None:
    """A height-balanced BST with the keys lo..hi: the middle key of the range
    goes at the root, so the in-order walk is lo..hi and the tree is a BST by
    construction. (Placed before the profiler block it serves so that EVERY
    helper sits inside the span the fragment's decorators mark for replacement —
    a helper after the last decorated def would be re-inserted twice on the
    assembler's second run.)"""
    if lo > hi:
        return None
    mid = (lo + hi) // 2
    return [
        mid,
        _validate_binary_search_tree_balanced(lo, mid - 1),
        _validate_binary_search_tree_balanced(mid + 1, hi),
    ]


@oracle("validate-binary-search-tree")
def _validate_binary_search_tree_oracle(root: list | None) -> bool:
    """The statement's definition transcribed literally and quadratically: every
    node of the left subtree is strictly smaller, every node of the right
    subtree strictly larger, and both subtrees are BSTs in their own right.
    O(n^2), and it never mentions an interval — which is what makes it a real
    differential against the reference's boundary walk. Total on the empty tree
    (vacuously a BST), which the statement's [1, 10^4] node range excludes."""
    if root is None:
        return True
    return (
        _validate_binary_search_tree_all_less(root[1], root[0])
        and _validate_binary_search_tree_all_greater(root[2], root[0])
        and _validate_binary_search_tree_oracle(root[1])
        and _validate_binary_search_tree_oracle(root[2])
    )


@cases("validate-binary-search-tree")
def _validate_binary_search_tree_case(n: int, rng: random.Random) -> tuple[list, bool]:
    n = max(1, min(n, 12))  # the statement's node range is [1, 10^4]
    roll = rng.random()
    if n >= 3 and roll < 0.5:
        # the parent-only trap half the time (needs depth 2, so three nodes)
        tree = _validate_binary_search_tree_trap(rng, n)
    else:
        tree = _validate_binary_search_tree_build(
            rng, _validate_binary_search_tree_values(rng, n)
        )
        if n >= 2 and roll < 0.7:
            tree = _validate_binary_search_tree_local_break(rng, tree)
    return [tree], _validate_binary_search_tree_oracle(tree)


@inputs("validate-binary-search-tree")
def _validate_binary_search_tree_profiler(n: int, rng: random.Random) -> list:
    """A perfectly height-balanced BST over the keys 0..n-1: exactly n nodes (so
    ~n of input), depth log n, and VALID — which the shared `_complete_tree`
    cannot be here: it labels node i with i, and that array-index labelling puts
    a left child (2i+1) above its own parent, so it is not a BST at all. Valid
    is the worst case on purpose: an invalid tree lets a solution return False
    at the first violation it meets, while a valid one forces every node to be
    examined by both implementations. Values sit inside the statement's
    [-2^31, 2^31 - 1] at every rung of the ladder (6400 at the top, so the
    largest key is 6399). Balanced rather than a chain so a recursive solution
    runs at depth log n instead of n."""
    return [_validate_binary_search_tree_balanced(0, max(1, n) - 1)]


@reference("validate-binary-search-tree")
def _validate_binary_search_tree_reference(root: list | None) -> bool:
    """Canonical O(n) time / O(h) space: one iterative walk carrying the open
    interval (lo, hi) each node must fall inside — lo is the tightest ancestor
    value the path has already exceeded, hi the tightest it has stayed below,
    and None means that end is still unbounded. This is exactly the state a
    parent-only check does not have, which is why it is the reference here.
    Strictness is the statement's own: a value equal to either end is not a BST.
    The explicit stack keeps depth O(h) without Python recursion limits, and the
    empty tree (which the statement's [1, 10^4] range excludes but the dojo
    representation allows) is vacuously a BST."""

    stack: list[tuple[list | None, int | None, int | None]] = [(root, None, None)]
    while stack:
        node, lo, hi = stack.pop()
        if node is None:
            continue
        value = node[0]
        if lo is not None and value <= lo:
            return False
        if hi is not None and value >= hi:
            return False
        stack.append((node[1], lo, value))
        stack.append((node[2], value, hi))
    return True


@measure("validate-binary-search-tree")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
