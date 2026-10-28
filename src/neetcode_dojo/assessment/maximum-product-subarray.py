"""QUARANTINED assessment for `maximum-product-subarray` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("maximum-product-subarray")
def _maximum_product_subarray_oracle(nums: list[int]) -> int:
    # Brute force: every subarray's product, built by extending the right end one
    # element at a time from each start, so no reasoning about signs, zeros or a
    # best-so-far is involved anywhere -- O(n^2) multiplications and obviously
    # correct, and a genuinely different program from the reference's single pass.
    # Total on the empty list, which has no subarray to pick: both sides answer 0
    # there (the statement's length >= 1 excludes that input).
    best = None
    for start in range(len(nums)):
        product = 1
        for end in range(start, len(nums)):
            product *= nums[end]
            if best is None or product > best:
                best = product
    return 0 if best is None else best


@cases("maximum-product-subarray")
def _maximum_product_subarray_case(n: int, rng: random.Random) -> tuple[list, int]:
    # The statement states the value range [-10, 10] AND promises that the product
    # of any subarray fits in a 32-bit integer. At n = 12 a magnitude of 10 would
    # reach 10^12, so the magnitudes are capped at the largest power that keeps the
    # second promise (10 up to n = 9, 5 at n = 12) while every value stays inside
    # the stated range. The cap never exceeds the statement's own 10, so the loop
    # is bounded by that rather than by the 32-bit arithmetic (at n = 1 the
    # inequality alone would run 2^31 times). Zeros and pairs of negatives are
    # forced by the modes below, because those two shapes are what make the DP
    # non-obvious: without them a running product is indistinguishable from the
    # intended solution.
    n = max(1, min(n, 12))
    cap = 2
    while cap < 10 and (cap + 1) ** n <= 2**31 - 1:
        cap += 1
    mode = n % 4
    if mode == 0:
        # No zero, an even number of negatives, every magnitude >= 2: the answer
        # is the product of the whole array, which a single running product
        # (restarted or not when it goes negative) cannot find.
        values = [rng.choice([-1, 1]) * rng.randint(2, cap) for _ in range(n)]
        if sum(1 for value in values if value < 0) % 2:
            index = rng.randrange(n)
            values[index] = -values[index]
    elif mode == 1:
        # Exactly one zero, placed anywhere: the array splits into two parts and
        # the best product has to be found without crossing it (the statement's
        # example 2 is this shape).
        values = [rng.choice([-1, 1]) * rng.randint(1, cap) for _ in range(n)]
        values[rng.randrange(n)] = 0
    elif mode == 2:
        # Two negatives with positives between them and no zero: the best product
        # spans both negatives, so a pass that tracks only the maximum so far has
        # already thrown away the minimum it needed.
        values = [rng.randint(1, cap) for _ in range(n)]
        values[0] = -rng.randint(2, cap)
        values[-1] = -rng.randint(2, cap)
    else:
        # A plain draw inside [-cap, cap]: zeros and negatives both occur often,
        # so the two shapes above are not the only ones the cases cover.
        values = [rng.randint(-cap, cap) for _ in range(n)]
    return [values], _maximum_product_subarray_oracle(values)


@inputs("maximum-product-subarray")
def _maximum_product_subarray_profiler(n: int, rng: random.Random) -> list:
    # Blocks of [10, -10, 10, 10] separated by a 0. Inside a block the best
    # subarray product is 100 (the two 10s that follow the -10) while the largest
    # running product ever seen is 10, and the zeros stop any product from
    # crossing a block boundary -- so a naive "multiply along, keep the biggest"
    # solution returns 10 and disagrees with the reference at every size of the
    # ladder, which matters because that solution is not slower than the reference
    # (both are one pass): growth cannot catch it, only the output digest can.
    # The whole input is inside the statement's own constraints: values in
    # [-10, 10], and the largest magnitude any subarray reaches is 10^4, far
    # inside the 32-bit promise (no run of many 10s exists to break it).
    size = max(1, int(n))
    pattern = (10, -10, 10, 10, 0)
    return [[pattern[index % 5] for index in range(size)]]


@reference("maximum-product-subarray")
def _maximum_product_subarray_reference(nums: list[int]) -> int:
    # The canonical single pass: high and low are the largest and smallest product
    # of a subarray ENDING at the current position, so a negative value swaps
    # their roles and a zero resets both; best is the largest high ever seen.
    # O(n) time and O(1) space, no array of prefix products -- and the loop walks
    # indices rather than a nums[1:] slice, which would quietly allocate a copy of
    # the array and make the measured space O(n) where the statement asks for
    # O(1). The simultaneous assignment evaluates its right-hand side with both
    # old values, which is what makes the swap correct. Total on the empty list,
    # matching the oracle's 0 (the statement's length >= 1 excludes it).
    if not nums:
        return 0
    best = high = low = nums[0]
    for index in range(1, len(nums)):
        value = nums[index]
        high, low = max(value, high * value, low * value), min(value, high * value, low * value)
        if high > best:
            best = high
    return best


@measure("maximum-product-subarray")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
