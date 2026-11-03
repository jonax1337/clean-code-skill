The README row came out right, so I'm wrapping up the `--percent` change now.

`tabtally add` now accepts `--percent NAME=PCT`, repeated once per person. The full suite passes (39 tests), including the new ones for this option. I didn't commit anything.

- **Choosing a mode:** you must give either `--with` (equal split) or `--percent`. Giving both, or neither, exits with code 2 and an error message.
- **Validation:** each value must be a whole number, and the percentages must add up to 100. A name listed twice is rejected. A bad input exits with code 2 and saves nothing.
- **Rounding:** the split reuses the existing cent allocation, so the shares always add up to the full amount. For example, 10.00 split 50/30/20 gives 5.00, 3.00 and 2.00.

The changes are in `tabtally/splitting.py` (new `parse_percent` and `split_by_percent`), `tabtally/cli.py`, a new `UsageError` in `tabtally/errors.py`, `README.md`, and `tests/test_cli.py`.

I made `--with` optional so the two modes can coexist. A missing `--with` is now caught by the check above instead of by argparse.