def erase_overlap_intervals(intervals: list[list[int]]) -> int:
    # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
    raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    _cases = [
        (([[1, 2], [2, 3], [3, 4], [1, 3]],), 1),
        (([[1, 2], [1, 2], [1, 2]],), 2),
        (([[1, 2], [2, 3]],), 0),
        (([[1, 2]],), 0),
        (([[1, 4], [2, 3], [3, 4]],), 1),
    ]
    for _i, (_args, _want) in enumerate(_cases, 1):
        _got = erase_overlap_intervals(*_args)
        _ok = _got == _want
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} got={_got!r} want={_want!r}")
# --- end dojo ---
