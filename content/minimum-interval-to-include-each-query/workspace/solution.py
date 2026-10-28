def min_interval(intervals: list[list[int]], queries: list[int]) -> list[int]:
    # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
    raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    _cases = [
        (([[1, 4], [2, 4], [3, 6], [4, 4]], [2, 3, 4, 5]), [3, 3, 1, 4]),
        (([[2, 3], [2, 5], [1, 8], [20, 25]], [2, 19, 5, 22]), [2, -1, 4, 6]),
        (([[1, 10], [2, 3]], [5, 5, 3]), [10, 10, 2]),
    ]
    for _i, (_args, _want) in enumerate(_cases, 1):
        _got = min_interval(*_args)
        _ok = _got == _want
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} got={_got!r} want={_want!r}")
# --- end dojo ---
