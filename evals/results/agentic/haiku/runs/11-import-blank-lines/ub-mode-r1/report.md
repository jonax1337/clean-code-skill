Fixed. Blank lines in the CSV are now skipped, so the trailing empty line no longer stops the import.

The cause was in `hourlog/importer.py`: `parse_entries` passed every line to `_parse_line`, including an empty one, which split into a single field and failed to unpack into three values.

**Changes**
- `hourlog/importer.py`: skip any line that is empty or whitespace-only before parsing. Line numbers still count the skipped lines, so errors on later lines point at the right place in the file.
- `tests/test_importer.py`: added `test_blank_lines_are_skipped`, which covers blank lines between and after entries, including a `\r\n` whitespace-only line. I saw it fail with your exact error before making the fix.
- `README.md`: added one sentence noting that blank lines are skipped.

**Verification:** the full suite passes (19 tests).

**Log of actions**
1. Searched the repo and read the importer, its tests, and the README to find the parsing path.
2. Added a failing test for blank lines and confirmed it reproduced the reported error.
3. Added the skip-blank-lines check to `parse_entries`.
4. Documented the behavior in the README.
5. Ran the full test suite.

I haven't committed anything. Say if you want it committed to `main`.