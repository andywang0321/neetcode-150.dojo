"""QUARANTINED assessment for `word-search-ii` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("word-search-ii")
def _word_search_ii_oracle(board: list[list[str]], words: list[str]) -> list[str]:
    # Brute force, and deliberately not a trie: for each word, walk the board once
    # looking for it — a DFS from every cell whose letter starts the word, with a
    # visited set that is undone on the way out (the statement forbids reusing a
    # cell within a word). No sharing between words at all. The result is sorted,
    # which is the canonical form of a set answer (the corpus convention for
    # "compare": "sorted"), so the visible tests can carry the statement's own
    # example output verbatim.
    rows = len(board)
    cols = len(board[0]) if rows else 0
    found: list[str] = []

    def _word_search_ii_here(word: str) -> bool:
        last = len(word) - 1
        visited = [[False] * cols for _ in range(rows)]

        def _word_search_ii_step(r: int, c: int, k: int) -> bool:
            if board[r][c] != word[k]:
                return False
            if k == last:
                return True
            visited[r][c] = True
            hit = any(
                _word_search_ii_step(nr, nc, k + 1)
                for nr, nc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1))
                if 0 <= nr < rows and 0 <= nc < cols and not visited[nr][nc]
            )
            visited[r][c] = False
            return hit

        return any(
            _word_search_ii_step(r, c, 0) for r in range(rows) for c in range(cols)
        )

    for word in dict.fromkeys(words):  # the statement promises unique words
        if word and len(word) <= rows * cols and _word_search_ii_here(word):
            found.append(word)
    return sorted(found)


@cases("word-search-ii")
def _word_search_ii_case(n: int, rng: random.Random) -> tuple[list, list, dict]:
    # Deterministic by construction: the board, the words and the paths they are
    # spelled along all come from the seeded rng, and the expected answer is the
    # oracle's own output. The board is 1..4 cells a side (independently per axis) and a word 1..4 letters
    # — well inside the statement's 12 x 12 and 10 (a case has to stay small
    # enough for the brute-force oracle), and every word is unique.
    n = max(1, min(n, 12))
    # Rows and columns vary INDEPENDENTLY (the statement allows m != n): every
    # generated board used to be square, so a solution that assumed a square
    # shape passed the whole generated set and was caught only by the 1x2 visible
    # case (verifier finding, v0.14).
    rows = 1 + n % 4  # 1 <= board.length, board[i].length <= 12
    cols = 1 + (n // 4) % 4
    letters = "abc"  # a small alphabet, so words do overlap real board paths
    board = [[rng.choice(letters) for _ in range(cols)] for _ in range(rows)]

    def _word_search_ii_spelled(length: int) -> str:
        # A self-avoiding walk of `length` cells spelled out: a string that really
        # is on the board, which is how a present word (and a long shared prefix)
        # gets built rather than hoped for.
        r, c = rng.randrange(rows), rng.randrange(cols)
        seen = {(r, c)}
        out = [board[r][c]]
        while len(out) < length:
            options = [
                (nr, nc)
                for nr, nc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1))
                if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in seen
            ]
            if not options:
                break  # cornered early: a shorter word is still a real path
            r, c = rng.choice(options)
            seen.add((r, c))
            out.append(board[r][c])
        return "".join(out)

    words: list[str] = []
    for _ in range(1 + n % 3):
        words.append(_word_search_ii_spelled(rng.randint(1, 4)))  # usually present
    for _ in range(1 + n % 3):
        words.append(  # 1 <= length <= 10, lowercase only
            "".join(rng.choice(letters) for _ in range(rng.randint(1, 4)))
        )
    words = list(dict.fromkeys(words))  # "All the strings of words are unique"
    return (
        [board, words],
        _word_search_ii_oracle(board, words),
        {"compare": "sorted"},  # the answer is a set: only its order is free
    )


@inputs("word-search-ii")
def _word_search_ii_profiler(n: int, rng: random.Random) -> list:
    # Board + words of total size ~n, both dimensions exercised: the board takes a
    # quarter of the budget and grows with n up to the statement's own 12 x 12 cap
    # (144 cells), and the word list takes everything left over, so the input keeps
    # growing after the grid has saturated.
    #
    # The words are built to make both a trie walk and a per-word board search do
    # their full work instead of returning early: seven in eight are a REAL board
    # path one letter short plus a reserved letter ('z' never occurs on the board),
    # so the word is absent — a per-word search has to exhaust the board before it
    # can answer false — while its entire prefix is genuinely present, so neither
    # implementation dies on the first letter. The eighth is a real path (present),
    # which keeps the answer non-empty so the two outputs are actually compared.
    # Values stay inside the statement's ranges: lowercase letters, board 1..12 a
    # side, words 1..10 letters and unique.
    n = max(1, int(n))
    side = max(1, min(12, int((n // 4) ** 0.5)))  # int sqrt: registry.py imports only random
    letters = "abcd"  # four letters: the walk's branching stays real but tractable
    board = [[rng.choice(letters) for _ in range(side)] for _ in range(side)]
    cells = side * side
    longest = max(1, min(10, cells))  # a word cannot be longer than the board

    def _word_search_ii_path(length: int) -> str:
        r, c = rng.randrange(side), rng.randrange(side)
        seen = {(r, c)}
        out = [board[r][c]]
        while len(out) < length:
            options = [
                (nr, nc)
                for nr, nc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1))
                if 0 <= nr < side and 0 <= nc < side and (nr, nc) not in seen
            ]
            if not options:
                break
            r, c = rng.choice(options)
            seen.add((r, c))
            out.append(board[r][c])
        return "".join(out)

    # Fill the rest of the budget with words, skipping repeats (the statement
    # says all strings are unique, and the short words collide heavily — "z" is
    # the only one-letter absent word there is), so the total really is ~n. The
    # iteration cap keeps a tiny board (where few distinct words exist at all)
    # total rather than spinning.
    budget = max(1, n - cells)
    words: list[str] = []
    seen: set[str] = set()
    used = 0
    i = 0
    while used < budget and i < 20 * budget + 20:
        length = 1 + i % longest
        if i % 8 == 0:
            word = _word_search_ii_path(length)
        elif length == 1:
            word = "z"
        else:
            word = _word_search_ii_path(length - 1) + "z"
        i += 1
        if word in seen:
            continue
        seen.add(word)
        words.append(word)
        used += len(word)
    return [board, words]


@reference("word-search-ii")
def _word_search_ii_reference(board: list[list[str]], words: list[str]) -> list[str]:
    """Canonical trie + backtracking: build ONE trie over every word, then walk the
    board once following trie edges, so a path that no word prefixes is never
    explored and the board is not re-walked per word the way a brute-force search
    re-walks it. A word is unlinked from the trie the moment it is found (and an
    empty branch is pruned from its parent), which keeps the result free of
    duplicates and stops the walk from descending into a branch that can no longer
    match anything.

    The words come back in discovery order, not sorted: the case's own
    "compare": "sorted" tag is what makes any order legal, and the probe's
    scale_compare is set to "sorted" for the same reason."""
    root: dict = {}
    for word in words:
        node = root
        for ch in word:
            nxt = node.get(ch)
            if nxt is None:
                nxt = {}
                node[ch] = nxt
            node = nxt
        node[None] = word  # the word-end marker carries the word itself

    rows = len(board)
    cols = len(board[0]) if rows else 0
    found: list[str] = []
    visited: set[tuple[int, int]] = set()

    def _word_search_ii_walk(r: int, c: int, node: dict) -> None:
        ch = board[r][c]
        nxt = node.get(ch)
        if nxt is None:
            return  # no remaining word has this prefix
        word = nxt.pop(None, None)
        if word is not None:
            found.append(word)  # unlinked: a second occurrence cannot re-add it
        if nxt:  # something is still reachable through this node: descend
            visited.add((r, c))
            for nr, nc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)):
                if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in visited:
                    _word_search_ii_walk(nr, nc, nxt)
            visited.discard((r, c))
        else:  # nothing left below: prune the edge so the walk stops paying for it
            node.pop(ch, None)

    for r in range(rows):
        for c in range(cols):
            _word_search_ii_walk(r, c, root)
    return found


@measure("word-search-ii")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    sorted."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'sorted'}
