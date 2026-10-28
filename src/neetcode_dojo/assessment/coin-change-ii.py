"""QUARANTINED assessment for `coin-change-ii` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("coin-change-ii")
def _coin_change_ii_oracle(amount: int, coins: list[int]) -> int:
    # Brute force over the combination space as the statement defines it: a
    # combination is a multiset of coins, so a multiset is fixed by how many of
    # each denomination it takes. The walk decides one denomination at a time --
    # "none of these coins at all" or "at least one, and this denomination is
    # still available" -- so every multiset is enumerated exactly once. That
    # index order is what makes the count a count of combinations and not of
    # permutations: 1 + 2 and 2 + 1 are the same multiset, and only the branch
    # that has not decided a denomination yet can produce it again. The memo on
    # (denomination, remaining) keeps the walk finite without changing what is
    # enumerated. Total on amount 0 (the empty combination), on a negative
    # amount (0), and on an empty or non-positive coin list (0).
    #
    # Depth is (denominations) + (amount // smallest coin) frames: the profiler
    # input's denominations are all >= amount / 2 and the generator's amounts are
    # <= 24, so the deepest walk this fragment can produce is ~300 frames. A
    # profiler input with a denomination of 1 at amount 5000 would not fit
    # Python's default stack, so keep that in mind if the two are ever changed
    # together.
    if amount < 0:
        return 0
    usable = [coin for coin in coins if coin > 0]
    memo: dict[tuple[int, int], int] = {}

    def ways(i: int, remaining: int) -> int:
        if remaining == 0:
            return 1
        if remaining < 0 or i == len(usable):
            return 0
        key = (i, remaining)
        if key in memo:
            return memo[key]
        count = ways(i + 1, remaining) + ways(i, remaining - usable[i])
        memo[key] = count
        return count

    return ways(0, amount)


@cases("coin-change-ii")
def _coin_change_ii_case(n: int, rng: random.Random) -> tuple[list, int]:
    # Four shapes, all inside the statement's constraints (1 <= coins.length,
    # 1 <= coins[i] <= 5000, denominations distinct, 0 <= amount <= 5000); n is
    # the number of denominations and the amounts stay small so the cases cover
    # many coin sets instead of a few large ones. Two of the four are the
    # families where a wrong-but-plausible number is the likely failure:
    #   * amount 0 -- exactly one combination, the empty one, whatever the
    #     denominations are (25% of the draws);
    #   * an amount no combination can make -- every denomination is even and the
    #     amount is odd, so the answer must be 0 (another 25%; the statement's
    #     own example 2 is the other kind of impossibility, every coin larger
    #     than the amount);
    #   * a set containing 1, which makes every amount reachable and the counts
    #     specific;
    #   * a plain draw, where unreachable amounts are common.
    # expected always comes from the oracle.
    n = max(1, min(n, 12))
    mode = n % 4
    if mode == 0:
        amount = 0
        coins = sorted(rng.sample(range(1, 5001), n))
    elif mode == 1:
        amount = 2 * rng.randint(0, 12) + 1
        coins = sorted(2 * coin for coin in rng.sample(range(1, 2501), n))
    elif mode == 2:
        amount = rng.randint(0, 24)
        coins = [1] if n == 1 else [1] + sorted(rng.sample(range(2, 5001), n - 1))
    else:
        amount = rng.randint(0, 24)
        coins = sorted(rng.sample(range(1, 5001), n))
    return [amount, coins], _coin_change_ii_oracle(amount, coins)


@inputs("coin-change-ii")
def _coin_change_ii_profiler(n: int, rng: random.Random) -> list:
    # The DP's work is (denominations) * (amount), so the amount scales with n up
    # to the statement's 5000 (probe_max_n -- the default ladder would measure
    # 6400 and generate an amount the statement forbids) and the denomination
    # count with it up to the statement's 300: both factors of the sweep are
    # exercised, and every coin is <= the amount, so no coin is dead weight in
    # the inner loop.
    #
    # The denominations sit in [amount // 2, amount // 2 + k - 1]. All of them are
    # at least half the amount, so no combination can use three of them and the
    # count stays tiny -- and that matters, because the statement guarantees the
    # answer fits a signed 32-bit integer: the small-denomination set that would
    # maximize the sweep (1, 2, 3, ... 300 with amount 5000) counts the
    # partitions of 5000, a number with about a hundred digits, which no 32-bit
    # answer can be.
    amount = max(1, min(n, 5000))
    k = max(1, min(300, amount // 4))
    start = max(1, amount // 2)
    return [amount, list(range(start, start + k))]


@reference("coin-change-ii")
def _coin_change_ii_reference(amount: int, coins: list[int]) -> int:
    # The canonical one-dimensional DP: ways[v] is the number of combinations
    # that make exactly v. The sweep is denominations OUTER, amounts inner, and
    # that order is the whole problem -- with the loops swapped, ways would count
    # ordered sequences of coins, so 1 + 2 and 2 + 1 would be two of its answers
    # instead of one (example 1 would read 9, not 4). Sweeping the amounts upward
    # leaves each denomination reusable, which is the statement's "infinite
    # number of each kind of coin". O(amount * len(coins)) time, O(amount) space.
    #
    # Total on amount 0 (the empty combination) and on a negative amount (0). A
    # coin <= 0 is skipped: the statement's denominations are >= 1, and skipping
    # keeps this side in step with the oracle off-constraint.
    if amount < 0:
        return 0
    ways = [0] * (amount + 1)
    ways[0] = 1
    for coin in coins:
        if coin <= 0:
            continue
        for value in range(coin, amount + 1):
            ways[value] += ways[value - coin]
    return ways[amount]


@measure("coin-change-ii")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
