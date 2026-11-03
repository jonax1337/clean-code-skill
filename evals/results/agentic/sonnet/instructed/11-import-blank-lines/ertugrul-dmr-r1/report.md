`hourlog import` now skips blank lines, so the empty line at the end of your accountant's CSV no longer causes the error. All 20 tests pass, including the two new ones. I didn't run it on your accountant's actual file.

The importer split every line on commas and expected three fields. An empty line gives one empty field, which is where "expected 3, got 1" came from.

The fix is in `parse_entries` in `hourlog/importer.py`. A line that is empty or only whitespace is skipped. Skipped lines still count towards line numbers, so an error on a later line still points at the right line in the file.

The new tests in `tests/test_importer.py` cover skipping blank lines (empty, whitespace-only and `\r\n`) and the line numbers in error messages after a blank line.

I didn't commit anything.