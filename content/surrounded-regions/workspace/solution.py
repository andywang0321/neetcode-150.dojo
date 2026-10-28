def solve(board: list[list[str]]) -> None:
    # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
    raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    import copy

    _cases = [
        (([['X', 'X', 'X', 'X'], ['X', 'O', 'O', 'X'], ['X', 'X', 'O', 'X'], ['X', 'O', 'X', 'X']],), [[['X', 'X', 'X', 'X'], ['X', 'X', 'X', 'X'], ['X', 'X', 'X', 'X'], ['X', 'O', 'X', 'X']]]),
        (([['X']],), [[['X']]]),
        (([['O', 'O'], ['O', 'O']],), [[['O', 'O'], ['O', 'O']]]),
        (([['X', 'X', 'X'], ['X', 'O', 'X'], ['X', 'X', 'X']],), [[['X', 'X', 'X'], ['X', 'X', 'X'], ['X', 'X', 'X']]]),
    ]
    for _i, (_args, _want) in enumerate(_cases, 1):
        _call = copy.deepcopy(list(_args))
        solve(*_call)  # in place: the arguments are the result
        _ok = _call == _want
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} args={_call!r} want={_want!r}")
# --- end dojo ---
