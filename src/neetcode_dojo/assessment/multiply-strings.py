"""QUARANTINED assessment for `multiply-strings` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


def _multiply_strings_number(rng: random.Random, length: int) -> str:
    """A number of exactly ``length`` digits with no leading zero (the
    statement's constraint), except that a one-digit draw is '0' itself about a
    fifth of the time - the single number the statement allows to start with a
    zero."""
    if length == 1 and rng.random() < 0.2:
        return '0'
    digits = [rng.choice('123456789')]
    digits += [rng.choice('0123456789') for _ in range(length - 1)]
    return ''.join(digits)


@oracle("multiply-strings")
def _multiply_strings_oracle(num1: str, num2: str) -> str:
    """Brute force, and deliberately NOT a student answer: Python's
    arbitrary-precision integers do the whole job in one expression, so the
    oracle has no digit or carry logic to share a bug with the reference's
    grade-school loop. The statement forbids exactly this route to the student,
    and the judge cannot see how the string was built - the note appended to the
    statement says so in the student's own words."""
    return str(int(num1) * int(num2))


@cases("multiply-strings")
def _multiply_strings_case(n: int, rng: random.Random) -> tuple[list, str]:
    # Both lengths come from [1, size] with size <= 12, so every operand is far
    # inside the statement's 1 <= num1.length, num2.length <= 200, is digits
    # only, and carries no leading zero. A zero operand is produced on purpose
    # (a one-digit draw, or the second operand outright): the statement's
    # zero-product carve-out is a path a generator drawn from 1..9 would never
    # reach, and expected always comes from the oracle.
    size = max(1, min(n, 12))
    num1 = _multiply_strings_number(rng, rng.randint(1, size))
    if rng.random() < 0.08:
        num2 = '0'
    else:
        num2 = _multiply_strings_number(rng, rng.randint(1, size))
    return [num1, num2], _multiply_strings_oracle(num1, num2)


@inputs("multiply-strings")
def _multiply_strings_profiler(n: int, rng: random.Random) -> list:
    # Total size about n, split evenly (equal lengths maximise m * n for a fixed
    # total), all nines: no digit pair is a zero shortcut and every position
    # carries, so the grade-school double loop runs to completion for both the
    # student and the reference. probe_max_n = 400 puts the top of the ladder at
    # 200 digits per operand, exactly the statement's cap; the default ladder
    # would have asked for 3200-digit operands, sixteen times over the stated
    # bound - the value-range mistake the v0.12 lesson is about.
    length = max(1, min(200, n // 2))
    return ['9' * length, '9' * length]


@reference("multiply-strings")
def _multiply_strings_reference(num1: str, num2: str) -> str:
    """Canonical grade-school multiplication, O(m * n) time and O(m + n) space:
    an accumulator of m + n digits (no product of an m-digit and an n-digit
    number is longer), each digit pair multiplied into position i + j + 1 with
    the carry pushed into i + j, and the leading zeros stripped at the end -
    that last step is what turns a 100 * 100 accumulator into '10000' instead of
    '010000', and what makes a zero product come out as '0' rather than '' ."""
    left = [int(character) for character in num1]
    right = [int(character) for character in num2]
    m, n = len(left), len(right)
    accumulator = [0] * (m + n)
    for i in range(m - 1, -1, -1):
        for j in range(n - 1, -1, -1):
            total = left[i] * right[j] + accumulator[i + j + 1]
            accumulator[i + j + 1] = total % 10
            accumulator[i + j] += total // 10
    start = 0
    while start < len(accumulator) - 1 and accumulator[start] == 0:
        start += 1
    return ''.join(str(digit) for digit in accumulator[start:])


@measure("multiply-strings")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
