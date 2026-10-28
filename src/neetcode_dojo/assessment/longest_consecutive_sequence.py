"""QUARANTINED assessment for `longest_consecutive_sequence` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("longest_consecutive_sequence")
def _longest_seqlen_oracle(nums: list[int]) -> int:
    num_set = set(nums)
    longest = 0
    for num in num_set:
        if num - 1 not in num_set:
            length = 1
            while num + length in num_set:
                length += 1
            longest = max(longest, length)
    return longest


@cases("longest_consecutive_sequence")
def _longest_seqlen_case(n: int, rng: random.Random) -> tuple[list, int]:
    n = max(0, min(n, 12))
    nums = [rng.randint(-10, 10) for _ in range(n)]
    return [nums], _longest_seqlen_oracle(nums)


@inputs("longest_consecutive_sequence")
def _longest_seqlen_profiler(n: int, rng: random.Random) -> list:
    values = list(range(n))
    rng.shuffle(values)
    return [values]


@reference("longest_consecutive_sequence")
def longest_seqlen(nums: list[int]) -> int:
    num_set = set(nums)
    longest = 0
    for num in num_set:
        if num - 1 not in num_set:
            length = 1
            while num + length in num_set:
                length += 1
            if length > longest:
                longest = length
    return longest


@measure("longest_consecutive_sequence")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
