"""QUARANTINED assessment for `koko-eating-bananas` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("koko-eating-bananas")
def _koko_eating_bananas_oracle(piles: list[int], h: int) -> int:
    # Brute force: try every speed from 1 upwards and answer with the first one
    # that fits in h hours. The `hours > h` break only skips the rest of a sum
    # that has already failed, so it cannot change the answer; without it this
    # loop would be hopeless on the profiler input, where the answer is 2000.
    if not piles:
        return 1  # unreachable under the statement's constraints (length >= 1)
    for speed in range(1, max(piles) + 1):
        hours = 0
        for pile in piles:
            hours += -(-pile // speed)  # ceil(pile / speed), in integers
            if hours > h:
                break
        if hours <= h:
            return speed
    # Unreachable while h >= len(piles): speed = max(piles) costs exactly
    # len(piles) hours, which the statement's `piles.length <= h` allows.
    return max(piles)


@cases("koko-eating-bananas")
def _koko_eating_bananas_case(n: int, rng: random.Random) -> tuple[list, int]:
    n = max(1, min(n, 12))  # the statement's floor: piles.length >= 1
    piles = [rng.randint(1, 20) for _ in range(n)]
    # piles.length <= h is the statement's own floor, and h == n is the tightest
    # legal case there is (every pile eaten in exactly one hour, answer = the
    # largest pile) — it is included on purpose, not by accident.
    h = rng.randint(n, n + 6)
    return [piles, h], _koko_eating_bananas_oracle(piles, h)


@inputs("koko-eating-bananas")
def _koko_eating_bananas_profiler(n: int, rng: random.Random) -> list:
    """n piles whose VALUES scale with n (n .. n + n/4), h = 5n, so the answer
    (n/4) is strictly inside [1, max(piles)] and the reference's binary search
    takes its full round count while every round scans all n piles.

    The values scale with n on purpose: with piles fixed near 10^4 the naive
    "try every speed from 1 to max(piles)" scan is linear IN n (its cost is
    n * max(piles), and max(piles) never grew), so it measured as "matches" with
    a ~100x constant factor — the batch verifier's finding, reproduced with the
    real probe. Scaling the values makes that wrong-class solution report
    WORSE (the Measured column prints "unresolved" because the declared O(n log m) is not a class the probe can name; the trend, 15-44x, carries the signal), while the
    brute-force oracle stays affordable (0.007 s at n=800, 0.509 s at n=6400) and
    every value stays inside 1 <= piles[i] <= 10^9."""
    n = max(2, min(n, 10_000))
    half = max(1, n // 2)
    piles = [n + (i % half) // 2 for i in range(n)]
    return [piles, 5 * n]


@reference("koko-eating-bananas")
def _koko_eating_bananas_reference(piles: list[int], h: int) -> int:
    if not piles:
        return 1  # unreachable under the statement's constraints (length >= 1)

    def hours_for(speed: int) -> int:
        total = 0
        for pile in piles:
            total += -(-pile // speed)  # ceil(pile / speed), in integers
        return total

    # Feasibility is monotone in the speed (a bigger speed never costs more
    # hours) and speed = max(piles) always fits, because the statement promises
    # piles.length <= h. So binary search the smallest feasible speed, scanning
    # every pile on every probe — nothing here exits early.
    lo, hi = 1, max(piles)
    while lo < hi:
        mid = (lo + hi) // 2
        if hours_for(mid) <= h:
            hi = mid
        else:
            lo = mid + 1
    return lo


@measure("koko-eating-bananas")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
