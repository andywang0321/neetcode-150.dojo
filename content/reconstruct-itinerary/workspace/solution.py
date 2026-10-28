def find_itinerary(tickets: list[list[str]]) -> list[str]:
    # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
    raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    _cases = [
        (([['MUC', 'LHR'], ['JFK', 'MUC'], ['SFO', 'SJC'], ['LHR', 'SFO']],), ['JFK', 'MUC', 'LHR', 'SFO', 'SJC']),
        (([['JFK', 'SFO'], ['JFK', 'ATL'], ['SFO', 'ATL'], ['ATL', 'JFK'], ['ATL', 'SFO']],), ['JFK', 'ATL', 'JFK', 'SFO', 'ATL', 'SFO']),
        (([['JFK', 'AAA']],), ['JFK', 'AAA']),
        (([['JFK', 'KUL'], ['JFK', 'NRT'], ['NRT', 'JFK']],), ['JFK', 'NRT', 'JFK', 'KUL']),
    ]
    for _i, (_args, _want) in enumerate(_cases, 1):
        _got = find_itinerary(*_args)
        _ok = _got == _want
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} got={_got!r} want={_want!r}")
# --- end dojo ---
