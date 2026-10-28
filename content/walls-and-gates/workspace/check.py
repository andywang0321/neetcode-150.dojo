"""Visible checks for `walls-and-gates` — the student runs these.

Shipped to the student and rendered into their workbench, so they check the
statement's promises and nothing more. The verdict that counts comes from the
oracle and its generated cases, which are quarantined in `assessment/`.
"""

CASES = [
    {'args': [[[2147483647, -1, 0, 2147483647], [2147483647, 2147483647, 2147483647, -1],
               [2147483647, -1, 2147483647, -1], [0, -1, 2147483647, 2147483647]]],
     'expected': [[[3, -1, 0, 1], [2, 2, 1, -1], [1, -1, 2, -1], [0, -1, 3, 4]]],
     'compare': 'mutates'},
    {'args': [[[-1]]], 'expected': [[[-1]]], 'compare': 'mutates'},
    {'args': [[[0, -1, 2147483647]]], 'expected': [[[0, -1, 2147483647]]], 'compare': 'mutates'},
    {'args': [[[2147483647]]], 'expected': [[[2147483647]]], 'compare': 'mutates'},
]


def check() -> None:
    import importlib.util
    from pathlib import Path

    _path = Path(__file__).with_name("solution.py")
    _spec = importlib.util.spec_from_file_location("artifact", _path)
    artifact = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(artifact)
    walls_and_gates = artifact.walls_and_gates

    checked = 0
    for number, case in enumerate(CASES, 1):
        got = walls_and_gates(*case["args"])
        compared = case["args"] if case.get("compare") == "mutates" else got
        ok = compared == case["expected"]
        assert ok, f"case {number}: got {compared!r}, want {case['expected']!r}"
        checked += 1
    print(f"{checked} of {len(CASES)} visible checks passed")


if __name__ == "__main__":
    check()
