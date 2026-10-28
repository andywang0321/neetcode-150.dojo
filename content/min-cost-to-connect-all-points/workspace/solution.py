def min_cost_connect_points(points: list[list[int]]) -> int:
    # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
    raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    _cases = [
        (([[0, 0], [2, 2], [3, 10], [5, 2], [7, 0]],), 20),
        (([[3, 12], [-2, 5], [-4, 1]],), 18),
        (([[0, 0]],), 0),
        (([[-1000000, -1000000], [1000000, 1000000]],), 4000000),
    ]
    for _i, (_args, _want) in enumerate(_cases, 1):
        _got = min_cost_connect_points(*_args)
        _ok = _got == _want
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} got={_got!r} want={_want!r}")
# --- end dojo ---
