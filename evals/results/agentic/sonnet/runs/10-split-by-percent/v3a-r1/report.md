`tabtally add` now accepts `--percent NAME=PCT`, so `--percent alice=50 --percent bob=30 --percent carol=20` splits an expense by percentage. I ran `python -m pytest -q` and all 49 tests pass, including the new ones. I did not run a linter or type checker.

- **`--with` and `--percent`:** exactly one of them is required, and using both is rejected. `--with` is no longer marked required on its own; the either/or rule replaces that.
- **Validation:** each value must look like `name=<whole number>`. Anything else is rejected, including `alice=5.5`, `alice=-5`, `alice=` and `=50`. The percentages must add up to exactly 100, and a name listed twice is rejected.
- **Errors:** these are reported as `error: ...` with exit code 2 and nothing is saved. The both-options case is rejected by argparse itself, so its message is argparse's usage error, still with exit code 2.
- **Rounding:** the split reuses the existing `allocate` in `money.py`, so the shares always add up to the full amount. For example, 1.01 split 50/30/20 still sums to 1.01.
- **Code and tests:** the new logic is in `tabtally/splitting.py` (`split_by_percent` and `parse_percent`), with a small `_split` helper in `tabtally/cli.py` choosing between the two modes. I moved the duplicate-name check into a shared helper there. New tests are in `tests/test_splitting.py` and `tests/test_cli.py`.
- **README:** it has a new row for the option.

A `0` percentage is accepted, so that person gets a zero share. I left that alone because you only asked for whole numbers that add up to 100.

I haven't committed anything.