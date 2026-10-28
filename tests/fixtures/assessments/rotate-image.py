"""Test fixture assessment: the ``mutates`` (in-place) comparison mode."""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


def _rotate(matrix: list[list[int]]) -> None:
    size = len(matrix)
    rotated = [[0] * size for _ in range(size)]
    for i in range(size):
        for j in range(size):
            rotated[j][size - 1 - i] = matrix[i][j]
    matrix[:] = rotated


@oracle("rotate-image")
def _oracle(matrix: list[list[int]]) -> None:
    _rotate(matrix)


@cases("rotate-image")
def _cases(n: int, rng: random.Random) -> tuple[list, list, dict]:
    side = max(1, min(n, 12))
    matrix = [[rng.randint(-1000, 1000) for _ in range(side)] for _ in range(side)]
    expected = [row[:] for row in matrix]
    _rotate(expected)
    return [matrix], [expected], {"compare": "mutates"}


@inputs("rotate-image")
def _inputs(n: int, rng: random.Random) -> list:
    side = max(1, int(n**0.5))
    return [[[rng.randint(-1000, 1000) for _ in range(side)] for _ in range(side)]]


@reference("rotate-image")
def _reference(matrix: list[list[int]]) -> None:
    size = len(matrix)
    for i in range(size):
        for j in range(i + 1, size):
            matrix[i][j], matrix[j][i] = matrix[j][i], matrix[i][j]
    for row in matrix:
        row.reverse()


@measure("rotate-image")
def _measure(ctx: dict) -> dict:
    return {
        "axis": "n",
        "sizes": [64, 144],
        "baseline": "reference",
        "compare": "mutates",
    }
