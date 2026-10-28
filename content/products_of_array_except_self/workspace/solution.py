def prod_except_self(nums: list[int]) -> list[int]:
    # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
    raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    _cases = [
        (([1, 2, 4, 6],), [48, 24, 12, 8]),
        (([-1, 0, 1, 2, 3],), [0, -6, 0, 0, 0]),
        (([2, 3],), [3, 2]),
    ]
    for _i, (_args, _want) in enumerate(_cases, 1):
        _got = prod_except_self(*_args)
        _ok = _got == _want
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} got={_got!r} want={_want!r}")
# --- end dojo ---
