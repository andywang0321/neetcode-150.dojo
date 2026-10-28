def max_coins(nums: list[int]) -> int:
    # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
    raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    _cases = [
        (([3, 1, 5, 8],), 167),
        (([1, 5],), 10),
        (([],), 0),
        (([8],), 8),
    ]
    for _i, (_args, _want) in enumerate(_cases, 1):
        _got = max_coins(*_args)
        _ok = _got == _want
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} got={_got!r} want={_want!r}")
# --- end dojo ---
