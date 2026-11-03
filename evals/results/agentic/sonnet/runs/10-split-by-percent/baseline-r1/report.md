`tabtally add` now takes `--percent NAME=PCT`, for example `--percent alice=50 --percent bob=30 --percent carol=20`. The full test suite passes, including new tests for this option. I haven't committed anything.

- **Exclusive with `--with`:** you give either `--with` or `--percent`, not both, and one of them is still required. Because of that, `--with` is no longer marked required on its own in the parser.
- **Rounding:** each person's share is rounded down to whole cents, and any leftover cents go to the largest remainders, same as the equal split.
- **Rejected input:**
  - percentages that don't total 100
  - values that aren't whole numbers, like `x` or `50.5`
  - a missing `=`
  - the same name listed twice
  Each of these prints `error: …` and exits with code 2.
- **README:** I added a sentence to the `add` row in the README's command table.

The new splitting code is in `tabtally/splitting.py`, the CLI change is in `tabtally/cli.py`, and the tests are in `tests/test_cli.py`.

I didn't add direct unit tests for the new functions in `tests/test_splitting.py`. They're only covered through the CLI tests.