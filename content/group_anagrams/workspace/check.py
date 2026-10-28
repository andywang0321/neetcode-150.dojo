"""Visible checks for `group_anagrams` — the student runs these.

Shipped to the student and rendered into their workbench, so they check the
statement's promises and nothing more. The verdict that counts comes from the
oracle and its generated cases, which are quarantined in `assessment/`.
"""

CASES = [
    {'args': [['act', 'pots', 'tops', 'cat', 'stop', 'hat']],
     'expected': [['act', 'cat'], ['hat'], ['pots', 'stop', 'tops']],
     'compare': 'sorted'},
    {'args': [['x']], 'expected': [['x']], 'compare': 'sorted'},
    {'args': [['']], 'expected': [['']], 'compare': 'sorted'},
]


def check() -> None:
    from solution import group_anagrams

    checked = 0
    for number, case in enumerate(CASES, 1):
        got = group_anagrams(*case["args"])
        if case.get("compare") == "sorted":
            ok = sorted(map(repr, got)) == sorted(map(repr, case["expected"]))
        else:
            ok = got == case["expected"]
        assert ok, f"case {number}: got {got!r}, want {case['expected']!r}"
        checked += 1
    print(f"{checked} of {len(CASES)} visible checks passed")


if __name__ == "__main__":
    check()
