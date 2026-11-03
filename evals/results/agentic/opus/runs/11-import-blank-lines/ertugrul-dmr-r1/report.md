I fixed it. `hourlog import` now skips empty lines, so the trailing line in your accountant's CSV no longer causes an error. All 21 tests pass.

**Cause:** in `hourlog/importer.py`, every line was split on commas and expected to give exactly three fields (`date,project,minutes`). An empty line gives just one, which caused the "expected 3, got 1" error.

**Fix:**
- `parse_entries` now skips any line that is empty or contains only whitespace. The check is in a small helper, `_is_blank`.
- Line numbers in error messages still count the skipped lines, so they match what you see in the file.
- Blank lines in the middle of the file are skipped too, not just the one at the end. That seemed right for an export file, but tell me if you'd rather a blank line in the middle be reported as an error.

**New tests** in `tests/test_importer.py`:
- a trailing empty line is ignored
- whitespace-only lines (including Windows `\r\n` endings) are ignored
- an error after a skipped blank line still reports the correct line number

I haven't committed anything.