def can_finish(num_courses: int, prerequisites: list[list[int]]) -> bool:
    # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
    raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    _cases = [
        ((2, [[1, 0]]), True),
        ((2, [[1, 0], [0, 1]]), False),
        ((1, []), True),
        ((3, [[0, 1], [1, 2], [2, 0]]), False),
    ]
    for _i, (_args, _want) in enumerate(_cases, 1):
        _got = can_finish(*_args)
        _ok = _got == _want
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} got={_got!r} want={_want!r}")
# --- end dojo ---
