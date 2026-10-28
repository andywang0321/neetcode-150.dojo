def letter_combinations(digits: str) -> list[str]:
    # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
    raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    _COMPARE = 'sorted'  # every case here compares this way
    _cases = [
        (('23',), ['ad', 'ae', 'af', 'bd', 'be', 'bf', 'cd', 'ce', 'cf']),
        (('2',), ['a', 'b', 'c']),
        (('79',), ['pw', 'px', 'py', 'pz', 'qw', 'qx', 'qy', 'qz', 'rw', 'rx', 'ry', 'rz', 'sw', 'sx', 'sy', 'sz']),
        (('2345',), ['adgj', 'adgk', 'adgl', 'adhj', 'adhk', 'adhl', 'adij', 'adik', 'adil', 'aegj', 'aegk', 'aegl', 'aehj', 'aehk', 'aehl', 'aeij', 'aeik', 'aeil', 'afgj', 'afgk', 'afgl', 'afhj', 'afhk', 'afhl', 'afij', 'afik', 'afil', 'bdgj', 'bdgk', 'bdgl', 'bdhj', 'bdhk', 'bdhl', 'bdij', 'bdik', 'bdil', 'begj', 'begk', 'begl', 'behj', 'behk', 'behl', 'beij', 'beik', 'beil', 'bfgj', 'bfgk', 'bfgl', 'bfhj', 'bfhk', 'bfhl', 'bfij', 'bfik', 'bfil', 'cdgj', 'cdgk', 'cdgl', 'cdhj', 'cdhk', 'cdhl', 'cdij', 'cdik', 'cdil', 'cegj', 'cegk', 'cegl', 'cehj', 'cehk', 'cehl', 'ceij', 'ceik', 'ceil', 'cfgj', 'cfgk', 'cfgl', 'cfhj', 'cfhk', 'cfhl', 'cfij', 'cfik', 'cfil']),
    ]

    def _same(_got, _want):
        if _COMPARE == "sorted":  # dojo accepts any order here
            return sorted(map(repr, _got)) == sorted(map(repr, _want))
        return _got == _want
    for _i, (_args, _want) in enumerate(_cases, 1):
        _got = letter_combinations(*_args)
        _ok = _same(_got, _want)
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} got={_got!r} want={_want!r}")
# --- end dojo ---
