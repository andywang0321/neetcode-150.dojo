"""Visible checks for `valid-parenthesis-string` — the student runs these.

Shipped to the student and rendered into their workbench, so they check the
statement's promises and nothing more. The verdict that counts comes from the
oracle and its generated cases, which are quarantined in `assessment/`.
"""

CASES = [
    {'args': ['()'], 'expected': True},
    {'args': ['(*)'], 'expected': True},
    {'args': ['(*))'], 'expected': True},
    {'args': ['('], 'expected': False},
    {'args': ['(*'], 'expected': True},
    {'args': ['*('], 'expected': False},
]


def check() -> None:
    import importlib.util
    from pathlib import Path

    _path = Path(__file__).with_name("solution.py")
    _spec = importlib.util.spec_from_file_location("artifact", _path)
    artifact = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(artifact)
    check_valid_string = artifact.check_valid_string

    checked = 0
    for number, case in enumerate(CASES, 1):
        got = check_valid_string(*case["args"])
        ok = got == case["expected"]
        assert ok, f"case {number}: got {got!r}, want {case['expected']!r}"
        checked += 1
    print(f"{checked} of {len(CASES)} visible checks passed")


if __name__ == "__main__":
    check()
