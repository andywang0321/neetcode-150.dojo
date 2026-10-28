"""QUARANTINED assessment for `longest-increasing-path-in-a-matrix` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("longest-increasing-path-in-a-matrix")
def _longest_increasing_path_in_a_matrix_oracle(matrix: list[list[int]]) -> int:
    # Brute force by the statement's definition: try every cell as a start and
    # walk every strictly increasing path out of it, with NO memo -- the path
    # itself is the only state, so nothing is shared between starts, and a
    # memoised solution is a different program entirely. Total on an empty
    # matrix and on a matrix with an empty first row, neither of which the
    # statement's 1 <= m, n allows.
    rows = len(matrix)
    cols = len(matrix[0]) if rows else 0
    if rows == 0 or cols == 0:
        return 0
    best = 0

    def walk(r: int, c: int, length: int) -> None:
        nonlocal best
        if length > best:
            best = length
        current = matrix[r][c]
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and matrix[nr][nc] > current:
                walk(nr, nc, length + 1)

    for r in range(rows):
        for c in range(cols):
            walk(r, c, 1)
    return best


@cases("longest-increasing-path-in-a-matrix")
def _longest_increasing_path_in_a_matrix_case(n: int, rng: random.Random) -> tuple[list, int]:
    # At most 12 cells (the caller sends 0..12; the statement's floor is 1 <= m, n)
    # in a square-ish grid, carrying one of four labelings, every one inside the
    # statement's 0 <= matrix[i][j] <= 2^31 - 1:
    #   * the boustrophedon snake -- all cells lie on one increasing path, so the
    #     answer is the cell count and a walk that stops one step short is caught;
    #   * a grid whose cells are ALL equal -- equal neighbours are not a step
    #     (example 1's duplicate 9s are the statement's own evidence), so the
    #     answer is 1;
    #   * a draw from the statement's two extreme values, 0 and 2^31 - 1, so ties
    #     and steps live in the same grid and the value bound is exercised;
    #   * a plain draw from 0..3, where duplicates are common.
    # 12 cells is also what keeps the enumeration oracle cheap: the 3 x 4 snake is
    # the worst shape the generator can reach, and it has 175 increasing paths
    # (measured), so the oracle's enumeration stays well inside a millisecond.
    n = max(1, min(n, 12))
    rows = 1
    while rows < 4 and (rows + 1) * (rows + 1) <= n:
        rows += 1
    cols = max(1, n // rows)
    shape = n % 4
    if shape == 0:
        matrix = [[0] * cols for _ in range(rows)]
        value = 0
        for i in range(rows):
            order = range(cols) if i % 2 == 0 else range(cols - 1, -1, -1)
            for j in order:
                value += 1
                matrix[i][j] = value
    elif shape == 1:
        flat = rng.randint(0, 2**31 - 1)
        matrix = [[flat] * cols for _ in range(rows)]
    elif shape == 2:
        matrix = [
            [rng.choice([0, 2**31 - 1]) for _ in range(cols)] for _ in range(rows)
        ]
    else:
        matrix = [[rng.randint(0, 3) for _ in range(cols)] for _ in range(rows)]
    return [matrix], _longest_increasing_path_in_a_matrix_oracle(matrix)


@inputs("longest-increasing-path-in-a-matrix")
def _longest_increasing_path_in_a_matrix_profiler(n: int, rng: random.Random) -> list:
    # ~n cells in a square-ish grid, both dimensions far below the statement's own
    # 200 (the ladder tops out at 28 x 28 = 784, which is probe_max_n). The grid
    # holds ONE long strictly increasing corridor -- every cell of the even rows,
    # joined by two-cell connectors in the odd rows at alternating ends, so the
    # path is a staircase, no two of its cells are adjacent out of order, and the
    # longest path is its length -- plus filler holding the statement's maximum
    # value 2^31 - 1, which can be neither entered from the corridor's interior
    # nor chained through (equal values are not steps).
    #
    # Why a corridor and not a boustrophedon snake over the whole grid, which is
    # the textbook worst case: (a) the oracle here is a brute-force enumeration of
    # every increasing path, and this is the input `_oracle_confirms` feeds it, in
    # process and with no timeout, whenever a student's output disagrees with the
    # reference at scale -- a Hamiltonian snake has ~2^700 increasing paths at
    # 784 cells, so that call would never return, while this corridor has ~L^2/2
    # (measured: ~0.3 s for the whole enumeration at the top of the ladder);
    # (b) a snake's longest path is the whole grid, so a canonical recursive
    # memoised solution -- and any student's -- would hit Python's recursion limit
    # instead of the algorithm being measured (the corpus builds complete trees
    # rather than spines for exactly this reason). The memo-less signal survives:
    # measured by the probe itself across this ladder, a memo-less walk's paired
    # ratio against the reference rises from 4.4 to ~283.
    size = max(1, min(int(n), 40_000))
    rows = 1
    while rows < 200 and (rows + 1) * (rows + 1) <= size:
        rows += 1
    cols = max(1, size // rows)
    matrix = [[2**31 - 1] * cols for _ in range(rows)]
    cap = 700  # a ceiling for callers that ask for the statement's 200 x 200
    path = [(0, 0)]
    r, c, step = 0, 0, 1
    while len(path) < cap:
        while 0 <= c + step < cols:
            c += step
            path.append((r, c))
            if len(path) >= cap:
                break
        if len(path) >= cap or r + 1 >= rows:
            break
        r += 1
        path.append((r, c))
        if len(path) >= cap or r + 1 >= rows:
            break
        r += 1
        path.append((r, c))
        step = -step
    for value, (rr, cc) in enumerate(path, start=1):
        matrix[rr][cc] = value
    return [matrix]


@reference("longest-increasing-path-in-a-matrix")
def _longest_increasing_path_in_a_matrix_reference(matrix: list[list[int]]) -> int:
    # The canonical memoised DFS: the longest increasing path starting at a cell
    # is 1 + the best of its strictly larger neighbours, so each cell's answer is
    # computed once and every later visit is a dict hit. O(m * n) time and
    # O(m * n) space -- the class the statement's complexity line declares -- and
    # total on an empty matrix, which the statement's 1 <= m, n excludes. The
    # recursion is as deep as the longest path, which is why the profiler input's
    # corridor is bounded rather than spanning the grid: at the top of the ladder
    # that is 407 frames, well inside the limit a live probe has (~995 measured).
    rows = len(matrix)
    cols = len(matrix[0]) if rows else 0
    if rows == 0 or cols == 0:
        return 0
    memo: dict[tuple[int, int], int] = {}

    def best_from(r: int, c: int) -> int:
        key = (r, c)
        if key in memo:
            return memo[key]
        longest = 1
        current = matrix[r][c]
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and matrix[nr][nc] > current:
                candidate = 1 + best_from(nr, nc)
                if candidate > longest:
                    longest = candidate
        memo[key] = longest
        return longest

    answer = 0
    for r in range(rows):
        for c in range(cols):
            candidate = best_from(r, c)
            if candidate > answer:
                answer = candidate
    return answer


@measure("longest-increasing-path-in-a-matrix")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
