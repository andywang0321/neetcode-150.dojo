"""QUARANTINED assessment for `hand-of-straights` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


def _hand_of_straights_groups(cards: tuple[int, ...], group_size: int):
    """Lazily yield every `group_size`-card sub-multiset of `cards` that contains
    its first card, as a value list. Index combinations, so two copies of the same
    value are two distinct choices."""

    def tails(start: int, need: int):
        if need == 0:
            yield ()
            return
        for index in range(start, len(cards) - need + 1):
            for rest in tails(index + 1, need - 1):
                yield (index,) + rest

    for indexes in tails(1, group_size - 1):
        yield [cards[0]] + [cards[index] for index in indexes]


@oracle("hand-of-straights")
def _hand_of_straights_oracle(hand: list[int], group_size: int) -> bool:
    """Exhaustive search: peel one group off at a time, recursing on the rest.

    A group is `group_size` *consecutive* cards, so the group holding the smallest
    remaining card can only be the run that starts there. This does not take that
    on trust: it enumerates every sub-multiset of that size from the remaining
    cards, keeps the ones whose values are that run, and recurses on what is left.
    With duplicates several index combinations are the same pick - a group's values
    are forced once its smallest card is fixed, so the enumeration's alternatives
    are all rejected and the search consumes cards rather than choosing between
    readings.

    What it does not reuse from the reference is any of the counting: no
    multiplicities, no divisibility shortcut, no sorted sweep. Removing ONE card per
    value (not every copy of those values - the hand is a multiset, and this is
    where such a search usually goes wrong) is a merge walk over the two sorted
    lists, and `failed` memoizes the multisets already proven impossible.

    Total on the empty hand (excluded by the statement's length bound) and on
    group_size 1, where every single card is a group of one. The recursion costs
    one frame per group peeled, so it reaches ~2900 cards at group_size 3 and would
    hit the interpreter's limit beyond that; every path that runs it stays far
    below - generated cases are <= 12 cards and the probe's oracle-versus-reference
    differential stops at 800 cards (the full 6400-card ladder measures the
    reference alone)."""
    cards = sorted(hand)
    if group_size < 1 or len(cards) % group_size:
        return False
    failed: set[tuple[int, ...]] = set()

    def peel(remaining: tuple[int, ...]) -> bool:
        if not remaining:
            return True
        if remaining in failed:
            return False
        run = [remaining[0] + step for step in range(group_size)]
        for picked in _hand_of_straights_groups(remaining, group_size):
            if sorted(picked) != run:
                continue
            gone = sorted(picked)
            rest: list[int] = []
            taken = 0
            for card in remaining:  # both lists are sorted: drop one copy per value
                if taken < len(gone) and card == gone[taken]:
                    taken += 1
                    continue
                rest.append(card)
            if peel(tuple(rest)):
                return True
        failed.add(remaining)
        return False

    return peel(tuple(cards))


@cases("hand-of-straights")
def _hand_of_straights_case(n: int, rng: random.Random) -> tuple[list, bool]:
    size = max(1, min(n, 12))  # statement: 1 <= hand.length <= 10^4
    group_size = rng.randint(1, size)  # statement: 1 <= groupSize <= hand.length
    roll = rng.random()
    if roll < 0.45 and size % group_size == 0:
        # A hand that IS a partition: size / group_size groups of consecutive
        # cards laid down at random starts. Groups may share values - the hand is a
        # multiset, so [1,2,3,1,2,3] is two groups of three.
        hand: list[int] = []
        for _ in range(size // group_size):
            start = rng.randint(0, 9)
            hand.extend(range(start, start + group_size))
    elif roll < 0.75:
        # A partitionable-looking hand with one card bumped by +1: the runs are
        # right but a count is off. This is the near miss the examples miss (they
        # fail on divisibility), and whether it is really unpartitionable is the
        # oracle's call, not the construction's.
        hand = []
        for _ in range(max(1, size // group_size)):
            start = rng.randint(0, 9)
            hand.extend(range(start, start + group_size))
        hand = hand[:size]
        hand[rng.randrange(len(hand))] += 1
    else:
        # No structure at all: duplicates and gaps in any arrangement.
        hand = [rng.randint(0, 9) for _ in range(size)]
    rng.shuffle(hand)
    return [hand, group_size], _hand_of_straights_oracle(hand, group_size)


@inputs("hand-of-straights")
def _hand_of_straights_profiler(n: int, rng: random.Random) -> list:
    # A hand that IS partitionable and has all-distinct values: the run 0, 1, ...,
    # size-1 cut into groups of three, inside the statement's 0..10^9 range.
    # Nothing can early-exit - the answer is true, no value of a run is missing and
    # every card is consumed - and ~n distinct values are what makes the counting
    # sweep sort a key per card, which is the intended solution's real cost (a
    # heap-based solution pays the same n log n, and a per-card rescan is what the
    # probe is there to catch).
    #
    # The ladder's smallest points bottom out at three cards, the fewest that can
    # form a group at all; the values stay distinct, so no duplicate can mask a
    # dropped or double-counted card and the digest changes with it.
    group_size = 3
    size = max(group_size, n - n % group_size)
    return [[i for i in range(size)], group_size]


@reference("hand-of-straights")
def _hand_of_straights_reference(hand: list[int], group_size: int) -> bool:
    """The intended O(n log n): count the cards, then sweep the distinct values in
    ascending order.

    Each distinct value is a group *start* as many times as it is still
    outstanding when the sweep reaches it (`need`), because the groups that
    contain the smallest unfinished value must all start exactly there. Those
    `need` groups then need `need` cards of each of the next `group_size - 1`
    values, which is what the inner loop charges. O(n) space for the counts, at
    most one entry per distinct card."""
    if group_size < 1 or len(hand) % group_size:
        return False
    counts: dict[int, int] = {}
    for card in hand:
        counts[card] = counts.get(card, 0) + 1
    for start in sorted(counts):
        need = counts[start]
        if need == 0:  # already consumed by the groups that started below it
            continue
        for value in range(start, start + group_size):
            if counts.get(value, 0) < need:
                return False
            counts[value] -= need
    return True


@measure("hand-of-straights")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
