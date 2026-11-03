`hourlog import` now skips blank lines, so the empty line 41 in your accountant's CSV no longer raises an error. All 19 tests pass, including the new one. I didn't run the import against your actual CSV file.

The cause was in `parse_entries` in `hourlog/importer.py`. An empty line was split on commas and gave one value instead of three, which is the "expected 3, got 1" error. I added a check at the top of the loop that skips any line that is empty or only whitespace.

Skipped lines still count toward line numbers. If a real error shows up after a blank line, the message still points to the right line in the file.

I added a test in `tests/test_importer.py` covering blank lines in the middle and at the end of a file, and checking that line numbers stay correct after one.