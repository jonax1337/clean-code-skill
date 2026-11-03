I fixed it: `hourlog import` now skips blank lines, so the empty line at the end of your accountant's file won't stop the import anymore. All 20 tests pass.

**Cause:** `_parse_line` in `hourlog/importer.py` splits every line on commas and expects exactly three values. An empty line gives only one, which caused the error you saw.

**Fix:** `parse_entries` now skips any line that is empty or contains only spaces, including Windows-style `\r\n` endings. Line numbers still count the skipped lines, so error messages point to the right line in the file. Everything else is unchanged: a line that does have content but is badly formatted still fails the import, and nothing gets saved.

**Tests:** I added two tests in `tests/test_cli.py` and confirmed they failed before the fix:
- `test_import_skips_blank_lines`: blank lines in the middle and at the end, including `\r\n` and spaces-only lines, are ignored.
- `test_import_error_counts_blank_lines`: when a blank line comes before a bad line, the error still reports the bad line's real line number.

I haven't committed anything.