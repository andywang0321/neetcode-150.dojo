def daily_temperatures(temperatures: list[int]) -> list[int]:
    # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
    raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    _cases = [
        (([30, 38, 30, 36, 35, 40, 28],), [1, 4, 1, 2, 1, 0, 0]),
        (([22, 21, 20],), [0, 0, 0]),
        (([40, 30, 20, 35],), [0, 2, 1, 0]),
    ]
    for _i, (_args, _want) in enumerate(_cases, 1):
        _got = daily_temperatures(*_args)
        _ok = _got == _want
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} got={_got!r} want={_want!r}")
# --- end dojo ---
