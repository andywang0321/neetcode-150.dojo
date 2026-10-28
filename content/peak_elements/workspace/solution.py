def find_a_peak(nums: list[int]) -> int:
    # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
    raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    _cases = [
        (([3, 5, 2, 4, 1],), None),
        (([4, 3, 2, 1],), 0),
        (([1, 2, 3, 4],), 3),
        (([1],), 0),
    ]
    for _i, (_args, _want) in enumerate(_cases, 1):
        _got = find_a_peak(*_args)
        if _want is None:  # dojo checks this one by property
            print(f"case {_i}: got={_got!r}")
            continue
        _ok = _got == _want
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} got={_got!r} want={_want!r}")
# --- end dojo ---
