def num_distinct(s: str, t: str) -> int:
    # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
    raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    _cases = [
        (('rabbbit', 'rabbit'), 3),
        (('babgbag', 'bag'), 5),
        (('a', 'a'), 1),
        (('a', 'aa'), 0),
    ]
    for _i, (_args, _want) in enumerate(_cases, 1):
        _got = num_distinct(*_args)
        _ok = _got == _want
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} got={_got!r} want={_want!r}")
# --- end dojo ---
