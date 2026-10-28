"""Visible checks for `count-good-nodes-in-binary-tree` — the student runs these.

Shipped to the student and rendered into their workbench, so they check the
statement's promises and nothing more. The verdict that counts comes from the
oracle and its generated cases, which are quarantined in `assessment/`.
"""

CASES = [
    {'args': [[3, [1, [3, None, None], None], [4, [1, None, None], [5, None, None]]]],
     'expected': 4},
    {'args': [[3, [3, [4, None, None], [2, None, None]], None]], 'expected': 3},
    {'args': [[1, None, None]], 'expected': 1},
    {'args': [[2, [2, [2, None, None], None], None]], 'expected': 3},
    {'args': [[-10000, [-10000, None, None], [10000, None, None]]], 'expected': 3},
]


def check() -> None:
    import importlib.util
    from pathlib import Path

    _path = Path(__file__).with_name("solution.py")
    _spec = importlib.util.spec_from_file_location("artifact", _path)
    artifact = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(artifact)
    good_nodes = artifact.good_nodes

    checked = 0
    for number, case in enumerate(CASES, 1):
        got = good_nodes(*case["args"])
        ok = got == case["expected"]
        assert ok, f"case {number}: got {got!r}, want {case['expected']!r}"
        checked += 1
    print(f"{checked} of {len(CASES)} visible checks passed")


if __name__ == "__main__":
    check()
