`tabtally add` now takes `--percent NAME=PCT`, which you can repeat to split an expense by percentage. All 53 tests pass (34 existing, 19 new).

```console
$ python -m tabtally add --paid-by alice --amount 30.00 --description Pizza --percent alice=50 --percent bob=30 --percent carol=20
```

**How it works**
- **One or the other:** `add` now needs exactly one of `--with` or `--percent`. Giving neither or both is rejected with the usual usage error (exit code 2). The existing `--with` behaviour hasn't changed.
- **Rounding:** splits go through the existing `allocate`, so no cents are lost. For example, 10.01 split 50/50 becomes 5.01 and 5.00.
- **Rejected input** (exit code 2, and nothing is saved):
  - percentages that don't add up to 100
  - a value that isn't `NAME=PCT`
  - a percentage that isn't a whole number from 1 to 100
  - a person listed twice

**Where the code is**
- `tabtally/splitting.py` has the new `parse_percent` and `split_by_percent`. I moved the duplicate-name check into a small helper so both split types use it.
- `tabtally/cli.py` adds the option.
- The README's command table has a row for the new form.
- New tests are in `tests/test_splitting.py` and `tests/test_cli.py`.

**Decision for you:** I chose to reject `0%`, because a person who owes nothing doesn't need to be in the split. If you'd rather allow zero shares, it's a one-line change in `parse_percent`.