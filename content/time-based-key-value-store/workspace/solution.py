class TimeMap:
    def __init__(self):
        # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
        raise NotImplementedError

    def set(self, key: str, value: str, timestamp: int) -> None:
        # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
        raise NotImplementedError

    def get(self, key: str, timestamp: int) -> str:
        # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
        raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    _cases = [
        ([['set', 'foo', 'bar', 1], ['get', 'foo', 1], ['get', 'foo', 3], ['set', 'foo', 'bar2', 4], ['get', 'foo', 4], ['get', 'foo', 5]], [None, 'bar', 'bar', None, 'bar2', 'bar2'], []),
        ([['get', 'foo', 1], ['set', 'foo', 'a', 2], ['get', 'foo', 1], ['get', 'bar', 5]], ['', None, '', ''], []),
        ([['set', 'k1', 'v1', 1], ['set', 'k2', 'v2', 2], ['set', 'k1', 'v3', 3], ['get', 'k1', 2], ['get', 'k1', 3], ['get', 'k2', 3]], [None, None, None, 'v1', 'v3', 'v2'], []),
    ]
    for _i, (_ops, _want, _ctor) in enumerate(_cases, 1):
        _obj = TimeMap(*_ctor)
        _got = [getattr(_obj, _m)(*_a) for _m, *_a in _ops]
        _ok = _got == _want
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} got={_got!r} want={_want!r}")
# --- end dojo ---
