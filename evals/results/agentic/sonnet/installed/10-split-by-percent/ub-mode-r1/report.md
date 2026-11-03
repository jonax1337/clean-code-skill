`tabtally add` now takes `--percent NAME=PCT`, for example `--percent alice=50 --percent bob=30 --percent carol=20`. The full test suite passes, including new tests for the percentage split, its error cases and the CLI.

- **Usage:** `--percent` and `--with` can't be combined, and you must give one of them.
- **Validation:** each entry must be `NAME=<whole number>`. The percentages must total exactly 100, and a name can appear only once. Otherwise you get the usual `error: ...` message and exit code 2.
- **Rounding:** shares use the same allocation as the equal split, so they always add up to the exact amount in cents.

The change is in `tabtally/splitting.py` (new `split_by_percent`) and `tabtally/cli.py`. I also added the option to the README's command table. I haven't committed anything.