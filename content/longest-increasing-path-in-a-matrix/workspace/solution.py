def longest_increasing_path(matrix: list[list[int]]) -> int:
    # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
    raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    _cases = [
        (([[9, 9, 4], [6, 6, 8], [2, 1, 1]],), 4),
        (([[3, 4, 5], [3, 2, 6], [2, 2, 1]],), 4),
        (([[1]],), 1),
        (([[1, 1], [1, 1]],), 1),
    ]
    for _i, (_args, _want) in enumerate(_cases, 1):
        _got = longest_increasing_path(*_args)
        _ok = _got == _want
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} got={_got!r} want={_want!r}")
# --- end dojo ---
