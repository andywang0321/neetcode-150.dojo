def my_pow(x: float, n: int) -> float:
    # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
    raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    _COMPARE = 'approx:1e-5'  # every case here compares this way
    _cases = [
        ((2.0, 10), 1024.0),
        ((2.1, 3), 9.261000000000001),
        ((2.0, -2), 0.25),
        ((2.5, 0), 1.0),
        ((-2.0, 3), -8.0),
    ]

    def _same(_got, _want):
        if _COMPARE == 'approx:1e-5':  # float tolerance
            return abs(_got - _want) <= 1e-5
        return _got == _want
    for _i, (_args, _want) in enumerate(_cases, 1):
        _got = my_pow(*_args)
        _ok = _same(_got, _want)
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} got={_got!r} want={_want!r}")
# --- end dojo ---
