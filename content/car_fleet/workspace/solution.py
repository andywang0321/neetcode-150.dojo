def car_fleet(target: int, position: list[int], speed: list[int]) -> int:
    # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
    raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    _cases = [
        ((10, [1, 4], [3, 2]), 1),
        ((10, [4, 1, 0, 7], [2, 2, 1, 1]), 3),
        ((12, [10, 8, 0, 5, 3], [2, 4, 1, 1, 3]), 3),
    ]
    for _i, (_args, _want) in enumerate(_cases, 1):
        _got = car_fleet(*_args)
        _ok = _got == _want
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} got={_got!r} want={_want!r}")
# --- end dojo ---
