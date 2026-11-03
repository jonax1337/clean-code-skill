`tabtally add` now takes `--percent NAME=PCT`, so an expense can be split by whole-number percentages. All 50 tests pass (34 existing, 16 new). I also ran the CLI end to end: a 30.00 split 50/30/20 gives alice 15.00, bob −9.00 and carol −6.00, and percentages summing to 90 are rejected with exit code 2.

Choices I made that you may want to change:

- **`--with` and `--percent` are mutually exclusive, and one of them is required.** Argparse rejects combining them and rejects neither.
- **Percentages must be non-negative whole numbers.** `50.5`, `-5` and `fifty` are rejected. Zero is allowed, so `bob=0` gives bob a zero share.
- **Duplicate names are rejected**, as they already are for `--with`.
- **Rounding uses the existing `allocate` helper**, so leftover cents go to the largest remainders and the shares always add up to the amount.

Changes:
- `tabtally/splitting.py`: new `split_by_percent`, which enforces the sum-to-100 rule.
- `tabtally/cli.py`: the `--percent` option, the mutually exclusive group, and `_parse_percents` for the `NAME=PCT` syntax.
- `tests/test_splitting.py` and `tests/test_cli.py`: new tests for the split, the rounding, and the error cases.
- `README.md`: a row in the command table for the new form.

I haven't committed anything.