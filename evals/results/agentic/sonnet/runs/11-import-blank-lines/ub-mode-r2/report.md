`hourlog import` now skips blank lines, so the trailing empty line in your accountant's CSV no longer causes the error. The full suite passes (19 tests). I haven't run it against the actual CSV file.

The importer split every line on commas, and an empty line gives one field instead of three. The fix is in `hourlog/importer.py`: lines that are empty or only whitespace are skipped. Skipped lines still count in the numbering, so an error on a later line still points at the right line in the file.

**Log**
- I read `importer.py` and its tests to find the cause.
- I added a test with blank lines in the middle and at the end, and it failed with your exact error.
- I added the skip in `parse_entries`.
- I ran the full suite.
- I committed the change as `4f4203b`. I did not push, since you didn't ask me to and I wasn't sure you wanted that.