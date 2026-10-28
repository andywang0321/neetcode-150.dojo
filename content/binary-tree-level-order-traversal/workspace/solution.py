def level_order(root: list | None) -> list[list[int]]:
    # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
    raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    _cases = [
        (([3, [9, None, None], [20, [15, None, None], [7, None, None]]],), [[3], [9, 20], [15, 7]]),
        (([1, None, None],), [[1]]),
        ((None,), []),
        (([1, [2, [4, None, None], None], [3, None, None]],), [[1], [2, 3], [4]]),
    ]
    for _i, (_args, _want) in enumerate(_cases, 1):
        _got = level_order(*_args)
        _ok = _got == _want
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} got={_got!r} want={_want!r}")
# --- end dojo ---
