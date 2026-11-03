`tabtally add` now takes `--percent NAME=PCT`, for example `--percent alice=50 --percent bob=30 --percent carol=20`. All 49 tests pass (`python -m pytest -q`). I didn't run a linter or type checker, and I didn't run the CLI by hand outside the tests.

**How it behaves**
- **Choosing a split:** `add` needs either `--with` (equal split) or `--percent`. Giving both, or neither, is an argparse usage error with exit code 2.
- **Rejected input:** each of these gives `error: …`, exit code 2, and nothing is saved:
  - the percentages don't add up to 100
  - a percentage is zero
  - a value isn't a whole number, for example `alice=5.5`, `alice=-5` or `alice=abc`
  - a name is missing, or the `=` is
  - a name is listed twice
- **Zero percent:** I rejected 0, since it would mean a person shares the expense but owes nothing. Say if you'd rather allow it.
- **Rounding:** the existing `allocate` function does the split, so the shares always add up to the exact amount. Splitting 0.01 at 50/50 gives alice 1 cent and bob 0.

**Code changes**
- In `tabtally/splitting.py` I added `parse_percent` and `split_by_percent`. I pulled the duplicate-name check that `split_equally` already had into a shared helper.
- In `tabtally/cli.py`, `_add` picks the split based on which option was given.
- I added unit tests for the two new functions and CLI tests for a successful percent split, percentages that don't add up, and combining `--with` with `--percent`.
- I added a `--percent` row to the command table in `README.md`.