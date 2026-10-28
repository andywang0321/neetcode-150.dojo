"""QUARANTINED assessment for `time-based-key-value-store` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, oracle, reference


@oracle("time-based-key-value-store")
def _time_based_key_value_store_oracle(ops: list[list]) -> list:
    """Brute force: keep every (timestamp, value) for a key and scan them all on
    a get, taking the latest timestamp that is <= the query."""
    store: dict[str, list[list]] = {}
    out: list = []
    for op in ops:
        method, *args = op
        if method == "set":
            key, value, timestamp = args
            store.setdefault(key, []).append([timestamp, value])
            out.append(None)
        elif method == "get":
            key, timestamp = args
            latest_stamp = None
            latest_value = ""
            for stamp, value in store.get(key, []):
                if stamp <= timestamp and (latest_stamp is None or stamp > latest_stamp):
                    latest_stamp, latest_value = stamp, value
            out.append(latest_value)
        else:  # pragma: no cover - the generator only emits set and get
            raise ValueError(f"unknown op {method}")
    return out


@cases("time-based-key-value-store")
def _time_based_key_value_store_case(n: int, rng: random.Random) -> tuple[list, list, dict]:
    # Deterministic by construction: every op comes from the seeded rng, the
    # timestamps are a strictly increasing counter (the statement's own
    # guarantee), and the key pool is fixed, so the same (n, rng) always
    # replays the same sequence on a fresh instance.
    steps = 2 * max(1, min(n, 12)) + 1
    written = ("k0", "k1", "k2")  # keys that get writes
    keys = written + ("k3",)  # k3 is never written: get on it must answer ""
    ops: list[list] = []
    stamp = 0
    for step in range(steps):
        key = rng.choice(keys if step % 2 else written)
        if step % 2 == 0:  # a set: the timestamp only ever moves forward
            stamp += rng.randint(1, 4)
            value = "".join(
                rng.choice("abcdefghijklmnopqrstuvwxyz0123456789")
                for _ in range(rng.randint(1, 3))
            )
            ops.append(["set", key, value, stamp])
        else:  # a get: at, just before, or just after the newest timestamp
            asked = max(1, stamp + rng.choice([-1, 0, 0, 1, 2]))
            ops.append(["get", key, asked])
    return [], _time_based_key_value_store_oracle(ops), {"ops": ops}


@reference("time-based-key-value-store")
def _time_based_key_value_store_reference(ops: list[list]) -> list:
    """Canonical TimeMap, driven through the same op list the oracle takes:
    one growing list of (timestamp, value) per key (appended in the statement's
    strictly increasing timestamp order) and a binary search for the latest set
    at or before the query — O(1) per set, O(log n) per get, O(n) space."""
    store: dict[str, list[tuple[int, str]]] = {}
    out: list = []
    for op in ops:
        method, *args = op
        if method == "set":
            key, value, timestamp = args
            store.setdefault(key, []).append((timestamp, value))
            out.append(None)
        elif method == "get":
            key, timestamp = args
            entries = store.get(key)
            if not entries:
                out.append("")
                continue
            lo, hi = 0, len(entries) - 1
            found = -1  # index of the latest timestamp <= the query
            while lo <= hi:
                mid = (lo + hi) // 2
                if entries[mid][0] <= timestamp:
                    found = mid
                    lo = mid + 1
                else:
                    hi = mid - 1
            out.append(entries[found][1] if found >= 0 else "")
        else:  # pragma: no cover - the generator only emits set and get
            raise ValueError(f"unknown op {method}")
    return out
