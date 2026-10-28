"""QUARANTINED assessment for `plus-one` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, oracle, reference


@oracle("plus-one")
def _plus_one_oracle(digits: list[int]) -> list[int]:
    """Brute force: read the array as an arbitrary-precision integer, add one,
    and write the decimal back out. There is no carry logic here at all, so it
    cannot share a bug with the in-place ripple the reference walks."""
    if not digits:
        return []  # not a legal input (length >= 1); kept total so it cannot raise
    value = int("".join(str(digit) for digit in digits)) + 1
    return [int(character) for character in str(value)]


@cases("plus-one")
def _plus_one_case(n: int, rng: random.Random) -> tuple[list, list]:
    # The carry is the problem, so it is generated on purpose instead of being
    # left to chance: about a third of the cases are all nines (the carry crosses
    # the whole array and the answer gains a digit) and the rest end in a run of
    # nines after a non-zero leading digit. size is the statement's own bound
    # clamped to the caller's 0..12, the digits are 0..9, and the leading digit
    # is never 0, so no case violates a stated constraint (see notes on [0]).
    size = max(1, min(n, 12))  # the statement's 1 <= digits.length <= 100
    if rng.random() < 0.34:
        digits = [9] * size
    else:
        run = rng.randint(0, size - 1)  # size >= 1, so the leading digit stays outside the run
        middle = [rng.randint(0, 9) for _ in range(size - 1 - run)]
        digits = [rng.randint(1, 9)] + middle + [9] * run
    return [digits], _plus_one_oracle(digits)


@reference("plus-one")
def _plus_one_reference(digits: list[int]) -> list[int]:
    """Canonical O(n) time / O(1) space: walk from the least significant digit,
    turn every trailing 9 into 0 and stop at the first digit below 9; if the
    carry survived the whole array (all nines) the answer is one digit longer."""
    out = list(digits)
    if not out:
        return []  # not a legal input; total, and the oracle agrees on it
    for i in range(len(out) - 1, -1, -1):
        if out[i] < 9:
            out[i] += 1
            return out
        out[i] = 0
    return [1] + out
