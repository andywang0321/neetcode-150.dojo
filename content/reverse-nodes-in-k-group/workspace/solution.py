def reverse_k_group(head: list[int], k: int) -> list[int]:
    # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
    raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    _cases = [
        (([1, 2, 3, 4, 5], 2), [2, 1, 4, 3, 5]),
        (([1, 2, 3, 4, 5], 3), [3, 2, 1, 4, 5]),
        (([1, 2, 3], 3), [3, 2, 1]),
        (([3, 1, 2, 3], 2), [1, 3, 3, 2]),
    ]
    for _i, (_args, _want) in enumerate(_cases, 1):
        _got = reverse_k_group(*_args)
        _ok = _got == _want
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} got={_got!r} want={_want!r}")
# --- end dojo ---
