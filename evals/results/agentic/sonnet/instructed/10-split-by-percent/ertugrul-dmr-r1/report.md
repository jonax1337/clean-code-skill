`tabtally add` now takes `--percent NAME=PCT`, for example `--percent alice=50 --percent bob=30 --percent carol=20`. All 47 tests pass, including the new ones.

- **Percentages:** They must be whole numbers and add up to exactly 100. Otherwise the command prints an `error:` message, exits with code 2 and saves nothing. This also applies to malformed entries like `alice=12.5` or `=50`, and to a name listed twice.
- **Rounding:** Odd cents are handled the same way as in the equal split, so the shares always add up to the full amount.
- **Not combinable with `--with`:** `--with` and `--percent` are mutually exclusive, and one of them is still required. Using both makes argparse exit with a usage error.

The split logic is a new `split_by_percent` in `tabtally/splitting.py`, which shares its duplicate-name check with `split_equally`. The option is wired up in `tabtally/cli.py`. I added tests in `tests/test_splitting.py` and `tests/test_cli.py`, and documented the option in `README.md`.

I haven't committed anything.