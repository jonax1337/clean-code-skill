I added `--percent NAME=PCT` to `tabtally add`. The full suite passes (50 tests, up from 34), and I ran the CLI by hand to check the split and the error paths.

What changed:

- **`tabtally/splitting.py`**: `split_by_percent` splits with the existing `allocate`, so the cents always add up exactly. `parse_percents` reads the `NAME=PCT` options.
- **`tabtally/cli.py`**: `--with` and `--percent` are now a required, mutually exclusive pair, so you must give one of them but not both.
- **Tests**: new cases in `tests/test_splitting.py` and `tests/test_cli.py` cover the split, the rounding, and the rejections.
- **`README.md`**: a row for the new form in the commands table.

Choices I made that you may want to change:

- Percentages must be whole numbers above zero, so `alice=0` is rejected. To leave someone out, omit them.
- Names must not repeat, as with `--with`.
- A percentage total other than 100 is an error: `percentages must add up to 100, not 120`.
- Using both `--with` and `--percent` is an argparse error with exit code 2.

I did not commit anything.