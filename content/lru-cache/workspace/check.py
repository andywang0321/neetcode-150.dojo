"""Visible checks for `lru-cache` — the student runs these.

Shipped to the student and rendered into their workbench, so they check the
statement's promises and nothing more. The verdict that counts comes from the
oracle and its generated cases, which are quarantined in `assessment/`.
"""

CASES = [
    {'ops': [['__init__', 2], ['put', 1, 1], ['put', 2, 2], ['get', 1], ['put', 3, 3],
             ['get', 2], ['put', 4, 4], ['get', 1], ['get', 3], ['get', 4]],
     'ctor_args': [2],
     'expected': [None, None, None, 1, None, -1, None, -1, 3, 4]},
    {'ops': [['__init__', 1], ['put', 0, 0], ['get', 0], ['put', 1, 0], ['get', 0], ['get', 1],
             ['put', 1, 7], ['get', 1]],
     'ctor_args': [1],
     'expected': [None, None, 0, None, -1, 0, None, 7]},
    {'ops': [['__init__', 2], ['put', 1, 1], ['put', 2, 2], ['put', 1, 10], ['put', 3, 3],
             ['get', 2], ['get', 1], ['get', 3]],
     'ctor_args': [2],
     'expected': [None, None, None, None, None, -1, 10, 3]},
]


def check() -> None:
    import importlib.util
    from pathlib import Path

    _path = Path(__file__).with_name("solution.py")
    _spec = importlib.util.spec_from_file_location("artifact", _path)
    artifact = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(artifact)
    LRUCache = artifact.LRUCache

    for number, case in enumerate(CASES, 1):
        obj = LRUCache(*case.get("ctor_args", []))
        got = []
        for op in case["ops"]:
            method, *args = op
            got.append(getattr(obj, method)(*args))
        assert got == case["expected"], (
            f"case {number}: got {got!r}, want {case['expected']!r}"
        )
    print(f"all {len(CASES)} visible checks passed")


if __name__ == "__main__":
    check()
