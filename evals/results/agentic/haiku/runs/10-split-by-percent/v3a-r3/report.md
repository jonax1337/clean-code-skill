`tabtally add` now takes `--percent NAME=PCT`, repeatable, and splits the expense by those whole-number percentages. All 51 tests pass (34 existing, 17 new), and I ran the example end to end: `alice=50 bob=30 carol=20` on a 30.00 expense gives alice 15.00, bob 9.00, carol 6.00 owed back. Percentages that don't sum to 100 are rejected with exit code 2 and nothing is saved.

Choices I made that you may want to change:

- **`--with` and `--percent` are mutually exclusive, and one of them is required.** Mixing them is an error.
- **A `0` percentage is allowed.** It means the person is listed but owes nothing. Negative, fractional, signed (`+50`) and empty values are rejected.
- **Rounding reuses the existing `allocate`**, so the cents always add up exactly. For example, 10.00 at 34/33/33 gives 3.40, 3.30, 3.30.
- **Duplicate names are rejected** for both `--with` and `--percent`, using a shared helper.
- **README updated** with a row for the new form.

Files changed: `tabtally/cli.py`, `tabtally/splitting.py` (new `split_by_percent`), `tests/test_cli.py`, `tests/test_splitting.py`, `README.md`. I wrote the tests before the implementation. Nothing is committed.