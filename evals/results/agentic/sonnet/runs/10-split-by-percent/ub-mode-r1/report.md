`tabtally add` now accepts `--percent NAME=PCT`, for example `--percent alice=50 --percent bob=30 --percent carol=20`. The full test suite passes (47 tests, including new ones for this option). I committed it to `main` as `d8362fd` but did not push, and I did not run the crapper, dryer or mutator tools.

- **Rules:** Percentages must be whole numbers that add up to 100. Anything else is rejected with an error and exit code 2, and nothing is saved. That covers a missing `=`, a non-integer or negative value, an empty name, a total other than 100, and a name listed twice.
- **`--with` and `--percent`:** `--with` is no longer required on its own. `add` needs exactly one of `--with` and `--percent`, and giving both or neither is an error. I check this in the code rather than with argparse's built-in exclusivity, so the error exits with code 2 like the other errors instead of argparse's own exit.
- **Rounding:** The split uses the existing `allocate` function, so the shares always add up to the full amount. With 50/30/20 on 10.00, alice's balance is 5.00, bob's is -3.00 and carol's is -2.00.
- **Files changed:** The new `split_by_percent` is in `tabtally/splitting.py`, and the option parsing is in `tabtally/cli.py`. I also added the option to the README command table.

**Log**
1. I read the CLI, splitting, money and test files to see how `--with` and the equal split work.
2. I wrote failing tests for the splitting and the CLI first. They failed on the missing import.
3. I moved the duplicate-name check into a shared helper so both splits use it, instead of copying it.
4. I added `split_by_percent`, the `--percent` option and its parsing, and made `--with` optional.
5. I updated the README and committed.