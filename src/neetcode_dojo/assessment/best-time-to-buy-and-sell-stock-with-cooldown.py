"""QUARANTINED assessment for `best-time-to-buy-and-sell-stock-with-cooldown` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("best-time-to-buy-and-sell-stock-with-cooldown")
def _best_time_to_buy_and_sell_stock_with_cooldown_oracle(prices: list[int]) -> int:
    # Brute force over transaction *sets*, which is the statement's own
    # definition: any number of transactions, never two at once, and one day of
    # cooldown after every sale. best[i] is the most profit obtainable from day
    # i onward when day i is free to buy -- either day i goes unused, or a
    # transaction opens on day i and sells on some later day j, after which the
    # next buy cannot come before j + 2. Every valid set of transactions is
    # enumerated by that recurrence, so nothing is assumed about which rises are
    # worth taking.
    #
    # The recurrence is evaluated from the last day backwards rather than as a
    # memoized recursion: the same search either way, but a recursive walk is
    # n frames deep, and the probe's own profiler input is 5000 days long
    # (`data/curation/offline/probe_smoke.py` runs the oracle at the ladder's
    # sizes, where a RecursionError would be reported as a broken oracle).
    # O(n^2) time, O(n) space, and it shares no state with the reference's
    # three-number machine. Total on the empty list (0), on a single day (0),
    # and on prices outside the statement's range -- nothing here requires them
    # to be non-negative.
    n = len(prices)
    best = [0] * (n + 2)
    for i in range(n - 1, -1, -1):
        top = best[i + 1]
        buy = prices[i]
        for sell in range(i + 1, n):
            candidate = prices[sell] - buy + best[sell + 2]
            if candidate > top:
                top = candidate
        best[i] = top
    return best[0]


@cases("best-time-to-buy-and-sell-stock-with-cooldown")
def _best_time_to_buy_and_sell_stock_with_cooldown_case(n: int, rng: random.Random) -> tuple[list, int]:
    # Four shapes, all inside the statement's constraints (1 <= prices.length,
    # 0 <= prices[i] <= 1000). Two of them answer 0 by construction and are 25%
    # of the draws each, so half of the generated cases are the answer-0
    # families:
    #   * flat -- every price equal, so every transaction nets exactly 0;
    #   * strictly decreasing -- rng.sample keeps the values distinct and the
    #     sort makes "strictly" literal, so no buy/sell pair is profitable;
    #   * sawtooth -- low, high, low, high: every rise is worth taking and the
    #     forced day off decides which of them fit together;
    #   * a plain draw over the whole value range.
    # expected always comes from the oracle.
    n = max(1, min(n, 12))
    mode = n % 4
    if mode == 0:
        prices = [rng.randint(0, 1000)] * n
    elif mode == 1:
        prices = sorted(rng.sample(range(1001), n), reverse=True)
    elif mode == 2:
        prices = []
        while len(prices) < n:
            low = rng.randint(0, 500)
            prices.append(low)
            if len(prices) < n:
                prices.append(low + rng.randint(1, 500))
    else:
        prices = [rng.randint(0, 1000) for _ in range(n)]
    return [prices], _best_time_to_buy_and_sell_stock_with_cooldown_oracle(prices)


@inputs("best-time-to-buy-and-sell-stock-with-cooldown")
def _best_time_to_buy_and_sell_stock_with_cooldown_profiler(n: int, rng: random.Random) -> list:
    # Every day is a turning point: the price alternates between the two ends of
    # the statement's own range (0 <= prices[i] <= 1000), so no implementation
    # can skip a day and the state machine's three transitions all fire on every
    # step. The length stops at the statement's 5000, which is what probe_max_n
    # records -- the default ladder would measure 6400 and generate an input the
    # statement does not allow.
    n = max(1, min(n, 5000))
    return [[1000 if i % 2 == 0 else 0 for i in range(n)]]


@reference("best-time-to-buy-and-sell-stock-with-cooldown")
def _best_time_to_buy_and_sell_stock_with_cooldown_reference(prices: list[int]) -> int:
    # The canonical state machine, one pass and three numbers: `hold` is the
    # best balance while holding a share, `sold` the best balance having sold
    # *today* (so tomorrow is a forced cooldown), `rest` the best balance that
    # is free to buy tomorrow. A buy may only follow `rest` and a sale may only
    # follow `hold`; a day's `rest` is carried over either from yesterday's
    # `rest` or from yesterday's `sold`, and that carry is the one-day cooldown.
    # O(n) time, O(1) space.
    #
    # The sentinel is an int far below any reachable balance (prices are >= 0, so
    # holding costs at most the largest price), never -inf, so every value stays
    # an int and an empty list answers 0 through `rest` alone.
    dead = -(1 << 60)
    hold, sold, rest = dead, dead, 0
    for price in prices:
        hold, sold, rest = max(hold, rest - price), hold + price, max(rest, sold)
    return max(sold, rest)


@measure("best-time-to-buy-and-sell-stock-with-cooldown")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
