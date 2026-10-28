class KthLargest:
    def __init__(self, k: int, nums: list[int]):
        # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
        raise NotImplementedError

    def add(self, val: int) -> int:
        # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
        raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    _cases = [
        ([['__init__', 3, [4, 5, 8, 2]], ['add', 3], ['add', 5], ['add', 10], ['add', 9], ['add', 4]], [None, 4, 5, 5, 8, 8], [3, [4, 5, 8, 2]]),
        ([['__init__', 4, [7, 7, 7, 7, 8, 3]], ['add', 2], ['add', 10], ['add', 9], ['add', 9]], [None, 7, 7, 7, 8], [4, [7, 7, 7, 7, 8, 3]]),
        ([['__init__', 1, []], ['add', -3]], [None, -3], [1, []]),
        ([['__init__', 3, [7, 7]], ['add', 7]], [None, 7], [3, [7, 7]]),
    ]
    for _i, (_ops, _want, _ctor) in enumerate(_cases, 1):
        _obj = KthLargest(*_ctor)
        _got = [getattr(_obj, _m)(*_a) for _m, *_a in _ops]
        _ok = _got == _want
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} got={_got!r} want={_want!r}")
# --- end dojo ---
