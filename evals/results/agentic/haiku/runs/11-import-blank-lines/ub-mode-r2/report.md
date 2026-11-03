`hourlog import` now skips blank lines, so the accountant's file imports without the error. I haven't committed the change.

**Cause:** `parse_entries` in `hourlog/importer.py` passed every line to the parser, including empty ones. An empty line splits into one field, which triggered the unpacking error. The line number in the message was correct; the line really was empty.

**Fix:** `parse_entries` skips any line that is empty or whitespace-only. Line numbers still come from `enumerate`, so an error after a blank line still reports the right line.

**Tests** (`tests/test_importer.py`), written first and confirmed failing for the reported reason before the fix:
- `test_blank_lines_are_skipped`: blank, whitespace-only, and CRLF-only lines between and after entries are ignored.
- `test_blank_line_does_not_shift_later_line_numbers`: a bad line after a blank one is reported as line 3.

**Verification:** the full suite passes (20 tests, up from 18). I also ran `python -m hourlog import` on a CSV ending in a blank line, and it reported `imported 2 entries`.

Changes are in `hourlog/importer.py` and `tests/test_importer.py`. Want me to commit this?