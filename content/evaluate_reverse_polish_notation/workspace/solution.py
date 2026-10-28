def eval_rpn(tokens: list[str]) -> int:
    # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
    raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    _cases = [
        ((['1', '2', '+', '3', '*', '4', '-'],), 5),
        ((['2', '1', '+', '3', '*'],), 9),
        ((['4', '13', '5', '/', '+'],), 6),
        ((['10', '6', '9', '3', '+', '-11', '*', '/', '*', '17', '+', '5', '+'],), 22),
        ((['18'],), 18),
    ]
    for _i, (_args, _want) in enumerate(_cases, 1):
        _got = eval_rpn(*_args)
        _ok = _got == _want
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} got={_got!r} want={_want!r}")
# --- end dojo ---
