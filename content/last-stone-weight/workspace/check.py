"""Visible checks for `last-stone-weight` — the student runs these.

Shipped to the student and rendered into their workbench, so they check the
statement's promises and nothing more. The verdict that counts comes from the
oracle and its generated cases, which are quarantined in `assessment/`.
"""

CASES = [
    {'args': [[2, 7, 4, 1, 8, 1]], 'expected': 1},
    {'args': [[1]], 'expected': 1},
    {'args': [[1, 1]], 'expected': 0},
    {'args': [[10, 10, 10]], 'expected': 10},
]


def check() -> None:
    import importlib.util
    from pathlib import Path

    _path = Path(__file__).with_name("solution.py")
    _spec = importlib.util.spec_from_file_location("artifact", _path)
    artifact = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(artifact)
    last_stone_weight = artifact.last_stone_weight

    checked = 0
    for number, case in enumerate(CASES, 1):
        got = last_stone_weight(*case["args"])
        ok = got == case["expected"]
        assert ok, f"case {number}: got {got!r}, want {case['expected']!r}"
        checked += 1
    print(f"{checked} of {len(CASES)} visible checks passed")


if __name__ == "__main__":
    check()
