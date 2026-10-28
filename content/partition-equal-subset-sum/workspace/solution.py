def can_partition(nums: list[int]) -> bool:
    # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
    raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    _cases = [
        (([1, 5, 11, 5],), True),
        (([1, 2, 3, 5],), False),
        (([2, 2],), True),
        (([1, 2, 5],), False),
    ]
    for _i, (_args, _want) in enumerate(_cases, 1):
        _got = can_partition(*_args)
        _ok = _got == _want
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} got={_got!r} want={_want!r}")
# --- end dojo ---
