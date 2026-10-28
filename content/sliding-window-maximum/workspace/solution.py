def max_sliding_window(nums: list[int], k: int) -> list[int]:
    # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
    raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    _cases = [
        (([1, 3, -1, -3, 5, 3, 6, 7], 3), [3, 3, 5, 5, 6, 7]),
        (([1], 1), [1]),
        (([4, 2, 7], 3), [7]),
        (([-1, -3, -2], 2), [-1, -2]),
    ]
    for _i, (_args, _want) in enumerate(_cases, 1):
        _got = max_sliding_window(*_args)
        _ok = _got == _want
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} got={_got!r} want={_want!r}")
# --- end dojo ---
