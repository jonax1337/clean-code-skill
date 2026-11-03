`hourlog import` no longer fails on your accountant's CSV. It now skips blank lines, including lines that contain only spaces, like the empty line at the end of their file.

**What was wrong:** In `hourlog/importer.py`, the parser split every line on commas and expected three values (date, project, minutes). An empty line gave it one value, which caused the error you saw.

**The fix:** `parse_entries` now skips any line that is empty after removing whitespace. Lines are still counted the same way, so error messages still point to the right line in the file.

**Tests:** I added two to `tests/test_cli.py`:
- A file with blank lines in the middle and at the end imports the correct number of entries.
- An error that comes after a blank line still reports the correct line number.

All 20 tests pass. I haven't committed anything.