def valid_anagram(s: str, t: str) -> bool:
    # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
    raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    _cases = [
        (('racecar', 'carrace'), True),
        (('jar', 'jam'), False),
        (('jarr', 'jar'), False),
        (('anagram', 'nagaram'), True),
    ]
    for _i, (_args, _want) in enumerate(_cases, 1):
        _got = valid_anagram(*_args)
        _ok = _got == _want
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} got={_got!r} want={_want!r}")
# --- end dojo ---
