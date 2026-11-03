I fixed it: `hourlog import` now skips blank lines, so the empty line at the end of your accountant's CSV no longer breaks it.

**The cause:** the importer (`hourlog/importer.py:15`) treated every line as `date,project,minutes`. An empty line splits into one value, not three, which is the error you saw.

**The fix:** before parsing, it skips any line that is empty or contains only spaces. This covers blank lines anywhere in the file, not just at the end. Error messages still give the real line number in the file.

**Tests:** I added two to `tests/test_importer.py`:
- Blank lines (including whitespace-only and Windows line endings) are skipped.
- A bad line that comes after a blank line still reports its correct line number.

Both failed before the fix. The full suite now passes: `pytest`: 20 passed. I couldn't run the linter because `ruff` isn't installed here. I haven't committed anything.