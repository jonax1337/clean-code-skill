You can now split an expense by percentage with `tabtally add --percent NAME=PCT`. All 51 tests pass, 17 of them new. I also ran it by hand: `--percent alice=50 --percent bob=60` fails with `error: percentages must add up to 100, not 110`.

```console
$ python -m tabtally add --paid-by alice --amount 10.00 --description Taxi --percent alice=50 --percent bob=30 --percent carol=20
added #1: 10.00 for Taxi
```

**How it behaves**
- **Either `--with` or `--percent`:** each `add` must use one of them, and using both is an argparse usage error.
- **Bad input saves nothing:** it exits with code 2 and prints `error: ...` (the same handling as a bad amount) when:
  - a value isn't in `NAME=PCT` form with a whole number (`bob=12.5`, `bob=-5`, `=50`);
  - the percentages don't add up to exactly 100;
  - the same person is listed twice.
- **One choice you may want to change:** each percentage must be between 1 and 100, so `bob=0` is rejected. Giving someone 0% would only add a person who owes nothing. If you'd rather allow 0, it's a one-line change.
- **Cents are never lost:** the split uses the same allocation as the equal split, so the shares always add up to the full amount. For example, 0.01 split 50/50 gives one person 0.01 and the other 0.00.

**Changes**
- `tabtally/splitting.py`: new `split_by_percent(cents, percents)`. I moved the duplicate-name check into a helper, `_reject_duplicates`, which both splits now use, so it isn't written twice (G5).
- `tabtally/cli.py`: `--with` and `--percent` are now alternatives and one is required. New `_split` picks the split, and `_parse_percent_share` reads each `NAME=PCT` value. The pattern is a named constant, `PERCENT_SHARE` (G25).
- `tests/test_splitting.py` and `tests/test_cli.py`: tests for normal splits, rounding, a 100% share, totals of 99 and 101, percentages of 0 and 101, malformed values, duplicates, and combining the two options.
- `README.md`: documents the new option.

Nothing is committed yet.