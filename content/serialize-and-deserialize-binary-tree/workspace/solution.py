def serialize(root: list | None) -> str:
    # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
    raise NotImplementedError

def deserialize(data: str) -> list | None:
    # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
    raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    _cases = [
        (([1, [2, None, None], [3, [4, None, None], [5, None, None]]],), None),
        ((None,), None),
        (([-1000, None, None],), None),
        (([7, [7, None, None], None],), None),
    ]
    for _i, (_args, _want) in enumerate(_cases, 1):
        _got = serialize(*_args)
        if _want is None:  # dojo checks this one by property
            print(f"case {_i}: got={_got!r}")
            continue
        _ok = _got == _want
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} got={_got!r} want={_want!r}")
# --- end dojo ---
