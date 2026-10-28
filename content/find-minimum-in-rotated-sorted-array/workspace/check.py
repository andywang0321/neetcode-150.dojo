"""Visible checks for `find-minimum-in-rotated-sorted-array` — the student runs these.

Shipped to the student and rendered into their workbench, so they check the
statement's promises and nothing more. The verdict that counts comes from the
oracle and its generated cases, which are quarantined in `assessment/`.
"""

CASES = [
    {'args': [[3, 4, 5, 1, 2]], 'expected': 1},
    {'args': [[4, 5, 6, 7, 0, 1, 2]], 'expected': 0},
    {'args': [[11, 13, 15, 17]], 'expected': 11},
    {'args': [[1]], 'expected': 1},
    {'args': [[2, 1]], 'expected': 1},
]


def check() -> None:
    import importlib.util
    from pathlib import Path

    _path = Path(__file__).with_name("solution.py")
    _spec = importlib.util.spec_from_file_location("artifact", _path)
    artifact = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(artifact)
    find_min = artifact.find_min

    checked = 0
    for number, case in enumerate(CASES, 1):
        got = find_min(*case["args"])
        ok = got == case["expected"]
        assert ok, f"case {number}: got {got!r}, want {case['expected']!r}"
        checked += 1
    print(f"{checked} of {len(CASES)} visible checks passed")


if __name__ == "__main__":
    check()
