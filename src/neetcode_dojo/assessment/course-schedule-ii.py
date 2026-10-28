"""QUARANTINED assessment for `course-schedule-ii` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, checker, inputs, measure, oracle, reference


@oracle("course-schedule-ii")
def _course_schedule_ii_oracle(num_courses: int, prerequisites: list[list[int]]) -> list[int]:
    """Brute force from the definition: at every step, ANY course whose
    prerequisites have all been taken may be taken next, so take the
    lowest-numbered one and repeat. If a round finds no such course while
    courses remain, the rest wait on each other in a cycle and the answer is [].

    O(n^2 + n * p) -- no queue, no indegree array, no memo. The tie-break here is
    only ever a display value: the valid_topological_order checker accepts any
    order that respects the edges, and it is deliberately NOT written in terms of
    this choice. Total on num_courses <= 0 and on an empty prerequisite list."""
    size = max(0, num_courses)
    needs: list[list[int]] = [[] for _ in range(size)]
    for course, prereq in prerequisites:
        needs[course].append(prereq)
    taken = [False] * size
    order: list[int] = []
    for _ in range(size):
        chosen = -1
        for course in range(size):
            if not taken[course] and all(taken[prereq] for prereq in needs[course]):
                chosen = course
                break
        if chosen == -1:
            return []
        taken[chosen] = True
        order.append(chosen)
    return order


@cases("course-schedule-ii")
def _course_schedule_ii_case(n: int, rng: random.Random) -> tuple[list, list, dict]:
    # The statement's own 1 <= numCourses <= 2000 and 0 <= prerequisites.length;
    # the caller sends 0..12, so the floor matters. The families are built for
    # the same reason as LC 207's, with one difference that matters here: LC 210
    # states ai != bi, so a self-pair is NOT a legal input and no family may emit
    # one -- and with a single course there is therefore no legal cycle at all,
    # which is why n = 1 is always the empty prerequisite list. Every case
    # carries the predicate tag, so the judge accepts any valid order rather than
    # the oracle's.
    num_courses = max(1, min(n, 12))
    order = list(range(num_courses))
    rng.shuffle(order)
    roll = rng.random()
    if num_courses == 1 or roll < 0.1:
        prerequisites: list[list[int]] = []
    elif roll < 0.6:
        # A sparse DAG: a random number of edges, each from a later rank to an
        # earlier one. Acyclic by construction and, crucially for this problem,
        # NOT order-forcing: with few edges many permutations are valid, so the
        # oracle's order and the reference's order really do differ and the
        # predicate checker is exercised on genuine alternatives.
        pairs = set()
        for _ in range(rng.randint(0, 2 * num_courses)):
            later = rng.randrange(1, num_courses)
            earlier = rng.randrange(later)
            pairs.add((order[later], order[earlier]))
        prerequisites = [list(pair) for pair in sorted(pairs)]
    else:
        # A chain -- order[i] requires order[i - 1] -- where exactly one order is
        # valid, and (in the top band) the edge that closes it into a cycle, so
        # the "return an empty array" branch is reached by construction.
        prerequisites = [[order[i], order[i - 1]] for i in range(1, num_courses)]
        seen = {tuple(pair) for pair in prerequisites}
        for _ in range(num_courses):
            later = rng.randrange(1, num_courses)
            earlier = rng.randrange(later)
            pair = (order[later], order[earlier])
            if pair not in seen:
                seen.add(pair)
                prerequisites.append(list(pair))
        if roll < 0.8:
            closing = [order[0], order[-1]]
            if tuple(closing) not in seen:
                prerequisites.append(closing)
    return (
        [num_courses, prerequisites],
        _course_schedule_ii_oracle(num_courses, prerequisites),
        {"predicate": "valid_topological_order"},
    )


@inputs("course-schedule-ii")
def _course_schedule_ii_profiler(n: int, rng: random.Random) -> list:
    # The same shape as LC 207's input and for the same reasons (see that
    # fragment's notes): n courses as parallel 200-deep chains, each course
    # requiring the two before it, ~2n distinct pairs inside the statement's
    # 0 <= prerequisites.length <= n * (n - 1) and ai != bi, all acyclic, built
    # at exactly the size asked for up to the statement's own 2000 courses.
    #
    # The chains release one course per round, so Kahn's peeling cannot finish
    # early, and the "rescan every course" shape pays a full scan per course.
    # Depth 200 is deliberate: a single size-long chain would blow CPython's
    # stack for the canonical recursive DFS, which the probe would report as a
    # failure at scale rather than as a growth verdict. The output digest is not
    # a correctness signal here (scale_compare is "none": two valid orders are
    # different lists), so the input's job is purely to make the cost model real.
    size = max(1, min(n, 2000))
    depth = 200
    prerequisites: list[list[int]] = []
    for start in range(0, size, depth):
        chain = list(range(start, min(start + depth, size)))
        for k in range(1, len(chain)):
            prerequisites.append([chain[k], chain[k - 1]])
            if k >= 2:
                prerequisites.append([chain[k], chain[k - 2]])
    return [size, prerequisites]


@reference("course-schedule-ii")
def _course_schedule_ii_reference(
    num_courses: int, prerequisites: list[list[int]]
) -> list[int]:
    """Kahn's algorithm: peel the courses whose prerequisites are all taken and
    release the courses that waited on them. Every course that comes off goes
    into the order; if any course is still waiting at the end, those courses
    depend on each other in a cycle and the answer is [].

    O(n + p) time and O(n + p) space (the reverse edges and the queue),
    standalone -- no imports, one top-level function, so the probe's subprocess
    can run it as it stands. The LIFO order among simultaneously available
    courses is arbitrary, which is exactly what the checker is built to accept:
    for the statement's example 2 this returns [0,2,1,3], the order the statement
    prints, while the oracle returns [0,1,2,3] -- both are correct answers."""
    size = max(0, num_courses)
    unlocks: list[list[int]] = [[] for _ in range(size)]
    waiting = [0] * size
    for course, prereq in prerequisites:
        if 0 <= course < size and 0 <= prereq < size:
            unlocks[prereq].append(course)
            waiting[course] += 1
    stack = [course for course in range(size - 1, -1, -1) if waiting[course] == 0]
    order: list[int] = []
    while stack:
        course = stack.pop()
        order.append(course)
        for released in unlocks[course]:
            waiting[released] -= 1
            if waiting[released] == 0:
                stack.append(released)
    return order if len(order) == size else []


@checker("valid_topological_order")
def _course_schedule_ii_valid_order(module, got, args) -> bool:
    """The contract as a property, because the answer is NOT unique.

    The statement says "If there are many valid answers, return any of them", so
    the checker validates exactly what is asked for -- got is a permutation of
    0..n-1 in which every prerequisite b comes before the course a that needs it
    -- and nothing else. It never recomputes the oracle's (or the reference's)
    choice among the valid orders: for the statement's own example 2 the oracle
    answers [0,1,2,3] and the reference answers [0,2,1,3], and both must pass.
    Equality judging here would false-fail a correct solution that picked another
    valid order (the k_closest_points trust bug, v0.12).

    An empty answer is accepted exactly when no order exists -- that is the
    statement's other branch, and it is decided by re-deriving schedulability,
    not by asking whether some particular order was produced."""
    num_courses, prerequisites = args
    if not isinstance(got, list):
        return False
    if any(not isinstance(course, int) or isinstance(course, bool) for course in got):
        return False
    if len(got) == num_courses and sorted(got) == list(range(num_courses)):
        position = {course: index for index, course in enumerate(got)}
        return all(
            position[prereq] < position[course] for course, prereq in prerequisites
        )
    return got == [] and not _course_schedule_ii_schedulable(num_courses, prerequisites)


def _course_schedule_ii_schedulable(
    num_courses: int, prerequisites: list[list[int]]
) -> bool:
    """Is there any full order at all? Indegree peeling, used ONLY to decide
    whether the empty answer is the right one -- the order it happens to produce
    is never compared with anything."""
    if num_courses <= 0:
        return True
    waiting = [0] * num_courses
    unlocks: list[list[int]] = [[] for _ in range(num_courses)]
    for course, prereq in prerequisites:
        waiting[course] += 1
        unlocks[prereq].append(course)
    queue = [course for course in range(num_courses) if waiting[course] == 0]
    head = 0
    taken = 0
    while head < len(queue):
        course = queue[head]
        head += 1
        taken += 1
        for released in unlocks[course]:
            waiting[released] -= 1
            if waiting[released] == 0:
                queue.append(released)
    return taken == num_courses


@measure("course-schedule-ii")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    none."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'none'}
