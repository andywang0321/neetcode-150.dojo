"""QUARANTINED assessment for `serialize-and-deserialize-binary-tree` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, checker, oracle


def _serialize_and_deserialize_binary_tree_encode(node: list | None) -> str:
    """A canonical preorder encoding with an explicit marker for a missing child:
    "N" for None and "value(left)(right)" for a node, so no value can be confused
    with a marker and no shape needs a delimiter. PRIVATE to the oracle -- the
    student's format is the student's own and the checker never looks at it."""
    if node is None:
        return "N"
    return (
        f"{node[0]}("
        f"{_serialize_and_deserialize_binary_tree_encode(node[1])}"
        f"{_serialize_and_deserialize_binary_tree_encode(node[2])})"
    )


def _serialize_and_deserialize_binary_tree_decode(
    data: str, i: int = 0
) -> tuple[list | None, int]:
    """Read back what `_..._encode` wrote; returns (tree, index just past it)."""
    if data[i] == "N":
        return None, i + 1
    start = i
    while data[i] != "(":
        i += 1
    value = int(data[start:i])
    left, i = _serialize_and_deserialize_binary_tree_decode(data, i + 1)
    right, i = _serialize_and_deserialize_binary_tree_decode(data, i)
    return [value, left, right], i + 1  # i is this node's closing paren


def _serialize_and_deserialize_binary_tree_encode(node: list | None) -> str:
    """A canonical preorder encoding with an explicit marker for a missing child:
    "N" for None and "value(left)(right)" for a node, so no value can be confused
    with a marker and no shape needs a delimiter. PRIVATE to the oracle -- the
    student's format is the student's own and the checker never looks at it."""
    if node is None:
        return "N"
    return (
        f"{node[0]}("
        f"{_serialize_and_deserialize_binary_tree_encode(node[1])}"
        f"{_serialize_and_deserialize_binary_tree_encode(node[2])})"
    )


def _serialize_and_deserialize_binary_tree_decode(
    data: str, i: int = 0
) -> tuple[list | None, int]:
    """Read back what `_..._encode` wrote; returns (tree, index just past it)."""
    if data[i] == "N":
        return None, i + 1
    start = i
    while data[i] != "(":
        i += 1
    value = int(data[start:i])
    left, i = _serialize_and_deserialize_binary_tree_decode(data, i + 1)
    right, i = _serialize_and_deserialize_binary_tree_decode(data, i)
    return [value, left, right], i + 1  # i is this node's closing paren


def _serialize_and_deserialize_binary_tree_encode(node: list | None) -> str:
    """A canonical preorder encoding with an explicit marker for a missing child:
    "N" for None and "value(left)(right)" for a node, so no value can be confused
    with a marker and no shape needs a delimiter. PRIVATE to the oracle -- the
    student's format is the student's own and the checker never looks at it."""
    if node is None:
        return "N"
    return (
        f"{node[0]}("
        f"{_serialize_and_deserialize_binary_tree_encode(node[1])}"
        f"{_serialize_and_deserialize_binary_tree_encode(node[2])})"
    )


def _serialize_and_deserialize_binary_tree_decode(
    data: str, i: int = 0
) -> tuple[list | None, int]:
    """Read back what `_..._encode` wrote; returns (tree, index just past it)."""
    if data[i] == "N":
        return None, i + 1
    start = i
    while data[i] != "(":
        i += 1
    value = int(data[start:i])
    left, i = _serialize_and_deserialize_binary_tree_decode(data, i + 1)
    right, i = _serialize_and_deserialize_binary_tree_decode(data, i)
    return [value, left, right], i + 1  # i is this node's closing paren


def _serialize_and_deserialize_binary_tree_value(rng: random.Random) -> int:
    """Inside the statement's -1000..1000. Half the draws come from a small range
    so values REPEAT: nothing in this statement promises unique values (unlike
    LC 105), and a codec that rebuilds the tree from a set of values instead of
    from the encoded structure breaks on a duplicate. Negatives appear in both
    halves, so the encoding has to carry the sign."""
    if rng.random() < 0.5:
        return rng.randint(-9, 9)
    return rng.randint(-1000, 1000)


def _serialize_and_deserialize_binary_tree_tree(
    rng: random.Random, n: int
) -> list | None:
    """A random tree with exactly n nodes: one draw in four is a degenerate chain
    (left-only or right-only), otherwise the nodes are split uniformly."""
    if n <= 0:
        return None
    if n > 2 and rng.random() < 0.25:
        if rng.random() < 0.5:
            return [
                _serialize_and_deserialize_binary_tree_value(rng),
                _serialize_and_deserialize_binary_tree_tree(rng, n - 1),
                None,
            ]
        return [
            _serialize_and_deserialize_binary_tree_value(rng),
            None,
            _serialize_and_deserialize_binary_tree_tree(rng, n - 1),
        ]
    left = rng.randrange(n)  # 0..n-1 nodes go left, the rest right
    return [
        _serialize_and_deserialize_binary_tree_value(rng),
        _serialize_and_deserialize_binary_tree_tree(rng, left),
        _serialize_and_deserialize_binary_tree_tree(rng, n - 1 - left),
    ]


@oracle("serialize-and-deserialize-binary-tree")
def _serialize_and_deserialize_binary_tree_oracle(root: list | None) -> list | None:
    """The round-trip anchor: what `deserialize(serialize(root))` has to produce
    is `root` again, so the oracle encodes with the canonical codec above and
    decodes back. An oracle is a value, and the answer to this problem is a PAIR
    OF FUNCTIONS -- the real grading is the `tree_codec_roundtrip` checker running
    the student's own two functions -- but the case dicts need an `expected`
    value, and the corpus contract test's generic predicate path calls this
    oracle and hands its answer to the checker. Both are the tree itself."""
    tree, _ = _serialize_and_deserialize_binary_tree_decode(
        _serialize_and_deserialize_binary_tree_encode(root)
    )
    return tree


@cases("serialize-and-deserialize-binary-tree")
def _serialize_and_deserialize_binary_tree_case(
    n: int, rng: random.Random
) -> tuple[list, list, dict]:
    # n = 0 is legal here (the statement allows an empty tree, and Example 2 is
    # one), so the clamp keeps it: 0..12 of the statement's 0..10^4.
    n = max(0, min(n, 12))
    tree = _serialize_and_deserialize_binary_tree_tree(rng, n)
    return [
        tree
    ], _serialize_and_deserialize_binary_tree_oracle(tree), {
        "predicate": "tree_codec_roundtrip"
    }


def _serialize_and_deserialize_binary_tree_same(a, b) -> bool:
    """Equality in dojo's tree shape: a node is a 3-element sequence whose first
    element is an int and whose other two are nodes or None. Tuples read as lists
    -- the judge's own strict comparison goes through JSON, where a tuple and a
    list are the same array, so a `deserialize` that rebuilds children as tuples
    must not be false-failed. bools are not ints here (Python says True == 1)."""
    if isinstance(a, (list, tuple)) or isinstance(b, (list, tuple)):
        if not (isinstance(a, (list, tuple)) and isinstance(b, (list, tuple))):
            return False
        return len(a) == 3 and len(b) == 3 and all(
            _serialize_and_deserialize_binary_tree_same(x, y) for x, y in zip(a, b)
        )
    if a is None or b is None:
        return a is None and b is None
    if isinstance(a, bool) or isinstance(b, bool):
        return False
    return isinstance(a, int) and isinstance(b, int) and a == b


def _serialize_and_deserialize_binary_tree_size(node: list | None) -> int:
    if node is None:
        return 0
    return (
        1
        + _serialize_and_deserialize_binary_tree_size(node[1])
        + _serialize_and_deserialize_binary_tree_size(node[2])
    )


def _serialize_and_deserialize_binary_tree_other(root: list | None) -> list:
    """A tree that cannot equal `root`: a left chain with exactly one node more
    than `root` (two equal trees have equal node counts). Values are 0, inside the
    statement's -1000..1000."""
    node: list | None = None
    for _ in range(_serialize_and_deserialize_binary_tree_size(root) + 1):
        node = [0, node, None]
    return node  # type: ignore[return-value]


@checker("tree_codec_roundtrip")
def _serialize_and_deserialize_binary_tree_roundtrip(module, got, args) -> bool:
    """`deserialize(serialize(root))` must be `root` again -- in ANY encoding, since
    the statement leaves the format entirely to the student.

    The checker never parses, inspects or guesses the format: it calls the
    student's own `serialize`/`deserialize` through the module the harness hands it
    and compares trees. `got` is the harness's own call of the student's
    `serialize` on the case's tree, so it must be a str (the statement's contract
    and the stub's annotation).

    A second tree -- a chain one node longer, so it can never equal the case's
    tree -- is serialized too, and both strings go back to `deserialize` in the
    REVERSE of the order they were produced in. A `deserialize` that ignores its
    argument and returns whatever `serialize` last stashed in a module global (or
    pops off a stack) therefore decodes the wrong tree and fails; a codec whose
    string really carries the tree is unaffected. A plain round trip cannot see
    that difference -- the harness has just called `serialize`, so the stash holds
    the right tree at that moment -- and it is the one shape of "deserialize
    ignores its input" that would otherwise pass. A constant-returning or
    None-returning `deserialize` fails on the non-empty cases outright, and the
    judge requires every case to pass."""
    root = args[0]
    serialize = getattr(module, "serialize", None)
    deserialize = getattr(module, "deserialize", None)
    if not (callable(serialize) and callable(deserialize)):
        # No codec pair to exercise. Read this branch carefully, because two very
        # different callers reach it:
        #  * a SUBMISSION that deleted or renamed one half of the pair: nothing can
        #    be round-tripped, and a serialized string is not a tree, so it fails.
        #  * the corpus contract test (tests/test_registry.py `_predicate_holds`),
        #    which exercises a predicate checker generically by handing it the
        #    *registry's* public namespace -- where no student codec can exist --
        #    together with the oracle's own answer, and asks only that the trust
        #    anchor's answer be accepted.
        # A submission is always a real module (the harness loads solution.py with
        # importlib, so it has __name__); a registry view is a SimpleNamespace and
        # has none. Without that gate a student who made `serialize` return the
        # tree object and deleted `deserialize` would "round-trip" for free.
        if not hasattr(module, "__name__"):
            return _serialize_and_deserialize_binary_tree_same(got, root)
        return False
    if not isinstance(got, str):
        return False  # the statement: the tree "can be serialized to a string"
    other = _serialize_and_deserialize_binary_tree_other(root)
    other_encoded = serialize(other)
    if not isinstance(other_encoded, str):
        return False
    return _serialize_and_deserialize_binary_tree_same(
        deserialize(got), root
    ) and _serialize_and_deserialize_binary_tree_same(
        deserialize(other_encoded), other
    )
