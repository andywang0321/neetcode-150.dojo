"""Test fixture assessment: the ``ops`` (class API) case shape."""

import random

from neetcode_dojo.registry import cases, oracle


@oracle("min_stack")
def _oracle(ops: list[list]) -> list:
    stack: list[int] = []
    mins: list[int] = []
    out: list = []
    for operation in ops:
        method, *args = operation
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
        else:
            raise ValueError(f"unknown op {method}")
    return out


@cases("min_stack")
def _cases(n: int, rng: random.Random) -> tuple[list, list, dict]:
    ops: list[list] = []
    size = 0
    for _ in range(max(1, min(n, 12)) * 2 + 1):
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
    return [], _oracle(ops), {"ops": ops}
