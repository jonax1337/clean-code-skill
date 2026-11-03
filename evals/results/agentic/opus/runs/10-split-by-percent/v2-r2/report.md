`tabtally add` now takes `--percent NAME=PCT`, and all 49 tests pass, including the 15 new ones.

```console
$ python -m tabtally add --paid-by alice --amount 100 --description Rent --percent alice=50 --percent bob=30 --percent carol=20
added #1: 100.00 for Rent
$ python -m tabtally balances
alice 50.00
bob -30.00
carol -20.00
```

**How it behaves:**
- **Either `--with` or `--percent`, not both.** You have to give one of them, and using both is a usage error.
- **Splitting the cents:** it uses the same allocation as the equal split, so the shares always add up to exactly the amount paid. Leftover cents go to the largest remainders, so 0.01 split 50/50 gives alice 0.01 and bob 0.00.
- **These are rejected with exit code 2, and nothing is saved:**
  - percentages that don't add up to 100 (the error shows the actual total)
  - a value that isn't a whole number, like `alice=12.5`, `alice=-10`, `alice=abc` or `alice`
  - the same person listed twice
- **0% is accepted** as long as the total is 100. That person is recorded with a share of zero. If you'd rather reject it, it's a one-line change.

**Changes:**
- `tabtally/splitting.py`: added `split_by_percent` and `parse_percentage`. I moved the duplicate-name check into a small helper so both splits use it; `split_equally` works the same as before.
- `tabtally/cli.py`: added the new option and the choice between the two splits.
- Tests in `tests/test_splitting.py` and `tests/test_cli.py`, plus a new row in the README command table.

Nothing is committed yet.