I fixed it: `hourlog import` now skips blank lines instead of failing on them.

**Fix:** In `hourlog/importer.py`, `parse_entries` now skips any line that is empty or only whitespace (including a lone `\r\n`). This applies anywhere in the file, not just at the end. The skipped lines still count, so if a later line is bad, the error gives its real line number in the file.

**Tests:** I added two tests to `tests/test_importer.py`. One checks that blank lines in the middle and at the end are skipped. The other checks that an error after a blank line still names the right line. Both failed before the fix. With the fix, `python -m pytest` shows 20 passed.

**Docs:** The CSV import section of the README now says "Blank lines are skipped."

I didn't try it on your accountant's actual file, since I don't have it. If that file has other surprises, like a header row or a different separator, the import will still stop with a line-numbered error.