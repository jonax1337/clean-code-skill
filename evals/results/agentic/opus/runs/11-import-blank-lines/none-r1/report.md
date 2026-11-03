I fixed it: `hourlog import` now skips blank lines, so the empty line at the end of your accountant's CSV no longer causes an error.

**Cause:** `_parse_line` in `hourlog/importer.py` splits each line on commas and expects exactly three fields (`date,project,minutes`). An empty line gives only one field, which caused the "expected 3, got 1" error.

**Fix:** `parse_entries` now skips any line that is empty or contains only whitespace before trying to read it. It doesn't renumber the lines, so if a real line is broken, the error still points to the correct line number in the file.

**Test:** I added `test_import_skips_blank_lines` to `tests/test_cli.py`. It covers a blank line in the middle, a final line with Windows line endings (`\r\n`), a line containing only spaces, and extra empty lines at the end. All 19 tests pass.

Lines that are broken in other ways, like the wrong number of fields or a non-number in the minutes column, are still rejected and the import stores nothing. I haven't committed the change.