"""QUARANTINED assessment for `graph-valid-tree` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("graph-valid-tree")
def _graph_valid_tree_oracle(n: int, edges: list[list[int]]) -> bool:
    """Brute force: the statement's definition, checked directly. One DFS from
    node 0, carrying the node it came from, must reach every node (connected) and
    must never meet a node it has already seen except the one it came from
    (acyclic).

    Total for n <= 0 (returning False), excluded by the statement's `1 <= n`. The
    parent test is what makes a repeated edge and a self-loop read as the cycles
    they are, so both sides of the differential agree on those shapes too."""
    if n <= 0:
        return False
    adjacency: list[list[int]] = [[] for _ in range(n)]
    for a, b in edges:
        adjacency[a].append(b)
        adjacency[b].append(a)
    seen = [False] * n
    seen[0] = True
    visited = 1
    stack = [(0, -1)]  # (node, parent)
    while stack:
        node, parent = stack.pop()
        for other in adjacency[node]:
            if not seen[other]:
                seen[other] = True
                visited += 1
                stack.append((other, node))
            elif other != parent:
                return False  # a back edge: a cycle
    return visited == n


@cases("graph-valid-tree")
def _graph_valid_tree_case(n: int, rng: random.Random) -> tuple[list, bool]:
    """Build a spanning tree on all n nodes (node v joins a random earlier node),
    then deliberately break it one of the two ways the statement names or leave it
    alone: about a third of the cases add one edge between a pair the tree does not
    use (a cycle, so `false`), about a third drop one tree edge (two components and
    n - 2 edges, so `false`), and the rest stay valid trees (`true`).

    Inside the statement's constraints: 1 <= n <= 12, edges written [min, max] with
    0 <= a_i, b_i <= n - 1, a_i != b_i, no repeated pairs. A one-node case (n = 1,
    no edges) is a valid tree and the generator emits it."""
    n = max(1, min(n, 12))  # the statement's own range: 1 <= n <= 2000
    edges: list[list[int]] = []
    taken: set[tuple[int, int]] = set()
    for v in range(1, n):
        u = rng.randrange(v)
        taken.add((u, v))
        edges.append([u, v])
    roll = rng.random()
    if n >= 2 and roll < 0.34:
        free = [
            (a, b)
            for a in range(n)
            for b in range(a + 1, n)
            if (a, b) not in taken
        ]
        if free:  # empty only for n = 2, where the tree already uses the one pair
            a, b = rng.choice(free)
            edges.append([a, b])
    elif n >= 2 and roll < 0.67:
        edges.pop(rng.randrange(len(edges)))  # one component splits in two
    rng.shuffle(edges)
    return [n, edges], _graph_valid_tree_oracle(n, edges)


@inputs("graph-valid-tree")
def _graph_valid_tree_profiler(n: int, rng: random.Random) -> list:
    # A path 0-1-...-(n-1) is a valid tree: the answer is True and NOTHING can
    # short-circuit. The edge count matches n - 1 exactly, so a solution that
    # checks the count first still has to look at every edge; there is no cycle,
    # so a union-find performs all n - 1 unions; and the traversal has to visit
    # every node and every edge to answer "connected". The alternative -- a near
    # tree whose LAST edge closes a cycle -- would let an `edges.length != n - 1`
    # check answer after one step, which would measure that solution as O(1).
    # The chain is also the shape an unranked union-find degenerates on. Inside
    # the statement's constraints: 1 <= n <= 2000, n - 1 edges (<= 5000), a_i <
    # b_i, no self-loops, no repeated edges.
    n = max(1, min(n, 2000))  # the statement's own cap: 1 <= n <= 2000
    return [n, [[i, i + 1] for i in range(n - 1)]]


@reference("graph-valid-tree")
def _graph_valid_tree_reference(n: int, edges: list[list[int]]) -> bool:
    """Canonical union-find: a valid tree on n nodes has exactly n - 1 edges, and
    every edge must join two DIFFERENT components -- the first edge that joins
    nodes already connected closes a cycle, so the edges are not a tree.

    The connectivity half needs no second pass, and that is a theorem rather than
    a shortcut: a forest on n nodes with c components has exactly n - c edges, so
    n - 1 edges with no cycle forces c = 1. The `len(edges) != n - 1` check is O(1)
    and does not skip any work on a real tree (it is exactly what the profiler
    input satisfies), which keeps the measured baseline a full union pass.

    Total for n <= 0 (returning False), matching the oracle on the input the
    constraints exclude. A repeated edge returns False here (same root found
    twice) and a self-loop returns False (find(a) == find(a)), the same answers the
    oracle gives, so the split does not depend on the statement's "no repeated
    edges / no self-loops" promises -- only on the definition of a tree."""
    if n <= 0:
        return False
    if len(edges) != n - 1:
        return False
    parent = list(range(n))
    size = [1] * n

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
            return False  # already connected: this edge closes a cycle
        if size[ra] < size[rb]:
            ra, rb = rb, ra
        parent[rb] = ra
        size[ra] += size[rb]
    return True


@measure("graph-valid-tree")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
