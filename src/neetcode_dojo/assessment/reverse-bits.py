"""QUARANTINED assessment for `reverse-bits` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, oracle, reference


@oracle("reverse-bits")
def _reverse_bits_oracle(n: int) -> int:
    """Brute force: write the value as a 32-character binary word and read it
    backwards — a different route from the reference's shift loop, and obvious
    enough to trust. 32 characters is exact on the graded domain, because no case
    exceeds the statement's 2^31 - 2."""
    return int(f"{n:032b}"[::-1], 2)


@cases("reverse-bits")
def _reverse_bits_case(n: int, rng: random.Random) -> tuple[int, int]:
    # The statement bounds the value itself (0 <= n <= 2^31 - 2, and n is even),
    # so the case size chooses a shape rather than a size: the lower bound, the
    # upper bound, and random even values drawn as 2 * k with k < 2^30.
    n = max(0, min(n, 12))
    if n == 0:
        value = 0
    elif n == 12:
        value = 2**31 - 2
    else:
        value = 2 * rng.randrange(2**30)  # even and <= 2^31 - 2, as the statement requires
    return [value], _reverse_bits_oracle(value)


@reference("reverse-bits")
def _reverse_bits_reference(n: int) -> int:
    """Canonical O(1): 32 fixed iterations, each pushing n's lowest bit onto the
    right of the result and shifting n down — the 32-bit reversal by definition."""
    result = 0
    for _ in range(32):
        result = (result << 1) | (n & 1)
        n >>= 1
    return result
