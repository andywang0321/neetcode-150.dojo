def merge_triplets(triplets: list[list[int]], target: list[int]) -> bool:
    # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
    raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    _cases = [
        (([[2, 5, 3], [1, 8, 4], [1, 7, 5]], [2, 7, 5]), True),
        (([[3, 4, 5], [4, 5, 6]], [3, 2, 5]), False),
        (([[2, 5, 3], [2, 3, 4], [1, 2, 5], [5, 2, 3]], [5, 5, 5]), True),
        (([[1, 1, 1]], [1, 1, 1]), True),
        (([[2, 2, 2]], [2, 2, 3]), False),
    ]
    for _i, (_args, _want) in enumerate(_cases, 1):
        _got = merge_triplets(*_args)
        _ok = _got == _want
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} got={_got!r} want={_want!r}")
# --- end dojo ---
