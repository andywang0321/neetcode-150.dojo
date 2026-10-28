def min_distance(word1: str, word2: str) -> int:
    # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
    raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    _cases = [
        (('horse', 'ros'), 3),
        (('intention', 'execution'), 5),
        (('', ''), 0),
        (('abc', ''), 3),
    ]
    for _i, (_args, _want) in enumerate(_cases, 1):
        _got = min_distance(*_args)
        _ok = _got == _want
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} got={_got!r} want={_want!r}")
# --- end dojo ---
