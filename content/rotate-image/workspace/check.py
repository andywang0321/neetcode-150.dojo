"""Visible checks for `rotate-image` — the student runs these.

Shipped to the student and rendered into their workbench, so they check the
statement's promises and nothing more. The verdict that counts comes from the
oracle and its generated cases, which are quarantined in `assessment/`.
"""

CASES = [
    {'args': [[[1, 2, 3], [4, 5, 6], [7, 8, 9]]],
     'expected': [[[7, 4, 1], [8, 5, 2], [9, 6, 3]]],
     'compare': 'mutates'},
    {'args': [[[5, 1, 9, 11], [2, 4, 8, 10], [13, 3, 6, 7], [15, 14, 12, 16]]],
     'expected': [[[15, 13, 2, 5], [14, 3, 4, 1], [12, 6, 8, 9], [16, 7, 10, 11]]],
     'compare': 'mutates'},
    {'args': [[[7]]], 'expected': [[[7]]], 'compare': 'mutates'},
]


def check() -> None:
    import importlib.util
    from pathlib import Path

    _path = Path(__file__).with_name("solution.py")
    _spec = importlib.util.spec_from_file_location("artifact", _path)
    artifact = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(artifact)
    rotate = artifact.rotate

    checked = 0
    for number, case in enumerate(CASES, 1):
        got = rotate(*case["args"])
        compared = case["args"] if case.get("compare") == "mutates" else got
        ok = compared == case["expected"]
        assert ok, f"case {number}: got {compared!r}, want {case['expected']!r}"
        checked += 1
    print(f"{checked} of {len(CASES)} visible checks passed")


if __name__ == "__main__":
    check()
