`tabtally add` now accepts `--percent NAME=PCT`, repeated once per person. For example, `--percent alice=50 --percent bob=30 --percent carol=20` splits the amount 50/30/20. All 50 tests pass, including the new ones. I couldn't run a linter or formatter because `ruff` isn't installed here.

- **`--with` vs `--percent`:** you must give exactly one of them. Using both, or neither, is an argparse usage error.
- **Validation:**
  - Percentages must be whole numbers, and `alice=5.5`, `alice=-5` or a missing name are rejected.
  - The total must be exactly 100.
  - A name listed twice is rejected.
  - A bad value stops the command before anything is saved. A malformed `NAME=PCT` is an argparse usage error; a bad total or a duplicate name prints `error: ...` and exits with code 2.
- **Rounding:** shares reuse the existing `allocate` function, so odd cents are still never lost.
- **Code:** the new logic is `parse_percent` and `split_by_percent` in `tabtally/splitting.py`, with a small wrapper in `tabtally/cli.py`. I also added a row to the README command table.
- **Tests:** they cover the splitting functions and the CLI. Equal splitting works as before.

A percentage of 0 is rejected, not allowed. The error message says it expects a whole number, so it doesn't explain that zero is the problem. Allowing zero would be a small change to `parse_percent`.