def valid_tree(n: int, edges: list[list[int]]) -> bool:
    # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
    raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    _cases = [
        ((5, [[0, 1], [0, 2], [0, 3], [1, 4]]), True),
        ((5, [[0, 1], [1, 2], [2, 3], [1, 3], [1, 4]]), False),
        ((4, [[0, 1], [2, 3]]), False),
        ((1, []), True),
        ((2, [[0, 1]]), True),
    ]
    for _i, (_args, _want) in enumerate(_cases, 1):
        _got = valid_tree(*_args)
        _ok = _got == _want
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} got={_got!r} want={_want!r}")
# --- end dojo ---
