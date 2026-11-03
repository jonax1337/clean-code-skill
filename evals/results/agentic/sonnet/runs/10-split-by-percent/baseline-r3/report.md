`tabtally add` now takes `--percent NAME=PCT`, repeated once per person, as an alternative to `--with`. The full test suite passes, including the new tests for this.

- **Rules:** percentages must be whole numbers that add up to 100. A name can't appear twice. Giving both `--with` and `--percent`, or neither, is an error. Each of these prints `error: …` and exits with code 2, like the existing errors.
- **Rounding:** each person's share is computed in cents with the existing `allocate` function, so shares always add up exactly to the amount paid. For example, 10.01 split 50/30/20 gives alice 5.01, bob 3.00 and carol 2.00. That is the 5.00, −3.00, −2.00 shown in my test's `balances` output, since alice paid and her own 5.01 share nets against it.
- **Where the changes are:**
  - `tabtally/splitting.py` has the new `parse_percent` and `split_by_percent`.
  - `tabtally/cli.py` has the new option. `--with` is no longer required by argparse; the check that you give exactly one of the two happens in `_add`.
  - The new tests are in `tests/test_cli.py`.
  - I added a `--percent` row to the command table in `README.md`.

I didn't commit anything.