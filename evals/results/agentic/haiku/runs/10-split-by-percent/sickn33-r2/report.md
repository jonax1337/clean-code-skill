`tabtally add` now takes `--percent NAME=PCT`, and all 45 tests pass (34 existing, 11 new). I did not commit.

```
$ python -m tabtally add --paid-by alice --amount 100 --description Dinner --percent alice=50 --percent bob=30 --percent carol=20
added #1: 100.00 for Dinner
$ python -m tabtally balances
alice 50.00
bob -30.00
carol -20.00
```

What changed:

- **`tabtally/cli.py`**: `--with` and `--percent` are now a required mutually exclusive pair, so you have to pick one and can't mix them. A new `parse_percent` accepts only `NAME=PCT` with a positive whole number. Anything else, such as `alice=33.3`, `alice`, or `alice=0`, fails with exit code 2 and nothing is saved.
- **`tabtally/splitting.py`**: new `split_by_percent`. It rejects a name listed twice and requires the percentages to sum to exactly 100. It reuses `allocate` from `money.py`, so the shares always add up to the amount in cents.
- **Tests**: new cases in `tests/test_cli.py` and `tests/test_splitting.py` cover the happy path, odd-cent rounding, a sum that isn't 100, fractional and malformed input, and the `--with`/`--percent` conflict.
- **`README.md`**: added a row for the new form in the commands table.

Choices I made that you may want to change:

- Percentages must be at least 1. A 0% share is rejected rather than stored as a zero entry.
- A bad percentage is reported as an error and exits 2, the same as a bad amount.
- Names are matched exactly, with no trimming, the same as `--with`.