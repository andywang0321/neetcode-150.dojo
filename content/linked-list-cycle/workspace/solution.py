def has_cycle(next_node: list[int]) -> bool:
    # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
    raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    _cases = [
        (([1, 2, 3, 1],), True),
        (([1, 0],), True),
        (([-1],), False),
        (([1, 2, 3, 4, 2],), True),
    ]
    for _i, (_args, _want) in enumerate(_cases, 1):
        _got = has_cycle(*_args)
        _ok = _got == _want
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} got={_got!r} want={_want!r}")
# --- end dojo ---
