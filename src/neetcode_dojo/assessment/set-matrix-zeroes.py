"""QUARANTINED assessment for `set-matrix-zeroes` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("set-matrix-zeroes")
def _set_matrix_zeroes_oracle(matrix: list[list[int]]) -> None:
    """Brute force by the definition, with the statement's own "simple
    improvement": record which rows and which columns contain a zero FIRST, then
    zero every cell those flags cover. Reading all the zeros before writing any
    of them is what keeps the cascade honest, and writing back into the argument
    is what dojo's "mutates" verdict compares. Total on an empty matrix (the
    statement requires at least one row and one column)."""
    rows = len(matrix)
    if rows == 0:
        return
    cols = len(matrix[0])
    zero_rows = [False] * rows
    zero_cols = [False] * cols
    for i in range(rows):
        for j in range(cols):
            if matrix[i][j] == 0:
                zero_rows[i] = True
                zero_cols[j] = True
    for i in range(rows):
        for j in range(cols):
            if zero_rows[i] or zero_cols[j]:
                matrix[i][j] = 0


@cases("set-matrix-zeroes")
def _set_matrix_zeroes_case(n: int, rng: random.Random) -> tuple[list, list, dict]:
    # The statement's 1 <= m, n <= 200; the caller sends 0..12, so both floors
    # matter (a 0-row matrix is not a legal input here).
    rows = max(1, min(n, 12))
    cols = rng.randint(1, max(1, min(n, 12)))
    if rng.random() < 0.5:
        # A dense small range: zeros are common, so flagged rows and columns
        # overlap and the cascade has to be decided before anything is written.
        matrix = [[rng.randint(-3, 3) for _ in range(cols)] for _ in range(rows)]
    else:
        # Sparse: exactly one zero, sometimes on the first row or the first
        # column - the very cells the constant-space marking uses as its flags.
        matrix = [[rng.randint(1, 1000) for _ in range(cols)] for _ in range(rows)]
        matrix[rng.randrange(rows)][rng.randrange(cols)] = 0
    expected = [row[:] for row in matrix]
    _set_matrix_zeroes_oracle(expected)
    return [matrix], [expected], {"compare": "mutates"}


@inputs("set-matrix-zeroes")
def _set_matrix_zeroes_profiler(n: int, rng: random.Random) -> list:
    # ~n cells in a square-ish grid: rows = isqrt(n) counted up by hand (the
    # registry imports only `random`) and cols = n // rows, so both dimensions
    # stay far below the statement's 200 and the default ladder's largest point
    # is 80 x 80 = 6400 cells. No probe_max_n is needed for this one.
    # Values are distinct and inside the statement's 32-bit range (7919 * i +
    # 104729 * j - 10^9 stays in [-10^9, -978 * 10^6]), so the digest is a real
    # statement about WHICH cells were zeroed. The three zeros sit on the first
    # row, on the first column and in the interior: that is the worst case for
    # the constant-space marking (a solution that forgets the first row/column
    # flags, or clears them too early, leaves a visibly different grid) and it
    # makes every marking and clearing pass run to the end on both sides.
    rows = 1
    while rows < 200 and (rows + 1) * (rows + 1) <= n:
        rows += 1
    cols = max(1, n // rows)
    matrix = [
        [7919 * i + 104729 * j - 1_000_000_000 for j in range(cols)]
        for i in range(rows)
    ]
    matrix[0][cols - 1] = 0
    matrix[rows - 1][0] = 0
    matrix[rows // 2][cols // 2] = 0
    return [matrix]


@reference("set-matrix-zeroes")
def _set_matrix_zeroes_reference(matrix: list[list[int]]) -> None:
    # The follow-up's constant-space marking: the first row and the first column
    # ARE the flag arrays. Record whether they themselves contained a zero, use
    # matrix[i][0] / matrix[0][j] as the row and column flags for the interior,
    # clear the interior from those flags, and clear the first row and column
    # last if they were flagged. O(m * n) time, O(1) extra space - no second
    # structure of any size, which is the space baseline the probe compares a
    # student's flag arrays against.
    rows = len(matrix)
    if rows == 0 or not matrix[0]:
        return
    cols = len(matrix[0])
    first_row_zero = any(matrix[0][j] == 0 for j in range(cols))
    first_col_zero = any(matrix[i][0] == 0 for i in range(rows))
    for i in range(1, rows):
        for j in range(1, cols):
            if matrix[i][j] == 0:
                matrix[i][0] = 0
                matrix[0][j] = 0
    for i in range(1, rows):
        for j in range(1, cols):
            if matrix[i][0] == 0 or matrix[0][j] == 0:
                matrix[i][j] = 0
    if first_row_zero:
        for j in range(cols):
            matrix[0][j] = 0
    if first_col_zero:
        for i in range(rows):
            matrix[i][0] = 0


@measure("set-matrix-zeroes")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    mutates."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'mutates'}
