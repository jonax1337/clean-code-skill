I fixed it: `hourlog import` now skips empty lines instead of treating them as entries, so the trailing empty line in the accountant's file no longer causes an error.

**Cause:** in `hourlog/importer.py`, every line was split on commas and expected to give exactly three values (date, project, minutes). An empty line gives only one value, which caused the "expected 3, got 1" error.

**Fix:** `parse_entries` now skips lines that are empty or contain only spaces before reading them. Line numbers in error messages stay correct, because they still count every line in the file, empty ones included.

I added a test, `test_import_skips_blank_lines`, that imports a file with empty lines in the middle and at the end. All 19 tests pass. I haven't committed anything.