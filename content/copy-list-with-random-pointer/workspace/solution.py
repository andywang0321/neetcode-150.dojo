def copy_random_list(head: list[list[int]]) -> list[list[int]]:
    # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
    raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    _cases = [
        (([[7, -1], [13, 0], [11, 4], [10, 2], [1, 0]],), None),
        (([[1, 1], [2, 1]],), None),
        (([[3, -1], [3, 0], [3, -1]],), None),
    ]
    for _i, (_args, _want) in enumerate(_cases, 1):
        _got = copy_random_list(*_args)
        if _want is None:  # dojo checks this one by property
            print(f"case {_i}: got={_got!r}")
            continue
        _ok = _got == _want
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} got={_got!r} want={_want!r}")
# --- end dojo ---
