"""QUARANTINED assessment for `coin-change` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("coin-change")
def _coin_change_oracle(coins: list[int], amount: int) -> int:
    # Brute force over the amount line: an amount is a node, a coin is an edge
    # that costs one coin, so a breadth-first sweep reaches every amount with the
    # fewest possible coins and the search order itself is the minimality proof --
    # no exchange argument and no greedy rule is used anywhere. Structurally
    # different from the reference's bottom-up sweep, and total on an empty coin
    # list and on amount 0 (the statement's constraints exclude neither the empty
    # list nor the zero amount, and it excludes a negative amount, which the
    # oracle answers rather than raising).
    if amount <= 0:
        return 0 if amount == 0 else -1
    usable = sorted({coin for coin in coins if coin > 0})
    if not usable:
        return -1
    distance = [-1] * (amount + 1)
    distance[0] = 0
    queue = [0]
    head = 0
    while head < len(queue):
        current = queue[head]
        head += 1
        for coin in usable:
            nxt = current + coin
            if nxt <= amount and distance[nxt] < 0:
                distance[nxt] = distance[current] + 1
                queue.append(nxt)
    return distance[amount]


@cases("coin-change")
def _coin_change_case(n: int, rng: random.Random) -> tuple[list, int]:
    # Four shapes, all inside the statement's constraints (1 <= coins.length <= 12,
    # 1 <= coins[i] <= 2^31 - 1, 0 <= amount <= 10^4). Denominations are drawn with
    # rng.sample, so they stay distinct, which is what the statement means by
    # "coins of different denominations". Amounts stay small (<= 20) so the cases
    # cover many coin sets rather than one large amount.
    n = max(1, min(n, 12))
    mode = n % 4
    amount = rng.randint(0, 12)
    if mode == 0:
        # [1, 3, 4] with an amount two more than a multiple of 4: the classic
        # greedy counterexample (greedy pays 4 + 1 + 1 coins, the optimum is
        # 3 + 3), so a greedy solution fails a generated case and not only the
        # visible one.
        coins = [1, 3, 4]
        amount = 4 * rng.randint(0, 3) + 2
    elif mode == 1:
        # No denomination of 1: unreachable amounts are common (the shape of the
        # statement's example 2), so -1 is exercised rather than assumed away.
        coins = rng.sample(range(2, 10), rng.randint(1, 4))
    elif mode == 2:
        # One denomination far above any generated amount -- the statement allows
        # up to 2^31 - 1 -- which every sweep must skip without indexing below 0.
        coins = sorted(
            {*rng.sample(range(2, 7), rng.randint(1, 2)), rng.choice([10**6, 2**31 - 1])}
        )
    else:
        # A plain draw, including amount = 0 (the statement's example 3 shape).
        coins = rng.sample(range(1, 13), rng.randint(1, 5))
        amount = rng.randint(0, 20)
    return [coins, amount], _coin_change_oracle(coins, amount)


@inputs("coin-change")
def _coin_change_profiler(n: int, rng: random.Random) -> list:
    # Twelve denominations -- the statement's own maximum -- and an amount that
    # grows with the measured size. The intended sweep compares every amount
    # against every denomination, so this is the largest amount-by-coins rectangle
    # the constraints allow, and neither implementation has a value-dependent
    # early exit to take: the loop bound is the amount, not the answer. The
    # denominations are 1..12, so every amount is reachable and the answer is a
    # real coin count rather than -1 (an amount no coin combination reaches would
    # let a student's -1 shortcut look correct at scale). Values stay far inside
    # the 2^31 - 1 bound, and the amount stays inside the statement's 10^4.
    amount = max(1, min(int(n), 10_000))
    return [list(range(1, 13)), amount]


@reference("coin-change")
def _coin_change_reference(coins: list[int], amount: int) -> int:
    # The canonical bottom-up DP: best[v] is the fewest coins that make v, filled
    # in increasing v order so that best[v - coin] is already final when it is
    # read. O(amount * len(coins)) time and O(amount) space, and deliberately
    # iterative -- the same recurrence written top-down would recurse once per
    # coin subtracted, i.e. up to `amount` frames deep (10^4 at the statement's
    # bound), which Python's default stack does not survive. The sentinel is
    # amount + 1, one more than any real answer (all-ones is the worst case), so
    # an unreachable amount stays distinguishable from a reachable one.
    if amount <= 0:
        return 0 if amount == 0 else -1
    unreachable = amount + 1
    best = [0] + [unreachable] * amount
    for value in range(1, amount + 1):
        for coin in coins:
            if 0 < coin <= value and best[value - coin] + 1 < best[value]:
                best[value] = best[value - coin] + 1
    return -1 if best[amount] >= unreachable else best[amount]


@measure("coin-change")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
