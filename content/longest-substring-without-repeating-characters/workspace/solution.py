def length_of_longest_substring(s: str) -> int:
    # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
    raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    _cases = [
        (('abcabcbb',), 3),
        (('bbbbb',), 1),
        (('pwwkew',), 3),
        (('',), 0),
        ((' ',), 1),
    ]
    for _i, (_args, _want) in enumerate(_cases, 1):
        _got = length_of_longest_substring(*_args)
        _ok = _got == _want
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} got={_got!r} want={_want!r}")
# --- end dojo ---
