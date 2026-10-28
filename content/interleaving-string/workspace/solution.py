def interleaving_string(s1: str, s2: str, s3: str) -> bool:
    # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
    raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    _cases = [
        (('aabcc', 'dbbca', 'aadbbcbcac'), True),
        (('aabcc', 'dbbca', 'aadbbbaccc'), False),
        (('', '', ''), True),
        (('', 'ab', 'ab'), True),
        (('a', 'b', 'abc'), False),
    ]
    for _i, (_args, _want) in enumerate(_cases, 1):
        _got = interleaving_string(*_args)
        _ok = _got == _want
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} got={_got!r} want={_want!r}")
# --- end dojo ---
