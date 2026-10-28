def longest_seqlen(nums: list[int]) -> int:
    # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
    raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    _cases = [
        (([2, 20, 4, 10, 3, 4, 5],), 4),
        (([0, 3, 2, 5, 4, 6, 1, 1],), 7),
        (([],), 0),
        (([100, 4, 200, 1, 3, 2],), 4),
    ]
    for _i, (_args, _want) in enumerate(_cases, 1):
        _got = longest_seqlen(*_args)
        _ok = _got == _want
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} got={_got!r} want={_want!r}")
# --- end dojo ---
