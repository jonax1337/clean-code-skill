I fixed it: `hourlog import` now skips blank lines, including ones that contain only spaces or a Windows line ending (`\r\n`). The accountant's file should import now.

**The cause:** `_parse_line` in `hourlog/importer.py` split every line on commas and expected exactly three values. An empty line splits into one empty value, so it failed.

**The fix:** `parse_entries` now skips a line if nothing is left after stripping whitespace. Errors still report the real line number in the file, because blank lines are still counted. A line that has content but is malformed still stops the import with a line-numbered error, as before.

**Test:** I added `test_import_skips_blank_lines` in `tests/test_cli.py`, which imports a file with blank lines in the middle and at the end. It fails without the fix and passes with it, and all 19 tests pass.

Nothing is committed yet.