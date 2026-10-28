"""QUARANTINED assessment for `number-of-islands` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("number-of-islands")
def _number_of_islands_oracle(grid: list[list[str]]) -> int:
    """Brute force, and deliberately NOT a traversal: every land cell is labelled
    with its own id and the labels are then relaxed against the four neighbours,
    forward sweep and backward sweep, until a full pass changes nothing. At that
    fixed point every cell of a 4-connected component carries the component's
    minimum id and no two components can share one, so counting distinct labels
    counts the islands -- with no queue, no stack and no visited set anywhere. It
    is total on an empty grid ([] or [[]]), which the statement's 1 <= m, n
    excludes from ever being generated."""
    rows = len(grid)
    cols = len(grid[0]) if rows else 0
    if rows == 0 or cols == 0:
        return 0
    label = [[0] * cols for _ in range(rows)]
    for i in range(rows):
        for j in range(cols):
            if grid[i][j] == "1":
                label[i][j] = i * cols + j + 1  # 0 stays "water"
    changed = True
    while changed:
        changed = False
        for i in range(rows):  # forward sweep: pull from up and left
            for j in range(cols):
                here = label[i][j]
                if not here:
                    continue
                best = here
                if i and 0 < label[i - 1][j] < best:
                    best = label[i - 1][j]
                if j and 0 < label[i][j - 1] < best:
                    best = label[i][j - 1]
                if best != here:
                    label[i][j] = best
                    changed = True
        for i in range(rows - 1, -1, -1):  # backward sweep: pull from down and right
            for j in range(cols - 1, -1, -1):
                here = label[i][j]
                if not here:
                    continue
                best = here
                if i + 1 < rows and 0 < label[i + 1][j] < best:
                    best = label[i + 1][j]
                if j + 1 < cols and 0 < label[i][j + 1] < best:
                    best = label[i][j + 1]
                if best != here:
                    label[i][j] = best
                    changed = True
    islands = {label[i][j] for i in range(rows) for j in range(cols) if label[i][j]}
    return len(islands)


@cases("number-of-islands")
def _number_of_islands_case(n: int, rng: random.Random) -> tuple[list, int]:
    """Sizes are clamped into the statement's own range (1 <= m, n <= 300; the
    caller only ever sends 0..12, so the floor is what matters) and the cells are
    exactly "0" and "1". Four families, so the answer varies in shape as well as
    in value: an all-water grid (no island at all), an all-land grid (exactly
    one), a handful of land rectangles, and i.i.d. cells at a density drawn per
    case. `expected` always comes from the oracle, never from the branch that
    built the case."""
    n = max(1, min(n, 12))  # the statement's floor: the grid is never empty
    rows = rng.randint(1, n)
    cols = rng.randint(1, n)
    roll = rng.random()
    if roll < 0.12:  # no land anywhere -> 0 islands
        grid = [["0"] * cols for _ in range(rows)]
    elif roll < 0.24:  # one island, filling the grid
        grid = [["1"] * cols for _ in range(rows)]
    elif roll < 0.60:  # rectangles of land: fewer, bigger islands
        grid = [["0"] * cols for _ in range(rows)]
        for _ in range(rng.randint(1, 3)):
            top = rng.randrange(rows)
            left = rng.randrange(cols)
            height = rng.randint(1, rows - top)
            width = rng.randint(1, cols - left)
            for i in range(top, top + height):
                for j in range(left, left + width):
                    grid[i][j] = "1"
    else:  # i.i.d. cells, with the density drawn per case
        density = rng.choice((0.2, 0.35, 0.5, 0.65, 0.8))
        grid = [
            ["1" if rng.random() < density else "0" for _ in range(cols)]
            for _ in range(rows)
        ]
    return [grid], _number_of_islands_oracle(grid)


@inputs("number-of-islands")
def _number_of_islands_profiler(n: int, rng: random.Random) -> list:
    """Mostly land, and all of it ONE island: nothing can early-exit, because the
    flood fill has to reach every land cell and the outer scan still has to look
    at the water row. Total area is ~n (cols = floor(sqrt(n)), rows rounded up),
    which keeps the grid inside the statement's 1 <= m, n <= 300 at every rung of
    the default ladder (80 x 80 at n = 6400)."""
    import math

    size = max(1, int(n))
    cols = max(1, math.isqrt(size))
    rows = max(1, (size + cols - 1) // cols)
    grid = [["1"] * cols for _ in range(rows)]
    if rows >= 2:
        grid[-1] = ["0"] * cols  # water, and it must still be scanned
    return [grid]


@reference("number-of-islands")
def _number_of_islands_reference(grid: list[list[str]]) -> int:
    # Canonical flood fill: scan the cells in order, and every land cell not yet
    # seen starts one BFS that marks its whole island. Each cell is enqueued at
    # most once, so the time is O(m * n) and the space is the visited grid plus a
    # queue that holds a whole island's frontier in the worst case -- O(m * n).
    # It leaves the argument alone (the visited grid is its own), it is iterative
    # so a 6400-cell island cannot touch the recursion limit, and it imports
    # `deque` inside itself because the probe hands this function alone to its own
    # subprocess.
    from collections import deque

    rows = len(grid)
    cols = len(grid[0]) if rows else 0
    if rows == 0 or cols == 0:
        return 0
    seen = [[False] * cols for _ in range(rows)]
    islands = 0
    for i in range(rows):
        for j in range(cols):
            if grid[i][j] != "1" or seen[i][j]:
                continue
            islands += 1
            seen[i][j] = True
            queue = deque([(i, j)])
            while queue:
                r, c = queue.popleft()
                for nr, nc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)):
                    if 0 <= nr < rows and 0 <= nc < cols and not seen[nr][nc] and grid[nr][nc] == "1":
                        seen[nr][nc] = True
                        queue.append((nr, nc))
    return islands


@measure("number-of-islands")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
