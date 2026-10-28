def reorder_list(head: list[int]) -> None:
    # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
    raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    import copy

    _cases = [
        (([1, 2, 3, 4],), [[1, 4, 2, 3]]),
        (([1, 2, 3, 4, 5],), [[1, 5, 2, 4, 3]]),
        (([1],), [[1]]),
    ]
    for _i, (_args, _want) in enumerate(_cases, 1):
        _call = copy.deepcopy(list(_args))
        reorder_list(*_call)  # in place: the arguments are the result
        _ok = _call == _want
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} args={_call!r} want={_want!r}")
# --- end dojo ---
