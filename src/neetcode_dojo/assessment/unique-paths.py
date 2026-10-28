"""QUARANTINED assessment for `unique-paths` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("unique-paths")
def _unique_paths_oracle(m: int, n: int) -> int:
    """Brute force by the definition: count the walks cell by cell.

    ways(i, j) is the number of walks from the top-left corner into cell (i, j).
    A walk into that cell arrived either from above or from the left, so its
    count is the sum of those two, and every cell of the first row or the first
    column has exactly one. Written as a memoized recursion rather than a table,
    so the differential against the reference (an array rolled in place,
    bottom-up) is a real one: opposite direction, a dict of states instead of an
    array, and no shared loop. The memo is what keeps it runnable: the unmemoized
    tree has as many leaves as there are paths -- 1,609,344,100 at the largest
    lattice the statement's own answer bound allows -- while only m * n states
    exist. Total on a degenerate grid (m or n below 1 -> 0, a single cell -> 1),
    which the statement's 1 <= m, n excludes and the generator never emits.
    """
    if m < 1 or n < 1:
        return 0
    memo: dict[tuple[int, int], int] = {}

    def ways(i: int, j: int) -> int:
        if i == 0 or j == 0:
            return 1
        seen = memo.get((i, j))
        if seen is None:
            seen = ways(i - 1, j) + ways(i, j - 1)
            memo[(i, j)] = seen
        return seen

    return ways(m - 1, n - 1)


@cases("unique-paths")
def _unique_paths_case(n: int, rng: random.Random) -> tuple[list, int]:
    # The caller sends 0..12 and the statement's own bound is 1 <= m, n <= 100,
    # so the floor is 1 (a zero-row grid is not an input this problem has) and
    # the ceiling is the caller's 12. One dimension is 1 on purpose a quarter of
    # the time: a single row, a single column and a 1 x 1 grid are the three
    # shapes with no interior cell at all, which is where a recurrence reading a
    # missing neighbour shows up, and the answer is 1 for every one of them.
    # Everything generated here is far inside the statement's <= 2 * 10^9
    # guarantee: the largest lattice a case can carry is 12 x 12 = C(22, 11) =
    # 705,432 paths. expected always comes from the oracle.
    size = max(1, min(n, 12))
    mode = n % 4
    if mode == 0:
        rows, cols = 1, rng.randint(1, size)
    elif mode == 1:
        rows, cols = rng.randint(1, size), 1
    elif mode == 2:
        rows = cols = rng.randint(1, size)
    else:
        rows, cols = rng.randint(1, size), rng.randint(1, size)
    return [rows, cols], _unique_paths_oracle(rows, cols)


@inputs("unique-paths")
def _unique_paths_profiler(n: int, rng: random.Random) -> list:
    # ~n cells of lattice, so the work grows with the ladder: 7 columns wide and
    # n // 7 rows tall. The input itself is two integers, so "size" here is the
    # DP's work, not the JSON -- the same reading counting-bits uses when the
    # input IS the size.
    #
    # THE CAP IS THE STATEMENT'S ANSWER BOUND, NOT ITS m, n BOUND. The robot
    # problem promises the answer is at most 2 * 10^9, and that guarantee -- not
    # 1 <= m, n <= 100 -- is what limits a lattice. Checked by brute force over
    # every 1 <= m, n <= 100: the largest legal lattice is 7 x 100 = 700 cells,
    # C(105, 6) = 1,609,344,100 paths, and 8 x 100 = 800 cells is already
    # outside the guarantee at C(106, 7) = 13,975,313,400. The probe's default
    # ladder tops at 6400 cells, which in a lattice is 80 x 80: inside the m, n
    # bound and 47 digits of answer (C(158, 79) ~ 1.0e46), i.e. 36 orders of
    # magnitude past anything the problem promises. That is the v0.12
    # products_of_array_except_self lesson in a different costume -- outside its
    # own guarantee the partial counts are multi-digit big integers, so a
    # correct O(m * n) solution pays a per-cell cost that drifts upward and
    # measures as superlinear. probe_max_n = 700 is therefore the ceiling, and
    # 700 cells is exactly the ladder's top rung.
    #
    # WHY SEVEN COLUMNS. 7 is the largest height for which the statement's own
    # column bound can still be reached: h * 100 <= 700 gives h = 7, so the top
    # rung is the largest legal lattice AND it ends on the statement's m, n <=
    # 100 corner (7 x 100). Holding the columns at 7 and growing the rows also
    # fixes the reference's workspace: the reference rolls one row over the
    # shorter side, so its tracemalloc peak is a constant 184-348 bytes across
    # the whole ladder, while a full m x n table's peak grows with it. Measured
    # at the top rung (100 x 7, answer 1,609,344,100): reference 348 B; a student
    # rolling the shorter side 348 B (ratio 1.00x flat, "matches"); a student
    # rolling the LONGER side 3,976 B (ratio 0.78x -> 11.43x across the ladder,
    # growth 10.01x); a student keeping the whole table 23,656 B (ratio 1.48x ->
    # 68.30x, growth 27.57x). Both of the latter are flagged as growing faster
    # than a reference whose workspace is the row -- which is the O(min(m, n))
    # versus O(max(m, n)) / O(m * n) difference the statement's target names.
    #
    # NOTHING CAN EARLY-EXIT. Every cell of every lattice is the sum of two of
    # its neighbours, so the reference's row and a memoized student's state space
    # both cover all m * n cells whatever the grid looks like; there is no value
    # or shape that lets either side stop. The shape's remaining job is the
    # digest, and the smallest rung is 2 x 7 rather than 1 x 7 on purpose: a
    # one-wide lattice has exactly one path at every size, so a stub returning 1
    # would agree with the reference there.
    return [max(2, min(100, n // 7)), 7]


@reference("unique-paths")
def _unique_paths_reference(m: int, n: int) -> int:
    """The canonical DP in its one-row form, rolled over the SHORTER side.

    row[j] holds the number of walks into the current row's cell j. The count
    from the cell above is already in row[j] and the count from the left is the
    row[j - 1] this row has just written, so each cell costs one addition and the
    workspace is a single row of the shorter dimension -- O(m * n) time and
    O(min(m, n)) space, the class the statement's complexity line names. The
    transposed branch is not decoration: without it the workspace would be n
    whatever the shape, and on a tall grid that is the LONGER side. Total on a
    degenerate grid (fewer than one row or column -> 0, a single cell -> 1),
    matching the oracle.
    """
    if m < 1 or n < 1:
        return 0
    if n <= m:
        row = [1] * n
        for _ in range(m - 1):
            for j in range(1, n):
                row[j] += row[j - 1]
        return row[n - 1]
    column = [1] * m
    for _ in range(n - 1):
        for i in range(1, m):
            column[i] += column[i - 1]
    return column[m - 1]


@measure("unique-paths")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
