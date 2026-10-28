"""QUARANTINED assessment for `walls-and-gates` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("walls-and-gates")
def _walls_and_gates_oracle(rooms: list[list[int]]) -> None:
    """Brute force from the definition: the distance from a room to its nearest
    gate is the number of steps in the shortest path to one, so run one BFS per
    empty room and stop the moment a gate comes off the frontier. A room whose
    BFS exhausts everything it can reach without meeting a gate is unreachable
    and keeps its INF.

    The walks run on a SNAPSHOT of the grid, because the answers are written
    back into ``rooms`` as they are found: a walk that read the grid it is
    filling would treat an already-filled room as an obstacle (its value is no
    longer INF) and could report an unreachable room next to a gate. Slow on
    purpose -- O(empty rooms * cells) -- and total on an empty grid, on a grid
    of walls, and on a grid with no gate at all."""
    inf = 2147483647
    if not rooms or not rooms[0]:
        return
    rows, cols = len(rooms), len(rooms[0])
    snapshot = [row[:] for row in rooms]
    for i in range(rows):
        for j in range(cols):
            if snapshot[i][j] != inf:
                continue
            seen = {(i, j)}
            frontier = [(i, j)]
            distance = 0
            found = False
            while frontier and not found:
                distance += 1
                nxt = []
                for r, c in frontier:
                    for nr, nc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)):
                        if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in seen:
                            if snapshot[nr][nc] == 0:
                                found = True
                            elif snapshot[nr][nc] == inf:
                                seen.add((nr, nc))
                                nxt.append((nr, nc))
                frontier = nxt
            if found:
                rooms[i][j] = distance


@cases("walls-and-gates")
def _walls_and_gates_case(n: int, rng: random.Random) -> tuple[list, list, dict]:
    # The statement's own 1 <= m, n <= 250; the caller sends 0..12, so both
    # floors matter (a 0-row grid is not a legal input here). The three shapes
    # below are built rather than drawn, because the two families that matter
    # most -- no gate at all, and a gate walled off from part of the grid -- are
    # the ones a uniform draw almost never produces.
    inf = 2147483647
    rows = max(1, min(n, 12))
    cols = rng.randint(1, max(1, min(n, 12)))
    roll = rng.random()
    if roll < 0.2:
        # No gate at all: every empty room is unreachable and must come back
        # unchanged. The statement promises no gate, and a solution that seeds
        # its search from "a gate" has to survive having none.
        rooms = [[rng.choice((-1, inf)) for _ in range(cols)] for _ in range(rows)]
    elif roll < 0.4:
        # A full wall row splits the grid: the rooms above it can only reach
        # gates above it, and the rooms below it reach nothing. This is the
        # shape the statement's "cannot reach any gate stays INF" is about.
        rooms = [[inf] * cols for _ in range(rows)]
        wall = rows // 2
        for j in range(cols):
            rooms[wall][j] = -1
        rooms[rows - 1][rng.randrange(cols)] = 0
    else:
        # Uniform over the three values with a gate forced in: walls, gates and
        # rooms in every row-major order, so the row-major fill order of a naive
        # solution is exercised in both directions.
        rooms = [
            [rng.choice((-1, -1, 0, inf, inf, inf, inf)) for _ in range(cols)]
            for _ in range(rows)
        ]
        rooms[rng.randrange(rows)][rng.randrange(cols)] = 0
    expected = [row[:] for row in rooms]
    _walls_and_gates_oracle(expected)
    return [rooms], [expected], {"compare": "mutates"}


@inputs("walls-and-gates")
def _walls_and_gates_profiler(n: int, rng: random.Random) -> list:
    # ~n cells in a square-ish grid (rows grows while the square fits, so the
    # side lengths stay inside the statement's 1 <= m, n <= 250). Values are
    # only -1, 0 and 2147483647 -- the statement's own three values, nothing
    # else -- and probe_max_n caps the ladder at 1600 cells (40 x 40).
    #
    # Four gates, one near each corner of the reachable block, and a full wall
    # row near the bottom, below which two rows of rooms are walled off from
    # every gate: those rooms must come back as INF, which is the statement's
    # own sentence and the branch a solution that fills every room with some
    # number gets wrong. The multi-source reference visits every reachable cell
    # whatever the shape, so it has no early exit here; the naive per-room BFS
    # pays for the distance to the nearest corner gate, and that distance grows
    # with the grid, which is what makes a per-room-BFS student measure as
    # superlinear rather than merely slower.
    inf = 2147483647
    rows = 1
    while rows < 250 and (rows + 1) * (rows + 1) <= n:
        rows += 1
    cols = max(1, n // rows)
    rooms = [[inf] * cols for _ in range(rows)]
    if rows >= 3:
        wall = rows - 3
        for j in range(cols):
            rooms[wall][j] = -1
    last_open = rows - 4 if rows >= 4 else 0
    for i, j in ((0, 0), (0, cols - 1), (last_open, 0), (last_open, cols - 1)):
        if rooms[i][j] == inf:
            rooms[i][j] = 0
    return [rooms]


@reference("walls-and-gates")
def _walls_and_gates_reference(rooms: list[list[int]]) -> None:
    """Multi-source BFS: every gate starts in the queue at distance 0, and a
    room is settled with its distance the first time the wave reaches it -- that
    first arrival IS the shortest path to some gate, which is why one shared
    wave replaces a search per room. Rooms no wave reaches keep their INF.

    O(m * n) time and O(m * n) space (the queue), standalone: no imports, one
    top-level function, so the probe's subprocess can run it as it stands."""
    inf = 2147483647
    rows = len(rooms)
    if not rows or not rooms[0]:
        return
    cols = len(rooms[0])
    queue = []
    head = 0
    for i in range(rows):
        for j in range(cols):
            if rooms[i][j] == 0:
                queue.append((i, j))
    while head < len(queue):
        r, c = queue[head]
        head += 1
        step = rooms[r][c] + 1
        for nr, nc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)):
            if 0 <= nr < rows and 0 <= nc < cols and rooms[nr][nc] == inf:
                rooms[nr][nc] = step
                queue.append((nr, nc))


@measure("walls-and-gates")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    mutates."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'mutates'}
