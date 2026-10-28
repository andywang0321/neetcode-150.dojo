"""QUARANTINED assessment for `rotate-image` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("rotate-image")
def _rotate_image_oracle(matrix: list[list[int]]) -> None:
    """Brute force by the definition: after a 90-degree clockwise turn the cell
    at (i, j) belongs at (j, size - 1 - i), so build the destination grid from
    that formula and write it back into the argument the caller holds - the
    post-call argument list is exactly what dojo's "mutates" verdict compares.
    Total on an empty matrix (the statement requires at least one row)."""
    size = len(matrix)
    rotated = [[0] * size for _ in range(size)]
    for i in range(size):
        for j in range(size):
            rotated[j][size - 1 - i] = matrix[i][j]
    matrix[:] = rotated


@cases("rotate-image")
def _rotate_image_case(n: int, rng: random.Random) -> tuple[list, list, dict]:
    side = max(1, min(n, 12))  # the statement's 1 <= n <= 20; the caller sends 0..12
    matrix = [[rng.randint(-1000, 1000) for _ in range(side)] for _ in range(side)]
    expected = [row[:] for row in matrix]
    _rotate_image_oracle(expected)
    # A "mutates" case: expected is the ARGUMENT LIST as it must stand after the
    # call, not the (None) return value the function hands back.
    return [matrix], [expected], {"compare": "mutates"}


@inputs("rotate-image")
def _rotate_image_profiler(n: int, rng: random.Random) -> list:
    # A square matrix of ~n cells: side = isqrt(n), counted up by hand because the
    # registry imports only `random`. The side is capped at the statement's own
    # 20, so with probe_max_n = 400 the ladder's largest point is exactly
    # 20 x 20 = 400 cells and NO point can exceed the statement's constraint.
    # Every cell holds a distinct value inside -1000..1000 (at most 400 cells and
    # 5 * index stays below 2001), so the digest is a real statement about the
    # permutation: a transpose-only, a row-flipped or a truncated rotation cannot
    # digest-match the reference. Nothing here can early-exit - a rotation has to
    # touch all n^2 cells whichever way it is written.
    side = 1
    while side < 20 and (side + 1) * (side + 1) <= n:
        side += 1
    return [
        [[(5 * (i * side + j)) % 2001 - 1000 for j in range(side)] for i in range(side)]
    ]


@reference("rotate-image")
def _rotate_image_reference(matrix: list[list[int]]) -> None:
    # The canonical two steps, both inside the matrix that was handed over: the
    # transpose swap loop (each pair of off-diagonal cells once) and then a
    # reversal of every row. O(n^2) time and O(1) extra space - this reference
    # never builds a second matrix, which is the space baseline the probe
    # measures a student's allocations against.
    size = len(matrix)
    for i in range(size):
        for j in range(i + 1, size):
            matrix[i][j], matrix[j][i] = matrix[j][i], matrix[i][j]
    for row in matrix:
        row.reverse()


@measure("rotate-image")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    mutates."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'mutates'}
