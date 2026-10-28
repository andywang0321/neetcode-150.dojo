def find_median_sorted_arrays(nums1: list[int], nums2: list[int]) -> float:
    # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
    raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    _COMPARE = 'approx:1e-5'  # every case here compares this way
    _cases = [
        (([1, 3], [2]), 2.0),
        (([1, 2], [3, 4]), 2.5),
        (([], [1]), 1.0),
        (([1], [2]), 1.5),
    ]

    def _same(_got, _want):
        if _COMPARE == 'approx:1e-5':  # float tolerance
            return abs(_got - _want) <= 1e-5
        return _got == _want
    for _i, (_args, _want) in enumerate(_cases, 1):
        _got = find_median_sorted_arrays(*_args)
        _ok = _same(_got, _want)
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} got={_got!r} want={_want!r}")
# --- end dojo ---
