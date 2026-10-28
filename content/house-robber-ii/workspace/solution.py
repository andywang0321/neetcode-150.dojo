def rob(nums: list[int]) -> int:
    # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
    raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    _cases = [
        (([2, 3, 2],), 3),
        (([1, 2, 3, 1],), 4),
        (([1, 2, 3],), 3),
        (([5],), 5),
        (([4, 1, 1, 4],), 5),
    ]
    for _i, (_args, _want) in enumerate(_cases, 1):
        _got = rob(*_args)
        _ok = _got == _want
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} got={_got!r} want={_want!r}")
# --- end dojo ---
