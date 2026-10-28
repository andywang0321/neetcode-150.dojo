class Trie:
    def __init__(self):
        # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
        raise NotImplementedError

    def insert(self, word: str) -> None:
        # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
        raise NotImplementedError

    def search(self, word: str) -> bool:
        # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
        raise NotImplementedError

    def startsWith(self, prefix: str) -> bool:
        # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
        raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    _cases = [
        ([['insert', 'apple'], ['search', 'apple'], ['search', 'app'], ['startsWith', 'app'], ['insert', 'app'], ['search', 'app']], [None, True, False, True, None, True], []),
        ([['search', 'a'], ['startsWith', 'a'], ['insert', 'a'], ['search', 'a'], ['startsWith', 'ab'], ['search', 'ab']], [False, False, None, True, False, False], []),
        ([['insert', 'app'], ['search', 'app'], ['insert', 'apple'], ['search', 'app'], ['search', 'apple'], ['search', 'appl'], ['startsWith', 'appl']], [None, True, None, True, True, False, True], []),
    ]
    for _i, (_ops, _want, _ctor) in enumerate(_cases, 1):
        _obj = Trie(*_ctor)
        _got = [getattr(_obj, _m)(*_a) for _m, *_a in _ops]
        _ok = _got == _want
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} got={_got!r} want={_want!r}")
# --- end dojo ---
