def merge_two_lists(list1: list[int], list2: list[int]) -> list[int]:
    # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
    raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    _cases = [
        (([1, 2, 4], [1, 3, 4]), [1, 1, 2, 3, 4, 4]),
        (([], []), []),
        (([], [0]), [0]),
        (([1, 2], [3, 4, 5, 6]), [1, 2, 3, 4, 5, 6]),
    ]
    for _i, (_args, _want) in enumerate(_cases, 1):
        _got = merge_two_lists(*_args)
        _ok = _got == _want
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} got={_got!r} want={_want!r}")
# --- end dojo ---
