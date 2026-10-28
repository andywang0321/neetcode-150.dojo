"""QUARANTINED assessment for `detect-squares` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, oracle, reference


_DETECT_SQUARES_SPAN = 5


_DETECT_SQUARES_SPAN = 5


def _detect_squares_forms_square(quad: list[list]) -> bool:
    """Four points form an axis-aligned square of positive area exactly when
    they use two distinct x values and two distinct y values, the two spans are
    equal, and all four corners (x, y) are present. That is the definition of
    the shape, stated as a membership test - there is no distance or diagonal
    arithmetic here to get wrong."""
    xs = sorted({point[0] for point in quad})
    ys = sorted({point[1] for point in quad})
    if len(xs) != 2 or len(ys) != 2:
        return False
    if xs[1] - xs[0] != ys[1] - ys[0]:
        return False
    present = {(point[0], point[1]) for point in quad}
    return all((x, y) in present for x in xs for y in ys)


@oracle("detect-squares")
def _detect_squares_oracle(ops: list[list]) -> list:
    """Brute force: every added point is kept as its own list entry - which is
    what makes the statement's 'duplicate points should be treated as different
    points' literal - and a count tries every triple of stored entries against
    the query point, testing the four points directly."""
    points: list[list] = []
    out: list = []
    for op in ops:
        method, *args = op
        if method == 'add':
            points.append(list(args[0]))
            out.append(None)
        elif method == 'count':
            x, y = args[0]
            total = 0
            size = len(points)
            for i in range(size):
                for j in range(i + 1, size):
                    for k in range(j + 1, size):
                        quad = [points[i], points[j], points[k], [x, y]]
                        if _detect_squares_forms_square(quad):
                            total += 1
            out.append(total)
        else:  # pragma: no cover - the generator only emits add and count
            raise ValueError(f'unknown op {method}')
    return out


@cases("detect-squares")
def _detect_squares_case(n: int, rng: random.Random) -> tuple[list, list, dict]:
    # Deterministic by construction: every op comes from the seeded rng, the
    # coordinate pool is fixed, and the harness builds a fresh instance per case,
    # so the same (n, rng) always replays the same stream on an empty structure.
    # The first two ops are adds (a count is never the whole case) and the rest
    # alternate, so both methods and the duplicate-add path are exercised.
    steps = 2 * max(1, min(n, 12)) + 1
    ops: list[list] = []
    for step in range(steps):
        point = [rng.randrange(_DETECT_SQUARES_SPAN), rng.randrange(_DETECT_SQUARES_SPAN)]
        if step >= 2 and step % 2 == 0:
            ops.append(['count', point])
        else:
            ops.append(['add', point])
    return [], _detect_squares_oracle(ops), {'ops': ops}


@reference("detect-squares")
def _detect_squares_reference(ops: list[list]) -> list:
    """Canonical design, driven through the same op list the oracle takes: a
    multiplicity map keyed by (x, y) for the adds, and a count that walks the
    distinct points stored, taking every point that shares the query's diagonal
    (|dx| == |dy| != 0) as the OPPOSITE corner of a square. The other two corners
    are then (px, qy) and (qx, py), so the product of the three multiplicities
    counts every way to choose the three points at once. O(1) per add, at most
    one pass over the distinct points per count, O(n) space."""
    counts: dict[tuple[int, int], int] = {}
    out: list = []
    for op in ops:
        method, *args = op
        if method == 'add':
            x, y = args[0]
            counts[(x, y)] = counts.get((x, y), 0) + 1
            out.append(None)
        elif method == 'count':
            qx, qy = args[0]
            total = 0
            for (px, py), multiplicity in counts.items():
                if px != qx and abs(px - qx) == abs(py - qy):
                    total += multiplicity * counts.get((px, qy), 0) * counts.get((qx, py), 0)
            out.append(total)
        else:  # pragma: no cover - the generator only emits add and count
            raise ValueError(f'unknown op {method}')
    return out
