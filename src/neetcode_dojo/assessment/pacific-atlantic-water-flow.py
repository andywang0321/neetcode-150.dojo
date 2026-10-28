"""QUARANTINED assessment for `pacific-atlantic-water-flow` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("pacific-atlantic-water-flow")
def _pacific_atlantic_water_flow_oracle(heights: list[list[int]]) -> list[list[int]]:
    """Brute force by the definition: for every cell, walk every path that never
    goes uphill -- a step to a neighbour is legal only when the neighbour's
    height is <= the current cell's, which is the statement's own rule -- and ask
    whether any such path reaches an edge of the Pacific (top row or left column)
    and an edge of the Atlantic (bottom row or right column). One DFS per cell
    with its own visited set, no ocean-wide search and no shared state, so the
    two oceans are decided independently and nothing about the answer (its size,
    its order) is assumed. The output is row-major, which is exactly the order
    the statement's Example 1 prints. Total on an empty grid (the constraints
    exclude it); assumes rectangular rows, which m x n promises."""
    rows = len(heights)
    if rows == 0 or not heights[0]:
        return []
    cols = len(heights[0])

    def pacific_edge(r: int, c: int) -> bool:
        return r == 0 or c == 0

    def atlantic_edge(r: int, c: int) -> bool:
        return r == rows - 1 or c == cols - 1

    def reaches(start_r: int, start_c: int, on_edge) -> bool:
        seen = {(start_r, start_c)}
        stack = [(start_r, start_c)]
        while stack:
            r, c = stack.pop()
            if on_edge(r, c):
                return True
            for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                nr, nc = r + dr, c + dc
                if (
                    0 <= nr < rows
                    and 0 <= nc < cols
                    and (nr, nc) not in seen
                    and heights[nr][nc] <= heights[r][c]
                ):
                    seen.add((nr, nc))
                    stack.append((nr, nc))
        return False

    return [
        [r, c]
        for r in range(rows)
        for c in range(cols)
        if reaches(r, c, pacific_edge) and reaches(r, c, atlantic_edge)
    ]


@cases("pacific-atlantic-water-flow")
def _pacific_atlantic_water_flow_case(n: int, rng: random.Random) -> tuple[list, list, dict]:
    # ~n cells in a shape the statement allows (1 <= m, n <= 200, every row the
    # same length); the caller sends 0..12, so the floor is a single cell. The
    # shape draw has three branches, because a board where the answer is a
    # STRICT subset of the grid needs both dimensions past the edge: an earlier
    # draft drew rows uniformly over 1..n, which made tall thin boards the norm
    # (every cell of a 1 x k board is adjacent to both oceans, so the answer was
    # trivially "all cells"), and a solution that ignored the heights entirely
    # passed 38 of 44 cases (after the fix it fails 16 of 44). So: an interior
    # it, otherwise a board with both dimensions >= 2, otherwise the full range
    # of shapes -- which is what keeps the degenerate 1 x k, k x 1 and 1 x 1
    # boards in the set.
    #
    # Three value modes, because the rule that decides this problem is the "less
    # than OR EQUAL" half of it: a three-value range makes ties everywhere, an
    # all-equal board makes every cell reach both oceans (the mode that pins the
    # equality), and the statement's full 0..10^5 range -- the most common one --
    # makes the answer a strict subset. expected comes from the oracle; the
    # "sorted" tag says the answer is the SET of coordinates, so their order is
    # free.
    cells = max(1, min(n, 12))
    if cells >= 9 and rng.random() < 0.6:
        rows = rng.randint(3, min(4, cells // 3))
        cols = rng.randint(3, max(3, cells // rows))
    elif cells >= 4 and rng.random() < 0.5:
        rows = rng.randint(2, min(4, cells // 2))
        cols = rng.randint(2, max(2, cells // rows))
    else:
        rows = rng.randint(1, cells)
        cols = rng.randint(1, max(1, cells // rows))
    roll = rng.random()
    if roll < 0.25:
        heights = [[rng.randint(0, 2) for _ in range(cols)] for _ in range(rows)]
    elif roll < 0.4:
        level = rng.randint(0, 10)
        heights = [[level] * cols for _ in range(rows)]
    else:
        heights = [[rng.randint(0, 10**5) for _ in range(cols)] for _ in range(rows)]
    return [heights], _pacific_atlantic_water_flow_oracle(heights), {"compare": "sorted"}


@inputs("pacific-atlantic-water-flow")
def _pacific_atlantic_water_flow_profiler(n: int, rng: random.Random) -> list:
    """A terraced bowl of ~n cells: every cell's height is its distance to the
    nearest edge, height = min(r, rows - 1 - r, c, cols - 1 - c).

    That shape is the worst case for both implementations, and the claim is
    checkable rather than asserted: the border ring is height 0, so it is a ring
    of equal heights -- the Pacific searches start on its top row and left
    column, the Atlantic searches on its bottom row and right column, and each
    walks the whole ring -- and the interior climbs exactly one terrace per step
    inward, so both reverse searches reach EVERY cell: 2 * m * n enqueues at
    every size, with no early exit available to either. The answer is therefore
    all m * n cells, the largest output this problem can produce, and the digest
    work is maximal too. The centre also gives the brute-force oracle its own
    worst single cell: every other cell lies on a descending path from it, so
    that one DFS explores the whole grid (measured: 1.50 s at 6400 cells), which
    is the input probe_smoke runs at n <= 800 and the one _oracle_confirms would
    run if a student's output ever disagreed.

    A monotone ramp does NOT have this property, and an earlier draft of this
    input was one: height = min(r, rows - 1 - r) + min(c, cols - 1 - c) (a
    pyramid rising toward a centre ridge) left the far corners reachable from
    only ONE ocean, so at 10 x 10 the answer came back as 68 of 100 cells and
    neither search did full work. Keeping the two axes' minima instead of their
    sum is what makes the bowl closed on all four sides.

    No probe_max_n: the default ladder's largest point is 6400 cells = 80 x 80,
    comfortably inside the statement's 1 <= m, n <= 200. Values respect
    0 <= heights[r][c] <= 10^5 with room to spare (the deepest terrace is 39 at
    80 x 80), which is the v0.12 value-fidelity rule: the shape is not enough,
    the values have to be legal. The wide plateaus also put the statement's "less
    than or equal" half of the flow rule to work on both sides of every search.
    rng is unused -- a paired measurement wants the same deterministic island at
    every rung."""
    cells = max(1, n)
    rows = 1
    while rows < 200 and (rows + 1) * (rows + 1) <= cells:
        rows += 1
    cols = max(1, cells // rows)
    heights = [
        [min(r, rows - 1 - r, c, cols - 1 - c) for c in range(cols)]
        for r in range(rows)
    ]
    return [heights]


@reference("pacific-atlantic-water-flow")
def _pacific_atlantic_water_flow_reference(heights: list[list[int]]) -> list[list[int]]:
    # The canonical reverse search. Water reaches an ocean from a cell exactly
    # when the cell is reachable FROM that ocean along edges that never go
    # downhill, i.e. the flow rule (neighbour <= current) read backwards
    # (neighbour >= current). Flood once from every border cell of each ocean --
    # O(m * n) per ocean, each cell enqueued at most once -- and intersect the
    # two visited grids. Row-major output, the statement's own order, so the
    # visible tests can be its examples transcribed.
    rows = len(heights)
    if rows == 0 or not heights[0]:
        return []
    cols = len(heights[0])

    def reachable_from(starts: list) -> list:
        seen = [[False] * cols for _ in range(rows)]
        queue = []
        for r, c in starts:
            if not seen[r][c]:
                seen[r][c] = True
                queue.append((r, c))
        head = 0
        while head < len(queue):
            r, c = queue[head]
            head += 1
            for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                nr, nc = r + dr, c + dc
                if (
                    0 <= nr < rows
                    and 0 <= nc < cols
                    and not seen[nr][nc]
                    and heights[nr][nc] >= heights[r][c]
                ):
                    seen[nr][nc] = True
                    queue.append((nr, nc))
        return seen

    pacific = reachable_from(
        [(0, c) for c in range(cols)] + [(r, 0) for r in range(rows)]
    )
    atlantic = reachable_from(
        [(rows - 1, c) for c in range(cols)] + [(r, cols - 1) for r in range(rows)]
    )
    return [
        [r, c]
        for r in range(rows)
        for c in range(cols)
        if pacific[r][c] and atlantic[r][c]
    ]


@measure("pacific-atlantic-water-flow")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    sorted."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'sorted'}
