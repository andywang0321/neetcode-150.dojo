def least_interval(tasks: list[str], n: int) -> int:
    # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
    raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    _cases = [
        ((['A', 'A', 'A', 'B', 'B', 'B'], 2), 8),
        ((['A', 'C', 'A', 'B', 'D', 'B'], 1), 6),
        ((['A', 'A', 'A', 'B', 'B', 'B'], 3), 10),
        ((['A', 'A', 'A', 'B', 'B', 'B'], 0), 6),
        ((['A', 'A', 'A', 'B', 'B', 'B', 'C', 'C', 'C', 'D', 'D', 'D'], 1), 12),
    ]
    for _i, (_args, _want) in enumerate(_cases, 1):
        _got = least_interval(*_args)
        _ok = _got == _want
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} got={_got!r} want={_want!r}")
# --- end dojo ---
