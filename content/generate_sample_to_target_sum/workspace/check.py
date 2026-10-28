"""Visible checks for `generate_sample_to_target_sum` — the student runs these.

Shipped to the student and rendered into their workbench, so they check the
statement's promises and nothing more. The verdict that counts comes from the
oracle and its generated cases, which are quarantined in `assessment/`.
"""

CASES = [
    {'args': [5, 3.6, 6], 'predicate': 'sample_valid', 'expected': True},
    {'args': [4, 2.0, 10], 'predicate': 'sample_valid', 'expected': True},
    {'args': [1, 0.5, -7], 'predicate': 'sample_valid', 'expected': True},
]


def check() -> None:
    from solution import generate_sample

    checked = 0
    for number, case in enumerate(CASES, 1):
        if "predicate" in case:
            # This one is decided by a dojo checker, not by equality:
            # `dojo check` runs it, and it is not reproduced here.
            continue
        got = generate_sample(*case["args"])
        ok = got == case["expected"]
        assert ok, f"case {number}: got {got!r}, want {case['expected']!r}"
        checked += 1
    print(f"{checked} of {len(CASES)} visible checks passed")


if __name__ == "__main__":
    check()
