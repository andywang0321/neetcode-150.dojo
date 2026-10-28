"""Visible checks for `find-the-duplicate-number` — the student runs these.

Shipped to the student and rendered into their workbench, so they check the
statement's promises and nothing more. The verdict that counts comes from the
oracle and its generated cases, which are quarantined in `assessment/`.
"""

CASES = [
    {'args': [[1, 3, 4, 2, 2]], 'expected': 2},
    {'args': [[3, 1, 3, 4, 2]], 'expected': 3},
    {'args': [[3, 3, 3, 3, 3]], 'expected': 3},
    {'args': [[1, 1]], 'expected': 1},
    {'args': [[1, 2, 2, 3]], 'expected': 2},
]


def check() -> None:
    import importlib.util
    from pathlib import Path

    _path = Path(__file__).with_name("solution.py")
    _spec = importlib.util.spec_from_file_location("artifact", _path)
    artifact = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(artifact)
    find_duplicate = artifact.find_duplicate

    checked = 0
    for number, case in enumerate(CASES, 1):
        got = find_duplicate(*case["args"])
        ok = got == case["expected"]
        assert ok, f"case {number}: got {got!r}, want {case['expected']!r}"
        checked += 1
    print(f"{checked} of {len(CASES)} visible checks passed")


if __name__ == "__main__":
    check()
