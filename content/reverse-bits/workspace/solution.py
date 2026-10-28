def reverse_bits(n: int) -> int:
    # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
    raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    _cases = [
        ((43261596,), 964176192),
        ((2147483644,), 1073741822),
        ((0,), 0),
    ]
    for _i, (_args, _want) in enumerate(_cases, 1):
        _got = reverse_bits(*_args)
        _ok = _got == _want
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} got={_got!r} want={_want!r}")
# --- end dojo ---
