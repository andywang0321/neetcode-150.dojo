def sum_largest_subarray(A: list[int]) -> int:
    # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
    raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    _cases = [
        (([-1, -3, 5, -4, 3, -6, 9, 2],), 11),
        (([-1, -5, -3, -7],), 0),
        (([-2, 1, -3, 4, -1, 2, 1, -5, 4],), 6),
        (([5],), 5),
    ]
    for _i, (_args, _want) in enumerate(_cases, 1):
        _got = sum_largest_subarray(*_args)
        _ok = _got == _want
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} got={_got!r} want={_want!r}")
# --- end dojo ---
