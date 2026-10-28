def max_area(height: list[int]) -> int:
    # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
    raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    _cases = [
        (([1, 7, 2, 5, 4, 7, 3, 6],), 36),
        (([2, 2, 2],), 4),
        (([1, 1],), 1),
    ]
    for _i, (_args, _want) in enumerate(_cases, 1):
        _got = max_area(*_args)
        _ok = _got == _want
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} got={_got!r} want={_want!r}")
# --- end dojo ---
