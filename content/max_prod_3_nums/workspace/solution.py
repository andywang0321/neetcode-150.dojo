def max_tri_prod(A: list[int]) -> int:
    # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
    raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    _cases = [
        (([1, 3, 4, 5],), 60),
        (([-2, -4, 5, 3],), 40),
        (([-3, -2, -1],), -6),
        (([0, 0, 0],), 0),
    ]
    for _i, (_args, _want) in enumerate(_cases, 1):
        _got = max_tri_prod(*_args)
        _ok = _got == _want
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} got={_got!r} want={_want!r}")
# --- end dojo ---
