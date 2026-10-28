"""QUARANTINED assessment for `reverse-integer` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, oracle, reference


@oracle("reverse-integer")
def _reverse_integer_oracle(x: int) -> int:
    # Brute force, and a different mechanism from the reference's digit
    # arithmetic: spell the digits out with str, reverse the string, parse it
    # back (int() drops the leading zeros a trailing-zero input produces), then
    # apply the statement's rule literally — outside [-2^31, 2^31 - 1] the
    # answer is 0. Total for every int, including 0 and both range ends.
    if x < 0:
        value = -int(str(-x)[::-1])
    else:
        value = int(str(x)[::-1])
    if value < -(2**31) or value > 2**31 - 1:
        return 0
    return value


@cases("reverse-integer")
def _reverse_integer_case(n: int, rng: random.Random) -> tuple[list, int]:
    # The 32-bit overflow rule is what this problem is about, so it is not left
    # to chance: the first branch is one rng.random() < 0.5 draw and EVERY value
    # it can produce reverses out of [-2^31, 2^31 - 1], so P(overflow) = 0.5 for
    # a generated case and the other half is guaranteed in range. Both halves
    # keep x itself inside the statement's own -2^31 <= x <= 2^31 - 1.
    if rng.random() < 0.5:  # OVERFLOW HALF: the oracle answers 0 for every case
        if rng.random() < 0.25:  # the classic boundary values, checked by hand
            x = rng.choice([1534236469, -1534236469, -1563847412, -2147483648, 2147483647])
        else:
            # Ten digits whose LAST digit is 3..9, so the reversal starts with
            # 3..9 and is therefore >= 3 * 10^9: above 2^31 - 1 on the positive
            # side and below -2^31 on the negative one. The magnitude stays
            # inside the statement's range (max 2147483639 < 2^31 - 1).
            magnitude = rng.randint(1_000_000_000, 2_147_483_639) // 10 * 10 + rng.randint(3, 9)
            x = magnitude if rng.random() < 0.5 else -magnitude
    elif rng.random() < 0.25:  # hand-checked values that must NOT become 0
        # -2147483412 is here on purpose: it is 236 below the negative bound,
        # and its reversal (-2143847412) is still inside the range, so it pins
        # that the rule reads the REVERSED value and not the input's magnitude.
        x = rng.choice([-2147483412, 1463847412, 1000000001, 1000000000, 120, -120, 0, 7])
    else:  # nine digits or fewer: the reversal cannot leave the range
        x = rng.randint(-999_999_999, 999_999_999)
    return [x], _reverse_integer_oracle(x)


@reference("reverse-integer")
def _reverse_integer_reference(x: int) -> int:
    # The intended digit-by-digit reversal: pop the last digit with % 10 and
    # push it onto the result, once per digit — O(log n) time in the number of
    # digits and O(1) space, with no string allocation. The statement's rule is
    # applied once, at the end, to the value that was actually built: outside
    # [-2^31, 2^31 - 1] the answer is 0. Nothing here needs a 64-bit type the
    # environment is said not to have — the comparison is against the two
    # 32-bit constants, and abs()/sign handling is what keeps the digit loop
    # off negative remainders (Python's % 10 on a negative x would otherwise
    # produce negative digits).
    limit = 2**31 - 1
    sign = -1 if x < 0 else 1
    value = abs(x)
    reversed_value = 0
    while value:
        reversed_value = reversed_value * 10 + value % 10
        value //= 10
    reversed_value *= sign
    if reversed_value > limit or reversed_value < -limit - 1:
        return 0
    return reversed_value
