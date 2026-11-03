`tabtally add` now accepts `--percent NAME=PCT`, for example `--percent alice=50 --percent bob=30 --percent carol=20`. All 48 tests pass, including the new ones for this option. I didn't commit anything.

- **Choosing a split:** `add` needs either `--with` (equal split, as before) or `--percent`, but not both. Using both, or neither, is a usage error that exits with code 2.
- **Validation:** each `--percent` value must be `NAME=<whole number>`, and the percentages must add up to exactly 100. A repeated name, a malformed value or a total other than 100 prints `error: …`, exits with code 2 and saves nothing. This matches how the existing errors behave.
- **Rounding:** the percentages go through the same cent-allocation routine as the equal split. The shares always add up to the full amount, and any leftover cents go to the largest remainders.

The changes are in `tabtally/splitting.py` and `tabtally/cli.py`, with new tests in `tests/test_splitting.py` and `tests/test_cli.py`. I also added a row for the new option to the command table in `README.md`.