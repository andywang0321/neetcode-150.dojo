"""QUARANTINED assessment for `number-of-1-bits` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, oracle, reference


@oracle("number-of-1-bits")
def _number_of_1_bits_oracle(n: int) -> int:
    """Brute force: spell the value in binary and count the '1' digits — a
    different route from the reference's bit trick, and obvious enough to trust.
    The statement's domain is n >= 1, where bin(n) prints the digits of n alone."""
    return bin(n).count("1")


@cases("number-of-1-bits")
def _number_of_1_bits_case(n: int, rng: random.Random) -> tuple[int, int]:
    # The statement's constraint is 1 <= n <= 2^31 - 1 on a single scalar, so the
    # case size cannot shape an input — it picks how many bits are set. Half the
    # cases get exactly that many, positions drawn from the full 31-bit width so
    # the high bits are exercised; half are any value in the statement's range.
    n = max(1, min(n, 12))
    if rng.random() < 0.5:
        value = rng.randint(1, 2**31 - 1)
    else:
        value = sum(1 << bit for bit in rng.sample(range(31), n))
    return [value], _number_of_1_bits_oracle(value)


@reference("number-of-1-bits")
def _number_of_1_bits_reference(n: int) -> int:
    """Canonical O(1): n & (n - 1) clears the lowest set bit, so the loop runs
    once per set bit — at most 31 steps for the statement's bound of 2^31 - 1."""
    count = 0
    while n:
        n &= n - 1
        count += 1
    return count
