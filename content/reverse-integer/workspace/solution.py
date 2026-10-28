def reverse(x: int) -> int:
    # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
    raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    _cases = [
        ((123,), 321),
        ((-123,), -321),
        ((120,), 21),
        ((1534236469,), 0),
        ((-2147483412,), -2143847412),
    ]
    for _i, (_args, _want) in enumerate(_cases, 1):
        _got = reverse(*_args)
        _ok = _got == _want
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} got={_got!r} want={_want!r}")
# --- end dojo ---
