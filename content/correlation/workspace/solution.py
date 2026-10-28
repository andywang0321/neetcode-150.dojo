def correlation(X: list, Y: list) -> float:
    # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
    raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    _COMPARE = 'approx:0.0001'  # every case here compares this way
    _cases = [
        (([1, 2, 3, 4, 5], [3, 2, 5, 9, 6]), 0.7506),
        (([1, 2, 3], [1, 2, 3]), 1.0),
        (([1, 2, 3], [3, 2, 1]), -1.0),
    ]

    def _same(_got, _want):
        if _COMPARE == 'approx:0.0001':  # float tolerance
            return abs(_got - _want) <= 0.0001
        return _got == _want
    for _i, (_args, _want) in enumerate(_cases, 1):
        _got = correlation(*_args)
        _ok = _same(_got, _want)
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} got={_got!r} want={_want!r}")
# --- end dojo ---
