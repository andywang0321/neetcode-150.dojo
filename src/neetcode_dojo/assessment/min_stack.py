"""QUARANTINED assessment for `min_stack` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, oracle


@oracle("min_stack")
def _min_stack_oracle(ops: list[list]) -> list:
    stack: list[int] = []
    mins: list[int] = []
    out: list = []
    for op in ops:
        method, *args = op
        if method == "push":
            stack.append(args[0])
            mins.append(args[0] if not mins else min(args[0], mins[-1]))
            out.append(None)
        elif method == "pop":
            stack.pop()
            mins.pop()
            out.append(None)
        elif method == "top":
            out.append(stack[-1])
        elif method == "getMin":
            out.append(mins[-1])
        else:  # pragma: no cover - generators only emit the four methods
            raise ValueError(f"unknown op {method}")
    return out


@cases("min_stack")
def _min_stack_case(n: int, rng: random.Random) -> tuple[list, list, dict]:
    n = max(1, min(n, 12))
    ops: list[list] = []
    size = 0
    for _ in range(n * 2 + 1):
        choices = ["push"]
        if size > 0:
            choices += ["pop", "top", "getMin"]
        method = rng.choice(choices)
        if method == "push":
            ops.append(["push", rng.randint(-20, 20)])
            size += 1
        else:
            ops.append([method])
            if method == "pop":
                size -= 1
    return [], _min_stack_oracle(ops), {"ops": ops}
