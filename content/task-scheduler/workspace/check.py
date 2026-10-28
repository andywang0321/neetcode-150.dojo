"""Visible checks for `task-scheduler` — the student runs these.

Shipped to the student and rendered into their workbench, so they check the
statement's promises and nothing more. The verdict that counts comes from the
oracle and its generated cases, which are quarantined in `assessment/`.
"""

CASES = [
    {'args': [['A', 'A', 'A', 'B', 'B', 'B'], 2], 'expected': 8},
    {'args': [['A', 'C', 'A', 'B', 'D', 'B'], 1], 'expected': 6},
    {'args': [['A', 'A', 'A', 'B', 'B', 'B'], 3], 'expected': 10},
    {'args': [['A', 'A', 'A', 'B', 'B', 'B'], 0], 'expected': 6},
    {'args': [['A', 'A', 'A', 'B', 'B', 'B', 'C', 'C', 'C', 'D', 'D', 'D'], 1], 'expected': 12},
]


def check() -> None:
    import importlib.util
    from pathlib import Path

    _path = Path(__file__).with_name("solution.py")
    _spec = importlib.util.spec_from_file_location("artifact", _path)
    artifact = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(artifact)
    least_interval = artifact.least_interval

    checked = 0
    for number, case in enumerate(CASES, 1):
        got = least_interval(*case["args"])
        ok = got == case["expected"]
        assert ok, f"case {number}: got {got!r}, want {case['expected']!r}"
        checked += 1
    print(f"{checked} of {len(CASES)} visible checks passed")


if __name__ == "__main__":
    check()
