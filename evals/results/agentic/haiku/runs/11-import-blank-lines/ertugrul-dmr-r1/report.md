`hourlog import` now skips blank lines, so the accountant's CSV should import. The full test suite passes (19 tests, including a new one for this case).

**The cause:** `_parse_line` splits each line on commas and unpacks three values. A blank line splits into one value, which raised the "not enough values to unpack" error. The error was then reported with the line number.

**The fix:** In `hourlog/importer.py`, `parse_entries` skips any line that is empty or only whitespace, so a stray blank line at the end of a file no longer breaks the import. Lines with real data are parsed as before, and a malformed line still raises `ImportFormatError` with its line number.

I added `test_blank_lines_are_skipped` to `tests/test_importer.py`. It covers blank lines in the middle of the file, whitespace-only lines, and CRLF endings.

I haven't committed anything. Let me know if you want a commit.