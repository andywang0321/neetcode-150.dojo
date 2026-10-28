"""QUARANTINED assessment for `happy-number` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


def _happy_number_next(value: int) -> int:
    """The sum of the squares of the digits of ``value`` - one step of the
    statement's process - by arithmetic rather than str(), so the profiler's
    search below does not allocate a string per step."""
    total = 0
    while value:
        digit = value % 10
        total += digit * digit
        value //= 10
    return total


def _happy_number_chain(value: int) -> tuple[int, bool]:
    """(steps, reached_one) for the chain starting at ``value``: the definition
    run until it reaches 1 or repeats a value. Used ONLY to pick the profiler
    input's worst case - every expected answer comes from the oracle."""
    seen: set[int] = set()
    steps = 0
    while value != 1 and value not in seen:
        seen.add(value)
        value = _happy_number_next(value)
        steps += 1
    return steps, value == 1


@oracle("happy-number")
def _happy_number_oracle(n: int) -> bool:
    """Brute force by the definition, with a different cycle test than the
    reference uses: Floyd's tortoise and hare walks the chain at one and two
    steps per turn, and the two meet exactly when the chain has entered a cycle.
    If the slow and fast pointers meet anywhere other than 1, the cycle cannot
    contain 1, which is the statement's "loops endlessly in a cycle which does
    not include 1". Total for n >= 0 (0 is its own fixed point and is not 1)."""
    slow = n
    fast = _happy_number_next(n)
    while fast != 1 and slow != fast:
        slow = _happy_number_next(slow)
        fast = _happy_number_next(_happy_number_next(fast))
    return fast == 1


@cases("happy-number")
def _happy_number_case(n: int, rng: random.Random) -> tuple[list, bool]:
    # This statement's parameter is a VALUE (1 <= n <= 2^31 - 1), not a size, so
    # the caller's 0..12 is read as a digit budget: 1..10 digits, ten being the
    # most 2^31 - 1 has. Values are drawn from the whole stated range, and the
    # two short lists make sure both verdicts appear at every call.
    digits = max(1, min(n, 10))
    low = 10 ** (digits - 1)
    high = min(10**digits - 1, 2**31 - 1)
    draw = rng.random()
    if draw < 0.2:
        value = rng.choice([1, 7, 10, 19, 100, 1000])  # happy values
    elif draw < 0.4:
        value = rng.choice([2, 3, 4, 16, 89, 999])  # unhappy values
    else:
        value = rng.randint(low, high)
    return [value], _happy_number_oracle(value)


@inputs("happy-number")
def _happy_number_profiler(n: int, rng: random.Random) -> list:
    # The input is a single VALUE, so "size ~n" means the number itself is about
    # n (100..6400 on the default ladder; the statement's ceiling is 2^31 - 1, so
    # every point is a legal input). The value is the worst case available in
    # [n, n + 128): an unhappy number whose chain is the longest there, so an
    # implementation that only stops at 1 cannot terminate on it and neither side
    # gets a short chain to hide in. Every 32-bit input falls to at most 730
    # after one step and the longest chain below that is 19 more steps, so ~12
    # iterations is the real worst case here, not a size effect - see the notes.
    start = max(1, n)
    best_value, best_score = start, None
    for value in range(start, start + 128):
        steps, reached_one = _happy_number_chain(value)
        score = (0 if reached_one else 1, steps)  # unhappy first, then the longest
        if best_score is None or score > best_score:
            best_value, best_score = value, score
    return [best_value]


@reference("happy-number")
def _happy_number_reference(n: int) -> bool:
    # The intended solution: follow the chain and remember every value seen in a
    # set, which is how the statement's "loops endlessly in a cycle" is detected
    # - the second time a value appears, no new value can ever follow, and if 1
    # has not shown up by then it never will. O(log n) time (each step sums the
    # squares of the value's O(log n) digits, and at most O(log n) distinct
    # values can appear before the chain repeats) and O(log n) space for the
    # seen set. Total for n >= 0.
    seen: set[int] = set()
    while n != 1 and n not in seen:
        seen.add(n)
        total = 0
        for digit in str(n):
            total += int(digit) * int(digit)
        n = total
    return n == 1


@measure("happy-number")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
