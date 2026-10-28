"""QUARANTINED assessment for `single-number` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("single-number")
def _single_number_oracle(nums: list[int]) -> int | None:
    """Brute force: for each value, count its occurrences in the whole array and
    return the first with an odd count — under the statement's "every element
    appears twice except for one" that value is unique. None for an empty array,
    which the statement's constraint (length >= 1) never asks for."""
    for value in nums:
        if sum(1 for other in nums if other == value) % 2:
            return value
    return None


@cases("single-number")
def _single_number_case(n: int, rng: random.Random) -> tuple[list, int | None]:
    # The statement's constraints: the array is non-empty and every element
    # appears exactly twice except one, so its length is odd and exactly one
    # value is unpaired. Values are distinct draws inside [-3 * 10^4, 3 * 10^4].
    n = max(1, min(n, 12))
    if n % 2 == 0:
        n -= 1
    pool = rng.sample(range(-30_000, 30_001), n // 2 + 1)
    nums = [pool[0]]
    for value in pool[1:]:
        nums += [value, value]
    rng.shuffle(nums)
    return [nums], _single_number_oracle(nums)


@inputs("single-number")
def _single_number_profiler(n: int, rng: random.Random) -> list:
    # n is the array length, and the statement's shape forces an odd length
    # (pairs plus one single), so an even ladder size is trimmed by one — 6399 at
    # the probe's top size, inside the statement's 3 * 10^4. Values are 0..n // 2,
    # inside [-3 * 10^4, 3 * 10^4], and the two copies of each value sit half the
    # array apart. Both implementations must read every element (the XOR scan and
    # the counting oracle), so there is no early exit to take.
    size = max(1, n if n % 2 else n - 1)
    pairs = size // 2
    return [list(range(pairs)) * 2 + [pairs]]


@reference("single-number")
def _single_number_reference(nums: list[int]) -> int:
    """Canonical O(n)/O(1): XOR the whole array — every paired value cancels
    (x ^ x == 0) and the unpaired one survives (0 ^ x == x)."""
    result = 0
    for value in nums:
        result ^= value
    return result


@measure("single-number")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
