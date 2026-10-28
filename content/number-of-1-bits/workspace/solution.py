def hamming_weight(n: int) -> int:
    # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
    raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    _cases = [
        ((11,), 3),
        ((128,), 1),
        ((2147483645,), 30),
        ((1,), 1),
        ((2147483647,), 31),
    ]
    for _i, (_args, _want) in enumerate(_cases, 1):
        _got = hamming_weight(*_args)
        _ok = _got == _want
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} got={_got!r} want={_want!r}")
# --- end dojo ---
