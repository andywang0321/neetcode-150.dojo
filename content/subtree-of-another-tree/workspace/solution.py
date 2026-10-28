def is_subtree(root: list | None, sub_root: list | None) -> bool:
    # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
    raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    _cases = [
        (([3, [4, [1, None, None], [2, None, None]], [5, None, None]], [4, [1, None, None], [2, None, None]]), True),
        (([3, [4, [1, None, None], [2, [0, None, None], None]], [5, None, None]], [4, [1, None, None], [2, None, None]]), False),
        (([1, [2, None, None], None], [1, [2, None, None], None]), True),
        (([1, None, None], [2, None, None]), False),
    ]
    for _i, (_args, _want) in enumerate(_cases, 1):
        _got = is_subtree(*_args)
        _ok = _got == _want
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} got={_got!r} want={_want!r}")
# --- end dojo ---
