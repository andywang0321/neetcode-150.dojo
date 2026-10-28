"""Visible checks for `pacific-atlantic-water-flow` — the student runs these.

Shipped to the student and rendered into their workbench, so they check the
statement's promises and nothing more. The verdict that counts comes from the
oracle and its generated cases, which are quarantined in `assessment/`.
"""

CASES = [
    {'args': [[[1, 2, 2, 3, 5], [3, 2, 3, 4, 4], [2, 4, 5, 3, 1], [6, 7, 1, 4, 5],
               [5, 1, 1, 2, 4]]],
     'expected': [[0, 4], [1, 3], [1, 4], [2, 2], [3, 0], [3, 1], [4, 0]],
     'compare': 'sorted'},
    {'args': [[[1]]], 'expected': [[0, 0]], 'compare': 'sorted'},
    {'args': [[[3, 3], [3, 3]]],
     'expected': [[0, 0], [0, 1], [1, 0], [1, 1]],
     'compare': 'sorted'},
    {'args': [[[10, 10, 10], [10, 1, 10], [10, 10, 10]]],
     'expected': [[0, 0], [0, 1], [0, 2], [1, 0], [1, 2], [2, 0], [2, 1], [2, 2]],
     'compare': 'sorted'},
]


def check() -> None:
    import importlib.util
    from pathlib import Path

    _path = Path(__file__).with_name("solution.py")
    _spec = importlib.util.spec_from_file_location("artifact", _path)
    artifact = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(artifact)
    pacific_atlantic = artifact.pacific_atlantic

    checked = 0
    for number, case in enumerate(CASES, 1):
        got = pacific_atlantic(*case["args"])
        if case.get("compare") == "sorted":
            ok = sorted(map(repr, got)) == sorted(map(repr, case["expected"]))
        else:
            ok = got == case["expected"]
        assert ok, f"case {number}: got {got!r}, want {case['expected']!r}"
        checked += 1
    print(f"{checked} of {len(CASES)} visible checks passed")


if __name__ == "__main__":
    check()
