def min_cost_climbing_stairs(cost: list[int]) -> int:
    # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
    raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    _cases = [
        (([10, 15, 20],), 15),
        (([1, 100, 1, 1, 1, 100, 1, 1, 100, 1],), 6),
        (([10, 15],), 10),
        (([0, 0],), 0),
    ]
    for _i, (_args, _want) in enumerate(_cases, 1):
        _got = min_cost_climbing_stairs(*_args)
        _ok = _got == _want
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} got={_got!r} want={_want!r}")
# --- end dojo ---
