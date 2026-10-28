"""QUARANTINED assessment for `search-a-2d-matrix` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


def _search_a_2d_matrix_absent_target(values: list[int], rng: random.Random) -> int:
    """A target inside the statement's own range that is not in ``values``."""
    present = set(values)
    for _ in range(64):
        candidate = rng.randint(-10_000, 10_000)
        if candidate not in present:
            return candidate
    # Unreachable with <= 12 values drawn from 20_001, kept so this is total.
    return next(v for v in range(-10_000, 10_001) if v not in present)


@oracle("search-a-2d-matrix")
def _search_a_2d_matrix_oracle(matrix: list[list[int]], target: int) -> bool:
    # Brute force: visit every cell and use none of the sortedness.
    for row in matrix:
        for value in row:
            if value == target:
                return True
    return False


@cases("search-a-2d-matrix")
def _search_a_2d_matrix_case(n: int, rng: random.Random) -> tuple[list, bool]:
    total = max(1, min(n, 12))  # the statement's floor: m >= 1 and n >= 1
    rows = rng.randint(1, min(4, total))
    cols = rng.randint(1, max(1, total // rows))
    # Strictly increasing in flattened order, so each row is non-decreasing AND
    # the first integer of each row is greater than the last of the previous one
    # (strictly increasing is the only shape that gives the statement's strict
    # ">" between rows). Values stay inside -10^4 <= matrix[i][j] <= 10^4.
    values: list[int] = []
    current = rng.randint(-10_000, 10_000 - 5 * rows * cols)
    for _ in range(rows * cols):
        values.append(current)
        current += rng.randint(1, 5)
    matrix = [values[i * cols:(i + 1) * cols] for i in range(rows)]
    if rng.random() < 0.5:
        target = rng.choice(values)  # a hit, the shape example 1 has
    else:
        target = _search_a_2d_matrix_absent_target(values, rng)  # a miss
    return [matrix, target], _search_a_2d_matrix_oracle(matrix, target)


@inputs("search-a-2d-matrix")
def _search_a_2d_matrix_profiler(n: int, rng: random.Random) -> list:
    # The matrix is one strictly increasing run of EVEN values laid out row by
    # row (so both stated properties hold exactly), and the target is an ODD
    # value in the gap just below the LAST cell: it is not in the matrix, so the
    # binary search cannot stop at a lucky midpoint but must run its loop to
    # exhaustion, on a deepest gap for this midpoint scheme (one round deeper
    # than a mid-matrix miss at every size I measured), while a linear scan must
    # read every cell (the `target > matrix[-1][-1]` short-circuit cannot fire
    # either). All values and the target are inside
    # -10^4 <= matrix[i][j], target <= 10^4, and the shape is square-ish with
    # both dimensions <= 100 (the statement's own bound), so the cell count is
    # ~n for the probe's ladder.
    n = max(2, min(n, 10_000))  # 100 x 100 is the most cells the statement allows
    side = max(1, int(n**0.5))  # no `math` import here: registry.py imports only random
    while side * side < n and side < 100:
        side += 1
    cols = min(100, side)
    rows = min(100, -(-n // cols))
    total = rows * cols
    values = [-10_000 + 2 * i for i in range(total)]
    matrix = [values[i * cols:(i + 1) * cols] for i in range(rows)]
    target = values[-2] + 1
    return [matrix, target]


@reference("search-a-2d-matrix")
def _search_a_2d_matrix_reference(matrix: list[list[int]], target: int) -> bool:
    # The two stated properties make the matrix a single sorted array read row
    # by row, so one binary search over cell indices is enough — and it never
    # materialises that array.
    if not matrix or not matrix[0]:
        return False
    cols = len(matrix[0])  # the statement guarantees every row is n long
    lo, hi = 0, len(matrix) * cols - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        value = matrix[mid // cols][mid % cols]
        if value == target:
            return True
        if value < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return False


@measure("search-a-2d-matrix")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
