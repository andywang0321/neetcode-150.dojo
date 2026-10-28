"""Visible checks for `kth-largest-element-in-an-array` — the student runs these.

Shipped to the student and rendered into their workbench, so they check the
statement's promises and nothing more. The verdict that counts comes from the
oracle and its generated cases, which are quarantined in `assessment/`.
"""

CASES = [
    {'args': [[3, 2, 1, 5, 6, 4], 2], 'expected': 5},
    {'args': [[3, 2, 3, 1, 2, 4, 5, 5, 6], 4], 'expected': 4},
    {'args': [[3, 2, 3, 1, 2, 4, 5, 5, 6], 9], 'expected': 1},
    {'args': [[7, 7, 7, 1], 3], 'expected': 7},
]


def check() -> None:
    import importlib.util
    from pathlib import Path

    _path = Path(__file__).with_name("solution.py")
    _spec = importlib.util.spec_from_file_location("artifact", _path)
    artifact = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(artifact)
    find_kth_largest = artifact.find_kth_largest

    checked = 0
    for number, case in enumerate(CASES, 1):
        got = find_kth_largest(*case["args"])
        ok = got == case["expected"]
        assert ok, f"case {number}: got {got!r}, want {case['expected']!r}"
        checked += 1
    print(f"{checked} of {len(CASES)} visible checks passed")


if __name__ == "__main__":
    check()
