`tabtally add` now takes `--percent NAME=PCT`, repeated once per person, as an alternative to `--with`. All 49 tests pass, including new ones for the percentage split and the CLI.

- **Choosing `--with` or `--percent`:** You must give exactly one of them. Using both is an argparse usage error.
- **What gets rejected:** The command exits with code 2 and saves nothing if:
  - a percentage isn't a whole number (`alice=12.5`);
  - the input isn't in `NAME=PCT` form;
  - a percentage is zero or negative;
  - the percentages don't add up to 100;
  - someone is listed twice.
- **Rounding:** Cents are split with the existing `allocate` function, so shares always add up to the full amount. For example, 1.01 split 50/30/20 still totals 1.01.
- **Where the code is:** The new functions `split_by_percent` and `parse_percent` are in `tabtally/splitting.py`. The duplicate-name check is now shared with `split_equally`. The option itself is in `tabtally/cli.py`.
- **README:** I added a row for `--percent` to the commands table.

I didn't commit anything.