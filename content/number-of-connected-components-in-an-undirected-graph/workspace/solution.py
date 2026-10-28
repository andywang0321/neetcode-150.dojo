def count_components(n: int, edges: list[list[int]]) -> int:
    # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
    raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    _cases = [
        ((5, [[0, 1], [1, 2], [3, 4]]), 2),
        ((5, [[0, 1], [1, 2], [2, 3], [3, 4]]), 1),
        ((3, []), 3),
        ((4, [[0, 1], [1, 2], [2, 0]]), 2),
        ((1, []), 1),
    ]
    for _i, (_args, _want) in enumerate(_cases, 1):
        _got = count_components(*_args)
        _ok = _got == _want
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} got={_got!r} want={_want!r}")
# --- end dojo ---
