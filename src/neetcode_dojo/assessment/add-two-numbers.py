"""QUARANTINED assessment for `add-two-numbers` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("add-two-numbers")
def _add_two_numbers_oracle(l1: list[int], l2: list[int]) -> list[int]:
    """Brute force via Python's bignums: rebuild both numbers from their digit
    lists, add them, and decompose the sum back into little-endian digits. It
    shares no step with the reference's carry loop, which is what makes the
    differential worth something."""
    a = 0
    for digit in reversed(l1):
        a = a * 10 + digit
    b = 0
    for digit in reversed(l2):
        b = b * 10 + digit
    total = a + b
    if total == 0:
        return [0]
    out: list[int] = []
    while total:
        out.append(total % 10)
        total //= 10
    return out


@cases("add-two-numbers")
def _add_two_numbers_case(n: int, rng: random.Random) -> tuple[list, list]:
    n = max(1, min(n, 12))  # the statement's floor: each list has >= 1 node
    m = max(1, min(n, 12))
    l1 = [rng.randint(0, 9) for _ in range(n)]
    l2 = [rng.randint(0, 9) for _ in range(m)]
    # The statement's guarantee is that neither list represents a number with a
    # leading zero, and a leading zero IS the most significant digit here: a
    # list ending in 0 would be a non-canonical number whose digit-wise sum has
    # more digits than its integer sum, so it is not a case this problem defines.
    # So the top digit is always redrawn from [1, 9] — and 15% of the time the
    # other list is the statement's one exception, the number 0 itself.
    l1[-1] = rng.randint(1, 9)
    l2[-1] = rng.randint(1, 9)
    if rng.random() < 0.15:
        l2 = [0]
    return [l1, l2], _add_two_numbers_oracle(l1, l2)


@inputs("add-two-numbers")
def _add_two_numbers_profiler(n: int, rng: random.Random) -> list:
    """Two 100-digit numbers of all 9s: 999...9 + 999...9 forces the carry to
    propagate through all 100 positions and the result to be one node longer
    than either input. Nothing can early-exit, and both inputs sit exactly on
    the statement's limit (nodes <= 100, digits 0..9)."""
    digits = [9] * max(1, min(n, 100))
    return [digits, list(digits)]


@reference("add-two-numbers")
def _add_two_numbers_reference(l1: list[int], l2: list[int]) -> list[int]:
    out: list[int] = []
    carry = 0
    i = 0
    while i < len(l1) or i < len(l2) or carry:
        total = carry
        if i < len(l1):
            total += l1[i]
        if i < len(l2):
            total += l2[i]
        out.append(total % 10)
        carry = total // 10
        i += 1
    return out or [0]


@measure("add-two-numbers")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
