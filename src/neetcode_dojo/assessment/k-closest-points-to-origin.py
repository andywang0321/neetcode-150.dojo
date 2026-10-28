"""QUARANTINED assessment for `k-closest-points-to-origin` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, checker, inputs, measure, oracle, reference


@oracle("k-closest-points-to-origin")
def _k_closest_points_to_origin_oracle(k: int, points: list[list[int]]) -> list[list[int]]:
    """Brute force: pick the closest remaining point k times (O(k*n)). That is the
    contract itself rather than a sort or a heap, and which of several tied points it
    happens to take does not matter — every case is judged by k_closest_valid."""
    remaining = [list(point) for point in points]
    chosen: list[list[int]] = []
    for _ in range(k):
        closest = min(
            range(len(remaining)),
            key=lambda i: (remaining[i][0] ** 2 + remaining[i][1] ** 2, i),
        )
        chosen.append(remaining.pop(closest))
    return chosen


@cases("k-closest-points-to-origin")
def _k_closest_points_to_origin_case(n: int, rng: random.Random) -> tuple[list, bool, dict]:
    n = max(1, min(n, 12))  # the statement's own constraint: 1 <= points.length
    roll = rng.random()
    if roll < 0.4:
        # A ring of four points at one distance r, drawn with replacement: every k
        # below n cuts a tie group, which is what equality judging false-fails on.
        r = rng.randint(1, 4)
        ring = [[r, 0], [0, r], [-r, 0], [0, -r]]
        points = [list(rng.choice(ring)) for _ in range(n)]
    elif roll < 0.7:
        # A tiny coordinate range: distance ties are frequent but not guaranteed.
        points = [[rng.randint(-3, 3), rng.randint(-3, 3)] for _ in range(n)]
    else:
        points = [  # the statement's stated range: -10^4 <= xi, yi <= 10^4
            [rng.randint(-10_000, 10_000), rng.randint(-10_000, 10_000)]
            for _ in range(n)
        ]
    dists = sorted(x * x + y * y for x, y in points)
    cuts = [i + 1 for i in range(n - 1) if dists[i] == dists[i + 1]]
    # Put k on a distance tie whenever the points offer one, so the boundary tie is
    # not left to chance; otherwise any k in the statement's own 1 <= k <= n.
    k = rng.choice(cuts) if cuts else rng.randint(1, n)
    return [k, points], True, {"predicate": "k_closest_valid"}


@inputs("k-closest-points-to-origin")
def _k_closest_points_to_origin_profiler(n: int, rng: random.Random) -> list:
    # k = n//2: the size-k heap fills half way and every later point then pays a
    # log k replace, so the reference cannot early-exit. Random coordinates across
    # the whole stated range (-10^4..10^4) keep the squared distances distinct (no
    # lucky tie short-circuit) and respect the statement's own value constraint,
    # not just the shape (v0.12). The brute-force oracle never runs at this size:
    # the gate and the registry tests drive it on small cases only, and
    # scale_compare "none" makes _oracle_confirms return before it is called.
    points = [
        [rng.randint(-10_000, 10_000), rng.randint(-10_000, 10_000)] for _ in range(n)
    ]
    return [max(1, n // 2), points]


@reference("k-closest-points-to-origin")
def _k_closest_points_to_origin_reference(k: int, points: list[list[int]]) -> list[list[int]]:
    """Canonical heap solution (the answer this group is about): a size-k max-heap
    keyed by squared distance — (-d, x, y) in a min-heap — so each point costs
    O(log k) and the heap holds O(k): O(n log k) time, O(k) space. Distances are
    exact integer squares, so no float rounding can reorder them. Which of several
    tied points survives is arbitrary, and k_closest_valid accepts any valid choice;
    the returned list is sorted closest-first only so the output is deterministic."""
    import heapq

    heap: list[tuple[int, int, int]] = []
    for x, y in points:
        item = (-(x * x + y * y), x, y)
        if len(heap) < k:
            heapq.heappush(heap, item)
        elif item > heap[0]:  # -d > -d_max: strictly closer than the farthest kept
            heapq.heapreplace(heap, item)
    return [[x, y] for _, x, y in sorted(heap, key=lambda t: (-t[0], t[1], t[2]))]


@checker("k_closest_valid")
def _k_closest_valid(module, got, args) -> bool:
    """The true k-closest contract — 'ties may be broken in any order':
    exactly k points drawn from the input multiset, none farther than the
    k-th smallest distance, and every strictly-closer point fully included.
    Equality judging false-fails on boundary ties; this grades the set."""
    from collections import Counter

    k, points = args
    if not isinstance(got, list) or len(got) != k:
        return False
    got_counts = Counter(tuple(p) for p in got)
    point_counts = Counter(tuple(p) for p in points)
    if any(got_counts[p] > point_counts.get(p, 0) for p in got_counts):
        return False  # more copies of a coordinate than the input holds
    dists = sorted(p[0] ** 2 + p[1] ** 2 for p in points)
    threshold = dists[k - 1]
    for p in points:
        d = p[0] ** 2 + p[1] ** 2
        if d < threshold and got_counts[tuple(p)] != point_counts[tuple(p)]:
            return False  # a strictly-closer point was skipped
        if d > threshold and got_counts[tuple(p)] > 0:
            return False  # a farther point sneaked in
    return True


@measure("k-closest-points-to-origin")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    none."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'none'}
