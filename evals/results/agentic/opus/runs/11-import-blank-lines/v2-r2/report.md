`hourlog import` now skips blank lines, so the trailing empty line in your accountant's file no longer causes that error. I didn't run it on their actual CSV, but the new tests cover the same case, and all 20 tests pass.

**The cause:** `_parse_line` in `hourlog/importer.py` splits every line on commas and expects three fields. An empty line has only one, so it failed.

**The fix:** `parse_entries` now skips any line that is empty or contains only whitespace, including a `\r\n` from a Windows file. That's a two-line change. Blank lines still count toward line numbers, so if a later line is bad, the error still points to the right line in the file.

**Tests:** I added two to `tests/test_importer.py`. One checks that blank lines in the middle and at the end are skipped. The other checks that an error after a blank line still reports the correct line number. Both failed before the fix and pass now.

I haven't committed anything.