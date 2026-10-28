"""QUARANTINED assessment for `correlation` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("correlation")
def _correlation_oracle(X: list, Y: list) -> float:
    n = len(X)
    ex = sum(X) / n
    ey = sum(Y) / n
    exy = sum(x * y for x, y in zip(X, Y)) / n
    exx = sum(x * x for x in X) / n
    eyy = sum(y * y for y in Y) / n
    return round((exy - ex * ey) / (((exx - ex**2) * (eyy - ey**2)) ** 0.5), 4)


@cases("correlation")
def _correlation_case(n: int, rng: random.Random) -> tuple[list, float, dict]:
    n = max(2, min(n, 12))
    X = [rng.randint(1, 20) for _ in range(n)]
    slope = rng.randint(-5, 5)
    intercept = rng.randint(-10, 10)
    Y = [slope * x + intercept + rng.randint(-5, 5) for x in X]
    if len(set(X)) == 1:
        X[0] += 1  # zero variance makes correlation undefined
    if len(set(Y)) == 1:
        Y[0] += 1
    return [X, Y], _correlation_oracle(X, Y), {"compare": "approx:0.0001"}


@inputs("correlation")
def _correlation_profiler(n: int, rng: random.Random) -> list:
    X = list(range(n))
    Y = [x + rng.randint(-10, 10) for x in X]
    return [X, Y]


@reference("correlation")
def correlation(X: list, Y: list) -> float:
    n = len(X)
    sx = sy = sxy = sxx = syy = 0.0
    for x, y in zip(X, Y):
        sx += x
        sy += y
        sxy += x * y
        sxx += x * x
        syy += y * y
    ex = sx / n
    ey = sy / n
    exy = sxy / n
    exx = sxx / n
    eyy = syy / n
    return round((exy - ex * ey) / (((exx - ex * ex) * (eyy - ey * ey)) ** 0.5), 4)


@measure("correlation")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
