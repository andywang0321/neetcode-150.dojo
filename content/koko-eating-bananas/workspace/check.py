"""Visible checks for `koko-eating-bananas` — the student runs these.

Shipped to the student and rendered into their workbench, so they check the
statement's promises and nothing more. The verdict that counts comes from the
oracle and its generated cases, which are quarantined in `assessment/`.
"""

CASES = [
    {'args': [[3, 6, 7, 11], 8], 'expected': 4},
    {'args': [[30, 11, 23, 4, 20], 5], 'expected': 30},
    {'args': [[30, 11, 23, 4, 20], 6], 'expected': 23},
    {'args': [[3, 6, 7, 11], 4], 'expected': 11},
    {'args': [[5], 5], 'expected': 1},
]


def check() -> None:
    import importlib.util
    from pathlib import Path

    _path = Path(__file__).with_name("solution.py")
    _spec = importlib.util.spec_from_file_location("artifact", _path)
    artifact = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(artifact)
    min_eating_speed = artifact.min_eating_speed

    checked = 0
    for number, case in enumerate(CASES, 1):
        got = min_eating_speed(*case["args"])
        ok = got == case["expected"]
        assert ok, f"case {number}: got {got!r}, want {case['expected']!r}"
        checked += 1
    print(f"{checked} of {len(CASES)} visible checks passed")


if __name__ == "__main__":
    check()
