def missing_number(nums: list[int]) -> int:
    # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
    raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    _cases = [
        (([3, 0, 1],), 2),
        (([0, 1],), 2),
        (([9, 6, 4, 2, 3, 5, 7, 0, 1],), 8),
        (([1],), 0),
        (([2, 3, 0],), 1),
    ]
    for _i, (_args, _want) in enumerate(_cases, 1):
        _got = missing_number(*_args)
        _ok = _got == _want
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} got={_got!r} want={_want!r}")
# --- end dojo ---
