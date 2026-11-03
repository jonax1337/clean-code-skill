`tabtally add` now takes `--percent NAME=PCT`, so you can split an expense by percentage. All 52 tests pass, the 18 new ones included. I also tried it from the command line: 10.01 split 50/30/20 came out as 5.01 / 3.00 / 2.00, and a set that only added up to 50 was refused.

```console
$ python -m tabtally add --paid-by alice --amount 100 --description Groceries \
    --percent alice=50 --percent bob=30 --percent carol=20
```

**How it behaves:**
- **Choosing a split:** you give either `--with` (equal split) or `--percent` (percentage split). You must give one, and using both is an error.
- **Rejected input:** the command errors with exit code 2 and saves nothing if:
  - a value isn't a whole number (`alice=12.5`, `alice=-10`, `alice=abc`, `=50`)
  - a percentage is 0
  - the same person is listed twice
  - the percentages don't add up to exactly 100
- **Odd cents:** shares use the same cent allocation as the equal split, so they always add up to the full amount. A leftover cent goes to whoever had the biggest rounding remainder, and to the person listed first if it's a tie.
- **Spaces:** spaces around the `=` are accepted (`alice = 50`).

**Changes:**
- `tabtally/splitting.py`: new `parse_percent` and `split_by_percent`. The duplicate-name check is now shared with `split_equally`.
- `tabtally/cli.py`: `--with` and `--percent` are an either/or pair, and one of them is required.
- Tests added to `tests/test_splitting.py` and `tests/test_cli.py`, plus a new row in the README command table.

One choice you might want to change: I made 0% an error, because someone with no share doesn't need to be listed. That rule is a single check in `split_by_percent` if you'd rather allow it.

Nothing is committed yet.