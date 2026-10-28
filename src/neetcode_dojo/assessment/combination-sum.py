"""QUARANTINED assessment for `combination-sum` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, oracle, reference


def _combination_sum_ways(values: list[int], target: int) -> tuple[int, int]:
    """(combinations summing to target, partial multisets with sum <= target).

    The unbounded-coin-change DP: ``ways[t]`` counts the multisets of values that
    sum to exactly t, counting each multiset once, so ``ways[target]`` is the size
    of the answer and ``sum(ways)`` bounds the nodes the oracle's count-vector
    enumeration visits. Both are used to keep a generated case small and cheap —
    the statement's own guarantee is "less than 150 combinations", and this keeps
    the *work* bounded as well as the answer.
    """
    ways = [0] * (target + 1)
    ways[0] = 1
    for value in values:
        for total in range(value, target + 1):
            ways[total] += ways[total - value]
    return ways[target], sum(ways)


@oracle("combination-sum")
def _combination_sum_oracle(candidates: list[int], target: int) -> list[list[int]]:
    # Brute force over how many times each candidate is used: level i decides the
    # count of candidates[i], every count that still fits the remaining target is
    # tried, and a count vector whose sum lands exactly on the target is one
    # combination. The candidates are distinct (the statement guarantees it and
    # the generator upholds it), so count vector <-> multiset of values is a
    # bijection: every combination is produced exactly once and none is missed.
    # Sorting first makes the output ascending-lexicographic, the canonical form
    # of a set answer (the visible tests carry the statement's example order).
    values = sorted(candidates)
    out: list[list[int]] = []

    def _combination_sum_counts(i: int, remaining: int, picks: list[int]) -> None:
        if i == len(values):
            if remaining == 0:
                out.append(list(picks))
            return
        value = values[i]
        count = 0
        while count * value <= remaining:
            _combination_sum_counts(i + 1, remaining - count * value, picks + [value] * count)
            count += 1

    _combination_sum_counts(0, target, [])
    return sorted(out)


@cases("combination-sum")
def _combination_sum_case(n: int, rng: random.Random) -> tuple[list, list, dict]:
    # The statement's guarantees, upheld exactly: 1 <= len(candidates) <= 30,
    # 2 <= candidates[i] <= 40, "All elements of candidates are distinct",
    # 1 <= target <= 40, and "the number of unique combinations that sum up to
    # target is less than 150" (tightened here to <= 24).
    #
    # Distinctness is load-bearing for the verdict: with a repeated candidate,
    # two different count vectors ("use the first 2 twice" / "use the second 2
    # twice") would produce the same multiset of values, the answer set would
    # stop being a set, and a correct solution returning the other copy would be
    # false-failed. The generator never repeats a value: it builds one value plus
    # a sample of distinct values above it (plus, sometimes, its partner).
    n = max(1, min(n, 12))
    target = rng.randint(1, 40)
    count = max(1, min(n, 8))  # candidates.length grows with n, capped at 8 of 30
    for _ in range(64):
        if target == 1 or (rng.random() < 0.2 and 40 - target >= count):
            # The statement's own Example 3 shape: every candidate is above the
            # target (candidates are >= 2, so target = 1 forces this), no
            # combination exists and the answer is the empty list.
            above = rng.sample(range(max(2, target + 1), 41), count)
            return [above, target], _combination_sum_oracle(above, target), {"compare": "sorted"}
        # Otherwise the small candidate is chosen so that a solution provably
        # exists: usually a *proper* divisor of the target, so repeating it takes
        # at least two steps and the unlimited reuse the statement allows
        # (Example 2's [2,2,2,2]) is genuinely exercised; sometimes the target
        # itself, which is one of Example 1's own combinations (7 = 7); and for a
        # target with no proper divisor at all the target is reached as a
        # two-value sum instead, which keeps a prime target a real case rather
        # than "the target is a candidate". The partner (target - small) is added
        # as a second candidate whenever it is a legal distinct value — it pairs
        # with `small` to make a second combination. The rest are distinct values
        # above `small`.
        proper = [d for d in range(2, target) if target % d == 0]
        if proper and rng.random() < 0.75:
            small = rng.choice(proper)
        elif proper:
            small = target
        else:
            small = rng.randint(2, max(2, target // 2))
        partner = target - small
        rest = rng.sample(range(small + 1, 41), min(count - 1, 40 - small))
        values = [small]
        if 2 <= partner <= 40 and partner != small:
            values.append(partner)
        values += [v for v in rest if v not in values]
        ways, nodes = _combination_sum_ways(values, target)
        if 1 <= ways <= 24 and nodes <= 4_000:
            return [values, target], _combination_sum_oracle(values, target), {"compare": "sorted"}
    # Deterministic fallback if all 64 draws were too large: the target itself is
    # a candidate, so the answer is exactly [[target]] — never empty, never big.
    values = [target] + (
        rng.sample(range(target + 1, 41), min(count - 1, 40 - target)) if target < 40 else []
    )
    return [values, target], _combination_sum_oracle(values, target), {"compare": "sorted"}


@reference("combination-sum")
def _combination_sum_reference(candidates: list[int], target: int) -> list[list[int]]:
    """Canonical backtracking at the intended complexity: sort once, then DFS over
    the candidates in non-decreasing index order, subtracting each pick from the
    remaining target and abandoning a branch as soon as the smallest candidate
    left does not fit (sorting is what makes that a `break` rather than a
    `continue`). The recursion stays at the *same* index after taking a value,
    which is the statement's "the same number may be chosen unlimited times", and
    the index never decreases, so each combination is built in exactly one order:
    no duplicates are possible and no `set` is needed to dedupe.

    The result comes out ascending-lexicographic, the canonical form of the set
    answer the cases compare with "compare": "sorted". Time is the size of the
    search tree (exponential in the target, linear in the candidates per node);
    the auxiliary space is the recursion depth and the current path, at most
    target // min(candidates) + 1."""
    values = sorted(candidates)
    out: list[list[int]] = []
    path: list[int] = []

    def _combination_sum_walk(start: int, remaining: int) -> None:
        if remaining == 0:
            out.append(list(path))
            return
        for i in range(start, len(values)):
            value = values[i]
            if value > remaining:
                break
            path.append(value)
            _combination_sum_walk(i, remaining - value)
            path.pop()

    _combination_sum_walk(0, target)
    return out
