"""Visible checks for `partition-equal-subset-sum` — the student runs these.

Shipped to the student and rendered into their workbench, so they check the
statement's promises and nothing more. The verdict that counts comes from the
oracle and its generated cases, which are quarantined in `assessment/`.
"""

CASES = [
    {'args': [[1, 5, 11, 5]], 'expected': True},
    {'args': [[1, 2, 3, 5]], 'expected': False},
    {'args': [[2, 2]], 'expected': True},
    {'args': [[1, 2, 5]], 'expected': False},
]


def check() -> None:
    import importlib.util
    from pathlib import Path

    _path = Path(__file__).with_name("solution.py")
    _spec = importlib.util.spec_from_file_location("artifact", _path)
    artifact = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(artifact)
    can_partition = artifact.can_partition

    checked = 0
    for number, case in enumerate(CASES, 1):
        got = can_partition(*case["args"])
        ok = got == case["expected"]
        assert ok, f"case {number}: got {got!r}, want {case['expected']!r}"
        checked += 1
    print(f"{checked} of {len(CASES)} visible checks passed")


if __name__ == "__main__":
    check()
