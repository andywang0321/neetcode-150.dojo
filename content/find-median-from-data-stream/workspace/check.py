"""Visible checks for `find-median-from-data-stream` — the student runs these.

Shipped to the student and rendered into their workbench, so they check the
statement's promises and nothing more. The verdict that counts comes from the
oracle and its generated cases, which are quarantined in `assessment/`.
"""

CASES = [
    {'ops': [['addNum', 1], ['addNum', 2], ['findMedian'], ['addNum', 3], ['findMedian']],
     'expected': [None, None, 1.5, None, 2.0]},
    {'ops': [['addNum', 5], ['findMedian']], 'expected': [None, 5.0]},
    {'ops': [['addNum', -100000], ['addNum', 100000], ['findMedian'], ['addNum', 0],
             ['findMedian']],
     'expected': [None, None, 0.0, None, 0.0]},
    {'ops': [['addNum', 1], ['addNum', 1], ['findMedian'], ['addNum', 1], ['findMedian']],
     'expected': [None, None, 1.0, None, 1.0]},
]


def check() -> None:
    import importlib.util
    from pathlib import Path

    _path = Path(__file__).with_name("solution.py")
    _spec = importlib.util.spec_from_file_location("artifact", _path)
    artifact = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(artifact)
    MedianFinder = artifact.MedianFinder

    for number, case in enumerate(CASES, 1):
        obj = MedianFinder(*case.get("ctor_args", []))
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
