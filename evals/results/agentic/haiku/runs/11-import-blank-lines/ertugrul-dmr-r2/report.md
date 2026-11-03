Fixed. `hourlog import` now skips blank lines, so a trailing empty line in the accountant's CSV no longer causes the crash.

**Cause:** `_parse_line` splits each line on commas and unpacks three values. An empty line splits into one value, so the unpack fails. The error was reported as line 41 because that is where the bad line sits.

**Changes:**
- `hourlog/importer.py`: `parse_entries` skips any line that is empty or only whitespace before parsing it.
- `tests/test_importer.py`: added `test_blank_lines_are_skipped`, which covers blank lines in the middle of the file, lines with only spaces, and Windows line endings.

The full suite passes: 19 tests.

I left the rest of the parser alone. A line with missing fields, such as `2025-03-03,Acme`, still raises an error that names the line, which is the right behaviour for real data problems. If you'd like a clearer message for those cases, that would be a separate change.