def build_tree(preorder: list[int], inorder: list[int]) -> list | None:
    # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
    raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    _cases = [
        (([3, 9, 20, 15, 7], [9, 3, 15, 20, 7]), [3, [9, None, None], [20, [15, None, None], [7, None, None]]]),
        (([-1], [-1]), [-1, None, None]),
        (([1, 2, 3], [3, 2, 1]), [1, [2, [3, None, None], None], None]),
        (([1, 2, 3], [1, 2, 3]), [1, None, [2, None, [3, None, None]]]),
    ]
    for _i, (_args, _want) in enumerate(_cases, 1):
        _got = build_tree(*_args)
        _ok = _got == _want
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} got={_got!r} want={_want!r}")
# --- end dojo ---
