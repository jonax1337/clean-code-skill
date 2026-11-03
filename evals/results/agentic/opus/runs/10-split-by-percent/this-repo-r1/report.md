`tabtally add` now takes `--percent NAME=PCT`, for example `--percent alice=50 --percent bob=30 --percent carol=20`. All 51 tests pass (`python -m pytest`, 34 before this change). I did not run a linter or formatter because `ruff` isn't installed here.

**Changes:**
- **`tabtally/splitting.py`**: a new `split_by_percent` function. It rejects anyone listed twice (the existing check, moved into a shared helper) and percentages that don't add up to 100, with a message like `percentages must add up to 100, not 99`. The cents are then divided with the existing `allocate` function, so the shares always add up to the full amount. For example, 10.01 split 50/30/20 gives 5.01 / 3.00 / 2.00.
- **`tabtally/cli.py`**: you must give either `--with` or `--percent` on `add`, and you can't give both. Each `--percent` value must be `NAME=PCT`, where PCT is a whole number from 0 to 100. Values like `alice`, `=50`, `alice=12.5`, `alice=-50` or `alice=101` are rejected with exit code 2, the same code used for other input errors.
- **`README.md`**: documents the new option.
- **Tests**: new tests for `split_by_percent` (exact split, a leftover cent, one person at 100%, totals of 99 and 101, a name listed twice) and for the command line (percent split with balances, wrong total, malformed values, `--with` and `--percent` together, neither given). They failed before the implementation and pass now.

**Decisions for you to check:**
- **0% is allowed.** That person is recorded with a 0.00 share. Say if you'd rather reject it.
- **Two kinds of error output.** A malformed `--percent` value is caught while the command line is read, so it gets argparse's usage-style message (`tabtally add: error: argument --percent: ...`). A wrong total or a repeated name gets the existing `error: ...` message. Both exit with code 2 and save nothing.

I haven't committed anything.