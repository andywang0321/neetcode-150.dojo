"""Visible checks for `meeting-rooms` — the student runs these.

Shipped to the student and rendered into their workbench, so they check the
statement's promises and nothing more. The verdict that counts comes from the
oracle and its generated cases, which are quarantined in `assessment/`.
"""

CASES = [
    {'args': [[[0, 30], [5, 10], [15, 20]]], 'expected': False},
    {'args': [[[7, 10], [2, 4]]], 'expected': True},
    {'args': [[]], 'expected': True},
    {'args': [[[1, 5], [5, 10]]], 'expected': True},
]


def check() -> None:
    import importlib.util
    from pathlib import Path

    _path = Path(__file__).with_name("solution.py")
    _spec = importlib.util.spec_from_file_location("artifact", _path)
    artifact = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(artifact)
    can_attend_meetings = artifact.can_attend_meetings

    checked = 0
    for number, case in enumerate(CASES, 1):
        got = can_attend_meetings(*case["args"])
        ok = got == case["expected"]
        assert ok, f"case {number}: got {got!r}, want {case['expected']!r}"
        checked += 1
    print(f"{checked} of {len(CASES)} visible checks passed")


if __name__ == "__main__":
    check()
