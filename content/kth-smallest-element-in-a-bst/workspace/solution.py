def kth_smallest(root: list | None, k: int) -> int:
    # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
    raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    _cases = [
        (([3, [1, None, [2, None, None]], [4, None, None]], 1), 1),
        (([5, [3, [2, [1, None, None], None], [4, None, None]], [6, None, None]], 3), 3),
        (([1, None, [2, None, [3, None, None]]], 3), 3),
    ]
    for _i, (_args, _want) in enumerate(_cases, 1):
        _got = kth_smallest(*_args)
        _ok = _got == _want
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} got={_got!r} want={_want!r}")
# --- end dojo ---
