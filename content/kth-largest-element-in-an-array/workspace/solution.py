def find_kth_largest(nums: list[int], k: int) -> int:
    # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
    raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    _cases = [
        (([3, 2, 1, 5, 6, 4], 2), 5),
        (([3, 2, 3, 1, 2, 4, 5, 5, 6], 4), 4),
        (([3, 2, 3, 1, 2, 4, 5, 5, 6], 9), 1),
        (([7, 7, 7, 1], 3), 7),
    ]
    for _i, (_args, _want) in enumerate(_cases, 1):
        _got = find_kth_largest(*_args)
        _ok = _got == _want
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} got={_got!r} want={_want!r}")
# --- end dojo ---
