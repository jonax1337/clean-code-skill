`tabtally add` now accepts `--percent NAME=PCT` as an alternative to `--with`. The full suite passes (49 tests, up from 34), and an end-to-end run split a 30.00 pizza 50/30/20 as 15.00, 9.00 and 6.00.

Behaviour and choices I made:

- **`--with` and `--percent` are mutually exclusive, and one of them is required.** Passing both is an argparse error (exit 2).
- **Percentages must be whole numbers from 0 to 100 and add up to exactly 100.** Anything else, such as `alice=50.5`, `alice=-5`, a missing `=`, or a sum of 120, is reported as `error:` with exit 2 and nothing is saved.
- **Rounding reuses the existing `allocate`**, so the shares always sum to the full amount. Odd cents go to the largest remainders, the same as the equal split.
- **A 0% share is allowed.** That person stays on the expense with nothing owed. Say if you would rather reject it.
- **A name listed twice is rejected**, the same as with `--with`. The duplicate check moved into a shared helper in `tabtally/splitting.py`.

Files changed: `tabtally/cli.py`, `tabtally/splitting.py`, `README.md` (new row in the command table), and tests in `tests/test_cli.py` and `tests/test_splitting.py`. Nothing is committed.