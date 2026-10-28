"""QUARANTINED assessment for `number-of-connected-components-in-an-undirected-graph` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("number-of-connected-components-in-an-undirected-graph")
def _number_of_connected_components_in_an_undirected_graph_oracle(n: int, edges: list[list[int]]) -> int:
    """Brute force: build the adjacency list and explore every node with an
    explicit stack, counting one component per unvisited start. Nothing is
    shared between the two sides of the differential beyond the statement's
    definition of a component (a maximal set of mutually reachable nodes).

    Total for n <= 0 (returning 0), which the statement's `1 <= n` excludes; a
    repeated edge only adds a duplicate adjacency entry and a self-loop only
    points a node at itself, neither of which changes the count here."""
    if n <= 0:
        return 0
    adjacency: list[list[int]] = [[] for _ in range(n)]
    for a, b in edges:
        adjacency[a].append(b)
        adjacency[b].append(a)
    seen = [False] * n
    components = 0
    for start in range(n):
        if seen[start]:
            continue
        components += 1
        seen[start] = True
        stack = [start]
        while stack:
            node = stack.pop()
            for other in adjacency[node]:
                if not seen[other]:
                    seen[other] = True
                    stack.append(other)
    return components


@cases("number-of-connected-components-in-an-undirected-graph")
def _number_of_connected_components_in_an_undirected_graph_case(n: int, rng: random.Random) -> tuple[list, int]:
    """A random forest (each node either starts its own component or joins a
    random earlier one), plus zero to two extra edges between pairs the forest
    does not use. The answer therefore ranges over 1..n and the generated set
    contains both extremes: one big component and all-isolated.

    Edges are written [min, max]; `a_i != b_i` and "no repeated edges" are
    upheld, so a pair is never emitted twice and never as a self-loop."""
    n = max(1, min(n, 12))  # the statement's own range: 1 <= n <= 2000
    edges: list[list[int]] = []
    taken: set[tuple[int, int]] = set()
    for v in range(1, n):
        if rng.random() < 0.6:
            u = rng.randrange(v)
            taken.add((u, v))
            edges.append([u, v])
    for _ in range(rng.randint(0, 2)):
        free = [
            (a, b)
            for a in range(n)
            for b in range(a + 1, n)
            if (a, b) not in taken
        ]
        if not free:
            break
        a, b = rng.choice(free)
        taken.add((a, b))
        edges.append([a, b])
    rng.shuffle(edges)
    return [n, edges], _number_of_connected_components_in_an_undirected_graph_oracle(n, edges)


@inputs("number-of-connected-components-in-an-undirected-graph")
def _number_of_connected_components_in_an_undirected_graph_profiler(n: int, rng: random.Random) -> list:
    # One path 0-1-...-(n-1): the whole graph is a single component, so the count
    # is only known after every node and every edge has been visited (there is no
    # early exit to take -- a traversal marks all n nodes, a union-find performs
    # all n - 1 unions, each of which merges two different components), and the
    # chain is the shape that degenerates an unranked union-find into a linear
    # find per edge. Inside the statement's constraints: 1 <= n <= 2000, n - 1
    # edges (<= 5000), a_i < b_i, no repeats, no self-loops.
    n = max(1, min(n, 2000))  # the statement's own cap: 1 <= n <= 2000
    return [n, [[i, i + 1] for i in range(n - 1)]]


@reference("number-of-connected-components-in-an-undirected-graph")
def _number_of_connected_components_in_an_undirected_graph_reference(n: int, edges: list[list[int]]) -> int:
    """Canonical union-find: every node starts in its own component and the count
    falls by one for each edge that joins two nodes that were not yet connected --
    an edge inside an existing component changes nothing. Path compression plus
    union by size keeps the pass near-linear (O(n + e) amortized here), and the
    parent array over the n nodes is the space; no adjacency list is ever built.

    Total for n <= 0 (returning 0), matching the oracle on the input the
    constraints exclude. A self-loop merges a node with itself (find(a) == find(a))
    and a repeated edge finds the same root twice; both leave the count alone, so
    the split does not depend on the statement's "no repeated edges" promise."""
    if n <= 0:
        return 0
    parent = list(range(n))
    size = [1] * n

    def find(x: int) -> int:
        root = x
        while parent[root] != root:
            root = parent[root]
        while parent[x] != root:  # path compression
            parent[x], x = root, parent[x]
        return root

    components = n
    for a, b in edges:
        ra, rb = find(a), find(b)
        if ra == rb:
            continue
        if size[ra] < size[rb]:
            ra, rb = rb, ra
        parent[rb] = ra
        size[ra] += size[rb]
        components -= 1
    return components


@measure("number-of-connected-components-in-an-undirected-graph")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
