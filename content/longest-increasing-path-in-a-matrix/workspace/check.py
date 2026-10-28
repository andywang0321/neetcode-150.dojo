"""Visible checks for `longest-increasing-path-in-a-matrix` — the student runs these.

Shipped to the student and rendered into their workbench, so they check the
statement's promises and nothing more. The verdict that counts comes from the
oracle and its generated cases, which are quarantined in `assessment/`.
"""

CASES = [
    {'args': [[[9, 9, 4], [6, 6, 8], [2, 1, 1]]], 'expected': 4},
    {'args': [[[3, 4, 5], [3, 2, 6], [2, 2, 1]]], 'expected': 4},
    {'args': [[[1]]], 'expected': 1},
    {'args': [[[1, 1], [1, 1]]], 'expected': 1},
]


def check() -> None:
    import importlib.util
    from pathlib import Path

    _path = Path(__file__).with_name("solution.py")
    _spec = importlib.util.spec_from_file_location("artifact", _path)
    artifact = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(artifact)
    longest_increasing_path = artifact.longest_increasing_path

    checked = 0
    for number, case in enumerate(CASES, 1):
        got = longest_increasing_path(*case["args"])
        ok = got == case["expected"]
        assert ok, f"case {number}: got {got!r}, want {case['expected']!r}"
        checked += 1
    print(f"{checked} of {len(CASES)} visible checks passed")


if __name__ == "__main__":
    check()
