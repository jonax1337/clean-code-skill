`tabtally add` now accepts `--percent NAME=PCT`, repeated once per person, and all 47 tests pass. I haven't committed anything.

For example, `--percent alice=50 --percent bob=30 --percent carol=20` on a 10.00 expense gives alice 5.00, bob 3.00 and carol 2.00.

- **`--with` and `--percent` are mutually exclusive.** `add` requires exactly one of them. Passing both is a usage error (exit 2).
- **Validation:**
  - **Malformed values:** anything that isn't `NAME=` plus a whole number is rejected by argparse with exit 2. That covers `bob`, `bob=`, `=50`, `bob=5.5`, `bob=-5` and `bob=abc`.
  - **Wrong total or repeated name:** if the percentages don't add up to 100, or a name appears twice, the command prints `error: ...` and exits 2. Nothing is saved.
- **Rounding:** cents are split with the existing `allocate`, so the shares always add up to the full amount. A 10.01 expense split 33/33/34 still totals 10.01.
- **Code and tests:**
  - **Split logic:** the new function is `split_by_percent` in `tabtally/splitting.py`. It shares the duplicate-name check with `split_equally`.
  - **CLI:** the option parsing is in `tabtally/cli.py`.
  - **Tests:** I added tests for both the split function and the CLI.
  - **README:** I added a row for the new form of the command.

A percentage of 0 is accepted, which gives that person a zero share. I left it that way because the request didn't rule it out.