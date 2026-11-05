`tabtally add` now takes `--percent NAME=PCT`, repeated once per person. For example, `--percent alice=50 --percent bob=30 --percent carol=20` splits 10.00 into 5.00, 3.00 and 2.00. The full test suite passes (51 tests), including new ones for this feature.

- **Rules:** percentages must be whole numbers greater than 0 and add up to 100. Duplicate names are rejected, as they already are for `--with`. A bad percentage prints `error:` and exits with code 2, and nothing is saved.
- **Rounding:** cents are allocated with the same `allocate` function the equal split uses, so no cent is lost.
- **`--with` is no longer required by argparse:** `add` now needs exactly one of `--with` or `--percent`. Giving both or neither is an error with exit code 2. This check is in `_add` in `tabtally/cli.py`, so `--help` no longer shows `--with` as required.
- **Where the code is:** `tabtally/splitting.py` has the new `parse_percent` and `split_by_percent`. I also added the option to `README.md`.

I decided that 0% is rejected rather than allowed, since someone with no share shouldn't be listed. Say so if you'd rather allow it.

I haven't committed anything.