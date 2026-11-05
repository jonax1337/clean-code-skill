`tabtally add` now takes `--percent NAME=PCT`, for example `--percent alice=50 --percent bob=30 --percent carol=20`. The full suite passes (47 tests, including the new ones).

- **Behavior:** the shares are whole-number percentages that must add up to 100. Rounding uses the existing `allocate`, so the shares always add up to the exact amount in cents. `--percent` replaces `--with`, which is no longer required on its own. For example, 10.00 at 50/30/20 gives 5.00, 3.00 and 2.00.
- **Errors:** these are reported as `error: …` with exit code 2, and nothing is saved:
  - percentages that don't total 100, or negative ones;
  - a value that isn't a whole number, such as `bob=fifty` or `bob=12.5`;
  - a missing `=`;
  - the same name listed twice;
  - using both `--with` and `--percent`, or neither.
- **Code:** the new `split_by_percent` is in `tabtally/splitting.py`. The argument parsing is in `tabtally/cli.py`.
- **Tests and docs:** I added tests in `tests/test_splitting.py` and `tests/test_cli.py`, and a row in the README command table.

I didn't commit anything.