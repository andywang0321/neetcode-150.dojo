def rotate(matrix: list[list[int]]) -> None:
    # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
    raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    import copy

    _cases = [
        (([[1, 2, 3], [4, 5, 6], [7, 8, 9]],), [[[7, 4, 1], [8, 5, 2], [9, 6, 3]]]),
        (([[5, 1, 9, 11], [2, 4, 8, 10], [13, 3, 6, 7], [15, 14, 12, 16]],), [[[15, 13, 2, 5], [14, 3, 4, 1], [12, 6, 8, 9], [16, 7, 10, 11]]]),
        (([[7]],), [[[7]]]),
    ]
    for _i, (_args, _want) in enumerate(_cases, 1):
        _call = copy.deepcopy(list(_args))
        rotate(*_call)  # in place: the arguments are the result
        _ok = _call == _want
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} args={_call!r} want={_want!r}")
# --- end dojo ---
