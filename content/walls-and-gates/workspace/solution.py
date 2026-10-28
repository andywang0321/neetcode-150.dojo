def walls_and_gates(rooms: list[list[int]]) -> None:
    # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
    raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    import copy

    _cases = [
        (([[2147483647, -1, 0, 2147483647], [2147483647, 2147483647, 2147483647, -1], [2147483647, -1, 2147483647, -1], [0, -1, 2147483647, 2147483647]],), [[[3, -1, 0, 1], [2, 2, 1, -1], [1, -1, 2, -1], [0, -1, 3, 4]]]),
        (([[-1]],), [[[-1]]]),
        (([[0, -1, 2147483647]],), [[[0, -1, 2147483647]]]),
        (([[2147483647]],), [[[2147483647]]]),
    ]
    for _i, (_args, _want) in enumerate(_cases, 1):
        _call = copy.deepcopy(list(_args))
        walls_and_gates(*_call)  # in place: the arguments are the result
        _ok = _call == _want
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} args={_call!r} want={_want!r}")
# --- end dojo ---
