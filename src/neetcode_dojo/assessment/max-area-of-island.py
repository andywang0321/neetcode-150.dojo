"""QUARANTINED assessment for `max-area-of-island` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("max-area-of-island")
def _max_area_of_island_oracle(grid: list[list[int]]) -> int:
    """Brute force, and the same deliberately un-traversal mechanism as
    number-of-islands' anchor: every land cell is labelled with its own id, the
    labels are relaxed against the four neighbours until a forward+backward pass
    changes nothing, and the answer is the largest class of equal labels. No
    queue, no stack, no visited set. Total on an empty grid, and 0 when there is
    no land at all."""
    rows = len(grid)
    cols = len(grid[0]) if rows else 0
    if rows == 0 or cols == 0:
        return 0
    label = [[0] * cols for _ in range(rows)]
    for i in range(rows):
        for j in range(cols):
            if grid[i][j] == 1:
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
    areas: dict[int, int] = {}
    for i in range(rows):
        for j in range(cols):
            if label[i][j]:
                areas[label[i][j]] = areas.get(label[i][j], 0) + 1
    return max(areas.values()) if areas else 0


@cases("max-area-of-island")
def _max_area_of_island_case(n: int, rng: random.Random) -> tuple[list, int]:
    """Sizes are clamped into the statement's own range (1 <= m, n <= 50; the
    caller only sends 0..12, so the floor is what matters) and the cells are
    exactly 0 and 1. Four families: all water (no island -> 0), all land (one
    island -> m * n), a handful of land rectangles (a few islands whose areas the
    answer has to compare), and i.i.d. cells at a density drawn per case.
    `expected` always comes from the oracle."""
    n = max(1, min(n, 12))  # the statement's floor: the grid is never empty
    rows = rng.randint(1, n)
    cols = rng.randint(1, n)
    roll = rng.random()
    if roll < 0.12:  # no island at all -> 0
        grid = [[0] * cols for _ in range(rows)]
    elif roll < 0.24:  # one island, filling the grid
        grid = [[1] * cols for _ in range(rows)]
    elif roll < 0.60:  # rectangles: several islands with different areas
        grid = [[0] * cols for _ in range(rows)]
        for _ in range(rng.randint(1, 3)):
            top = rng.randrange(rows)
            left = rng.randrange(cols)
            height = rng.randint(1, rows - top)
            width = rng.randint(1, cols - left)
            for i in range(top, top + height):
                for j in range(left, left + width):
                    grid[i][j] = 1
    else:  # i.i.d. cells, with the density drawn per case
        density = rng.choice((0.2, 0.35, 0.5, 0.65, 0.8))
        grid = [
            [1 if rng.random() < density else 0 for _ in range(cols)]
            for _ in range(rows)
        ]
    return [grid], _max_area_of_island_oracle(grid)


@inputs("max-area-of-island")
def _max_area_of_island_profiler(n: int, rng: random.Random) -> list:
    """A big solid island plus a row of isolated single cells, at total area ~n
    inside the statement's own 50 x 50 ceiling (probe_max_n = 2500 cuts the
    ladder there, so no rung can ask for more).

    The big island is what makes both implementations traverse everything: the
    flood fill has to reach all of it, and its area is the answer, so it grows
    with n and the digest is informative at every rung. The isolated cells are
    there so the answer is NOT the total number of 1s -- "count every 1" is this
    problem's classic wrong answer, and on this input it disagrees with the
    reference at every measured size instead of escaping as "matches".
    """
    import math

    size = max(1, int(n))
    cols = max(1, min(50, math.isqrt(size)))
    rows = max(1, min(50, (size + cols - 1) // cols))
    if rows < 3:  # degenerate rungs: one island, still nothing to early-exit on
        return [[[1] * cols for _ in range(rows)]]
    grid = [[1] * cols for _ in range(rows - 2)]  # the big island: (rows - 2) * cols
    grid.append([0] * cols)  # a water row, so the block ends cleanly
    grid.append([1 if j % 2 == 0 else 0 for j in range(cols)])  # isolated single cells
    return [grid]


@reference("max-area-of-island")
def _max_area_of_island_reference(grid: list[list[int]]) -> int:
    # Canonical flood fill: every land cell not yet seen starts one BFS that
    # measures its whole island, and the largest measurement wins. Each cell is
    # enqueued at most once -> O(m * n) time; the visited grid plus the queue's
    # frontier -> O(m * n) space. The argument is left alone, the walk is
    # iterative, and `deque` is imported inside the function because the probe
    # hands this function alone to its own subprocess.
    from collections import deque

    rows = len(grid)
    cols = len(grid[0]) if rows else 0
    if rows == 0 or cols == 0:
        return 0
    seen = [[False] * cols for _ in range(rows)]
    best = 0
    for i in range(rows):
        for j in range(cols):
            if grid[i][j] != 1 or seen[i][j]:
                continue
            seen[i][j] = True
            area = 0
            queue = deque([(i, j)])
            while queue:
                r, c = queue.popleft()
                area += 1
                for nr, nc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)):
                    if 0 <= nr < rows and 0 <= nc < cols and not seen[nr][nc] and grid[nr][nc] == 1:
                        seen[nr][nc] = True
                        queue.append((nr, nc))
            if area > best:
                best = area
    return best


@measure("max-area-of-island")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
