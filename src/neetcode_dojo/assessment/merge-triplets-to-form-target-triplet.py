"""QUARANTINED assessment for `merge-triplets-to-form-target-triplet` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("merge-triplets-to-form-target-triplet")
def _merge_triplets_oracle(triplets: list[list[int]], target: list[int]) -> bool:
    """Brute force by running the stated operation to its end.

    A merge writes a componentwise max into one of the two slots, so a triplet
    that is already above `target` in some coordinate can never come back down.
    Nor can one ever help: follow the lineage of the element that ends up equal to
    `target` back through the merges that built it and every value on that lineage
    is the componentwise max of some subset of the original triplets - hence at
    most `target` componentwise, because the final value is `target`. So only
    triplets that stay inside `target` can take part in a sequence that works.

    Merging *all* of those into a single slot is a legal sequence of the stated
    operation, and it leaves their componentwise maximum in that slot: the largest
    triplet any legitimate sequence can hold. The target is obtainable exactly when
    that maximum is the target itself - if it is below the target in some
    coordinate, every subset's maximum is too. One pass, O(1) extra space, total on
    an empty triplet list (which the statement's length bound excludes)."""
    size = len(target)
    best = None
    for row in triplets:
        if all(row[k] <= target[k] for k in range(size)):
            best = list(row) if best is None else [max(best[k], row[k]) for k in range(size)]
    return best is not None and best == list(target)


@cases("merge-triplets-to-form-target-triplet")
def _merge_triplets_case(n: int, rng: random.Random) -> tuple[list, list]:
    size = max(1, min(n, 12))  # statement: 1 <= triplets.length <= 10^5
    # Every coordinate stays inside the statement's 1..1000 (these are 1..11), and
    # the target's own values are >= 2 so that "one below it" is still >= 1.
    target = [rng.randint(2, 8) for _ in range(3)]
    roll = rng.random()
    if roll < 0.4:
        # Obtainable: one triplet per coordinate, each one inside the target and
        # matching it on its own axis.
        triplets = [
            [target[axis] if k == axis else rng.randint(1, target[k]) for k in range(3)]
            for axis in range(3)
        ]
    elif roll < 0.55:
        # Obtainable the easy way: the target is already a triplet.
        triplets = [list(target)]
    elif roll < 0.8:
        # Every triplet stays inside the target, yet one coordinate is never hit
        # exactly - so the answer is false although nothing overshoots.
        axis = rng.randrange(3)
        triplets = [
            [rng.randint(1, target[k] - 1) if k == axis else rng.randint(1, target[k])
             for k in range(3)]
            for _ in range(size)
        ]
    elif roll < 0.9:
        # Every triplet overshoots the target in the same coordinate: none of them
        # may take part, and no merge can repair a value that is already too big.
        axis = rng.randrange(3)
        over = target[axis] + rng.randint(1, 3)
        triplets = [
            [over if k == axis else rng.randint(1, target[k]) for k in range(3)]
            for _ in range(size)
        ]
    else:
        # An unstructured draw: random triplets against a random target.
        triplets = [[rng.randint(1, 8) for _ in range(3)] for _ in range(size)]
    triplets = triplets[:size]
    while len(triplets) < size:
        # Filler rows, drawn like the unstructured branch: they may add coverage or
        # overshoot, and the oracle decides what that does to the answer.
        triplets.append([rng.randint(1, 8) for _ in range(3)])
    rng.shuffle(triplets)
    return [triplets, target], _merge_triplets_oracle(triplets, target)


@inputs("merge-triplets-to-form-target-triplet")
def _merge_triplets_profiler(n: int, rng: random.Random) -> list:
    # n triplets, every one of them inside the target (so a correct solution must
    # look at all of them - it cannot discard a row and stop), but the third
    # coordinate is drawn from 1..999 against a target of 1000, so that coordinate
    # is never matched and the answer is false: no implementation can return early
    # on a success either. Values stay inside the statement's 1..1000 and ~n rows of
    # three coordinates are the input's whole size.
    target = [1000, 1000, 1000]
    triplets = [
        [rng.randint(1, 1000), rng.randint(1, 1000), rng.randint(1, 999)]
        for _ in range(n)
    ]
    return [triplets, target]


@reference("merge-triplets-to-form-target-triplet")
def _merge_triplets_reference(triplets: list[list[int]], target: list[int]) -> bool:
    """The intended single pass: one sweep, three flags.

    Keep only the triplets that stay inside the target - anything above it is stuck
    above it and can never be part of a merge that ends at the target - and record
    which coordinates of the target one of those already matches. A coordinate that
    no surviving triplet matches can never be reached, because every value a merge
    can produce is a componentwise max of original triplets and this one is below
    the target everywhere. O(n) time over the triplets and O(1) extra space."""
    size = len(target)
    seen = [False] * size
    for row in triplets:
        if all(row[k] <= target[k] for k in range(size)):
            for k in range(size):
                if row[k] == target[k]:
                    seen[k] = True
    return all(seen)


@measure("merge-triplets-to-form-target-triplet")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
