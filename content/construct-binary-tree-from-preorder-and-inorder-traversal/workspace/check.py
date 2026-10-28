"""Visible checks for `construct-binary-tree-from-preorder-and-inorder-traversal` — the student runs these.

Shipped to the student and rendered into their workbench, so they check the
statement's promises and nothing more. The verdict that counts comes from the
oracle and its generated cases, which are quarantined in `assessment/`.
"""

CASES = [
    {'args': [[3, 9, 20, 15, 7], [9, 3, 15, 20, 7]],
     'expected': [3, [9, None, None], [20, [15, None, None], [7, None, None]]]},
    {'args': [[-1], [-1]], 'expected': [-1, None, None]},
    {'args': [[1, 2, 3], [3, 2, 1]], 'expected': [1, [2, [3, None, None], None], None]},
    {'args': [[1, 2, 3], [1, 2, 3]], 'expected': [1, None, [2, None, [3, None, None]]]},
]


def check() -> None:
    import importlib.util
    from pathlib import Path

    _path = Path(__file__).with_name("solution.py")
    _spec = importlib.util.spec_from_file_location("artifact", _path)
    artifact = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(artifact)
    build_tree = artifact.build_tree

    checked = 0
    for number, case in enumerate(CASES, 1):
        got = build_tree(*case["args"])
        ok = got == case["expected"]
        assert ok, f"case {number}: got {got!r}, want {case['expected']!r}"
        checked += 1
    print(f"{checked} of {len(CASES)} visible checks passed")


if __name__ == "__main__":
    check()
