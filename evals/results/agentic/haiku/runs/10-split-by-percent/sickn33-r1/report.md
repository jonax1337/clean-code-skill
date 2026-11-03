`tabtally add` now accepts `--percent NAME=PCT`, so an expense can be split by whole-number percentages. All 50 tests pass, including new ones for the feature.

```
$ python -m tabtally add --paid-by alice --amount 100.00 --description Dinner --percent alice=50 --percent bob=30 --percent carol=20
added #1: 100.00 for Dinner
```

Balances come out as alice 50.00, bob -30.00, carol -20.00.

What changed:
- **`tabtally/cli.py`**: `--with` and `--percent` are now a required, mutually exclusive pair. Passing both is a usage error (exit 2), and so is passing neither.
- **`tabtally/splitting.py`**: `split_by_percent` reuses the existing `allocate()` rounding, so odd cents are never lost. `parse_percent_assignments` parses `NAME=PCT`.
- **`README.md`**: added a row for the new form to the commands table.
- **Tests**: covers the happy path, percentages that don't sum to 100 (nothing is saved), malformed input like `alice=50.5`, `alice=-5`, `alice=` and a missing `=`, duplicate names, and the `--with`/`--percent` conflict.

Choices I made that you may want to change:
- `0` is accepted as a percentage, so someone can be listed with no share. Negative numbers and decimals are rejected.
- The percentages must add up to exactly 100. Anything else is an error rather than being normalised.
- Names are matched exactly, as they are for `--with`.

I haven't committed anything.