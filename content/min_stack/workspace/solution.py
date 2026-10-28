class MinStack:
    def __init__(self):
        # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
        raise NotImplementedError

    def push(self, val: int) -> None:
        # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
        raise NotImplementedError

    def pop(self) -> None:
        # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
        raise NotImplementedError

    def top(self) -> int:
        # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
        raise NotImplementedError

    def getMin(self) -> int:
        # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
        raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    _cases = [
        ([['push', 1], ['push', 2], ['push', 0], ['getMin'], ['pop'], ['top'], ['getMin']], [None, None, None, 0, None, 2, 1], []),
        ([['push', -2], ['push', 0], ['push', -3], ['getMin'], ['pop'], ['top'], ['getMin']], [None, None, None, -3, None, 0, -2], []),
        ([['push', 5], ['top'], ['getMin'], ['pop']], [None, 5, 5, None], []),
    ]
    for _i, (_ops, _want, _ctor) in enumerate(_cases, 1):
        _obj = MinStack(*_ctor)
        _got = [getattr(_obj, _m)(*_a) for _m, *_a in _ops]
        _ok = _got == _want
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} got={_got!r} want={_want!r}")
# --- end dojo ---
