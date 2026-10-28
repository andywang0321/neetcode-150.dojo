def multiply(num1: str, num2: str) -> str:
    # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
    raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    _cases = [
        (('2', '3'), '6'),
        (('123', '456'), '56088'),
        (('0', '0'), '0'),
        (('100', '100'), '10000'),
    ]
    for _i, (_args, _want) in enumerate(_cases, 1):
        _got = multiply(*_args)
        _ok = _got == _want
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} got={_got!r} want={_want!r}")
# --- end dojo ---
