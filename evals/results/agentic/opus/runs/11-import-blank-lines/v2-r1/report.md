`hourlog import` now skips empty lines, so the accountant's file should import cleanly. I ran the test suite: all 20 tests pass, including two new ones.

**The cause:** in `hourlog/importer.py`, `_parse_line` splits every line on commas and expects exactly three values. An empty line splits into one value, which gave you the "expected 3, got 1" error.

**The fix:** `parse_entries` now skips any line that is empty or contains only whitespace (including a stray `\r\n`), wherever it appears in the file. Line numbers in error messages still count the skipped lines, so they match what you see in an editor.

**New tests** in `tests/test_importer.py`:
- `test_blank_lines_are_skipped`: blank and whitespace-only lines, in the middle and at the end, are ignored.
- `test_line_numbers_count_skipped_blank_lines`: an error after a blank line still reports the right line number.

Both failed before the fix. I haven't committed anything.