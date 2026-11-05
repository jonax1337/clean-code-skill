`tabtally add` now takes `--percent NAME=PCT`, repeated once per person, as an alternative to `--with`. All 48 tests pass, including the new ones. I haven't run the command by hand.

- **Options:** `--with` and `--percent` can't be combined, and one of them is required.
- **Validation:** each value must be `NAME=<whole number>`, no name can repeat, and the percentages must add up to 100. Otherwise you get the usual `error: …` message and exit code 2, and nothing is saved.
- **Rounding:** shares always add up to the exact amount. If the percentages don't divide it evenly, the leftover cents go to the largest remainders. That is the same rule the equal split already uses.
- **Where it lives:** the parsing and splitting are in `tabtally/splitting.py` (`parse_percent`, `split_by_percent`), the option wiring is in `tabtally/cli.py`, and the new tests are in `tests/test_splitting.py` and `tests/test_cli.py`. I also added a row for `--percent` to the README table.
- **Refactor:** I pulled the existing duplicate-name check out of `split_equally` into a small shared helper so both splits use it.

Nothing is committed.