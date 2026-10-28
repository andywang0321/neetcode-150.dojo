class LRUCache:
    def __init__(self, capacity: int):
        # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
        raise NotImplementedError

    def get(self, key: int) -> int:
        # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
        raise NotImplementedError

    def put(self, key: int, value: int) -> None:
        # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
        raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    _cases = [
        ([['__init__', 2], ['put', 1, 1], ['put', 2, 2], ['get', 1], ['put', 3, 3], ['get', 2], ['put', 4, 4], ['get', 1], ['get', 3], ['get', 4]], [None, None, None, 1, None, -1, None, -1, 3, 4], [2]),
        ([['__init__', 1], ['put', 0, 0], ['get', 0], ['put', 1, 0], ['get', 0], ['get', 1], ['put', 1, 7], ['get', 1]], [None, None, 0, None, -1, 0, None, 7], [1]),
        ([['__init__', 2], ['put', 1, 1], ['put', 2, 2], ['put', 1, 10], ['put', 3, 3], ['get', 2], ['get', 1], ['get', 3]], [None, None, None, None, None, -1, 10, 3], [2]),
    ]
    for _i, (_ops, _want, _ctor) in enumerate(_cases, 1):
        _obj = LRUCache(*_ctor)
        _got = [getattr(_obj, _m)(*_a) for _m, *_a in _ops]
        _ok = _got == _want
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} got={_got!r} want={_want!r}")
# --- end dojo ---
