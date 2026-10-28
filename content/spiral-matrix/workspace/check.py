"""Visible checks for `spiral-matrix` — the student runs these.

Shipped to the student and rendered into their workbench, so they check the
statement's promises and nothing more. The verdict that counts comes from the
oracle and its generated cases, which are quarantined in `assessment/`.
"""

CASES = [
    {'args': [[[1, 2, 3], [4, 5, 6], [7, 8, 9]]], 'expected': [1, 2, 3, 6, 9, 8, 7, 4, 5]},
    {'args': [[[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]],
     'expected': [1, 2, 3, 4, 8, 12, 11, 10, 9, 5, 6, 7]},
    {'args': [[[7]]], 'expected': [7]},
    {'args': [[[1, 2, 3, 4]]], 'expected': [1, 2, 3, 4]},
]


def check() -> None:
    import importlib.util
    from pathlib import Path

    _path = Path(__file__).with_name("solution.py")
    _spec = importlib.util.spec_from_file_location("artifact", _path)
    artifact = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(artifact)
    spiral_order = artifact.spiral_order

    checked = 0
    for number, case in enumerate(CASES, 1):
        got = spiral_order(*case["args"])
        ok = got == case["expected"]
        assert ok, f"case {number}: got {got!r}, want {case['expected']!r}"
        checked += 1
    print(f"{checked} of {len(CASES)} visible checks passed")


if __name__ == "__main__":
    check()
