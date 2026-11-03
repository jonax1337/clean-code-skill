`tabtally add` now accepts `--percent NAME=PCT`. All 51 tests pass: the original 34 plus 17 new ones. I also ran it by hand: `--amount 10 --percent alice=33 --percent bob=67` saved the expense, and `balances` showed `alice 6.70` / `bob -6.70`.

**How it behaves:**
- **Only one split style per expense.** `--with` and `--percent` can't be used together, but you must give one of them. Using both stops with argparse's usual usage error (exit code 2).
- **Percentages must be whole numbers from 0 to 100 and add up to 100.** Otherwise you get `error: percentages must add up to 100, not 90` and nothing is saved.
- **Badly written values are rejected.** Inputs like `alice`, `=50`, `alice=12.5` or `alice=-10` get an error explaining that the format is `NAME=PCT`.
- **The same person can't appear twice**, just as with `--with`.
- **The shares always add up to the full amount.** It reuses the existing `allocate`, so any leftover cents go to the people with the largest remainders.

**Changes:**
- `tabtally/splitting.py`: added `split_by_percent` and `parse_percent`. The duplicate-name check that was inside `split_equally` is now a shared `_reject_duplicates` function, so both split styles use it.
- `tabtally/cli.py`: the two options are now an either/or pair, and `_add` picks the split based on which one was given.
- `README.md`: added a row to the commands table.
- `tests/test_splitting.py` and `tests/test_cli.py`: tests for the new option.

Two choices you might want changed:
- **A 0% share is allowed**, so someone can be listed without owing anything.
- **Names are split at the last `=`**, so a name that contains `=` still works.

I didn't run a linter because ruff isn't installed here. Nothing is committed.