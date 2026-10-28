def lowest_common_ancestor(root: list | None, p: int, q: int) -> int:
    # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
    raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    _cases = [
        (([6, [2, [0, None, None], [4, [3, None, None], [5, None, None]]], [8, [7, None, None], [9, None, None]]], 2, 8), 6),
        (([6, [2, [0, None, None], [4, [3, None, None], [5, None, None]]], [8, [7, None, None], [9, None, None]]], 2, 4), 2),
        (([2, [1, None, None], None], 2, 1), 2),
        (([6, [2, [0, None, None], [4, [3, None, None], [5, None, None]]], [8, [7, None, None], [9, None, None]]], 3, 5), 4),
    ]
    for _i, (_args, _want) in enumerate(_cases, 1):
        _got = lowest_common_ancestor(*_args)
        _ok = _got == _want
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} got={_got!r} want={_want!r}")
# --- end dojo ---
