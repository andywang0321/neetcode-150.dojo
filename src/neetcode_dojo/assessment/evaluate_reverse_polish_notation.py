"""QUARANTINED assessment for `evaluate_reverse_polish_notation` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


def _random_expr(rng: random.Random, depth: int) -> tuple[list[str], int]:
    """A random RPN expression (tokens, value). Leaves are nonzero so
    division never divides by zero."""
    if depth <= 0 or rng.random() < 0.4:
        value = rng.choice([v for v in range(-10, 11) if v != 0])
        return [str(value)], value
    left_tokens, left = _random_expr(rng, depth - 1)
    right_tokens, right = _random_expr(rng, depth - 1)
    op = rng.choice("+-*/")
    if op == "+":
        value = left + right
    elif op == "-":
        value = left - right
    elif op == "*":
        value = left * right
    else:
        if right == 0:
            right = rng.randint(1, 10)
            right_tokens = [str(right)]
        value = int(left / right)  # truncation toward zero, per the prompt
    return left_tokens + right_tokens + [op], value


@oracle("evaluate_reverse_polish_notation")
def _eval_rpn_oracle(tokens: list[str]) -> int:
    stack: list[int] = []
    for tok in tokens:
        if tok in "+-*/":
            b = stack.pop()
            a = stack.pop()
            if tok == "+":
                stack.append(a + b)
            elif tok == "-":
                stack.append(a - b)
            elif tok == "*":
                stack.append(a * b)
            else:
                stack.append(int(a / b))
        else:
            stack.append(int(tok))
    return stack[-1]


@cases("evaluate_reverse_polish_notation")
def _eval_rpn_case(n: int, rng: random.Random) -> tuple[list, int]:
    n = max(1, min(n, 10))
    tokens, value = _random_expr(rng, depth=3)
    return [tokens], value


@inputs("evaluate_reverse_polish_notation")
def _eval_rpn_profiler(n: int, rng: random.Random) -> list:
    return [["1", "1", "+"] * max(1, n // 3)]


@reference("evaluate_reverse_polish_notation")
def eval_rpn(tokens: list[str]) -> int:
    stack: list[int] = []
    for tok in tokens:
        if tok == "+":
            b = stack.pop()
            a = stack.pop()
            stack.append(a + b)
        elif tok == "-":
            b = stack.pop()
            a = stack.pop()
            stack.append(a - b)
        elif tok == "*":
            b = stack.pop()
            a = stack.pop()
            stack.append(a * b)
        elif tok == "/":
            b = stack.pop()
            a = stack.pop()
            stack.append(int(a / b))
        else:
            stack.append(int(tok))
    return stack[-1]


@measure("evaluate_reverse_polish_notation")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
