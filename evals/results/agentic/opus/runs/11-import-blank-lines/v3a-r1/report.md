I fixed it: `hourlog import` now skips blank lines, so the empty line at the end of your accountant's file no longer causes an error.

**The cause:** `parse_entries` in `hourlog/importer.py` sent every line to the parser, including empty ones. An empty line splits into a single field, which is where "expected 3, got 1" came from.

**The fix:** lines that are empty or contain only spaces are now skipped wherever they appear in the file, not just at the end. Error messages still give the right line number in the file, because every line is still counted. I also added "Blank lines are skipped." to the importer module's description.

**Tests:** I added two tests to `tests/test_importer.py`. One checks that blank lines (including ones with spaces or Windows line endings) are ignored. The other checks that an error after a blank line still reports the correct line number. Both failed before the change, and the full suite passes now (20 tests).

I haven't committed anything.