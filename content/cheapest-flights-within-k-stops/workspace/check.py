"""Visible checks for `cheapest-flights-within-k-stops` — the student runs these.

Shipped to the student and rendered into their workbench, so they check the
statement's promises and nothing more. The verdict that counts comes from the
oracle and its generated cases, which are quarantined in `assessment/`.
"""

CASES = [
    {'args': [4, [[0, 1, 100], [1, 2, 100], [2, 0, 100], [1, 3, 600], [2, 3, 200]], 0, 3, 1],
     'expected': 700},
    {'args': [3, [[0, 1, 100], [1, 2, 100], [0, 2, 500]], 0, 2, 1], 'expected': 200},
    {'args': [3, [[0, 1, 100], [1, 2, 100], [0, 2, 500]], 0, 2, 0], 'expected': 500},
    {'args': [3, [[0, 1, 100]], 0, 2, 1], 'expected': -1},
    {'args': [2, [], 0, 1, 0], 'expected': -1},
]


def check() -> None:
    import importlib.util
    from pathlib import Path

    _path = Path(__file__).with_name("solution.py")
    _spec = importlib.util.spec_from_file_location("artifact", _path)
    artifact = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(artifact)
    find_cheapest_price = artifact.find_cheapest_price

    checked = 0
    for number, case in enumerate(CASES, 1):
        got = find_cheapest_price(*case["args"])
        ok = got == case["expected"]
        assert ok, f"case {number}: got {got!r}, want {case['expected']!r}"
        checked += 1
    print(f"{checked} of {len(CASES)} visible checks passed")


if __name__ == "__main__":
    check()
