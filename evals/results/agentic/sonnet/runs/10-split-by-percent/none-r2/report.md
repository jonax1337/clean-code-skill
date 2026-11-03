`tabtally add` now takes `--percent NAME=PCT`, repeated once per person. The full test suite passes, including two new tests for the percentage split.

I also ran your style of example by hand: 10.01 split 50/30/20 gave alice 5.01, bob 3.00 and carol 2.00, so the shares add up to the amount. A 50/30 split was rejected with `error: percentages must add up to 100, got 80`.

- **Rules:**
  - Percentages must be whole numbers, and each person can appear only once.
  - A total other than 100 is rejected.
  - A malformed value such as `alice=5.5` or `=50` is rejected with a clear error.
- **`--with` is now optional:** you must give either `--with` (equal split) or `--percent`, not both and not neither. Before this change `--with` was required on its own.
- **Rounding:** when a percentage doesn't divide the amount into whole cents, the leftover cents go to the largest remainders, earlier names first on a tie. That is the same rounding rule the equal split already uses.

The code is in `tabtally/splitting.py` and `tabtally/cli.py`. I added the new option to the README command table and the tests to `tests/test_splitting.py`. I didn't add a CLI-level test for `--percent`; I checked that path by running it manually. I haven't committed anything.