"""QUARANTINED assessment for `k_smallest_elem_matrix` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("k_smallest_elem_matrix")
def _k_smallest_oracle(k: int, matrix: list[list[int]]) -> int:
    return sorted(x for row in matrix for x in row)[k - 1]


@cases("k_smallest_elem_matrix")
def _k_smallest_case(n: int, rng: random.Random) -> tuple[list, int]:
    n = max(1, min(n, 12))
    scale = rng.randint(1, 3)
    # (i+1)*(j+1) is sorted along rows and columns; a constant scale keeps that.
    matrix = [[scale * (i + 1) * (j + 1) for j in range(n)] for i in range(n)]
    k = rng.randint(1, n * n)
    return [k, matrix], _k_smallest_oracle(k, matrix)


@inputs("k_smallest_elem_matrix")
def _k_smallest_profiler(n: int, rng: random.Random) -> list:
    side = max(1, int(n ** 0.5))  # keep total elements ~n
    matrix = [[(i + 1) * (j + 1) for j in range(side)] for i in range(side)]
    return [max(1, side * side // 2), matrix]


@reference("k_smallest_elem_matrix")
def k_smallest(k: int, matrix: list[list[int]]) -> int:
    import heapq
    n = len(matrix)
    heap = [(matrix[i][0], i, 0) for i in range(n)]
    heapq.heapify(heap)
    for _ in range(k - 1):
        val, r, c = heapq.heappop(heap)
        if c + 1 < n:
            heapq.heappush(heap, (matrix[r][c + 1], r, c + 1))
    return heap[0][0]


@measure("k_smallest_elem_matrix")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
