"""QUARANTINED assessment for `lru-cache` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, oracle, reference


@oracle("lru-cache")
def _lru_cache_oracle(ops: list[list]) -> list:
    """Brute force: the recency order is a plain list that is scanned and spliced
    in full on every access — O(capacity) per op instead of the intended O(1) —
    driven by the same op list the class problems use. The capacity arrives as the
    leading ["__init__", capacity] op; a get or put before it is an error rather
    than a silent default (see the fragment notes for why the constructor travels
    inside the op list)."""
    capacity = None
    values: dict[int, int] = {}
    recency: list[int] = []  # least recently used first, most recently used last
    out: list = []
    for op in ops:
        method, *args = op
        if method == "__init__":
            capacity = args[0]
            values = {}
            recency = []
            out.append(None)
        elif method == "get":
            if capacity is None:
                raise ValueError('the op list must start with ["__init__", capacity]')
            key = args[0]
            if key not in values:
                out.append(-1)
            else:
                recency.remove(key)
                recency.append(key)
                out.append(values[key])
        elif method == "put":
            if capacity is None:
                raise ValueError('the op list must start with ["__init__", capacity]')
            key, value = args
            if key in values:
                recency.remove(key)
            values[key] = value
            recency.append(key)
            if len(values) > capacity:
                oldest = recency.pop(0)
                del values[oldest]
            out.append(None)
        else:  # pragma: no cover - the generator only emits the three methods
            raise ValueError(f"unknown op {method}")
    return out


@cases("lru-cache")
def _lru_cache_case(n: int, rng: random.Random) -> tuple[list, list, dict]:
    # Deterministic by construction: every op comes from the seeded rng, the op
    # sequence never depends on what the cache answers, and each case replays on a
    # fresh instance (the harness builds one per case from ctor_args, and the
    # drivers rebuild their state on the __init__ op). Constraints honoured:
    # 1 <= capacity <= 3000 (kept at 1..3 so eviction happens constantly),
    # 0 <= key <= 10^4 (a pool of 0..3, so updates and evictions are common), and
    # 0 <= value <= 10^5 — the first put always stores 0, because a falsy value is
    # what catches `if not self.cache[key]` treating a stored 0 as a miss.
    n = max(1, min(n, 12))
    capacity = rng.randint(1, 3)
    key_pool = list(range(rng.randint(1, 4)))
    ops: list[list] = [["__init__", capacity]]
    for step in range(2 * n):
        key = rng.choice(key_pool)
        if step % 4 == 3:
            ops.append(["get", key])
        else:
            ops.append(["put", key, 0 if step == 0 else rng.randint(0, 20)])
    return [], _lru_cache_oracle(ops), {"ops": ops, "ctor_args": [capacity]}


@reference("lru-cache")
def _lru_cache_reference(ops: list[list]) -> list:
    """The intended design, driven through the same op list the oracle takes: a
    dict key -> node plus an intrusive doubly linked list in recency order with a
    sentinel at each end — O(1) per get and per put, O(capacity) nodes. The
    capacity arrives as the leading ["__init__", capacity] op, because the judge's
    convention for a class problem hands the reference the op list and nothing
    else; the op rebuilds the cache, so every case runs on fresh state."""
    head: list = []  # sentinel at the LRU end: its [next] is the eviction victim
    tail: list = []  # sentinel at the MRU end: its [prev] is the newest node
    nodes: dict[int, list] = {}
    capacity: int | None = None

    def _lru_cache_unlink(node: list) -> None:
        node[2][3] = node[3]
        node[3][2] = node[2]

    def _lru_cache_move_to_mru(node: list) -> None:
        _lru_cache_unlink(node)
        newest = tail[2]
        newest[3] = node
        node[2] = newest
        node[3] = tail
        tail[2] = node

    out: list = []
    for op in ops:
        method, *args = op
        if method == "__init__":
            capacity = args[0]
            head = [None, None, None, None]
            tail = [None, None, None, None]
            head[3] = tail
            tail[2] = head
            nodes = {}
            out.append(None)
        elif method == "get":
            if capacity is None:
                raise ValueError('the op list must start with ["__init__", capacity]')
            node = nodes.get(args[0])
            if node is None:
                out.append(-1)
            else:
                _lru_cache_move_to_mru(node)
                out.append(node[1])
        elif method == "put":
            if capacity is None:
                raise ValueError('the op list must start with ["__init__", capacity]')
            key, value = args
            node = nodes.get(key)
            if node is not None:
                node[1] = value  # an update also makes the key most recent
                _lru_cache_move_to_mru(node)
            else:
                if len(nodes) >= capacity:
                    victim = head[3]
                    _lru_cache_unlink(victim)
                    del nodes[victim[0]]
                node = [key, value, None, None]
                nodes[key] = node
                newest = tail[2]
                newest[3] = node
                node[2] = newest
                node[3] = tail
                tail[2] = node
            out.append(None)
        else:  # pragma: no cover - the generator only emits the three methods
            raise ValueError(f"unknown op {method}")
    return out
