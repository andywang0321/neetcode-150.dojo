"""Test fixture assessment: strict comparisons with an oracle and a reference."""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


def _is_valid(s: str) -> bool:
    pairs = {")": "(", "]": "[", "}": "{"}
    stack: list[str] = []
    for char in s:
        if char in "([{":
            stack.append(char)
        elif not stack or stack.pop() != pairs[char]:
            return False
    return not stack


@oracle("valid_parentheses")
def _oracle(s: str) -> bool:
    return _is_valid(s)


@cases("valid_parentheses")
def _cases(n: int, rng: random.Random) -> tuple[list, bool]:
    s = "".join(rng.choice("()[]{}") for _ in range(max(1, n)))
    return [s], _is_valid(s)


@inputs("valid_parentheses")
def _inputs(n: int, rng: random.Random) -> list:
    return ["(" * n + ")" * n]


@reference("valid_parentheses")
def _reference(s: str) -> bool:
    return _is_valid(s)


@measure("valid_parentheses")
def _measure(ctx: dict) -> dict:
    return {
        "axis": "n",
        "sizes": [64, 128, 256, 512],
        "baseline": "reference",
        "compare": "strict",
        "declared_time": "O(n)",
    }
