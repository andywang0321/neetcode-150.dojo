"""Visible checks for `rotting-oranges` — the student runs these.

Shipped to the student and rendered into their workbench, so they check the
statement's promises and nothing more. The verdict that counts comes from the
oracle and its generated cases, which are quarantined in `assessment/`.
"""

CASES = [
    {'args': [[[2, 1, 1], [1, 1, 0], [0, 1, 1]]], 'expected': 4},
    {'args': [[[2, 1, 1], [0, 1, 1], [1, 0, 1]]], 'expected': -1},
    {'args': [[[0, 2]]], 'expected': 0},
    {'args': [[[1]]], 'expected': -1},
    {'args': [[[0]]], 'expected': 0},
]


def check() -> None:
    import importlib.util
    from pathlib import Path

    _path = Path(__file__).with_name("solution.py")
    _spec = importlib.util.spec_from_file_location("artifact", _path)
    artifact = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(artifact)
    oranges_rotting = artifact.oranges_rotting

    checked = 0
    for number, case in enumerate(CASES, 1):
        got = oranges_rotting(*case["args"])
        ok = got == case["expected"]
        assert ok, f"case {number}: got {got!r}, want {case['expected']!r}"
        checked += 1
    print(f"{checked} of {len(CASES)} visible checks passed")


if __name__ == "__main__":
    check()
