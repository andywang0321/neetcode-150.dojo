def longest_common_subsequence(text1: str, text2: str) -> int:
    # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
    raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    _cases = [
        (('abcde', 'ace'), 3),
        (('abc', 'abc'), 3),
        (('abc', 'def'), 0),
        (('a', 'a'), 1),
        (('aaa', 'aa'), 2),
    ]
    for _i, (_args, _want) in enumerate(_cases, 1):
        _got = longest_common_subsequence(*_args)
        _ok = _got == _want
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} got={_got!r} want={_want!r}")
# --- end dojo ---
