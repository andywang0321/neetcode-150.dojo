"""QUARANTINED assessment for `design-add-and-search-words-data-structure` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, oracle, reference


@oracle("design-add-and-search-words-data-structure")
def _design_add_and_search_words_data_structure_oracle(ops: list[list]) -> list:
    # Brute force: keep every added word and, for a query, compare it against them
    # one at a time — a plain membership test when the pattern has no dot, a
    # per-character match when it has one. O(N * L) a query, no trie, no prefix
    # pruning: the differential against the reference is real.
    words: list[str] = []
    out: list = []
    for op in ops:
        method, *args = op
        if method == "addWord":
            words.append(args[0])
            out.append(None)
        elif method == "search":
            pattern = args[0]
            hit = False
            for word in words:
                if len(word) != len(pattern):
                    continue
                if all(p == "." or p == ch for p, ch in zip(pattern, word)):
                    hit = True
                    break
            out.append(hit)
        else:  # pragma: no cover - the generator only emits addWord and search
            raise ValueError(f"unknown op {method}")
    return out


@cases("design-add-and-search-words-data-structure")
def _design_add_and_search_words_data_structure_case(
    n: int, rng: random.Random
) -> tuple[list, list, dict]:
    # Deterministic by construction: every op comes from the seeded rng, the
    # alphabet and length range are fixed, and the op list replays on a fresh
    # instance (the judge harness builds one per case).
    steps = 2 * max(1, min(n, 12)) + 1
    alphabet = "ab"  # two letters: words overlap and prefix each other constantly
    ops: list[list] = []
    added: list[str] = []
    patterns = 0  # cycles the dot through first, last and middle position
    for step in range(steps):
        if not added or step % 3 == 0:
            # 1 <= word.length <= 25, lowercase only: 1..4 letters of "ab"
            word = "".join(rng.choice(alphabet) for _ in range(rng.randint(1, 4)))
            ops.append(["addWord", word])
            if word not in added:
                added.append(word)
            continue
        base = rng.choice(added)  # 1..4 letters, already in the dictionary
        if rng.random() < 0.15:
            # Occasionally a dotted query whose LENGTH no added word has: the
            # statement allows it, and without it a solution that only ever
            # matched against existing word lengths looked complete (verifier
            # finding, v0.14).
            length = 1 + (len(base) % 4) + 1  # one longer than a 1..4-letter base
            base = "".join(rng.choice(alphabet) for _ in range(min(length, 4)))
            if base in added:
                base = base + "a" if len(base) < 4 else base
        roll = rng.randint(0, 3)
        if roll == 0:
            ops.append(["search", base])  # a hit
        elif roll == 1:
            # ONE dot, placed at the first, the last and the middle position in
            # turn: the statement's only worked example puts it in the middle
            # (".ad"), so a generator that never tried the ends would leave "a dot
            # matches any single letter" half-pinned.
            pos = (0, len(base) - 1, len(base) // 2)[patterns % 3]
            patterns += 1
            ops.append(["search", base[:pos] + "." + base[pos + 1:]])
        elif roll == 2 and len(base) >= 2:
            # TWO dots — the statement's own maximum per query. The two ends when
            # the word has a middle to spare, a random distinct pair otherwise.
            if len(base) >= 3 and patterns % 2:
                i, j = 0, len(base) - 1
            else:
                i, j = sorted(rng.sample(range(len(base)), 2))
            patterns += 1
            chars = list(base)
            chars[i] = chars[j] = "."
            ops.append(["search", "".join(chars)])
        else:
            # a length the dictionary cannot hold: one letter longer, or one
            # shorter (never empty — the statement's floor is length 1)
            if len(base) >= 2 and rng.random() < 0.5:
                ops.append(["search", base[:-1]])
            else:
                ops.append(["search", base + rng.choice(alphabet)])
    return [], _design_add_and_search_words_data_structure_oracle(ops), {"ops": ops}


@reference("design-add-and-search-words-data-structure")
def _design_add_and_search_words_data_structure_reference(ops: list[list]) -> list:
    """Canonical WordDictionary, driven through the same op list the oracle takes:
    one dict per node (a None key marks the end of an added word), and a search
    that descends the trie letter by letter, branching into every child when it
    meets a '.' — at most two per query by the statement's own constraint, so the
    walk stays linear in the word length up to a 26^2 constant."""

    def _design_add_and_search_words_data_structure_matches(
        node: dict, word: str, i: int
    ) -> bool:
        if i == len(word):
            return None in node
        ch = word[i]
        if ch == ".":
            return any(
                _design_add_and_search_words_data_structure_matches(child, word, i + 1)
                for key, child in node.items()
                if key is not None
            )
        child = node.get(ch)
        return child is not None and _design_add_and_search_words_data_structure_matches(
            child, word, i + 1
        )

    root: dict = {}
    out: list = []
    for op in ops:
        method, *args = op
        if method == "addWord":
            node = root
            for ch in args[0]:
                nxt = node.get(ch)
                if nxt is None:
                    nxt = {}
                    node[ch] = nxt
                node = nxt
            node[None] = True
            out.append(None)
        elif method == "search":
            out.append(
                _design_add_and_search_words_data_structure_matches(root, args[0], 0)
            )
        else:  # pragma: no cover - the generator only emits addWord and search
            raise ValueError(f"unknown op {method}")
    return out
