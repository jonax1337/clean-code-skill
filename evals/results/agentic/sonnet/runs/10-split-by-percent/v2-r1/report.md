`tabtally add` now accepts `--percent NAME=PCT`, for example `--percent alice=50 --percent bob=30 --percent carol=20`. All 48 tests pass, including the new ones.

- **Validation:** each value must be a whole number, so `alice=12.5`, `alice=-5` and `alice` with no value are rejected. The percentages must add up to 100, and a name can't appear twice. Bad input gives the usual `error: …` message with exit code 2, and nothing is saved.
- **Rounding:** shares are rounded to whole cents and always add up to the full amount. For example, 33/33/34 on 9.99 loses no cents.
- **`--with` and `--percent`:** you must give one or the other. Giving both is an argparse usage error, as is giving neither. Because of this, `--with` is no longer individually required.
- **Code:** the new functions `parse_percent` and `split_by_percent` are in `tabtally/splitting.py`, and the option is wired up in `tabtally/cli.py`. I pulled the duplicate-name check out of `split_equally` so both splits share it.
- **Tests and docs:** I added tests to `tests/test_splitting.py` and `tests/test_cli.py`, and a `--percent` row to the README command table.

The working copies use CRLF line endings, and git warns it will convert them to LF the next time it touches the files. I didn't change any line endings myself.