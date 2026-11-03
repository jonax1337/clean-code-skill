`hourlog import` now skips blank lines, so the accountant's file with the empty last line will import. The full test suite passes (20 tests). I haven't run it against the actual file.

**The bug:** `_parse_line` in `hourlog/importer.py` split every line on commas and expected exactly three fields. An empty line gave one field, which caused the "not enough values to unpack" error.

**The fix:** `parse_entries` now passes over any line that is empty or only whitespace (including a bare `\r\n`). Line numbers still count the skipped lines, so error messages point to the right line in the file.

**Tests:** I added two tests to `tests/test_importer.py`. One checks that blank lines in the middle and at the end are skipped. The other checks that an error after a blank line still reports the correct line number. Both failed before the fix and pass now.

Lines with the wrong number of fields, like `2025-03-03,Acme`, still give the same unclear "unpack" message. You may want a clearer error there too, like "expected 3 fields, got 2". I didn't change that because it's outside this fix.

Nothing is committed yet.