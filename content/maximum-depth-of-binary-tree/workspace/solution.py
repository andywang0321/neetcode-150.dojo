def max_depth(root: list | None) -> int:
    # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
    raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    _cases = [
        (([3, [9, None, None], [20, [15, None, None], [7, None, None]]],), 3),
        (([1, None, [2, None, None]],), 2),
        ((None,), 0),
    ]
    for _i, (_args, _want) in enumerate(_cases, 1):
        _got = max_depth(*_args)
        _ok = _got == _want
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} got={_got!r} want={_want!r}")
# --- end dojo ---
