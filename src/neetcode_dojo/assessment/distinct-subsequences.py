"""QUARANTINED assessment for `distinct-subsequences` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("distinct-subsequences")
def _distinct_subsequences_oracle(s: str, t: str) -> int:
    # The statement's definition walked directly: at each position of s either
    # SKIP it, or -- when it equals t's next character -- USE it and advance both
    # strings, and the number of ways is the sum of those two branches. The memo
    # only stops the same (i, j) pair from being solved twice; without it this is
    # 2^m, the honest brute force, which cannot finish at the generator's sizes.
    # A different program from the reference's one-row sweep: top-down, recursive,
    # no array, counting branches rather than accumulating table cells. Total on
    # the empty strings, which the statement's 1 <= length excludes but which the
    # reference answers identically: an empty t has exactly one subsequence (the
    # empty one) and a non-empty t cannot be formed from an empty s. The recursion
    # is |s| deep, which is why the profiler input stops at |s| = 800.
    memo: dict[tuple[int, int], int] = {}

    def solve(i: int, j: int) -> int:
        if j == len(t):
            return 1
        if i == len(s):
            return 0
        key = (i, j)
        if key in memo:
            return memo[key]
        total = solve(i + 1, j)
        if s[i] == t[j]:
            total += solve(i + 1, j + 1)
        memo[key] = total
        return total

    return solve(0, 0)


@cases("distinct-subsequences")
def _distinct_subsequences_case(n: int, rng: random.Random) -> tuple[list, int]:
    # Sizes are the statement's own (1 <= |s|, |t| <= 1000) clamped to the 1..12
    # the caller's 0..12 allows -- and 12 is exactly what keeps the statement's
    # OTHER constraint true, "the answer fits on a 32-bit signed integer": the
    # count of embeddings is at most the number of subsequences of s, 2^12 = 4096.
    # Four shapes: t longer than s (0), t equal to s (1), a two-letter draw (many
    # embeddings), and s = t followed by extra characters. Expected values come
    # from the oracle in every case.
    n = max(1, min(n, 12))
    mode = n % 4
    if mode == 1:
        shorter = max(1, n - rng.randint(1, 3))
        s = "".join(rng.choice("ab") for _ in range(shorter))
        t = "".join(rng.choice("ab") for _ in range(max(shorter + 1, n)))
    elif mode == 2:
        s = "".join(rng.choice("abc") for _ in range(n))
        t = s
    elif mode == 3:
        s = "".join(rng.choice("ab") for _ in range(n))
        t = "".join(rng.choice("ab") for _ in range(rng.randint(1, n)))
    else:
        keep = rng.randint(1, n)
        t = "".join(rng.choice("ab") for _ in range(keep))
        noise = "".join(rng.choice("ab") for _ in range(n - keep))
        s = t + noise
    return [s, t], _distinct_subsequences_oracle(s, t)


@inputs("distinct-subsequences")
def _distinct_subsequences_profiler(n: int, rng: random.Random) -> list:
    # |s| + |t| ~ n, both inside the statement's 1..1000, and -- the constraint
    # that decides this input's whole shape -- the answer is a COUNT THE STATEMENT
    # GUARANTEES FITS IN A 32-BIT SIGNED INTEGER. An s of a few hundred characters
    # over a small alphabet with |t| ~ |s| / 2 has a count with hundreds of
    # digits, which would make a correct solution's additions bignum-slow and
    # measure it as superlinear (the v0.12 value-range lesson), so the input is
    # built from two independent parts instead:
    #
    #   * a core, t_core = "ab" * p and s_core = "ab" * (2p): the number of ways
    #     to embed ("ab")^p into ("ab")^(2p) is exactly C(3p, p) -- verified
    #     against math.comb for every p this generator can emit -- so the answer
    #     is a large number on purpose (1,251,677,700 at p = 12, the biggest this
    #     construction reaches while staying under 2^31 - 1). Big counts are the
    #     point: they make the DP add real numbers instead of 0s and 1s.
    #   * a tail over letters disjoint from {a, b}, written into s with a 'c'
    #     between every pair of its characters. The projection of that part of s
    #     onto the tail's alphabet IS the tail, so the tail has exactly one
    #     embedding and multiplies the core's count by 1 -- it is what carries
    #     |t| toward the statement's 1000 without changing or inflating the
    #     answer, and it keeps the input away from the degenerate s == t shape.
    #
    # Nothing can early-exit: the count is never 0 (a 0 would let a "t is not a
    # subsequence of s" shortcut answer before any DP runs), t is never longer
    # than s, and both sides fill the whole |s| * |t| table. probe_max_n = 1200
    # keeps |s| <= 800, the largest s the oracle's |s|-deep recursion can walk
    # inside Python's default limit; at the statement's own 1000 it would not.
    size = max(2, min(int(n), 1200))
    pairs = max(1, min(12, size // 100))
    tail_length = max(0, (size - 6 * pairs) // 3)
    tail_alphabet = "defghijklmnopqrstuvwxyz"
    tail = "".join(
        tail_alphabet[i % len(tail_alphabet)] for i in range(tail_length)
    )
    core_t = "ab" * pairs
    core_s = "ab" * (2 * pairs)
    s = core_s + ("c" + "c".join(tail) if tail_length else "")
    return [s, core_t + tail]


@reference("distinct-subsequences")
def _distinct_subsequences_reference(s: str, t: str) -> int:
    # The canonical one-row table: dp[j] is the number of ways t[:j] can be formed
    # from the prefix of s seen so far, swept BACKWARDS over j so the entry it
    # reads (dp[j - 1], the "this character of s is used" term) is still the
    # previous row's while the entry it writes keeps the "not used" term. O(m * n)
    # time and O(n) space -- the class the statement's complexity line declares --
    # and dp[0] stays 1, which is what makes the empty t have exactly one
    # subsequence and an empty s unable to supply a non-empty t, matching the
    # oracle on every empty-string case the statement's own lengths exclude.
    n = len(t)
    dp = [0] * (n + 1)
    dp[0] = 1
    for i in range(len(s)):
        for j in range(n, 0, -1):
            if s[i] == t[j - 1]:
                dp[j] += dp[j - 1]
    return dp[n]


@measure("distinct-subsequences")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
