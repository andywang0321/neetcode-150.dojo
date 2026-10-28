"""QUARANTINED assessment for `clone-graph` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, checker, inputs, measure, oracle, reference


@oracle("clone-graph")
def _clone_graph_oracle(graph: list[list[int]]) -> list[list[int]]:
    """Brute force: the definition of "deep copy" in dojo's representation.

    A brand-new list per node, each holding a brand-new neighbour list with the
    same indices. No traversal, no visited map, no assumption that the input is
    connected or even that it is a well-formed graph -- it is structurally blind
    to HOW a copy was built, which is what makes it a usable correctness anchor
    for a problem whose entire contract is the identity of the copy. Total on the
    empty graph (the statement's own Example 3) and on a disconnected input
    (which the statement's "The Graph is connected" excludes)."""
    return [list(neighbours) for neighbours in graph]


@cases("clone-graph")
def _clone_graph_case(n: int, rng: random.Random) -> tuple[list, list, dict]:
    # The statement's [0, 100] nodes; the caller sends 0..12, and n = 0 is the
    # statement's own empty-graph case. The graph is built the way the statement
    # promises -- connected, simple, undirected -- because graph_copy_valid
    # grades the input by exactly those invariants: a spanning tree first
    # (connected by construction), then extra edges that are never duplicates,
    # then a shuffle of every neighbour list, since the statement calls an
    # adjacency list "a collection of unordered lists". expected comes from the
    # oracle, so it is a genuine deep copy, not the input itself.
    size = max(0, min(n, 12))
    graph: list[list[int]] = [[] for _ in range(size)]
    for node in range(1, size):
        parent = rng.randrange(node)
        graph[node].append(parent)
        graph[parent].append(node)
    for _ in range(rng.randint(0, size)):
        a, b = rng.randrange(size), rng.randrange(size)
        if a != b and b not in graph[a]:
            graph[a].append(b)
            graph[b].append(a)
    for entry in graph:
        rng.shuffle(entry)
    return [graph], _clone_graph_oracle(graph), {"predicate": "graph_copy_valid"}


@inputs("clone-graph")
def _clone_graph_profiler(n: int, rng: random.Random) -> list:
    """One cycle over `size` nodes, `size` clamped to the statement's [0, 100].

    The cycle is the shape whose total size is ~n: n nodes and n edges, so
    neither term can dominate, and both implementations have to touch every node
    and every edge -- the reference BFS walks the whole ring, the oracle rebuilds
    every list, and there is nothing either could early-exit on. Indices are the
    graph's value domain in this representation (the statement's unique 1..100
    `val`s become 0-based indices) and they stay in range by construction, which
    is the value-fidelity rule of the v0.12 lesson applied to an index-valued
    input. Node 0's list is [1, size - 1] for size >= 3 -- deliberately unsorted,
    so nothing passes by rebuilding sorted lists. rng is unused: a paired
    measurement wants the same deterministic shape at every rung. The overrides
    carry probe_max_n = 100 so the ladder (1, 3, 6, 12, 25, 50, 100) stays inside
    the statement's own node bound."""
    size = max(1, min(n, 100))
    graph: list[list[int]] = [[] for _ in range(size)]
    for node in range(size):
        nxt = (node + 1) % size
        if nxt != node:  # size == 1: one node, no edge
            graph[node].append(nxt)
            graph[nxt].append(node)
    return [graph]


@reference("clone-graph")
def _clone_graph_reference(graph: list[list[int]]) -> list[list[int]]:
    # The canonical traversal clone: one new (empty) neighbour list per node,
    # then a breadth-first walk that copies each node's edges as it discovers
    # them, so every node and every edge is visited exactly once -- O(n + e)
    # time, O(n) extra space on top of the copy it returns (the copy itself is
    # the output, which is why the declared space is O(n + e) rather than O(n)).
    # Iterating over every possible start keeps it total on a disconnected
    # input, which the statement excludes; on a connected one the outer loop
    # finds nothing left to do after the first pass.
    copied: list[list[int]] = [[] for _ in graph]
    seen = [False] * len(graph)
    for start in range(len(graph)):
        if seen[start]:
            continue
        seen[start] = True
        queue = [start]
        head = 0
        while head < len(queue):
            node = queue[head]
            head += 1
            for neighbour in graph[node]:
                copied[node].append(neighbour)
                if not seen[neighbour]:
                    seen[neighbour] = True
                    queue.append(neighbour)
    return copied


@checker("graph_copy_valid")
def _graph_copy_valid(module, got, args) -> bool:
    """The deep-copy contract for clone-graph in the corpus's index-valued
    adjacency-list representation: graph[i] lists the 0-based indices of node i's
    neighbours (the statement's 1-based `val` minus one), for a simple,
    undirected, connected graph -- no self-loops, no repeated edges, the edges on
    both endpoints' lists. Those are the statement's own promises, translated.

    ACCEPTS any `got` that describes the same graph -- the same node count, and
    node i's neighbour SET equal to graph[i]'s -- while sharing no list object
    with the input, however the copy was built (BFS, DFS, or a rebuild of the
    lists). The neighbour SET rather than the list is deliberate: the statement
    calls an adjacency list "a collection of unordered lists", so a clone that
    appends a node's neighbours in a different order is correct, and an
    element-wise comparison (or a strict output digest in the probe) would fail
    it. The checker re-imposes the graph's well-formedness on both sides instead
    -- indices in range, no self-loops, no repeated edges -- so a "copy" that
    invents a duplicate or a self-loop fails even where the sets would match.

    REJECTS, in the order the checks run:
    - `args[0]` is not a well-formed simple connected undirected adjacency list.
      This is also the MUTATION check: the judge harness passes the argument list
      as it stands AFTER the call, so a solution that corrupts the input it was
      handed -- appends a neighbour, drops an edge, duplicates or invents an
      index, changes the node count -- fails here. Its blind spot is stated in
      the fragment's notes: a rewrite that leaves the input a valid simple
      connected graph, and that the returned copy then agrees with, is invisible
      to a checker that only ever sees the post-call arguments.
    - `got` is not itself a well-formed adjacency list of that same form;
    - `got` has a different node count, or some node's neighbour set differs --
      a partial copy, a copy of the wrong values, or a copy of the wrong graph;
    - `got is graph` -- returning the input is the degenerate "copy";
    - `got` shares ANY list object with the input: a new outer list over the
      input's own inner lists (the shallow copy) is structurally equal to the
      input and is caught only by this walk, exactly as deep_copy_valid catches
      it for the node-list form.

    The module argument is part of the predicate signature; this checker needs
    nothing from it, which is why tests/test_registry.py can exercise it on the
    oracle's own answer through its generic path."""
    if not isinstance(args, (list, tuple)) or not args:
        return False
    graph = args[0]

    def _well_formed(value) -> bool:
        """A simple, undirected, connected adjacency list of the corpus form."""
        if not isinstance(value, list):
            return False
        size = len(value)
        if size == 0:
            return True  # the statement's Example 3: an empty graph
        for node, entry in enumerate(value):
            if not isinstance(entry, list):
                return False
            for neighbour in entry:
                if not isinstance(neighbour, int) or isinstance(neighbour, bool):
                    return False
                if not 0 <= neighbour < size or neighbour == node:
                    return False
            if len(set(entry)) != len(entry):
                return False  # a repeated edge
        for node, entry in enumerate(value):
            for neighbour in entry:
                if node not in value[neighbour]:
                    return False  # not undirected: the edge is on one side only
        seen = [False] * size
        seen[0] = True
        frontier = [0]
        reached = 1
        while frontier:
            node = frontier.pop()
            for neighbour in value[node]:
                if not seen[neighbour]:
                    seen[neighbour] = True
                    reached += 1
                    frontier.append(neighbour)
        return reached == size  # the statement promises a connected graph

    def _list_objects(value, into: set) -> None:
        if isinstance(value, list):
            into.add(id(value))
            for item in value:
                _list_objects(item, into)

    if not _well_formed(graph):
        return False  # a solution that mutated the input it was given fails here
    if not _well_formed(got):
        return False
    if len(got) != len(graph):
        return False
    for copied, original in zip(got, graph):
        if set(copied) != set(original):
            return False
    if got is graph:
        return False

    original_objects = {id(graph)}
    for entry in graph:
        original_objects.add(id(entry))
    copied_objects: set = set()
    _list_objects(got, copied_objects)
    if original_objects & copied_objects:
        return False  # a shallow copy aliases part of the input
    return True


@measure("clone-graph")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    none."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'none'}
