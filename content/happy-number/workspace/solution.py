def is_happy(n: int) -> bool:
    # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
    raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    _cases = [
        ((19,), True),
        ((2,), False),
        ((1,), True),
        ((4,), False),
    ]
    for _i, (_args, _want) in enumerate(_cases, 1):
        _got = is_happy(*_args)
        _ok = _got == _want
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} got={_got!r} want={_want!r}")
# --- end dojo ---
