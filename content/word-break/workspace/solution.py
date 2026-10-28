def word_break(s: str, word_dict: list[str]) -> bool:
    # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
    raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    _cases = [
        (('leetcode', ['leet', 'code']), True),
        (('applepenapple', ['apple', 'pen']), True),
        (('catsandog', ['cats', 'dog', 'sand', 'and', 'cat']), False),
        (('a', ['a']), True),
        (('cars', ['car', 'ca', 'rs']), True),
    ]
    for _i, (_args, _want) in enumerate(_cases, 1):
        _got = word_break(*_args)
        _ok = _got == _want
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} got={_got!r} want={_want!r}")
# --- end dojo ---
