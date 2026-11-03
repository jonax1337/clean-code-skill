`tabtally add` now takes `--percent NAME=PCT`, for example `--percent alice=50 --percent bob=30 --percent carol=20`. `python -m pytest` passes with 49 tests. I didn't run a linter or formatter, because `ruff` isn't installed here.

- **Usage:** `--with` and `--percent` are now an exclusive pair, and one of them is required. Passing both is an argparse usage error.
- **Validation:** each `NAME=PCT` must have a name and a whole-number percentage. Percentages can't be negative and must add up to 100. A name can't appear twice, which is the same duplicate check `--with` uses. These problems print `error: …`, exit with code 2, and save nothing.
- **Rounding:** odd cents are handled by the existing `allocate`, so shares always add up to the amount paid. For example, 10.01 split 50/50 gives 5.01 and 5.00.
- **Code:** the new `split_by_percent` is in `tabtally/splitting.py`, next to `split_equally`. I moved the duplicate-name check into a shared helper there. The `NAME=PCT` parsing is in `tabtally/cli.py`.
- **Tests and docs:** I added tests for the split function and for the CLI, including malformed input and the total not being 100. I also added a row to the commands table in `README.md`.
- **`--percent X=0`:** a 0% share is accepted and gives that person a share of 0. I didn't forbid it.