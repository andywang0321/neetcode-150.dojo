"""QUARANTINED assessment for `valid_sudoku` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, oracle, reference


_VALID_BOARD = [
    ["5", "3", "4", "6", "7", "8", "9", "1", "2"],
    ["6", "7", "2", "1", "9", "5", "3", "4", "8"],
    ["1", "9", "8", "3", "4", "2", "5", "6", "7"],
    ["8", "5", "9", "7", "6", "1", "4", "2", "3"],
    ["4", "2", "6", "8", "5", "3", "7", "9", "1"],
    ["7", "1", "3", "9", "2", "4", "8", "5", "6"],
    ["9", "6", "1", "5", "3", "7", "2", "8", "4"],
    ["2", "8", "7", "4", "1", "9", "6", "3", "5"],
    ["3", "4", "5", "2", "8", "6", "1", "7", "9"],
]


@oracle("valid_sudoku")
def _valid_sudoku_oracle(board: list[list[str]]) -> bool:
    def ok(cells: list[str]) -> bool:
        digits = [c for c in cells if c != "."]
        return len(digits) == len(set(digits))

    for row in board:
        if not ok(row):
            return False
    for j in range(9):
        if not ok([board[i][j] for i in range(9)]):
            return False
    for bi in range(3):
        for bj in range(3):
            if not ok([board[bi * 3 + di][bj * 3 + dj] for di in range(3) for dj in range(3)]):
                return False
    return True


@cases("valid_sudoku")
def _valid_sudoku_case(n: int, rng: random.Random) -> tuple[list, bool]:
    digits = rng.sample("123456789", 9)
    board = [[digits[int(c) - 1] if c != "." else "." for c in row] for row in _VALID_BOARD]
    for _ in range(rng.randint(0, 20)):  # partially filled boards stay valid
        board[rng.randrange(9)][rng.randrange(9)] = "."
    if rng.random() < 0.5:
        # Two equal digits in one row is always invalid.
        row = rng.randrange(9)
        for j in range(9):
            if board[row][j] == "1":
                board[row][j] = "."
        j1 = rng.randrange(9)
        j2 = rng.randrange(9)
        while j2 == j1:
            j2 = rng.randrange(9)
        board[row][j1] = board[row][j2] = "1"
    return [board], _valid_sudoku_oracle(board)


@reference("valid_sudoku")
def valid_sudoku(board: list[list[str]]) -> bool:
    rows = [set() for _ in range(9)]
    cols = [set() for _ in range(9)]
    boxes = [set() for _ in range(9)]
    for i in range(9):
        for j in range(9):
            c = board[i][j]
            if c == ".":
                continue
            b = (i // 3) * 3 + (j // 3)
            if c in rows[i] or c in cols[j] or c in boxes[b]:
                return False
            rows[i].add(c)
            cols[j].add(c)
            boxes[b].add(c)
    return True
