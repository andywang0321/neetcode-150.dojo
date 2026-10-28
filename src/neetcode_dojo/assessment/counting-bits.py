"""QUARANTINED assessment for `counting-bits` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("counting-bits")
def _counting_bits_oracle(n: int) -> list[int]:
    """Brute force — the statement's own "very easy O(n log n)" baseline: count
    each i's set bits with a shift-and-mask loop (no popcount built-in, which the
    statement forbids) and collect the counts. n < 0 returns [] ; the statement's
    constraint is 0 <= n, so the generator never asks for one."""
    counts = []
    for value in range(max(0, n) + 1):
        bits = 0
        rest = value
        while rest:
            bits += rest & 1
            rest >>= 1
        counts.append(bits)
    return counts


@cases("counting-bits")
def _counting_bits_case(n: int, rng: random.Random) -> tuple[int, list[int]]:
    # The statement's constraint is 0 <= n <= 10^5 on a single scalar, so there
    # is no array shape to randomize: the case size *is* the value. It stays at
    # 0..12 on purpose — one 10^5 case would push ~200 kB of expected, and as
    # much again of got, through the judge's 1 MB stdout budget (proc.OUT_CAP),
    # where a truncated protocol line is reported as a broken run rather than as
    # the size problem it is. 0..12 already covers every branch of the intended
    # DP (0, 1, powers of two, odd and even); scale is the profiler input's job.
    n = max(0, min(n, 12))
    return [n], _counting_bits_oracle(n)


@inputs("counting-bits")
def _counting_bits_profiler(n: int, rng: random.Random) -> list:
    # Here the input *is* the size: the answer holds n + 1 counts, so both sides
    # do O(n) work with no shape to force and no early exit to avoid — a correct
    # solution must emit every entry, and the worst case is the whole array. The
    # probe's ladder (100..6400) sits inside the statement's 0 <= n <= 10^5, so
    # no probe_max_n cap is needed.
    return [n]


@reference("counting-bits")
def _counting_bits_reference(n: int) -> list[int]:
    """Canonical single pass, O(n) time and O(n) space: ans[i] is ans[i >> 1]
    plus i's lowest bit — shifting right drops exactly that one bit — and
    ans[0] = 0 seeds it."""
    counts = [0] * (max(0, n) + 1)
    for i in range(1, len(counts)):
        counts[i] = counts[i >> 1] + (i & 1)
    return counts


@measure("counting-bits")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
