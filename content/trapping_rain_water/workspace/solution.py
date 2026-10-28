def trap(height: list[int]) -> int:
    # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
    raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    _cases = [
        (([0, 2, 0, 3, 1, 0, 1, 3, 2, 1],), 9),
        (([4, 2, 0, 3, 2, 5],), 9),
        (([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1],), 6),
    ]
    for _i, (_args, _want) in enumerate(_cases, 1):
        _got = trap(*_args)
        _ok = _got == _want
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} got={_got!r} want={_want!r}")
# --- end dojo ---
