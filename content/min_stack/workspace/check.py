"""Visible checks for `min_stack` — the student runs these.

Shipped to the student and rendered into their workbench, so they check the
statement's promises and nothing more. The verdict that counts comes from the
oracle and its generated cases, which are quarantined in `assessment/`.
"""

CASES = [
    {'ops': [['push', 1], ['push', 2], ['push', 0], ['getMin'], ['pop'], ['top'], ['getMin']],
     'expected': [None, None, None, 0, None, 2, 1]},
    {'ops': [['push', -2], ['push', 0], ['push', -3], ['getMin'], ['pop'], ['top'], ['getMin']],
     'expected': [None, None, None, -3, None, 0, -2]},
    {'ops': [['push', 5], ['top'], ['getMin'], ['pop']], 'expected': [None, 5, 5, None]},
]


def check() -> None:
    from solution import MinStack

    for number, case in enumerate(CASES, 1):
        obj = MinStack(*case.get("ctor_args", []))
        got = []
        for op in case["ops"]:
            method, *args = op
            got.append(getattr(obj, method)(*args))
        assert got == case["expected"], (
            f"case {number}: got {got!r}, want {case['expected']!r}"
        )
    print(f"all {len(CASES)} visible checks passed")


if __name__ == "__main__":
    check()
