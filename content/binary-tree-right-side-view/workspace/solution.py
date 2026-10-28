def right_side_view(root: list | None) -> list[int]:
    # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
    raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    _cases = [
        (([1, [2, None, [5, None, None]], [3, None, [4, None, None]]],), [1, 3, 4]),
        (([1, [2, [4, [5, None, None], None], None], [3, None, None]],), [1, 3, 4, 5]),
        (([1, None, [3, None, None]],), [1, 3]),
        ((None,), []),
        (([1, [2, None, None], None],), [1, 2]),
    ]
    for _i, (_args, _want) in enumerate(_cases, 1):
        _got = right_side_view(*_args)
        _ok = _got == _want
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} got={_got!r} want={_want!r}")
# --- end dojo ---
