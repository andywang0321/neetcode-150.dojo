"""QUARANTINED assessment for `rotting-oranges` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("rotting-oranges")
def _rotting_oranges_oracle(grid: list[list[int]]) -> int:
    """Brute force: the statement's own minute-by-minute simulation, with the
    whole grid rescanned from scratch every minute and every fresh orange tested
    against its four neighbours. No queue, no distances, no visited set -- the
    definition made executable, which is what makes it a usable anchor for the
    -1 rule as well ("nothing changed this minute, so it never will"). Total on
    an empty grid and on a grid with no fresh orange (0 minutes)."""
    rows = len(grid)
    cols = len(grid[0]) if rows else 0
    if rows == 0 or cols == 0:
        return 0
    state = [row[:] for row in grid]
    minutes = 0
    while True:
        fresh = [
            (i, j)
            for i in range(rows)
            for j in range(cols)
            if state[i][j] == 1
        ]
        if not fresh:
            return minutes  # no cell has a fresh orange
        turning = []
        for i, j in fresh:
            if (
                (i and state[i - 1][j] == 2)
                or (i + 1 < rows and state[i + 1][j] == 2)
                or (j and state[i][j - 1] == 2)
                or (j + 1 < cols and state[i][j + 1] == 2)
            ):
                turning.append((i, j))
        if not turning:
            return -1  # a fresh orange with no rotten neighbour will never rot
        for i, j in turning:
            state[i][j] = 2  # the whole minute's rot happens at once
        minutes += 1


@cases("rotting-oranges")
def _rotting_oranges_case(n: int, rng: random.Random) -> tuple[list, int]:
    """Cells are exactly 0, 1 and 2, and the grid is clamped into the statement's
    own 1 <= m, n <= 10 (the caller only sends 0..12, and 12 is already past the
    statement's ceiling).

    Five families, so the two answers that a sample of random grids would almost
    never reach are generated on purpose rather than hoped for:
      * no rotten orange anywhere (the rot starts nowhere): 0 when nothing is
        fresh either, -1 whenever some orange is fresh, because nothing can
        ever rot;
      * impossible WITH rot present: a full water column splits the grid, the
        rot is put on one side and fresh oranges on the other, so the answer is
        -1 by construction;
      * all fresh but for a few rotten ones: the rot sweeps the whole grid and
        the answer is finite;
      * i.i.d. cells, and a mostly-empty grid with a little rot.
    `expected` always comes from the oracle, never from the branch that built
    the case."""
    cap = max(1, min(n, 10))  # the statement's 1 <= m, n <= 10
    rows = rng.randint(1, cap)
    cols = rng.randint(1, cap)
    roll = rng.random()
    if roll < 0.20:
        # THE ROT STARTS NOWHERE. No cell is 2 anywhere in this family.
        if rng.random() < 0.4:
            grid = [[0] * cols for _ in range(rows)]  # nothing fresh either -> 0
        else:
            grid = [
                [rng.choice((0, 1, 1)) for _ in range(cols)] for _ in range(rows)
            ]
            i, j = rng.randrange(rows), rng.randrange(cols)
            grid[i][j] = 1  # at least one fresh orange that can never rot -> -1
    elif roll < 0.50 and cols >= 3:
        # IMPOSSIBLE WITH ROT PRESENT: column `split` is water top to bottom, the
        # rotten oranges live left of it and fresh oranges right of it. split
        # stops at cols - 2 so the right-hand side is never empty.
        grid = [[rng.choice((0, 1)) for _ in range(cols)] for _ in range(rows)]
        split = rng.randrange(1, cols - 1)
        for i in range(rows):
            grid[i][split] = 0
        for i in range(rows):  # clear the right-hand side of rot...
            for j in range(split + 1, cols):
                if grid[i][j] == 2:
                    grid[i][j] = 1
        grid[rng.randrange(rows)][rng.randrange(split)] = 2  # ...and seed the left
        grid[rng.randrange(rows)][rng.randrange(split + 1, cols)] = 1
    elif roll < 0.68:
        # EVERYTHING FRESH BUT THE SEED ROT: the rot sweeps the whole grid.
        grid = [[1] * cols for _ in range(rows)]
        for _ in range(rng.randint(1, 3)):
            grid[rng.randrange(rows)][rng.randrange(cols)] = 2
    elif roll < 0.84:
        # i.i.d. cells, rot sparse enough that fresh oranges often get cut off.
        grid = [
            [rng.choice((0, 0, 0, 1, 1, 2)) for _ in range(cols)] for _ in range(rows)
        ]
    else:
        # mostly empty with a little rot: the answer is small but finite or -1
        grid = [
            [rng.choice((0, 0, 1, 2)) for _ in range(cols)] for _ in range(rows)
        ]
    return [grid], _rotting_oranges_oracle(grid)


@inputs("rotting-oranges")
def _rotting_oranges_profiler(n: int, rng: random.Random) -> list:
    """A snake of fresh oranges with ONE rotten orange at (0, 0). Every even row
    is full and every odd row is water except a single cell: the turn at the end
    of the row above, alternating between the last column (odd rows 1, 5, 9, ...)
    and the first one (odd rows 3, 7, 11, ...). The fresh cells therefore form a
    single simple PATH whose one end is the rotten orange, so the rot has to walk
    the whole snake one cell per minute and the answer is exactly the number of
    fresh cells -- the largest value this many cells allow. Nothing can
    early-exit: a BFS must enqueue every fresh cell, the minute-by-minute oracle
    pays its full minutes x cells, and a "rescan the grid every minute" solution
    pays the whole minutes x cells product too.

    Total area is ~n inside the statement's own 1 <= m, n <= 10 (probe_max_n =
    100 cuts the ladder at the ceiling), so no rung can ask for a grid the
    statement forbids.
    """
    import math

    size = max(1, int(n))
    cols = max(1, min(10, math.isqrt(size)))
    rows = max(1, min(10, (size + cols - 1) // cols))
    grid = [[0] * cols for _ in range(rows)]
    for i in range(0, rows, 2):  # the snake's full rows
        for j in range(cols):
            grid[i][j] = 1
    for i in range(1, rows, 2):  # the turn down to the next full row
        grid[i][cols - 1 if i % 4 == 1 else 0] = 1
    grid[0][0] = 2  # the one rotten orange, at the snake's mouth
    return [grid]


@reference("rotting-oranges")
def _rotting_oranges_reference(grid: list[list[int]]) -> int:
    # Canonical multi-source BFS: every rotten orange is in the queue at minute
    # 0, and the search advances one whole level per minute, so a fresh orange is
    # reached at exactly its shortest distance to any rotten one. Each cell is
    # enqueued at most once -> O(m * n) time; the queue plus the state copy ->
    # O(m * n) space. A local copy is marked instead of the argument (the
    # statement grades a returned number, and a reference that left the grid
    # eaten would surprise whoever calls it twice), and `deque` is imported
    # inside the function because the probe hands this function alone to its own
    # subprocess.
    from collections import deque

    rows = len(grid)
    cols = len(grid[0]) if rows else 0
    if rows == 0 or cols == 0:
        return 0
    state = [row[:] for row in grid]
    queue = deque()
    fresh = 0
    for i in range(rows):
        for j in range(cols):
            if state[i][j] == 2:
                queue.append((i, j))
            elif state[i][j] == 1:
                fresh += 1
    minutes = 0
    while queue and fresh:
        minutes += 1
        for _ in range(len(queue)):  # one whole level == one minute
            i, j = queue.popleft()
            for ni, nj in ((i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1)):
                if 0 <= ni < rows and 0 <= nj < cols and state[ni][nj] == 1:
                    state[ni][nj] = 2
                    fresh -= 1
                    queue.append((ni, nj))
    return minutes if fresh == 0 else -1


@measure("rotting-oranges")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
