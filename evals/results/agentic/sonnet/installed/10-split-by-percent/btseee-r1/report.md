`tabtally add` now accepts `--percent NAME=PCT`, so `--percent alice=50 --percent bob=30 --percent carol=20` splits an expense by percentage. The full test suite passes, including the new tests.

- **Mutually exclusive:** you must give either `--with` or `--percent`. `--with` is no longer marked required in argparse, and the check now happens in `_add` in `tabtally/cli.py`. Giving both or neither exits with code 2 and an `error:` message.
- **Validation:** percentages must be whole numbers. A malformed entry, a repeated name, or a total other than 100 is rejected with an error. The parsing and checks live in `parse_percent` and `split_by_percent` in `tabtally/splitting.py`.
- **Rounding:** shares use the existing `allocate` helper, so they always add up exactly to the amount. For example, 10.00 at 50/30/20 gives 5.00, 3.00 and 2.00.
- **Docs and tests:** I added a README row for the new option and tests in `tests/test_cli.py` for a successful split and five rejection cases.

I haven't committed anything.