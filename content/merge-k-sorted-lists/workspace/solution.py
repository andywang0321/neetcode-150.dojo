def merge_k_lists(lists: list[list[int]]) -> list[int]:
    # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
    raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    _cases = [
        (([[1, 4, 5], [1, 3, 4], [2, 6]],), [1, 1, 2, 3, 4, 4, 5, 6]),
        (([],), []),
        (([[]],), []),
        (([[], [0], []],), [0]),
        (([[5], [1], [3]],), [1, 3, 5]),
    ]
    for _i, (_args, _want) in enumerate(_cases, 1):
        _got = merge_k_lists(*_args)
        _ok = _got == _want
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} got={_got!r} want={_want!r}")
# --- end dojo ---
