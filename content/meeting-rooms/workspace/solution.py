def can_attend_meetings(intervals: list[list[int]]) -> bool:
    # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
    raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    _cases = [
        (([[0, 30], [5, 10], [15, 20]],), False),
        (([[7, 10], [2, 4]],), True),
        (([],), True),
        (([[1, 5], [5, 10]],), True),
    ]
    for _i, (_args, _want) in enumerate(_cases, 1):
        _got = can_attend_meetings(*_args)
        _ok = _got == _want
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} got={_got!r} want={_want!r}")
# --- end dojo ---
