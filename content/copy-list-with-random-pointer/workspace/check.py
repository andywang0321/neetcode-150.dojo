"""Visible checks for `copy-list-with-random-pointer` — the student runs these.

Shipped to the student and rendered into their workbench, so they check the
statement's promises and nothing more. The verdict that counts comes from the
oracle and its generated cases, which are quarantined in `assessment/`.
"""

CASES = [
    {'args': [[[7, -1], [13, 0], [11, 4], [10, 2], [1, 0]]],
     'expected': [[7, -1], [13, 0], [11, 4], [10, 2], [1, 0]],
     'predicate': 'deep_copy_valid'},
    {'args': [[[1, 1], [2, 1]]], 'expected': [[1, 1], [2, 1]], 'predicate': 'deep_copy_valid'},
    {'args': [[[3, -1], [3, 0], [3, -1]]],
     'expected': [[3, -1], [3, 0], [3, -1]],
     'predicate': 'deep_copy_valid'},
]


def check() -> None:
    import importlib.util
    from pathlib import Path

    _path = Path(__file__).with_name("solution.py")
    _spec = importlib.util.spec_from_file_location("artifact", _path)
    artifact = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(artifact)
    copy_random_list = artifact.copy_random_list

    checked = 0
    for number, case in enumerate(CASES, 1):
        if "predicate" in case:
            # This one is decided by a dojo checker, not by equality:
            # `dojo check` runs it, and it is not reproduced here.
            continue
        got = copy_random_list(*case["args"])
        ok = got == case["expected"]
        assert ok, f"case {number}: got {got!r}, want {case['expected']!r}"
        checked += 1
    print(f"{checked} of {len(CASES)} visible checks passed")


if __name__ == "__main__":
    check()
