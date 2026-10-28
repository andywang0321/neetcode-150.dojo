def find_target_sum_ways(nums: list[int], target: int) -> int:
    # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
    raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    _cases = [
        (([1, 1, 1, 1, 1], 3), 5),
        (([1], 1), 1),
        (([1, 1, 1, 1, 1], 6), 0),
        (([1, 1, 1, 1, 1], -3), 5),
    ]
    for _i, (_args, _want) in enumerate(_cases, 1):
        _got = find_target_sum_ways(*_args)
        _ok = _got == _want
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} got={_got!r} want={_want!r}")
# --- end dojo ---
