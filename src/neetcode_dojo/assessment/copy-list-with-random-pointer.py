"""QUARANTINED assessment for `copy-list-with-random-pointer` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, checker, inputs, measure, oracle, reference


@oracle("copy-list-with-random-pointer")
def _copy_list_with_random_pointer_oracle(head: list) -> list:
    """Brute force: a brand-new list object per node and a brand-new pair per
    node, with the random index copied verbatim. Obvious enough to trust as the
    correctness anchor, and structurally blind to how a copy was built."""
    return [[node[0], node[1]] for node in head]


@cases("copy-list-with-random-pointer")
def _copy_list_with_random_pointer_case(n: int, rng: random.Random) -> tuple[list, list, dict]:
    n = max(0, min(n, 12))  # the statement's range is [0, 1000]
    head = []
    for i in range(n):
        # -1 with probability 1/3: null random pointers are as common as the
        # statement's own first example makes them.
        target = -1 if rng.random() < 1 / 3 else rng.randint(0, n - 1)
        head.append([rng.randint(-10**4, 10**4), target])
    return [head], _copy_list_with_random_pointer_oracle(head), {"predicate": "deep_copy_valid"}


@inputs("copy-list-with-random-pointer")
def _copy_list_with_random_pointer_profiler(n: int, rng: random.Random) -> list:
    """n nodes (clamped to the statement's 1000), every random pointer non-null
    and in range, so both implementations walk exactly n nodes and every random
    pointer has to be resolved — a null-heavy list would let a lazy copy skip
    work. Values are spread across the whole -10^4..10^4 range the statement
    allows rather than clustered at 0."""
    size = max(1, min(n, 1000))
    lo, hi = -10**4, 10**4
    head = [[lo + (hi - lo) * i // max(1, size - 1), (i + 1) % size] for i in range(size)]
    return [head]


@reference("copy-list-with-random-pointer")
def _copy_list_with_random_pointer_reference(head: list) -> list:
    if not head:
        return []
    # Hash map pass, the canonical O(n) solution: one new node per original,
    # then the random pointers are rewired through the map, so a random pointer
    # that aims backwards or forwards costs the same.
    copied = {i: [node[0], -1] for i, node in enumerate(head)}
    for i, node in enumerate(head):
        target = node[1]
        copied[i][1] = target if target == -1 else target
    return [copied[i] for i in range(len(head))]


@checker("deep_copy_valid")
def _deep_copy_valid(module, got, args) -> bool:
    """The deep-copy contract for copy-list-with-random-pointer: `got` must be a
    genuine structural copy of the node list (whose `next` chain is the list
    order), sharing no list object with it, and the input must be unchanged.

    The module argument is part of the predicate signature (round-trip checkers
    call a sibling function through it); this checker needs nothing from it --
    that is exactly why it can also grade the oracle's own output, which is how
    tests/test_registry.py exercises a predicate of a problem with no oracle
    needed special-casing.

    Rejections, in the order they are checked:
    - the input is not in the corpus form [[value, random_index], ...];
    - `got` is the input itself (identity) or is not element-by-element equal to
      it (wrong length, a mutated/partial copy, or a copy of the wrong values);
    - `got` shares ANY list object with the input -- the shallow-copy rejection
      (a copy that aliases only the inner [value, random_index] pairs is caught
      even though its next chain looks perfect);
    - the copy is not element-by-element equal to `args[0]` (wrong length, a
      mutated/partial copy, or a copy of the wrong values).

    WHAT IT CANNOT SEE (a harness limit, not a checker oversight): the judge hands
    a predicate the arguments in their POST-call state, so there is no pre-call
    snapshot to compare against. A student who mutates the input and then copies
    the damaged values passes — the copy IS faithful to what the input now holds.
    The scale probe still catches that shape (its digest is the input, so a
    mutating student disagrees with the reference at every size), and closing it
    in the judge would need the pre-call arguments passed to checkers.

    What it does NOT do: fix a node count or a value range. The contract has no
    freedom in either (n and the values come from the input), so they are graded
    by the equality check rather than re-imposed on a correct copy.
    """
    if not isinstance(args, (list, tuple)) or not args:
        return False
    head = args[0]

    def _is_node_list(value) -> bool:
        return (
            isinstance(value, list)
            and all(
                isinstance(entry, list)
                and len(entry) == 2
                and isinstance(entry[0], int)
                and not isinstance(entry[0], bool)
                and isinstance(entry[1], int)
                and not isinstance(entry[1], bool)
                and -1 <= entry[1] < len(value)
                for entry in value
            )
        )

    if not _is_node_list(head):
        return False
    if not _is_node_list(got):
        return False
    # Structural equality: the copy holds the same values and the same random
    # pointers. `next` needs no separate check because the list order IS the
    # next chain (and random_index is index-based, so it never dangles).
    if len(got) != len(head):
        return False
    for copied, original in zip(got, head):
        if copied[0] != original[0] or copied[1] != original[1]:
            return False
    if got is head:  # returning the input is the degenerate "copy"
        return False

    def _list_objects(value, into: set) -> None:
        if isinstance(value, list):
            into.add(id(value))
            for item in value:
                _list_objects(item, into)

    original_objects = {id(head)}
    for entry in head:
        original_objects.add(id(entry))
    copied_objects: set = set()
    _list_objects(got, copied_objects)
    if original_objects & copied_objects:
        return False  # a shallow copy aliases part of the original list

    return True  # a genuine deep copy, and the input still holds its own values


@measure("copy-list-with-random-pointer")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
