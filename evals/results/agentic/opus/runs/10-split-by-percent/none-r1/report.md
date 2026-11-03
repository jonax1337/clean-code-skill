`tabtally add` now takes `--percent NAME=PCT`, and the full test suite passes (51 tests, including the new ones).

```console
$ python -m tabtally add --paid-by alice --amount 10.01 --description Taxi --percent alice=50 --percent bob=30 --percent carol=20
added #1: 10.01 for Taxi
$ python -m tabtally balances
alice 5.00
bob -3.00
carol -2.00
```

**How it works:**
- **Choosing a split:** an expense uses either `--with` (equal split) or `--percent`, not both. If you give both, or neither, the command stops with a usage error.
- **Rules for percentages:** each one must be a whole number from 1 to 100, and together they must add up to exactly 100. Anything else, including a person listed twice, gives an `error:` message, exit code 2, and nothing is saved.
- **Rounding:** this uses the same rounding as equal splits, so the shares always add up to the exact amount paid. In the Taxi example above, the leftover cent went to alice.

**Two decisions you may want to change:**
- I reject `0%`, since a person with a zero share probably shouldn't be on the expense. Allowing it is a one-line change.
- I split each entry on its last `=`, so a name that itself contains `=` still works.

**Changes:**
- `tabtally/splitting.py`: new `split_by_percent` and `parse_percent`, plus a small helper for the duplicate-name check that both split types now use.
- `tabtally/cli.py`: `--with` and `--percent` are now a required either/or option, and `_add` uses whichever one was given.
- Tests in `tests/test_splitting.py` and `tests/test_cli.py`, and a new row for `--percent` in the README's command table.

I haven't committed anything.