"""QUARANTINED assessment for `generate_parentheses` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, oracle, reference


@oracle("generate_parentheses")
def _generate_parentheses_oracle(n: int) -> list[str]:
    out: list[str] = []

    def build(prefix: str, opens: int, closes: int) -> None:
        if opens == n and closes == n:
            out.append(prefix)
            return
        if opens < n:
            build(prefix + "(", opens + 1, closes)
        if closes < opens:
            build(prefix + ")", opens, closes + 1)

    build("", 0, 0)
    return out  # DFS yields lexicographic order


@cases("generate_parentheses")
def _generate_parentheses_case(n: int, rng: random.Random) -> tuple[list, list, dict]:
    n = max(1, min(n, 7))
    return [n], _generate_parentheses_oracle(n), {"compare": "sorted"}


@reference("generate_parentheses")
def generate_parentheses(n: int) -> list[str]:
    out: list[str] = []
    buf: list[str] = []

    def build(opens: int, closes: int) -> None:
        if opens == n and closes == n:
            out.append("".join(buf))
            return
        if opens < n:
            buf.append("(")
            build(opens + 1, closes)
            buf.pop()
        if closes < opens:
            buf.append(")")
            build(opens, closes + 1)
            buf.pop()

    build(0, 0)
    return out
