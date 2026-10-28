def count_bits(n: int) -> list[int]:
    # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
    raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    _cases = [
        ((2,), [0, 1, 1]),
        ((5,), [0, 1, 1, 2, 1, 2]),
        ((0,), [0]),
    ]
    for _i, (_args, _want) in enumerate(_cases, 1):
        _got = count_bits(*_args)
        _ok = _got == _want
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} got={_got!r} want={_want!r}")
# --- end dojo ---
