I fixed it: `hourlog import` now skips blank lines, so the empty line at the end of your accountant's file no longer stops the import. All 20 tests pass, and a test file with Windows line endings and a trailing empty line imported both entries and reported the right totals.

**Cause:** the importer split every line into three fields, including empty ones. An empty line produces only one field, which caused the "not enough values to unpack" error.

**Log of what I did:**
1. **Read the code.** The failure was in `_parse_line` in `hourlog/importer.py`.
2. **Wrote failing tests first** in `tests/test_importer.py`:
   - Blank and whitespace-only lines, including `\r\n` ones, are skipped.
   - Error messages still count blank lines, so "line 3" still means line 3 of the file.
   
   Both failed with the same error you got.
3. **Fixed it** with a two-line change in `parse_entries`: a line that is empty or only whitespace is skipped before parsing.
4. **Updated the README** to say "Blank lines are skipped."
5. **Committed** as `f85cc38`, with the reason and the test results in the message.

Blank lines in the middle of a file are skipped too, not just the one at the end. I didn't run the crapper, dryer or mutator tools for a change this small, and I haven't pushed. Let me know if you want it pushed to `main`.