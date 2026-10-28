"""Visible checks for `detect-squares` — the student runs these.

Shipped to the student and rendered into their workbench, so they check the
statement's promises and nothing more. The verdict that counts comes from the
oracle and its generated cases, which are quarantined in `assessment/`.
"""

CASES = [
    {'ops': [['add', [3, 10]], ['add', [11, 2]], ['add', [3, 2]], ['count', [11, 10]],
             ['count', [14, 8]], ['add', [11, 2]], ['count', [11, 10]]],
     'expected': [None, None, None, 1, 0, None, 2]},
    {'ops': [['add', [0, 0]], ['add', [2, 0]], ['add', [0, 3]], ['count', [2, 3]]],
     'expected': [None, None, None, 0]},
    {'ops': [['count', [5, 5]]], 'expected': [0]},
]


def check() -> None:
    import importlib.util
    from pathlib import Path

    _path = Path(__file__).with_name("solution.py")
    _spec = importlib.util.spec_from_file_location("artifact", _path)
    artifact = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(artifact)
    DetectSquares = artifact.DetectSquares

    for number, case in enumerate(CASES, 1):
        obj = DetectSquares(*case.get("ctor_args", []))
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
