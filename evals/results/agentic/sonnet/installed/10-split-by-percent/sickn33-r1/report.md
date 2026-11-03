`tabtally add` now takes `--percent NAME=PCT`, repeated once per person, as an alternative to `--with`. The full suite passes, including the new tests.

- **Splitting:** `--percent alice=50 --percent bob=30 --percent carol=20` splits the amount by those percentages. Leftover cents go to the largest remainders, so the shares always add up to the exact amount.
- **Validation:** a percentage must be a whole number written as `NAME=PCT`. The percentages must add up to 100, and a name can't appear twice. Any of these errors prints `error: …` and exits with code 2, like the existing money errors.
- **`--with` and `--percent`:** you must give exactly one of them. Using both is rejected by argparse, which exits with its own usage error.

The code changes are in `tabtally/splitting.py` and `tabtally/cli.py`. I also added tests to `tests/test_splitting.py` and `tests/test_cli.py` and a README row for the new option. I haven't committed anything.