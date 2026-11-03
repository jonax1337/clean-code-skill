Fixed. `hourlog import` now skips blank lines, including whitespace-only ones and `\r\n` endings, so the accountant's trailing empty line no longer crashes the import.

**Cause:** `_parse_line` did `line.split(",")` and unpacked into three names. An empty line splits to a single empty string, so the unpack failed with "expected 3, got 1".

**Change:** In `hourlog/importer.py`, `parse_entries` now continues past any line where `line.strip()` is empty. Line numbers still count every physical line, so a real error after a blank line still reports the correct line in the file.

**Tests:** I added two tests to `tests/test_importer.py`:
- `test_blank_lines_are_skipped` covers blank, whitespace-only, and CRLF blank lines mixed with valid rows.
- `test_bad_line_after_blank_line_keeps_its_line_number` checks that a malformed row after a blank line is still reported as the correct line.

The full suite passes: 20 tests.

I did not change how malformed non-blank lines are handled. A line with the wrong number of fields still raises `ImportFormatError` with its line number.