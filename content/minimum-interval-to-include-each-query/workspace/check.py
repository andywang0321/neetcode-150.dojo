"""Visible checks for `minimum-interval-to-include-each-query` — the student runs these.

Shipped to the student and rendered into their workbench, so they check the
statement's promises and nothing more. The verdict that counts comes from the
oracle and its generated cases, which are quarantined in `assessment/`.
"""

CASES = [
    {'args': [[[1, 4], [2, 4], [3, 6], [4, 4]], [2, 3, 4, 5]], 'expected': [3, 3, 1, 4]},
    {'args': [[[2, 3], [2, 5], [1, 8], [20, 25]], [2, 19, 5, 22]], 'expected': [2, -1, 4, 6]},
    {'args': [[[1, 10], [2, 3]], [5, 5, 3]], 'expected': [10, 10, 2]},
]


def check() -> None:
    import importlib.util
    from pathlib import Path

    _path = Path(__file__).with_name("solution.py")
    _spec = importlib.util.spec_from_file_location("artifact", _path)
    artifact = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(artifact)
    min_interval = artifact.min_interval

    checked = 0
    for number, case in enumerate(CASES, 1):
        got = min_interval(*case["args"])
        ok = got == case["expected"]
        assert ok, f"case {number}: got {got!r}, want {case['expected']!r}"
        checked += 1
    print(f"{checked} of {len(CASES)} visible checks passed")


if __name__ == "__main__":
    check()
