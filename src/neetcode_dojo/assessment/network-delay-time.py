"""QUARANTINED assessment for `network-delay-time` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("network-delay-time")
def _network_delay_time_oracle(times: list[list[int]], n: int, k: int) -> int:
    """Brute force: Bellman-Ford. Distances start at infinity except the source,
    and n - 1 rounds each relax EVERY edge -- after round r every node reachable
    in r hops holds its shortest distance, so after n - 1 rounds every reachable
    node is settled. The answer is the largest settled distance, or -1 when some
    node is still at infinity.

    The rounds are deliberately NOT cut short when a round changes nothing: the
    full (n - 1) * e relaxation work is this implementation's honest cost, and
    the profiler input is measured against it.

    Inside the statement's constraints an edge always names two different nodes in
    1..n (the generator only emits those); an edge that names a node outside that
    range is skipped rather than raising, and the reference applies the same rule,
    so the two stay in step on shapes the statement forbids. n <= 1 and an
    out-of-range k return the statement's own answers for their degenerate cases
    (a lone source node needs no time; a source that is not a node reaches
    nothing)."""
    if n <= 0:
        return -1
    if n == 1:
        return 0
    if not 1 <= k <= n:
        return -1
    infinity = float("inf")
    distance = [infinity] * (n + 1)
    distance[k] = 0
    for _ in range(n - 1):
        for edge in times:
            u, v, w = edge[0], edge[1], edge[2]
            if not (1 <= u <= n and 1 <= v <= n):
                continue
            if distance[u] + w < distance[v]:
                distance[v] = distance[u] + w
    worst = max(distance[1:])
    return -1 if worst == infinity else int(worst)


@cases("network-delay-time")
def _network_delay_time_case(n: int, rng: random.Random) -> tuple[list, int, int]:
    """Two shapes, chosen at random, both inside the statement's constraints.

    CONNECTED (three cases in five): a directed cycle through a random order of
    the nodes (every node is then reachable from every other) plus a few extra
    unique pairs. The answer is a finite time.

    DISCONNECTED (two cases in five, so the -1 branch is about 40% of the
    generated set): a non-empty island of nodes that excludes k, with edges
    emitted only inside the reachable part or FROM the island INTO it -- nothing
    may enter the island, so those nodes stay unreachable from k and every such
    case answers -1. An edge island -> reachable is legal here and does not
    connect anything: reachability runs from k, and no edge points back.

    n is clamped to 2..12 and times.length is always >= 1: with ui != vi and at
    least one edge, the statement's `1 <= k <= n <= 100` and `1 <= times.length`
    cannot both hold at n = 1, so n = 1 is the one size the constraints exclude.
    Every edge is a unique ordered pair with 1 <= ui, vi <= n, ui != vi and
    0 <= wi <= 100."""
    n = max(2, min(n, 12))  # 1 <= k <= n <= 100, narrowed by ui != vi + times.length >= 1
    k = rng.randint(1, n)
    if rng.random() < 0.4:
        others = [node for node in range(1, n + 1) if node != k]
        rng.shuffle(others)
        island = set(others[: rng.randint(1, len(others))])
        reachable = {node for node in range(1, n + 1) if node not in island}
        allowed = [
            (u, v)
            for u in range(1, n + 1)
            for v in range(1, n + 1)
            if u != v and not (u in reachable and v in island)
        ]
        made = rng.sample(allowed, rng.randint(1, min(len(allowed), 2 * n)))
        edges = [[u, v, rng.randint(0, 100)] for u, v in made]
    else:
        order = list(range(1, n + 1))
        rng.shuffle(order)
        edges = [[order[i], order[(i + 1) % n], rng.randint(0, 100)] for i in range(n)]
        used = {(u, v) for u, v, _ in edges}
        for _ in range(rng.randint(0, 2 * n)):
            u, v = rng.randint(1, n), rng.randint(1, n)
            if u == v or (u, v) in used:
                continue
            used.add((u, v))
            edges.append([u, v, rng.randint(0, 100)])
    rng.shuffle(edges)
    return [edges, n, k], _network_delay_time_oracle(edges, n, k)


@inputs("network-delay-time")
def _network_delay_time_profiler(n: int, rng: random.Random) -> list:
    """The widest CONNECTED graph the statement allows at size n: n distinct edges
    over as many nodes as that edge budget can carry (v = min(100, n), the
    statement's own cap), built from a directed cycle through every node -- so
    every node is reachable from k = 1 and the answer is never -1 -- plus the
    remaining pairs in a deterministic spread order. Using the full node budget
    is what makes this the oracle's worst case as well: Bellman-Ford costs
    (v - 1) * e, so 99 rounds over the whole edge list at the cap.

    Both sides do their full work and neither can early-exit: Dijkstra relaxes
    every one of the e edges and settles all v nodes, and Bellman-Ford runs its
    full (v - 1) * e relaxations over the whole edge list -- every round over
    every edge, which is the work a reachable graph with this many edges forces
    at this node count. Weights are deterministic values in 0..100, and many of
    them tie, which is the shape that exercises a heap's tie handling.

    Inside the statement's constraints: 1 <= k = 1 <= v <= 100 nodes,
    times.length = n <= 6000, every edge a unique ordered pair (u, v) with
    u != v and 0 <= wi <= 100. The construction is deterministic from n (rng is
    unused) so the input at a given size is the same for the student run, the
    reference run, `locate_mismatch` and `flow._oracle_confirms`."""
    n = max(2, min(n, 6000))  # the statement's own cap: 1 <= times.length <= 6000
    nodes = min(100, n)  # as many nodes as the edge budget can carry (a cycle needs v edges)
    edges: list[list[int]] = []
    used: set[tuple[int, int]] = set()
    for u in range(1, nodes + 1):
        v = u % nodes + 1
        used.add((u, v))
        edges.append([u, v, (u * 12289 + v * 3) % 101])
    rest = [
        (u, v)
        for u in range(1, nodes + 1)
        for v in range(1, nodes + 1)
        if u != v and (u, v) not in used
    ]
    # Deterministic spread: a cheap mixing key instead of the natural (u, v)
    # order, which would pile every extra edge onto the lowest-numbered node.
    rest.sort(key=lambda pair: ((pair[0] * 7919) ^ (pair[1] * 104729)) % 1000003)
    for u, v in rest[: n - nodes]:
        edges.append([u, v, (u * 12289 + v * 3) % 101])
    edges.sort()
    return [edges, nodes, 1]


@reference("network-delay-time")
def _network_delay_time_reference(times: list[list[int]], n: int, k: int) -> int:
    """Canonical Dijkstra on a non-negative weighted directed graph: build the
    adjacency list, then repeatedly settle the unsettled node with the smallest
    known distance and relax its outgoing edges. Pop with a stale (larger) key are
    skipped, so every node is settled once and every edge relaxed once, giving
    O(e log n) time and O(n + e) space -- against the oracle's O(n * e)
    Bellman-Ford rounds.

    The answer is the largest settled distance; a node still at infinity was
    unreachable, which is the statement's -1. Weights may be 0 (the statement's
    own bound), which Dijkstra handles because they are never negative.

    Total on the shapes the statement excludes: n <= 1 and an out-of-range k
    return the same answers the oracle gives, and an edge naming a node outside
    1..n is skipped there too."""
    import heapq

    if n <= 0:
        return -1
    if n == 1:
        return 0
    if not 1 <= k <= n:
        return -1
    adjacency: list[list[tuple[int, int]]] = [[] for _ in range(n + 1)]
    for edge in times:
        u, v, w = edge[0], edge[1], edge[2]
        if 1 <= u <= n and 1 <= v <= n:
            adjacency[u].append((v, w))
    infinity = float("inf")
    distance = [infinity] * (n + 1)
    distance[k] = 0
    heap = [(0, k)]
    while heap:
        delay, node = heapq.heappop(heap)
        if delay > distance[node]:
            continue  # a stale entry: this node was settled with a smaller delay
        for neighbour, weight in adjacency[node]:
            candidate = delay + weight
            if candidate < distance[neighbour]:
                distance[neighbour] = candidate
                heapq.heappush(heap, (candidate, neighbour))
    worst = max(distance[1:])
    return -1 if worst == infinity else int(worst)


@measure("network-delay-time")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
