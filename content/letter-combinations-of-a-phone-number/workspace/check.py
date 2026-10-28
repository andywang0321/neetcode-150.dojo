"""Visible checks for `letter-combinations-of-a-phone-number` — the student runs these.

Shipped to the student and rendered into their workbench, so they check the
statement's promises and nothing more. The verdict that counts comes from the
oracle and its generated cases, which are quarantined in `assessment/`.
"""

CASES = [
    {'args': ['23'],
     'expected': ['ad', 'ae', 'af', 'bd', 'be', 'bf', 'cd', 'ce', 'cf'],
     'compare': 'sorted'},
    {'args': ['2'], 'expected': ['a', 'b', 'c'], 'compare': 'sorted'},
    {'args': ['79'],
     'expected': ['pw', 'px', 'py', 'pz', 'qw', 'qx', 'qy', 'qz', 'rw', 'rx', 'ry', 'rz', 'sw',
                  'sx', 'sy', 'sz'],
     'compare': 'sorted'},
    {'args': ['2345'],
     'expected': ['adgj', 'adgk', 'adgl', 'adhj', 'adhk', 'adhl', 'adij', 'adik', 'adil',
                  'aegj', 'aegk', 'aegl', 'aehj', 'aehk', 'aehl', 'aeij', 'aeik', 'aeil',
                  'afgj', 'afgk', 'afgl', 'afhj', 'afhk', 'afhl', 'afij', 'afik', 'afil',
                  'bdgj', 'bdgk', 'bdgl', 'bdhj', 'bdhk', 'bdhl', 'bdij', 'bdik', 'bdil',
                  'begj', 'begk', 'begl', 'behj', 'behk', 'behl', 'beij', 'beik', 'beil',
                  'bfgj', 'bfgk', 'bfgl', 'bfhj', 'bfhk', 'bfhl', 'bfij', 'bfik', 'bfil',
                  'cdgj', 'cdgk', 'cdgl', 'cdhj', 'cdhk', 'cdhl', 'cdij', 'cdik', 'cdil',
                  'cegj', 'cegk', 'cegl', 'cehj', 'cehk', 'cehl', 'ceij', 'ceik', 'ceil',
                  'cfgj', 'cfgk', 'cfgl', 'cfhj', 'cfhk', 'cfhl', 'cfij', 'cfik', 'cfil'],
     'compare': 'sorted'},
]


def check() -> None:
    import importlib.util
    from pathlib import Path

    _path = Path(__file__).with_name("solution.py")
    _spec = importlib.util.spec_from_file_location("artifact", _path)
    artifact = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(artifact)
    letter_combinations = artifact.letter_combinations

    checked = 0
    for number, case in enumerate(CASES, 1):
        got = letter_combinations(*case["args"])
        if case.get("compare") == "sorted":
            ok = sorted(map(repr, got)) == sorted(map(repr, case["expected"]))
        else:
            ok = got == case["expected"]
        assert ok, f"case {number}: got {got!r}, want {case['expected']!r}"
        checked += 1
    print(f"{checked} of {len(CASES)} visible checks passed")


if __name__ == "__main__":
    check()
