"""QUARANTINED assessment for `spiral-matrix` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("spiral-matrix")
def _spiral_matrix_oracle(matrix: list[list[int]]) -> list[int]:
    """Brute force by the definition: peel the outermost ring off a working copy
    of the grid - the top row left to right, the right column top to bottom, the
    bottom row right to left, the left column bottom to top - and repeat on what
    is left. That is the statement's walk written down directly, with no
    boundary bookkeeping. Total on an empty grid (the statement requires at
    least one row and one column)."""
    grid = [row[:] for row in matrix]
    out: list[int] = []
    while grid and grid[0]:
        out.extend(grid.pop(0))  # top row, left -> right
        if grid and grid[0]:
            for row in grid:  # right column, top -> bottom
                out.append(row.pop())
        if grid and grid[0]:
            out.extend(reversed(grid.pop()))  # bottom row, right -> left
        if grid and grid[0]:
            for row in reversed(grid):  # left column, bottom -> top
                out.append(row.pop(0))
    return out


@cases("spiral-matrix")
def _spiral_matrix_case(n: int, rng: random.Random) -> tuple[list, list]:
    # The statement's own constraint is 1 <= m, n <= 10, and the caller sends
    # 0..12 - so the floor is 1 and the ceiling is 10, not 12. Four of the five
    # shapes are the degenerate ones the examples never show: a single row, a
    # single column and a 1 x 1 grid are where a boundary walk that forgets to
    # re-check its bounds walks a row twice.
    base = max(1, min(n, 10))
    shape = rng.randrange(5)
    if shape == 0:
        rows = cols = base  # square
    elif shape == 1:
        rows, cols = base, rng.randint(1, 10)  # wider than tall
    elif shape == 2:
        rows, cols = rng.randint(1, 10), base  # taller than wide
    elif shape == 3:
        rows, cols = 1, base  # a single row
    else:
        rows, cols = base, 1  # a single column
    grid = [[rng.randint(-100, 100) for _ in range(cols)] for _ in range(rows)]
    return [grid], _spiral_matrix_oracle(grid)


@inputs("spiral-matrix")
def _spiral_matrix_profiler(n: int, rng: random.Random) -> list:
    # ~n cells in a square-ish grid: rows = isqrt(n) counted up by hand (the
    # registry imports only `random`) and cols = n // rows. The statement caps
    # BOTH dimensions at 10, which is why probe_max_n is 100: the ladder stops at
    # 10 x 10 = 100 cells, the largest legal input, and the default ladder's
    # 6400-cell point would be a 80 x 80 grid this statement forbids. Every cell
    # holds a distinct value inside -100..100 (at most 100 cells and 2 * index
    # stays below 201), so the returned order IS the whole answer: a walk that
    # repeats, drops or reorders a cell cannot match the reference's digest.
    # Both implementations are length-driven, so neither can early-exit.
    rows = 1
    while rows < 10 and (rows + 1) * (rows + 1) <= n:
        rows += 1
    cols = max(1, n // rows)
    return [
        [[(2 * (i * cols + j)) % 201 - 100 for j in range(cols)] for i in range(rows)]
    ]


@reference("spiral-matrix")
def _spiral_matrix_reference(matrix: list[list[int]]) -> list[int]:
    # The canonical four-boundary walk: top, right, bottom, left, shrinking each
    # boundary as it is consumed. The two `if` guards are the whole trick - they
    # stop a single remaining row or column from being walked twice, which is
    # this problem's classic failure. O(m * n) time; the result list is the only
    # thing it builds, and it does not touch the argument.
    if not matrix or not matrix[0]:
        return []
    out: list[int] = []
    top, bottom = 0, len(matrix) - 1
    left, right = 0, len(matrix[0]) - 1
    while top <= bottom and left <= right:
        for j in range(left, right + 1):
            out.append(matrix[top][j])
        top += 1
        for i in range(top, bottom + 1):
            out.append(matrix[i][right])
        right -= 1
        if top <= bottom:
            for j in range(right, left - 1, -1):
                out.append(matrix[bottom][j])
            bottom -= 1
        if left <= right:
            for i in range(bottom, top - 1, -1):
                out.append(matrix[i][left])
            left += 1
    return out


@measure("spiral-matrix")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
