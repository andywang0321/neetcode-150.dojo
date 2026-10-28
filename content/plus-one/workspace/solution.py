def plus_one(digits: list[int]) -> list[int]:
    # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
    raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    _cases = [
        (([1, 2, 3],), [1, 2, 4]),
        (([4, 3, 2, 1],), [4, 3, 2, 2]),
        (([9],), [1, 0]),
        (([9, 9, 9],), [1, 0, 0, 0]),
        (([2, 9, 9],), [3, 0, 0]),
    ]
    for _i, (_args, _want) in enumerate(_cases, 1):
        _got = plus_one(*_args)
        _ok = _got == _want
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} got={_got!r} want={_want!r}")
# --- end dojo ---
