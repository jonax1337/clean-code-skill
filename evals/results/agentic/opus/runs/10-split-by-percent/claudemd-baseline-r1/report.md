`tabtally add` now takes `--percent NAME=PCT`, repeated once for each person, as another way to split an expense instead of `--with`. The full test suite passes (52 tests, including the new ones).

**How it works**
- **The two options don't mix:** you use either `--with` or `--percent` for an expense, and one of them is required. If you give both, or neither, `add` stops with a usage error.
- **Percentages:** each must be a whole number from 0 to 100, and together they must add up to exactly 100. Duplicate names are rejected, the same as with `--with`.
- **Odd cents:** splits use the same cent-rounding as equal splits, so the shares always add up to the full amount.
- **Bad input:** a malformed entry (`bob`, `bob=12.5`, `bob=-5`, `bob=101`), a total other than 100, or a duplicate name prints `error: ...`, exits with code 2, and saves nothing.
- **The rule I chose:** I allowed 0%, which records that person with a share of zero. Say if you'd rather reject it.

**Changes**
- `tabtally/splitting.py`: new `parse_percent` and `split_by_percent` functions; the duplicate-name check is now shared with `split_equally`.
- `tabtally/cli.py`: the `--with`/`--percent` options and how `add` chooses between them.
- `README.md`: a row in the commands table for the percentage form.

**Tests**
- `tests/test_splitting.py`: splitting by percentage, keeping every cent, totals other than 100, duplicates, and bad `NAME=PCT` input.
- `tests/test_cli.py`: a full add-then-balances run with 50/30/20, a total that isn't 100, a malformed entry, and using `--with` and `--percent` together. The error tests also check that nothing gets saved.

Nothing is committed yet.