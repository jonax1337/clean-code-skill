`tabtally add` now takes `--percent NAME=PCT`, repeated once per person, as an alternative to `--with`. `python -m pytest` passes all 48 tests, including the new ones. I did not run a linter or type checker.

- **Splitting:** `tabtally/splitting.py` has two new functions. `parse_percent` reads `alice=50` into a name and a whole number. `split_by_percent` requires the percentages to add up to exactly 100 and rejects a name listed twice. It reuses the existing `allocate`, so odd cents still add up to the full amount.
- **CLI:** `--with` and `--percent` are mutually exclusive, and one of them is required. Combining them gives argparse's usage error (a `SystemExit`, not a `tabtally` error). A malformed value or percentages that don't sum to 100 print `error: …`, exit with code 2 and save nothing.
- **Duplicate check:** I moved the duplicate-name check into a small shared helper so both split modes use it.
- **Tests and docs:** I added tests for the splitting functions and the CLI, and a README row for the new option.

Percentages must be whole numbers. Decimals like `33.3`, negatives and non-numeric values are rejected. `0` is accepted, which gives that person a zero share.