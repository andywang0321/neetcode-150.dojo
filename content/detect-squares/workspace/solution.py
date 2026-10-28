class DetectSquares:
    def __init__(self):
        # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
        raise NotImplementedError

    def add(self, point: list[int]) -> None:
        # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
        raise NotImplementedError

    def count(self, point: list[int]) -> int:
        # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
        raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    _cases = [
        ([['add', [3, 10]], ['add', [11, 2]], ['add', [3, 2]], ['count', [11, 10]], ['count', [14, 8]], ['add', [11, 2]], ['count', [11, 10]]], [None, None, None, 1, 0, None, 2], []),
        ([['add', [0, 0]], ['add', [2, 0]], ['add', [0, 3]], ['count', [2, 3]]], [None, None, None, 0], []),
        ([['count', [5, 5]]], [0], []),
    ]
    for _i, (_ops, _want, _ctor) in enumerate(_cases, 1):
        _obj = DetectSquares(*_ctor)
        _got = [getattr(_obj, _m)(*_a) for _m, *_a in _ops]
        _ok = _got == _want
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} got={_got!r} want={_want!r}")
# --- end dojo ---
