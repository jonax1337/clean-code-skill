`hourlog import` now skips blank lines, so your accountant's CSV with the empty line at the end should import without the error. All 19 tests pass, including a new one for this case.

**Cause:** `hourlog/importer.py` sent every line to the parser, including empty ones. Splitting an empty line on commas gives one value instead of three, which caused `not enough values to unpack`.

**Fix:** `parse_entries` now skips any line that is empty or contains only spaces before parsing it (`hourlog/importer.py:16`). Line numbers in error messages still match the file, so a real formatting problem is still reported on the right line.

**Test:** `test_import_skips_blank_lines` in `tests/test_cli.py` imports a file with blank lines in the middle, a whitespace-only line, and empty lines at the end. It failed before the change and passes now.

I haven't committed anything.