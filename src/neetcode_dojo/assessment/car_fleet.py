"""QUARANTINED assessment for `car_fleet` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("car_fleet")
def _car_fleet_oracle(target: int, position: list[int], speed: list[int]) -> int:
    cars = sorted(zip(position, speed), reverse=True)
    fleets = 0
    slowest = -1.0
    for pos, spd in cars:
        arrival = (target - pos) / spd
        if arrival > slowest:
            fleets += 1
            slowest = arrival
    return fleets


@cases("car_fleet")
def _car_fleet_case(n: int, rng: random.Random) -> tuple[list, int]:
    n = max(1, min(n, 8))
    target = 10 + rng.randint(1, 20)
    position = rng.sample(range(target), n)
    speed = [rng.randint(1, 10) for _ in range(n)]
    return [target, position, speed], _car_fleet_oracle(target, position, speed)


@inputs("car_fleet")
def _car_fleet_profiler(n: int, rng: random.Random) -> list:
    target = 2 * n
    position = list(range(n))
    speed = [rng.randint(1, 100) for _ in range(n)]
    return [target, position, speed]


@reference("car_fleet")
def car_fleet(target: int, position: list[int], speed: list[int]) -> int:
    cars = sorted(zip(position, speed), reverse=True)
    fleets = 0
    slowest = -1.0
    for pos, spd in cars:
        arrival = (target - pos) / spd
        if arrival > slowest:
            fleets += 1
            slowest = arrival
    return fleets


@measure("car_fleet")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
