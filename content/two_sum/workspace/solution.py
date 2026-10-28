def twosum(nums: list[int], target: int) -> list[int]:
    # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
    raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    _cases = [
        (([3, 4, 5, 6], 7), [0, 1]),
        (([4, 5, 6], 10), [0, 2]),
        (([5, 5], 10), [0, 1]),
        (([1, 2, 5, 5], 10), [2, 3]),
    ]
    for _i, (_args, _want) in enumerate(_cases, 1):
        _got = twosum(*_args)
        _ok = _got == _want
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} got={_got!r} want={_want!r}")
# --- end dojo ---
