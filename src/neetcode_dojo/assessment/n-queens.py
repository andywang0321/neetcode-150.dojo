"""QUARANTINED assessment for `n-queens` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, oracle, reference


@oracle("n-queens")
def _n_queens_oracle(n: int) -> list[list[str]]:
    # Brute force over every placement: row by row, try all n columns and keep a
    # partial placement only while the new queen attacks none of the queens below
    # it. The attack test is the statement's rule written out plainly -- same
    # column, or the same diagonal because the row distance equals the column
    # distance -- against EVERY queen already placed, with no column set and no
    # diagonal set to get wrong. That is what makes it a real differential against
    # the reference's three-set bookkeeping, and it is COMPLETE: a solution has
    # exactly one queen in each row (n queens, none sharing a row), so its column
    # tuple is one of the n**n assignments this walk visits, and the attack test
    # accepts exactly the placements the statement calls solutions -- so nothing is
    # missed and nothing extra is admitted. Solutions come out in lexicographic
    # column order, which is the order the statement's own Example 1 uses.
    # Total for n <= 0 (n=0 is the "empty input" the constraints exclude): no queen
    # is ever placed, so there is no solution to report.
    if n < 1:
        return []
    out: list[list[str]] = []
    placed: list[int] = []  # placed[r] = the column of the queen in row r

    def _n_queens_assign(r: int) -> None:
        if r == n:
            out.append(
                [
                    "".join("Q" if placed[row] == col else "." for col in range(n))
                    for row in range(n)
                ]
            )
            return
        for c in range(n):
            if all(
                c != col and abs(c - col) != r - row
                for row, col in enumerate(placed)
            ):
                placed.append(c)
                _n_queens_assign(r + 1)
                placed.pop()

    _n_queens_assign(0)
    return out


@cases("n-queens")
def _n_queens_case(n: int, rng: random.Random) -> tuple[list, list, dict]:
    # The statement's whole range, 1 <= n <= 9, with no clamp of my own at either
    # end: the caller sends 0..12, and n IS the entire input, so there is nothing
    # else to vary and nothing to keep inside a range but n itself. The ceiling is
    # the statement's own, not a cost cap: the oracle prunes as it places, so its
    # search is the pruned tree rather than n**n leaves (measured, n=9 costs it
    # 54-97 ms against the reference's 11-24 ms), and a case stays cheap enough for the
    # reference gate's 20 cases and a 200-case self-check. n=2 and n=3 are in the
    # range and have no solutions at all, so the empty answer is generated too.
    n = max(1, min(n, 9))
    return [n], _n_queens_oracle(n), {"compare": "sorted"}  # only the ORDER is free


@reference("n-queens")
def _n_queens_reference(n: int) -> list[list[str]]:
    """Canonical backtracking, the three-set version every writeup of this problem
    gives: place one queen per row, keep a set of used columns and a set for each
    diagonal direction, and recurse only into a column that attacks nothing. The
    two diagonal sets are indexed by r - c and r + c, which is what makes the
    attack test O(1) instead of the oracle's scan over the queens already placed.

    O(n!) time and O(n^2) space: the search tree holds at most n! partial
    placements (each row takes a column no earlier row took, so the number of
    k-queen prefixes is n!/(n-k)! and the whole tree is O(n!)), and the board is
    an n x n list of characters that the search marks and unmarks in place, with
    O(n) more for the three sets. The board is the reference's own state, not
    output, so it is counted; the returned list of solutions is not, which is the
    corpus convention (three_sum, add_two_numbers).

    Solutions come back in lexicographic column order -- the order the statement's
    own Example 1 uses, which is why the visible tests can transcribe it verbatim
    -- and the case's "compare": "sorted" tag is what makes any other order legal
    for a student."""
    if n < 1:
        return []
    out: list[list[str]] = []
    board = [["."] * n for _ in range(n)]
    cols: set[int] = set()
    diag: set[int] = set()  # r - c: one set per "" diagonal
    anti: set[int] = set()  # r + c: one set per "/" diagonal

    def _n_queens_place(r: int) -> None:
        if r == n:
            out.append(["".join(row) for row in board])
            return
        for c in range(n):
            if c in cols or (r - c) in diag or (r + c) in anti:
                continue
            cols.add(c)
            diag.add(r - c)
            anti.add(r + c)
            board[r][c] = "Q"
            _n_queens_place(r + 1)
            board[r][c] = "."
            cols.discard(c)
            diag.discard(r - c)
            anti.discard(r + c)

    _n_queens_place(0)
    return out
