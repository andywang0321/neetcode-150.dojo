"""QUARANTINED assessment for `reconstruct-itinerary` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


def _reconstruct_itinerary_airports(rng: random.Random, count: int) -> list[str]:
    """`count` distinct three-letter uppercase airport names, never "JFK" (the
    statement's own departure airport, and the search's fixed start)."""
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    names: set[str] = set()
    while len(names) < count:
        name = "".join(rng.choice(letters) for _ in range(3))
        if name != "JFK":
            names.add(name)
    return sorted(names)


def _reconstruct_itinerary_stop(prefix: str, index: int) -> str:
    """A three-letter uppercase airport name: `prefix` plus `index` in two
    base-26 letters ("A" + "AA" = "AAA"). Increasing in `index`, which is the
    order the profiler's excursions rely on."""
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return prefix + letters[index // 26] + letters[index % 26]


@oracle("reconstruct-itinerary")
def _reconstruct_itinerary_oracle(tickets: list[list[str]]) -> list[str]:
    """Brute force: depth-first search from "JFK" that tries the destinations
    available at the current airport in lexical order and returns the first
    itinerary that has used EVERY ticket. The lexical order IS the statement's
    tie-break ("the itinerary that has the smallest lexical order when read as a
    single string"): the first complete path this search finds is that itinerary,
    so nothing ever compares two candidate itineraries.

    Each ticket is tracked by its own index, not by its (from, to) pair, so two
    identical tickets are two distinct edges and are consumed one at a time.

    Total on everything the generator can produce and on the shapes it cannot: no
    tickets gives ["JFK"] (the zero-length walk from the start), and a ticket set
    no walk can consume whole gives [] -- the sentinel for "no such itinerary",
    which the statement's promise ("all tickets form at least one valid
    itinerary") excludes and which the reference mirrors.

    Exponential in the worst case -- a graph whose early destinations dead-end
    makes the search retry -- and that is why the profiler input is built so the
    lexical-first walk completes: this anchor runs on that input too."""
    by_source: dict[str, list[int]] = {}
    for index, ticket in enumerate(tickets):
        by_source.setdefault(ticket[0], []).append(index)
    for indices in by_source.values():
        indices.sort(key=lambda i: (tickets[i][1], i))
    used = [False] * len(tickets)
    path = ["JFK"]

    def walk() -> bool:
        if len(path) == len(tickets) + 1:
            return True
        for index in by_source.get(path[-1], ()):
            if used[index]:
                continue
            used[index] = True
            path.append(tickets[index][1])
            if walk():
                return True
            path.pop()
            used[index] = False
        return False

    return path if walk() else []


@cases("reconstruct-itinerary")
def _reconstruct_itinerary_case(n: int, rng: random.Random) -> tuple[list, list[str]]:
    """A random WALK over a small pool of airports, turned into tickets: the walk
    is itself an itinerary through all of them, so the statement's promise ("all
    tickets form at least one valid itinerary") holds by construction and
    `expected` is the oracle's own answer.

    Inside the statement's constraints: 1..12 tickets (<= 300), every airport
    three uppercase letters, from != to (the walk never stays put). The pool is
    smaller than the walk, so airports repeat and the tickets carry branches,
    cycles and reused airports -- and an identical ticket pair can appear twice,
    which the statement allows: it never promises the tickets are distinct, unlike
    its neighbours in the corpus that spell out "no multiple edges"."""
    n = max(1, min(n, 12))  # the statement's own range: 1 <= tickets.length <= 300
    pool = _reconstruct_itinerary_airports(rng, min(n + 1, 7))
    walk = ["JFK"]
    for _ in range(n):
        walk.append(rng.choice([name for name in pool if name != walk[-1]]))
    tickets = [[walk[i], walk[i + 1]] for i in range(n)]
    rng.shuffle(tickets)
    return [tickets], _reconstruct_itinerary_oracle(tickets)


@inputs("reconstruct-itinerary")
def _reconstruct_itinerary_profiler(n: int, rng: random.Random) -> list:
    """Excursions out of "JFK" that each come back to it: JFK -> A_xx -> B_xx ->
    JFK, three tickets apiece, with the final excursion shortened by the
    remainder so the total is exactly n.

    No early exit is available to either side: an itinerary may not stop while
    tickets are left, so all n tickets are consumed, and JFK carries one out-edge
    per excursion (up to 100 destinations), which is where the reference's sort
    lives.

    The naming is what keeps the ORACLE tractable, and it is deliberate: the
    excursions' first stops grow with the excursion's index ("AAA", "AAB", ...)
    and each excursion returns to JFK, so the lexical-first walk takes them in
    turn and completes without backtracking; the shortened excursion has the
    largest index, so it is tried last and its dead end is the walk's own end
    rather than a detour the search has to undo. A dead-end-rich shape would make
    the oracle's exponential worst case real at n=300, and the oracle runs on this
    input too (the probe smoke's differential and `flow._oracle_confirms`).

    Inside the statement's constraints: n <= 300 tickets, three-letter uppercase
    airports, from != to (JFK vs A.., A.. vs B.., B.. vs JFK)."""
    n = max(1, min(n, 300))  # the statement's own cap: 1 <= tickets.length <= 300
    tickets: list[list[str]] = []
    remaining = n
    index = 0
    while remaining > 0:
        length = min(3, remaining)
        first = _reconstruct_itinerary_stop("A", index)
        second = _reconstruct_itinerary_stop("B", index)
        tickets.append(["JFK", first])
        if length >= 2:
            tickets.append([first, second])
        if length >= 3:
            tickets.append([second, "JFK"])
        remaining -= length
        index += 1
    return [tickets]


@reference("reconstruct-itinerary")
def _reconstruct_itinerary_reference(tickets: list[list[str]]) -> list[str]:
    """Canonical Hierholzer: sort every airport's destinations, then walk the
    graph taking the smallest destination still available and appending an airport
    to the route only once it has no destination left. Reversing that route is an
    Eulerian path over every ticket -- each ticket is a multigraph edge and is
    popped exactly once -- and because every step takes the SMALLEST remaining
    destination the path is the smallest in lexical order, which is the
    statement's tie-break obtained by the algorithm instead of by comparing
    candidate itineraries.

    O(n log n) time (one sort of the n destinations plus one visit per ticket) and
    O(n) space (the destination lists and the two stacks).

    Total on the shapes the statement excludes: no tickets gives ["JFK"], and a
    ticket set no walk can consume whole gives [] -- the length check below is
    what keeps that in step with the oracle, and it can only fire on inputs that
    violate the statement's "at least one valid itinerary" promise."""
    destinations: dict[str, list[str]] = {}
    for ticket in tickets:
        destinations.setdefault(ticket[0], []).append(ticket[1])
    for outgoing in destinations.values():
        outgoing.sort(reverse=True)  # so pop() yields the smallest destination
    stack = ["JFK"]
    route: list[str] = []
    while stack:
        outgoing = destinations.get(stack[-1])
        if outgoing:
            stack.append(outgoing.pop())
        else:
            route.append(stack.pop())
    route.reverse()
    if len(route) != len(tickets) + 1:
        return []
    return route


@measure("reconstruct-itinerary")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
