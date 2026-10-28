def is_valid_bst(root: list | None) -> bool:
    # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
    raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    _cases = [
        (([2, [1, None, None], [3, None, None]],), True),
        (([5, [1, None, None], [4, [3, None, None], [6, None, None]]],), False),
        (([5, [4, None, None], [6, [3, None, None], [7, None, None]]],), False),
    ]
    for _i, (_args, _want) in enumerate(_cases, 1):
        _got = is_valid_bst(*_args)
        _ok = _got == _want
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} got={_got!r} want={_want!r}")
# --- end dojo ---
