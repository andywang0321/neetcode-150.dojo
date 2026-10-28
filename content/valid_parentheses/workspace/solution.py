def is_valid(s: str) -> bool:
    # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
    raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    _cases = [
        (('[]',), True),
        (('([{}])',), True),
        (('[(])',), False),
        (('(',), False),
        ((')',), False),
        (('()',), True),
        (('',), True),
        (('(((((((',), False),
        ((']]]]',), False),
        (('([)]',), False),
    ]
    for _i, (_args, _want) in enumerate(_cases, 1):
        _got = is_valid(*_args)
        _ok = _got == _want
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} got={_got!r} want={_want!r}")
# --- end dojo ---
