"""QUARANTINED assessment for `best-time-to-buy-and-sell-stock` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("best-time-to-buy-and-sell-stock")
def _best_time_to_buy_and_sell_stock_oracle(prices: list[int]) -> int:
    best = 0
    for i in range(len(prices)):
        for j in range(i + 1, len(prices)):
            best = max(best, prices[j] - prices[i])
    return best


@cases("best-time-to-buy-and-sell-stock")
def _best_time_to_buy_and_sell_stock_case(n: int, rng: random.Random) -> tuple[list, int]:
    n = max(1, min(n, 12))  # the statement's own constraint: length >= 1
    prices = [rng.randint(0, 20) for _ in range(n)]
    return [prices], _best_time_to_buy_and_sell_stock_oracle(prices)


@inputs("best-time-to-buy-and-sell-stock")
def _best_time_to_buy_and_sell_stock_profiler(n: int, rng: random.Random) -> list:
    # Strictly decreasing, inside the statement's value range: the running minimum
    # updates on every step (nothing to early-exit on for either implementation)
    # and no profitable pair exists, so the answer is 0 without a scan stopping
    # early on a lucky buy.
    return [[max(1, 10_000 - i) for i in range(n)]]


@reference("best-time-to-buy-and-sell-stock")
def _best_time_to_buy_and_sell_stock_reference(prices: list[int]) -> int:
    best = 0
    low = None
    for price in prices:
        if low is None or price < low:
            low = price
        else:
            best = max(best, price - low)
    return best


@measure("best-time-to-buy-and-sell-stock")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
