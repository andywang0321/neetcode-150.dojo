def spiral_order(matrix: list[list[int]]) -> list[int]:
    # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
    raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    _cases = [
        (([[1, 2, 3], [4, 5, 6], [7, 8, 9]],), [1, 2, 3, 6, 9, 8, 7, 4, 5]),
        (([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]],), [1, 2, 3, 4, 8, 12, 11, 10, 9, 5, 6, 7]),
        (([[7]],), [7]),
        (([[1, 2, 3, 4]],), [1, 2, 3, 4]),
    ]
    for _i, (_args, _want) in enumerate(_cases, 1):
        _got = spiral_order(*_args)
        _ok = _got == _want
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} got={_got!r} want={_want!r}")
# --- end dojo ---
