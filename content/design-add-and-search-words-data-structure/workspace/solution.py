class WordDictionary:
    def __init__(self):
        # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
        raise NotImplementedError

    def addWord(self, word: str) -> None:
        # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
        raise NotImplementedError

    def search(self, word: str) -> bool:
        # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
        raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    _cases = [
        ([['addWord', 'bad'], ['addWord', 'dad'], ['addWord', 'mad'], ['search', 'pad'], ['search', 'bad'], ['search', '.ad'], ['search', 'b..']], [None, None, None, False, True, True, True], []),
        ([['search', '.'], ['addWord', 'a'], ['search', '.'], ['search', 'a'], ['search', 'b'], ['search', 'aa']], [False, None, True, True, False, False], []),
        ([['addWord', 'ba'], ['search', 'ba.'], ['search', '.a'], ['search', 'b.'], ['search', '..'], ['search', 'bad']], [None, False, True, True, True, False], []),
        ([['addWord', 'bad'], ['search', 'ba'], ['search', '.ad'], ['search', 'b.d'], ['search', 'b..'], ['search', 'bad.']], [None, False, True, True, True, False], []),
    ]
    for _i, (_ops, _want, _ctor) in enumerate(_cases, 1):
        _obj = WordDictionary(*_ctor)
        _got = [getattr(_obj, _m)(*_a) for _m, *_a in _ops]
        _ok = _got == _want
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} got={_got!r} want={_want!r}")
# --- end dojo ---
