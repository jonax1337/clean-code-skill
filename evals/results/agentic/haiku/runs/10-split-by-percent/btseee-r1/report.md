`tabtally add` now accepts `--percent NAME=PCT`, and your example works: `30.00` split 50/30/20 gives alice 15.00, bob 9.00, carol 6.00. The full suite passes (48 tests, 34 existing plus 14 new). I haven't committed anything.

Changes:

- **`tabtally/splitting.py`**: new `split_by_percent`. It rejects totals other than 100 and reuses the existing `allocate`, so the shares always add up to the exact amount, with leftover cents going to the largest remainders.
- **`tabtally/cli.py`**: `--percent` is repeatable and mutually exclusive with `--with`. Exactly one of the two is required. Entries are parsed as `NAME=PCT`.
- **Tests**: new cases in `tests/test_splitting.py` and `tests/test_cli.py` cover the split, rounding, the sum-to-100 check, malformed entries, duplicate names, and the `--with`/`--percent` conflict.
- **`README.md`**: added a row for the new form to the commands table.

Choices I made that you may want to change:

- **Zero and negative percentages are rejected.** Only whole numbers above zero are accepted. To leave someone out, omit them.
- **Duplicate names are rejected**, matching how `--with` already treats repeats.
- **Errors use the existing exit code 2** and print the same `error:` prefix as other input problems, so nothing is saved on a bad entry.