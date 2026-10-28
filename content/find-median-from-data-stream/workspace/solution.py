class MedianFinder:
    def __init__(self):
        # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
        raise NotImplementedError

    def addNum(self, num: int) -> None:
        # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
        raise NotImplementedError

    def findMedian(self) -> float:
        # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
        raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    _cases = [
        ([['addNum', 1], ['addNum', 2], ['findMedian'], ['addNum', 3], ['findMedian']], [None, None, 1.5, None, 2.0], []),
        ([['addNum', 5], ['findMedian']], [None, 5.0], []),
        ([['addNum', -100000], ['addNum', 100000], ['findMedian'], ['addNum', 0], ['findMedian']], [None, None, 0.0, None, 0.0], []),
        ([['addNum', 1], ['addNum', 1], ['findMedian'], ['addNum', 1], ['findMedian']], [None, None, 1.0, None, 1.0], []),
    ]
    for _i, (_ops, _want, _ctor) in enumerate(_cases, 1):
        _obj = MedianFinder(*_ctor)
        _got = [getattr(_obj, _m)(*_a) for _m, *_a in _ops]
        _ok = _got == _want
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} got={_got!r} want={_want!r}")
# --- end dojo ---
