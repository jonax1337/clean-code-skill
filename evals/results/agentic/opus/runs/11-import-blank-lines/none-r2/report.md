I fixed it: `hourlog import` now skips blank lines, so the empty line at the end of your accountant's CSV no longer causes an error.

**The problem:** in `hourlog/importer.py`, every line was split on commas and expected to give exactly three values (date, project, minutes). An empty line gives only one value, which caused the `expected 3, got 1` error.

**The fix:** `parse_entries` now skips any line that is empty or contains only spaces before trying to read it. This also covers Windows-style line endings and blank lines in the middle of the file. Line numbers in error messages are unchanged, so a genuinely bad line is still reported with its real line number in the file.

I added a test, `test_import_skips_blank_lines` in `tests/test_cli.py`, that imports a file with blank lines in the middle and at the end. All 19 tests pass. I haven't committed anything.