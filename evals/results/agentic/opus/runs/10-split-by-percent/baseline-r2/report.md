I added `--percent NAME=PCT` to `tabtally add`. All 50 tests pass, including the 16 new ones. I haven't committed anything.

```console
$ python -m tabtally add --paid-by alice --amount 100 --description Groceries \
    --percent alice=50 --percent bob=30 --percent carol=20
```

**How it behaves**
- **`--with` or `--percent`:** you must use exactly one of them. Using both, or neither, makes the command stop with a usage error.
- **Whole cents:** the split uses the same rounding as equal splits, so the shares always add up to exactly the amount paid. For example, 10.00 split 33/33/34 becomes 3.30 / 3.30 / 3.40.
- **What gets rejected:** percentages that don't add up to 100, a person listed twice, and badly formed entries like `alice`, `=50`, `alice=50.5`, `alice=-10` or `alice=+5`. Each gives the usual `error: ...` message, exits with code 2, and saves nothing.
- **0% is allowed** (e.g. `bob=0`) as long as the total is still 100. That person is recorded with a share of 0.00. If you'd rather reject it, it's a one-line change.

**Changes**
- `tabtally/splitting.py`: new `parse_percent` and `split_by_percent`. I moved the duplicate-name check into a helper so both split types use it.
- `tabtally/cli.py`: the new option and the choice between equal and percentage splits.
- `README.md`: a row for the new form of `add`.
- `tests/test_splitting.py` and `tests/test_cli.py`: tests for the new option.