Fixed. `hourlog import` now skips blank lines, so the accountant's CSV imports.

**Cause:** `parse_entries` in `hourlog/importer.py` passed every line to `_parse_line`. An empty line splits into one value, not three, so the unpack failed.

**Change:**
- `hourlog/importer.py`: `parse_entries` skips any line that is empty or whitespace-only. Line numbers still count the skipped lines, so error messages point at the right line in the file.
- `tests/test_cli.py`: added `test_import_ignores_blank_lines`, which imports a file with blank lines between and after the entries and expects 2 entries imported.

**Verification:**
- `python -m pytest -q`: 19 passed.
- With the fix reverted, the new test fails with `assert 1 == 0`, so it covers the bug.

**Choice to check:** the skip applies to blank lines anywhere in the file, not only at the end. That seemed the right call for a CSV, but say if you want stricter handling.