`tabtally add` now accepts `--percent NAME=PCT` as an alternative to `--with`. The full suite passes (49 tests, up from 34), and a manual run with `alice=50 bob=30 carol=20` on a 30.00 expense gives alice 15.00, bob -9.00, carol -6.00.

Changes:
- **`tabtally/splitting.py`**: new `split_by_percent`. It rejects percentages that don't total 100, any percentage below 1, and a name listed twice. It reuses the existing `allocate`, so odd cents still go to someone and the shares always sum to the amount.
- **`tabtally/cli.py`**: `--with` and `--percent` are in a mutually exclusive, required group, so you must use one and can't mix them. `NAME=PCT` parsing accepts only whole numbers. Malformed input like `alice`, `=50`, `alice=12.5`, `alice=50%` or `alice=-5` is reported as `error:` with exit code 2, and nothing is saved.
- **Tests**: added cases in `tests/test_splitting.py` and `tests/test_cli.py` covering the split, rounding, the sum-to-100 check, zero percentages, duplicates, malformed input, and the `--with`/`--percent` conflict.
- **`README.md`**: added a row for the new form of `add`.

Choices I made that you may want to change:
- Percentages must be at least 1. Zero is rejected, so you can't use `alice=0` to leave someone out; they just shouldn't be listed.
- The percentage syntax is strict: no `%` sign and no decimals. `--percent alice=33.3` is an error.

Nothing has been committed.