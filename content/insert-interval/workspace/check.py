"""Visible checks for `insert-interval` — the student runs these.

Shipped to the student and rendered into their workbench, so they check the
statement's promises and nothing more. The verdict that counts comes from the
oracle and its generated cases, which are quarantined in `assessment/`.
"""

CASES = [
    {'args': [[[1, 3], [6, 9]], [2, 5]], 'expected': [[1, 5], [6, 9]]},
    {'args': [[[1, 2], [3, 5], [6, 7], [8, 10], [12, 16]], [4, 8]],
     'expected': [[1, 2], [3, 10], [12, 16]]},
    {'args': [[], [5, 7]], 'expected': [[5, 7]]},
    {'args': [[[1, 2], [5, 5]], [5, 6]], 'expected': [[1, 2], [5, 6]]},
]


def check() -> None:
    import importlib.util
    from pathlib import Path

    _path = Path(__file__).with_name("solution.py")
    _spec = importlib.util.spec_from_file_location("artifact", _path)
    artifact = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(artifact)
    insert = artifact.insert

    checked = 0
    for number, case in enumerate(CASES, 1):
        got = insert(*case["args"])
        ok = got == case["expected"]
        assert ok, f"case {number}: got {got!r}, want {case['expected']!r}"
        checked += 1
    print(f"{checked} of {len(CASES)} visible checks passed")


if __name__ == "__main__":
    check()
