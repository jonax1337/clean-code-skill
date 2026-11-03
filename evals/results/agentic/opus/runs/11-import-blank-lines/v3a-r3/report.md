I fixed it, and the import now skips blank lines. That includes the empty line at the end of your accountant's file and lines that contain only whitespace or `\r\n`.

**Cause:** `parse_entries` in `hourlog/importer.py` passed every line to `_parse_line`. That function splits each line on commas and expects exactly three parts, so an empty line crashed it.

**Fix:** `parse_entries` now skips any line that is empty after trimming whitespace. Line numbers in error messages still count the skipped lines, so they keep matching the line numbers in the file.

**Tests:** I added two tests to `tests/test_importer.py`. One checks that blank lines are skipped. The other checks that line numbers still count blank lines. Both failed before the change and pass after it. The full suite passes: 20 passed.

**Not changed:** a line with the wrong number of fields, like `2025-03-03,Acme`, still gives the same confusing "not enough values to unpack" message, though it does say which line. I can change that to something clearer, like "expected date,project,minutes", if you want.