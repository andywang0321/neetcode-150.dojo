"""QUARANTINED assessment for `implement-trie-prefix-tree` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, oracle, reference


@oracle("implement-trie-prefix-tree")
def _implement_trie_prefix_tree_oracle(ops: list[list]) -> list:
    # Brute force: keep the inserted words in a list and answer every query by
    # scanning it — membership for search, a startswith scan for startsWith.
    # O(N * L) a query, which is exactly what the trie exists to avoid.
    words: list[str] = []
    out: list = []
    for op in ops:
        method, *args = op
        if method == "insert":
            words.append(args[0])
            out.append(None)
        elif method == "search":
            out.append(args[0] in words)
        elif method == "startsWith":
            out.append(any(word.startswith(args[0]) for word in words))
        else:  # pragma: no cover - the generator only emits the three methods
            raise ValueError(f"unknown op {method}")
    return out


@cases("implement-trie-prefix-tree")
def _implement_trie_prefix_tree_case(n: int, rng: random.Random) -> tuple[list, list, dict]:
    # Deterministic by construction: every op comes from the seeded rng, the
    # alphabet and the length range are fixed, and the op list replays on a fresh
    # instance (the judge harness builds one per case).
    steps = 2 * max(1, min(n, 12)) + 1
    alphabet = "ab"  # two letters: prefixes collide in almost every call
    ops: list[list] = []
    inserted: list[str] = []
    for step in range(steps):
        if not inserted or step % 3 == 0:
            # 1 <= word.length <= 2000, lowercase only: 1..4 letters of "ab"
            word = "".join(rng.choice(alphabet) for _ in range(rng.randint(1, 4)))
            ops.append(["insert", word])
            if word not in inserted:
                inserted.append(word)
            continue
        word = rng.choice(inserted)
        cut = rng.randint(1, len(word))  # a real prefix, sometimes the word itself
        roll = rng.randint(0, 3)
        if roll == 0:
            ops.append(["search", word])  # a hit
        elif roll == 1:
            ops.append(["search", word + rng.choice(alphabet)])  # a miss
        elif roll == 2:
            ops.append(["startsWith", word[:cut]])  # a hit (the empty prefix is
            # not reachable here: cut >= 1)
        else:
            # a real prefix asked as a whole word: true exactly when that prefix
            # was itself inserted earlier, which is what makes search and
            # startsWith differ
            ops.append(["search", word[:cut]])
    return [], _implement_trie_prefix_tree_oracle(ops), {"ops": ops}


@reference("implement-trie-prefix-tree")
def _implement_trie_prefix_tree_reference(ops: list[list]) -> list:
    """Canonical trie, driven through the same op list the oracle takes: one dict
    per node mapping a character to its child, plus a None key marking "a word
    ends here" — which is the whole difference between search and startsWith.
    Each call walks its word once (O(len(word)) time), and the structure holds one
    node per distinct prefix (O(total inserted characters) space)."""
    root: dict = {}
    out: list = []
    for op in ops:
        method, *args = op
        word = args[0]
        if method == "insert":
            node = root
            for ch in word:
                nxt = node.get(ch)
                if nxt is None:
                    nxt = {}
                    node[ch] = nxt
                node = nxt
            node[None] = True  # a word ends at this node
            out.append(None)
        elif method == "search":
            node = root
            for ch in word:
                node = node.get(ch)
                if node is None:
                    break
            out.append(node is not None and None in node)
        elif method == "startsWith":
            node = root
            for ch in word:
                node = node.get(ch)
                if node is None:
                    break
            out.append(node is not None)
        else:  # pragma: no cover - the generator only emits the three methods
            raise ValueError(f"unknown op {method}")
    return out
