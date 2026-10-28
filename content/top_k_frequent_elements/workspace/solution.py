def top_k_freq(nums: list[int], k: int) -> list[int]:
    # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
    raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    _COMPARE = 'sorted'  # every case here compares this way
    _cases = [
        (([1, 2, 2, 3, 3, 3], 2), [3, 2]),
        (([7, 7], 1), [7]),
        (([8], 1), [8]),
        (([1, 1, 1, 2, 2, 3], 2), [1, 2]),
    ]

    def _same(_got, _want):
        if _COMPARE == "sorted":  # dojo accepts any order here
            return sorted(map(repr, _got)) == sorted(map(repr, _want))
        return _got == _want
    for _i, (_args, _want) in enumerate(_cases, 1):
        _got = top_k_freq(*_args)
        _ok = _same(_got, _want)
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} got={_got!r} want={_want!r}")
# --- end dojo ---
