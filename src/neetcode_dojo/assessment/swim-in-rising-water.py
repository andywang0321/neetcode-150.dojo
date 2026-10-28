"""QUARANTINED assessment for `swim-in-rising-water` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("swim-in-rising-water")
def _swim_in_rising_water_oracle(grid: list[list[int]]) -> int:
    """Brute force: the definition of the answer, one reachability check per
    candidate level.

    The answer is always the elevation of some cell on the winning route, so it
    is one of the grid's own values: try them in increasing order and return the
    first level at which the top-left cell can reach the bottom-right one,
    flooding through every cell whose elevation is <= that level. O(V * E) at
    worst (one flood per candidate level), which is the point -- it is obviously
    correct, it shares no step with Dijkstra, and it never reasons about
    "settling" a cell. Total on an empty grid (which the statement's 1 <= n
    excludes); the statement's square promise is what keeps the flood in range,
    so a ragged grid -- also excluded -- is handled only as far as row 0's
    width."""
    if not grid or not grid[0]:
        return 0
    rows, cols = len(grid), len(grid[0])
    goal = (rows - 1, cols - 1)
    for level in sorted({value for row in grid for value in row}):
        if grid[0][0] > level:
            continue
        seen = {(0, 0)}
        stack = [(0, 0)]
        while stack:
            r, c = stack.pop()
            if (r, c) == goal:
                return level
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nr, nc = r + dr, c + dc
                if (
                    0 <= nr < rows
                    and 0 <= nc < cols
                    and (nr, nc) not in seen
                    and grid[nr][nc] <= level
                ):
                    seen.add((nr, nc))
                    stack.append((nr, nc))
    # Unreachable for the rectangular grid the statement promises (at the
    # maximum level everything is submerged and connected); the highest
    # elevation is the honest stand-in for input the constraints exclude.
    return max(max(row) for row in grid)


@cases("swim-in-rising-water")
def _swim_in_rising_water_case(n: int, rng: random.Random) -> tuple[list, int]:
    """~n cells, square, values a permutation of 0 .. side*side - 1.

    side = clamp(n, 1, 12): the statement allows 1 <= n <= 50, but the ceiling
    here is the ORACLE's cost (one flood per candidate level, so 12 x 12 = 144
    cells is already ~20k steps), exactly as word-search's generator says of
    itself. The permutation is a constraint, not a style: the statement says
    each value is unique and 0 <= grid[i][j] < n^2, which for an n x n grid
    means the values are exactly 0 .. n^2 - 1. Four shapes, chosen by one roll
    so a 12-case batch reaches all of them, and `expected` always comes from the
    oracle:
      * a uniform random permutation (the generic case);
      * row-major ascending -- the goal holds the global maximum, so no route
        can avoid it and the answer is the largest value;
      * descending -- the START holds the global maximum, so the answer is the
        start's own elevation and no cell ever needs settling;
      * the goal holds 0 -- the minimum, so the answer is strictly between the
        two obvious bounds and every route has to climb to reach the goal.
    """
    side = max(1, min(n, 12))
    cells = side * side
    roll = rng.random()
    if roll < 0.45:
        flat = list(range(cells))
        rng.shuffle(flat)
    elif roll < 0.65:
        flat = list(range(cells))
    elif roll < 0.80:
        flat = list(range(cells))[::-1]
    else:
        rest = list(range(1, cells))
        rng.shuffle(rest)
        flat = rest + [0]
    grid = [flat[row * side : (row + 1) * side] for row in range(side)]
    return [grid], _swim_in_rising_water_oracle(grid)


@inputs("swim-in-rising-water")
def _swim_in_rising_water_profiler(n: int, rng: random.Random) -> list:
    """Row-major ascending elevations for a side = isqrt(n) grid, clamped to the
    statement's own 1 <= n <= 50.

    Values are exactly the permutation the statement promises (unique, and
    0 <= grid[i][j] < side^2), and the input's total size is ~n CELLS, which is
    the quantity the ladder scales -- this is why probe_max_n is 2500 and not 50:
    n = 2500 is the statement's own ceiling (a 50 x 50 grid) counted in cells.
    The shape is the worst case for BOTH implementations and the argument is
    checkable rather than asserted: the bottom-right cell carries the grid's
    maximum, so every route to it ends at that value and the answer is the
    maximum; Dijkstra therefore has to settle every one of the n cells before it
    can pop the goal (nothing early-exits), the heap stays ~n deep, and the
    brute-force oracle's last and fullest flood is the whole grid. rng is
    unused: a paired measurement wants the same deterministic grid at every
    rung."""
    import math  # the registry imports only random; the probe subprocess is separate

    side = max(1, min(math.isqrt(n), 50))
    return [[[row * side + col for col in range(side)] for row in range(side)]]


@reference("swim-in-rising-water")
def _swim_in_rising_water_reference(grid: list[list[int]]) -> int:
    """Canonical Dijkstra on (time, cell): O(n log n) time and O(n) space, where
    n is the number of cells.

    The cost of a route is the MAXIMUM elevation along it (that is what "you can
    swim infinite distances in zero time" means), so the state to settle is the
    smallest such maximum, and a min-heap over (level, row, col) pops cells in
    increasing level exactly once each. The neighbor's key is max(level,
    grid[nr][nc]) -- never a sum: adding elevations answers a different problem.
    The statement's square promise is what keeps the neighbor indices in range;
    an empty grid (which 1 <= n excludes) returns 0, and a 1 x 1 grid -- where
    the start IS the goal -- returns that cell's elevation."""
    import heapq  # the probe runs this snippet alone; imports must be inside it

    if not grid or not grid[0]:
        return 0
    rows, cols = len(grid), len(grid[0])
    goal = (rows - 1, cols - 1)
    settled: dict[tuple[int, int], int] = {}
    heap = [(grid[0][0], 0, 0)]
    while heap:
        level, r, c = heapq.heappop(heap)
        if (r, c) in settled:
            continue
        settled[(r, c)] = level
        if (r, c) == goal:
            return level
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in settled:
                heapq.heappush(heap, (max(level, grid[nr][nc]), nr, nc))
    return grid[0][0]  # unreachable only for a ragged grid


@measure("swim-in-rising-water")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
