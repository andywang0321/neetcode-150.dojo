"""QUARANTINED assessment for `min-cost-to-connect-all-points` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


def _min_cost_to_connect_all_points_sample(
    n: int, rng: random.Random, span: int
) -> list[list[int]]:
    """`n` DISTINCT points with coordinates in [-span, span] (the statement's
    "all pairs (xi, yi) are distinct"). A small `span` makes ties and near-ties
    common; the full 10^6 makes the coordinate arithmetic the statement's own."""
    seen: set[tuple[int, int]] = set()
    points: list[list[int]] = []
    while len(points) < n:
        point = (rng.randint(-span, span), rng.randint(-span, span))
        if point in seen:
            continue
        seen.add(point)
        points.append([point[0], point[1]])
    return points


@oracle("min-cost-to-connect-all-points")
def _min_cost_to_connect_all_points_oracle(points: list[list[int]]) -> int:
    """Exhaustive over the COMPLETE graph: materialize every pair of points as an
    edge carrying its manhattan cost, sort the edges cheapest first, and walk
    them, adding each edge that joins two points which are not already connected.
    That is the statement's sentence read directly ("make all points connected
    ... minimum cost") with the statement's own distance formula, and it is
    correct by the standard exchange argument: the cheapest edge joining two
    components belongs to some minimum spanning tree.

    A union-find answers "are these two already connected?" as the walk proceeds,
    which is what keeps an exhaustive edge walk affordable -- every one of the
    n(n-1)/2 pairs is visited exactly once, so the cost is O(n^2 log n) time (the
    sort) and O(n^2) space. That is strictly worse than the reference on both axes
    -- a correctness anchor, never a performance baseline -- but it is not
    exponential, so it stays runnable wherever the judge, the probe smoke and
    `flow._oracle_confirms` call it, including the statement's full 1000-point
    cap.

    It shares NOTHING with the reference beyond the manhattan formula: no
    incremental frontier, no per-point distance array, no cut scan.

    Total on the shapes the statement excludes: n <= 1 gives 0."""
    n = len(points)
    if n <= 1:
        return 0
    edges: list[tuple[int, int, int]] = []
    for i in range(n):
        x, y = points[i]
        for j in range(i + 1, n):
            edges.append((abs(x - points[j][0]) + abs(y - points[j][1]), i, j))
    edges.sort()
    parent = list(range(n))
    size = [1] * n
    total = 0
    joined = 0
    for cost, i, j in edges:
        a = i
        while parent[a] != a:  # find, halving the path on the way up
            parent[a] = parent[parent[a]]
            a = parent[a]
        b = j
        while parent[b] != b:
            parent[b] = parent[parent[b]]
            b = parent[b]
        if a == b:
            continue  # this pair is already connected; adding it would close a cycle
        if size[a] < size[b]:
            a, b = b, a
        parent[b] = a
        size[a] += size[b]
        total += cost
        joined += 1
        if joined == n - 1:  # a spanning tree is complete
            break
    return total


@cases("min-cost-to-connect-all-points")
def _min_cost_to_connect_all_points_case(n: int, rng: random.Random) -> tuple[list, int]:
    """Distinct random points, drawn from a tiny span half the time and from the
    statement's full +-10^6 the rest: the tiny span produces the equal and
    near-equal distances a tie-free sample would never show, and the full span
    exercises the statement's own coordinate arithmetic (|dx| + |dy| up to
    2 * 10^6). Both are inside the constraints -- 1 <= n <= 12 distinct points,
    -10^6 <= xi, yi <= 10^6. `expected` is the oracle's own answer."""
    n = max(1, min(n, 12))  # the statement's own range: 1 <= points.length <= 1000
    span = 10 ** 6 if rng.random() < 0.5 else 3
    points = _min_cost_to_connect_all_points_sample(n, rng, span)
    return [points], _min_cost_to_connect_all_points_oracle(points)


@inputs("min-cost-to-connect-all-points")
def _min_cost_to_connect_all_points_profiler(n: int, rng: random.Random) -> list:
    """`n` distinct points spread over the statement's FULL coordinate range
    (-10^6 .. 10^6), so the manhattan arithmetic is the problem's own largest
    (|dx| + |dy| up to 2 * 10^6) rather than a toy range, and no pair is ever
    zero-distance.

    There is no early exit for either side to take: every point has to end up
    connected, so the reference relaxes all n^2 ordered pairs and the oracle
    visits all n(n-1)/2 edges. The sequence is generated deterministically from n
    (a fixed-seed LCG, no rng), so the input at a given size is the same for the
    student run, the reference run, `locate_mismatch` and
    `flow._oracle_confirms` -- those last two build their own Random, and a
    size-independent-of-rng shape keeps their comparison on the same input the
    probe measured.

    Inside the statement's constraints: n <= 1000 points, coordinates in
    +-10^6, all distinct. probe_max_n = 1000 is that cap, which the oracle can
    afford: it walks every pair once, not every pair per round."""
    n = max(1, min(n, 1000))  # the statement's own cap: 1 <= points.length <= 1000
    span = 10 ** 6
    state = 20_240_510
    seen: set[tuple[int, int]] = set()
    points: list[list[int]] = []
    while len(points) < n:
        state = (state * 1_103_515_245 + 12_345) % (2 ** 31)
        x = state % (2 * span + 1) - span
        state = (state * 1_103_515_245 + 12_345) % (2 ** 31)
        y = state % (2 * span + 1) - span
        if (x, y) in seen:
            continue
        seen.add((x, y))
        points.append([x, y])
    return [points]


@reference("min-cost-to-connect-all-points")
def _min_cost_to_connect_all_points_reference(points: list[list[int]]) -> int:
    """Canonical array-based Prim: keep one growing tree and, for every point
    outside it, the cost of its cheapest known edge into the tree. Each round
    takes the outside point with the smallest such cost (its point 0 seeds the
    tree at cost 0), adds that cost to the total, and relaxes that point's
    distance against every point still outside -- so each of the n^2 ordered
    pairs is looked at once and no edge list is ever built.

    O(n^2) time and O(n) space, which is the statement's target: the graph here is
    COMPLETE (any two points may be connected), so materializing its n(n-1)/2
    edges to sort them would cost O(n^2 log n) time and O(n^2) space for nothing.

    Total on the shapes the statement excludes: n <= 1 gives 0."""
    n = len(points)
    if n <= 1:
        return 0
    best: list[int | None] = [None] * n  # cheapest known edge into the tree
    in_tree = [False] * n
    best[0] = 0
    total = 0
    for _ in range(n):
        pick = -1
        for j in range(n):
            if in_tree[j] or best[j] is None:
                continue
            if pick == -1 or best[j] < best[pick]:
                pick = j
        in_tree[pick] = True
        total += best[pick]
        x, y = points[pick]
        for j in range(n):
            if in_tree[j]:
                continue
            cost = abs(x - points[j][0]) + abs(y - points[j][1])
            if best[j] is None or cost < best[j]:
                best[j] = cost
    return total


@measure("min-cost-to-connect-all-points")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
