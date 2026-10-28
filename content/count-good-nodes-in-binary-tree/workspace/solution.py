def good_nodes(root: list | None) -> int:
    # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
    raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    _cases = [
        (([3, [1, [3, None, None], None], [4, [1, None, None], [5, None, None]]],), 4),
        (([3, [3, [4, None, None], [2, None, None]], None],), 3),
        (([1, None, None],), 1),
        (([2, [2, [2, None, None], None], None],), 3),
        (([-10000, [-10000, None, None], [10000, None, None]],), 3),
    ]
    for _i, (_args, _want) in enumerate(_cases, 1):
        _got = good_nodes(*_args)
        _ok = _got == _want
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} got={_got!r} want={_want!r}")
# --- end dojo ---
