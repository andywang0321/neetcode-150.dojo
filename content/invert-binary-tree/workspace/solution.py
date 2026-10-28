def invert_tree(root: list | None) -> list | None:
    # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
    raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    _cases = [
        (([4, [2, [1, None, None], [3, None, None]], [7, [6, None, None], [9, None, None]]],), [4, [7, [9, None, None], [6, None, None]], [2, [3, None, None], [1, None, None]]]),
        (([2, [1, None, None], [3, None, None]],), [2, [3, None, None], [1, None, None]]),
        ((None,), None),
    ]
    for _i, (_args, _want) in enumerate(_cases, 1):
        _got = invert_tree(*_args)
        _ok = _got == _want
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} got={_got!r} want={_want!r}")
# --- end dojo ---
