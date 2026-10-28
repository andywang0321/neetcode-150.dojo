def set_zeroes(matrix: list[list[int]]) -> None:
    # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
    raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    import copy

    _cases = [
        (([[1, 1, 1], [1, 0, 1], [1, 1, 1]],), [[[1, 0, 1], [0, 0, 0], [1, 0, 1]]]),
        (([[0, 1, 2, 0], [3, 4, 5, 2], [1, 3, 1, 5]],), [[[0, 0, 0, 0], [0, 4, 5, 0], [0, 3, 1, 0]]]),
        (([[1, 0], [2, 3]],), [[[0, 0], [2, 0]]]),
    ]
    for _i, (_args, _want) in enumerate(_cases, 1):
        _call = copy.deepcopy(list(_args))
        set_zeroes(*_call)  # in place: the arguments are the result
        _ok = _call == _want
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} args={_call!r} want={_want!r}")
# --- end dojo ---
