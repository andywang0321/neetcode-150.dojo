def max_product(nums: list[int]) -> int:
    # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
    raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    _cases = [
        (([2, 3, -2, 4],), 6),
        (([-2, 0, -1],), 0),
        (([-3],), -3),
        (([-2, -3, -4],), 12),
    ]
    for _i, (_args, _want) in enumerate(_cases, 1):
        _got = max_product(*_args)
        _ok = _got == _want
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} got={_got!r} want={_want!r}")
# --- end dojo ---
