`hourlog import` now skips blank lines, so the accountant's file should import cleanly.

**Cause:** `parse_entries` in `hourlog/importer.py` tried to split every line into `date,project,minutes`. The empty line at the end has no commas, so the split produced one value instead of three, and the import stopped with that error.

**Fix:** `parse_entries` now skips any line that is empty or only whitespace (including a bare `\r\n`), wherever it appears in the file. Error messages still use the line's real position in the file, so they point at the right line.

**Tests:** I added two to `tests/test_importer.py`. One checks that blank lines are skipped. The other checks that an error after a blank line still gives the correct line number. Both failed before the fix. Now `pytest` shows all 20 passing.

I didn't run it on the accountant's actual CSV, since I don't have it. If anything else in that file is malformed, such as a line with the wrong number of commas, you'll still get the same hard-to-read "not enough values to unpack" message. I left that alone because it wasn't what you asked, but it would be a small follow-up to give it a clearer message.