"""Visible checks for `min-cost-to-connect-all-points` — the student runs these.

Shipped to the student and rendered into their workbench, so they check the
statement's promises and nothing more. The verdict that counts comes from the
oracle and its generated cases, which are quarantined in `assessment/`.
"""

CASES = [
    {'args': [[[0, 0], [2, 2], [3, 10], [5, 2], [7, 0]]], 'expected': 20},
    {'args': [[[3, 12], [-2, 5], [-4, 1]]], 'expected': 18},
    {'args': [[[0, 0]]], 'expected': 0},
    {'args': [[[-1000000, -1000000], [1000000, 1000000]]], 'expected': 4000000},
]


def check() -> None:
    import importlib.util
    from pathlib import Path

    _path = Path(__file__).with_name("solution.py")
    _spec = importlib.util.spec_from_file_location("artifact", _path)
    artifact = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(artifact)
    min_cost_connect_points = artifact.min_cost_connect_points

    checked = 0
    for number, case in enumerate(CASES, 1):
        got = min_cost_connect_points(*case["args"])
        ok = got == case["expected"]
        assert ok, f"case {number}: got {got!r}, want {case['expected']!r}"
        checked += 1
    print(f"{checked} of {len(CASES)} visible checks passed")


if __name__ == "__main__":
    check()
