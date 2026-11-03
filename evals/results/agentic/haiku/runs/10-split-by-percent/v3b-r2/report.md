`tabtally add` now accepts `--percent NAME=PCT`, and the full suite passes (50 tests, up from 39 before my new tests). I did not commit anything.

```
$ python -m tabtally add --paid-by alice --amount 30.00 --description Pizza --percent alice=50 --percent bob=30 --percent carol=20
added #1: 30.00 for Pizza
```

With that expense, `balances` shows alice 15.00, bob -9.00, carol -6.00.

**Behavior**
- `--with` and `--percent` are mutually exclusive, and one of them is required. Passing both, or neither, makes argparse exit with code 2.
- Percentages must be whole numbers of at least 1. Anything else, such as `alice=12.5`, `alice=0` or a missing name, is reported as an error.
- The percentages must add up to exactly 100. Otherwise the error says what the total was, and nothing is saved.
- Duplicate names are rejected, the same as with `--with`.
- Cents are split with the existing `allocate` helper, so the shares always add up to the amount.

**Changes**
- `tabtally/splitting.py`: added `parse_percent` and `split_by_percent`. I moved the duplicate check into a shared `_reject_duplicates` helper that both split functions use.
- `tabtally/cli.py`: `--with` and `--percent` are now a mutually exclusive group. A small `_shares` helper picks the split method.
- `tests/test_splitting.py` and `tests/test_cli.py`: tests for the new split, the parsing rules, the 100% check, and the option combinations.
- `README.md`: a row in the commands table for the percentage form.

**Choices I made**
- A person with 0% is rejected rather than accepted. Leaving someone out is clearer with `--with` or by not listing them.
- I did not require the payer to be one of the people in the split. The existing `--with` path doesn't require it either.