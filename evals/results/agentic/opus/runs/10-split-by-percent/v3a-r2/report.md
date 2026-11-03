`tabtally add` now takes `--percent NAME=PCT`, so you can split an expense by percentage. All 50 tests pass: the 34 that already existed plus 16 new ones.

```console
$ python -m tabtally add --paid-by alice --amount 30.00 --description Pizza \
    --percent alice=50 --percent bob=30 --percent carol=20
```

**What changed**
- **`tabtally/splitting.py`**:
  - `parse_percent("alice=50")` returns `("alice", 50)`. Anything that isn't a whole number from 0 to 100 is rejected, including decimals, negatives, a missing name and values above 100.
  - `split_by_percent(cents, ...)` checks that the percentages total exactly 100 and that nobody is listed twice. It reuses the existing `allocate`, so the shares still add up to the full amount to the cent.
  - The duplicate-name check moved into a helper, `_reject_duplicates`, that both split functions use.
- **`tabtally/cli.py`**: `--with` and `--percent` are now alternatives: you must give exactly one of them. If you give both, or neither, argparse prints a usage error and exits with code 2. Bad percentages are reported the same way as other input errors (`error: ...`, exit code 2) and nothing is saved.
- **`README.md`**: added a row for the new form of `add`.
- **Tests**: new tests in `tests/test_splitting.py` for parsing, splitting, rounding, totals that aren't 100 and duplicate names. New tests in `tests/test_cli.py` for a full add → balances run, the error path, and combining `--with` with `--percent`.

**Choice to check:** a share of `0` is accepted, as in `bob=0`. That person is recorded with a share of 0.00. If you'd rather reject 0, it's a one-line change in `parse_percent`.