"""Visible checks for `kth-largest-element-in-a-stream` — the student runs these.

Shipped to the student and rendered into their workbench, so they check the
statement's promises and nothing more. The verdict that counts comes from the
oracle and its generated cases, which are quarantined in `assessment/`.
"""

CASES = [
    {'ops': [['__init__', 3, [4, 5, 8, 2]], ['add', 3], ['add', 5], ['add', 10], ['add', 9],
             ['add', 4]],
     'ctor_args': [3, [4, 5, 8, 2]],
     'expected': [None, 4, 5, 5, 8, 8]},
    {'ops': [['__init__', 4, [7, 7, 7, 7, 8, 3]], ['add', 2], ['add', 10], ['add', 9],
             ['add', 9]],
     'ctor_args': [4, [7, 7, 7, 7, 8, 3]],
     'expected': [None, 7, 7, 7, 8]},
    {'ops': [['__init__', 1, []], ['add', -3]], 'ctor_args': [1, []], 'expected': [None, -3]},
    {'ops': [['__init__', 3, [7, 7]], ['add', 7]],
     'ctor_args': [3, [7, 7]],
     'expected': [None, 7]},
]


def check() -> None:
    import importlib.util
    from pathlib import Path

    _path = Path(__file__).with_name("solution.py")
    _spec = importlib.util.spec_from_file_location("artifact", _path)
    artifact = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(artifact)
    KthLargest = artifact.KthLargest

    for number, case in enumerate(CASES, 1):
        obj = KthLargest(*case.get("ctor_args", []))
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
