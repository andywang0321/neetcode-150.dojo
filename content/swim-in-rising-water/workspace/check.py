"""Visible checks for `swim-in-rising-water` — the student runs these.

Shipped to the student and rendered into their workbench, so they check the
statement's promises and nothing more. The verdict that counts comes from the
oracle and its generated cases, which are quarantined in `assessment/`.
"""

CASES = [
    {'args': [[[0, 2], [1, 3]]], 'expected': 3},
    {'args': [[[0, 1, 2, 3, 4], [24, 23, 22, 21, 5], [12, 13, 14, 15, 16], [11, 17, 18, 19, 20],
               [10, 9, 8, 7, 6]]],
     'expected': 16},
    {'args': [[[0]]], 'expected': 0},
    {'args': [[[0, 7, 5], [2, 6, 4], [3, 8, 1]]], 'expected': 6},
]


def check() -> None:
    import importlib.util
    from pathlib import Path

    _path = Path(__file__).with_name("solution.py")
    _spec = importlib.util.spec_from_file_location("artifact", _path)
    artifact = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(artifact)
    swim_in_water = artifact.swim_in_water

    checked = 0
    for number, case in enumerate(CASES, 1):
        got = swim_in_water(*case["args"])
        ok = got == case["expected"]
        assert ok, f"case {number}: got {got!r}, want {case['expected']!r}"
        checked += 1
    print(f"{checked} of {len(CASES)} visible checks passed")


if __name__ == "__main__":
    check()
