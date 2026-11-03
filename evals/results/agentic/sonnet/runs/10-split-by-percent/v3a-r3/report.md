`tabtally add` now takes `--percent NAME=PCT`. For example, `--percent alice=50 --percent bob=30 --percent carol=20` splits the expense 50/30/20. The full suite passes with `python -m pytest` (48 tests). I didn't run a linter or type checker.

- **Choosing a split:** `--with` and `--percent` can't be combined, and one of them is required. Combining them is a usage error that exits with code 2.
- **Validation:** each entry must look like `NAME=<whole number>`. Entries like `alice`, `=50`, `alice=5.5` and `alice=-5` are rejected. The percentages must add up to exactly 100, and a name can't appear twice. Errors print `error: …` and exit with code 2, and nothing is saved.
- **Rounding:** shares reuse the existing cent-allocation code, so they always add up to the amount paid. Any odd cents go to the share with the largest rounding remainder, the same as equal splits.
- **Zero percent:** `name=0` is accepted and gives that person a zero share.

The new splitting function is `split_by_percent` in `tabtally/splitting.py`, and the option is wired up in `tabtally/cli.py`. I added tests for both and a row for the new option in the README command table.

I haven't committed anything.