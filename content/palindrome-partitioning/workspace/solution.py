def partition(s: str) -> list[list[str]]:
    # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
    raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    _COMPARE = 'sorted'  # every case here compares this way
    _cases = [
        (('aab',), [['a', 'a', 'b'], ['aa', 'b']]),
        (('a',), [['a']]),
        (('aaa',), [['a', 'a', 'a'], ['a', 'aa'], ['aa', 'a'], ['aaa']]),
    ]

    def _same(_got, _want):
        if _COMPARE == "sorted":  # dojo accepts any order here
            return sorted(map(repr, _got)) == sorted(map(repr, _want))
        return _got == _want
    for _i, (_args, _want) in enumerate(_cases, 1):
        _got = partition(*_args)
        _ok = _same(_got, _want)
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} got={_got!r} want={_want!r}")
# --- end dojo ---
