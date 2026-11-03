`tabtally add` now accepts `--percent NAME=PCT`, for example `--percent alice=50 --percent bob=30 --percent carol=20`. All 49 tests pass with `python -m pytest` (34 before, plus 15 new).

**How it behaves**
- **Either/or with `--with`:** you have to give one of `--with` or `--percent`, and using both is rejected (`tabtally/cli.py`).
- **Format check:** a value that isn't `NAME=PCT` with a whole-number percentage (like `bob`, `=50`, `bob=12.5` or `bob=half`) is rejected straight away with a message that mentions `NAME=PCT`.
- **Other checks:** `split_by_percent` in `tabtally/splitting.py` rejects a name listed twice, a percentage of zero or less, and a total other than 100 (for example "percentages must add up to 100, not 90"). These errors look like the existing ones (`error: ...`, exit code 2), and nothing is saved when one occurs. I tried the "not 90" case by hand.
- **Rounding:** the split reuses the existing `allocate`, so no cents are lost. For example, 10.01 split 50/50 gives 5.01 and 5.00.
- **Duplicates:** the check that `split_equally` already had now lives in a small shared helper, and both split functions use it.
- **README:** the commands table has a new row for the `--percent` form.

**Choices you may want to change**
- **0% is rejected:** a 0% share seemed more likely to be a typo than intended. If you want people listed at 0%, it's a one-line change.
- **Error style differs:** format errors come from argparse and print its usage-style message, while the other errors use the app's own `error: ...` style. Both exit with code 2.

I haven't committed anything.