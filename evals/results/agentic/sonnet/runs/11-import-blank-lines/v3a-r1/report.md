`hourlog import` now skips blank lines, so the empty line at the end of your accountant's CSV no longer causes the error. `python -m pytest -q` passes (19 tests). I haven't run it against the actual file.

The importer in `hourlog/importer.py` tried to parse every line, and an empty one splits into a single value instead of three. `parse_entries` now skips any line that is empty or only whitespace. Skipped lines still count toward line numbers, so an error on a bad row still points at the right line in the file.

I added a test in `tests/test_importer.py` covering blank lines in the middle and at the end, and checking that the reported line number is still correct after a blank line.

I left everything else alone. A line with a real but malformed row, like `garbage`, still raises an error.