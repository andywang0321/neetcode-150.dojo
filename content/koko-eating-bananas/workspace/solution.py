def min_eating_speed(piles: list[int], h: int) -> int:
    # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
    raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    _cases = [
        (([3, 6, 7, 11], 8), 4),
        (([30, 11, 23, 4, 20], 5), 30),
        (([30, 11, 23, 4, 20], 6), 23),
        (([3, 6, 7, 11], 4), 11),
        (([5], 5), 1),
    ]
    for _i, (_args, _want) in enumerate(_cases, 1):
        _got = min_eating_speed(*_args)
        _ok = _got == _want
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} got={_got!r} want={_want!r}")
# --- end dojo ---
