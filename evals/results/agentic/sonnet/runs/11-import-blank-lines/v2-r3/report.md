`hourlog import` now skips blank lines, so the accountant's CSV should import. I didn't have that file, so I only tested with a sample that has blank lines. The full test suite passes (19 tests).

**Cause:** the parser in `hourlog/importer.py` split every line on commas, and an empty line gave one value instead of three. That is the "expected 3, got 1" error.

**Fix:** `parse_entries` skips lines that are empty or only whitespace. Line numbers in error messages still count the skipped lines, so a real error is reported at the line where you'd find it in an editor.

**Test:** I added `test_import_ignores_blank_lines` in `tests/test_cli.py`. It covers a blank line in the middle, a whitespace-only line, and blank lines at the end of the file.

I haven't committed anything.