"""QUARANTINED assessment for `decode-ways` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("decode-ways")
def _decode_ways_oracle(s: str) -> int:
    """Brute force: enumerate every grouping of the string into codes, exactly as
    the statement defines it -- a lone '0' is not a code, and a two-digit code is
    valid only in 10..26. No memo: the recursion IS the definition, and the
    generator's cases (n <= 12) and the probe's input are both cheap for it.
    Total on the empty string (one way: the empty message), which the statement's
    1 <= s.length excludes."""
    n = len(s)

    def ways(i: int) -> int:
        if i == n:
            return 1
        if s[i] == "0":
            return 0
        total = ways(i + 1)
        if i + 1 < n and 10 <= int(s[i : i + 2]) <= 26:
            total += ways(i + 2)
        return total

    return ways(0)


@cases("decode-ways")
def _decode_ways_case(n: int, rng: random.Random) -> tuple[list, int]:
    """The zero shapes are the problem, so all three get their own branch: a
    leading zero (the whole string is undecodable), the "10"/"20" pairs (a valid
    two-digit code carrying a zero), and an internal zero that is only decodable
    through the pair in front of it. `expected` is always the oracle's count."""
    n = max(1, min(n, 12))  # the statement's own floor: 1 <= s.length <= 100
    roll = rng.random()
    if roll < 0.20:
        # a leading zero: position 0 cannot start a code, so the answer is 0
        s = "0" + "".join(rng.choice("0123456789") for _ in range(n - 1))
    elif roll < 0.45:
        # "10"/"20" pairs (and two ordinary pairs so the branch is not only
        # zeros): the two-digit code that carries a zero.
        s = ("".join(rng.choice(("10", "20", "12", "26")) for _ in range(n)))[:n]
    elif roll < 0.70 and n >= 2:
        # an internal zero: only decodable through the pair that ends on it
        digits = [rng.choice("1234567890") for _ in range(n)]
        digits[rng.randrange(1, n)] = "0"
        s = "".join(digits)
    else:
        # no zeros at all, over a small digit alphabet so two-digit codes recur
        s = "".join(rng.choice("123") for _ in range(n))
    return [s], _decode_ways_oracle(s)


@inputs("decode-ways")
def _decode_ways_profiler(n: int, rng: random.Random) -> list:
    # A "10"-pair string. The intended solution's work is one step per character
    # whatever the digits are, so this input buys no timing signal beyond n; what
    # it does buy is the probe's digest check at the largest legal size and the
    # "failed at scale" finding for an exponential recursion that passes every
    # n <= 12 judge case. Deliberately NOT a run of "1"s: that shape has
    # Fibonacci-many decodings (5.7e20 at n = 100), which breaks the statement's
    # own "the answer fits in a 32-bit integer" guarantee AND makes the
    # brute-force oracle itself infeasible at n = 100, where the probe runs both
    # sides (probe_smoke runs the oracle as the student). "10" repeated has
    # exactly one decoding, so the oracle is linear on it and every one of the
    # zero cases the problem is about is exercised.
    n = max(1, n)
    return [("10" * (n // 2 + 1))[:n]]


@reference("decode-ways")
def _decode_ways_reference(s: str) -> int:
    """One left-to-right pass carrying the two previous counts -- the intended
    O(n) time / O(1) space. prev1 is the ways to decode s[:i-1] and prev2 the
    ways to decode s[:i-2]; a single digit contributes prev1 unless it is '0',
    and a two-digit code contributes prev2 when it is 10..26."""
    prev2, prev1 = 1, 1
    for i in range(1, len(s) + 1):
        cur = 0
        if s[i - 1] != "0":
            cur += prev1
        if i >= 2:
            pair = (ord(s[i - 2]) - 48) * 10 + (ord(s[i - 1]) - 48)
            if 10 <= pair <= 26:
                cur += prev2
        prev2, prev1 = prev1, cur
    return prev1


@measure("decode-ways")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
