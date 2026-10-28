"""QUARANTINED assessment for `powx-n` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


_POWX_N_BASES = (
    2.0, 2.1, 1.5, 2.5, 3.0, 0.5, 0.75, 1.1,
    -2.0, -2.1, -1.5, -2.5, -3.0, -0.5, -0.75, -1.1,
)


_POWX_N_BASES = (
    2.0, 2.1, 1.5, 2.5, 3.0, 0.5, 0.75, 1.1,
    -2.0, -2.1, -1.5, -2.5, -3.0, -0.5, -0.75, -1.1,
)


@oracle("powx-n")
def _powx_n_oracle(x: float, n: int) -> float:
    """Brute force: x multiplied by itself |n| times - no fast exponentiation -
    and inverted once when the exponent is negative. This is the definition of
    x^n, so the intended binary exponentiation is checked against the slow thing
    it must equal."""
    result = 1.0
    for _ in range(abs(n)):
        result *= x
    return result if n >= 0 else 1.0 / result


@cases("powx-n")
def _powx_n_case(n: int, rng: random.Random) -> tuple[list, float, dict]:
    # The exponent is capped at +-5, well inside the statement's 2^31 - 1, for two
    # reasons. The judge grades a whole case list under one 10-second budget, so
    # a large exponent would turn a merely linear solution into a timeout that
    # hides every other verdict; and the tighter bound keeps every answer in
    # [3.0 ** -5, 3.0 ** 5] = [0.0041, 243] inside the statement's
    # -10^4 <= x^n <= 10^4 while leaving the smallest answer four hundred
    # tolerances away from zero - which is what makes approx:1e-5 safe (notes).
    limit = max(1, min(n, 5))
    x = rng.choice(_POWX_N_BASES)
    exponent = rng.randint(-limit, limit)
    return [x, exponent], _powx_n_oracle(x, exponent), {"compare": "approx:1e-5"}


@inputs("powx-n")
def _powx_n_profiler(n: int, rng: random.Random) -> list:
    # The measured size is the EXPONENT, not an array: x = 0.5 with exponent
    # k = max(0, min(n, 1000)) makes a repeated-multiplication solution pay k
    # float multiplies while the intended binary exponentiation pays about
    # log2(k) squarings, so the paired ratio separates the two classes instead of
    # measuring noise. Positive k only: 0.5 ** -k is 2 ** k, which leaves the
    # statement's |x^n| <= 10^4 bound as soon as k is large.
    #
    # 0.5 rather than a base near 1 (1 + 1e-7 would allow a much larger exponent
    # inside that bound): every partial product is an exact power of two, so a
    # repeated-multiplication student and this squaring reference return
    # bit-identical floats at every size, and the probe's exact digest comparison
    # cannot report a correct student as disagreeing with the reference. With a
    # base near 1 the two shapes differ in the last bits and a correct answer
    # would be blamed for it. probe_max_n = 1000 keeps the answer a normal double
    # (2 ** -1000 is about 9.3e-302, far above the smallest subnormal) instead of
    # underflowing to 0.0 at the default 6400, and the exponent stays inside the
    # statement's 2^31 - 1 with room to spare.
    return [0.5, max(0, min(n, 1000))]


@reference("powx-n")
def _powx_n_reference(x: float, n: int) -> float:
    """Canonical binary exponentiation, iteratively: square the base and halve
    the exponent, multiplying into the accumulator for every set bit, then invert
    once when the exponent is negative - O(log|n|) time, O(1) space, and no
    recursion for the statement's 2^31 - 1 ceiling to blow up."""
    exponent = abs(n)
    base = x
    result = 1.0
    while exponent:
        if exponent & 1:
            result *= base
        base *= base
        exponent >>= 1
    return result if n >= 0 else 1.0 / result


@measure("powx-n")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
