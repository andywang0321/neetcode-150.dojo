"""QUARANTINED assessment for `task-scheduler` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("task-scheduler")
def _task_scheduler_oracle(tasks: list[str], n: int) -> int:
    """The closed form, and the anchor for every expected value. With f the
    largest number of copies of any one label and c the number of labels reaching
    f: those c labels force (f - 1) blocks of n intervals after each of their
    first f - 1 copies, i.e. (f - 1) * (n + 1) + c intervals, and when the other
    labels are numerous enough to fill every one of those gaps the answer is
    simply len(tasks) — hence the max(). One pass over the tasks: O(m) time and
    O(1) space. Verified against an exhaustive shortest-schedule search and
    against the simulation reference; see the notes.
    """
    counts: dict[str, int] = {}
    for label in tasks:
        counts[label] = counts.get(label, 0) + 1
    if not counts:
        return 0
    most = max(counts.values())
    tied = sum(1 for count in counts.values() if count == most)
    return max(len(tasks), (most - 1) * (n + 1) + tied)


@cases("task-scheduler")
def _task_scheduler_case(n: int, rng: random.Random) -> tuple[list, int]:
    total = max(1, min(n, 12))  # the statement's own constraint: 1 <= tasks.length
    kinds = rng.randint(1, min(total, 6))
    labels = rng.sample("ABCDEFGHIJKLMNOPQRSTUVWXYZ", kinds)
    counts = [1] * kinds
    for _ in range(total - kinds):
        counts[rng.randrange(kinds)] += 1
    tasks = [label for label, count in zip(labels, counts) for _ in range(count)]
    rng.shuffle(tasks)
    # 0 is the statement's floor and the one value with no gap to respect (the
    # answer is then simply len(tasks)); a large cooldown is where the max()
    # clamp and the idle counting actually decide the answer.
    cooldown = rng.choice([0, 0, 1, 2, 3, rng.randint(0, 100)])
    return [tasks, cooldown], _task_scheduler_oracle(tasks, cooldown)


@inputs("task-scheduler")
def _task_scheduler_profiler(n: int, rng: random.Random) -> list:
    # All 26 labels, as evenly as the count allows, at the statement's maximum
    # cooldown (100). The cooldown — not the task count — sets the schedule's
    # length, so the answer is about 3.9 * n intervals (~74% of them idle) and a
    # simulation pays for every one of them, while a closed-form solution still
    # has to read all n tasks. The answer is far from len(tasks), so a solution
    # that forgets the idles is caught by the digest comparison as well. The
    # shape is deliberately bounded rather than maximally idle (a single label at
    # n = 100 would be ~101 * n intervals), because a correct but naive
    # simulation (a 26-counter scan per interval, with tracemalloc on for the
    # space call) would then approach the probe's 20 s per-call timeout and be
    # reported as "failed at scale" — an unfair verdict for code that is merely
    # slower.
    size = max(1, n)
    tasks = [chr(ord("A") + i) for i in range(26) for _ in range(size // 26)]
    for i in range(size % 26):
        tasks.append(chr(ord("A") + i))
    rng.shuffle(tasks)
    return [tasks, 100]


@reference("task-scheduler")
def _task_scheduler_reference(tasks: list[str], n: int) -> int:
    """The interval-by-interval simulation a student writes, over fixed 26-slot
    arrays: remaining[i] counts label i's copies left, ready[i] is how many more
    intervals label i must wait (0 = runnable now, and running it sets it to n).
    Each interval runs the runnable label with the most copies left, or idles
    when every label is still cooling, and intervals are counted until nothing is
    left. O(answer * 26) = O(m) time (answer <= 101 * len(tasks)) and O(1) space —
    the same class as the closed form, which is the point: it is deliberately the
    heavy baseline, not the fast one. The closed form is ~15-300x quicker in
    constant terms, and a comparison across the probe's 100..6400 ladder cannot
    cancel a gap that large — the faster side's fixed cost dominates its own time
    at n = 100, the ratio drifts ~2x, and a correct simulation gets named one
    class slower. Measured, not theorized: with the closed form as the baseline a
    correct heap simulation read 9.16x at n = 100 rising to 18.11x at n = 6400.
    Against this baseline every honest implementation reads flat (heap simulation
    ~0.06x, array or dict scan ~1x, both across the ladder), and when machine
    noise does bite it errs toward "unresolved" rather than toward blaming the
    student. The closed form is not lost by the swap — it is the oracle, so the
    gate re-checks this simulation against it on every case, forever.
    """
    remaining = [0] * 26
    for label in tasks:
        index = ord(label) - 65  # "A".."Z", the statement's own constraint
        if not 0 <= index < 26:
            raise ValueError(f"unexpected task label {label!r}")
        remaining[index] += 1
    ready = [0] * 26
    left = len(tasks)
    intervals = 0
    while left:
        intervals += 1
        pick = -1
        best = 0
        for i in range(26):
            count = remaining[i]
            if count and ready[i] == 0 and count > best:
                pick, best = i, count
        for i in range(26):
            if i != pick and ready[i] > 0:
                ready[i] -= 1
        if pick >= 0:
            remaining[pick] -= 1
            left -= 1
            ready[pick] = n if remaining[pick] else 0
    return intervals


@measure("task-scheduler")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
