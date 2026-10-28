"""QUARANTINED assessment for `redundant-connection` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


def _redundant_connection_is_tree(n: int, edges: list[list[int]]) -> bool:
    """Is this edge set a tree on nodes 1..n?

    Checked as the statement defines a tree -- connected and acyclic -- with the
    edge count checked too, so a duplicated edge cannot slip through the
    `n - 1` arithmetic as if it were a tree."""
    if len(edges) != n - 1:
        return False
    adjacency: dict[int, list[int]] = {}
    for a, b in edges:
        adjacency.setdefault(a, []).append(b)
        adjacency.setdefault(b, []).append(a)
    seen = {1}
    stack = [(1, 0)]  # (node, parent)
    while stack:
        node, parent = stack.pop()
        for other in adjacency.get(node, []):
            if other not in seen:
                seen.add(other)
                stack.append((other, node))
            elif other != parent:
                return False  # a back edge: a cycle
    return len(seen) == n


@oracle("redundant-connection")
def _redundant_connection_oracle(edges: list[list[int]]) -> list[int]:
    """Brute force, straight off the statement: try every edge as the one to
    remove, scanning from the LAST edge to the first, and return the first edge
    whose removal leaves a tree on all n nodes. Walking the input backwards is
    what makes the statement's own tie-break -- "If there are multiple answers,
    return the answer that occurs last in the input" -- fall out without any
    code of its own.

    `n` is `len(edges)`, the statement's own constraint (`n == edges.length`,
    nodes labelled 1..n). The graph is connected by the statement's promise, so
    the remaining edge set is checked against the statement's definition of a
    tree directly: `n` nodes, `n - 1` edges, acyclic, and every node reachable
    from node 1."""
    n = len(edges)
    for i in range(n - 1, -1, -1):
        kept = [edge for j, edge in enumerate(edges) if j != i]
        if _redundant_connection_is_tree(n, kept):
            return [edges[i][0], edges[i][1]]
    return []  # unreachable: the statement promises exactly one extra edge


@cases("redundant-connection")
def _redundant_connection_case(n: int, rng: random.Random) -> tuple[list, list[int]]:
    """The statement's own construction: a random tree on nodes 1..n (each node
    v joins a random earlier node) plus one extra edge between two vertices the
    tree does not already join. The whole list is then shuffled, so the answer is
    "the last edge of the single cycle in the shuffled order" rather than a fixed
    position -- and every edge is written [min, max], because the statement's
    constraint is `1 <= a_i < b_i <= edges.length`."""
    n = max(3, min(n, 12))  # the statement's own range: 3 <= n <= 1000
    edges = [[rng.randint(1, v - 1), v] for v in range(2, n + 1)]
    taken = {(a, b) for a, b in edges}
    free = [
        (a, b)
        for a in range(1, n + 1)
        for b in range(a + 1, n + 1)
        if (a, b) not in taken
    ]
    a, b = rng.choice(free)  # never empty: a tree on n >= 3 nodes misses a pair
    edges.append([a, b])
    rng.shuffle(edges)
    return [edges], _redundant_connection_oracle(edges)


@inputs("redundant-connection")
def _redundant_connection_profiler(n: int, rng: random.Random) -> list:
    # A path 1-2-...-n (the tree) plus the edge [1, n] appended LAST: the last
    # edge in the input is the one that closes the only cycle, so it is also the
    # answer, and neither side can early-exit -- the union-find has to add all
    # n - 1 tree edges before it reaches the closing one, and the brute-force
    # oracle walks the input from the end. The path is also the shape that makes
    # an unranked union-find degenerate into a linear find per edge, which is the
    # student-side blowup this probe is meant to see. Every edge obeys the
    # statement: 1 <= a_i < b_i <= edges.length, distinct pairs, connected.
    n = max(3, min(n, 1000))  # the statement's own cap: n == edges.length <= 1000
    edges = [[i, i + 1] for i in range(1, n)]
    edges.append([1, n])
    return [edges]


@reference("redundant-connection")
def _redundant_connection_reference(edges: list[list[int]]) -> list[int]:
    """Canonical union-find: process the edges in the input's own order and return
    the first edge whose endpoints are already connected.

    That edge is exactly what the statement asks for. The graph is a tree plus one
    extra edge, so it has exactly one cycle, and the edges whose removal leaves a
    tree are precisely the edges of that cycle. The first edge found to close the
    cycle is the LAST cycle edge in input order -- every other cycle edge has
    already been added by the time it is reached, and no edge outside the cycle can
    close one -- which is the statement's tie-break rule.

    Path compression with union by size keeps the pass near-linear (O(n) amortized
    for n edges); the path shape in the profiler input is what an unranked
    union-find degenerates on."""
    n = len(edges)
    parent = list(range(n + 1))  # nodes are labelled 1..n
    size = [1] * (n + 1)

    def find(x: int) -> int:
        root = x
        while parent[root] != root:
            root = parent[root]
        while parent[x] != root:  # path compression
            parent[x], x = root, parent[x]
        return root

    for a, b in edges:
        ra, rb = find(a), find(b)
        if ra == rb:
            return [a, b]
        if size[ra] < size[rb]:
            ra, rb = rb, ra
        parent[rb] = ra
        size[ra] += size[rb]
    return []  # unreachable: the statement guarantees one extra edge


@measure("redundant-connection")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
