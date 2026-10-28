"""QUARANTINED assessment for `word-search` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


def _word_search_case_path(board: list[list[str]], rng: random.Random, length: int) -> str:
    """A real self-avoiding walk of up to ``length`` cells, spelled out.

    Built by stepping to an unvisited neighbour, which is what makes the word
    genuinely present on the board; a walk that runs out of neighbours comes back
    short, and a short word is still a legal word."""
    rows = len(board)
    cols = len(board[0])
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
            break
        r, c = rng.choice(options)
        seen.add((r, c))
        out.append(board[r][c])
    return "".join(out)


@oracle("word-search")
def _word_search_oracle(board: list[list[str]], word: str) -> bool:
    # Brute force, and deliberately UNPRUNED: walk every self-avoiding path of
    # exactly len(word) cells on the board and compare the spelled string only
    # once a path is complete. No first-letter filter, no early exit inside a
    # path -- so it is obviously correct and structurally different from the
    # reference, which prunes on the letter and returns at the first hit. Total
    # for an empty board; the empty word is "found" on both sides, which the
    # statement's 1 <= word.length excludes from ever being generated.
    rows = len(board)
    cols = len(board[0]) if rows else 0
    target = list(word)
    if not target:
        return True
    used = [[False] * cols for _ in range(rows)]
    spelled: list[str] = []

    def _word_search_walk(r: int, c: int, k: int) -> bool:
        used[r][c] = True
        spelled.append(board[r][c])
        if k == len(target) - 1:
            hit = spelled == target
        else:
            hit = any(
                _word_search_walk(nr, nc, k + 1)
                for nr, nc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1))
                if 0 <= nr < rows and 0 <= nc < cols and not used[nr][nc]
            )
        spelled.pop()
        used[r][c] = False
        return hit

    return any(_word_search_walk(r, c, 0) for r in range(rows) for c in range(cols))


@cases("word-search")
def _word_search_case(n: int, rng: random.Random) -> tuple[list, bool]:
    # Board 1..3 cells a side and a word of 1..6 letters. Both bounds are inside
    # the statement's own (1 <= m, n <= 6 and 1 <= word.length <= 15); the ceiling
    # is the ORACLE's, not the statement's, because the oracle enumerates every
    # self-avoiding path and a case has to stay cheap for the reference gate's 20
    # generated cases and a 200-case self-check (the word-search-ii precedent).
    # The alphabet is mixed case on purpose: the statement's letters are
    # case-sensitive, so a solution that lowercases the board fails here.
    n = max(1, min(n, 12))
    side = 1 + n % 3  # 1 <= board.length = board[i].length <= 6
    alphabet = "ABab"
    board = [[rng.choice(alphabet) for _ in range(side)] for _ in range(side)]
    cells = side * side
    length = rng.randint(1, min(6, cells + 2))  # 1 <= word.length <= 15
    mode = n % 4
    if mode == 0:
        # Random letters from the board's own alphabet: usually absent, and the
        # only mode that can produce a word longer than the board.
        word = "".join(rng.choice(alphabet) for _ in range(length))
    elif mode == 1:
        # A real path, so the answer is true whenever the walk was not cornered.
        word = _word_search_case_path(board, rng, min(length, cells))
    elif mode == 2:
        # A real path one letter short, spoiled with 'z' (never on the board, and
        # never in the alphabet): every letter of the prefix IS present, so a
        # pruned search still has to walk the board before it can answer false.
        path = _word_search_case_path(board, rng, max(1, min(length - 1, cells)))
        word = path[:-1] + "z" if path else "z"
    else:
        # The re-use trap, whenever the board allows it: on a one-letter board the
        # word 'a' * (cells + 1) would need some cell twice, which the statement
        # forbids -- the rule the statement's own "ABCB" example demonstrates.
        flat = {ch for row in board for ch in row}
        if len(flat) == 1 and cells + 1 <= 15:
            word = next(iter(flat)) * (cells + 1)
        else:
            word = "".join(rng.choice(alphabet) for _ in range(length))
    return [board, word], _word_search_oracle(board, word)


@inputs("word-search")
def _word_search_profiler(n: int, rng: random.Random) -> list:
    # The worst case is a board whose every cell carries the same letter plus a
    # word that ends in a letter the board does not contain: every prefix of the
    # word matches, so no pruning step can fire and every branch dies only at the
    # LAST letter, and the answer is false, so neither implementation can stop at
    # a hit.
    #
    # TOTAL SIZE ~n, and the word length takes a third of it while the board takes
    # the rest, so both dimensions grow: the board area is what makes the "try
    # every cell as a start" factor real, the word length is what makes the
    # backtracking deep. n is clamped to the statement's own ceiling -- 6 x 6 = 36
    # cells plus a 15-letter word -- because a larger n has no legal input to
    # describe. probe_max_n (40 in the overrides) is what keeps the ladder's top
    # inside the probe's timeout: measured, this input's reference call costs
    # ~0.23 s at n=40 and ~2.9 s at the statement's ceiling, so the ascent stops
    # where a slower-but-correct student is nowhere near the 20 s per-run bound.
    n = max(2, min(int(n), 51))
    length = max(2, min(15, n // 3))  # 2 <= word.length <= 15
    budget = max(1, n - length)  # the cells left for the board
    side = 1
    while side < 6 and (side + 1) ** 2 <= budget:
        side += 1
    board = [["a"] * side for _ in range(side)]
    word = "a" * (length - 1) + "b"
    return [board, word]


@reference("word-search")
def _word_search_reference(board: list[list[str]], word: str) -> bool:
    """Canonical DFS + backtracking: try every cell as the start of the word,
    descend to a neighbour only while the letter keeps matching, mark the cell
    used on the way down and release it on the way back up (the statement forbids
    using a cell twice), and return at the first complete path. The letter test is
    the pruning step, so a mismatch anywhere abandons that whole branch, which is
    what makes this O(m * n * 3^L) rather than the oracle's unpruned 4^L walk.

    O(m * n * 3^L) time and O(L) space: from each of the m * n start cells at most
    three new directions per step (the cell you came from is excluded) to a depth
    of L, and the auxiliary state is the L-deep recursion plus the used-cell mark.
    The visited cells are a set of (row, column) pairs rather than an m x n matrix,
    so the reference's own footprint is O(L) and a student's O(m * n) mark is
    visible in the space ratio rather than hidden by the baseline. The board is
    never mutated -- the mark is separate -- so an in-place implementation cannot
    be blamed on the reference, and the return value is the same bool either way."""
    rows = len(board)
    cols = len(board[0]) if rows else 0
    if not word:
        return True
    last = len(word) - 1
    used: set[tuple[int, int]] = set()

    def _word_search_step(r: int, c: int, k: int) -> bool:
        if board[r][c] != word[k]:
            return False
        if k == last:
            return True
        used.add((r, c))
        for nr, nc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)):
            if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in used:
                if _word_search_step(nr, nc, k + 1):
                    used.discard((r, c))
                    return True
        used.discard((r, c))
        return False

    return any(_word_search_step(r, c, 0) for r in range(rows) for c in range(cols))


@measure("word-search")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
