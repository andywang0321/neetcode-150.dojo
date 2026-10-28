"""QUARANTINED assessment for `daily_temperatures` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("daily_temperatures")
def _daily_temperatures_oracle(temperatures: list[int]) -> list[int]:
    out: list[int] = []
    for i, t in enumerate(temperatures):
        wait = 0
        for j in range(i + 1, len(temperatures)):
            if temperatures[j] > t:
                wait = j - i
                break
        out.append(wait)
    return out


@cases("daily_temperatures")
def _daily_temperatures_case(n: int, rng: random.Random) -> tuple[list, list]:
    n = max(0, min(n, 12))
    temperatures = [rng.randint(0, 50) for _ in range(n)]
    return [temperatures], _daily_temperatures_oracle(temperatures)


@inputs("daily_temperatures")
def _daily_temperatures_profiler(n: int, rng: random.Random) -> list:
    return [list(range(1000, 1000 - n, -1))]  # strictly cooling: stack drains at the end


@reference("daily_temperatures")
def daily_temperatures(temperatures: list[int]) -> list[int]:
    n = len(temperatures)
    result = [0] * n
    stack: list[int] = []
    for i, t in enumerate(temperatures):
        while stack and temperatures[stack[-1]] < t:
            j = stack.pop()
            result[j] = i - j
        stack.append(i)
    return result


@measure("daily_temperatures")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
