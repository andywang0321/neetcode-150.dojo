def diameter(root: list | None) -> int:
    # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
    raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    _cases = [
        (([1, None, None],), 0),
        (([0, [1, None, [2, None, None]], None],), 2),
        (([0, [1, [2, None, [3, None, None]], [2, None, None]], [1, None, [2, [3, None, None], None]]],), 6),
        (([1, [2, [4, None, None], None], [3, None, None]],), 3),
    ]
    for _i, (_args, _want) in enumerate(_cases, 1):
        _got = diameter(*_args)
        _ok = _got == _want
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} got={_got!r} want={_want!r}")
# --- end dojo ---
