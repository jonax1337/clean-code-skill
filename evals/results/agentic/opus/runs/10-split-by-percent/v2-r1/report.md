`tabtally add` now takes `--percent NAME=PCT`. All 49 tests pass (34 old, 15 new), and I tried the command by hand: `--percent alice=50 --percent bob=40` prints `error: percentages must add up to 100, not 90`.

**How it works**
- **`tabtally/splitting.py`:** a new `split_by_percent(cents, [(name, pct), ...])` checks that the percentages add up to 100, then splits the amount with the existing `allocate`. That's the same rounding the equal split uses, so no cents get lost: 0.01 split 50/50 gives alice 0.01 and bob 0.00. The check for a name listed twice now lives in a small helper that both split types share.
- **`tabtally/cli.py`:** `--with` and `--percent` can't be used together, and every `add` needs one of them. Each `NAME=PCT` value is checked when the command line is read, so input like `alice`, `=50`, `alice=12.5`, `alice=-50` or `alice=+50` is rejected right away with exit code 2.
- **`README.md`:** added a row for the new form of `add`.

**Choices you may want to change**
- **0% is rejected.** I required each percentage to be a positive whole number, since a 0% share does nothing except add a 0.00 line to `balances`. If you'd rather allow 0, it's one condition in `_percent_share`.
- **Error output differs by case.** A badly formed `--percent` value gets argparse's usage message. Percentages that don't add up to 100 and duplicate names get the usual `error: ...` line, and nothing is saved. All of these exit with code 2.

I haven't committed anything.