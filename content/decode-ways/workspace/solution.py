def num_decodings(s: str) -> int:
    # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
    raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    _cases = [
        (('12',), 2),
        (('226',), 3),
        (('06',), 0),
        (('11106',), 2),
        (('10',), 1),
        (('1',), 1),
    ]
    for _i, (_args, _want) in enumerate(_cases, 1):
        _got = num_decodings(*_args)
        _ok = _got == _want
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} got={_got!r} want={_want!r}")
# --- end dojo ---
