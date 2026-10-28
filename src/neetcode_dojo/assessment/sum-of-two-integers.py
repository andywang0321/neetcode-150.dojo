"""QUARANTINED assessment for `sum-of-two-integers` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, oracle, reference


@oracle("sum-of-two-integers")
def _sum_of_two_integers_oracle(a: int, b: int) -> int:
    # Brute force, and deliberately NOT a solution to the puzzle: the oracle's
    # only job is to produce the right integer, and it may use the very operator
    # the statement forbids the student. Python's own integer addition shares no
    # step with the reference's carry loop, which is what makes the differential
    # against the reference worth something. Total over every pair.
    return sum((a, b))


@cases("sum-of-two-integers")
def _sum_of_two_integers_case(n: int, rng: random.Random) -> tuple[list, int]:
    bound = 1000  # the statement's own value constraint: -1000 <= a, b <= 1000
    # There is no length in this problem, so the caller's n (0..12) cannot be
    # clamped into a size constraint. It selects WHICH shape of pair this case
    # is, so the pairs a bit-trick solution gets wrong are emitted on purpose
    # instead of being left to a lucky draw; the live judge draws n at random,
    # so all five shapes appear within a session.
    shape = n % 5
    if shape == 0:  # any pair inside the range: both signs, any magnitudes
        a, b = rng.randint(-bound, bound), rng.randint(-bound, bound)
    elif shape == 1:  # the ends of the stated range, and zero
        a = rng.choice([-bound, bound])
        b = rng.choice([-bound, bound, 0])
    elif shape == 2:  # zero and the additive identities
        a = rng.choice([0, 1, -1, 2, -2])
        b = rng.choice([0, 1, -1, -bound, bound])
    elif shape == 3:  # a carry chain through every bit: (2^k - 1) + 1
        k = rng.randint(1, 9)
        a = (1 << k) - 1
        b = rng.choice([1, -1, 1 << k, -(1 << k)])
    else:  # opposite signs, half of them cancelling exactly: a + (-a) is the
        # pair a naive unmasked Python carry loop never escapes from
        a = rng.randint(1, bound)
        b = -a if rng.random() < 0.5 else -rng.randint(1, bound)
    return [a, b], _sum_of_two_integers_oracle(a, b)


@reference("sum-of-two-integers")
def _sum_of_two_integers_reference(a: int, b: int) -> int:
    # The canonical bit-trick add: XOR is the sum without carries, AND shifted
    # left is the carry, and the two are folded together until no carry is left.
    # The 32-bit mask is load-bearing in Python, not decoration: on unbounded
    # ints the plain `(a & b) << 1` of an opposite-sign pair gains a set bit
    # above bit 31 on every pass and never terminates (a = 1000, b = -1000 runs
    # forever — see the notes). Masking to the statement's own 32-bit setting
    # bounds the loop at 32 passes, and the sign is restored with ~ so this
    # reference uses no `+` and no `-` either: it obeys the rule it teaches.
    # O(1) time, O(1) space.
    mask = 0xFFFFFFFF
    x, y = a & mask, b & mask
    while y:
        carry = ((x & y) << 1) & mask
        x = (x ^ y) & mask
        y = carry
    return x if x < 0x80000000 else ~(x ^ mask)
