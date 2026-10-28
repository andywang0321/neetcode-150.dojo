"""Visible checks for `kth-smallest-element-in-a-bst` — the student runs these.

Shipped to the student and rendered into their workbench, so they check the
statement's promises and nothing more. The verdict that counts comes from the
oracle and its generated cases, which are quarantined in `assessment/`.
"""

CASES = [
    {'args': [[3, [1, None, [2, None, None]], [4, None, None]], 1], 'expected': 1},
    {'args': [[5, [3, [2, [1, None, None], None], [4, None, None]], [6, None, None]], 3],
     'expected': 3},
    {'args': [[1, None, [2, None, [3, None, None]]], 3], 'expected': 3},
]


def check() -> None:
    import importlib.util
    from pathlib import Path

    _path = Path(__file__).with_name("solution.py")
    _spec = importlib.util.spec_from_file_location("artifact", _path)
    artifact = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(artifact)
    kth_smallest = artifact.kth_smallest

    checked = 0
    for number, case in enumerate(CASES, 1):
        got = kth_smallest(*case["args"])
        ok = got == case["expected"]
        assert ok, f"case {number}: got {got!r}, want {case['expected']!r}"
        checked += 1
    print(f"{checked} of {len(CASES)} visible checks passed")


if __name__ == "__main__":
    check()
