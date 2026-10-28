"""Visible checks for `encode_and_decode_strings` — the student runs these.

Shipped to the student and rendered into their workbench, so they check the
statement's promises and nothing more. The verdict that counts comes from the
oracle and its generated cases, which are quarantined in `assessment/`.
"""

CASES = [
    {'args': [['neet', 'code', 'love', 'you']],
     'predicate': 'encode_decode_roundtrip',
     'expected': True},
    {'args': [['we', 'say', ':', 'yes']],
     'predicate': 'encode_decode_roundtrip',
     'expected': True},
    {'args': [[]], 'predicate': 'encode_decode_roundtrip', 'expected': True},
    {'args': [['']], 'predicate': 'encode_decode_roundtrip', 'expected': True},
    {'args': [['', '']], 'predicate': 'encode_decode_roundtrip', 'expected': True},
]


def check() -> None:
    from solution import encode

    checked = 0
    for number, case in enumerate(CASES, 1):
        if "predicate" in case:
            # This one is decided by a dojo checker, not by equality:
            # `dojo check` runs it, and it is not reproduced here.
            continue
        got = encode(*case["args"])
        ok = got == case["expected"]
        assert ok, f"case {number}: got {got!r}, want {case['expected']!r}"
        checked += 1
    print(f"{checked} of {len(CASES)} visible checks passed")


if __name__ == "__main__":
    check()
