`tabtally add` now takes `--percent NAME=PCT`, for example `--percent alice=50 --percent bob=30 --percent carol=20`. `pytest` ran after my last edit: 48 passed. I didn't run a linter or type checker.

- **Splitting:** `split_by_percent` in `tabtally/splitting.py` uses the existing `allocate`, so the shares always add up to the exact amount in cents. For example, 10.01 split 50/30/20 keeps every cent.
- **CLI:** `--with` and `--percent` are mutually exclusive, and one of them is still required. Passing both makes argparse exit with its own usage error.
- **Duplicate names:** the duplicate-name check is now shared between the equal and percent splits, so the message is unchanged.
- **Validation:** a percentage that isn't a whole number (`alice=12.5`, `alice=-10`, `alice=ten`) or a missing name or `=` is rejected. So are percentages that don't total 100. These go through the existing error path (message to stderr, exit code 2), and nothing is saved.
- **Tests and docs:** I added tests for the percent split, the malformed entries, the totals and duplicate names. I also added CLI tests for a successful percent split, the rejected total, and combining `--with` with `--percent`. The README command table has a new row.

An entry such as `alice=0` is accepted, so someone can be listed with a 0% share.

I haven't committed anything.