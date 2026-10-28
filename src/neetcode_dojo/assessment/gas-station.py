"""QUARANTINED assessment for `gas-station` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


def _gas_station_valid_starts(gas: list[int], cost: list[int]) -> list[int]:
    """Every station the circuit can be completed from, by simulation. The
    generator uses it to check the uniqueness the statement promises before it
    hands a case over; the oracle is the same idea with a first-hit return."""
    n = len(gas)
    starts: list[int] = []
    for start in range(n):
        tank = 0
        for k in range(n):
            i = (start + k) % n
            tank += gas[i] - cost[i]
            if tank < 0:
                break
        else:
            starts.append(start)
    return starts


@oracle("gas-station")
def _gas_station_oracle(gas: list[int], cost: list[int]) -> int:
    """Brute force: try every station and drive the whole circuit from it,
    abandoning a start the moment the tank goes negative. The first station that
    completes the loop is the answer, else -1.

    With the statement's uniqueness guarantee that first hit *is* the answer, but
    the oracle assumes nothing: on an input with two valid stations it answers
    with the lowest index, which is also what the canonical greedy answers there
    (checked exhaustively over small arrays before this fragment was written)."""
    n = len(gas)
    for start in range(n):
        tank = 0
        for k in range(n):
            i = (start + k) % n
            tank += gas[i] - cost[i]
            if tank < 0:
                break
        else:
            return start
    return -1


@cases("gas-station")
def _gas_station_case(n: int, rng: random.Random) -> tuple[list, int]:
    n = max(1, min(n, 12))  # the statement's own constraint: 1 <= n <= 10^5
    # The net profile d[i] = gas[i] - cost[i] is built as a tank-level walk seen
    # from the starting station: levels[0] = 0 at `start`, the levels ahead of it
    # stay positive, and levels[n] is the circuit's total.
    #
    # A station at offset m can finish the circuit exactly when (a) no later
    # level sits below its own, and (b) after the wrap the total still covers
    # every earlier level. With levels[0] = 0 the unique minimum, (b) for m >= 1
    # reduces to `total >= levels[m]`. So:
    #   * total >= 0 and every other level >= 3 -> only offset 0 can finish, i.e.
    #     the answer is unique, which is the statement's "if there exists a
    #     solution, it is guaranteed to be unique" (a non-negative total
    #     guarantees *a* solution but not a unique one, and a strict surplus does
    #     not imply uniqueness either: gas=[0,1]/cost=[0,0] has two valid starts);
    #   * total < 0 -> every circuit ends in deficit, no station finishes, and
    #     the answer is -1, trivially unique.
    # 2 cases in 5 are solvable and 3 in 5 are not: the statement says nothing
    # about the mix, and a generator producing only one kind would leave half the
    # contract untested.
    start = rng.randrange(n)
    solvable = rng.random() < 0.4
    total = rng.randint(0, 2) if solvable else -rng.randint(1, 3)
    levels = [0] + [rng.randint(3, 6) for _ in range(n - 1)] + [total]
    net = [levels[(i - start) % n + 1] - levels[(i - start) % n] for i in range(n)]
    cost = [rng.randint(max(0, -d), max(0, -d) + 4) for d in net]
    gas = [c + d for c, d in zip(cost, net)]
    expected = _gas_station_oracle(gas, cost)
    if expected >= 0 and _gas_station_valid_starts(gas, cost) != [expected]:
        # Verified, not assumed: if the walk ever failed to leave exactly one
        # station able to finish, this generator would ship an input the
        # statement forbids. Fall back to a shape whose uniqueness is by
        # inspection (the whole surplus at the last station, every earlier one
        # empty) rather than trusting the argument above. Two earlier versions of
        # that argument were wrong, which is exactly why it is checked.
        cost = [1] * n
        gas = [0] * (n - 1) + [n + 1]
        expected = _gas_station_oracle(gas, cost)
    return [gas, cost], expected


@inputs("gas-station")
def _gas_station_profiler(n: int, rng: random.Random) -> list:
    # The answer is the LAST station, and every earlier start fails only on the
    # step that would have carried it there.
    #
    # cost[i] = n everywhere; gas ramps at n + 1 (a net gain of +1 per station)
    # and drops to 0 at station n - 2, with the whole surplus parked at station
    # n - 1. Starting at j < n - 1 the tank climbs by one per station and the
    # cliff empties it, so the failure lands exactly on the step before station
    # n - 1 — a per-start simulation is Theta(n^2) here (20.5M steps at n = 6400)
    # and the brute-force oracle cannot early-exit. The canonical greedy still
    # scans all n stations and returns n - 1, which is what makes the answer's
    # position a real test of "did you traverse".
    #
    # Values respect the statement: cost = n and gas <= n + 3 are both inside
    # 0..10^4 for every probe size (the ladder tops out at n = 6400, so cost = n
    # is comfortably legal; a shorter ladder would still work, a longer one would
    # need a different base cost).
    n = max(1, int(n))
    if n == 1:
        return [[4], [1]]  # single station, and it is the last one: 4 >= 1
    cost = [n] * n
    gas = [n + 1] * (n - 2) + [0, n + 3]
    return [gas, cost]


@reference("gas-station")
def _gas_station_reference(gas: list[int], cost: list[int]) -> int:
    """Canonical greedy: total >= 0 decides *whether* a start exists, and the
    start is the station right after the last prefix whose tank went negative —
    one pass, O(1) extra space. A tank that goes negative on the way to i rules
    out every start in [start, i], which is what lets a single scan replace the
    n simulations. The empty input is excluded by n >= 1; the guard keeps the
    reference identical to the oracle (which answers -1) if it ever arrives."""
    if not gas:
        return -1
    total = 0
    tank = 0
    start = 0
    for i in range(len(gas)):
        delta = gas[i] - cost[i]
        total += delta
        tank += delta
        if tank < 0:
            start = i + 1
            tank = 0
    return start if total >= 0 else -1


@measure("gas-station")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
