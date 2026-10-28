"""Visible checks for `time-based-key-value-store` — the student runs these.

Shipped to the student and rendered into their workbench, so they check the
statement's promises and nothing more. The verdict that counts comes from the
oracle and its generated cases, which are quarantined in `assessment/`.
"""

CASES = [
    {'ops': [['set', 'foo', 'bar', 1], ['get', 'foo', 1], ['get', 'foo', 3],
             ['set', 'foo', 'bar2', 4], ['get', 'foo', 4], ['get', 'foo', 5]],
     'expected': [None, 'bar', 'bar', None, 'bar2', 'bar2']},
    {'ops': [['get', 'foo', 1], ['set', 'foo', 'a', 2], ['get', 'foo', 1], ['get', 'bar', 5]],
     'expected': ['', None, '', '']},
    {'ops': [['set', 'k1', 'v1', 1], ['set', 'k2', 'v2', 2], ['set', 'k1', 'v3', 3],
             ['get', 'k1', 2], ['get', 'k1', 3], ['get', 'k2', 3]],
     'expected': [None, None, None, 'v1', 'v3', 'v2']},
]


def check() -> None:
    import importlib.util
    from pathlib import Path

    _path = Path(__file__).with_name("solution.py")
    _spec = importlib.util.spec_from_file_location("artifact", _path)
    artifact = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(artifact)
    TimeMap = artifact.TimeMap

    for number, case in enumerate(CASES, 1):
        obj = TimeMap(*case.get("ctor_args", []))
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
