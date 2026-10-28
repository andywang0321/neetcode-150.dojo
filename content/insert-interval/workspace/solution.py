def insert(intervals: list[list[int]], newInterval: list[int]) -> list[list[int]]:
    # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
    raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    _cases = [
        (([[1, 3], [6, 9]], [2, 5]), [[1, 5], [6, 9]]),
        (([[1, 2], [3, 5], [6, 7], [8, 10], [12, 16]], [4, 8]), [[1, 2], [3, 10], [12, 16]]),
        (([], [5, 7]), [[5, 7]]),
        (([[1, 2], [5, 5]], [5, 6]), [[1, 2], [5, 6]]),
    ]
    for _i, (_args, _want) in enumerate(_cases, 1):
        _got = insert(*_args)
        _ok = _got == _want
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} got={_got!r} want={_want!r}")
# --- end dojo ---
