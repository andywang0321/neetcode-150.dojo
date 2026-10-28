"""QUARANTINED assessment for `products_of_array_except_self` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("products_of_array_except_self")
def _prod_except_self_oracle(nums: list[int]) -> list[int]:
    out: list[int] = []
    for i in range(len(nums)):
        product = 1
        for j in range(len(nums)):
            if i != j:
                product *= nums[j]
        out.append(product)
    return out


@cases("products_of_array_except_self")
def _prod_except_self_case(n: int, rng: random.Random) -> tuple[list, list]:
    n = max(0, min(n, 12))
    nums = [rng.randint(-5, 5) for _ in range(n)]
    return [nums], _prod_except_self_oracle(nums)


@inputs("products_of_array_except_self")
def _prod_except_self_profiler(n: int, rng: random.Random) -> list:
    return [[rng.randint(-20, 20) or 1 for _ in range(n)]]


@reference("products_of_array_except_self")
def _prod_except_self_reference(nums: list[int]) -> list[int]:
    """Prefix/suffix products — the intended O(n).

    The oracle is an O(n^2) double loop, so before this reference existed the
    problem had no fast baseline at all: the probe could only have reported a
    correct O(n) solution as "faster than the reference", which says nothing."""
    size = len(nums)
    out = [1] * size
    left = 1
    for i in range(size):
        out[i] = left
        left *= nums[i]
    right = 1
    for i in range(size - 1, -1, -1):
        out[i] *= right
        right *= nums[i]
    return out


@measure("products_of_array_except_self")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
