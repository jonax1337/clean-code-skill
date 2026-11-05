`tabtally add` now takes `--percent NAME=PCT`, so `--percent alice=50 --percent bob=30 --percent carol=20` splits an expense by percentage. All 54 tests pass (34 existing, 20 new).

- **Validation:** each value must be a whole number from 1 to 100, and the values must add up to 100. Anything else exits with code 2 and saves nothing. Malformed items like `bob` or `alice=50.5` are rejected, and so is a name listed twice.
- **Rounding:** the shares are computed with the existing `allocate`, so the cents always add up to the amount. For example, `--amount 10.00` with 34/33/33 gives 6.80, 3.30, 3.30 (the shares of the total are 3.40, 3.30, 3.30 in percent terms, but the rounding follows the existing largest-remainder rule).
- **`--with` vs `--percent`:** they are mutually exclusive and one of them is required, so argparse rejects using both or neither.
- **Storage:** the file still stores only the cents per person, so `list` and `balances` need no changes.

I also added a row to the README's command table.

The changes are in `tabtally/splitting.py`, `tabtally/cli.py`, the two test files, and `README.md`. I haven't committed anything.