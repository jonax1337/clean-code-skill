`tabtally add` now takes `--percent NAME=PCT`, for example `--percent alice=50 --percent bob=30 --percent carol=20`. I ran `python -m pytest -q` and all 49 tests pass, including the new ones. I didn't run a linter or type checker.

- **Either/or:** `--with` and `--percent` are mutually exclusive, and one of them is required. Combining them is an argparse usage error.
- **Validation:** each spec must look like `NAME=<whole number>`, so `alice`, `=50`, `alice=5.5`, `alice=-5` and `alice=abc` are all rejected. The percentages must add up to exactly 100. A name listed twice is rejected, as with `--with`.
- **Error handling:** these failures print `error: …`, exit with code 2 and save nothing.
- **Rounding:** the split goes through the existing `allocate`, so shares always add up to the full amount. Leftover cents go to the largest remainders, as in the equal split.
- **Code changes:** `tabtally/splitting.py` has two new functions, `parse_percent` and `split_by_percent`. The duplicate-name check is now shared with `split_equally`. `tabtally/cli.py` and the README command table are updated to match.
- **Tests:** I added tests in `tests/test_splitting.py` and `tests/test_cli.py`. They cover the 50/30/20 split, a split with odd cents, totals that don't reach 100, malformed specs, duplicates, and combining `--with` with `--percent`.

I haven't committed anything.