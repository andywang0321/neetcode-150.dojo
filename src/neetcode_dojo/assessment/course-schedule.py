"""QUARANTINED assessment for `course-schedule` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("course-schedule")
def _course_schedule_oracle(num_courses: int, prerequisites: list[list[int]]) -> bool:
    """Brute force from the definition: a full schedule exists iff the
    prerequisite graph has no cycle, and a cycle exists iff some course can be
    reached from itself by following prerequisite edges. So walk the chain of
    prerequisites from every course in turn and report a cycle the moment a walk
    comes back to where it started -- no queue, no indegree array, no memo, and
    a different route to the answer than the reference's peeling.

    O(n * (n + p)) worst case. Total on num_courses <= 0 (nothing to take) and
    on an empty prerequisite list (the walk from every course is one step)."""
    if num_courses <= 0:
        return True
    needs: list[list[int]] = [[] for _ in range(num_courses)]
    for course, prereq in prerequisites:
        needs[course].append(prereq)
    for start in range(num_courses):
        seen = {start}
        stack = [start]
        while stack:
            node = stack.pop()
            for nxt in needs[node]:
                if nxt == start:
                    return False
                if nxt not in seen:
                    seen.add(nxt)
                    stack.append(nxt)
    return True


@cases("course-schedule")
def _course_schedule_case(n: int, rng: random.Random) -> tuple[list, bool]:
    # The statement's own 1 <= numCourses <= 2000 and 0 <= prerequisites.length;
    # the caller sends 0..12, so the floor matters. The families are BUILT rather
    # than drawn, because a uniform draw over pairs of courses almost never
    # produces the shapes this problem is about. Every edge points from a later
    # rank to an earlier one in a shuffled order, so a family is acyclic unless
    # it deliberately closes a cycle.
    num_courses = max(1, min(n, 12))
    order = list(range(num_courses))
    rng.shuffle(order)
    roll = rng.random()
    if roll < 0.12:
        prerequisites: list[list[int]] = []
    elif roll < 0.2 and num_courses >= 2:
        # A course that requires itself. NOTE: LC 207's constraint list says only
        # "0 <= ai, bi < numCourses" and "all pairs are unique" -- it does NOT
        # say ai != bi (LC 210's does), so this is a legal input here and it is a
        # one-course cycle.
        course = rng.randrange(num_courses)
        prerequisites = [[course, course]]
    elif roll < 0.6:
        # A sparse DAG: a random number of edges, each from a later rank to an
        # earlier one. Acyclic by construction, and -- unlike a chain -- it
        # leaves many courses free, so "which course may be taken first" is a
        # real choice rather than a forced one.
        pairs = set()
        if num_courses >= 2:
            for _ in range(rng.randint(0, 2 * num_courses)):
                later = rng.randrange(1, num_courses)
                earlier = rng.randrange(later)
                pairs.add((order[later], order[earlier]))
        prerequisites = [list(pair) for pair in sorted(pairs)]
    else:
        # A chain -- order[i] requires order[i - 1] -- so exactly one order is
        # valid, plus extra edges in the same direction, and (when roll lands in
        # the top band) the edge that closes the chain into a cycle. The closing
        # edge is a cycle only BECAUSE the chain's own edges already give a path
        # back from order[-1] to order[0] -- which is why it is added here and
        # not to the sparse family.
        prerequisites = [[order[i], order[i - 1]] for i in range(1, num_courses)]
        seen = {tuple(pair) for pair in prerequisites}
        if num_courses >= 2:
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
    return [num_courses, prerequisites], _course_schedule_oracle(num_courses, prerequisites)


@inputs("course-schedule")
def _course_schedule_profiler(n: int, rng: random.Random) -> list:
    # n courses in parallel prerequisite chains 200 long, every course requiring
    # the two before it (~2n pairs, inside 0 <= prerequisites.length <= 5000 and
    # with every pair distinct), all of it acyclic, built at exactly the size
    # asked for up to the statement's own 2000 courses -- which probe_max_n also
    # caps, so the ladder never claims a size the input did not build.
    #
    # Why chains and not a random DAG: an acyclic chain releases exactly one
    # course per round, so Kahn's algorithm peels the whole graph one course at a
    # time and cannot finish early, and the "rescan every course for one whose
    # prerequisites are done" shape that the oracle uses pays a full scan per
    # course -- the worst case for both sides. Why chains of 200 rather than one
    # chain of 2000: a single 2000-long chain would fail a CORRECT recursive DFS
    # (the canonical solution NeetCode teaches) with a RecursionError at the top
    # rungs, and the probe would report a failure at scale instead of a growth
    # verdict -- the trap house-robber's notes record for CPython's stack. Depth
    # 200 leaves the intended recursive solution plenty of room while keeping the
    # graph's dependency structure non-trivial.
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


@reference("course-schedule")
def _course_schedule_reference(num_courses: int, prerequisites: list[list[int]]) -> bool:
    """Kahn's algorithm: peel the courses whose prerequisites are all taken,
    releasing the courses that waited on them. If every course comes off, the
    graph is acyclic; if courses are left with unmet prerequisites, those wait on
    each other in a cycle. O(n + p) time and O(n + p) space (the reverse edges
    and the queue), standalone -- no imports, one top-level function."""
    unlocks: list[list[int]] = [[] for _ in range(max(0, num_courses))]
    waiting = [0] * len(unlocks)
    for course, prereq in prerequisites:
        if 0 <= course < len(unlocks) and 0 <= prereq < len(unlocks):
            unlocks[prereq].append(course)
            waiting[course] += 1
    queue = [course for course in range(len(unlocks)) if waiting[course] == 0]
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
    return taken == len(unlocks)


@measure("course-schedule")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
