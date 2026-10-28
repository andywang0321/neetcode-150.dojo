def is_n_straight_hand(hand: list[int], group_size: int) -> bool:
    # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
    raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    _cases = [
        (([1, 2, 3, 6, 2, 3, 4, 7, 8], 3), True),
        (([1, 2, 3, 4, 5], 4), False),
        (([1], 1), True),
        (([1, 2, 3, 4, 6, 7], 3), False),
    ]
    for _i, (_args, _want) in enumerate(_cases, 1):
        _got = is_n_straight_hand(*_args)
        _ok = _got == _want
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} got={_got!r} want={_want!r}")
# --- end dojo ---
