"""QUARANTINED assessment for `surrounded-regions` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("surrounded-regions")
def _surrounded_regions_oracle(board: list[list[str]]) -> None:
    """Brute force by the definition, one region at a time: take the first 'O'
    that has not been decided yet, flood its whole region (cells connected
    horizontally or vertically), decide the region by ONE question -- does any of
    its cells sit on the edge of the board? -- and then write that decision into
    every cell of the region. Regions are found and judged, not searched for from
    the border, so the statement's definition is applied literally and no
    conclusion is drawn from a cell's position before its region is known.

    '.' is a third state that cannot collide with the statement's 'X'/'O'
    alphabet; it marks a cell as belonging to a region that has already been
    decided, which is what keeps the outer scan from deciding one twice. Writes
    into the argument in place, which is what dojo's "mutates" verdict compares
    (the function returns None). Total on an empty board (the 1 <= m, n
    constraint excludes it) and on an all-'X' board; assumes rectangular rows,
    which m x n promises."""
    rows = len(board)
    if rows == 0:
        return
    cols = len(board[0])
    for r0 in range(rows):
        for c0 in range(cols):
            if board[r0][c0] != "O":
                continue
            region = [(r0, c0)]
            board[r0][c0] = "."
            surrounded = True
            head = 0
            while head < len(region):
                r, c = region[head]
                head += 1
                if r == 0 or c == 0 or r == rows - 1 or c == cols - 1:
                    surrounded = False
                for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < rows and 0 <= nc < cols and board[nr][nc] == "O":
                        board[nr][nc] = "."
                        region.append((nr, nc))
            for r, c in region:
                board[r][c] = "X" if surrounded else "O"


@cases("surrounded-regions")
def _surrounded_regions_case(n: int, rng: random.Random) -> tuple[list, list, dict]:
    # ~n cells in a shape the statement allows (1 <= m, n <= 200, every row the
    # same length); the caller sends 0..12, so the floor is a 1 x 1 board. The
    # shape draw has two branches because the case that matters here is the
    # ENCLOSED region, and a board only has one if it has an interior: when the
    # budget allows (>= 9 cells) most draws are 3-4 rows by 3-4 columns, and the
    # rest is the full range, which is what puts single-row and single-column
    # boards in the set. An earlier draft drew rows uniformly over 1..n, which
    # made cols = 1 the common case, and the cost was measured before it was
    # fixed: over 2000 cases only 11 boards changed at all and just 28 had a
    # 3x3-or-larger interior, so a solution that did NOTHING passed 99.5% of the
    # generated cases. That is the whole point of this generator, so the draw
    # was corrected.
    #
    # Three boards, because a region's fate has two outcomes: all 'O' (one region
    # lying on the edge -- nothing is captured), an 'X'-dominant random board
    # (small regions, some of them enclosed by luck), and all 'X' with one 'O'
    # rectangle planted strictly inside, which is surrounded BY CONSTRUCTION and
    # must be captured. expected is the argument list after the call, taken from
    # the oracle on a copy -- the "mutates" contract.
    cells = max(1, min(n, 12))
    if cells >= 9 and rng.random() < 0.6:
        rows = rng.randint(3, min(4, cells // 3))
        cols = rng.randint(3, max(3, cells // rows))
    else:
        rows = rng.randint(1, cells)
        cols = rng.randint(1, max(1, cells // rows))
    roll = rng.random()
    if roll < 0.25:
        # One region covering the whole board, lying on the edge: nothing is
        # captured, whatever the shape.
        board = [["O"] * cols for _ in range(rows)]
    elif rows >= 3 and cols >= 3 and roll < 0.8:
        # All 'X' with one 'O' rectangle planted strictly inside. This is the
        # branch that makes the capture path COMMON rather than lucky, and it is
        # why the shape draw above exists: a board with no interior (fewer than
        # 3 rows or 3 columns) makes an enclosed region impossible, so a quarter
        # of the caller's size range could never exercise it.
        board = [["X"] * cols for _ in range(rows)]
        top, bottom = rng.randint(1, rows - 2), rng.randint(1, rows - 2)
        left, right = rng.randint(1, cols - 2), rng.randint(1, cols - 2)
        for r in range(min(top, bottom), max(top, bottom) + 1):
            for c in range(min(left, right), max(left, right) + 1):
                board[r][c] = "O"
    elif rows * cols > 1:
        # 'X'-dominant random: small regions, some enclosed by luck. On a board
        # with no interior nothing can be enclosed, and the case still pins that
        # an edge region survives.
        board = [
            ["X" if rng.random() < 0.6 else "O" for _ in range(cols)]
            for _ in range(rows)
        ]
    else:
        board = [["X"]]  # the 1 x 1 board the constraints allow
    expected = [row[:] for row in board]
    _surrounded_regions_oracle(expected)
    return [board], [expected], {"compare": "mutates"}


@inputs("surrounded-regions")
def _surrounded_regions_profiler(n: int, rng: random.Random) -> list:
    """A square-ish board of ~n cells with a one-cell 'X' frame drawn inside the
    border.

    The outermost ring is all 'O' and connected, so the border flood marks the
    whole ring and cannot early-exit (the frame is the only thing that could stop
    it, and the ring goes around the frame); everything inside the frame is one
    enclosed 'O' region that MUST be captured. Both halves of the problem are
    therefore exercised at every rung -- the safe marking, the capture, and the
    final sweep over all m * n cells -- and the answer is the input with its
    interior turned to 'X', so it is not the identity. That last part is
    load-bearing for the probe: scale_compare is "mutates", so the digest is the
    mutated board, and an all-'O' board (the other candidate worst case) would
    have digested identical to its input, i.e. it would have passed for a student
    who did nothing at all. Values are only 'X' and 'O', the statement's
    alphabet.

    No probe_max_n: the default ladder's largest point is 6400 cells = 80 x 80,
    inside the statement's 1 <= m, n <= 200, and this oracle is O(m * n) (one
    region decision per cell, never revisited), so it survives the same input at
    the top rung. Boards smaller than 5 x 5 have no room for a frame and come
    back all 'O' (every cell is then on the edge, so nothing is captured). rng is
    unused -- a paired measurement wants the same deterministic board at every
    rung."""
    cells = max(1, n)
    rows = 1
    while rows < 200 and (rows + 1) * (rows + 1) <= cells:
        rows += 1
    cols = max(1, cells // rows)
    board = [["O"] * cols for _ in range(rows)]
    if rows >= 5 and cols >= 5:
        for c in range(1, cols - 1):
            board[1][c] = "X"
            board[rows - 2][c] = "X"
        for r in range(1, rows - 1):
            board[r][1] = "X"
            board[r][cols - 2] = "X"
    return [board]


@reference("surrounded-regions")
def _surrounded_regions_reference(board: list[list[str]]) -> None:
    # The canonical border flood, in place: every 'O' reachable from the edge is
    # NOT surrounded (the statement's rule), so mark those 'S' and flood them
    # once (each cell enqueued at most once -- O(m * n) time), then one sweep
    # turns the remaining 'O' into 'X' and the 'S' marks back into 'O'. 'S' is a
    # state the input can never contain (the alphabet is 'X'/'O'), so it cannot
    # be confused with data. Two full passes over m * n cells and a stack that
    # can hold O(m * n) cells at the worst point: the declared space is
    # therefore O(m * n), not O(1).
    rows = len(board)
    if rows == 0:
        return
    cols = len(board[0])
    stack = []
    for r in range(rows):
        for c in (0, cols - 1):
            if board[r][c] == "O":
                board[r][c] = "S"
                stack.append((r, c))
    for c in range(cols):
        for r in (0, rows - 1):
            if board[r][c] == "O":
                board[r][c] = "S"
                stack.append((r, c))
    while stack:
        r, c = stack.pop()
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and board[nr][nc] == "O":
                board[nr][nc] = "S"
                stack.append((nr, nc))
    for r in range(rows):
        for c in range(cols):
            if board[r][c] == "O":
                board[r][c] = "X"
            elif board[r][c] == "S":
                board[r][c] = "O"


@measure("surrounded-regions")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    mutates."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'mutates'}
