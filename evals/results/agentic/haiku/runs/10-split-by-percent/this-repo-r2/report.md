`tabtally add` now takes `--percent NAME=PCT`, repeated for each person, as an alternative to `--with`. The test suite passes: 49 tests, up from 34.

Running it end to end gave the expected balances: a 30.00 expense split 50/30/20 gives alice 15.00, bob 9.00 and carol 6.00. A total other than 100 is rejected with exit code 2, and nothing is saved.

Choices I made that you may want to change:

- **`--with` and `--percent` are mutually exclusive, and one is required.** Passing both, or neither, is an argparse error.
- **Percentages must be whole numbers from 1 to 100, and each name may appear only once.** I rejected `0` on purpose, since a person at 0% should just be left off. Negatives, decimals and duplicate names are also rejected.
- **Rounding reuses the existing `allocate` function**, so cents are never lost. For example, 10 cents at 33/33/34 gives 3/3/4.
- **Error messages** follow the existing `MoneyError` path, so they print as `error: ...` with exit code 2.

The changes are in `tabtally/splitting.py` (`parse_percents`, `split_by_percent`), `tabtally/cli.py`, the tests in `tests/test_splitting.py` and `tests/test_cli.py`, and a new row in the README command table. I haven't committed anything.