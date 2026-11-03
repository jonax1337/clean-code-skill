I fixed it. `hourlog import` now skips blank lines, so the accountant's file goes through.

**Cause:** `_parse_line` in `hourlog/importer.py` split every line on commas, including the empty one at the end. An empty line gives one field instead of three, which produced the "not enough values to unpack" error.

**Fix:** `parse_entries` now skips any line that is empty or only whitespace (for example `\r\n` or spaces), wherever it is in the file. Error messages still use the real line numbers from the file. I also added a sentence to the README saying blank lines are skipped.

**Log:**
1. Read the importer, CLI and tests to find the cause.
2. Added two tests to `tests/test_importer.py`: blank lines (in the middle, whitespace-only and at the end) are skipped, and error line numbers still count the blank lines. Both failed with the exact error you reported.
3. Added the two-line skip in `parse_entries`. That's the smallest fix, and the check happens where each line is read.
4. Updated the README's CSV import section.
5. All 20 tests pass. I also ran a real import of a Windows-style file (`\r\n` line endings) with a blank last line: it imported 2 entries and the report totals were correct.
6. Committed as `f6df2ef` on `main`. It isn't pushed because the repo has no remote configured.

I didn't run the crapper, dryer or mutator tools from the skill, because they aren't available here.