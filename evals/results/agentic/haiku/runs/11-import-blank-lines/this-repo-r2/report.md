Blank lines in the import file are now skipped, so the accountant's CSV should import. The test suite passes: 20 tests, up from 18.

**What was wrong:** `_parse_line` in `hourlog/importer.py` split every line on commas and unpacked three fields. A blank line splits into one empty field, so the unpack failed. The line number was right; the file just had a blank line at the end.

**The fix:** `parse_entries` now skips any line that is empty or only whitespace. Line numbers still count physical lines, so an error on a later line still points at the right place in the file.

**Tests added in `tests/test_importer.py`:**
- Blank and whitespace-only lines between entries are skipped, and the entries still parse correctly.
- A bad line after a blank line reports its true file line number (line 3, not line 2).

The first test fails without the fix, since the blank line raised the unpack error.

I didn't commit anything, and I didn't run the import against the accountant's actual file. If that file has other quirks, such as a header row or a different delimiter, it will still fail with a line-numbered error.