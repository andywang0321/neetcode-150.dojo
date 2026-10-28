def ladder_length(beginWord: str, endWord: str, wordList: list[str]) -> int:
    # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
    raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    _cases = [
        (('hit', 'cog', ['hot', 'dot', 'dog', 'lot', 'log', 'cog']), 5),
        (('hit', 'cog', ['hot', 'dot', 'dog', 'lot', 'log']), 0),
        (('hot', 'dot', ['dot']), 2),
        (('hit', 'cog', ['hot', 'cog']), 0),
    ]
    for _i, (_args, _want) in enumerate(_cases, 1):
        _got = ladder_length(*_args)
        _ok = _got == _want
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} got={_got!r} want={_want!r}")
# --- end dojo ---
